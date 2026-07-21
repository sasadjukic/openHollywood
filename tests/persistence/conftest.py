"""Shared migrated SQLite fixtures."""

from collections.abc import Iterator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from open_hollywood_api.persistence.database import create_sqlite_engine
from sqlalchemy import Engine

WORKSPACE_ROOT = Path(__file__).resolve().parents[2]


def alembic_config() -> Config:
    """Load the workspace Alembic configuration by absolute path."""
    return Config(WORKSPACE_ROOT / "alembic.ini")


@pytest.fixture
def migrated_database_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Upgrade an isolated database through the real migration chain."""
    database_path = tmp_path / "database" / "open_hollywood.db"
    monkeypatch.setenv("OPEN_HOLLYWOOD_DB_PATH", str(database_path))
    command.upgrade(alembic_config(), "head")
    return database_path


@pytest.fixture
def database_engine(migrated_database_path: Path) -> Iterator[Engine]:
    """Connect application sessions to an isolated migrated database."""
    engine = create_sqlite_engine(migrated_database_path)
    try:
        yield engine
    finally:
        engine.dispose()
