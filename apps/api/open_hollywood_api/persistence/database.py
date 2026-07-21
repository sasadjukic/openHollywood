"""SQLite engine and session construction."""

import os
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from sqlalchemy import URL, Engine, create_engine, event
from sqlalchemy.orm import Session, sessionmaker

DATABASE_PATH_VARIABLE = "OPEN_HOLLYWOOD_DB_PATH"
DEFAULT_DATABASE_PATH = Path("data/open_hollywood.db")


def database_path_from_environment(environment: Mapping[str, str] | None = None) -> Path:
    """Resolve the configured local database path without creating it."""
    values = os.environ if environment is None else environment
    configured_path = values.get(DATABASE_PATH_VARIABLE, str(DEFAULT_DATABASE_PATH)).strip()
    if not configured_path:
        raise ValueError(f"{DATABASE_PATH_VARIABLE} must not be empty")
    return Path(configured_path).expanduser()


def sqlite_url(database_path: Path) -> URL:
    """Build a URL without interpolating or escaping filesystem paths manually."""
    return URL.create(drivername="sqlite+pysqlite", database=str(database_path))


def _configure_sqlite_connection(
    dbapi_connection: Any,
    _connection_record: Any,
) -> None:
    cursor = dbapi_connection.cursor()
    try:
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA busy_timeout=5000")
    finally:
        cursor.close()


def create_sqlite_engine(database_path: Path, *, echo: bool = False) -> Engine:
    """Create the local engine and ensure its parent directory exists."""
    database_path.parent.mkdir(parents=True, exist_ok=True)
    engine = create_engine(sqlite_url(database_path), echo=echo, pool_pre_ping=True)
    event.listen(engine, "connect", _configure_sqlite_connection)
    return engine


def create_session_factory(engine: Engine) -> sessionmaker[Session]:
    """Create sessions that keep ORM records usable after transaction commits."""
    return sessionmaker(bind=engine, class_=Session, expire_on_commit=False)
