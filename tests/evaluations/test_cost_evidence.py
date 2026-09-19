"""Cost acceptance requires complete provenance, including recovered calls."""

from __future__ import annotations

import hashlib
from dataclasses import replace
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from uuid import uuid4
from zipfile import ZipFile

import pytest
from open_hollywood_api.persistence.database import create_session_factory
from open_hollywood_api.persistence.models import AgentInvocation, InvocationStatus
from open_hollywood_api.services.evaluation_execution import DirectBaselineBenchmarkExecutor
from open_hollywood_engine.evaluations import (
    BenchmarkCaseExecutionError,
    BenchmarkCaseResult,
    BenchmarkCaseStatus,
    BenchmarkCorpus,
    BenchmarkInvocationCost,
    BenchmarkOutput,
    BenchmarkPlan,
    BenchmarkRunReport,
    BenchmarkSummary,
    BlindAnswerKey,
    BlindPublicBundle,
    HumanReviewBundle,
    build_campaign_evidence_archive,
    run_benchmark_plan,
    summarize_benchmark,
    verify_campaign_evidence_archive,
)
from open_hollywood_engine.models import (
    ModelCostBasis,
    ModelDeployment,
    ModelResponse,
    ModelTiming,
    ModelUsage,
)
from sqlalchemy import Engine, select

from tests.evaluations.test_harness import FixtureExecutor, FixtureGateway
from tests.evaluations.test_scoped_campaigns import EvidenceInputs, cloud_plan

LEGACY_ARCHIVE = Path(__file__).parent / "fixtures/cost-v1-evidence.zip"


def response(amount: str = "0", basis: ModelCostBasis = ModelCostBasis.UNKNOWN) -> ModelResponse:
    return ModelResponse(
        provider="ollama",
        model_identifier="cloud-fixture",
        deployment=ModelDeployment.CLOUD,
        content="Title: A Story\nThe end.",
        thinking=None,
        finish_reason="stop",
        created_at=datetime.now(UTC),
        usage=ModelUsage(input_tokens=100, output_tokens=10),
        timing=ModelTiming(total_ms=12),
        estimated_cost_usd=Decimal(amount),
        cost_basis=basis,
    )


@pytest.mark.parametrize("amount", ["NaN", "Infinity", "-Infinity", "-1"])
def test_response_rejects_invalid_numeric_costs(amount: str) -> None:
    with pytest.raises(ValueError, match="finite and nonnegative"):
        response(amount)


def test_cloud_response_cannot_claim_local_zero_cost() -> None:
    with pytest.raises(ValueError, match="must execute locally"):
        response("0", ModelCostBasis.LOCAL_INFERENCE)
    assert response("0").cost_basis is ModelCostBasis.UNKNOWN
    assert response("0", ModelCostBasis.PROVIDER_REPORTED).estimated_cost_usd == 0


@pytest.mark.parametrize(
    ("basis", "amount"),
    [
        (ModelCostBasis.UNKNOWN, "0"),
        (ModelCostBasis.PROVIDER_REPORTED, None),
        (ModelCostBasis.LOCAL_INFERENCE, "0.01"),
        (ModelCostBasis.PROVIDER_REPORTED, "-1"),
    ],
)
def test_invocation_evidence_cannot_confuse_unknown_with_zero(
    basis: ModelCostBasis, amount: str | None
) -> None:
    with pytest.raises(ValueError):
        BenchmarkInvocationCost(invocation_id=uuid4(), basis=basis, amount_usd=amount)


@pytest.mark.anyio
@pytest.mark.parametrize(("amount", "expected"), [("0", True), ("2", True), ("2.000001", False)])
async def test_complete_reported_costs_control_acceptance(amount: str, expected: bool) -> None:
    corpus, plan = cloud_plan()
    report = await run_benchmark_plan(plan=plan, corpus=corpus, executor=FixtureExecutor())
    results = []
    for result in report.results:
        assert result.output is not None
        cost = BenchmarkInvocationCost(
            invocation_id=result.output.invocation_ids[0],
            basis=ModelCostBasis.PROVIDER_REPORTED,
            amount_usd=amount,
        )
        # Acceptance uses evidence, not an unrelated legacy numeric placeholder.
        output = result.output.model_copy(
            update={"estimated_cost_usd": "0", "cost_evidence": (cost,)}
        )
        results.append(result.model_copy(update={"output": output}))
    summary = summarize_benchmark(plan=plan, results=results)
    assert summary.schema_version == "2"
    assert summary.criteria.median_cloud_cost_within_budget is expected
    assert all(metric.known_cost_cases == 12 for metric in summary.target_metrics)
    assert all(metric.unknown_cost_cases == 0 for metric in summary.target_metrics)
    assert all(metric.median_cost_usd == float(amount) for metric in summary.target_metrics)


@pytest.mark.anyio
@pytest.mark.parametrize("gap", ["unknown_call", "legacy_output", "missing_case", "failed_case"])
async def test_cost_acceptance_cannot_pass_with_partial_evidence(gap: str) -> None:
    corpus, plan = cloud_plan()
    report = await run_benchmark_plan(plan=plan, corpus=corpus, executor=FixtureExecutor())
    results = list(report.results)
    cloud = results[1]
    assert cloud.output is not None
    if gap == "missing_case":
        results.pop(1)
    elif gap == "failed_case":
        results[1] = BenchmarkCaseResult(
            case_id=cloud.case_id, status=BenchmarkCaseStatus.FAILED, error_code="fixture"
        )
    else:
        evidence = (
            None
            if gap == "legacy_output"
            else (
                BenchmarkInvocationCost(
                    invocation_id=cloud.output.invocation_ids[0],
                    basis=ModelCostBasis.UNKNOWN,
                    amount_usd=None,
                ),
            )
        )
        results[1] = cloud.model_copy(
            update={"output": cloud.output.model_copy(update={"cost_evidence": evidence})}
        )
    summary = summarize_benchmark(plan=plan, results=results)
    metric = next(metric for metric in summary.target_metrics if metric.target == "cloud")
    assert (metric.known_cost_cases, metric.unknown_cost_cases) == (11, 1)
    assert metric.median_cost_usd is None
    assert summary.criteria.median_cloud_cost_within_budget is None


@pytest.mark.anyio
async def test_mixed_local_and_cloud_invocations_need_every_cost_and_exact_lineage() -> None:
    corpus, plan = cloud_plan()
    output = await FixtureExecutor().execute(plan.cases[1], corpus.prompts[0])
    ids = (uuid4(), uuid4(), uuid4())
    evidence = (
        BenchmarkInvocationCost(
            invocation_id=ids[0], basis=ModelCostBasis.LOCAL_INFERENCE, amount_usd="0"
        ),
        BenchmarkInvocationCost(
            invocation_id=ids[1], basis=ModelCostBasis.PROVIDER_REPORTED, amount_usd="1.25"
        ),
        BenchmarkInvocationCost(
            invocation_id=ids[2], basis=ModelCostBasis.UNKNOWN, amount_usd=None
        ),
    )
    output = output.model_copy(update={"invocation_ids": ids, "cost_evidence": evidence})
    assert BenchmarkOutput.model_validate_json(output.model_dump_json()).known_cost_usd is None
    costed = output.model_copy(
        update={
            "cost_evidence": (
                *evidence[:2],
                evidence[2].model_copy(
                    update={"basis": ModelCostBasis.PROVIDER_REPORTED, "amount_usd": "0.25"}
                ),
            )
        }
    )
    assert costed.known_cost_usd == Decimal("1.50")
    for bad_evidence in (evidence[:2], (*evidence, evidence[0])):
        changed = output.model_copy(update={"cost_evidence": bad_evidence})
        with pytest.raises(ValueError, match="every output invocation exactly once"):
            BenchmarkOutput.model_validate_json(changed.model_dump_json())


@pytest.mark.anyio
async def test_baseline_costs_include_rejected_response_and_survive_resume(
    database_engine: Engine,
) -> None:
    corpus, plan = cloud_plan()
    gateway = FixtureGateway(
        replace(response("0.25", ModelCostBasis.PROVIDER_REPORTED), content="Title: Empty")
    )
    executor = DirectBaselineBenchmarkExecutor(
        campaign_id=plan.campaign_id,
        session_factory=create_session_factory(database_engine),
        gateway=gateway,
    )
    with pytest.raises(BenchmarkCaseExecutionError, match="title and story body"):
        await executor.execute(plan.cases[0], corpus.prompts[0])
    gateway.response = response("1.25", ModelCostBasis.PROVIDER_REPORTED)
    output = await executor.execute(plan.cases[0], corpus.prompts[0])
    assert await executor.execute(plan.cases[0], corpus.prompts[0]) == output
    assert len(output.invocation_ids) == 2
    assert output.known_cost_usd == Decimal("1.50")
    assert output.input_tokens == 200
    with create_session_factory(database_engine)() as session:
        rows = session.scalars(select(AgentInvocation).order_by(AgentInvocation.started_at)).all()
        assert [row.status for row in rows] == [InvocationStatus.FAILED, InvocationStatus.SUCCEEDED]
        assert all(row.cost_basis is ModelCostBasis.PROVIDER_REPORTED for row in rows)
        assert rows[0].estimated_cost_usd == Decimal("0.25")


def legacy_inputs() -> EvidenceInputs:
    with ZipFile(LEGACY_ARCHIVE) as archive:
        return EvidenceInputs(
            corpus=BenchmarkCorpus.model_validate_json(archive.read("public/corpus.json")),
            plan=BenchmarkPlan.model_validate_json(archive.read("private/campaign-plan.json")),
            report=BenchmarkRunReport.model_validate_json(
                archive.read("private/campaign-report.json")
            ),
            public_bundle=BlindPublicBundle.model_validate_json(
                archive.read("public/blind-comparisons.json")
            ),
            answer_key=BlindAnswerKey.model_validate_json(
                archive.read("private/blind-answer-key.json")
            ),
            reviews=HumanReviewBundle.model_validate_json(
                archive.read("private/human-reviews.json")
            ),
            summary=BenchmarkSummary.model_validate_json(
                archive.read("private/campaign-summary.json")
            ),
            normal_cloud_run_budget_usd=Decimal("2.00"),
        )


def test_original_archive_verifies_but_legacy_zero_is_not_new_cost_acceptance() -> None:
    archive = LEGACY_ARCHIVE.read_bytes()
    assert (
        hashlib.sha256(archive).hexdigest()
        == "5ad70c4936f070001a294dbd5b43238c0cc2020e1109a44b6eb852700ac5556b"
    )
    assert verify_campaign_evidence_archive(archive).schema_version == "1"
    inputs = legacy_inputs()
    assert inputs["summary"].criteria.median_cloud_cost_within_budget is True
    with pytest.raises(ValueError, match="regenerate the summary"):
        build_campaign_evidence_archive(**inputs)
    summary = summarize_benchmark(
        plan=inputs["plan"],
        results=inputs["report"].results,
        answer_key=inputs["answer_key"],
        review_bundle=inputs["reviews"],
    )
    assert summary.criteria.median_cloud_cost_within_budget is None
    assert all(metric.median_cost_usd is None for metric in summary.target_metrics)
    inputs["summary"] = summary
    manifest, resealed = build_campaign_evidence_archive(**inputs)
    assert manifest.schema_version == "2"
    assert verify_campaign_evidence_archive(resealed) == manifest
    # Unknown cost may be sealed as evidence, but a fabricated pass is rejected.
    inputs["summary"] = summary.model_copy(
        update={
            "criteria": summary.criteria.model_copy(
                update={"median_cloud_cost_within_budget": True}
            )
        }
    )
    with pytest.raises(ValueError, match="summary does not match"):
        build_campaign_evidence_archive(**inputs)


@pytest.mark.parametrize("budget", [float("nan"), float("inf"), -1.0])
def test_invalid_acceptance_budget_is_rejected(budget: float) -> None:
    _, plan = cloud_plan()
    with pytest.raises(ValueError, match="finite and nonnegative"):
        summarize_benchmark(plan=plan, results=(), normal_cloud_run_budget_usd=budget)
