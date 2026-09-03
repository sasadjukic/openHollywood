"""Regression tests for production handoff and failed-node recovery."""

from __future__ import annotations

from pathlib import Path
from typing import cast
from uuid import uuid4, uuid5

import pytest
from open_hollywood_api.persistence.database import create_session_factory
from open_hollywood_api.persistence.models import (
    Artifact,
    ArtifactVersion,
    Project,
    RunStatus,
    WorkflowRun,
)
from open_hollywood_api.services.blueprint_workflow import BlueprintWorkflowService
from open_hollywood_api.services.production_workflow import (
    SceneProductionService,
    SceneProductionWorkflowRunError,
    _materialize_schema_artifact,
)
from open_hollywood_api.services.workspace import WorkspaceStore
from open_hollywood_engine.artifacts import ArtifactKind, ScenePlan
from open_hollywood_engine.workflows import (
    SCENE_PRODUCTION_GRAPH_VERSION,
    SCENE_PRODUCTION_WORKFLOW_NAME,
    ArtifactReference,
    ProductionNode,
    RunBudget,
    RunControlAction,
    RunControlCommand,
    RunControlStatus,
    SceneProductionExecutor,
)
from open_hollywood_worker.runtime import WorkflowWorker
from sqlalchemy import Engine, select

pytestmark = pytest.mark.anyio


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


def test_regenerated_blueprint_appends_lineage_safe_handoff_version(
    database_engine: Engine,
) -> None:
    session_factory = create_session_factory(database_engine)
    project_id = uuid4()
    first_blueprint_version_id = uuid4()
    revised_blueprint_version_id = uuid4()
    first_plan = _scene_plan(title="Stitches of Silence")
    revised_plan = first_plan.model_copy(update={"title": "Silk and Secrets"})

    with session_factory.begin() as session:
        session.add(Project(id=project_id, name="The Seamstress"))
    with session_factory.begin() as session:
        first = _materialize_schema_artifact(
            session,
            project_id=project_id,
            artifact_key="scene_plan_scene_1",
            kind=ArtifactKind.SCENE_PLAN,
            title=first_plan.title,
            content=first_plan,
            summary="Initial approved Blueprint.",
            source_blueprint_version_id=first_blueprint_version_id,
        )
    with session_factory.begin() as session:
        revised = _materialize_schema_artifact(
            session,
            project_id=project_id,
            artifact_key="scene_plan_scene_1",
            kind=ArtifactKind.SCENE_PLAN,
            title=revised_plan.title,
            content=revised_plan,
            summary="Regenerated approved Blueprint.",
            source_blueprint_version_id=revised_blueprint_version_id,
        )
        replay = _materialize_schema_artifact(
            session,
            project_id=project_id,
            artifact_key="scene_plan_scene_1",
            kind=ArtifactKind.SCENE_PLAN,
            title=revised_plan.title,
            content=revised_plan,
            summary="Regenerated approved Blueprint.",
            source_blueprint_version_id=revised_blueprint_version_id,
        )

    assert first.version_id != revised.version_id
    assert revised == replay
    with session_factory() as session:
        artifact = session.scalar(
            select(Artifact).where(
                Artifact.project_id == project_id,
                Artifact.artifact_key == "scene_plan_scene_1",
            )
        )
        assert artifact is not None
        versions = session.scalars(
            select(ArtifactVersion)
            .where(ArtifactVersion.artifact_id == artifact.id)
            .order_by(ArtifactVersion.version_number)
        ).all()
    assert [version.version_number for version in versions] == [1, 2]
    assert versions[1].parent_version_id == versions[0].id
    assert versions[1].id == uuid5(
        revised_blueprint_version_id,
        "scene_plan_scene_1:deterministic-handoff",
    )


@pytest.mark.anyio
async def test_handoff_failure_persists_terminal_production_child(
    migrated_database_path: Path,
    database_engine: Engine,
) -> None:
    session_factory = create_session_factory(database_engine)
    project_id = uuid4()
    blueprint_run_id = uuid4()
    missing_blueprint = ArtifactReference(
        kind=ArtifactKind.STORY_BLUEPRINT,
        artifact_key="story_blueprint",
        version_id=uuid4(),
        schema_version="1",
    )
    with session_factory.begin() as session:
        project = Project(id=project_id, name="Broken Handoff")
        session.add_all(
            (
                project,
                WorkflowRun(
                    id=blueprint_run_id,
                    project=project,
                    workflow_name="story_blueprint",
                    graph_version="3",
                    status=RunStatus.SUCCEEDED,
                    input_state={"execution_kind": "interactive"},
                    budget=RunBudget().to_data(),
                ),
            )
        )

    async with SceneProductionService(
        database_path=migrated_database_path,
        session_factory=session_factory,
        executor=cast(SceneProductionExecutor, object()),
    ) as service:
        with pytest.raises(
            SceneProductionWorkflowRunError,
            match="approved Blueprint artifact lineage is invalid",
        ):
            await service.execute(blueprint_run_id, missing_blueprint)

    production_run_id = uuid5(
        blueprint_run_id,
        "agentic-scene-production-workflow",
    )
    with session_factory() as session:
        production_run = session.get(WorkflowRun, production_run_id)
    assert production_run is not None
    assert production_run.parent_workflow_run_id == blueprint_run_id
    assert production_run.status is RunStatus.FAILED
    assert production_run.current_node == "handoff"
    assert production_run.error_code == "production_handoff_failed"
    assert production_run.error_message == "approved Blueprint artifact lineage is invalid"
    worker = WorkflowWorker(
        session_factory=session_factory,
        blueprint_service=cast(BlueprintWorkflowService, object()),
        production_service=cast(SceneProductionService, object()),
    )
    assert worker._next_candidate() is None


@pytest.mark.anyio
async def test_failed_production_node_is_retryable_from_exact_checkpoint(
    migrated_database_path: Path,
    database_engine: Engine,
) -> None:
    session_factory = create_session_factory(database_engine)
    project_id = uuid4()
    production_run_id = uuid4()
    with session_factory.begin() as session:
        project = Project(id=project_id, name="Retryable Production")
        session.add_all(
            (
                project,
                WorkflowRun(
                    id=production_run_id,
                    project=project,
                    workflow_name=SCENE_PRODUCTION_WORKFLOW_NAME,
                    graph_version=SCENE_PRODUCTION_GRAPH_VERSION,
                    status=RunStatus.FAILED,
                    current_node=ProductionNode.CONTINUITY.value,
                    checkpoint_id="checkpoint-continuity",
                    input_state={"execution_kind": "interactive"},
                    budget=RunBudget().to_data(),
                    error_code="workflow_execution_failed",
                    error_message="production specialist returned invalid structured output",
                ),
            )
        )

    before = WorkspaceStore(session_factory).get_project_workspace(project_id)
    assert before.workflow_runs[0].retryable_nodes == (ProductionNode.CONTINUITY.value,)

    service = SceneProductionService(
        database_path=migrated_database_path,
        session_factory=session_factory,
        executor=cast(SceneProductionExecutor, object()),
    )
    result = await service.queue_retry_from_node(
        production_run_id,
        RunControlCommand(
            id=uuid4(),
            action=RunControlAction.RETRY_FROM_NODE,
            target_node=ProductionNode.CONTINUITY.value,
        ),
    )

    assert result.command_status is RunControlStatus.APPLIED
    assert result.resulting_workflow_run_id == production_run_id
    assert result.workflow_status is RunStatus.PENDING
    with session_factory() as session:
        production_run = session.get(WorkflowRun, production_run_id)
    assert production_run is not None
    assert production_run.status is RunStatus.PENDING
    assert production_run.checkpoint_id == "checkpoint-continuity"
    assert production_run.error_code is None
    assert production_run.error_message is None


def _scene_plan(*, title: str) -> ScenePlan:
    return ScenePlan(
        id="scene_1",
        scene_number=1,
        title=title,
        summary="The seamstress enters the royal court.",
        purpose="Begin the intrigue.",
        point_of_view_character_id="genevieve",
        character_ids=("genevieve",),
        location_id="versailles",
        time_context="During the French Revolution",
        entry_state="Genevieve is unknown at court.",
        goal="Deliver a coded gown.",
        conflict="The guards inspect every seam.",
        turning_point="A hidden stitch passes inspection.",
        outcome="The message reaches the resistance.",
        exit_state="Genevieve earns cautious trust.",
        beat_ids=("arrival",),
        estimated_word_count=900,
    )
