import pytest
from httpx import ASGITransport, AsyncClient

from app.main import create_app
from app.core.config import Settings

@pytest.fixture
def settings():
    return Settings(
        _env_file=None,    # type: ignore
        environment="test",
        app_name="From pytest") 

@pytest.fixture
def app(settings):
    return create_app(settings=settings)

@pytest.fixture
async def client(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c

                