"""SQLite configuration and migration tests."""

from decimal import Decimal
from pathlib import Path

import pytest
from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.runtime.migration import MigrationContext
from open_hollywood_api.persistence import models
from open_hollywood_api.persistence.database import (
    create_sqlite_engine,
    database_path_from_environment,
)
from sqlalchemy import create_engine, inspect, select
from sqlalchemy.orm import Session

from tests.conftest import alembic_config
from tests.persistence.test_models import _populate_story_graph

EXPECTED_TABLES = {
    "agent_invocation_inputs",
    "agent_invocations",
    "alembic_version",
    "artifact_versions",
    "artifacts",
    "checkpoints",
    "conversations",
    "evaluations",
    "human_decisions",
    "messages",
    "model_profiles",
    "project_deletion_requests",
    "projects",
    "workflow_runs",
    "workflow_run_controls",
    "workflow_events",
    "writes",
}


def test_database_path_uses_default_and_environment_override() -> None:
    assert database_path_from_environment({}) == Path("data/open_hollywood.db")
    assert database_path_from_environment({"OPEN_HOLLYWOOD_DB_PATH": "custom/story.db"}) == Path(
        "custom/story.db"
    )

    with pytest.raises(ValueError, match="must not be empty"):
        database_path_from_environment({"OPEN_HOLLYWOOD_DB_PATH": "  "})


def test_application_engine_configures_sqlite_for_local_durability(tmp_path: Path) -> None:
    database_path = tmp_path / "nested" / "open_hollywood.db"
    engine = create_sqlite_engine(database_path)

    try:
        with engine.connect() as connection:
            assert connection.exec_driver_sql("PRAGMA foreign_keys").scalar_one() == 1
            assert connection.exec_driver_sql("PRAGMA journal_mode").scalar_one() == "wal"
            assert connection.exec_driver_sql("PRAGMA busy_timeout").scalar_one() == 5000
    finally:
        engine.dispose()

    assert database_path.is_file()


def test_migration_upgrade_matches_metadata_and_downgrades(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    database_path = tmp_path / "nested" / "migration.db"
    monkeypatch.setenv("OPEN_HOLLYWOOD_DB_PATH", str(database_path))
    configuration = alembic_config()

    command.upgrade(configuration, "head")
    engine = create_engine(f"sqlite+pysqlite:///{database_path.as_posix()}")
    try:
        assert set(inspect(engine).get_table_names()) == EXPECTED_TABLES
        with engine.connect() as connection:
            context = MigrationContext.configure(connection)
            assert compare_metadata(context, models.Base.metadata) == []
    finally:
        engine.dispose()

    command.downgrade(configuration, "base")
    downgraded_engine = create_engine(f"sqlite+pysqlite:///{database_path.as_posix()}")
    try:
        assert set(inspect(downgraded_engine).get_table_names()) == {"alembic_version"}
    finally:
        downgraded_engine.dispose()


def test_cost_migration_preserves_populated_lineage_and_leaves_old_costs_unknown(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    database_path = tmp_path / "cost-migration.db"
    monkeypatch.setenv("OPEN_HOLLYWOOD_DB_PATH", str(database_path))
    configuration = alembic_config()
    command.upgrade(configuration, "head")
    engine = create_engine(f"sqlite+pysqlite:///{database_path.as_posix()}")
    with Session(engine) as session:
        _populate_story_graph(session)
        invocation = session.scalar(select(models.AgentInvocation))
        assert invocation is not None
        invocation.estimated_cost_usd = Decimal("1.25")
        session.commit()
    engine.dispose()
    command.downgrade(configuration, "0007")

    def snapshot() -> dict[str, list[tuple[object, ...]]]:
        with engine.connect() as connection:
            return {
                name: [tuple(row) for row in connection.exec_driver_sql(f'SELECT * FROM "{name}"')]
                for name in sorted(EXPECTED_TABLES - {"alembic_version"})
            }

    before = snapshot()
    command.upgrade(configuration, "head")
    after = snapshot()
    assert [row[-1] for row in after["agent_invocations"]] == ["UNKNOWN"]
    after["agent_invocations"] = [row[:-1] for row in after["agent_invocations"]]
    assert after == before
    with engine.connect() as connection:
        assert connection.exec_driver_sql("PRAGMA integrity_check").scalar_one() == "ok"
        assert connection.exec_driver_sql("PRAGMA foreign_key_check").all() == []
    engine.dispose()
    command.downgrade(configuration, "0007")
    assert snapshot() == before
    engine.dispose()
