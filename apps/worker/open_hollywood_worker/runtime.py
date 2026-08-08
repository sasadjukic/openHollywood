"""Sequential durable claimant for interactive Blueprint and production runs."""

from __future__ import annotations

import asyncio
import logging
from contextlib import suppress
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid5

from open_hollywood_api.persistence.models import (
    ModelProfile,
    RunStatus,
    WorkflowEvent,
    WorkflowRun,
)
from open_hollywood_api.services.blueprint_workflow import BlueprintWorkflowService
from open_hollywood_api.services.production_workflow import SceneProductionService
from open_hollywood_engine.artifacts import ArtifactKind
from open_hollywood_engine.evaluations import canonical_sha256
from open_hollywood_engine.models import ModelProfileConfiguration
from open_hollywood_engine.workflows import (
    INTERACTIVE_BLUEPRINT_BUDGET,
    SCENE_PRODUCTION_WORKFLOW_NAME,
    STORY_BLUEPRINT_WORKFLOW_NAME,
)
from sqlalchemy import select, update
from sqlalchemy.orm import Session, sessionmaker

LOGGER = logging.getLogger(__name__)
INTERACTIVE_EXECUTION_KIND = "interactive"
INTERACTIVE_CONSTRAINTS: dict[str, object] = {
    "category": "interactive",
    "genres": ["fiction"],
    "intended_maturity": "standard_fiction",
    "target_word_count": {"minimum": 2_500, "maximum": 5_000},
    "required_elements": [],
    "forbidden_shortcuts": [],
    "factual_research_allowed": False,
}


class _CandidateKind(StrEnum):
    BLUEPRINT = "blueprint"
    PRODUCTION = "production"


@dataclass(frozen=True, slots=True)
class _Candidate:
    kind: _CandidateKind
    workflow_run_id: UUID
    blueprint_run_id: UUID
    control_run_ids: tuple[UUID, ...]


class WorkflowWorker:
    """Claim interactive SQLite runs sequentially and execute durable graphs."""

    def __init__(
        self,
        *,
        session_factory: sessionmaker[Session],
        blueprint_service: BlueprintWorkflowService,
        production_service: SceneProductionService,
        poll_interval_seconds: float = 0.25,
    ) -> None:
        if poll_interval_seconds <= 0:
            raise ValueError("worker poll interval must be positive")
        self._session_factory = session_factory
        self._blueprint_service = blueprint_service
        self._production_service = production_service
        self._poll_interval_seconds = poll_interval_seconds
        self._loop_task: asyncio.Task[None] | None = None
        self._active_tasks: dict[UUID, asyncio.Task[None]] = {}
        self._wake = asyncio.Event()
        self._stopping = False

    async def start(self) -> None:
        """Start the single durable claiming loop."""
        if self._loop_task is not None:
            raise RuntimeError("workflow worker is already running")
        self._stopping = False
        await asyncio.to_thread(self._recover_interrupted_runs)
        self._loop_task = asyncio.create_task(self._run(), name="open-hollywood-worker")

    async def stop(self) -> None:
        """Cancel active work and close the claiming loop."""
        self._stopping = True
        for task in set(self._active_tasks.values()):
            task.cancel()
        if self._loop_task is not None:
            self._loop_task.cancel()
            with suppress(asyncio.CancelledError):
                await self._loop_task
        self._loop_task = None
        self._active_tasks.clear()

    def cancel_active_run(self, workflow_run_id: UUID) -> None:
        """Cancel an open provider call after a durable stop command is recorded."""
        task = self._active_tasks.get(workflow_run_id)
        if task is not None:
            task.cancel()
        self._wake.set()

    def wake(self) -> None:
        """Wake the claimant after an external durable state transition."""
        self._wake.set()

    async def _run(self) -> None:
        while True:
            candidate = await asyncio.to_thread(self._next_candidate)
            if candidate is None:
                self._wake.clear()
                with suppress(TimeoutError):
                    await asyncio.wait_for(
                        self._wake.wait(),
                        timeout=self._poll_interval_seconds,
                    )
                continue

            execution = asyncio.create_task(
                self._execute(candidate),
                name=f"open-hollywood-{candidate.kind.value}-{candidate.workflow_run_id}",
            )
            for run_id in candidate.control_run_ids:
                self._active_tasks[run_id] = execution
            try:
                await execution
            except asyncio.CancelledError:
                if self._stopping:
                    raise
            except Exception:
                LOGGER.exception(
                    "Interactive workflow execution failed for %s",
                    candidate.workflow_run_id,
                )
            finally:
                for run_id in candidate.control_run_ids:
                    if self._active_tasks.get(run_id) is execution:
                        self._active_tasks.pop(run_id, None)

    async def _execute(self, candidate: _Candidate) -> None:
        if candidate.kind is _CandidateKind.BLUEPRINT:
            await self._blueprint_service.execute(candidate.workflow_run_id)
            return
        blueprint = await self._blueprint_service.inspect(candidate.blueprint_run_id)
        approved_blueprint = next(
            (
                reference
                for reference in blueprint.artifacts
                if reference.kind is ArtifactKind.STORY_BLUEPRINT
            ),
            None,
        )
        if approved_blueprint is None:
            raise RuntimeError("approved interactive Blueprint artifact is missing")
        await self._production_service.execute(
            candidate.blueprint_run_id,
            approved_blueprint,
        )

    def _next_candidate(self) -> _Candidate | None:
        with self._session_factory.begin() as session:
            blueprint_runs = session.scalars(
                select(WorkflowRun)
                .where(
                    WorkflowRun.workflow_name == STORY_BLUEPRINT_WORKFLOW_NAME,
                    WorkflowRun.conversation_id.is_not(None),
                    WorkflowRun.status == RunStatus.PENDING,
                )
                .order_by(WorkflowRun.created_at, WorkflowRun.id)
            ).all()
            for run in blueprint_runs:
                if "benchmark_campaign_id" in run.input_state:
                    continue
                if not self._freeze_interactive_inputs(session, run):
                    continue
                if not self._claim_pending_run(session, run):
                    continue
                return _Candidate(
                    kind=_CandidateKind.BLUEPRINT,
                    workflow_run_id=run.id,
                    blueprint_run_id=run.id,
                    control_run_ids=(run.id,),
                )

            production_runs = session.scalars(
                select(WorkflowRun)
                .where(
                    WorkflowRun.workflow_name == SCENE_PRODUCTION_WORKFLOW_NAME,
                    WorkflowRun.status == RunStatus.PENDING,
                )
                .order_by(WorkflowRun.created_at, WorkflowRun.id)
            ).all()
            for run in production_runs:
                parent_id = run.parent_workflow_run_id
                if parent_id is None or run.input_state.get("execution_kind") != (
                    INTERACTIVE_EXECUTION_KIND
                ):
                    continue
                if not self._claim_pending_run(session, run):
                    continue
                return _Candidate(
                    kind=_CandidateKind.PRODUCTION,
                    workflow_run_id=run.id,
                    blueprint_run_id=parent_id,
                    control_run_ids=(run.id,),
                )

            approved_runs = session.scalars(
                select(WorkflowRun)
                .where(
                    WorkflowRun.workflow_name == STORY_BLUEPRINT_WORKFLOW_NAME,
                    WorkflowRun.conversation_id.is_not(None),
                    WorkflowRun.status == RunStatus.SUCCEEDED,
                )
                .order_by(WorkflowRun.updated_at, WorkflowRun.id)
            ).all()
            for run in approved_runs:
                if run.input_state.get("execution_kind") != INTERACTIVE_EXECUTION_KIND:
                    continue
                if any(
                    child.workflow_name == SCENE_PRODUCTION_WORKFLOW_NAME
                    for child in run.child_workflow_runs
                ):
                    continue
                production_run_id = uuid5(run.id, "agentic-scene-production-workflow")
                return _Candidate(
                    kind=_CandidateKind.PRODUCTION,
                    workflow_run_id=run.id,
                    blueprint_run_id=run.id,
                    control_run_ids=(run.id, production_run_id),
                )
        return None

    def _recover_interrupted_runs(self) -> None:
        """Requeue browser runs left running by a stopped local process."""
        with self._session_factory.begin() as session:
            interrupted = session.scalars(
                select(WorkflowRun).where(WorkflowRun.status == RunStatus.RUNNING)
            ).all()
            for run in interrupted:
                if run.input_state.get("execution_kind") != INTERACTIVE_EXECUTION_KIND:
                    continue
                run.status = RunStatus.PENDING
                session.add(
                    WorkflowEvent(
                        workflow_run_id=run.id,
                        event_type="workflow.execution.recovered",
                        source="worker",
                        payload={"node": run.current_node},
                    )
                )

    def _freeze_interactive_inputs(self, session: Session, run: WorkflowRun) -> bool:
        if run.input_state.get("execution_kind") == INTERACTIVE_EXECUTION_KIND:
            return True
        profile = session.scalar(select(ModelProfile).where(ModelProfile.is_default.is_(True)))
        if profile is None:
            self._record_waiting_for_profile(session, run)
            return False
        configuration = ModelProfileConfiguration.from_data(profile.configuration)
        if not configuration.is_complete:
            self._record_waiting_for_profile(session, run)
            return False
        run.input_state = {
            **run.input_state,
            "execution_kind": INTERACTIVE_EXECUTION_KIND,
            "model_profile_id": str(profile.id),
            "model_profile_configuration": configuration.to_data(),
            "model_profile_configuration_sha256": canonical_sha256(configuration.to_data()),
            "premise": self._premise(run),
            "run_seed": run.id.int % (2**31),
            "benchmark_constraints": dict(INTERACTIVE_CONSTRAINTS),
        }
        if not run.budget:
            run.budget = INTERACTIVE_BLUEPRINT_BUDGET.to_data()
        session.add(
            WorkflowEvent(
                workflow_run_id=run.id,
                event_type="workflow.runtime.configured",
                source="worker",
                payload={
                    "model_profile_id": str(profile.id),
                    "model_profile_mode": configuration.mode.value,
                },
            )
        )
        return True

    @staticmethod
    def _claim_pending_run(session: Session, run: WorkflowRun) -> bool:
        """Atomically give one worker ownership before any graph call starts."""
        session.flush()
        claimed_run_id = session.scalar(
            update(WorkflowRun)
            .where(
                WorkflowRun.id == run.id,
                WorkflowRun.status == RunStatus.PENDING,
            )
            .values(
                status=RunStatus.RUNNING,
                started_at=run.started_at or datetime.now(UTC),
            )
            .returning(WorkflowRun.id)
        )
        if claimed_run_id is None:
            return False
        run.status = RunStatus.RUNNING
        run.started_at = run.started_at or datetime.now(UTC)
        return True

    @staticmethod
    def _premise(run: WorkflowRun) -> str:
        sequence = run.input_state.get("premise_message_sequence", 1)
        message = next(
            (candidate for candidate in run.messages if candidate.sequence_number == sequence),
            None,
        )
        if message is None or not message.content.strip():
            raise RuntimeError("interactive workflow premise is unavailable")
        return message.content

    @staticmethod
    def _record_waiting_for_profile(session: Session, run: WorkflowRun) -> None:
        exists = session.scalar(
            select(WorkflowEvent.id)
            .where(
                WorkflowEvent.workflow_run_id == run.id,
                WorkflowEvent.event_type == "workflow.waiting_for_model_profile",
            )
            .limit(1)
        )
        if exists is None:
            session.add(
                WorkflowEvent(
                    workflow_run_id=run.id,
                    event_type="workflow.waiting_for_model_profile",
                    source="worker",
                    payload={"action": "Activate a complete Local, Cloud, or Hybrid profile."},
                )
            )
