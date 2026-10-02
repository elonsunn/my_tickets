from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config

from app.core.config import get_settings


@pytest.fixture
def alembic_config() -> Config:
    """Alembic config against the test database."""
    alembic_ini_path = str(Path(__file__).resolve().parents[2] / "alembic.ini")
    config = Config(alembic_ini_path)
    config.set_main_option(
        "sqlalchemy.url", get_settings().database_url.replace("%", "%%")
    )
    return config


def test_migrations_upgrade_to_head(alembic_config: Config) -> None:
    command.upgrade(alembic_config, "head")


def test_model_and_migrations_sync(alembic_config: Config) -> None:
    command.upgrade(alembic_config, "head")
    command.check(alembic_config)
