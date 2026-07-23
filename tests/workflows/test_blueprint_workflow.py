"""Integration tests for the first persisted story-blueprint LangGraph."""

from __future__ import annotations

import asyncio
import hashlib
import json
from collections import Counter
from pathlib import Path
from uuid import NAMESPACE_URL, UUID, uuid4, uuid5

import pytest
from open_hollywood_api.persistence.database import create_session_factory
from open_hollywood_api.persistence.models import (
    Artifact,
    ArtifactStatus,
    ArtifactVersion,
    HumanDecision,
    HumanDecisionStatus,
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
    BlueprintDecisionAction,
    BlueprintHumanDecision,
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
        self.tasks: list[BlueprintNodeTask] = []

    async def execute(self, task: BlueprintNodeTask) -> BlueprintNodeResult:
        self.calls.append(task.node)
        self.tasks.append(task)
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
                versions = session.scalars(
                    select(ArtifactVersion)
                    .where(ArtifactVersion.artifact_id == existing.id)
                    .order_by(ArtifactVersion.version_number.desc())
                ).all()
                latest = versions[0]
                if task.human_decision_id is None or latest.content.get("human_decision_id") == str(
                    task.human_decision_id
                ):
                    return ArtifactReference(
                        kind=kind,
                        artifact_key=artifact_key,
                        version_id=latest.id,
                        schema_version=latest.schema_version,
                    )
                artifact = existing
                version_number = latest.version_number + 1
                parent_version_id = latest.id
            else:
                artifact = Artifact(
                    project_id=workflow_run.project_id,
                    artifact_key=artifact_key,
                    artifact_type=kind.value,
                    title=f"{task.node.value} {kind.value}",
                    status=ArtifactStatus.DRAFT,
                )
                version_number = 1
                parent_version_id = None
            content = {
                "human_decision_id": (
                    str(task.human_decision_id) if task.human_decision_id is not None else None
                ),
                "input_artifact_version_ids": [
                    str(reference.version_id) for reference in task.input_artifacts
                ],
                "node": task.node.value,
                "reviewed_artifact_version_ids": [
                    str(reference.version_id) for reference in task.reviewed_artifacts
                ],
                "specialist_role": task.specialist_role,
            }
            canonical_content = json.dumps(content, separators=(",", ":"), sort_keys=True)
            version = ArtifactVersion(
                id=uuid5(
                    NAMESPACE_URL,
                    f"{task.workflow_run_id}:{artifact_key}:{version_number}",
                ),
                artifact=artifact,
                parent_version_id=parent_version_id,
                version_number=version_number,
                schema_version="1",
                content=content,
                content_sha256=hashlib.sha256(canonical_content.encode()).hexdigest(),
                change_summary=f"Created by {task.node.value}",
            )
            session.add(artifact)
            session.add(version)
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


def _decision(
    execution_interrupt_id: str | None,
    action: BlueprintDecisionAction,
    instruction: str | None = None,
) -> BlueprintHumanDecision:
    assert execution_interrupt_id is not None
    return BlueprintHumanDecision(
        id=uuid4(),
        interrupt_id=execution_interrupt_id,
        action=action,
        instruction=instruction,
    )


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


async def test_approve_resumes_after_restart_and_approves_exact_blueprint_version(
    migrated_database_path: Path,
    database_engine: Engine,
) -> None:
    session_factory = _session_factory(database_engine)
    workflow_run_id = _persist_run(session_factory)
    executor = PersistingExecutor(session_factory)

    async with BlueprintWorkflowService(
        migrated_database_path,
        session_factory,
        executor,
    ) as service:
        interrupted = await service.execute(workflow_run_id)

    blueprint_before = next(
        artifact
        for artifact in interrupted.artifacts
        if artifact.kind is ArtifactKind.STORY_BLUEPRINT
    )
    decision = _decision(interrupted.interrupt_id, BlueprintDecisionAction.APPROVE)

    async with BlueprintWorkflowService(
        migrated_database_path,
        session_factory,
        executor,
    ) as restarted_service:
        approved = await restarted_service.resume(workflow_run_id, decision)
        duplicate = await restarted_service.resume(workflow_run_id, decision)

    assert approved.awaiting_approval is False
    assert duplicate == approved
    assert executor.calls.count(BlueprintNode.INTEGRATION) == 1
    with session_factory() as session:
        workflow_run = session.get(WorkflowRun, workflow_run_id)
        persisted_decision = session.get(HumanDecision, decision.id)
        blueprint_version = session.get(ArtifactVersion, blueprint_before.version_id)
        assert workflow_run is not None
        assert workflow_run.status is RunStatus.SUCCEEDED
        assert workflow_run.completed_at is not None
        assert persisted_decision is not None
        assert persisted_decision.status is HumanDecisionStatus.APPLIED
        assert persisted_decision.instruction is None
        assert blueprint_version is not None
        assert blueprint_version.artifact.status is ArtifactStatus.APPROVED
        events = session.scalars(
            select(WorkflowEvent)
            .where(WorkflowEvent.workflow_run_id == workflow_run_id)
            .order_by(WorkflowEvent.id)
        ).all()
        assert sum(event.event_type == "workflow.human_decision.received" for event in events) == 1
        assert events[-1].event_type == "workflow.blueprint.approved"


async def test_revise_reruns_only_integration_and_evaluation_with_durable_feedback(
    migrated_database_path: Path,
    database_engine: Engine,
) -> None:
    session_factory = _session_factory(database_engine)
    workflow_run_id = _persist_run(session_factory)
    executor = PersistingExecutor(session_factory)

    async with BlueprintWorkflowService(
        migrated_database_path,
        session_factory,
        executor,
    ) as service:
        interrupted = await service.execute(workflow_run_id)
        initial_call_count = len(executor.calls)
        decision = _decision(
            interrupted.interrupt_id,
            BlueprintDecisionAction.REVISE,
            "Make the ending tragic but preserve the stroller image.",
        )
        assert decision.instruction is not None
        revised = await service.resume(workflow_run_id, decision)

    assert revised.awaiting_approval is True
    assert revised.interrupt_id != interrupted.interrupt_id
    assert executor.calls[initial_call_count:] == [
        BlueprintNode.INTEGRATION,
        BlueprintNode.EVALUATION,
    ]
    revision_task = executor.tasks[initial_call_count]
    assert revision_task.human_decision_id == decision.id
    assert {artifact.kind for artifact in revision_task.reviewed_artifacts} == {
        ArtifactKind.STORY_BLUEPRINT,
        ArtifactKind.CRITIQUE,
    }
    active_blueprint = next(
        artifact for artifact in revised.artifacts if artifact.kind is ArtifactKind.STORY_BLUEPRINT
    )
    with session_factory() as session:
        persisted_decision = session.get(HumanDecision, decision.id)
        active_version = session.get(ArtifactVersion, active_blueprint.version_id)
        workflow_run = session.get(WorkflowRun, workflow_run_id)
        assert persisted_decision is not None
        assert persisted_decision.status is HumanDecisionStatus.APPLIED
        assert persisted_decision.instruction == decision.instruction
        assert active_version is not None
        assert active_version.version_number == 2
        assert active_version.parent_version_id is not None
        assert workflow_run is not None
        assert workflow_run.status is RunStatus.PAUSED
        assert session.scalar(select(func.count(ArtifactVersion.id))) == 11
        event_payloads = session.scalars(
            select(WorkflowEvent.payload).where(WorkflowEvent.workflow_run_id == workflow_run_id)
        ).all()
        assert all(decision.instruction not in json.dumps(payload) for payload in event_payloads)

    with database_engine.connect() as connection:
        checkpoint_bytes = connection.execute(
            text("SELECT checkpoint FROM checkpoints WHERE thread_id = :thread_id"),
            {"thread_id": str(workflow_run_id)},
        ).scalars()
        assert all(decision.instruction.encode() not in value for value in checkpoint_bytes)


async def test_reject_regenerates_from_premise_with_active_version_replacement(
    migrated_database_path: Path,
    database_engine: Engine,
) -> None:
    session_factory = _session_factory(database_engine)
    workflow_run_id = _persist_run(session_factory)
    executor = PersistingExecutor(session_factory)

    async with BlueprintWorkflowService(
        migrated_database_path,
        session_factory,
        executor,
    ) as service:
        interrupted = await service.execute(workflow_run_id)
        initial_call_count = len(executor.calls)
        rejected = await service.resume(
            workflow_run_id,
            _decision(
                interrupted.interrupt_id,
                BlueprintDecisionAction.REJECT,
                "Regenerate with a grounded explanation and no supernatural cause.",
            ),
        )

    rerun_calls = executor.calls[initial_call_count:]
    assert rerun_calls[0] is BlueprintNode.PREMISE
    assert set(rerun_calls[1:3]) == {
        BlueprintNode.WORLD_SPECIALIST,
        BlueprintNode.CHARACTER_SPECIALIST,
    }
    assert rerun_calls[-2:] == [
        BlueprintNode.INTEGRATION,
        BlueprintNode.EVALUATION,
    ]
    assert rejected.awaiting_approval is True
    assert len(rejected.artifacts) == 9
    assert len({artifact.artifact_key for artifact in rejected.artifacts}) == 9
    with session_factory() as session:
        assert session.scalar(select(func.count(ArtifactVersion.id))) == 17


async def test_fork_creates_child_thread_and_preserves_source_lineage(
    migrated_database_path: Path,
    database_engine: Engine,
) -> None:
    session_factory = _session_factory(database_engine)
    source_run_id = _persist_run(session_factory)
    executor = PersistingExecutor(session_factory)

    async with BlueprintWorkflowService(
        migrated_database_path,
        session_factory,
        executor,
    ) as service:
        interrupted = await service.execute(source_run_id)
        source_checkpoint_id = interrupted.checkpoint_id
        initial_call_count = len(executor.calls)
        decision = _decision(
            interrupted.interrupt_id,
            BlueprintDecisionAction.FORK,
            "Fork toward a psychological-horror explanation.",
        )
        forked = await service.resume(source_run_id, decision)
        duplicate = await service.resume(source_run_id, decision)

    assert forked.workflow_run_id != source_run_id
    assert duplicate == forked
    assert forked.awaiting_approval is True
    assert executor.calls[initial_call_count] is BlueprintNode.PREMISE
    with session_factory() as session:
        source_run = session.get(WorkflowRun, source_run_id)
        child_run = session.get(WorkflowRun, forked.workflow_run_id)
        persisted_decision = session.get(HumanDecision, decision.id)
        assert source_run is not None
        assert source_run.status is RunStatus.CANCELLED
        assert source_run.checkpoint_id == source_checkpoint_id
        assert child_run is not None
        assert child_run.parent_workflow_run_id == source_run_id
        assert child_run.forked_from_checkpoint_id == source_checkpoint_id
        assert child_run.status is RunStatus.PAUSED
        assert persisted_decision is not None
        assert persisted_decision.status is HumanDecisionStatus.APPLIED
        assert persisted_decision.resulting_workflow_run_id == child_run.id
        assert session.scalar(select(func.count(WorkflowRun.id))) == 2
        assert session.scalar(select(func.count(ArtifactVersion.id))) == 17


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
