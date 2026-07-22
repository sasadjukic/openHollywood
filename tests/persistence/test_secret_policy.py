"""Persistence and database-export secret policy integration tests."""

from uuid import uuid4

import pytest
from open_hollywood_api.persistence import audit_database_export
from open_hollywood_api.persistence.database import create_session_factory
from open_hollywood_api.persistence.models import (
    AgentInvocation,
    Artifact,
    ArtifactVersion,
    ModelProfile,
    ModelProfileMode,
    Project,
    WorkflowRun,
)
from open_hollywood_engine.secrets import SecretLeakError
from sqlalchemy import Engine, text


def test_runtime_credential_cannot_enter_story_records(
    database_engine: Engine,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("OLLAMA_API_KEY", "unit-test-runtime-credential")
    session_factory = create_session_factory(database_engine)

    with session_factory() as session:
        session.add(Project(name="unit-test-runtime-credential"))

        with pytest.raises(SecretLeakError) as error:
            session.commit()

    assert "unit-test-runtime-credential" not in str(error.value)


def test_runtime_credential_cannot_enter_artifact_content(
    database_engine: Engine,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("OLLAMA_API_KEY", "unit-test-runtime-credential")
    session_factory = create_session_factory(database_engine)

    with session_factory() as session:
        project = Project(name="Safe project")
        artifact = Artifact(
            project=project,
            artifact_key="blueprint",
            artifact_type="story_blueprint",
            title="Blueprint",
        )
        session.add(
            ArtifactVersion(
                artifact=artifact,
                version_number=1,
                schema_version="1",
                content={"logline": "unit-test-runtime-credential"},
                content_sha256="1" * 64,
            )
        )

        with pytest.raises(SecretLeakError) as error:
            session.commit()

    assert "ArtifactVersion" in str(error.value)
    assert "unit-test-runtime-credential" not in str(error.value)


def test_runtime_credential_cannot_enter_invocation_trace(
    database_engine: Engine,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("OLLAMA_API_KEY", "unit-test-runtime-credential")
    session_factory = create_session_factory(database_engine)

    with session_factory() as session:
        project = Project(name="Safe project")
        run = WorkflowRun(project=project, workflow_name="blueprint", graph_version="1")
        session.add(
            AgentInvocation(
                workflow_run=run,
                specialist_role="architect",
                provider="ollama",
                model_identifier="gemma4:e4b",
                prompt_sha256="1" * 64,
                prompt_text="unit-test-runtime-credential",
            )
        )

        with pytest.raises(SecretLeakError) as error:
            session.commit()

    assert "AgentInvocation" in str(error.value)
    assert "unit-test-runtime-credential" not in str(error.value)


def test_credential_label_cannot_enter_secret_free_model_profile(
    database_engine: Engine,
) -> None:
    session_factory = create_session_factory(database_engine)

    with session_factory() as session:
        session.add(
            ModelProfile(
                name="Unsafe profile",
                mode=ModelProfileMode.CLOUD,
                configuration={"api_key": "not-allowed-even-when-not-configured"},
            )
        )

        with pytest.raises(SecretLeakError, match="ModelProfile"):
            session.commit()


def test_database_export_audit_passes_for_secret_references(
    database_engine: Engine,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("OLLAMA_API_KEY", "unit-test-runtime-credential")
    session_factory = create_session_factory(database_engine)
    with session_factory() as session:
        session.add(
            ModelProfile(
                name="Safe cloud profile",
                mode=ModelProfileMode.CLOUD,
                configuration={"secret_reference": "ollama_api_key"},
            )
        )
        session.commit()

    audit_database_export(database_engine)


def test_database_export_audit_detects_rows_written_outside_orm_policy(
    database_engine: Engine,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("OLLAMA_API_KEY", "unit-test-runtime-credential")
    with database_engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO projects "
                "(id, name, story_format, status, settings, created_at, updated_at) "
                "VALUES (:id, :name, 'short_prose', 'ACTIVE', '{}', CURRENT_TIMESTAMP, "
                "CURRENT_TIMESTAMP)"
            ),
            {"id": uuid4().hex, "name": "unit-test-runtime-credential"},
        )

    with pytest.raises(SecretLeakError) as error:
        audit_database_export(database_engine)

    assert "unit-test-runtime-credential" not in str(error.value)
