from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker

from app.core.config import Settings, get_settings
from app.core.database import create_database_engine
from app.core.logging import configure_logging
from app.core.middleware import RequestIDMiddleware

from .module.health.router import router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    settings = app.state.settings
    database_url: str = settings.database_url
    database_echo: bool = settings.database_echo
    engine: AsyncEngine = await create_database_engine(url=database_url, echo=database_echo)
    app.state.engine = engine
    app.state.sessionmaker = async_sessionmaker(engine, expire_on_commit=False)

    try:
        yield
    finally:
        await engine.dispose()


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    configure_logging(log_level=settings.log_level, json_logs=settings.json_logs)

    app = FastAPI(title=settings.app_name, lifespan=lifespan)
    app.state.settings = settings
    app.add_middleware(RequestIDMiddleware)
    app.include_router(router=router)
    return app
