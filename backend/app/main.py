from fastapi import FastAPI

from app.core.config import Settings, get_settings

from .module.health.router import router


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()

    app = FastAPI(title=settings.app_name)
    app.state.settings = settings
    app.include_router(router=router)
    return app


app = create_app()
