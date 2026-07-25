"""Aggregate technical and blind-human benchmark evidence."""

from __future__ import annotations

from collections.abc import Iterable
from statistics import fmean, median
from uuid import UUID

from open_hollywood_engine.evaluations.contracts import (
    BENCHMARK_SCHEMA_VERSION,
    BenchmarkCase,
    BenchmarkCaseResult,
    BenchmarkCaseStatus,
    BenchmarkPlan,
    BenchmarkSuccessCriteria,
    BenchmarkSummary,
    BenchmarkSystem,
    BenchmarkTargetMetrics,
    BlindAnswerKey,
    BlindPreference,
    CanonicalStoryScore,
    EvaluationDimension,
    HardGate,
    HumanComparisonReview,
)


def summarize_benchmark(
    *,
    plan: BenchmarkPlan,
    results: Iterable[BenchmarkCaseResult],
    answer_key: BlindAnswerKey | None = None,
    reviews: Iterable[HumanComparisonReview] = (),
    normal_cloud_run_budget_usd: float = 2.0,
) -> BenchmarkSummary:
    """Calculate the accepted v0.1 metrics and threshold outcomes."""
    if normal_cloud_run_budget_usd < 0:
        raise ValueError("normal cloud run budget must not be negative")
    cases = {case.case_id: case for case in plan.cases}
    all_results = tuple(results)
    result_by_id = {result.case_id: result for result in all_results}
    if len(result_by_id) != len(all_results):
        raise ValueError("benchmark results must have unique case IDs")
    if not set(result_by_id).issubset(cases):
        raise ValueError("benchmark results contain cases outside the plan")

    target_metrics = tuple(
        _target_metrics(target, plan.cases, result_by_id)
        for target in ("baseline", "local", "cloud", "hybrid")
    )
    all_reviews = tuple(reviews)
    human = _human_metrics(
        plan=plan,
        answer_key=answer_key,
        reviews=all_reviews,
    )
    agentic_metrics = [metric for metric in target_metrics if metric.target != "baseline"]
    planned_agentic = sum(metric.planned_cases for metric in agentic_metrics)
    succeeded_agentic = sum(metric.succeeded_cases for metric in agentic_metrics)
    completion_rate = succeeded_agentic / planned_agentic if planned_agentic else 0.0
    cloud_costs = [
        float(result.output.estimated_cost_usd)
        for case in plan.cases
        if case.target_key in {"cloud", "hybrid"}
        and (result := result_by_id.get(case.case_id)) is not None
        and result.status is BenchmarkCaseStatus.SUCCEEDED
        and result.output is not None
    ]
    median_cloud_cost = median(cloud_costs) if cloud_costs else None
    criteria = BenchmarkSuccessCriteria(
        technical_completion_at_least_95_percent=completion_rate >= 0.95,
        severe_continuity_free_at_least_80_percent=(
            human.continuity_rate >= 0.80 if human.continuity_rate is not None else None
        ),
        weighted_human_score_at_least_3_5=(
            human.mean_weighted_score >= 3.5 if human.mean_weighted_score is not None else None
        ),
        no_dimension_average_below_2_5=(
            human.lowest_dimension_mean >= 2.5 if human.lowest_dimension_mean is not None else None
        ),
        agentic_preference_at_least_60_percent=(
            human.preference_rate >= 0.60 if human.preference_rate is not None else None
        ),
        median_cloud_cost_within_budget=(
            median_cloud_cost <= normal_cloud_run_budget_usd
            if median_cloud_cost is not None
            else None
        ),
    )
    return BenchmarkSummary(
        schema_version=BENCHMARK_SCHEMA_VERSION,
        campaign_id=plan.campaign_id,
        target_metrics=target_metrics,
        human_review_count=len(all_reviews),
        mean_agentic_weighted_score=human.mean_weighted_score,
        lowest_agentic_dimension_mean=human.lowest_dimension_mean,
        severe_continuity_free_rate=human.continuity_rate,
        agentic_baseline_preference_rate=human.preference_rate,
        criteria=criteria,
    )


class _HumanMetrics:
    def __init__(
        self,
        *,
        mean_weighted_score: float | None,
        lowest_dimension_mean: float | None,
        continuity_rate: float | None,
        preference_rate: float | None,
    ) -> None:
        self.mean_weighted_score = mean_weighted_score
        self.lowest_dimension_mean = lowest_dimension_mean
        self.continuity_rate = continuity_rate
        self.preference_rate = preference_rate


def _human_metrics(
    *,
    plan: BenchmarkPlan,
    answer_key: BlindAnswerKey | None,
    reviews: tuple[HumanComparisonReview, ...],
) -> _HumanMetrics:
    if not reviews:
        return _HumanMetrics(
            mean_weighted_score=None,
            lowest_dimension_mean=None,
            continuity_rate=None,
            preference_rate=None,
        )
    if answer_key is None:
        raise ValueError("blind reviews require a private answer key")
    if answer_key.campaign_id != plan.campaign_id:
        raise ValueError("blind answer key belongs to a different campaign")

    case_by_id = {case.case_id: case for case in plan.cases}
    answers = {answer.comparison_id: answer for answer in answer_key.answers}
    if len(answers) != len(answer_key.answers):
        raise ValueError("blind answer-key comparison IDs must be unique")
    agentic_scores: list[CanonicalStoryScore] = []
    baseline_preferences: list[float] = []
    seen_reviews: set[tuple[str, str]] = set()
    for review in reviews:
        review_key = (review.comparison_id, review.reviewer_id)
        if review_key in seen_reviews:
            raise ValueError("a reviewer may score each comparison only once")
        seen_reviews.add(review_key)
        try:
            answer = answers[review.comparison_id]
            case_a = case_by_id[answer.candidate_a_case_id]
            case_b = case_by_id[answer.candidate_b_case_id]
        except KeyError as error:
            raise ValueError("blind review references an unknown comparison") from error

        if case_a.system is BenchmarkSystem.AGENTIC:
            agentic_scores.append(review.candidate_a_score)
        if case_b.system is BenchmarkSystem.AGENTIC:
            agentic_scores.append(review.candidate_b_score)
        if {case_a.system, case_b.system} == {
            BenchmarkSystem.SINGLE_MODEL_BASELINE,
            BenchmarkSystem.AGENTIC,
        }:
            baseline_preferences.append(
                _agentic_preference_value(review.preference, case_a, case_b)
            )

    if not agentic_scores:
        return _HumanMetrics(
            mean_weighted_score=None,
            lowest_dimension_mean=None,
            continuity_rate=None,
            preference_rate=(fmean(baseline_preferences) if baseline_preferences else None),
        )
    dimension_means = {
        dimension: fmean(score.dimension_scores[dimension] for score in agentic_scores)
        for dimension in EvaluationDimension
    }
    return _HumanMetrics(
        mean_weighted_score=fmean(score.weighted_score for score in agentic_scores),
        lowest_dimension_mean=min(dimension_means.values()),
        continuity_rate=fmean(
            float(score.hard_gates[HardGate.CENTRAL_FACTS_CONSISTENT]) for score in agentic_scores
        ),
        preference_rate=(fmean(baseline_preferences) if baseline_preferences else None),
    )


def _agentic_preference_value(
    preference: BlindPreference,
    case_a: BenchmarkCase,
    case_b: BenchmarkCase,
) -> float:
    if preference is BlindPreference.TIE:
        return 0.5
    preferred = case_a if preference is BlindPreference.A else case_b
    return float(preferred.system is BenchmarkSystem.AGENTIC)


def _target_metrics(
    target: str,
    cases: tuple[BenchmarkCase, ...],
    results: dict[UUID, BenchmarkCaseResult],
) -> BenchmarkTargetMetrics:
    target_cases = [case for case in cases if case.target_key == target]
    succeeded = [
        result
        for case in target_cases
        if (result := results.get(case.case_id)) is not None
        and result.status is BenchmarkCaseStatus.SUCCEEDED
    ]
    costs = [
        float(result.output.estimated_cost_usd) for result in succeeded if result.output is not None
    ]
    return BenchmarkTargetMetrics(
        target=target,
        planned_cases=len(target_cases),
        succeeded_cases=len(succeeded),
        technical_success_rate=(len(succeeded) / len(target_cases) if target_cases else 0.0),
        median_cost_usd=median(costs) if costs else None,
    )
