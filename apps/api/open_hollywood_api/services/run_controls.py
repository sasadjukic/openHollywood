"""Durable idempotent workflow controls and aggregate-budget enforcement."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID

from open_hollywood_engine.workflows import (
    BudgetLimit,
    RunBudget,
    RunControlAction,
    RunControlCommand,
    RunControlStatus,
    RunPauseReason,
    RunUsage,
    budget_can_cover_usage,
    projected_budget_limits,
)
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from open_hollywood_api.persistence.models import (
    InvocationStatus,
    RunStatus,
    WorkflowEvent,
    WorkflowRun,
    WorkflowRunControl,
)
from open_hollywood_api.persistence.secret_policy import active_secret_guard


@dataclass(frozen=True, slots=True)
class RunControlResult:
    """UI-safe state after applying or recording one control command."""

    command_id: UUID
    workflow_run_id: UUID
    action: RunControlAction
    command_status: RunControlStatus
    workflow_status: RunStatus
    pause_reason: RunPauseReason | None
    target_node: str | None
    resulting_workflow_run_id: UUID | None
    checkpoint_id: str | None
    budget: RunBudget
    usage: RunUsage
    error_message: str | None


class RunControlError(RuntimeError):
    """Raised when a command conflicts with durable workflow state."""


class WorkflowPausedSignal(RuntimeError):
    """Internal cooperative signal raised before an unaffordable or paused node."""


class WorkflowStoppedSignal(RuntimeError):
    """Internal cooperative signal raised after a run is cancelled."""


class RunControlStore:
    """Persist commands and enforce them at safe workflow node boundaries."""

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def request_pause(
        self,
        workflow_run_id: UUID,
        command: RunControlCommand,
    ) -> RunControlResult:
        """Pause before start or persist a cooperative boundary request."""
        if command.action is not RunControlAction.PAUSE:
            raise ValueError("request_pause requires a pause command")
        with self._session_factory.begin() as session:
            record, existing = _record_command(session, workflow_run_id, command)
            if existing:
                return _result(session, record)
            workflow_run = _require_run(session, workflow_run_id)
            if workflow_run.status is RunStatus.PENDING:
                _apply_pause(
                    session,
                    workflow_run,
                    RunPauseReason.USER,
                    command=record,
                )
            elif workflow_run.status is RunStatus.RUNNING:
                _add_event(
                    session,
                    workflow_run_id,
                    "workflow.pause.requested",
                    {"command_id": str(command.id)},
                )
            else:
                raise RunControlError(
                    f"workflow cannot pause from status {workflow_run.status.value}"
                )
            return _result(session, record)

    def stop(
        self,
        workflow_run_id: UUID,
        command: RunControlCommand,
    ) -> RunControlResult:
        """Cancel a run immediately and let active work stop cooperatively."""
        if command.action is not RunControlAction.STOP:
            raise ValueError("stop requires a stop command")
        with self._session_factory.begin() as session:
            record, existing = _record_command(session, workflow_run_id, command)
            if existing:
                return _result(session, record)
            workflow_run = _require_run(session, workflow_run_id)
            if workflow_run.status in {RunStatus.SUCCEEDED, RunStatus.CANCELLED}:
                raise RunControlError(
                    f"workflow cannot stop from status {workflow_run.status.value}"
                )
            workflow_run.status = RunStatus.CANCELLED
            workflow_run.pause_reason = None
            workflow_run.completed_at = datetime.now(UTC)
            workflow_run.error_code = None
            workflow_run.error_message = None
            for invocation in workflow_run.invocations:
                if invocation.status in {
                    InvocationStatus.PENDING,
                    InvocationStatus.RUNNING,
                }:
                    invocation.status = InvocationStatus.CANCELLED
                    invocation.completed_at = datetime.now(UTC)
                    invocation.error_code = "workflow_stopped"
                    invocation.error_message = "Cancelled by workflow stop command."
            _mark_applied(record, workflow_run.checkpoint_id)
            _add_event(
                session,
                workflow_run_id,
                "workflow.stopped",
                {
                    "command_id": str(command.id),
                    "node": workflow_run.current_node,
                },
            )
            return _result(session, record)

    def update_budget(
        self,
        workflow_run_id: UUID,
        command: RunControlCommand,
        *,
        default_max_graph_steps: int,
    ) -> RunControlResult:
        """Persist a validated hard-budget update that covers consumed usage."""
        if command.action is not RunControlAction.UPDATE_BUDGET:
            raise ValueError("update_budget requires an update_budget command")
        with self._session_factory.begin() as session:
            record, existing = _record_command(session, workflow_run_id, command)
            if existing:
                return _result(
                    session,
                    record,
                    default_max_graph_steps=default_max_graph_steps,
                )
            workflow_run = _require_run(session, workflow_run_id)
            if workflow_run.status in {RunStatus.SUCCEEDED, RunStatus.CANCELLED}:
                raise RunControlError(
                    f"workflow budget cannot change from status {workflow_run.status.value}"
                )
            budget = RunBudget.from_data(
                workflow_run.budget,
                default_max_graph_steps=default_max_graph_steps,
            ).replace(command.budget_updates or {})
            usage = run_usage(workflow_run)
            if not budget_can_cover_usage(budget, usage):
                raise RunControlError("updated budget cannot be lower than consumed usage")
            workflow_run.budget = budget.to_data()
            _mark_applied(record, workflow_run.checkpoint_id)
            _add_event(
                session,
                workflow_run_id,
                "workflow.budget.updated",
                {
                    "budget": budget.to_data(),
                    "command_id": str(command.id),
                    "usage": usage.to_data(),
                },
            )
            return _result(
                session,
                record,
                default_max_graph_steps=default_max_graph_steps,
            )

    def begin_resume(
        self,
        workflow_run_id: UUID,
        command: RunControlCommand,
    ) -> RunControlResult:
        """Move a user- or budget-paused run back to executable pending state."""
        if command.action is not RunControlAction.RESUME:
            raise ValueError("begin_resume requires a resume command")
        with self._session_factory.begin() as session:
            record, existing = _record_command(session, workflow_run_id, command)
            if existing:
                return _result(session, record)
            workflow_run = _require_run(session, workflow_run_id)
            if workflow_run.status is not RunStatus.PAUSED:
                raise RunControlError(
                    f"workflow cannot resume from status {workflow_run.status.value}"
                )
            if workflow_run.pause_reason is RunPauseReason.HUMAN_APPROVAL:
                raise RunControlError("human-approval pause requires a blueprint decision")
            if workflow_run.pause_reason not in {
                RunPauseReason.USER,
                RunPauseReason.BUDGET,
            }:
                raise RunControlError("workflow pause reason is missing or invalid")
            workflow_run.status = RunStatus.PENDING
            workflow_run.pause_reason = None
            workflow_run.completed_at = None
            workflow_run.error_code = None
            workflow_run.error_message = None
            _mark_applied(record, workflow_run.checkpoint_id)
            _add_event(
                session,
                workflow_run_id,
                "workflow.resumed",
                {"command_id": str(command.id)},
            )
            return _result(session, record)

    def begin_retry(
        self,
        workflow_run_id: UUID,
        command: RunControlCommand,
    ) -> RunControlResult:
        """Record a retry request before the workflow runtime creates its child."""
        if command.action is not RunControlAction.RETRY_FROM_NODE:
            raise ValueError("begin_retry requires a retry_from_node command")
        with self._session_factory.begin() as session:
            record, existing = _record_command(session, workflow_run_id, command)
            if existing:
                return _result(session, record)
            workflow_run = _require_run(session, workflow_run_id)
            if workflow_run.status in {RunStatus.PENDING, RunStatus.RUNNING}:
                raise RunControlError(
                    f"workflow cannot retry from status {workflow_run.status.value}"
                )
            return _result(session, record)

    def complete_retry(
        self,
        command_id: UUID,
        resulting_workflow_run_id: UUID,
        checkpoint_id: str,
    ) -> RunControlResult:
        """Link the immutable source command to its new child run."""
        with self._session_factory.begin() as session:
            record = _require_control(session, command_id)
            record.resulting_workflow_run_id = resulting_workflow_run_id
            _mark_applied(record, checkpoint_id)
            _add_event(
                session,
                record.workflow_run_id,
                "workflow.retry.created",
                {
                    "command_id": str(command_id),
                    "resulting_workflow_run_id": str(resulting_workflow_run_id),
                    "target_node": record.target_node,
                },
            )
            return _result(session, record)

    def fail_command(self, command_id: UUID, error: Exception) -> None:
        """Persist a redacted command failure for idempotent replay."""
        safe_message = active_secret_guard().redact_text(str(error))[:2000]
        with self._session_factory.begin() as session:
            record = _require_control(session, command_id)
            record.status = RunControlStatus.FAILED
            record.error_message = safe_message

    def before_node(
        self,
        workflow_run_id: UUID,
        node: str,
        *,
        includes_model_call: bool,
        default_max_graph_steps: int,
    ) -> None:
        """Apply pending controls and reserve aggregate budget before a node."""
        signal: type[RuntimeError] | None = None
        message = ""
        with self._session_factory.begin() as session:
            workflow_run = _require_run(session, workflow_run_id)
            if workflow_run.status is RunStatus.CANCELLED:
                signal = WorkflowStoppedSignal
                message = "workflow was stopped"
            elif workflow_run.status is RunStatus.PAUSED and workflow_run.pause_reason in {
                RunPauseReason.USER,
                RunPauseReason.BUDGET,
            }:
                signal = WorkflowPausedSignal
                message = "workflow is paused"
            else:
                pause_command = session.scalar(
                    select(WorkflowRunControl)
                    .where(
                        WorkflowRunControl.workflow_run_id == workflow_run_id,
                        WorkflowRunControl.action == RunControlAction.PAUSE,
                        WorkflowRunControl.status == RunControlStatus.PENDING,
                    )
                    .order_by(WorkflowRunControl.created_at, WorkflowRunControl.id)
                    .limit(1)
                )
                if pause_command is not None:
                    workflow_run.current_node = node
                    _apply_pause(
                        session,
                        workflow_run,
                        RunPauseReason.USER,
                        command=pause_command,
                    )
                    signal = WorkflowPausedSignal
                    message = "workflow paused before the next node"
                else:
                    budget = RunBudget.from_data(
                        workflow_run.budget,
                        default_max_graph_steps=default_max_graph_steps,
                    )
                    usage = run_usage(workflow_run)
                    limits = projected_budget_limits(
                        budget,
                        usage,
                        includes_model_call=includes_model_call,
                    )
                    if limits:
                        workflow_run.current_node = node
                        _apply_pause(
                            session,
                            workflow_run,
                            RunPauseReason.BUDGET,
                            budget_limits=limits,
                            usage=usage,
                        )
                        signal = WorkflowPausedSignal
                        message = "workflow paused before exceeding its budget"
        if signal is not None:
            raise signal(message)

    def execution_boundary(self, workflow_run_id: UUID) -> None:
        """Honor stop/pause state before finalizing graph output."""
        with self._session_factory() as session:
            workflow_run = _require_run(session, workflow_run_id)
            if workflow_run.status is RunStatus.CANCELLED:
                raise WorkflowStoppedSignal("workflow was stopped")
            if workflow_run.status is RunStatus.PAUSED and workflow_run.pause_reason in {
                RunPauseReason.USER,
                RunPauseReason.BUDGET,
            }:
                raise WorkflowPausedSignal("workflow is paused")

    def result(self, command_id: UUID) -> RunControlResult:
        """Return the latest durable state for an existing command."""
        with self._session_factory() as session:
            return _result(session, _require_control(session, command_id))


def _record_command(
    session: Session,
    workflow_run_id: UUID,
    command: RunControlCommand,
) -> tuple[WorkflowRunControl, bool]:
    existing = session.get(WorkflowRunControl, command.id)
    if existing is not None:
        if (
            existing.workflow_run_id != workflow_run_id
            or existing.action is not command.action
            or existing.target_node != command.target_node
            or (existing.budget_updates or None)
            != (dict(command.budget_updates) if command.budget_updates else None)
        ):
            raise RunControlError("command ID was already used with different data")
        return existing, True
    _require_run(session, workflow_run_id)
    record = WorkflowRunControl(
        id=command.id,
        workflow_run_id=workflow_run_id,
        action=command.action,
        target_node=command.target_node,
        budget_updates=(
            dict(command.budget_updates) if command.budget_updates is not None else None
        ),
        status=RunControlStatus.PENDING,
    )
    session.add(record)
    session.flush()
    return record, False


def _apply_pause(
    session: Session,
    workflow_run: WorkflowRun,
    reason: RunPauseReason,
    *,
    command: WorkflowRunControl | None = None,
    budget_limits: tuple[BudgetLimit, ...] = (),
    usage: RunUsage | None = None,
) -> None:
    workflow_run.status = RunStatus.PAUSED
    workflow_run.pause_reason = reason
    workflow_run.error_code = None
    workflow_run.error_message = None
    if command is not None:
        _mark_applied(command, workflow_run.checkpoint_id)
    payload: dict[str, object] = {"reason": reason.value}
    if command is not None:
        payload["command_id"] = str(command.id)
    if budget_limits:
        payload["limits"] = [limit.value for limit in budget_limits]
    if usage is not None:
        payload["usage"] = usage.to_data()
    _add_event(session, workflow_run.id, "workflow.paused", payload)


def _mark_applied(
    record: WorkflowRunControl,
    checkpoint_id: str | None,
) -> None:
    record.status = RunControlStatus.APPLIED
    record.checkpoint_id = checkpoint_id
    record.applied_at = datetime.now(UTC)
    record.error_message = None


def run_usage(workflow_run: WorkflowRun) -> RunUsage:
    now = datetime.now(UTC)
    started_at = workflow_run.started_at
    if started_at is not None and started_at.tzinfo is None:
        started_at = started_at.replace(tzinfo=UTC)
    return RunUsage(
        graph_steps=sum(
            event.event_type == "workflow.node.started" for event in workflow_run.events
        ),
        model_calls=len(workflow_run.invocations),
        input_tokens=sum(invocation.input_tokens for invocation in workflow_run.invocations),
        output_tokens=sum(invocation.output_tokens for invocation in workflow_run.invocations),
        cost_usd=sum(
            (invocation.estimated_cost_usd for invocation in workflow_run.invocations),
            start=Decimal("0"),
        ),
        wall_clock_seconds=(
            max(0, int((now - started_at).total_seconds())) if started_at is not None else 0
        ),
    )


def _result(
    session: Session,
    record: WorkflowRunControl,
    *,
    default_max_graph_steps: int = 64,
) -> RunControlResult:
    workflow_run = _require_run(session, record.workflow_run_id)
    return RunControlResult(
        command_id=record.id,
        workflow_run_id=workflow_run.id,
        action=record.action,
        command_status=record.status,
        workflow_status=workflow_run.status,
        pause_reason=workflow_run.pause_reason,
        target_node=record.target_node,
        resulting_workflow_run_id=record.resulting_workflow_run_id,
        checkpoint_id=record.checkpoint_id or workflow_run.checkpoint_id,
        budget=RunBudget.from_data(
            workflow_run.budget,
            default_max_graph_steps=default_max_graph_steps,
        ),
        usage=run_usage(workflow_run),
        error_message=record.error_message,
    )


def _require_run(session: Session, workflow_run_id: UUID) -> WorkflowRun:
    workflow_run = session.get(WorkflowRun, workflow_run_id)
    if workflow_run is None:
        raise RunControlError(f"unknown workflow run {workflow_run_id}")
    return workflow_run


def _require_control(session: Session, command_id: UUID) -> WorkflowRunControl:
    record = session.get(WorkflowRunControl, command_id)
    if record is None:
        raise RunControlError(f"unknown run-control command {command_id}")
    return record


def _add_event(
    session: Session,
    workflow_run_id: UUID,
    event_type: str,
    payload: dict[str, object],
) -> None:
    session.add(
        WorkflowEvent(
            workflow_run_id=workflow_run_id,
            event_type=event_type,
            source="human" if "command_id" in payload else "system",
            schema_version="1",
            payload=payload,
        )
    )
