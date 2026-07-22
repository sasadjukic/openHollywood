"""Integration tests for the first persisted story-blueprint LangGraph."""

from __future__ import annotations

import asyncio
import hashlib
import json
from collections import Counter
from pathlib import Path
from uuid import NAMESPACE_URL, UUID, uuid5

import pytest
from open_hollywood_api.persistence.database import create_session_factory
from open_hollywood_api.persistence.models import (
    Artifact,
    ArtifactStatus,
    ArtifactVersion,
    Project,
    RunStatus,
    WorkflowEvent,
    WorkflowRun,
)
from open_hollywood_api.services.blueprint_workflow import BlueprintWorkflowService
from open_hollywood_engine.artifacts import ArtifactKind
from open_hollywood_engine.workflows import (
    DEFAULT_MAX_GRAPH_STEPS,
    STORY_BLUEPRINT_GRAPH_VERSION,
    STORY_BLUEPRINT_WORKFLOW_NAME,
    ArtifactReference,
    BlueprintNode,
    BlueprintNodeExecutor,
    BlueprintNodeResult,
    BlueprintNodeTask,
    RetryableSpecialistError,
)
from sqlalchemy import Engine, func, select, text
from sqlalchemy.orm import Session, sessionmaker

pytestmark = pytest.mark.anyio

_OUTPUT_KINDS: dict[BlueprintNode, tuple[ArtifactKind, ...]] = {
    BlueprintNode.BRIEF: (ArtifactKind.CREATIVE_BRIEF,),
    BlueprintNode.PREMISE: (ArtifactKind.PREMISE,),
    BlueprintNode.WORLD_SPECIALIST: (ArtifactKind.LOCATION, ArtifactKind.WORLD_RULE),
    BlueprintNode.CHARACTER_SPECIALIST: (
        ArtifactKind.CHARACTER,
        ArtifactKind.CHARACTER,
        ArtifactKind.RELATIONSHIP,
    ),
    BlueprintNode.INTEGRATION: (ArtifactKind.STORY_BLUEPRINT,),
    BlueprintNode.EVALUATION: (ArtifactKind.CRITIQUE,),
}


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


class PersistingExecutor(BlueprintNodeExecutor):
    """Deterministic test specialist that honors the durable-output contract."""

    def __init__(
        self,
        session_factory: sessionmaker[Session],
        *,
        fail_once: dict[BlueprintNode, Exception] | None = None,
        fail_after_completed: dict[BlueprintNode, BlueprintNode] | None = None,
        delays: dict[BlueprintNode, float] | None = None,
    ) -> None:
        self._session_factory = session_factory
        self._fail_once = dict(fail_once or {})
        self._fail_after_completed = dict(fail_after_completed or {})
        self._delays = dict(delays or {})
        self._completed = {node: asyncio.Event() for node in BlueprintNode}
        self.calls: list[BlueprintNode] = []

    async def execute(self, task: BlueprintNodeTask) -> BlueprintNodeResult:
        self.calls.append(task.node)
        delay = self._delays.get(task.node, 0)
        if delay:
            await asyncio.sleep(delay)
        failure = self._fail_once.pop(task.node, None)
        if failure is not None:
            dependency = self._fail_after_completed.get(task.node)
            if dependency is not None:
                await self._completed[dependency].wait()
                await asyncio.sleep(0.01)
            raise failure

        output_kinds = _OUTPUT_KINDS[task.node]
        references = await asyncio.to_thread(
            self._persist_outputs,
            task,
            output_kinds,
        )
        self._completed[task.node].set()
        return BlueprintNodeResult(artifacts=references)

    def _persist_outputs(
        self,
        task: BlueprintNodeTask,
        output_kinds: tuple[ArtifactKind, ...],
    ) -> tuple[ArtifactReference, ...]:
        return tuple(
            self._persist_output(task, kind, index)
            for index, kind in enumerate(output_kinds, start=1)
        )

    def _persist_output(
        self,
        task: BlueprintNodeTask,
        kind: ArtifactKind,
        index: int,
    ) -> ArtifactReference:
        suffix = f"_{index}" if _OUTPUT_KINDS[task.node].count(kind) > 1 else ""
        artifact_key = f"{task.node.value}_{kind.value}{suffix}"
        with self._session_factory.begin() as session:
            workflow_run = session.get(WorkflowRun, task.workflow_run_id)
            assert workflow_run is not None
            existing = session.scalar(
                select(Artifact).where(
                    Artifact.project_id == workflow_run.project_id,
                    Artifact.artifact_key == artifact_key,
                )
            )
            if existing is not None:
                version = session.scalar(
                    select(ArtifactVersion)
                    .where(ArtifactVersion.artifact_id == existing.id)
                    .order_by(ArtifactVersion.version_number.desc())
                    .limit(1)
                )
                assert version is not None
                return ArtifactReference(
                    kind=kind,
                    artifact_key=artifact_key,
                    version_id=version.id,
                    schema_version=version.schema_version,
                )

            artifact = Artifact(
                project_id=workflow_run.project_id,
                artifact_key=artifact_key,
                artifact_type=kind.value,
                title=f"{task.node.value} {kind.value}",
                status=ArtifactStatus.DRAFT,
            )
            content = {
                "input_artifact_version_ids": [
                    str(reference.version_id) for reference in task.input_artifacts
                ],
                "node": task.node.value,
                "specialist_role": task.specialist_role,
            }
            canonical_content = json.dumps(content, separators=(",", ":"), sort_keys=True)
            version = ArtifactVersion(
                id=uuid5(NAMESPACE_URL, f"{task.workflow_run_id}:{artifact_key}:1"),
                artifact=artifact,
                version_number=1,
                schema_version="1",
                content=content,
                content_sha256=hashlib.sha256(canonical_content.encode()).hexdigest(),
                change_summary=f"Created by {task.node.value}",
            )
            session.add(artifact)
            session.flush()
            return ArtifactReference(
                kind=kind,
                artifact_key=artifact_key,
                version_id=version.id,
                schema_version=version.schema_version,
            )


def _persist_run(session_factory: sessionmaker[Session]) -> UUID:
    with session_factory.begin() as session:
        project = Project(name="The Untouched Stroller")
        workflow_run = WorkflowRun(
            project=project,
            workflow_name=STORY_BLUEPRINT_WORKFLOW_NAME,
            graph_version=STORY_BLUEPRINT_GRAPH_VERSION,
            status=RunStatus.PENDING,
            input_state={
                "premise": "A pristine stroller waits outside an abandoned building.",
                "user_constraints": ["Short prose only."],
            },
            budget={"max_graph_steps": DEFAULT_MAX_GRAPH_STEPS},
        )
        session.add(project)
        session.flush()
        return workflow_run.id


def _session_factory(database_engine: Engine) -> sessionmaker[Session]:
    return create_session_factory(database_engine)


async def test_graph_persists_checkpoints_artifacts_events_and_review_state(
    migrated_database_path: Path,
    database_engine: Engine,
) -> None:
    session_factory = _session_factory(database_engine)
    workflow_run_id = _persist_run(session_factory)
    executor = PersistingExecutor(
        session_factory,
        delays={
            BlueprintNode.WORLD_SPECIALIST: 0.02,
            BlueprintNode.CHARACTER_SPECIALIST: 0.001,
        },
    )

    async with BlueprintWorkflowService(
        migrated_database_path,
        session_factory,
        executor,
    ) as service:
        result = await service.execute(workflow_run_id)

    assert result.awaiting_approval is True
    assert result.checkpoint_id
    assert len(result.artifacts) == 9
    assert Counter(reference.kind for reference in result.artifacts) == Counter(
        {
            ArtifactKind.CREATIVE_BRIEF: 1,
            ArtifactKind.PREMISE: 1,
            ArtifactKind.LOCATION: 1,
            ArtifactKind.WORLD_RULE: 1,
            ArtifactKind.CHARACTER: 2,
            ArtifactKind.RELATIONSHIP: 1,
            ArtifactKind.STORY_BLUEPRINT: 1,
            ArtifactKind.CRITIQUE: 1,
        }
    )
    assert executor.calls[:2] == [BlueprintNode.BRIEF, BlueprintNode.PREMISE]
    assert set(executor.calls[2:4]) == {
        BlueprintNode.WORLD_SPECIALIST,
        BlueprintNode.CHARACTER_SPECIALIST,
    }
    assert executor.calls[-2:] == [BlueprintNode.INTEGRATION, BlueprintNode.EVALUATION]

    with session_factory() as session:
        workflow_run = session.get(WorkflowRun, workflow_run_id)
        assert workflow_run is not None
        assert workflow_run.status is RunStatus.PAUSED
        assert workflow_run.current_node == BlueprintNode.APPROVAL.value
        assert workflow_run.checkpoint_id == result.checkpoint_id
        assert session.scalar(select(func.count(ArtifactVersion.id))) == 9
        events = session.scalars(
            select(WorkflowEvent)
            .where(WorkflowEvent.workflow_run_id == workflow_run_id)
            .order_by(WorkflowEvent.id)
        ).all()
        assert sum(event.event_type == "workflow.node.started" for event in events) == 8
        assert sum(event.event_type == "workflow.node.completed" for event in events) == 7
        assert events[-1].event_type == "workflow.awaiting_approval"
        assert all("premise" not in event.payload for event in events)

    with database_engine.connect() as connection:
        checkpoint_count = connection.scalar(
            text("SELECT COUNT(*) FROM checkpoints WHERE thread_id = :thread_id"),
            {"thread_id": str(workflow_run_id)},
        )
        checkpoint_bytes = connection.execute(
            text("SELECT checkpoint FROM checkpoints WHERE thread_id = :thread_id"),
            {"thread_id": str(workflow_run_id)},
        ).scalars()
        assert checkpoint_count is not None and checkpoint_count >= 8
        assert all(b"pristine stroller" not in value for value in checkpoint_bytes)


async def test_failed_parallel_superstep_resumes_without_repeating_successful_sibling(
    migrated_database_path: Path,
    database_engine: Engine,
) -> None:
    session_factory = _session_factory(database_engine)
    workflow_run_id = _persist_run(session_factory)
    first_executor = PersistingExecutor(
        session_factory,
        fail_once={BlueprintNode.CHARACTER_SPECIALIST: RuntimeError("character model unavailable")},
        fail_after_completed={
            BlueprintNode.CHARACTER_SPECIALIST: BlueprintNode.WORLD_SPECIALIST,
        },
    )

    async with BlueprintWorkflowService(
        migrated_database_path,
        session_factory,
        first_executor,
    ) as service:
        with pytest.raises(RuntimeError, match="character model unavailable"):
            await service.execute(workflow_run_id)

    with session_factory() as session:
        failed_run = session.get(WorkflowRun, workflow_run_id)
        assert failed_run is not None
        assert failed_run.status is RunStatus.FAILED
        assert failed_run.checkpoint_id is not None

    resumed_executor = PersistingExecutor(session_factory)
    async with BlueprintWorkflowService(
        migrated_database_path,
        session_factory,
        resumed_executor,
    ) as service:
        result = await service.execute(workflow_run_id)

    assert result.awaiting_approval is True
    assert resumed_executor.calls == [
        BlueprintNode.CHARACTER_SPECIALIST,
        BlueprintNode.INTEGRATION,
        BlueprintNode.EVALUATION,
    ]
    with session_factory() as session:
        resumed_run = session.get(WorkflowRun, workflow_run_id)
        assert resumed_run is not None
        assert resumed_run.status is RunStatus.PAUSED
        assert session.scalar(select(func.count(ArtifactVersion.id))) == 9


async def test_retry_policy_retries_only_explicit_retryable_specialist_failures(
    migrated_database_path: Path,
    database_engine: Engine,
) -> None:
    session_factory = _session_factory(database_engine)
    workflow_run_id = _persist_run(session_factory)
    executor = PersistingExecutor(
        session_factory,
        fail_once={
            BlueprintNode.WORLD_SPECIALIST: RetryableSpecialistError("temporary provider failure")
        },
    )

    async with BlueprintWorkflowService(
        migrated_database_path,
        session_factory,
        executor,
    ) as service:
        result = await service.execute(workflow_run_id)

    assert result.awaiting_approval is True
    assert executor.calls.count(BlueprintNode.WORLD_SPECIALIST) == 2


async def test_service_rejects_incompatible_run_and_closed_usage(
    migrated_database_path: Path,
    database_engine: Engine,
) -> None:
    session_factory = _session_factory(database_engine)
    workflow_run_id = _persist_run(session_factory)
    executor = PersistingExecutor(session_factory)
    service = BlueprintWorkflowService(migrated_database_path, session_factory, executor)

    with pytest.raises(RuntimeError, match="async context manager"):
        await service.execute(workflow_run_id)

    with session_factory.begin() as session:
        workflow_run = session.get(WorkflowRun, workflow_run_id)
        assert workflow_run is not None
        workflow_run.graph_version = "unsupported"

    async with service:
        with pytest.raises(RuntimeError, match="incompatible graph_version"):
            await service.execute(workflow_run_id)
