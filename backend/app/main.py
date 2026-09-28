from fastapi import FastAPI

from .module.health.router import router
from app.core.config import Settings, get_settings

def create_app(settings: Settings | None = None):
    settings = settings or get_settings()

    app = FastAPI(title=settings.app_name)
    app.state.settings = settings
    app.include_router(router=router)
    return app

app = create_app()