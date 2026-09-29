import pytest

from app.core.config import Settings


def test_default_config_value(monkeypatch: pytest.MonkeyPatch) -> None:
    for env in ("ENVIRONMENT", "DATABASE_URL"):
        monkeypatch.delenv(env, raising=False)

    settings = Settings(
        _env_file=None,  # type: ignore
        environment="test",
        app_name="From pytest",
    )

    assert settings.environment == "test"
    assert settings.app_name == "From pytest"
