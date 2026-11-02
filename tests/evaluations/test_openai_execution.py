"""OpenAI billing/error metadata survives the ordinary persisted execution path."""

import json
from uuid import uuid4

import httpx
import pytest
from open_hollywood_api.persistence.database import create_session_factory
from open_hollywood_api.persistence.models import AgentInvocation, InvocationStatus
from open_hollywood_api.services.evaluation_execution import DirectBaselineBenchmarkExecutor
from open_hollywood_engine.evaluations import (
    BenchmarkCase,
    BenchmarkCaseExecutionError,
    BenchmarkModelTarget,
    BenchmarkProfileSnapshot,
    BenchmarkSystem,
    build_benchmark_plan,
    load_benchmark_corpus,
)
from open_hollywood_engine.models import (
    MODEL_PRESETS,
    ModelCostBasis,
    ModelDeployment,
    ModelProfileMode,
    ModelSelection,
    OpenAIGateway,
    ProviderModelGateway,
)
from open_hollywood_engine.secrets import EnvironmentSecretStore
from open_hollywood_engine.workflows import (
    SCENE_PRODUCTION_GRAPH_VERSION,
    STORY_BLUEPRINT_GRAPH_VERSION,
)
from sqlalchemy import Engine, select

from scripts.evaluation_harness import _ollama_campaign_gateway
from tests.evaluations.test_agentic_blueprint import CORPUS_PATH
from tests.models.test_openai_gateway import SECRET, payload

pytestmark = pytest.mark.anyio


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.mark.parametrize("outcome", ["complete", "refusal", "timeout"])
async def test_baseline_persists_openai_provenance_on_success_and_failure(
    database_engine: Engine,
    outcome: str,
) -> None:
    prompt = load_benchmark_corpus(CORPUS_PATH).prompts[0]
    case = BenchmarkCase(
        case_id=uuid4(),
        prompt_id=prompt.prompt_id,
        prompt_version=prompt.version,
        system=BenchmarkSystem.SINGLE_MODEL_BASELINE,
        run_seed=prompt.random_seed,
        baseline_model=BenchmarkModelTarget(
            provider="openai",
            model_identifier="gpt-5.4-nano",
            deployment=ModelDeployment.CLOUD,
        ),
    )

    def handler(request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content)
        assert body["model"] == "gpt-5.4-nano"
        if request.url.path.endswith("input_tokens"):
            return httpx.Response(200, json={"input_tokens": 100})
        if outcome == "timeout":
            raise httpx.ReadTimeout(SECRET, request=request)
        data = payload()
        data["output"][-1]["content"] = (
            [{"type": "refusal", "refusal": "declined"}]
            if outcome == "refusal"
            else [{"type": "output_text", "text": "Title: Synthetic\nA complete tiny story."}]
        )
        return httpx.Response(200, json=data)

    factory = create_session_factory(database_engine)
    async with OpenAIGateway(
        secret_store=EnvironmentSecretStore({"OPENAI_OH_KEY": SECRET}),
        transport=httpx.MockTransport(handler),
    ) as gateway:
        executor = DirectBaselineBenchmarkExecutor(
            campaign_id=uuid4(),
            session_factory=factory,
            gateway=gateway,
        )
        if outcome == "complete":
            result = await executor.execute(case, prompt)
            assert result.known_cost_usd is None
        else:
            with pytest.raises(BenchmarkCaseExecutionError):
                await executor.execute(case, prompt)
    with factory() as session:
        row = session.scalars(select(AgentInvocation)).one()
        assert row.status is (
            InvocationStatus.SUCCEEDED if outcome == "complete" else InvocationStatus.FAILED
        )
        metadata = row.request_settings["provider_metadata"]
        assert metadata["counted_input_tokens"] == 100
        assert metadata["effective_settings"]["store"] is False
        assert row.cost_basis is ModelCostBasis.UNKNOWN
        if outcome != "timeout":
            assert row.input_tokens == 100 and row.output_tokens == 20
            assert metadata["reasoning_tokens"] == 12
            assert row.estimated_cost_usd > 0
        assert SECRET not in str(row.request_settings)
        assert SECRET not in (row.error_message or "")


async def test_evaluation_composition_freezes_mixed_providers_even_with_overlapping_ids() -> None:
    corpus = load_benchmark_corpus(CORPUS_PATH)
    local = ModelSelection("ollama", "gpt-5.4-nano", ModelDeployment.LOCAL)
    cloud = ModelSelection("openai", "gpt-5.4-nano", ModelDeployment.CLOUD)
    profiles = {
        mode: BenchmarkProfileSnapshot.from_configuration(
            profile_id=uuid4(),
            configuration=MODEL_PRESETS[mode].configuration(
                local_model=local,
                cloud_model=cloud,
            ),
        )
        for mode in ModelProfileMode
    }
    plan = build_benchmark_plan(
        campaign_id=uuid4(),
        corpus=corpus,
        baseline_model=cloud,
        profiles=profiles,
        workflow_versions={
            "story_blueprint": STORY_BLUEPRINT_GRAPH_VERSION,
            "scene_production": SCENE_PRODUCTION_GRAPH_VERSION,
        },
    )
    router = _ollama_campaign_gateway(
        plan,
        target_keys=frozenset({"hybrid"}),
        ollama_base_url=None,
        direct_ollama_cloud=False,
        ollama_cloud_base_url=None,
        ollama_timeout_seconds=10,
    )
    try:
        assert isinstance(router, ProviderModelGateway)
        assert router.supports(local) and router.supports(cloud)
        assert not router.supports(ModelSelection("openai", "gpt-6.1-sol", ModelDeployment.CLOUD))
    finally:
        await router.close()
