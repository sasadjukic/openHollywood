"""Frozen-corpus, campaign, blind-review, and reporting tests."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from uuid import UUID, uuid5

import pytest
from open_hollywood_api.persistence.database import create_session_factory
from open_hollywood_api.services.model_profiles import (
    BUILTIN_PROFILE_IDS,
    ModelProfileStore,
)
from open_hollywood_engine.evaluations import (
    BenchmarkCase,
    BenchmarkCaseExecutionError,
    BenchmarkCaseStatus,
    BenchmarkCorpus,
    BenchmarkOutput,
    BenchmarkPlan,
    BenchmarkProfileSnapshot,
    BenchmarkPrompt,
    BlindPreference,
    CanonicalStoryScore,
    EvaluationDimension,
    HardGate,
    HumanComparisonReview,
    build_benchmark_plan,
    build_blind_bundle,
    load_benchmark_corpus,
    run_benchmark_plan,
    summarize_benchmark,
)
from open_hollywood_engine.models import (
    MODEL_PRESETS,
    ModelDeployment,
    ModelProfileMode,
    ModelSelection,
)
from open_hollywood_engine.workflows import (
    SCENE_PRODUCTION_GRAPH_VERSION,
    STORY_BLUEPRINT_GRAPH_VERSION,
)
from sqlalchemy import Engine

from scripts.evaluation_harness import create_plan_from_database

WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
CORPUS_PATH = WORKSPACE_ROOT / "benchmarks" / "v0.1" / "corpus.json"
CAMPAIGN_ID = UUID("aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa")


class FixtureExecutor:
    """Deterministic output boundary for orchestration tests."""

    def __init__(self, *, fail_case_id: UUID | None = None) -> None:
        self.fail_case_id = fail_case_id
        self.calls: list[UUID] = []

    async def execute(
        self,
        case: BenchmarkCase,
        _prompt: BenchmarkPrompt,
    ) -> BenchmarkOutput:
        self.calls.append(case.case_id)
        if case.case_id == self.fail_case_id:
            raise BenchmarkCaseExecutionError(
                "fixture_failure",
                "The fixture rejected this case.",
            )
        content = " ".join(("story",) * 2_499 + (str(case.case_id),))
        return BenchmarkOutput(
            title="Blind benchmark story",
            content=content,
            content_sha256=hashlib.sha256(content.encode()).hexdigest(),
            word_count=len(content.split()),
            workflow_run_id=uuid5(case.case_id, "workflow"),
            artifact_version_ids=(uuid5(case.case_id, "artifact"),),
            invocation_ids=(uuid5(case.case_id, "invocation"),),
            input_tokens=100,
            output_tokens=500,
            latency_ms=1_000,
            estimated_cost_usd="1.00",
            hard_gates={gate: True for gate in HardGate},
        )


@pytest.fixture
def benchmark_plan() -> tuple[BenchmarkCorpus, BenchmarkPlan]:
    corpus = load_benchmark_corpus(CORPUS_PATH)
    local = ModelSelection(
        provider="ollama",
        model_identifier="local-fixture",
        deployment=ModelDeployment.LOCAL,
    )
    cloud = ModelSelection(
        provider="ollama",
        model_identifier="cloud-fixture",
        deployment=ModelDeployment.CLOUD,
    )
    snapshots = {
        ModelProfileMode.LOCAL: BenchmarkProfileSnapshot.from_configuration(
            profile_id=UUID("00000000-0000-4000-8000-000000000131"),
            configuration=MODEL_PRESETS[ModelProfileMode.LOCAL].configuration(local_model=local),
        ),
        ModelProfileMode.CLOUD: BenchmarkProfileSnapshot.from_configuration(
            profile_id=UUID("00000000-0000-4000-8000-000000000132"),
            configuration=MODEL_PRESETS[ModelProfileMode.CLOUD].configuration(cloud_model=cloud),
        ),
        ModelProfileMode.HYBRID: BenchmarkProfileSnapshot.from_configuration(
            profile_id=UUID("00000000-0000-4000-8000-000000000133"),
            configuration=MODEL_PRESETS[ModelProfileMode.HYBRID].configuration(
                local_model=local,
                cloud_model=cloud,
            ),
        ),
    }
    plan = build_benchmark_plan(
        campaign_id=CAMPAIGN_ID,
        corpus=corpus,
        baseline_model=cloud,
        profiles=snapshots,
        workflow_versions={
            "story_blueprint": STORY_BLUEPRINT_GRAPH_VERSION,
            "scene_production": SCENE_PRODUCTION_GRAPH_VERSION,
        },
    )
    return corpus, plan


def test_frozen_v01_corpus_has_twelve_versioned_prompts() -> None:
    corpus = load_benchmark_corpus(CORPUS_PATH)

    assert len(corpus.prompts) == 12
    assert [prompt.prompt_id for prompt in corpus.prompts] == [
        f"OH-V01-{number:03d}" for number in range(1, 13)
    ]
    assert len(corpus.content_sha256) == 64
    assert all(
        prompt.target_word_count.minimum == 2_500 and prompt.target_word_count.maximum == 5_000
        for prompt in corpus.prompts
    )


def test_plan_expands_every_prompt_into_baseline_and_three_profiles(
    benchmark_plan: tuple[BenchmarkCorpus, BenchmarkPlan],
) -> None:
    corpus, plan = benchmark_plan

    assert len(plan.cases) == len(corpus.prompts) * 4
    assert [case.target_key for case in plan.cases[:4]] == [
        "baseline",
        "local",
        "cloud",
        "hybrid",
    ]
    assert plan.corpus_sha256 == corpus.content_sha256
    baseline_model = plan.cases[0].baseline_model
    assert baseline_model is not None
    assert (
        build_benchmark_plan(
            campaign_id=CAMPAIGN_ID,
            corpus=corpus,
            baseline_model=baseline_model.to_selection(),
            profiles={
                case.profile.mode: case.profile
                for case in plan.cases[:4]
                if case.profile is not None
            },
            workflow_versions=plan.workflow_versions,
        )
        == plan
    )


@pytest.mark.anyio
async def test_harness_is_failure_isolated_and_resumable(
    benchmark_plan: tuple[BenchmarkCorpus, BenchmarkPlan],
) -> None:
    corpus, plan = benchmark_plan
    fail_case = plan.cases[2]
    first_executor = FixtureExecutor(fail_case_id=fail_case.case_id)

    first_report = await run_benchmark_plan(
        plan=plan,
        corpus=corpus,
        executor=first_executor,
    )

    assert len(first_report.results) == 48
    assert first_report.results[2].status is BenchmarkCaseStatus.FAILED
    assert first_report.results[2].error_code == "fixture_failure"

    resumed_executor = FixtureExecutor()
    resumed = await run_benchmark_plan(
        plan=plan,
        corpus=corpus,
        executor=resumed_executor,
        prior_results=first_report.results[:5],
    )

    assert len(resumed_executor.calls) == 43
    assert resumed.results[:5] == first_report.results[:5]
    assert resumed.plan_sha256 == plan.content_sha256


@pytest.mark.anyio
async def test_blind_bundle_hides_provenance_and_randomizes_stably(
    benchmark_plan: tuple[BenchmarkCorpus, BenchmarkPlan],
) -> None:
    corpus, plan = benchmark_plan
    report = await run_benchmark_plan(
        plan=plan,
        corpus=corpus,
        executor=FixtureExecutor(),
    )

    public, private = build_blind_bundle(
        plan=plan,
        corpus=corpus,
        results=report.results,
        blinding_key=b"0123456789abcdef0123456789abcdef",
    )
    repeated_public, repeated_private = build_blind_bundle(
        plan=plan,
        corpus=corpus,
        results=report.results,
        blinding_key=b"0123456789abcdef0123456789abcdef",
    )

    assert len(public.comparisons) == 12 * 5
    assert len(private.answers) == len(public.comparisons)
    assert public == repeated_public
    assert private == repeated_private
    serialized_public = json.dumps(public.model_dump(mode="json"))
    assert "ollama" not in serialized_public
    assert "local-fixture" not in serialized_public
    assert "cloud-fixture" not in serialized_public


@pytest.mark.anyio
async def test_summary_maps_blind_preference_back_to_agentic_system(
    benchmark_plan: tuple[BenchmarkCorpus, BenchmarkPlan],
) -> None:
    corpus, plan = benchmark_plan
    report = await run_benchmark_plan(
        plan=plan,
        corpus=corpus,
        executor=FixtureExecutor(),
    )
    _, answer_key = build_blind_bundle(
        plan=plan,
        corpus=corpus,
        results=report.results,
        blinding_key=b"0123456789abcdef0123456789abcdef",
    )
    cases = {case.case_id: case for case in plan.cases}
    baseline_answer = next(
        answer
        for answer in answer_key.answers
        if {
            cases[answer.candidate_a_case_id].target_key,
            cases[answer.candidate_b_case_id].target_key,
        }
        == {"baseline", "local"}
    )
    preference = (
        BlindPreference.A
        if cases[baseline_answer.candidate_a_case_id].target_key == "local"
        else BlindPreference.B
    )
    score = CanonicalStoryScore(
        dimension_scores={dimension: 4 for dimension in EvaluationDimension},
        hard_gates={gate: True for gate in HardGate},
    )
    review = HumanComparisonReview(
        comparison_id=baseline_answer.comparison_id,
        reviewer_id="reviewer-1",
        preference=preference,
        candidate_a_score=score,
        candidate_b_score=score,
    )

    summary = summarize_benchmark(
        plan=plan,
        results=report.results,
        answer_key=answer_key,
        reviews=(review,),
    )

    assert summary.agentic_baseline_preference_rate == 1
    assert summary.mean_agentic_weighted_score == 4
    assert summary.severe_continuity_free_rate == 1
    assert all(metric.technical_success_rate == 1 for metric in summary.target_metrics)
    assert all(value is True for value in summary.criteria.model_dump().values())


def test_canonical_score_requires_every_dimension_and_hard_gate() -> None:
    with pytest.raises(ValueError, match="every evaluation dimension"):
        CanonicalStoryScore(
            dimension_scores={EvaluationDimension.DIALOGUE: 4},
            hard_gates={gate: True for gate in HardGate},
        )


def test_operator_plan_snapshots_configured_database_profiles(
    migrated_database_path: Path,
    database_engine: Engine,
) -> None:
    store = ModelProfileStore(create_session_factory(database_engine))
    local = ModelSelection(
        provider="ollama",
        model_identifier="local-fixture",
        deployment=ModelDeployment.LOCAL,
    )
    cloud = ModelSelection(
        provider="ollama",
        model_identifier="cloud-fixture",
        deployment=ModelDeployment.CLOUD,
    )
    store.configure_profile(
        BUILTIN_PROFILE_IDS[ModelProfileMode.LOCAL],
        local_model=local,
        cloud_model=None,
    )
    store.configure_profile(
        BUILTIN_PROFILE_IDS[ModelProfileMode.CLOUD],
        local_model=None,
        cloud_model=cloud,
    )
    store.configure_profile(
        BUILTIN_PROFILE_IDS[ModelProfileMode.HYBRID],
        local_model=local,
        cloud_model=cloud,
    )

    plan = create_plan_from_database(
        campaign_id=CAMPAIGN_ID,
        corpus_path=CORPUS_PATH,
        database_path=migrated_database_path,
    )

    assert len(plan.cases) == 48
    assert {case.profile.mode for case in plan.cases if case.profile is not None} == set(
        ModelProfileMode
    )
