"""Alembic runtime configuration for the local SQLite database."""

from __future__ import annotations

from logging.config import fileConfig

from alembic import context
from open_hollywood_api.persistence import models
from open_hollywood_api.persistence.database import database_path_from_environment, sqlite_url
from sqlalchemy import engine_from_config, pool

configuration = context.config

if configuration.config_file_name is not None:
    fileConfig(configuration.config_file_name)

configured_database_path = database_path_from_environment()
configured_database_path.parent.mkdir(parents=True, exist_ok=True)
configuration.set_main_option(
    "sqlalchemy.url",
    sqlite_url(configured_database_path).render_as_string(hide_password=False),
)
target_metadata = models.Base.metadata


def run_migrations_offline() -> None:
    """Render SQL without opening a database connection."""
    context.configure(
        url=configuration.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Apply migrations with foreign-key enforcement enabled."""
    connectable = engine_from_config(
        configuration.get_section(configuration.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        connection.exec_driver_sql("PRAGMA foreign_keys=ON")
        connection.exec_driver_sql("PRAGMA busy_timeout=5000")
        connection.commit()
        context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
