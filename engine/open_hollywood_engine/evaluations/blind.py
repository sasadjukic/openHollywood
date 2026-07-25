"""Deterministic blind-comparison packaging and private answer keys."""

from __future__ import annotations

import hashlib
import hmac
from collections.abc import Iterable

from open_hollywood_engine.evaluations.contracts import (
    BENCHMARK_SCHEMA_VERSION,
    BenchmarkCaseResult,
    BenchmarkCaseStatus,
    BenchmarkCorpus,
    BenchmarkPlan,
    BlindAnswer,
    BlindAnswerKey,
    BlindComparison,
    BlindDocument,
    BlindPublicBundle,
    canonical_sha256,
)

ComparisonPair = tuple[str, str]
DEFAULT_COMPARISON_PAIRS: tuple[ComparisonPair, ...] = (
    ("baseline", "local"),
    ("baseline", "cloud"),
    ("baseline", "hybrid"),
    ("local", "cloud"),
    ("cloud", "hybrid"),
)


def build_blind_bundle(
    *,
    plan: BenchmarkPlan,
    corpus: BenchmarkCorpus,
    results: Iterable[BenchmarkCaseResult],
    blinding_key: bytes,
    comparison_pairs: tuple[ComparisonPair, ...] = DEFAULT_COMPARISON_PAIRS,
) -> tuple[BlindPublicBundle, BlindAnswerKey]:
    """Build a reviewer packet and a separately stored identity map."""
    if len(blinding_key) < 16:
        raise ValueError("blinding_key must contain at least 16 bytes")
    if plan.corpus_sha256 != corpus.content_sha256:
        raise ValueError("benchmark plan and corpus digest do not match")
    _validate_pairs(comparison_pairs)

    cases = {case.case_id: case for case in plan.cases}
    successful = {
        result.case_id: result
        for result in results
        if result.status is BenchmarkCaseStatus.SUCCEEDED
    }
    by_prompt_and_target = {
        (case.prompt_id, case.prompt_version, case.target_key): case for case in plan.cases
    }
    comparisons: list[BlindComparison] = []
    answers: list[BlindAnswer] = []
    for prompt in corpus.prompts:
        for left_target, right_target in comparison_pairs:
            left = by_prompt_and_target.get((prompt.prompt_id, prompt.version, left_target))
            right = by_prompt_and_target.get((prompt.prompt_id, prompt.version, right_target))
            if (
                left is None
                or right is None
                or left.case_id not in successful
                or right.case_id not in successful
            ):
                continue
            comparison_id, reverse = _blind_identity(
                blinding_key,
                plan,
                prompt.prompt_id,
                prompt.version,
                left_target,
                right_target,
            )
            case_a, case_b = (right, left) if reverse else (left, right)
            output_a = successful[case_a.case_id].output
            output_b = successful[case_b.case_id].output
            if output_a is None or output_b is None:
                raise RuntimeError("successful benchmark result is missing its output")
            comparisons.append(
                BlindComparison(
                    comparison_id=comparison_id,
                    prompt_id=prompt.prompt_id,
                    prompt_version=prompt.version,
                    prompt=prompt.prompt,
                    candidate_a=BlindDocument(
                        label="A",
                        title=output_a.title,
                        content=output_a.content,
                        content_sha256=output_a.content_sha256,
                    ),
                    candidate_b=BlindDocument(
                        label="B",
                        title=output_b.title,
                        content=output_b.content,
                        content_sha256=output_b.content_sha256,
                    ),
                )
            )
            answers.append(
                BlindAnswer(
                    comparison_id=comparison_id,
                    candidate_a_case_id=case_a.case_id,
                    candidate_b_case_id=case_b.case_id,
                )
            )

    unknown_result_ids = set(successful).difference(cases)
    if unknown_result_ids:
        raise ValueError("benchmark results contain cases outside the plan")
    public = BlindPublicBundle(
        schema_version=BENCHMARK_SCHEMA_VERSION,
        campaign_id=plan.campaign_id,
        comparisons=tuple(comparisons),
    )
    private = BlindAnswerKey(
        schema_version=BENCHMARK_SCHEMA_VERSION,
        campaign_id=plan.campaign_id,
        public_bundle_sha256=canonical_sha256(public.model_dump(mode="json")),
        answers=tuple(answers),
    )
    return public, private


def _blind_identity(
    key: bytes,
    plan: BenchmarkPlan,
    prompt_id: str,
    prompt_version: str,
    left_target: str,
    right_target: str,
) -> tuple[str, bool]:
    payload = (
        f"{plan.campaign_id}:{prompt_id}:{prompt_version}:{left_target}:{right_target}"
    ).encode()
    digest = hmac.new(key, payload, hashlib.sha256).hexdigest()
    return digest[:24], bool(int(digest[-1], 16) & 1)


def _validate_pairs(pairs: tuple[ComparisonPair, ...]) -> None:
    allowed = {"baseline", "local", "cloud", "hybrid"}
    if not pairs:
        raise ValueError("at least one comparison pair is required")
    normalized = [tuple(sorted(pair)) for pair in pairs]
    if len(set(normalized)) != len(pairs):
        raise ValueError("comparison pairs must be unique regardless of order")
    if any(left not in allowed or right not in allowed or left == right for left, right in pairs):
        raise ValueError("comparison pairs must contain two distinct known targets")
