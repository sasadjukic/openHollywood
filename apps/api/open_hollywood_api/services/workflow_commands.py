"""Workflow-agnostic command handling for worker-owned execution."""

from __future__ import annotations

from collections.abc import Callable
from typing import Protocol, runtime_checkable
from uuid import UUID

from open_hollywood_engine.workflows import (
    DEFAULT_MAX_GRAPH_STEPS,
    STORY_BLUEPRINT_WORKFLOW_NAME,
    RunControlAction,
    RunControlCommand,
)
from sqlalchemy.orm import Session, sessionmaker

from open_hollywood_api.persistence.models import WorkflowRun
from open_hollywood_api.services.blueprint_workflow import BlueprintWorkflowService
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
        *,
        cancel_active_run: Callable[[UUID], None] | None = None,
    ) -> None:
        self._session_factory = session_factory
        self._blueprint_service = blueprint_service
        self._controls = RunControlStore(session_factory)
        self._cancel_active_run = cancel_active_run

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
            return self._controls.begin_resume(workflow_run_id, command)
        if command.action is RunControlAction.RETRY_FROM_NODE:
            if self._workflow_name(workflow_run_id) != STORY_BLUEPRINT_WORKFLOW_NAME:
                raise RunControlError("retry-from-node is available only for Story Blueprint runs")
            return await self._blueprint_service.apply_control(workflow_run_id, command)
        raise RunControlError(f"unsupported run-control action {command.action.value}")

    def _workflow_name(self, workflow_run_id: UUID) -> str:
        with self._session_factory() as session:
            workflow_run = session.get(WorkflowRun, workflow_run_id)
            if workflow_run is None:
                raise RunControlError(f"unknown workflow run {workflow_run_id}")
            return workflow_run.workflow_name
