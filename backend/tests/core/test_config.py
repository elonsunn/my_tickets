import pytest
from pydantic import ValidationError

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


def test_jwt_secret_hidden_from_repr(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("JWT_SECRET", "a" * 40)

    settings = Settings(_env_file=None)  # type: ignore
    assert "a" * 40 not in repr(settings)
    assert settings.jwt_secret.get_secret_value() == "a" * 40


def test_short_jwt_secret_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("JWT_SECRET", "short-secret")
    with pytest.raises(ValidationError, match="32"):
        Settings(_env_file=None)
