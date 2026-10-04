from collections.abc import AsyncGenerator
from contextlib import AsyncExitStack, asynccontextmanager

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker

from app.core.config import Settings, get_settings
from app.core.database import create_database_engine
from app.core.exceptions import ApplicationError, application_error_handler
from app.core.logging import configure_logging
from app.core.middleware import RequestIDMiddleware

from .module.health.router import router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    settings: Settings = app.state.settings
    async with AsyncExitStack() as stack:
        engine: AsyncEngine = await create_database_engine(
            url=settings.database_url,
            echo=settings.database_echo,
            pool_size=settings.database_pool_size,
            max_overflow=settings.database_max_overflow,
            pool_timeout=settings.database_pool_timeout,
        )
        stack.push_async_callback(engine.dispose)
        app.state.engine = engine
        app.state.sessionmaker = async_sessionmaker(engine, expire_on_commit=False)
        yield


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    configure_logging(log_level=settings.log_level, json_logs=settings.json_logs)

    app = FastAPI(title=settings.app_name, lifespan=lifespan)
    app.state.settings = settings
    app.add_middleware(RequestIDMiddleware)
    app.add_exception_handler(ApplicationError, application_error_handler)
    app.include_router(router=router)
    return app
