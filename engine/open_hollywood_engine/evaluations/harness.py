"""Sequential, resumable benchmark execution without provider coupling."""

from __future__ import annotations

from typing import Protocol
from uuid import UUID

from open_hollywood_engine.evaluations.contracts import (
    BENCHMARK_SCHEMA_VERSION,
    BenchmarkCase,
    BenchmarkCaseResult,
    BenchmarkCaseStatus,
    BenchmarkCorpus,
    BenchmarkOutput,
    BenchmarkPlan,
    BenchmarkPrompt,
    BenchmarkRunReport,
)


class BenchmarkCaseExecutionError(RuntimeError):
    """Expected, persistable failure of one model-backed benchmark case."""

    def __init__(self, code: str, message: str) -> None:
        normalized_code = code.strip()
        normalized_message = message.strip()
        if not normalized_code or not normalized_message:
            raise ValueError("benchmark error code and message must not be empty")
        super().__init__(normalized_message)
        self.code = normalized_code


class BenchmarkCaseExecutor(Protocol):
    """Application boundary that runs one exact baseline or agentic case."""

    async def execute(
        self,
        case: BenchmarkCase,
        prompt: BenchmarkPrompt,
    ) -> BenchmarkOutput:
        """Return one complete output with exact artifact-version lineage."""
        ...


class BenchmarkReportCheckpoint(Protocol):
    """Durably preserve a validated partial report after each executed case."""

    async def save(self, report: BenchmarkRunReport) -> None:
        """Persist the complete current report atomically."""
        ...


async def run_benchmark_plan(
    *,
    plan: BenchmarkPlan,
    corpus: BenchmarkCorpus,
    executor: BenchmarkCaseExecutor,
    prior_results: tuple[BenchmarkCaseResult, ...] = (),
    checkpoint: BenchmarkReportCheckpoint | None = None,
    retry_failed: bool = False,
    target_keys: frozenset[str] | None = None,
    case_ids: frozenset[UUID] | None = None,
) -> BenchmarkRunReport:
    """Execute missing cases in stable order and checkpoint every new result."""
    _require_matching_corpus(plan, corpus)
    planned_ids = {case.case_id for case in plan.cases}
    prior_by_id = {result.case_id: result for result in prior_results}
    if len(prior_by_id) != len(prior_results):
        raise ValueError("prior benchmark results must have unique case IDs")
    if not set(prior_by_id).issubset(planned_ids):
        raise ValueError("prior benchmark results contain cases outside the plan")
    known_targets = {case.target_key for case in plan.cases}
    if target_keys is not None and not target_keys.issubset(known_targets):
        raise ValueError("target_keys contains an unknown benchmark target")
    if case_ids is not None and not case_ids.issubset(planned_ids):
        raise ValueError("case_ids contains an unknown benchmark case")

    prompts = {(prompt.prompt_id, prompt.version): prompt for prompt in corpus.prompts}
    results: list[BenchmarkCaseResult] = []
    for case in plan.cases:
        prior = prior_by_id.get(case.case_id)
        if prior is not None and not (retry_failed and prior.status is BenchmarkCaseStatus.FAILED):
            results.append(prior)
            continue
        if target_keys is not None and case.target_key not in target_keys:
            continue
        if case_ids is not None and case.case_id not in case_ids:
            continue
        prompt = prompts[(case.prompt_id, case.prompt_version)]
        try:
            output = await executor.execute(case, prompt)
        except BenchmarkCaseExecutionError as error:
            results.append(
                BenchmarkCaseResult(
                    case_id=case.case_id,
                    status=BenchmarkCaseStatus.FAILED,
                    error_code=error.code,
                    error_message=str(error)[:2_000],
                )
            )
        else:
            _validate_output_for_prompt(output, prompt)
            results.append(
                BenchmarkCaseResult(
                    case_id=case.case_id,
                    status=BenchmarkCaseStatus.SUCCEEDED,
                    output=output,
                )
            )
        if checkpoint is not None:
            await checkpoint.save(_report(plan, results))
    report = _report(plan, results)
    if checkpoint is not None:
        await checkpoint.save(report)
    return report


def _report(
    plan: BenchmarkPlan,
    results: list[BenchmarkCaseResult],
) -> BenchmarkRunReport:
    return BenchmarkRunReport(
        schema_version=BENCHMARK_SCHEMA_VERSION,
        campaign_id=plan.campaign_id,
        plan_sha256=plan.content_sha256,
        results=tuple(results),
    )


def _validate_output_for_prompt(
    output: BenchmarkOutput,
    prompt: BenchmarkPrompt,
) -> None:
    adherence = output.word_count_adherence
    if adherence is None:
        raise ValueError("benchmark output must report advisory word-count adherence")
    if adherence.target != prompt.target_word_count:
        raise ValueError("word-count adherence does not match the frozen prompt target")


def _require_matching_corpus(plan: BenchmarkPlan, corpus: BenchmarkCorpus) -> None:
    if (
        plan.corpus_id != corpus.corpus_id
        or plan.corpus_version != corpus.corpus_version
        or plan.corpus_sha256 != corpus.content_sha256
    ):
        raise ValueError("benchmark plan does not match the supplied corpus")
    prompt_refs = {(prompt.prompt_id, prompt.version) for prompt in corpus.prompts}
    if any((case.prompt_id, case.prompt_version) not in prompt_refs for case in plan.cases):
        raise ValueError("benchmark plan references an unknown prompt version")
