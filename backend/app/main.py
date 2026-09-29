from fastapi import FastAPI

from app.core.config import Settings, get_settings
from app.core.logging import configure_logging
from app.core.middleware import RequestIDMiddleware

from .module.health.router import router


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    configure_logging(log_level=settings.log_level, json_logs=settings.json_logs)

    app = FastAPI(title=settings.app_name)
    app.state.settings = settings
    app.add_middleware(RequestIDMiddleware)
    app.include_router(router=router)
    return app
