from fastapi import FastAPI

from .module.health.router import router

def create_app():
    app = FastAPI(title="my tickets API")
    app.include_router(router=router)
    return app

app = create_app()