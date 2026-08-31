"""Frozen-corpus, campaign, blind-review, and reporting tests."""

from __future__ import annotations

import asyncio
import csv
import hashlib
import json
from datetime import UTC, datetime
from decimal import Decimal
from io import StringIO
from pathlib import Path
from uuid import UUID, uuid5

import pytest
from open_hollywood_api.persistence.database import create_session_factory
from open_hollywood_api.persistence.models import (
    AgentInvocation,
    ArtifactVersion,
    InvocationStatus,
    RunStatus,
    WorkflowRun,
)
from open_hollywood_api.services.evaluation_execution import (
    DirectBaselineBenchmarkExecutor,
    automatic_hard_gates,
)
from open_hollywood_api.services.model_profiles import (
    BUILTIN_PROFILE_IDS,
    ModelProfileStore,
)
from open_hollywood_engine.evaluations import (
    HUMAN_REVIEW_SCHEMA_VERSION,
    REVIEW_CSV_COLUMNS,
    BenchmarkCase,
    BenchmarkCaseExecutionError,
    BenchmarkCaseStatus,
    BenchmarkCorpus,
    BenchmarkFailureAttempt,
    BenchmarkOutput,
    BenchmarkPlan,
    BenchmarkProfileSnapshot,
    BenchmarkPrompt,
    BenchmarkRunReport,
    BlindPreference,
    CanonicalStoryScore,
    EvaluationDimension,
    EvidenceRole,
    HardGate,
    HumanComparisonReview,
    HumanReviewBundle,
    TargetWordCount,
    WordCountAdherence,
    WordCountStatus,
    build_benchmark_plan,
    build_blind_bundle,
    build_campaign_evidence_archive,
    load_benchmark_corpus,
    parse_review_csvs,
    render_review_csv,
    render_review_guide,
    run_benchmark_plan,
    summarize_benchmark,
    verify_campaign_evidence_archive,
)
from open_hollywood_engine.models import (
    MODEL_PRESETS,
    CampaignModelGateway,
    InvocationContext,
    MessageRole,
    ModelCallBudget,
    ModelCapabilities,
    ModelDeployment,
    ModelDescriptor,
    ModelMessage,
    ModelProfileMode,
    ModelRequest,
    ModelResponse,
    ModelSelection,
    ModelTiming,
    ModelUsage,
)
from open_hollywood_engine.workflows import (
    BLUEPRINT_NODE_DEFINITIONS,
    DIALOGUE_NODE_DEFINITIONS,
    PRODUCTION_NODE_DEFINITIONS,
    SCENE_PRODUCTION_GRAPH_VERSION,
    STORY_BLUEPRINT_GRAPH_VERSION,
)
from sqlalchemy import Engine, func, select

from scripts.evaluation_harness import (
    AtomicJsonReportCheckpoint,
    _agentic_case_batch,
    _current_runtime_versions,
    _require_current_runtime_versions,
    _write_json_atomically,
    create_plan_from_database,
)
from scripts.evaluation_harness import (
    main as evaluation_main,
)

WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
CORPUS_PATH = WORKSPACE_ROOT / "benchmarks" / "v0.1" / "corpus.json"
CAMPAIGN_ID = UUID("aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa")


class FixtureExecutor:
    """Deterministic output boundary for orchestration tests."""

    def __init__(self, *, fail_case_id: UUID | None = None, word_count: int = 2_500) -> None:
        self.fail_case_id = fail_case_id
        self.word_count = word_count
        self.calls: list[UUID] = []

    async def execute(
        self,
        case: BenchmarkCase,
        prompt: BenchmarkPrompt,
    ) -> BenchmarkOutput:
        self.calls.append(case.case_id)
        if case.case_id == self.fail_case_id:
            raise BenchmarkCaseExecutionError(
                "fixture_failure",
                "The fixture rejected this case.",
                failure_history=(
                    BenchmarkFailureAttempt(
                        invocation_id=uuid5(case.case_id, "failed-invocation"),
                        workflow_node="continuity",
                        specialist_role="continuity_supervisor",
                        operation="continuity",
                        schema_variant="initial_check",
                        attempt_number=1,
                        error_code="schema_validation_failed",
                        error_message="findings.0 used an invalid structured branch.",
                        provider_finish_reason="stop",
                    ),
                ),
            )
        content = " ".join(("story",) * (self.word_count - 1) + (f"{case.case_id}.",))
        adherence = WordCountAdherence.measure(
            target=prompt.target_word_count,
            actual=self.word_count,
        )
        return BenchmarkOutput(
            title="Blind benchmark story",
            content=content,
            content_sha256=hashlib.sha256(content.encode()).hexdigest(),
            word_count=len(content.split()),
            word_count_adherence=adherence,
            workflow_run_id=uuid5(case.case_id, "workflow"),
            artifact_version_ids=(uuid5(case.case_id, "artifact"),),
            invocation_ids=(uuid5(case.case_id, "invocation"),),
            input_tokens=100,
            output_tokens=500,
            latency_ms=1_000,
            estimated_cost_usd="1.00",
            hard_gates={gate: True for gate in HardGate},
        )


class FixtureGateway:
    """Provider boundary for persisted direct-baseline tests."""

    provider = "ollama"

    def __init__(self, response: ModelResponse) -> None:
        self.response = response
        self.requests: list[ModelRequest] = []

    async def generate(self, request: ModelRequest) -> ModelResponse:
        self.requests.append(request)
        return self.response

    async def list_models(self) -> tuple[ModelDescriptor, ...]:
        return ()

    async def capabilities(self, _model_identifier: str) -> ModelCapabilities:
        raise NotImplementedError

    async def close(self) -> None:
        return None


class SimulatedProcessExit(BaseException):
    """Represent a process ending before normal exception cleanup can run."""


class InterruptedFixtureGateway(FixtureGateway):
    """Leave persisted execution state running to simulate a hard interruption."""

    async def generate(self, request: ModelRequest) -> ModelResponse:
        self.requests.append(request)
        raise SimulatedProcessExit


class BlockingFixtureGateway(FixtureGateway):
    """Hold one request until its caller cancels the in-flight task."""

    def __init__(self, response: ModelResponse) -> None:
        super().__init__(response)
        self.started = asyncio.Event()

    async def generate(self, request: ModelRequest) -> ModelResponse:
        self.requests.append(request)
        self.started.set()
        await asyncio.Event().wait()
        raise AssertionError("the blocking gateway must be cancelled")


class RoutedFixtureGateway(FixtureGateway):
    """Track which deployment receives a routed campaign request."""

    def __init__(self, deployment: ModelDeployment) -> None:
        self.deployment = deployment
        self.requests: list[ModelRequest] = []
        self.closed = False

    async def generate(self, request: ModelRequest) -> ModelResponse:
        self.requests.append(request)
        return ModelResponse(
            provider=self.provider,
            model_identifier=request.model_identifier,
            deployment=self.deployment,
            content="routed response",
            thinking=None,
            finish_reason="stop",
            created_at=datetime.now(UTC),
            usage=ModelUsage(input_tokens=1, output_tokens=1),
            timing=ModelTiming(total_ms=1),
            estimated_cost_usd=Decimal("0"),
        )

    async def close(self) -> None:
        self.closed = True


def _complete_review_form(form: str, *, maximum_rows: int | None = None) -> str:
    reader = csv.DictReader(StringIO(form, newline=""))
    rows = list(reader)
    if maximum_rows is not None:
        rows = rows[:maximum_rows]
    for row in rows:
        row["preference"] = "a"
        for dimension in EvaluationDimension:
            row[f"candidate_a_score__{dimension.value}"] = "4"
            row[f"candidate_b_score__{dimension.value}"] = "4"
        for gate in HardGate:
            row[f"candidate_a_gate__{gate.value}"] = "true"
            row[f"candidate_b_gate__{gate.value}"] = "true"
    output = StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=REVIEW_CSV_COLUMNS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()


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


def test_word_count_target_is_advisory_and_separate_from_hard_gates() -> None:
    target = TargetWordCount(minimum=2_500, maximum=5_000)

    adherence = WordCountAdherence.measure(target=target, actual=5_425)
    gates = automatic_hard_gates(
        content="A complete short-prose story ends here.",
        finish_reason="stop",
    )

    assert adherence.policy == "advisory"
    assert adherence.status is WordCountStatus.OVER_TARGET
    assert adherence.deviation_words == 425
    assert gates[HardGate.COMPLETE] is True
    assert gates[HardGate.TARGET_FORMAT_VALID] is None
    assert gates[HardGate.ENDING_NOT_TRUNCATED] is True


@pytest.mark.anyio
async def test_plan_accepts_complete_output_above_advisory_word_target(
    benchmark_plan: tuple[BenchmarkCorpus, BenchmarkPlan],
) -> None:
    corpus, plan = benchmark_plan
    case = plan.cases[0]

    report = await run_benchmark_plan(
        plan=plan,
        corpus=corpus,
        executor=FixtureExecutor(word_count=5_425),
        case_ids=frozenset({case.case_id}),
    )

    result = report.results[0]
    assert result.status is BenchmarkCaseStatus.SUCCEEDED
    assert result.output is not None
    assert result.output.word_count == 5_425
    assert result.output.word_count_adherence is not None
    assert result.output.word_count_adherence.status is WordCountStatus.OVER_TARGET
    assert result.output.word_count_adherence.deviation_words == 425


def test_word_count_adherence_rejects_incorrect_classification() -> None:
    with pytest.raises(ValueError, match="does not match"):
        WordCountAdherence(
            target=TargetWordCount(minimum=2_500, maximum=5_000),
            actual=5_425,
            status=WordCountStatus.WITHIN_TARGET,
            deviation_words=0,
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
async def test_campaign_gateway_routes_frozen_models_by_deployment() -> None:
    local = RoutedFixtureGateway(ModelDeployment.LOCAL)
    cloud = RoutedFixtureGateway(ModelDeployment.CLOUD)
    gateway = CampaignModelGateway(
        provider="ollama",
        deployments={
            ModelDeployment.LOCAL: local,
            ModelDeployment.CLOUD: cloud,
        },
        model_deployments={
            "local-fixture": ModelDeployment.LOCAL,
            "cloud-fixture": ModelDeployment.CLOUD,
        },
    )

    for model_identifier in ("local-fixture", "cloud-fixture"):
        response = await gateway.generate(
            ModelRequest(
                model_identifier=model_identifier,
                messages=(ModelMessage(role=MessageRole.USER, content="route me"),),
                budget=ModelCallBudget(
                    max_input_tokens=10,
                    max_output_tokens=10,
                    max_cost_usd=Decimal("1"),
                ),
                invocation=InvocationContext(
                    specialist_role="fixture",
                    prompt_template_version="1",
                ),
            )
        )
        assert response.model_identifier == model_identifier
    await gateway.close()

    assert [request.model_identifier for request in local.requests] == ["local-fixture"]
    assert [request.model_identifier for request in cloud.requests] == ["cloud-fixture"]
    assert local.closed is True
    assert cloud.closed is True


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
    assert len(first_report.results[2].failure_history) == 1
    attempt = first_report.results[2].failure_history[0]
    assert attempt.specialist_role == "continuity_supervisor"
    assert attempt.schema_variant == "initial_check"
    serialized = json.loads(first_report.model_dump_json())
    assert serialized["results"][2]["failure_history"][0]["error_message"] == (
        "findings.0 used an invalid structured branch."
    )

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
async def test_harness_atomically_checkpoints_each_new_case_and_can_retry_failures(
    benchmark_plan: tuple[BenchmarkCorpus, BenchmarkPlan],
    tmp_path: Path,
) -> None:
    corpus, plan = benchmark_plan
    failed_case = plan.cases[2]
    first_report = await run_benchmark_plan(
        plan=plan,
        corpus=corpus,
        executor=FixtureExecutor(fail_case_id=failed_case.case_id),
    )
    checkpoint_path = tmp_path / "campaign" / "report.json"
    resumed_executor = FixtureExecutor()

    resumed = await run_benchmark_plan(
        plan=plan,
        corpus=corpus,
        executor=resumed_executor,
        prior_results=first_report.results,
        checkpoint=AtomicJsonReportCheckpoint(checkpoint_path, plan),
        retry_failed=True,
    )

    assert resumed_executor.calls == [failed_case.case_id]
    assert all(result.status is BenchmarkCaseStatus.SUCCEEDED for result in resumed.results)
    assert (
        BenchmarkRunReport.model_validate(json.loads(checkpoint_path.read_text(encoding="utf-8")))
        == resumed
    )


@pytest.mark.anyio
async def test_harness_can_stage_only_one_campaign_target(
    benchmark_plan: tuple[BenchmarkCorpus, BenchmarkPlan],
) -> None:
    corpus, plan = benchmark_plan
    executor = FixtureExecutor()

    report = await run_benchmark_plan(
        plan=plan,
        corpus=corpus,
        executor=executor,
        target_keys=frozenset({"baseline"}),
    )

    assert len(report.results) == 12
    assert executor.calls == [case.case_id for case in plan.cases if case.target_key == "baseline"]


@pytest.mark.anyio
async def test_harness_can_stage_an_exact_case_batch(
    benchmark_plan: tuple[BenchmarkCorpus, BenchmarkPlan],
) -> None:
    corpus, plan = benchmark_plan
    selected = frozenset((plan.cases[1].case_id, plan.cases[3].case_id))
    executor = FixtureExecutor()

    report = await run_benchmark_plan(
        plan=plan,
        corpus=corpus,
        executor=executor,
        case_ids=selected,
    )

    assert executor.calls == [case.case_id for case in plan.cases if case.case_id in selected]
    assert {result.case_id for result in report.results} == selected


def test_operator_partitions_one_target_in_frozen_plan_order(
    benchmark_plan: tuple[BenchmarkCorpus, BenchmarkPlan],
) -> None:
    _, plan = benchmark_plan
    cloud_ids = tuple(case.case_id for case in plan.cases if case.target_key == "cloud")

    batches = tuple(
        _agentic_case_batch(
            plan,
            target_keys=frozenset({"cloud"}),
            explicit_case_ids=None,
            batch_size=4,
            batch_number=number,
        )
        for number in (1, 2, 3)
    )

    assert batches == (cloud_ids[:4], cloud_ids[4:8], cloud_ids[8:12])


@pytest.mark.anyio
async def test_atomic_checkpoint_merges_stale_parallel_batches(
    benchmark_plan: tuple[BenchmarkCorpus, BenchmarkPlan],
    tmp_path: Path,
) -> None:
    corpus, plan = benchmark_plan
    report_path = tmp_path / "campaign" / "report.json"
    first_id = plan.cases[0].case_id
    second_id = plan.cases[1].case_id

    await run_benchmark_plan(
        plan=plan,
        corpus=corpus,
        executor=FixtureExecutor(),
        checkpoint=AtomicJsonReportCheckpoint(report_path, plan),
        case_ids=frozenset({first_id}),
    )
    await run_benchmark_plan(
        plan=plan,
        corpus=corpus,
        executor=FixtureExecutor(),
        checkpoint=AtomicJsonReportCheckpoint(report_path, plan),
        case_ids=frozenset({second_id}),
    )

    merged = BenchmarkRunReport.model_validate(json.loads(report_path.read_text(encoding="utf-8")))
    assert [result.case_id for result in merged.results] == [first_id, second_id]


@pytest.mark.anyio
async def test_direct_baseline_persists_idempotent_model_and_artifact_lineage(
    benchmark_plan: tuple[BenchmarkCorpus, BenchmarkPlan],
    database_engine: Engine,
) -> None:
    corpus, plan = benchmark_plan
    case = plan.cases[0]
    prompt = corpus.prompts[0]
    story = " ".join(("story",) * 2_499 + ("ending.",))
    gateway = FixtureGateway(
        ModelResponse(
            provider="ollama",
            model_identifier="cloud-fixture",
            deployment=ModelDeployment.CLOUD,
            content=f"Title: The Test Story\n{story}",
            thinking=None,
            finish_reason="stop",
            created_at=datetime.now(UTC),
            usage=ModelUsage(input_tokens=200, output_tokens=3_000),
            timing=ModelTiming(total_ms=12_345),
            estimated_cost_usd=Decimal("1.25"),
        )
    )
    executor = DirectBaselineBenchmarkExecutor(
        campaign_id=plan.campaign_id,
        session_factory=create_session_factory(database_engine),
        gateway=gateway,
    )

    first = await executor.execute(case, prompt)
    replayed = await executor.execute(case, prompt)

    assert replayed == first
    assert len(gateway.requests) == 1
    assert first.title == "The Test Story"
    assert first.word_count == 2_500
    assert first.word_count_adherence is not None
    assert first.word_count_adherence.status is WordCountStatus.WITHIN_TARGET
    assert first.word_count_adherence.deviation_words == 0
    assert first.estimated_cost_usd == "1.250000"
    assert first.hard_gates[HardGate.COMPLETE] is True
    assert first.hard_gates[HardGate.TARGET_FORMAT_VALID] is None
    assert first.hard_gates[HardGate.CENTRAL_FACTS_CONSISTENT] is None
    assert first.hard_gates[HardGate.MANDATORY_REQUIREMENTS_PRESENT] is None
    with create_session_factory(database_engine)() as session:
        run = session.get(WorkflowRun, first.workflow_run_id)
        assert run is not None
        assert run.status is RunStatus.SUCCEEDED
        assert session.scalar(select(func.count()).select_from(AgentInvocation)) == 1
        assert session.scalar(select(func.count()).select_from(ArtifactVersion)) == 2
        invocation = session.get(AgentInvocation, first.invocation_ids[0])
        assert invocation is not None
        assert invocation.status is InvocationStatus.SUCCEEDED
        assert invocation.request_settings["provider_response_model_identifier"] == "cloud-fixture"
        assert [version.id for version in invocation.input_versions] != []
        assert [version.id for version in invocation.output_versions] == list(
            first.artifact_version_ids
        )
        assert invocation.output_versions[0].content["word_count_adherence"] == {
            "policy": "advisory",
            "target": {"minimum": 2_500, "maximum": 5_000},
            "actual": 2_500,
            "status": "within_target",
            "deviation_words": 0,
        }


@pytest.mark.anyio
async def test_direct_baseline_reconciles_interrupted_attempt_before_retry(
    benchmark_plan: tuple[BenchmarkCorpus, BenchmarkPlan],
    database_engine: Engine,
) -> None:
    corpus, plan = benchmark_plan
    case = plan.cases[0]
    prompt = corpus.prompts[0]
    story = " ".join(("story",) * 2_499 + ("ending.",))
    response = ModelResponse(
        provider="ollama",
        model_identifier="cloud-fixture",
        deployment=ModelDeployment.CLOUD,
        content=f"Title: Recovered Story\n{story}",
        thinking=None,
        finish_reason="stop",
        created_at=datetime.now(UTC),
        usage=ModelUsage(input_tokens=200, output_tokens=3_000),
        timing=ModelTiming(total_ms=12_345),
        estimated_cost_usd=Decimal("1.25"),
    )
    interrupted = DirectBaselineBenchmarkExecutor(
        campaign_id=plan.campaign_id,
        session_factory=create_session_factory(database_engine),
        gateway=InterruptedFixtureGateway(response),
    )
    with pytest.raises(SimulatedProcessExit):
        await interrupted.execute(case, prompt)

    recovered = DirectBaselineBenchmarkExecutor(
        campaign_id=plan.campaign_id,
        session_factory=create_session_factory(database_engine),
        gateway=FixtureGateway(response),
    )
    output = await recovered.execute(case, prompt)

    with create_session_factory(database_engine)() as session:
        invocations = tuple(
            session.scalars(
                select(AgentInvocation).order_by(
                    AgentInvocation.started_at,
                    AgentInvocation.id,
                )
            )
        )
        assert [invocation.status for invocation in invocations] == [
            InvocationStatus.FAILED,
            InvocationStatus.SUCCEEDED,
        ]
        assert invocations[0].error_code == "interrupted_execution"
        assert output.invocation_ids == (invocations[1].id,)


@pytest.mark.anyio
async def test_direct_baseline_cancellation_marks_invocation_terminal(
    benchmark_plan: tuple[BenchmarkCorpus, BenchmarkPlan],
    database_engine: Engine,
) -> None:
    corpus, plan = benchmark_plan
    case = plan.cases[0]
    response = ModelResponse(
        provider="ollama",
        model_identifier="cloud-fixture",
        deployment=ModelDeployment.CLOUD,
        content="unused",
        thinking=None,
        finish_reason="stop",
        created_at=datetime.now(UTC),
        usage=ModelUsage(input_tokens=0, output_tokens=0),
        timing=ModelTiming(total_ms=0),
        estimated_cost_usd=Decimal("0"),
    )
    gateway = BlockingFixtureGateway(response)
    executor = DirectBaselineBenchmarkExecutor(
        campaign_id=plan.campaign_id,
        session_factory=create_session_factory(database_engine),
        gateway=gateway,
    )
    task = asyncio.create_task(executor.execute(case, corpus.prompts[0]))
    await gateway.started.wait()

    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task

    with create_session_factory(database_engine)() as session:
        invocation = session.scalar(select(AgentInvocation))
        run = session.scalar(select(WorkflowRun))
        assert invocation is not None
        assert invocation.status is InvocationStatus.FAILED
        assert invocation.error_code == "cancelled_execution"
        assert run is not None
        assert run.status is RunStatus.FAILED


def test_operator_parses_long_form_ollama_timeout() -> None:
    from scripts.evaluation_harness import _parser

    args = _parser().parse_args(
        [
            "run-baseline",
            "--plan",
            "plan.json",
            "--report",
            "report.json",
            "--ollama-timeout-seconds",
            "900",
        ]
    )

    assert args.ollama_timeout_seconds == 900.0


def test_formal_runtime_versions_cover_every_nested_graph_and_timeout() -> None:
    versions = _current_runtime_versions()

    assert {
        "direct_story",
        "direct_story_prompt",
        "dialogue_subgraph",
        "story_blueprint",
        "story_blueprint_prompt",
        "scene_production",
        "scene_production_prompt",
    } == set(versions)
    assert all(
        definition.timeout_seconds == 900 for definition in BLUEPRINT_NODE_DEFINITIONS.values()
    )
    assert all(
        definition.timeout_seconds == 900 for definition in DIALOGUE_NODE_DEFINITIONS.values()
    )
    assert all(
        definition.timeout_seconds == 900 for definition in PRODUCTION_NODE_DEFINITIONS.values()
    )


def test_atomic_report_write_retries_transient_windows_file_lock(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output = tmp_path / "report.json"
    original_replace = Path.replace
    attempts = 0

    def transient_replace(source: Path, target: Path) -> Path:
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise PermissionError("simulated transient file lock")
        return original_replace(source, target)

    monkeypatch.setattr(Path, "replace", transient_replace)

    _write_json_atomically(output, {"status": "checkpointed"})

    assert attempts == 3
    assert json.loads(output.read_text(encoding="utf-8")) == {"status": "checkpointed"}
    assert not tuple(tmp_path.glob(".*.tmp"))


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
async def test_review_csv_round_trip_is_bound_to_exact_public_packet(
    benchmark_plan: tuple[BenchmarkCorpus, BenchmarkPlan],
) -> None:
    corpus, plan = benchmark_plan
    report = await run_benchmark_plan(
        plan=plan,
        corpus=corpus,
        executor=FixtureExecutor(),
    )
    public, answer_key = build_blind_bundle(
        plan=plan,
        corpus=corpus,
        results=report.results,
        blinding_key=b"0123456789abcdef0123456789abcdef",
    )
    form = render_review_csv(public, reviewer_id="reviewer-1")
    guide = render_review_guide(public, reviewer_id="reviewer-1")
    completed_form = _complete_review_form(form, maximum_rows=1)

    review_bundle = parse_review_csvs(
        public,
        (completed_form,),
    )
    summary = summarize_benchmark(
        plan=plan,
        results=report.results,
        answer_key=answer_key,
        review_bundle=review_bundle,
    )

    assert review_bundle.public_bundle_sha256 == answer_key.public_bundle_sha256
    assert "Do events follow convincingly" in guide
    assert "word-count range is advisory, not a hard gate" in guide
    assert answer_key.public_bundle_sha256 in guide
    assert len(review_bundle.reviews) == 1
    assert summary.human_review_count == 1
    with pytest.raises(ValueError, match="preference"):
        parse_review_csvs(public, (form,))
    with pytest.raises(ValueError, match="score each comparison only once"):
        parse_review_csvs(public, (completed_form, completed_form))
    mismatched = review_bundle.model_copy(
        update={"public_bundle_sha256": "0" * 64},
    )
    with pytest.raises(ValueError, match="different public review packet"):
        summarize_benchmark(
            plan=plan,
            results=report.results,
            answer_key=answer_key,
            review_bundle=mismatched,
        )


@pytest.mark.anyio
async def test_formal_campaign_evidence_is_complete_deterministic_and_verifiable(
    benchmark_plan: tuple[BenchmarkCorpus, BenchmarkPlan],
    tmp_path: Path,
) -> None:
    corpus, full_plan = benchmark_plan
    plan = full_plan.model_copy(update={"cases": full_plan.cases[:4]})
    report = await run_benchmark_plan(
        plan=plan,
        corpus=corpus,
        executor=FixtureExecutor(),
    )
    public, answer_key = build_blind_bundle(
        plan=plan,
        corpus=corpus,
        results=report.results,
        blinding_key=b"0123456789abcdef0123456789abcdef",
    )
    reviews = parse_review_csvs(
        public,
        (_complete_review_form(render_review_csv(public, reviewer_id="reviewer-1")),),
    )
    summary = summarize_benchmark(
        plan=plan,
        results=report.results,
        answer_key=answer_key,
        review_bundle=reviews,
    )

    manifest, archive = build_campaign_evidence_archive(
        corpus=corpus,
        plan=plan,
        report=report,
        public_bundle=public,
        answer_key=answer_key,
        reviews=reviews,
        summary=summary,
        normal_cloud_run_budget_usd=Decimal("2.0"),
    )
    repeated_manifest, repeated_archive = build_campaign_evidence_archive(
        corpus=corpus,
        plan=plan,
        report=report,
        public_bundle=public,
        answer_key=answer_key,
        reviews=reviews,
        summary=summary,
        normal_cloud_run_budget_usd=Decimal("2.0"),
    )

    assert manifest == repeated_manifest
    assert archive == repeated_archive
    assert verify_campaign_evidence_archive(archive) == manifest
    assert {file.role for file in manifest.files} == set(EvidenceRole)
    assert manifest.terminal_result_count == manifest.planned_case_count == 4
    assert manifest.comparison_count == manifest.review_count == 5
    with pytest.raises(ValueError, match="at least one human review per comparison"):
        build_campaign_evidence_archive(
            corpus=corpus,
            plan=plan,
            report=report,
            public_bundle=public,
            answer_key=answer_key,
            reviews=reviews.model_copy(update={"reviews": reviews.reviews[:-1]}),
            summary=summary,
            normal_cloud_run_budget_usd=Decimal("2.0"),
        )
    with pytest.raises(ValueError, match="archive is invalid"):
        verify_campaign_evidence_archive(archive[:-10])

    paths = {
        "corpus": tmp_path / "corpus.json",
        "plan": tmp_path / "plan.json",
        "report": tmp_path / "report.json",
        "public": tmp_path / "public.json",
        "answer": tmp_path / "answer.json",
        "reviews": tmp_path / "reviews.json",
        "summary": tmp_path / "summary.json",
        "archive": tmp_path / "evidence.zip",
    }
    for key, document in {
        "corpus": corpus,
        "plan": plan,
        "report": report,
        "public": public,
        "answer": answer_key,
        "reviews": reviews,
        "summary": summary,
    }.items():
        paths[key].write_text(document.model_dump_json(), encoding="utf-8")
    assert (
        evaluation_main(
            [
                "seal-evidence",
                "--corpus",
                str(paths["corpus"]),
                "--plan",
                str(paths["plan"]),
                "--report",
                str(paths["report"]),
                "--public-bundle",
                str(paths["public"]),
                "--answer-key",
                str(paths["answer"]),
                "--reviews",
                str(paths["reviews"]),
                "--summary",
                str(paths["summary"]),
                "--output",
                str(paths["archive"]),
            ]
        )
        == 0
    )
    assert paths["archive"].read_bytes() == archive
    assert (
        evaluation_main(
            [
                "verify-evidence",
                "--archive",
                str(paths["archive"]),
            ]
        )
        == 0
    )


@pytest.mark.anyio
async def test_operator_packages_separate_review_evidence_and_summarizes(
    benchmark_plan: tuple[BenchmarkCorpus, BenchmarkPlan],
    tmp_path: Path,
) -> None:
    corpus, plan = benchmark_plan
    report = await run_benchmark_plan(
        plan=plan,
        corpus=corpus,
        executor=FixtureExecutor(),
    )
    plan_path = tmp_path / "plan.json"
    report_path = tmp_path / "report.json"
    key_path = tmp_path / "private.key"
    public_path = tmp_path / "review.json"
    answer_path = tmp_path / "answers.json"
    review_form_path = tmp_path / "reviewer-1.csv"
    review_guide_path = tmp_path / "reviewer-1.md"
    review_bundle_path = tmp_path / "reviews.json"
    summary_path = tmp_path / "summary.json"
    plan_path.write_text(plan.model_dump_json(), encoding="utf-8")
    report_path.write_text(report.model_dump_json(), encoding="utf-8")
    key_path.write_bytes(b"0123456789abcdef0123456789abcdef")

    assert (
        evaluation_main(
            [
                "package-review",
                "--plan",
                str(plan_path),
                "--report",
                str(report_path),
                "--blinding-key",
                str(key_path),
                "--public-output",
                str(public_path),
                "--answer-key-output",
                str(answer_path),
            ]
        )
        == 0
    )
    assert (
        evaluation_main(
            [
                "create-review-form",
                "--public-bundle",
                str(public_path),
                "--reviewer-id",
                "reviewer-1",
                "--output",
                str(review_form_path),
                "--guide-output",
                str(review_guide_path),
            ]
        )
        == 0
    )
    review_form_path.write_text(
        _complete_review_form(
            review_form_path.read_text(encoding="utf-8"),
            maximum_rows=1,
        ),
        encoding="utf-8",
    )
    assert (
        evaluation_main(
            [
                "import-reviews",
                "--public-bundle",
                str(public_path),
                "--input",
                str(review_form_path),
                "--output",
                str(review_bundle_path),
            ]
        )
        == 0
    )
    assert (
        evaluation_main(
            [
                "summarize",
                "--plan",
                str(plan_path),
                "--report",
                str(report_path),
                "--output",
                str(summary_path),
            ]
        )
        == 0
    )

    public_text = public_path.read_text(encoding="utf-8")
    assert len(json.loads(public_text)["comparisons"]) == 60
    assert "ollama" not in public_text
    answer_key = json.loads(answer_path.read_text(encoding="utf-8"))
    assert len(answer_key["answers"]) == 60
    reviews = json.loads(review_bundle_path.read_text(encoding="utf-8"))
    assert reviews["public_bundle_sha256"] == answer_key["public_bundle_sha256"]
    assert len(reviews["reviews"]) == 1
    assert answer_key["public_bundle_sha256"] in review_guide_path.read_text(encoding="utf-8")
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["human_review_count"] == 0
    assert summary["criteria"]["weighted_human_score_at_least_3_5"] is None


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
        review_bundle=HumanReviewBundle(
            schema_version=HUMAN_REVIEW_SCHEMA_VERSION,
            campaign_id=plan.campaign_id,
            public_bundle_sha256=answer_key.public_bundle_sha256,
            reviews=(review,),
        ),
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
    assert plan.workflow_versions == _current_runtime_versions()
    assert {case.profile.mode for case in plan.cases if case.profile is not None} == set(
        ModelProfileMode
    )
    drifted = plan.model_copy(
        update={
            "workflow_versions": {
                **plan.workflow_versions,
                "story_blueprint_prompt": "older",
            }
        }
    )
    with pytest.raises(ValueError, match="runtime versions do not match"):
        _require_current_runtime_versions(drifted)
