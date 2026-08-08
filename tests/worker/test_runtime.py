"""Browser-runtime integration through the durable local worker."""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from pathlib import Path
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient
from open_hollywood_api.persistence.database import create_session_factory
from open_hollywood_api.persistence.models import (
    AgentInvocation,
    Artifact,
    RunStatus,
    WorkflowRun,
)
from open_hollywood_api.services.blueprint_model_executor import (
    ProfileRoutedBlueprintNodeExecutor,
)
from open_hollywood_api.services.blueprint_workflow import BlueprintWorkflowService
from open_hollywood_api.services.model_profiles import (
    BUILTIN_PROFILE_IDS,
    ModelProfileStore,
)
from open_hollywood_api.services.production_model_executor import (
    ProfileRoutedProductionExecutor,
)
from open_hollywood_api.services.production_workflow import SceneProductionService
from open_hollywood_api.services.workflow_commands import QueuedWorkflowCommandService
from open_hollywood_api.services.workspace import WorkspaceStore
from open_hollywood_engine.artifacts import ArtifactKind
from open_hollywood_engine.evaluations import load_benchmark_corpus
from open_hollywood_engine.models import ModelDeployment, ModelProfileMode, ModelSelection
from open_hollywood_engine.workflows import (
    SCENE_PRODUCTION_WORKFLOW_NAME,
    BlueprintDecisionAction,
    BlueprintHumanDecision,
    RunBudget,
    RunControlAction,
    RunControlCommand,
    RunControlStatus,
)
from open_hollywood_worker.app import create_worker_app
from open_hollywood_worker.runtime import (
    INTERACTIVE_EXECUTION_KIND,
    WorkflowWorker,
)
from sqlalchemy import Engine, func, select
from sqlalchemy.orm import Session, sessionmaker

from tests.evaluations.test_agentic_blueprint import CORPUS_PATH
from tests.evaluations.test_agentic_production import ProductionFixtureGateway

pytestmark = pytest.mark.anyio


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


async def test_worker_claims_browser_story_and_completes_production(
    migrated_database_path: Path,
    database_engine: Engine,
) -> None:
    session_factory = create_session_factory(database_engine)
    premise = "A courier pigeon discovers that the city's drones are exchanging secrets."
    prompt = load_benchmark_corpus(CORPUS_PATH).prompts[0]
    gateway = ProductionFixtureGateway(premise, prompt)
    profile_store = ModelProfileStore(session_factory)
    profile_store.list_profiles()
    local_profile_id = BUILTIN_PROFILE_IDS[ModelProfileMode.LOCAL]
    profile_store.configure_profile(
        local_profile_id,
        local_model=ModelSelection(
            provider="ollama",
            model_identifier="fixture-local",
            deployment=ModelDeployment.LOCAL,
        ),
        cloud_model=None,
    )
    profile_store.activate_profile(local_profile_id)
    created = WorkspaceStore(session_factory).create_story_project(
        request_id=uuid4(),
        premise=premise,
        title="Pigeon Express",
    )
    blueprint_executor = ProfileRoutedBlueprintNodeExecutor(
        session_factory=session_factory,
        gateway=gateway,
    )
    production_executor = ProfileRoutedProductionExecutor(
        session_factory=session_factory,
        gateway=gateway,
    )

    async with (
        BlueprintWorkflowService(
            migrated_database_path,
            session_factory,
            blueprint_executor,
        ) as blueprint_service,
        SceneProductionService(
            database_path=migrated_database_path,
            session_factory=session_factory,
            executor=production_executor,
        ) as production_service,
    ):
        worker = WorkflowWorker(
            session_factory=session_factory,
            blueprint_service=blueprint_service,
            production_service=production_service,
            poll_interval_seconds=0.01,
        )
        await worker.start()
        try:
            await _wait_for(
                lambda: _run_status(session_factory, created.workflow_run_id) is RunStatus.PAUSED
            )
            with session_factory.begin() as session:
                legacy_run = session.get(WorkflowRun, created.workflow_run_id)
                assert legacy_run is not None
                legacy_run.budget = RunBudget().to_data()
            initial_integrations = sum(
                request.invocation.specialist_role == "blueprint_integrator"
                for request in gateway.requests
            )
            retry = await QueuedWorkflowCommandService(
                session_factory,
                blueprint_service,
                wake_worker=worker.wake,
            ).apply_control(
                created.workflow_run_id,
                RunControlCommand(
                    id=uuid4(),
                    action=RunControlAction.RETRY_FROM_NODE,
                    target_node="integration",
                ),
            )
            assert retry.command_status is RunControlStatus.PENDING
            assert retry.resulting_workflow_run_id is not None
            active_blueprint_run_id = retry.resulting_workflow_run_id
            await _wait_for(
                lambda: _run_status(session_factory, active_blueprint_run_id) is RunStatus.PAUSED
            )
            assert (
                sum(
                    request.invocation.specialist_role == "blueprint_integrator"
                    for request in gateway.requests
                )
                == initial_integrations + 1
            )
            blueprint = await blueprint_service.inspect(active_blueprint_run_id)
            assert blueprint.awaiting_approval is True
            assert blueprint.interrupt_id is not None
            await blueprint_service.resume(
                active_blueprint_run_id,
                BlueprintHumanDecision(
                    id=uuid4(),
                    interrupt_id=blueprint.interrupt_id,
                    action=BlueprintDecisionAction.APPROVE,
                ),
            )
            await _wait_for(
                lambda: (
                    _production_status(session_factory, active_blueprint_run_id)
                    is RunStatus.SUCCEEDED
                )
            )
        finally:
            await worker.stop()

    with session_factory() as session:
        source_run = session.get(WorkflowRun, created.workflow_run_id)
        assert source_run is not None
        assert source_run.status is RunStatus.CANCELLED
        assert source_run.budget["per_call_output_tokens"] == 2_000
        blueprint_run = session.get(WorkflowRun, active_blueprint_run_id)
        assert blueprint_run is not None
        assert blueprint_run.status is RunStatus.SUCCEEDED
        assert blueprint_run.pause_reason is None
        assert blueprint_run.input_state["execution_kind"] == INTERACTIVE_EXECUTION_KIND
        assert blueprint_run.input_state["model_profile_id"] == str(local_profile_id)
        assert blueprint_run.budget["per_call_input_tokens"] == 12_000
        assert blueprint_run.budget["per_call_output_tokens"] == 8_000
        production_run = session.scalar(
            select(WorkflowRun).where(
                WorkflowRun.parent_workflow_run_id == active_blueprint_run_id,
                WorkflowRun.workflow_name == SCENE_PRODUCTION_WORKFLOW_NAME,
            )
        )
        assert production_run is not None
        assert production_run.status is RunStatus.SUCCEEDED
        invocation_count = session.scalar(select(func.count(AgentInvocation.id)))
        scene_count = session.scalar(
            select(func.count(Artifact.id)).where(
                Artifact.artifact_type == ArtifactKind.SCENE_DRAFT.value
            )
        )
        assert invocation_count is not None and invocation_count > 0
        assert scene_count is not None and scene_count >= 3


async def test_worker_leaves_story_pending_until_a_complete_profile_is_active(
    migrated_database_path: Path,
    database_engine: Engine,
) -> None:
    session_factory = create_session_factory(database_engine)
    created = WorkspaceStore(session_factory).create_story_project(
        request_id=uuid4(),
        premise="A lost button keeps returning to a collector's empty display case.",
        title="The Collector of Lost Buttons",
    )
    gateway = ProductionFixtureGateway(
        "A lost button keeps returning to a collector's empty display case.",
        load_benchmark_corpus(CORPUS_PATH).prompts[0],
    )
    async with (
        BlueprintWorkflowService(
            migrated_database_path,
            session_factory,
            ProfileRoutedBlueprintNodeExecutor(
                session_factory=session_factory,
                gateway=gateway,
            ),
        ) as blueprint_service,
        SceneProductionService(
            database_path=migrated_database_path,
            session_factory=session_factory,
            executor=ProfileRoutedProductionExecutor(
                session_factory=session_factory,
                gateway=gateway,
            ),
        ) as production_service,
    ):
        worker = WorkflowWorker(
            session_factory=session_factory,
            blueprint_service=blueprint_service,
            production_service=production_service,
            poll_interval_seconds=0.01,
        )
        await worker.start()
        try:
            await _wait_for(
                lambda: _event_exists(
                    session_factory,
                    created.workflow_run_id,
                    "workflow.waiting_for_model_profile",
                )
            )
        finally:
            await worker.stop()

    with session_factory() as session:
        run = session.get(WorkflowRun, created.workflow_run_id)
        assert run is not None
        assert run.status is RunStatus.PENDING
        assert run.pause_reason is None
        assert session.scalar(select(func.count(AgentInvocation.id))) == 0


async def test_composed_app_exposes_worker_owned_run_commands(
    migrated_database_path: Path,
) -> None:
    prompt = load_benchmark_corpus(CORPUS_PATH).prompts[0]
    application = create_worker_app(
        gateway=ProductionFixtureGateway(prompt.prompt, prompt),
        poll_interval_seconds=0.01,
    )
    transport = ASGITransport(app=application)

    async with (
        application.router.lifespan_context(application),
        AsyncClient(transport=transport, base_url="http://test") as client,
    ):
        response = await client.post(
            "/api/v1/workflow-runs/00000000-0000-4000-8000-000000000000/controls",
            json={"action": "stop", "command_id": str(uuid4())},
        )

    assert migrated_database_path.is_file()
    assert response.status_code == 404
    assert response.json()["detail"] == "Workflow run not found"


async def _wait_for(predicate: Callable[[], bool], *, timeout_seconds: float = 5) -> None:
    deadline = asyncio.get_running_loop().time() + timeout_seconds
    while not predicate():
        if asyncio.get_running_loop().time() >= deadline:
            raise AssertionError("timed out waiting for durable workflow state")
        await asyncio.sleep(0.01)


def _run_status(
    session_factory: sessionmaker[Session],
    workflow_run_id: object,
) -> RunStatus:
    with session_factory() as session:
        run = session.get(WorkflowRun, workflow_run_id)
        assert run is not None
        return run.status


def _production_status(
    session_factory: sessionmaker[Session],
    blueprint_run_id: object,
) -> RunStatus | None:
    with session_factory() as session:
        run = session.scalar(
            select(WorkflowRun).where(
                WorkflowRun.parent_workflow_run_id == blueprint_run_id,
                WorkflowRun.workflow_name == SCENE_PRODUCTION_WORKFLOW_NAME,
            )
        )
        return run.status if run is not None else None


def _event_exists(
    session_factory: sessionmaker[Session],
    workflow_run_id: object,
    event_type: str,
) -> bool:
    with session_factory() as session:
        return (
            session.scalar(
                select(WorkflowRun.id)
                .join(WorkflowRun.events)
                .where(
                    WorkflowRun.id == workflow_run_id,
                    WorkflowRun.events.any(event_type=event_type),
                )
                .limit(1)
            )
            is not None
        )
