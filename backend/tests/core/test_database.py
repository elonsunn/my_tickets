from collections.abc import AsyncGenerator

import pytest
import sqlalchemy.dialects.postgresql
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy import (
    CheckConstraint,
    Column,
    CreateTable,
    Integer,
    String,
    Table,
    text,
)
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from app.core.database import Base, DBsession


def test_constrains_get_conventional_names() -> None:
    table = Table(
        "pytest",
        Base.metadata,
        Column("id", Integer, primary_key=True),
        Column("code", String(10), unique=True),
        Column("size", Integer),
        CheckConstraint("size>0", name="positive_size"),
    )

    ddl_text = str(
        CreateTable(table).compile(dialect=sqlalchemy.dialects.postgresql.dialect())
    )
    assert "CONSTRAINT pk_pytest PRIMARY KEY" in ddl_text
    assert "CONSTRAINT uq_pytest_code UNIQUE" in ddl_text
    assert "CONSTRAINT ck_pytest_positive_size CHECK" in ddl_text


async def test_database_session_query(app_started: FastAPI) -> None:
    async with app_started.state.sessionmaker() as session:
        assert isinstance(session, AsyncSession)
        result = await session.execute(text("SELECT 1"))
        assert result.scalar_one() == 1


@pytest.fixture
def app_with_ping(app_started: FastAPI) -> FastAPI:
    @app_started.get("/_test/ping")
    async def ping(db: DBsession) -> dict[str, object]:
        res = await db.execute(text("SELECT 1"))
        return {"db": res.scalar_one()}

    return app_started


@pytest.fixture
async def ping_client(app_with_ping: FastAPI) -> AsyncGenerator[AsyncClient]:
    async with AsyncClient(
        transport=ASGITransport(app=app_with_ping), base_url="http://test"
    ) as c:
        yield c


async def test_dependency_use_real_database_connection(
    ping_client: AsyncClient,
) -> None:
    res = await ping_client.get(url="/_test/ping")
    assert res.status_code == 200
    assert res.json() == {"db": 1}


@pytest.fixture
def app_with_rollback(app_started: FastAPI) -> FastAPI:
    @app_started.post("/_test/rollback")
    async def rollback(db: DBsession) -> None:
        await db.execute(text("INSERT INTO _rollback_table (id) VALUES (1)"))
        raise RuntimeError("Crash on purpose")

    return app_started


async def test_failed_request_rollback_uncommited_work(
    app_with_rollback: FastAPI,
) -> None:
    engine: AsyncEngine = app_with_rollback.state.engine
    async with engine.begin() as conn:
        await conn.execute(text("CREATE TABLE _rollback_table (id int)"))

    try:
        async with AsyncClient(
            transport=ASGITransport(app=app_with_rollback, raise_app_exceptions=False),
            base_url="http://test",
        ) as client:
            resp = await client.post("/_test/rollback")
            assert resp.status_code == 500

            async with engine.connect() as conn:
                result = await conn.execute(text("SELECT COUNT(*) FROM _rollback_table"))
                assert result.scalar_one() == 0
    finally:
        async with engine.begin() as conn:
            await conn.execute(text("DROP TABLE IF EXISTS _rollback_table"))
