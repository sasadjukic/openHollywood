"""Matched cross-version canary comparisons without provider calls or invented scores."""

from __future__ import annotations

import hashlib
import hmac
from dataclasses import dataclass
from typing import Any, Literal
from uuid import UUID

from open_hollywood_engine.evaluations.contracts import (
    BenchmarkCorpus,
    BenchmarkPlan,
    BenchmarkRunReport,
    BlindComparison,
    BlindDocument,
    BlindPublicBundle,
    EvaluationModel,
    HumanReviewBundle,
    NonEmptyText,
    Sha256,
    canonical_sha256,
)

KNOWN_BLUEPRINT_FAILURE = UUID("1a7d4aed-05d6-5dc1-b1d6-54c1f85d18de")
KNOWN_BLUEPRINT_ERROR = (
    "Integrated Story Blueprint violates story_blueprint: Value error, "
    "beats missing from scene plans: ['beat5', 'beat6']"
)
_VARIABLE_VERSIONS = {"scene_production", "scene_production_prompt"}


@dataclass(frozen=True)
class CanaryEvidence:
    name: str
    plan: BenchmarkPlan
    report: BenchmarkRunReport
    report_sha256: str

    def validate(self) -> None:
        if not self.name.strip():
            raise ValueError("canary name must not be empty")
        if self.report.campaign_id != self.plan.campaign_id:
            raise ValueError("canary report campaign does not match its plan")
        if self.report.plan_sha256 != self.plan.content_sha256:
            raise ValueError("canary report digest does not match its plan")
        if not self.report.results:
            raise ValueError("canary has no attempted cases")
        if not {r.case_id for r in self.report.results} <= {c.case_id for c in self.plan.cases}:
            raise ValueError("canary report contains an unplanned case")


def require_matched_canaries(left: CanaryEvidence, right: CanaryEvidence) -> None:
    """Allow production-contract versions to differ, not the frozen experiment."""
    left.validate()
    right.validate()
    if left.name == right.name:
        raise ValueError("canary labels must be distinct")
    for field in ("corpus_id", "corpus_version", "corpus_sha256", "cases"):
        if getattr(left.plan, field) != getattr(right.plan, field):
            raise ValueError(f"canary comparison has mismatched {field}")
    versions = [
        {k: v for k, v in run.plan.workflow_versions.items() if k not in _VARIABLE_VERSIONS}
        for run in (left, right)
    ]
    if versions[0] != versions[1]:
        raise ValueError("non-production workflow versions changed")
    if {r.case_id for r in left.report.results} != {r.case_id for r in right.report.results}:
        raise ValueError("canary comparison has mismatched attempted cases")


def compare_canaries(left: CanaryEvidence, right: CanaryEvidence) -> dict[str, Any]:
    require_matched_canaries(left, right)
    successful = [{r.case_id for r in run.report.results if r.output} for run in (left, right)]
    known_excluded = all(
        any(
            r.case_id == KNOWN_BLUEPRINT_FAILURE
            and r.error_code == "artifact_contract_failed"
            and r.error_message == KNOWN_BLUEPRINT_ERROR
            for r in run.report.results
        )
        for run in (left, right)
    )
    denominator = len(left.report.results) - int(known_excluded)
    if denominator == 0:
        raise ValueError("no eligible production cases are available")
    cases = {case.case_id: case for case in left.plan.cases}
    summaries = []
    for run, successes in zip((left, right), successful, strict=True):
        summaries.append(
            {
                "name": run.name,
                "report_sha256": run.report_sha256,
                "workflow_versions": run.plan.workflow_versions,
                "completed": len(successes),
                "attempted": len(run.report.results),
                "eligible_production_cases": denominator,
                "production_completion_rate": len(successes) / denominator,
                "by_target": {
                    target: {
                        "completed": sum(case_id in successes for case_id in selected),
                        "attempted": len(selected),
                    }
                    for target in sorted({case.target_key for case in cases.values()})
                    if (
                        selected := [
                            r.case_id
                            for r in run.report.results
                            if cases[r.case_id].target_key == target
                        ]
                    )
                },
                "unknown_output_hard_gates": sum(
                    value is None
                    for r in run.report.results
                    if r.output
                    for value in r.output.hard_gates.values()
                ),
            }
        )
    return {
        "schema_version": "1",
        "runs": summaries,
        "excluded_inherited_blueprint_case": str(KNOWN_BLUEPRINT_FAILURE)
        if known_excluded
        else None,
        "retained_successes": sorted(map(str, successful[0] & successful[1])),
        "new_successes": sorted(map(str, successful[1] - successful[0])),
        "lost_successes": sorted(map(str, successful[0] - successful[1])),
        "human_quality": "pending_separate_blind_review",
        "interpretation": "One matched sample, not proof of repeatability or literary quality.",
    }


class CanaryOrigin(EvaluationModel):
    run: NonEmptyText
    case_id: UUID
    report_sha256: Sha256
    content_sha256: Sha256


class CanaryAnswer(EvaluationModel):
    comparison_id: NonEmptyText
    candidate_a: CanaryOrigin
    candidate_b: CanaryOrigin


class CanaryAnswerKey(EvaluationModel):
    schema_version: Literal["canary-1"] = "canary-1"
    campaign_id: UUID
    public_bundle_sha256: Sha256
    answers: tuple[CanaryAnswer, ...]


def build_canary_review(
    left: CanaryEvidence,
    right: CanaryEvidence,
    corpus: BenchmarkCorpus,
    *,
    blinding_key: bytes,
) -> tuple[BlindPublicBundle, CanaryAnswerKey]:
    """Blind paired completed stories; never expose the run labels in the public packet."""
    require_matched_canaries(left, right)
    if len(blinding_key) < 16:
        raise ValueError("blinding_key must contain at least 16 bytes")
    if corpus.content_sha256 != left.plan.corpus_sha256:
        raise ValueError("review corpus does not match the frozen plans")
    pair_digest = hmac.new(
        blinding_key, (left.report_sha256 + right.report_sha256).encode(), hashlib.sha256
    ).digest()
    campaign_id = UUID(bytes=pair_digest[:16], version=4)
    prompts = {(p.prompt_id, p.version): p for p in corpus.prompts}
    results = [{r.case_id: r for r in run.report.results} for run in (left, right)]
    comparisons = []
    answers = []
    for case in left.plan.cases:
        outputs = [
            items[case.case_id].output if case.case_id in items else None for items in results
        ]
        if any(output is None for output in outputs):
            continue
        digest = hmac.new(
            blinding_key, pair_digest + case.case_id.bytes, hashlib.sha256
        ).hexdigest()
        order = (1, 0) if int(digest[-1], 16) & 1 else (0, 1)
        documents = []
        origins = []
        labels: tuple[Literal["A", "B"], ...] = ("A", "B")
        for label, index in zip(labels, order, strict=True):
            output = outputs[index]
            assert output is not None
            documents.append(
                BlindDocument(
                    label=label,
                    title=output.title,
                    content=output.content,
                    content_sha256=output.content_sha256,
                )
            )
            origins.append(
                CanaryOrigin(
                    run=(left, right)[index].name,
                    case_id=case.case_id,
                    report_sha256=(left, right)[index].report_sha256,
                    content_sha256=output.content_sha256,
                )
            )
        prompt = prompts[(case.prompt_id, case.prompt_version)]
        comparisons.append(
            BlindComparison(
                comparison_id=digest[:24],
                prompt_id=case.prompt_id,
                prompt_version=case.prompt_version,
                prompt=prompt.prompt,
                candidate_a=documents[0],
                candidate_b=documents[1],
            )
        )
        answers.append(
            CanaryAnswer(
                comparison_id=digest[:24],
                candidate_a=origins[0],
                candidate_b=origins[1],
            )
        )
    if not comparisons:
        raise ValueError("no paired successful cases are available for blind review")
    public = BlindPublicBundle(
        schema_version="1",
        campaign_id=campaign_id,
        comparisons=tuple(sorted(comparisons, key=lambda c: c.comparison_id)),
    )
    return public, CanaryAnswerKey(
        campaign_id=campaign_id,
        public_bundle_sha256=canonical_sha256(public.model_dump(mode="json")),
        answers=tuple(sorted(answers, key=lambda a: a.comparison_id)),
    )


def summarize_canary_reviews(
    public: BlindPublicBundle,
    private: CanaryAnswerKey,
    reviews: HumanReviewBundle,
) -> dict[str, Any]:
    digest = canonical_sha256(public.model_dump(mode="json"))
    if not (
        public.campaign_id == private.campaign_id == reviews.campaign_id
        and digest == private.public_bundle_sha256 == reviews.public_bundle_sha256
    ):
        raise ValueError("reviews and answer key must match the exact public packet")
    answers = {answer.comparison_id: answer for answer in private.answers}
    if len(answers) != len(private.answers) or set(answers) != {
        comparison.comparison_id for comparison in public.comparisons
    }:
        raise ValueError("answer key must cover each comparison exactly once")
    for comparison in public.comparisons:
        answer = answers[comparison.comparison_id]
        for document, origin in (
            (comparison.candidate_a, answer.candidate_a),
            (comparison.candidate_b, answer.candidate_b),
        ):
            if (
                hashlib.sha256(document.content.encode()).hexdigest() != document.content_sha256
                or document.content_sha256 != origin.content_sha256
            ):
                raise ValueError("answer key content digest does not match the public candidate")
    scores: dict[str, list[float]] = {}
    hard_gate_failures: dict[str, int] = {}
    preferences: dict[str, int] = {}
    reviewed = set()
    for review in reviews.reviews:
        if review.comparison_id not in answers:
            raise ValueError("review contains an unknown comparison")
        reviewed.add(review.comparison_id)
        answer = answers[review.comparison_id]
        for label, origin, score in (
            ("a", answer.candidate_a, review.candidate_a_score),
            ("b", answer.candidate_b, review.candidate_b_score),
        ):
            scores.setdefault(origin.run, []).append(score.weighted_score)
            hard_gate_failures[origin.run] = hard_gate_failures.get(origin.run, 0) + int(
                not score.passes_hard_gates
            )
            preferences[origin.run] = preferences.get(origin.run, 0) + int(
                review.preference == label
            )
    return {
        "schema_version": "1",
        "review_submissions": len(reviews.reviews),
        "reviewed_pairs": len(reviewed),
        "pending_pairs": len(answers) - len(reviewed),
        "status": "complete" if len(reviewed) == len(answers) else "pending",
        "by_run": {
            name: {
                "mean_weighted_score": sum(values) / len(values),
                "hard_gate_failures": hard_gate_failures[name],
                "preferences": preferences[name],
            }
            for name, values in scores.items()
        },
        "ties": sum(review.preference == "tie" for review in reviews.reviews),
        "scope": "Paired completed stories only; unpaired failures remain in technical comparison.",
    }
