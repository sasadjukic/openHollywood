"""Cross-version comparison and human evidence remain matched, blind, and read-only."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest
from open_hollywood_engine.evaluations.canary import (
    KNOWN_BLUEPRINT_ERROR,
    KNOWN_BLUEPRINT_FAILURE,
    CanaryEvidence,
    build_canary_review,
    compare_canaries,
    summarize_canary_reviews,
)
from open_hollywood_engine.evaluations.contracts import (
    BenchmarkCaseResult,
    BenchmarkCaseStatus,
    BenchmarkCorpus,
    BenchmarkPlan,
    BenchmarkRunReport,
    HumanReviewBundle,
    canonical_sha256,
)
from open_hollywood_engine.evaluations.reviews import parse_review_csvs, render_review_csv

from scripts.canary_review import _write_new_files, load_canary
from tests.evaluations.test_harness import (
    FixtureExecutor,
    _complete_review_form,
)
from tests.evaluations.test_harness import (
    benchmark_plan as benchmark_plan,
)


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture
async def canary_pair(
    benchmark_plan: tuple[BenchmarkCorpus, BenchmarkPlan],
) -> tuple[BenchmarkCorpus, CanaryEvidence, CanaryEvidence]:
    corpus, plan = benchmark_plan
    output = await FixtureExecutor(word_count=30).execute(plan.cases[0], corpus.prompts[0])
    report = BenchmarkRunReport(
        schema_version="1",
        campaign_id=plan.campaign_id,
        plan_sha256=plan.content_sha256,
        results=(
            BenchmarkCaseResult(
                case_id=plan.cases[0].case_id, status=BenchmarkCaseStatus.SUCCEEDED, output=output
            ),
        ),
    )
    left = CanaryEvidence(
        "reference", plan, report, canonical_sha256(report.model_dump(mode="json"))
    )
    new_plan = plan.model_copy(
        update={
            "workflow_versions": {
                **plan.workflow_versions,
                "scene_production": "6",
                "scene_production_prompt": "26",
            }
        }
    )
    right_report = report.model_copy(update={"plan_sha256": new_plan.content_sha256})
    right = CanaryEvidence(
        "candidate", new_plan, right_report, canonical_sha256(right_report.model_dump(mode="json"))
    )
    return corpus, left, right


@pytest.mark.anyio
async def test_comparison_does_not_count_unattempted_cases_or_invent_quality(
    canary_pair: tuple[BenchmarkCorpus, CanaryEvidence, CanaryEvidence],
) -> None:
    _, left, right = canary_pair
    result = compare_canaries(left, right)
    assert result["runs"][0]["attempted"] == 1
    assert result["retained_successes"] == [str(left.report.results[0].case_id)]
    assert result["human_quality"] == "pending_separate_blind_review"
    failed = right.report.results[0].model_copy(
        update={
            "status": BenchmarkCaseStatus.FAILED,
            "output": None,
            "error_code": "production_failed",
        }
    )
    changed = replace(right, report=right.report.model_copy(update={"results": (failed,)}))
    assert compare_canaries(left, changed)["lost_successes"] == result["retained_successes"]


@pytest.mark.anyio
@pytest.mark.parametrize("mismatch", ["cases", "workflow_versions", "results", "plan_sha256"])
async def test_mismatched_experiments_are_rejected(
    canary_pair: tuple[BenchmarkCorpus, CanaryEvidence, CanaryEvidence],
    mismatch: str,
) -> None:
    _, left, right = canary_pair
    if mismatch in {"cases", "workflow_versions"}:
        value = right.plan.cases[1:] if mismatch == "cases" else {"story_blueprint": "unexpected"}
        plan = right.plan.model_copy(update={mismatch: value})
        right = replace(
            right,
            plan=plan,
            report=right.report.model_copy(
                update={
                    "plan_sha256": plan.content_sha256,
                }
            ),
        )
    else:
        right = replace(
            right,
            report=right.report.model_copy(
                update={
                    mismatch: () if mismatch == "results" else "0" * 64,
                }
            ),
        )
    with pytest.raises(ValueError):
        compare_canaries(left, right)


@pytest.mark.anyio
async def test_only_exact_inherited_blueprint_failure_is_excluded(
    canary_pair: tuple[BenchmarkCorpus, CanaryEvidence, CanaryEvidence],
) -> None:
    _, left, right = canary_pair
    known_case = left.plan.cases[1].model_copy(update={"case_id": KNOWN_BLUEPRINT_FAILURE})
    failure = BenchmarkCaseResult(
        case_id=KNOWN_BLUEPRINT_FAILURE,
        status=BenchmarkCaseStatus.FAILED,
        error_code="artifact_contract_failed",
        error_message=KNOWN_BLUEPRINT_ERROR,
    )
    runs = []
    for run in (left, right):
        plan = run.plan.model_copy(update={"cases": (*run.plan.cases, known_case)})
        runs.append(
            replace(
                run,
                plan=plan,
                report=run.report.model_copy(
                    update={
                        "plan_sha256": plan.content_sha256,
                        "results": (*run.report.results, failure),
                    }
                ),
            )
        )
    assert compare_canaries(*runs)["runs"][0]["eligible_production_cases"] == 1
    changed = failure.model_copy(update={"error_message": "A different Blueprint failure"})
    runs[1] = replace(
        runs[1],
        report=runs[1].report.model_copy(
            update={
                "results": (runs[1].report.results[0], changed),
            }
        ),
    )
    assert compare_canaries(*runs)["excluded_inherited_blueprint_case"] is None


@pytest.mark.anyio
async def test_blind_packet_and_reviews_bind_exact_cross_version_candidates(
    canary_pair: tuple[BenchmarkCorpus, CanaryEvidence, CanaryEvidence],
) -> None:
    corpus, left, right = canary_pair
    public, private = build_canary_review(left, right, corpus, blinding_key=b"test-only-key-123456")
    assert "reference" not in public.model_dump_json()
    assert "report_sha256" not in public.model_dump_json()
    assert len(public.comparisons) == 1
    assert private.answers[0].candidate_a.case_id == private.answers[0].candidate_b.case_id
    assert private.answers[0].candidate_a.run != private.answers[0].candidate_b.run
    blank = render_review_csv(public, reviewer_id="test-reviewer")
    with pytest.raises(ValueError):
        parse_review_csvs(public, [blank])
    empty = HumanReviewBundle(
        schema_version="2",
        campaign_id=public.campaign_id,
        public_bundle_sha256=private.public_bundle_sha256,
        reviews=(),
    )
    assert summarize_canary_reviews(public, private, empty)["status"] == "pending"
    completed = parse_review_csvs(public, [_complete_review_form(blank)])
    summary = summarize_canary_reviews(public, private, completed)
    assert summary["status"] == "complete"
    assert summary["by_run"]["candidate"]["mean_weighted_score"] == 4
    with pytest.raises(ValueError, match="exact public packet"):
        summarize_canary_reviews(
            public,
            private,
            completed.model_copy(
                update={
                    "public_bundle_sha256": "0" * 64,
                }
            ),
        )


@pytest.mark.anyio
async def test_pinned_reports_and_review_outputs_cannot_be_overwritten(
    canary_pair: tuple[BenchmarkCorpus, CanaryEvidence, CanaryEvidence],
    tmp_path: Path,
) -> None:
    _, left, _ = canary_pair
    source = tmp_path / "canary"
    source.mkdir()
    (source / "plan.json").write_text(left.plan.model_dump_json(), encoding="utf-8")
    (source / "report.json").write_text(left.report.model_dump_json(), encoding="utf-8")
    with pytest.raises(ValueError, match="pinned report digest changed"):
        load_canary("reference", source, expected_sha256="0" * 64)
    with pytest.raises(ValueError, match="outside the source"):
        _write_new_files({source / "new.json": "{}"}, protected_directories=(source,))
    with pytest.raises(ValueError, match="overwrite"):
        _write_new_files({source / "report.json": "{}"}, protected_directories=())
