"""Persistence model integration tests."""

from decimal import Decimal

import pytest
from open_hollywood_api.persistence.database import create_session_factory
from open_hollywood_api.persistence.models import (
    AgentInvocation,
    Artifact,
    ArtifactStatus,
    ArtifactVersion,
    Conversation,
    Evaluation,
    ImmutableArtifactVersionError,
    InvocationStatus,
    Message,
    MessageRole,
    ModelProfile,
    ModelProfileMode,
    Project,
    RunStatus,
    WorkflowRun,
)
from sqlalchemy import Engine, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

PERSISTED_RECORDS = (
    Project,
    Conversation,
    Message,
    Artifact,
    ArtifactVersion,
    WorkflowRun,
    AgentInvocation,
    ModelProfile,
    Evaluation,
)


def _populate_story_graph(session: Session) -> tuple[Project, ArtifactVersion, ArtifactVersion]:
    project = Project(name="The Empty Building", description="A supernatural horror story")
    conversation = Conversation(project=project, title="Story development")
    profile = ModelProfile(
        name="Local development",
        mode=ModelProfileMode.LOCAL,
        configuration={"roles": {"architect": {"provider": "ollama", "model": "test"}}},
        is_default=True,
    )
    workflow_run = WorkflowRun(
        project=project,
        conversation=conversation,
        workflow_name="story_blueprint",
        graph_version="1",
        status=RunStatus.RUNNING,
        input_state={"premise_message_sequence": 1},
        budget={"max_invocations": 12, "max_cost_usd": "2.00"},
    )
    artifact = Artifact(
        project=project,
        artifact_key="story-blueprint",
        artifact_type="story_blueprint",
        title="Story Blueprint",
        status=ArtifactStatus.DRAFT,
    )
    first_version = ArtifactVersion(
        artifact=artifact,
        version_number=1,
        schema_version="1",
        content={"logline": "A stroller waits outside a building that was never finished."},
        content_sha256="1" * 64,
        change_summary="Initial blueprint",
    )
    invocation = AgentInvocation(
        workflow_run=workflow_run,
        model_profile=profile,
        specialist_role="story_architect",
        provider="ollama",
        model_identifier="test",
        status=InvocationStatus.SUCCEEDED,
        request_settings={"temperature": 0.7},
        prompt_sha256="2" * 64,
        input_tokens=120,
        output_tokens=240,
        estimated_cost_usd=Decimal("0"),
        latency_ms=250,
        schema_validation_succeeded=True,
        input_versions=[first_version],
    )
    second_version = ArtifactVersion(
        artifact=artifact,
        parent_version=first_version,
        created_by_invocation=invocation,
        version_number=2,
        schema_version="1",
        content={
            "logline": "A pristine stroller lures a grieving mother toward an unfinished ruin."
        },
        content_sha256="3" * 64,
        change_summary="Sharpened protagonist and conflict",
    )
    message = Message(
        conversation=conversation,
        workflow_run=workflow_run,
        agent_invocation=invocation,
        sequence_number=1,
        role=MessageRole.USER,
        content="Write a story about the stroller outside the abandoned building.",
    )
    evaluation = Evaluation(
        project=project,
        workflow_run=workflow_run,
        artifact_version=second_version,
        evaluator_invocation=invocation,
        rubric_name="blueprint-quality",
        rubric_version="1",
        scores={"causality": 92, "originality": 88},
        weighted_score=Decimal("90.00"),
        summary="The revised blueprint has a stronger causal spine.",
    )
    session.add_all([project, profile, message, evaluation])
    session.commit()
    return project, first_version, second_version


def test_all_step_four_records_persist_with_lineage(database_engine: Engine) -> None:
    session_factory = create_session_factory(database_engine)
    with session_factory() as session:
        project, first_version, second_version = _populate_story_graph(session)
        project_id = project.id
        first_version_id = first_version.id
        second_version_id = second_version.id

    with session_factory() as session:
        for record_type in PERSISTED_RECORDS:
            count = session.scalar(select(func.count()).select_from(record_type))
            assert count == 1 if record_type not in (ArtifactVersion,) else count == 2

        stored_project = session.get(Project, project_id)
        stored_first_version = session.get(ArtifactVersion, first_version_id)
        stored_second_version = session.get(ArtifactVersion, second_version_id)

        assert stored_project is not None
        assert stored_first_version is not None
        assert stored_second_version is not None
        assert stored_second_version.parent_version_id == stored_first_version.id
        assert stored_second_version.created_by_invocation is not None
        assert stored_second_version.created_by_invocation.input_versions == [stored_first_version]
        assert stored_project.conversations[0].messages[0].sequence_number == 1
        assert stored_project.evaluations[0].weighted_score == Decimal("90.00")


def test_artifact_versions_are_append_only(database_engine: Engine) -> None:
    session_factory = create_session_factory(database_engine)
    with session_factory() as session:
        _, first_version, _ = _populate_story_graph(session)
        first_version.content = {"logline": "Overwritten"}

        with pytest.raises(ImmutableArtifactVersionError, match="create a new version"):
            session.commit()


def test_version_numbers_are_unique_within_an_artifact(database_engine: Engine) -> None:
    session_factory = create_session_factory(database_engine)
    with session_factory() as session:
        _, first_version, _ = _populate_story_graph(session)
        session.add(
            ArtifactVersion(
                artifact_id=first_version.artifact_id,
                version_number=1,
                schema_version="1",
                content={"logline": "Duplicate version"},
                content_sha256="4" * 64,
            )
        )

        with pytest.raises(IntegrityError):
            session.commit()
