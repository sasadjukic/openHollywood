"""SQLAlchemy boundary enforcing secret-free durable state and exports."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

from open_hollywood_engine.secrets import EnvironmentSecretStore, SecretLeakGuard
from sqlalchemy import Engine, MetaData, event, inspect, select
from sqlalchemy.orm import Session


def active_secret_guard() -> SecretLeakGuard:
    """Build a guard from model credentials configured for the current process."""
    return SecretLeakGuard(EnvironmentSecretStore().configured_values())


@event.listens_for(Session, "before_flush")
def reject_secrets_before_flush(
    session: Session,
    _flush_context: object,
    _instances: object,
) -> None:
    """Reject credentials before any ORM-backed record reaches SQLite or a trace table."""
    guard = active_secret_guard()
    for record in session.new.union(session.dirty):
        state = inspect(record)
        values = {
            attribute.key: getattr(record, attribute.key) for attribute in state.mapper.columns
        }
        guard.ensure_safe(
            values,
            destination=f"database record {record.__class__.__name__}",
        )


def audit_database_export(engine: Engine) -> None:
    """Fail closed if a database contains a configured credential before export."""
    guard = active_secret_guard()
    metadata = MetaData()
    metadata.reflect(bind=engine)
    with engine.connect() as connection:
        for table in metadata.sorted_tables:
            for row in _rows(connection.execute(select(table)).mappings()):
                guard.ensure_safe(row, destination=f"database export table {table.name}")


def _rows(rows: Any) -> Iterator[dict[str, Any]]:
    for row in rows:
        yield dict(row)
