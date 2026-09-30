from collections.abc import AsyncIterator

import pytest
from asgi_lifespan import LifespanManager
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.core.config import Settings
from app.main import create_app


@pytest.fixture
def settings() -> Settings:
    return Settings(
        _env_file=None,  # type: ignore
        environment="test",
        app_name="From pytest",
    )


@pytest.fixture
def app(settings: Settings) -> FastAPI:
    return create_app(settings=settings)


@pytest.fixture
async def app_started(app: FastAPI) -> AsyncIterator[FastAPI]:
    async with LifespanManager(app=app):
        yield app


@pytest.fixture
async def client(app_started: FastAPI) -> AsyncIterator[AsyncClient]:
    async with AsyncClient(transport=ASGITransport(app=app_started), base_url="http://test") as c:
        yield c
