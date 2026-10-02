from functools import lru_cache
from typing import Annotated, Literal, Self

from fastapi import Depends, Request
from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_DEV_JWT_SECRET = "dev-only-insecure-jwt-secret-change-me-0123456789"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    app_name: str = "My Tickets API"
    environment: Literal["test", "stage", "prod"] = "test"
    log_level: str = "INFO"
    json_logs: bool = True
    database_url: str = (
        "postgresql+asyncpg://mytickets:mytickets@localhost:54321/mytickets"
    )
    database_echo: bool = False
    database_pool_size: int = 5
    database_max_overflow: int = 5
    database_pool_timeout: int = 20
    jwt_secret: SecretStr = SecretStr(_DEV_JWT_SECRET)
    jwt_algo: Literal["HS256"] = "HS256"
    access_token_ttl_seconds: int = Field(default=15 * 60, gt=0)
    refresh_token_ttl_seconds: int = Field(default=7 * 24 * 60 * 60, gt=0)

    @model_validator(mode="after")
    def _check_jwt_secret(self) -> Self:
        secret = self.jwt_secret.get_secret_value()
        if len(secret) < 32:
            raise ValueError("JWT_SECRET must be at least 32 char long")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()


def get_running_app_settings(request: Request) -> Settings:
    return request.app.state.settings


AppSettings = Annotated[Settings, Depends(get_running_app_settings)]
