"""Provider routing through real durable workflows, with synthetic model responses."""

from dataclasses import replace
from decimal import Decimal
from pathlib import Path
from uuid import uuid4

import pytest
from open_hollywood_api.persistence.database import create_session_factory
from open_hollywood_api.persistence.models import AgentInvocation, RunStatus
from open_hollywood_api.services.blueprint_model_executor import ProfileRoutedBlueprintNodeExecutor
from open_hollywood_api.services.blueprint_workflow import BlueprintWorkflowService
from open_hollywood_api.services.model_profiles import BUILTIN_PROFILE_IDS, ModelProfileStore
from open_hollywood_api.services.production_model_executor import ProfileRoutedProductionExecutor
from open_hollywood_api.services.production_workflow import SceneProductionService
from open_hollywood_api.services.workspace import WorkspaceStore
from open_hollywood_engine.evaluations import load_benchmark_corpus
from open_hollywood_engine.models import (
    ModelCostBasis,
    ModelDeployment,
    ModelProfileMode,
    ModelRequest,
    ModelResponse,
    ModelSelection,
    ProviderModelGateway,
)
from open_hollywood_engine.workflows import BlueprintDecisionAction, BlueprintHumanDecision
from open_hollywood_worker.runtime import WorkflowWorker
from sqlalchemy import Engine, select

from tests.evaluations.test_agentic_blueprint import CORPUS_PATH
from tests.evaluations.test_agentic_production import ProductionFixtureGateway
from tests.worker.test_runtime import _production_status, _run_status, _wait_for

pytestmark = pytest.mark.anyio


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


class OpenAIFixture(ProductionFixtureGateway):
    provider = "openai"

    async def generate(self, request: ModelRequest) -> ModelResponse:
        assert request.provider == "openai"
        assert request.deployment is ModelDeployment.CLOUD
        assert request.response_schema is not None
        result = await super().generate(request)
        return replace(
            result,
            deployment=ModelDeployment.CLOUD,
            cost_basis=ModelCostBasis.UNKNOWN,
            estimated_cost_usd=Decimal("0.0002"),
            usage=replace(result.usage, reasoning_tokens=12),
            metadata={"reasoning_tokens": 12, "effective_settings": {"seed_supported": False}},
        )


@pytest.mark.parametrize("mode", [ModelProfileMode.CLOUD, ModelProfileMode.HYBRID])
async def test_openai_profiles_preserve_blueprint_checkpoint_and_route_production(
    mode: ModelProfileMode,
    migrated_database_path: Path,
    database_engine: Engine,
) -> None:
    factory = create_session_factory(database_engine)
    premise = "A courier pigeon discovers the city's drones are exchanging secrets."
    prompt = load_benchmark_corpus(CORPUS_PATH).prompts[0]
    local = ProductionFixtureGateway(premise, prompt)
    cloud = OpenAIFixture(premise, prompt)
    router = ProviderModelGateway(
        {
            ("ollama", ModelDeployment.LOCAL): local,
            ("openai", ModelDeployment.CLOUD): cloud,
        }
    )
    store = ModelProfileStore(factory)
    profile_id = BUILTIN_PROFILE_IDS[mode]
    store.configure_profile(
        profile_id,
        local_model=(
            ModelSelection("ollama", "fixture-local", ModelDeployment.LOCAL)
            if mode is ModelProfileMode.HYBRID
            else None
        ),
        cloud_model=ModelSelection("openai", "gpt-5.4-nano", ModelDeployment.CLOUD),
    )
    store.activate_profile(profile_id)
    created = WorkspaceStore(factory).create_story_project(
        request_id=uuid4(),
        premise=premise,
        title="Synthetic provider routing",
    )
    async with (
        BlueprintWorkflowService(
            migrated_database_path,
            factory,
            ProfileRoutedBlueprintNodeExecutor(session_factory=factory, gateway=router),
        ) as blueprint,
        SceneProductionService(
            database_path=migrated_database_path,
            session_factory=factory,
            executor=ProfileRoutedProductionExecutor(session_factory=factory, gateway=router),
        ) as production,
    ):
        worker = WorkflowWorker(
            session_factory=factory,
            blueprint_service=blueprint,
            production_service=production,
            poll_interval_seconds=0.01,
        )
        await worker.start()
        try:
            await _wait_for(
                lambda: _run_status(factory, created.workflow_run_id) is RunStatus.PAUSED,
                timeout_seconds=15,
            )
            paused = await blueprint.inspect(created.workflow_run_id)
            assert paused.awaiting_approval and paused.interrupt_id is not None
            assert not any(
                item.invocation.specialist_role == "scene_writer" for item in cloud.requests
            )
            await blueprint.resume(
                created.workflow_run_id,
                BlueprintHumanDecision(
                    id=uuid4(),
                    interrupt_id=paused.interrupt_id,
                    action=BlueprintDecisionAction.APPROVE,
                ),
            )
            await _wait_for(
                lambda: _production_status(factory, created.workflow_run_id) is RunStatus.SUCCEEDED,
                timeout_seconds=15,
            )
        finally:
            await worker.stop()
            await router.close()
    assert any(item.invocation.specialist_role == "scene_writer" for item in cloud.requests)
    assert bool(local.requests) is (mode is ModelProfileMode.HYBRID)
    with factory() as session:
        rows = session.scalars(select(AgentInvocation).where(AgentInvocation.provider == "openai"))
        invocations = list(rows)
        assert invocations
        assert all(
            row.request_settings["provider_metadata"]["reasoning_tokens"] == 12
            for row in invocations
        )
        assert all(row.request_settings["schema_enforced"] is True for row in invocations)
        assert all(row.estimated_cost_usd > 0 for row in invocations)
        assert all(row.cost_basis is ModelCostBasis.UNKNOWN for row in invocations)
