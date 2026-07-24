"""SQLite-backed execution and human-interrupt service for Story Blueprints."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast
from uuid import UUID

import aiosqlite
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.types import Command, Interrupt, StateSnapshot
from open_hollywood_engine.artifacts import ArtifactKind
from open_hollywood_engine.workflows import (
    BLUEPRINT_NODE_DEFINITIONS,
    BLUEPRINT_RETRYABLE_NODES,
    DEFAULT_MAX_GRAPH_STEPS,
    STORY_BLUEPRINT_GRAPH_VERSION,
    STORY_BLUEPRINT_WORKFLOW_NAME,
    ArtifactReference,
    BlueprintCompiledGraph,
    BlueprintDecisionAction,
    BlueprintGraphState,
    BlueprintHumanDecision,
    BlueprintNode,
    BlueprintNodeExecutor,
    BlueprintWorkflowObserver,
    RunControlAction,
    RunControlCommand,
    RunControlStatus,
    RunPauseReason,
    artifact_references_from_state,
    build_blueprint_graph,
    initial_blueprint_fork_state,
    initial_blueprint_retry_state,
    initial_blueprint_state,
)
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from open_hollywood_api.persistence.models import (
    Artifact,
    ArtifactStatus,
    ArtifactVersion,
    HumanDecision,
    HumanDecisionStatus,
    RunStatus,
    WorkflowEvent,
    WorkflowRun,
    WorkflowRunControl,
)
from open_hollywood_api.persistence.secret_policy import active_secret_guard
from open_hollywood_api.services.run_controls import (
    RunControlError,
    RunControlResult,
    RunControlStore,
    WorkflowPausedSignal,
    WorkflowStoppedSignal,
)

_MIN_GRAPH_STEPS = 8
_MAX_GRAPH_STEPS = 64


@dataclass(frozen=True, slots=True)
class BlueprintWorkflowExecution:
    """Durable workflow state after execution, interruption, or approval."""

    workflow_run_id: UUID
    checkpoint_id: str
    artifacts: tuple[ArtifactReference, ...]
    awaiting_approval: bool
    interrupt_id: str | None = None


class BlueprintWorkflowRunError(RuntimeError):
    """Raised for unknown, incompatible, or invalid workflow transitions."""


class SqlAlchemyBlueprintWorkflowObserver(BlueprintWorkflowObserver):
    """Mirror graph lifecycle into WorkflowRun and its append-only event log."""

    def __init__(
        self,
        session_factory: sessionmaker[Session],
        run_controls: RunControlStore,
    ) -> None:
        self._session_factory = session_factory
        self._run_controls = run_controls

    async def node_started(self, workflow_run_id: UUID, node: BlueprintNode) -> None:
        await asyncio.to_thread(self._node_started, workflow_run_id, node)

    def _node_started(self, workflow_run_id: UUID, node: BlueprintNode) -> None:
        self._run_controls.before_node(
            workflow_run_id,
            node.value,
            includes_model_call=(BLUEPRINT_NODE_DEFINITIONS[node].specialist_role is not None),
            default_max_graph_steps=DEFAULT_MAX_GRAPH_STEPS,
        )
        with self._session_factory.begin() as session:
            workflow_run = _require_run(session, workflow_run_id)
            workflow_run.status = RunStatus.RUNNING
            workflow_run.pause_reason = None
            workflow_run.current_node = node.value
            workflow_run.started_at = workflow_run.started_at or datetime.now(UTC)
            workflow_run.error_code = None
            workflow_run.error_message = None
            _add_event(
                session,
                workflow_run_id,
                "workflow.node.started",
                {"node": node.value},
                source=node.value,
            )

    async def node_completed(
        self,
        workflow_run_id: UUID,
        node: BlueprintNode,
        artifacts: tuple[ArtifactReference, ...],
    ) -> None:
        await asyncio.to_thread(self._node_completed, workflow_run_id, node, artifacts)

    def _node_completed(
        self,
        workflow_run_id: UUID,
        node: BlueprintNode,
        artifacts: tuple[ArtifactReference, ...],
    ) -> None:
        with self._session_factory.begin() as session:
            _require_run(session, workflow_run_id)
            _add_event(
                session,
                workflow_run_id,
                "workflow.node.completed",
                {
                    "node": node.value,
                    "output_artifacts": [_artifact_payload(artifact) for artifact in artifacts],
                },
                source=node.value,
            )

    async def awaiting_approval(
        self,
        workflow_run_id: UUID,
        artifacts: tuple[ArtifactReference, ...],
        interrupt_id: str,
    ) -> None:
        await asyncio.to_thread(
            self._awaiting_approval,
            workflow_run_id,
            artifacts,
            interrupt_id,
        )

    def _awaiting_approval(
        self,
        workflow_run_id: UUID,
        artifacts: tuple[ArtifactReference, ...],
        interrupt_id: str,
    ) -> None:
        with self._session_factory.begin() as session:
            workflow_run = _require_run(session, workflow_run_id)
            workflow_run.status = RunStatus.PAUSED
            workflow_run.pause_reason = RunPauseReason.HUMAN_APPROVAL
            workflow_run.current_node = BlueprintNode.APPROVAL.value
            workflow_run.error_code = None
            workflow_run.error_message = None
            if _approval_event_exists(session, workflow_run_id, interrupt_id):
                return
            _add_event(
                session,
                workflow_run_id,
                "workflow.node.started",
                {"node": BlueprintNode.APPROVAL.value},
                source=BlueprintNode.APPROVAL.value,
            )
            _add_event(
                session,
                workflow_run_id,
                "workflow.awaiting_approval",
                {
                    "allowed_actions": [action.value for action in BlueprintDecisionAction],
                    "artifacts": [_artifact_payload(artifact) for artifact in artifacts],
                    "checkpoint": "story_blueprint",
                    "interrupt_id": interrupt_id,
                },
                source=BlueprintNode.APPROVAL.value,
            )

    async def decision_received(
        self,
        workflow_run_id: UUID,
        decision: BlueprintHumanDecision,
    ) -> None:
        await asyncio.to_thread(self._decision_received, workflow_run_id, decision)

    def _decision_received(
        self,
        workflow_run_id: UUID,
        decision: BlueprintHumanDecision,
    ) -> None:
        with self._session_factory.begin() as session:
            _require_run(session, workflow_run_id)
            if _decision_event_exists(session, workflow_run_id, decision.id):
                return
            _add_event(
                session,
                workflow_run_id,
                "workflow.human_decision.received",
                {
                    "action": decision.action.value,
                    "decision_id": str(decision.id),
                    "interrupt_id": decision.interrupt_id,
                },
                source="human",
            )

    async def workflow_failed(self, workflow_run_id: UUID, error: Exception) -> None:
        safe_message = active_secret_guard().redact_text(str(error))[:2000]
        await asyncio.to_thread(self._workflow_failed, workflow_run_id, safe_message)

    def _workflow_failed(self, workflow_run_id: UUID, safe_message: str) -> None:
        with self._session_factory.begin() as session:
            workflow_run = _require_run(session, workflow_run_id)
            workflow_run.status = RunStatus.FAILED
            workflow_run.pause_reason = None
            workflow_run.error_code = "workflow_execution_failed"
            workflow_run.error_message = safe_message
            _add_event(
                session,
                workflow_run_id,
                "workflow.failed",
                {
                    "error_code": "workflow_execution_failed",
                    "node": workflow_run.current_node,
                },
                source=workflow_run.current_node,
            )


class BlueprintWorkflowService:
    """Own the SQLite checkpointer and apply durable human decisions."""

    def __init__(
        self,
        database_path: Path,
        session_factory: sessionmaker[Session],
        executor: BlueprintNodeExecutor,
    ) -> None:
        self._database_path = database_path
        self._session_factory = session_factory
        self._executor = executor
        self._connection: aiosqlite.Connection | None = None
        self._checkpointer: AsyncSqliteSaver | None = None
        self._graph: BlueprintCompiledGraph | None = None
        self._run_controls = RunControlStore(session_factory)
        self._observer = SqlAlchemyBlueprintWorkflowObserver(
            session_factory,
            self._run_controls,
        )

    async def __aenter__(self) -> BlueprintWorkflowService:
        self._connection = await aiosqlite.connect(str(self._database_path))
        await self._connection.execute("PRAGMA journal_mode=WAL")
        await self._connection.execute("PRAGMA busy_timeout=5000")
        await self._connection.commit()
        serializer = JsonPlusSerializer(allowed_msgpack_modules=None)
        self._checkpointer = AsyncSqliteSaver(self._connection, serde=serializer)
        self._graph = build_blueprint_graph(
            self._executor,
            checkpointer=self._checkpointer,
            observer=self._observer,
        )
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: object | None,
    ) -> None:
        del exc_type, exc_value, traceback
        if self._connection is not None:
            await self._connection.close()
        self._connection = None
        self._checkpointer = None
        self._graph = None

    async def execute(self, workflow_run_id: UUID) -> BlueprintWorkflowExecution:
        """Start a graph thread or resume its latest failed super-step."""
        graph, checkpointer = self._require_open()
        max_graph_steps, status = self._run_configuration(workflow_run_id)
        if status is RunStatus.PAUSED:
            raise BlueprintWorkflowRunError("workflow is already awaiting approval")
        if status not in {RunStatus.PENDING, RunStatus.RUNNING, RunStatus.FAILED}:
            raise BlueprintWorkflowRunError(f"workflow cannot execute from status {status.value}")

        config = _graph_config(workflow_run_id, max_graph_steps)
        existing = await checkpointer.aget_tuple(config)
        graph_input: BlueprintGraphState | None
        graph_input = None if existing is not None else initial_blueprint_state(workflow_run_id)
        return await self._invoke(workflow_run_id, graph_input, config=config)

    async def resume(
        self,
        workflow_run_id: UUID,
        decision: BlueprintHumanDecision,
    ) -> BlueprintWorkflowExecution:
        """Idempotently resolve the run's current human interrupt."""
        graph, _ = self._require_open()
        max_graph_steps, status = self._run_configuration(workflow_run_id)
        config = _graph_config(workflow_run_id, max_graph_steps)
        existing_decision = self._existing_decision(decision.id)
        if existing_decision is not None:
            _require_same_decision(existing_decision, workflow_run_id, decision)
        if (
            existing_decision is not None
            and existing_decision.status is HumanDecisionStatus.APPLIED
        ):
            result_run_id = existing_decision.resulting_workflow_run_id or workflow_run_id
            return await self._execution_from_current_state(result_run_id)

        if status is not RunStatus.PAUSED:
            raise BlueprintWorkflowRunError(
                f"workflow cannot accept a human decision from status {status.value}"
            )
        snapshot = await graph.aget_state(config)
        interrupt_value = _single_interrupt(snapshot)
        if interrupt_value.id != decision.interrupt_id:
            raise BlueprintWorkflowRunError("decision does not match the active interrupt")
        if existing_decision is None:
            self._record_decision(
                workflow_run_id,
                decision,
                checkpoint_id=_checkpoint_id(snapshot),
            )

        await self._observer.decision_received(workflow_run_id, decision)
        if decision.action is BlueprintDecisionAction.FORK:
            return await self._fork(workflow_run_id, decision, snapshot)

        try:
            result = await self._invoke(
                workflow_run_id,
                Command(resume=decision.resume_payload()),
                config=config,
            )
        except Exception as exc:
            self._mark_decision_failed(decision.id, exc)
            raise

        self._mark_decision_applied(decision.id, workflow_run_id)
        return result

    async def apply_control(
        self,
        workflow_run_id: UUID,
        command: RunControlCommand,
    ) -> RunControlResult:
        """Apply one idempotent run command at the durable runtime boundary."""
        if command.action is RunControlAction.PAUSE:
            return self._run_controls.request_pause(workflow_run_id, command)
        if command.action is RunControlAction.STOP:
            return self._run_controls.stop(workflow_run_id, command)
        if command.action is RunControlAction.UPDATE_BUDGET:
            return self._run_controls.update_budget(
                workflow_run_id,
                command,
                default_max_graph_steps=DEFAULT_MAX_GRAPH_STEPS,
            )
        if command.action is RunControlAction.RESUME:
            result = self._run_controls.begin_resume(workflow_run_id, command)
            if (
                result.command_status is RunControlStatus.APPLIED
                and result.workflow_status is RunStatus.PENDING
            ):
                try:
                    await self.execute(workflow_run_id)
                except Exception as error:
                    self._run_controls.fail_command(command.id, error)
                    raise
            return self._run_controls.result(command.id)
        if command.action is RunControlAction.RETRY_FROM_NODE:
            return await self._retry_from_node(workflow_run_id, command)
        raise RunControlError(f"unsupported run-control action {command.action.value}")

    async def _invoke(
        self,
        workflow_run_id: UUID,
        graph_input: BlueprintGraphState | Command[Any] | None,
        *,
        config: RunnableConfig,
    ) -> BlueprintWorkflowExecution:
        graph, _ = self._require_open()
        try:
            await graph.ainvoke(graph_input, config=config)
            self._run_controls.execution_boundary(workflow_run_id)
        except (WorkflowPausedSignal, WorkflowStoppedSignal):
            await self._sync_checkpoint_id(workflow_run_id, graph, config)
            return await self._execution_from_current_state(workflow_run_id)
        except Exception as exc:
            await self._observer.workflow_failed(workflow_run_id, exc)
            await self._sync_checkpoint_id(workflow_run_id, graph, config)
            raise

        snapshot = await graph.aget_state(config)
        checkpoint_id = await self._sync_checkpoint_id(
            workflow_run_id,
            graph,
            config,
            snapshot=snapshot,
        )
        state = _snapshot_state(snapshot)
        artifacts = artifact_references_from_state(state)
        if snapshot.interrupts:
            active_interrupt = _single_interrupt(snapshot)
            review_artifacts = _review_artifacts(artifacts)
            await self._observer.awaiting_approval(
                workflow_run_id,
                review_artifacts,
                active_interrupt.id,
            )
            self._apply_checkpoint_decision(state, workflow_run_id)
            return BlueprintWorkflowExecution(
                workflow_run_id=workflow_run_id,
                checkpoint_id=checkpoint_id,
                artifacts=artifacts,
                awaiting_approval=True,
                interrupt_id=active_interrupt.id,
            )

        action = _state_action(state)
        if action is not BlueprintDecisionAction.APPROVE:
            error = BlueprintWorkflowRunError("blueprint graph ended without an approval decision")
            await self._observer.workflow_failed(workflow_run_id, error)
            raise error
        self._approve_blueprint(workflow_run_id, artifacts)
        self._apply_checkpoint_decision(state, workflow_run_id)
        return BlueprintWorkflowExecution(
            workflow_run_id=workflow_run_id,
            checkpoint_id=checkpoint_id,
            artifacts=artifacts,
            awaiting_approval=False,
        )

    async def _retry_from_node(
        self,
        workflow_run_id: UUID,
        command: RunControlCommand,
    ) -> RunControlResult:
        result = self._run_controls.begin_retry(workflow_run_id, command)
        if (
            result.command_status is RunControlStatus.APPLIED
            and result.resulting_workflow_run_id is not None
        ):
            return result
        try:
            target = BlueprintNode(command.target_node or "")
        except ValueError as error:
            self._run_controls.fail_command(command.id, error)
            raise RunControlError("retry target is not a registered blueprint node") from error
        if target not in BLUEPRINT_RETRYABLE_NODES:
            retry_error = RunControlError(f"node {target.value} cannot be retried")
            self._run_controls.fail_command(command.id, retry_error)
            raise retry_error

        graph, checkpointer = self._require_open()
        max_steps, _ = self._run_configuration(workflow_run_id)
        source_snapshot = await graph.aget_state(_graph_config(workflow_run_id, max_steps))
        source_state = _snapshot_state(source_snapshot)
        source_checkpoint_id = _checkpoint_id(source_snapshot)

        with self._session_factory.begin() as session:
            record = session.get(WorkflowRunControl, command.id)
            if record is None:
                raise RunControlError("retry command disappeared before child creation")
            if record.resulting_workflow_run_id is not None:
                child_run_id = record.resulting_workflow_run_id
                child = _require_run(session, child_run_id)
            else:
                source = _require_run(session, workflow_run_id)
                child = WorkflowRun(
                    project_id=source.project_id,
                    conversation_id=source.conversation_id,
                    parent_workflow_run_id=source.id,
                    forked_from_checkpoint_id=source_checkpoint_id,
                    workflow_name=source.workflow_name,
                    graph_version=source.graph_version,
                    status=RunStatus.PENDING,
                    input_state=dict(source.input_state),
                    budget=dict(source.budget),
                )
                session.add(child)
                session.flush()
                child_run_id = child.id
                record.resulting_workflow_run_id = child_run_id
                record.checkpoint_id = source_checkpoint_id
                if source.status is RunStatus.PAUSED:
                    source.status = RunStatus.CANCELLED
                    source.pause_reason = None
                    source.completed_at = datetime.now(UTC)

        child_config = _graph_config(child_run_id, max_steps)
        existing_child_checkpoint = await checkpointer.aget_tuple(child_config)
        try:
            if existing_child_checkpoint is not None and child.status in {
                RunStatus.PAUSED,
                RunStatus.SUCCEEDED,
                RunStatus.CANCELLED,
            }:
                child_snapshot = await graph.aget_state(child_config)
                return self._run_controls.complete_retry(
                    command.id,
                    child_run_id,
                    _checkpoint_id(child_snapshot),
                )
            if existing_child_checkpoint is not None:
                child_execution = await self.execute(child_run_id)
            else:
                retry_state = initial_blueprint_retry_state(
                    child_run_id,
                    artifact_references_from_state(source_state),
                    target,
                    command.id,
                )
                child_execution = await self._invoke(
                    child_run_id,
                    retry_state,
                    config=child_config,
                )
        except Exception as error:
            self._run_controls.fail_command(command.id, error)
            raise
        return self._run_controls.complete_retry(
            command.id,
            child_run_id,
            child_execution.checkpoint_id,
        )

    async def _fork(
        self,
        workflow_run_id: UUID,
        decision: BlueprintHumanDecision,
        source_snapshot: StateSnapshot,
    ) -> BlueprintWorkflowExecution:
        source_state = _snapshot_state(source_snapshot)
        source_artifacts = artifact_references_from_state(source_state)
        source_checkpoint_id = _checkpoint_id(source_snapshot)
        child_run_id = self._create_fork_run(
            workflow_run_id,
            decision,
            source_checkpoint_id,
        )
        child_steps, _ = self._run_configuration(child_run_id)
        child_config = _graph_config(child_run_id, child_steps)
        child_state = initial_blueprint_fork_state(
            child_run_id,
            source_artifacts,
            decision.id,
        )
        try:
            result = await self._invoke(child_run_id, child_state, config=child_config)
        except Exception as exc:
            self._mark_decision_failed(decision.id, exc)
            raise
        self._mark_decision_applied(decision.id, child_run_id)
        return result

    def _create_fork_run(
        self,
        source_run_id: UUID,
        decision: BlueprintHumanDecision,
        source_checkpoint_id: str,
    ) -> UUID:
        with self._session_factory.begin() as session:
            persisted_decision = _require_decision(session, decision.id)
            if persisted_decision.resulting_workflow_run_id is not None:
                return persisted_decision.resulting_workflow_run_id
            source = _require_run(session, source_run_id)
            child = WorkflowRun(
                project_id=source.project_id,
                conversation_id=source.conversation_id,
                parent_workflow_run_id=source.id,
                forked_from_checkpoint_id=source_checkpoint_id,
                workflow_name=source.workflow_name,
                graph_version=source.graph_version,
                status=RunStatus.PENDING,
                input_state={
                    **source.input_state,
                    "fork_decision_id": str(decision.id),
                    "forked_from_workflow_run_id": str(source.id),
                },
                budget=dict(source.budget),
            )
            session.add(child)
            session.flush()
            persisted_decision.resulting_workflow_run_id = child.id
            source.status = RunStatus.CANCELLED
            source.pause_reason = None
            source.completed_at = datetime.now(UTC)
            _add_event(
                session,
                source.id,
                "workflow.forked",
                {
                    "decision_id": str(decision.id),
                    "forked_workflow_run_id": str(child.id),
                    "source_checkpoint_id": source_checkpoint_id,
                },
                source="human",
            )
            _add_event(
                session,
                child.id,
                "workflow.fork.started",
                {
                    "decision_id": str(decision.id),
                    "source_workflow_run_id": str(source.id),
                    "source_checkpoint_id": source_checkpoint_id,
                },
                source="human",
            )
            return child.id

    def _record_decision(
        self,
        workflow_run_id: UUID,
        decision: BlueprintHumanDecision,
        *,
        checkpoint_id: str,
    ) -> HumanDecision:
        try:
            with self._session_factory.begin() as session:
                existing = session.get(HumanDecision, decision.id)
                if existing is not None:
                    _require_same_decision(existing, workflow_run_id, decision)
                    session.expunge(existing)
                    return existing
                interrupt_decision = session.scalar(
                    select(HumanDecision).where(
                        HumanDecision.workflow_run_id == workflow_run_id,
                        HumanDecision.interrupt_id == decision.interrupt_id,
                    )
                )
                if interrupt_decision is not None:
                    raise BlueprintWorkflowRunError(
                        "the active interrupt already has a different decision"
                    )
                record = HumanDecision(
                    id=decision.id,
                    workflow_run_id=workflow_run_id,
                    interrupt_id=decision.interrupt_id,
                    checkpoint_id=checkpoint_id,
                    action=decision.action.value,
                    instruction=decision.instruction,
                    status=HumanDecisionStatus.PENDING,
                )
                session.add(record)
                session.flush()
                session.expunge(record)
                return record
        except IntegrityError as exc:
            with self._session_factory() as session:
                existing = session.get(HumanDecision, decision.id)
                if existing is not None:
                    _require_same_decision(existing, workflow_run_id, decision)
                    session.expunge(existing)
                    return existing
                interrupt_decision = session.scalar(
                    select(HumanDecision).where(
                        HumanDecision.workflow_run_id == workflow_run_id,
                        HumanDecision.interrupt_id == decision.interrupt_id,
                    )
                )
                if interrupt_decision is not None:
                    raise BlueprintWorkflowRunError(
                        "the active interrupt already has a different decision"
                    ) from exc
            raise

    def _existing_decision(self, decision_id: UUID) -> HumanDecision | None:
        with self._session_factory() as session:
            decision = session.get(HumanDecision, decision_id)
            if decision is not None:
                session.expunge(decision)
            return decision

    def _mark_decision_applied(
        self,
        decision_id: UUID,
        resulting_workflow_run_id: UUID,
    ) -> None:
        with self._session_factory.begin() as session:
            decision = _require_decision(session, decision_id)
            decision.status = HumanDecisionStatus.APPLIED
            decision.resulting_workflow_run_id = resulting_workflow_run_id
            decision.applied_at = datetime.now(UTC)
            decision.error_message = None

    def _mark_decision_failed(self, decision_id: UUID, error: Exception) -> None:
        safe_message = active_secret_guard().redact_text(str(error))[:2000]
        with self._session_factory.begin() as session:
            decision = _require_decision(session, decision_id)
            decision.status = HumanDecisionStatus.FAILED
            decision.error_message = safe_message

    def _apply_checkpoint_decision(
        self,
        state: BlueprintGraphState,
        resulting_workflow_run_id: UUID,
    ) -> None:
        raw_decision_id = state.get("human_decision_id")
        if raw_decision_id is None:
            return
        try:
            decision_id = UUID(raw_decision_id)
        except ValueError as exc:
            raise BlueprintWorkflowRunError(
                "checkpoint contains an invalid human_decision_id"
            ) from exc
        with self._session_factory() as session:
            decision = session.get(HumanDecision, decision_id)
            if decision is None or decision.status is HumanDecisionStatus.APPLIED:
                return
        self._mark_decision_applied(decision_id, resulting_workflow_run_id)

    def _approve_blueprint(
        self,
        workflow_run_id: UUID,
        artifacts: tuple[ArtifactReference, ...],
    ) -> None:
        blueprint = _single_blueprint(artifacts)
        with self._session_factory.begin() as session:
            workflow_run = _require_run(session, workflow_run_id)
            version = session.get(ArtifactVersion, blueprint.version_id)
            if version is None:
                raise BlueprintWorkflowRunError("approved blueprint version does not exist")
            artifact = session.get(Artifact, version.artifact_id)
            if artifact is None or artifact.project_id != workflow_run.project_id:
                raise BlueprintWorkflowRunError(
                    "approved blueprint does not belong to the workflow project"
                )
            artifact.status = ArtifactStatus.APPROVED
            workflow_run.status = RunStatus.SUCCEEDED
            workflow_run.pause_reason = None
            workflow_run.completed_at = datetime.now(UTC)
            workflow_run.error_code = None
            workflow_run.error_message = None
            _add_event(
                session,
                workflow_run_id,
                "workflow.blueprint.approved",
                {
                    "artifact": _artifact_payload(blueprint),
                    "decision_id": _state_decision_id_from_run(session, workflow_run_id),
                },
                source="human",
            )

    async def _execution_from_current_state(
        self,
        workflow_run_id: UUID,
    ) -> BlueprintWorkflowExecution:
        graph, _ = self._require_open()
        max_steps, _ = self._run_configuration(workflow_run_id)
        config = _graph_config(workflow_run_id, max_steps)
        snapshot = await graph.aget_state(config)
        checkpoint_id = _checkpoint_id(snapshot)
        state = _snapshot_state(snapshot)
        artifacts = artifact_references_from_state(state)
        interrupt_id = snapshot.interrupts[0].id if snapshot.interrupts else None
        return BlueprintWorkflowExecution(
            workflow_run_id=workflow_run_id,
            checkpoint_id=checkpoint_id,
            artifacts=artifacts,
            awaiting_approval=interrupt_id is not None,
            interrupt_id=interrupt_id,
        )

    def _run_configuration(self, workflow_run_id: UUID) -> tuple[int, RunStatus]:
        with self._session_factory() as session:
            workflow_run = _require_run(session, workflow_run_id)
            if workflow_run.workflow_name != STORY_BLUEPRINT_WORKFLOW_NAME:
                raise BlueprintWorkflowRunError("workflow_run has an incompatible workflow_name")
            if workflow_run.graph_version != STORY_BLUEPRINT_GRAPH_VERSION:
                raise BlueprintWorkflowRunError("workflow_run has an incompatible graph_version")
            raw_steps = workflow_run.budget.get(
                "max_graph_steps",
                DEFAULT_MAX_GRAPH_STEPS,
            )
            if (
                not isinstance(raw_steps, int)
                or isinstance(raw_steps, bool)
                or not _MIN_GRAPH_STEPS <= raw_steps <= _MAX_GRAPH_STEPS
            ):
                raise BlueprintWorkflowRunError(
                    f"max_graph_steps must be between {_MIN_GRAPH_STEPS} and {_MAX_GRAPH_STEPS}"
                )
            return raw_steps, workflow_run.status

    async def _sync_checkpoint_id(
        self,
        workflow_run_id: UUID,
        graph: BlueprintCompiledGraph,
        config: RunnableConfig,
        *,
        snapshot: StateSnapshot | None = None,
    ) -> str:
        current = snapshot or await graph.aget_state(config)
        checkpoint_id = _checkpoint_id(current)
        with self._session_factory.begin() as session:
            workflow_run = _require_run(session, workflow_run_id)
            workflow_run.checkpoint_id = checkpoint_id
        return checkpoint_id

    def _require_open(self) -> tuple[BlueprintCompiledGraph, AsyncSqliteSaver]:
        if self._graph is None or self._checkpointer is None:
            raise RuntimeError("BlueprintWorkflowService must be used as an async context manager")
        return self._graph, self._checkpointer


def _graph_config(workflow_run_id: UUID, max_graph_steps: int) -> RunnableConfig:
    return {
        "configurable": {"thread_id": str(workflow_run_id)},
        "recursion_limit": max_graph_steps,
    }


def _snapshot_state(snapshot: StateSnapshot) -> BlueprintGraphState:
    if not isinstance(snapshot.values, dict):
        raise BlueprintWorkflowRunError("LangGraph checkpoint state is invalid")
    return cast(BlueprintGraphState, snapshot.values)


def _checkpoint_id(snapshot: StateSnapshot) -> str:
    configurable = snapshot.config.get("configurable", {})
    checkpoint_id = configurable.get("checkpoint_id")
    if not isinstance(checkpoint_id, str) or not checkpoint_id:
        raise BlueprintWorkflowRunError("LangGraph did not persist a checkpoint ID")
    return checkpoint_id


def _single_interrupt(snapshot: StateSnapshot) -> Interrupt:
    if len(snapshot.interrupts) != 1:
        raise BlueprintWorkflowRunError("workflow must expose exactly one active human interrupt")
    active_interrupt = snapshot.interrupts[0]
    if not isinstance(active_interrupt.value, dict):
        raise BlueprintWorkflowRunError("human interrupt payload is invalid")
    return active_interrupt


def _state_action(state: BlueprintGraphState) -> BlueprintDecisionAction | None:
    raw_action = state.get("human_action")
    if raw_action is None:
        return None
    try:
        return BlueprintDecisionAction(raw_action)
    except ValueError as exc:
        raise BlueprintWorkflowRunError("checkpoint contains an invalid human action") from exc


def _review_artifacts(
    artifacts: tuple[ArtifactReference, ...],
) -> tuple[ArtifactReference, ...]:
    return tuple(
        artifact
        for artifact in artifacts
        if artifact.kind in {ArtifactKind.STORY_BLUEPRINT, ArtifactKind.CRITIQUE}
    )


def _single_blueprint(
    artifacts: tuple[ArtifactReference, ...],
) -> ArtifactReference:
    blueprints = tuple(
        artifact for artifact in artifacts if artifact.kind is ArtifactKind.STORY_BLUEPRINT
    )
    if len(blueprints) != 1:
        raise BlueprintWorkflowRunError(
            "approval requires exactly one active Story Blueprint version"
        )
    return blueprints[0]


def _require_run(session: Session, workflow_run_id: UUID) -> WorkflowRun:
    workflow_run = session.get(WorkflowRun, workflow_run_id)
    if workflow_run is None:
        raise BlueprintWorkflowRunError(f"unknown workflow run {workflow_run_id}")
    return workflow_run


def _require_decision(session: Session, decision_id: UUID) -> HumanDecision:
    decision = session.get(HumanDecision, decision_id)
    if decision is None:
        raise BlueprintWorkflowRunError(f"unknown human decision {decision_id}")
    return decision


def _require_same_decision(
    record: HumanDecision,
    workflow_run_id: UUID,
    decision: BlueprintHumanDecision,
) -> None:
    if (
        record.workflow_run_id != workflow_run_id
        or record.interrupt_id != decision.interrupt_id
        or record.action != decision.action.value
        or record.instruction != decision.instruction
    ):
        raise BlueprintWorkflowRunError("decision ID was already used with different command data")


def _approval_event_exists(
    session: Session,
    workflow_run_id: UUID,
    interrupt_id: str,
) -> bool:
    events = session.scalars(
        select(WorkflowEvent).where(
            WorkflowEvent.workflow_run_id == workflow_run_id,
            WorkflowEvent.event_type == "workflow.awaiting_approval",
        )
    )
    return any(event.payload.get("interrupt_id") == interrupt_id for event in events)


def _decision_event_exists(
    session: Session,
    workflow_run_id: UUID,
    decision_id: UUID,
) -> bool:
    events = session.scalars(
        select(WorkflowEvent).where(
            WorkflowEvent.workflow_run_id == workflow_run_id,
            WorkflowEvent.event_type == "workflow.human_decision.received",
        )
    )
    return any(event.payload.get("decision_id") == str(decision_id) for event in events)


def _state_decision_id_from_run(session: Session, workflow_run_id: UUID) -> str:
    decision = session.scalar(
        select(HumanDecision)
        .where(HumanDecision.workflow_run_id == workflow_run_id)
        .order_by(HumanDecision.created_at.desc())
        .limit(1)
    )
    if decision is None:
        raise BlueprintWorkflowRunError("approved workflow has no human decision")
    return str(decision.id)


def _add_event(
    session: Session,
    workflow_run_id: UUID,
    event_type: str,
    payload: dict[str, Any],
    *,
    source: str | None,
) -> None:
    session.add(
        WorkflowEvent(
            workflow_run_id=workflow_run_id,
            event_type=event_type,
            source=source,
            schema_version="1",
            payload=payload,
        )
    )


def _artifact_payload(artifact: ArtifactReference) -> dict[str, str]:
    return {
        "artifact_kind": artifact.kind.value,
        "artifact_key": artifact.artifact_key,
        "artifact_version_id": str(artifact.version_id),
        "schema_version": artifact.schema_version,
    }
