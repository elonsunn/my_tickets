from unittest.mock import AsyncMock

import pytest
from asgi_lifespan import LifespanManager
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker

from app.core.config import Settings
from app.main import create_app


async def test_lifespan_creates_database_pools(settings: Settings) -> None:
    app = create_app(settings)

    async with LifespanManager(app):
        assert isinstance(app.state.engine, AsyncEngine)
        assert isinstance(app.state.sessionmaker, async_sessionmaker)
        assert app.state.engine.url.database == "mytickets"
        assert app.state.engine.pool.size() == settings.database_pool_size  # pyright: ignore


async def test_lifespan_dispose_database_on_shutdown(
    settings: Settings, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Use a mock async function to replace real dispose
    dispose_mock = AsyncMock()
    monkeypatch.setattr(AsyncEngine, "dispose", dispose_mock)

    app = create_app(settings)
    async with LifespanManager(app):
        pass

    dispose_mock.assert_awaited_once()
