"""Workflow-agnostic command handling for worker-owned execution."""

from __future__ import annotations

from collections.abc import Callable
from typing import Protocol, runtime_checkable
from uuid import UUID

from open_hollywood_engine.workflows import (
    DEFAULT_MAX_GRAPH_STEPS,
    INTERACTIVE_BLUEPRINT_BUDGET,
    SCENE_PRODUCTION_WORKFLOW_NAME,
    STORY_BLUEPRINT_WORKFLOW_NAME,
    RunBudget,
    RunControlAction,
    RunControlCommand,
)
from sqlalchemy.orm import Session, sessionmaker

from open_hollywood_api.persistence.models import WorkflowRun
from open_hollywood_api.services.blueprint_workflow import BlueprintWorkflowService
from open_hollywood_api.services.production_workflow import SceneProductionService
from open_hollywood_api.services.run_controls import (
    RunControlError,
    RunControlResult,
    RunControlStore,
)


@runtime_checkable
class WorkflowCommandService(Protocol):
    """Apply durable commands without exposing a concrete graph runtime."""

    async def apply_control(
        self,
        workflow_run_id: UUID,
        command: RunControlCommand,
    ) -> RunControlResult:
        """Apply one idempotent command at a durable workflow boundary."""


class QueuedWorkflowCommandService:
    """Persist generic controls and leave resumed execution to the worker."""

    def __init__(
        self,
        session_factory: sessionmaker[Session],
        blueprint_service: BlueprintWorkflowService,
        production_service: SceneProductionService,
        *,
        cancel_active_run: Callable[[UUID], None] | None = None,
        wake_worker: Callable[[], None] | None = None,
    ) -> None:
        self._session_factory = session_factory
        self._blueprint_service = blueprint_service
        self._production_service = production_service
        self._controls = RunControlStore(session_factory)
        self._cancel_active_run = cancel_active_run
        self._wake_worker = wake_worker

    async def apply_control(
        self,
        workflow_run_id: UUID,
        command: RunControlCommand,
    ) -> RunControlResult:
        """Apply a command while keeping execution ownership in the worker loop."""
        if command.action is RunControlAction.PAUSE:
            return self._controls.request_pause(workflow_run_id, command)
        if command.action is RunControlAction.STOP:
            result = self._controls.stop(workflow_run_id, command)
            if self._cancel_active_run is not None:
                self._cancel_active_run(workflow_run_id)
            return result
        if command.action is RunControlAction.UPDATE_BUDGET:
            return self._controls.update_budget(
                workflow_run_id,
                command,
                default_max_graph_steps=DEFAULT_MAX_GRAPH_STEPS,
            )
        if command.action is RunControlAction.RESUME:
            result = self._controls.begin_resume(workflow_run_id, command)
            if self._wake_worker is not None:
                self._wake_worker()
            return result
        if command.action is RunControlAction.RETRY_FROM_NODE:
            workflow_name = self._workflow_name(workflow_run_id)
            if workflow_name == STORY_BLUEPRINT_WORKFLOW_NAME:
                result = await self._blueprint_service.queue_retry_from_node(
                    workflow_run_id,
                    self._interactive_retry_command(workflow_run_id, command),
                )
            elif workflow_name == SCENE_PRODUCTION_WORKFLOW_NAME:
                result = await self._production_service.queue_retry_from_node(
                    workflow_run_id,
                    command,
                )
            else:
                raise RunControlError("retry-from-node is unavailable for this workflow")
            if self._wake_worker is not None:
                self._wake_worker()
            return result
        raise RunControlError(f"unsupported run-control action {command.action.value}")

    def _workflow_name(self, workflow_run_id: UUID) -> str:
        with self._session_factory() as session:
            workflow_run = session.get(WorkflowRun, workflow_run_id)
            if workflow_run is None:
                raise RunControlError(f"unknown workflow run {workflow_run_id}")
            return workflow_run.workflow_name

    def _interactive_retry_command(
        self,
        workflow_run_id: UUID,
        command: RunControlCommand,
    ) -> RunControlCommand:
        with self._session_factory() as session:
            workflow_run = session.get(WorkflowRun, workflow_run_id)
            if workflow_run is None:
                raise RunControlError(f"unknown workflow run {workflow_run_id}")
            if workflow_run.input_state.get("execution_kind") != "interactive":
                return command
            current = RunBudget.from_data(
                workflow_run.budget,
                default_max_graph_steps=DEFAULT_MAX_GRAPH_STEPS,
            )
        updates = dict(command.budget_updates or {})
        requested_input = updates.get("per_call_input_tokens", 0)
        requested_output = updates.get("per_call_output_tokens", 0)
        if (
            not isinstance(requested_input, int)
            or isinstance(requested_input, bool)
            or not isinstance(requested_output, int)
            or isinstance(requested_output, bool)
        ):
            raise RunControlError("retry per-call token budgets must be integers")
        updates["per_call_input_tokens"] = max(
            requested_input,
            current.per_call_input_tokens,
            INTERACTIVE_BLUEPRINT_BUDGET.per_call_input_tokens,
        )
        updates["per_call_output_tokens"] = max(
            requested_output,
            current.per_call_output_tokens,
            INTERACTIVE_BLUEPRINT_BUDGET.per_call_output_tokens,
        )
        return RunControlCommand(
            id=command.id,
            action=command.action,
            target_node=command.target_node,
            budget_updates=updates,
        )
