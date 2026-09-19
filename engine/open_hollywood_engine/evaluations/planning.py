"""Deterministic benchmark campaign expansion."""

from __future__ import annotations

from collections.abc import Mapping
from uuid import UUID, uuid5

from open_hollywood_engine.evaluations.contracts import (
    BENCHMARK_PLAN_SCHEMA_VERSION,
    BenchmarkCase,
    BenchmarkCorpus,
    BenchmarkModelTarget,
    BenchmarkPlan,
    BenchmarkProfileSnapshot,
    BenchmarkScope,
    BenchmarkSystem,
)
from open_hollywood_engine.models import ModelProfileMode, ModelSelection


def build_benchmark_plan(
    *,
    campaign_id: UUID,
    corpus: BenchmarkCorpus,
    baseline_model: ModelSelection,
    profiles: Mapping[ModelProfileMode, BenchmarkProfileSnapshot],
    workflow_versions: Mapping[str, str],
    scope: BenchmarkScope = BenchmarkScope.ALL_PROFILES,
) -> BenchmarkPlan:
    """Expand every prompt into the explicitly selected comparison matrix."""
    if set(profiles) != set(scope.agentic_modes):
        raise ValueError(f"benchmark profiles must match the {scope.value} scope")
    if any(snapshot.mode is not mode for mode, snapshot in profiles.items()):
        raise ValueError("benchmark profile keys must match their snapshot modes")
    normalized_versions = {key.strip(): value.strip() for key, value in workflow_versions.items()}
    if not normalized_versions or any(
        not key or not value for key, value in normalized_versions.items()
    ):
        raise ValueError("workflow versions must contain non-empty keys and values")

    cases: list[BenchmarkCase] = []
    baseline_target = BenchmarkModelTarget.from_selection(baseline_model)
    for prompt in corpus.prompts:
        cases.append(
            BenchmarkCase(
                case_id=_case_id(
                    campaign_id,
                    prompt.prompt_id,
                    prompt.version,
                    "baseline",
                ),
                prompt_id=prompt.prompt_id,
                prompt_version=prompt.version,
                system=BenchmarkSystem.SINGLE_MODEL_BASELINE,
                run_seed=prompt.random_seed,
                baseline_model=baseline_target,
            )
        )
        for mode in scope.agentic_modes:
            cases.append(
                BenchmarkCase(
                    case_id=_case_id(
                        campaign_id,
                        prompt.prompt_id,
                        prompt.version,
                        mode.value,
                    ),
                    prompt_id=prompt.prompt_id,
                    prompt_version=prompt.version,
                    system=BenchmarkSystem.AGENTIC,
                    run_seed=prompt.random_seed,
                    profile=profiles[mode],
                )
            )
    return BenchmarkPlan(
        schema_version=BENCHMARK_PLAN_SCHEMA_VERSION,
        scope=scope,
        campaign_id=campaign_id,
        corpus_id=corpus.corpus_id,
        corpus_version=corpus.corpus_version,
        corpus_sha256=corpus.content_sha256,
        workflow_versions=normalized_versions,
        cases=tuple(cases),
    )


def _case_id(
    campaign_id: UUID,
    prompt_id: str,
    prompt_version: str,
    target: str,
) -> UUID:
    return uuid5(campaign_id, f"{prompt_id}:{prompt_version}:{target}")
