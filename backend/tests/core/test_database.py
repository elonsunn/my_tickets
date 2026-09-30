from fastapi import FastAPI
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import create_database_engine


async def test_datebase_engine_connection(app: FastAPI) -> None:
    engine = await create_database_engine(
        url=app.state.settings.database_url, echo=app.state.settings.database_echo
    )

    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT 1"))
        print(result.scalar())


async def test_database_session_query(app_started: FastAPI) -> None:
    async with app_started.state.sessionmaker() as session:
        assert isinstance(session, AsyncSession)
        result = await session.execute(text("SELECT 1"))
        assert result.scalar_one() == 1
