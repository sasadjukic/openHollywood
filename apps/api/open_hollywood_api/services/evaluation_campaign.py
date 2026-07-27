"""Operator orchestration for resumable agentic benchmark campaigns."""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from uuid import UUID, uuid5

from open_hollywood_engine.evaluations import (
    BenchmarkCase,
    BenchmarkCorpus,
    BenchmarkPlan,
    BenchmarkPrompt,
    BenchmarkReportCheckpoint,
    BenchmarkRunReport,
    run_benchmark_plan,
)
from open_hollywood_engine.models import ModelGateway, ModelProfileMode
from open_hollywood_engine.workflows import (
    BlueprintDecisionAction,
    BlueprintHumanDecision,
)
from sqlalchemy.orm import Session, sessionmaker

from open_hollywood_api.persistence.models import RunStatus, WorkflowRun
from open_hollywood_api.services.agentic_benchmark import (
    AgenticBenchmarkBlueprintService,
    AgenticBenchmarkCaseExecutor,
    AgenticBlueprintPreparation,
)
from open_hollywood_api.services.blueprint_model_executor import (
    BenchmarkBlueprintNodeExecutor,
)
from open_hollywood_api.services.blueprint_workflow import BlueprintWorkflowService

AGENTIC_TARGET_KEYS = frozenset(mode.value for mode in ModelProfileMode)


async def prepare_agentic_cases(
    *,
    plan: BenchmarkPlan,
    corpus: BenchmarkCorpus,
    database_path: Path,
    session_factory: sessionmaker[Session],
    gateway: ModelGateway,
    target_keys: frozenset[str] = AGENTIC_TARGET_KEYS,
) -> tuple[AgenticBlueprintPreparation, ...]:
    """Sequentially prepare selected agentic cases at the approval boundary."""
    cases = _selected_agentic_cases(plan, corpus, target_keys)
    prompts = _campaign_prompts(plan, corpus)
    service = AgenticBenchmarkBlueprintService(
        campaign_id=plan.campaign_id,
        database_path=database_path,
        session_factory=session_factory,
        gateway=gateway,
    )
    preparations: list[AgenticBlueprintPreparation] = []
    for case in cases:
        preparations.append(
            await service.prepare(
                case,
                prompts[(case.prompt_id, case.prompt_version)],
            )
        )
    return tuple(preparations)


async def approve_agentic_cases(
    *,
    plan: BenchmarkPlan,
    corpus: BenchmarkCorpus,
    database_path: Path,
    session_factory: sessionmaker[Session],
    gateway: ModelGateway,
    case_ids: tuple[UUID, ...],
    target_keys: frozenset[str] = AGENTIC_TARGET_KEYS,
) -> tuple[AgenticBlueprintPreparation, ...]:
    """Apply explicit, idempotent approval to already prepared benchmark cases."""
    if not case_ids:
        raise ValueError("at least one agentic case ID is required")
    if len(set(case_ids)) != len(case_ids):
        raise ValueError("agentic case IDs must be unique")
    selected = _selected_agentic_cases(plan, corpus, target_keys)
    selected_by_id = {case.case_id: case for case in selected}
    unknown = set(case_ids).difference(selected_by_id)
    if unknown:
        formatted = ", ".join(sorted(str(case_id) for case_id in unknown))
        raise ValueError(f"case IDs are not selected agentic cases: {formatted}")
    cases = tuple(selected_by_id[case_id] for case_id in case_ids)
    _require_prepared_runs(session_factory, plan.campaign_id, cases)
    prompts = _campaign_prompts(plan, corpus)
    service = AgenticBenchmarkBlueprintService(
        campaign_id=plan.campaign_id,
        database_path=database_path,
        session_factory=session_factory,
        gateway=gateway,
    )
    approved: list[AgenticBlueprintPreparation] = []
    executor = BenchmarkBlueprintNodeExecutor(
        session_factory=session_factory,
        gateway=gateway,
    )
    async with BlueprintWorkflowService(
        database_path,
        session_factory,
        executor,
    ) as workflow:
        for case in cases:
            preparation = await service.prepare(
                case,
                prompts[(case.prompt_id, case.prompt_version)],
            )
            if not preparation.awaiting_approval:
                approved.append(preparation)
                continue
            if preparation.interrupt_id is None:
                raise RuntimeError("paused benchmark Blueprint has no interrupt ID")
            decision = BlueprintHumanDecision(
                id=uuid5(
                    case.case_id,
                    f"benchmark-blueprint-approval:{preparation.interrupt_id}",
                ),
                interrupt_id=preparation.interrupt_id,
                action=BlueprintDecisionAction.APPROVE,
            )
            execution = await workflow.resume(
                preparation.workflow_run_id,
                decision,
            )
            if execution.awaiting_approval:
                raise RuntimeError("approved benchmark Blueprint remained paused")
            approved.append(
                AgenticBlueprintPreparation(
                    case_id=case.case_id,
                    project_id=preparation.project_id,
                    workflow_run_id=execution.workflow_run_id,
                    artifacts=execution.artifacts,
                    awaiting_approval=False,
                    interrupt_id=None,
                )
            )
    return tuple(approved)


async def run_agentic_cases(
    *,
    plan: BenchmarkPlan,
    corpus: BenchmarkCorpus,
    database_path: Path,
    session_factory: sessionmaker[Session],
    gateway: ModelGateway,
    prior_report: BenchmarkRunReport | None,
    checkpoint: BenchmarkReportCheckpoint | None,
    target_keys: frozenset[str] = AGENTIC_TARGET_KEYS,
    retry_failed: bool = False,
) -> BenchmarkRunReport:
    """Run approved agentic cases and checkpoint each terminal result."""
    cases = _selected_agentic_cases(plan, corpus, target_keys)
    _require_approved_runs(session_factory, plan.campaign_id, cases)
    executor = AgenticBenchmarkCaseExecutor(
        campaign_id=plan.campaign_id,
        database_path=database_path,
        session_factory=session_factory,
        gateway=gateway,
    )
    return await run_benchmark_plan(
        plan=plan,
        corpus=corpus,
        executor=executor,
        prior_results=prior_report.results if prior_report is not None else (),
        checkpoint=checkpoint,
        retry_failed=retry_failed,
        target_keys=target_keys,
    )


def _selected_agentic_cases(
    plan: BenchmarkPlan,
    corpus: BenchmarkCorpus,
    target_keys: frozenset[str],
) -> tuple[BenchmarkCase, ...]:
    _campaign_prompts(plan, corpus)
    if not target_keys or not target_keys.issubset(AGENTIC_TARGET_KEYS):
        raise ValueError("agentic target keys must select Local, Cloud, or Hybrid")
    cases = tuple(case for case in plan.cases if case.target_key in target_keys)
    if not cases:
        raise ValueError("the campaign plan has no cases for the selected agentic targets")
    return cases


def _campaign_prompts(
    plan: BenchmarkPlan,
    corpus: BenchmarkCorpus,
) -> dict[tuple[str, str], BenchmarkPrompt]:
    if (
        plan.corpus_id != corpus.corpus_id
        or plan.corpus_version != corpus.corpus_version
        or plan.corpus_sha256 != corpus.content_sha256
    ):
        raise ValueError("benchmark plan does not match the supplied corpus")
    prompts = {(prompt.prompt_id, prompt.version): prompt for prompt in corpus.prompts}
    if any((case.prompt_id, case.prompt_version) not in prompts for case in plan.cases):
        raise ValueError("benchmark plan references an unknown prompt version")
    return prompts


def _require_prepared_runs(
    session_factory: sessionmaker[Session],
    campaign_id: UUID,
    cases: Iterable[BenchmarkCase],
) -> None:
    with session_factory() as session:
        for case in cases:
            run = session.get(
                WorkflowRun,
                uuid5(case.case_id, "agentic-blueprint-workflow"),
            )
            if run is None or run.status not in {RunStatus.PAUSED, RunStatus.SUCCEEDED}:
                raise ValueError(f"agentic case {case.case_id} must be prepared before approval")
            _require_campaign_run(run, campaign_id, case)


def _require_approved_runs(
    session_factory: sessionmaker[Session],
    campaign_id: UUID,
    cases: Iterable[BenchmarkCase],
) -> None:
    unapproved: list[UUID] = []
    with session_factory() as session:
        for case in cases:
            run = session.get(
                WorkflowRun,
                uuid5(case.case_id, "agentic-blueprint-workflow"),
            )
            if run is None:
                unapproved.append(case.case_id)
                continue
            _require_campaign_run(run, campaign_id, case)
            if run.status is not RunStatus.SUCCEEDED:
                unapproved.append(case.case_id)
    if unapproved:
        formatted = ", ".join(str(case_id) for case_id in unapproved)
        raise ValueError(
            "all selected agentic cases require explicit Blueprint approval before "
            f"production; pending cases: {formatted}"
        )


def _require_campaign_run(
    run: WorkflowRun,
    campaign_id: UUID,
    case: BenchmarkCase,
) -> None:
    if run.input_state.get("benchmark_campaign_id") != str(campaign_id) or run.input_state.get(
        "benchmark_case_id"
    ) != str(case.case_id):
        raise ValueError(f"persisted Blueprint run does not match agentic case {case.case_id}")
