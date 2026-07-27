"""Operate reproducible Step 19 campaigns and their separated review evidence."""

from __future__ import annotations

import argparse
import asyncio
import json
import secrets
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

from open_hollywood_api.persistence.database import (
    create_session_factory,
    create_sqlite_engine,
)
from open_hollywood_api.services.agentic_benchmark import AgenticBlueprintPreparation
from open_hollywood_api.services.evaluation_campaign import (
    AGENTIC_TARGET_KEYS,
    approve_agentic_cases,
    prepare_agentic_cases,
    run_agentic_cases,
)
from open_hollywood_api.services.evaluation_execution import (
    DirectBaselineBenchmarkExecutor,
)
from open_hollywood_api.services.model_profiles import ModelProfileStore
from open_hollywood_engine.evaluations import (
    BENCHMARK_SCHEMA_VERSION,
    BenchmarkPlan,
    BenchmarkProfileSnapshot,
    BenchmarkRunReport,
    BlindAnswerKey,
    HumanReviewBundle,
    build_benchmark_plan,
    build_blind_bundle,
    load_benchmark_corpus,
    run_benchmark_plan,
    summarize_benchmark,
)
from open_hollywood_engine.models import (
    CampaignModelGateway,
    EnvironmentSecretStore,
    ModelDeployment,
    ModelGateway,
    ModelProfileConfiguration,
    ModelProfileMode,
    ModelSelection,
    OllamaGateway,
    OllamaHost,
)
from open_hollywood_engine.workflows import (
    SCENE_PRODUCTION_GRAPH_VERSION,
    STORY_BLUEPRINT_GRAPH_VERSION,
)

WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CORPUS_PATH = WORKSPACE_ROOT / "benchmarks" / "v0.1" / "corpus.json"
DEFAULT_DATABASE_PATH = WORKSPACE_ROOT / "data" / "open_hollywood.db"


class AtomicJsonReportCheckpoint:
    """Crash-safe report checkpoint for long sequential campaign runs."""

    def __init__(self, path: Path, plan: BenchmarkPlan) -> None:
        self._path = path
        self._plan = plan

    async def save(self, report: BenchmarkRunReport) -> None:
        """Validate campaign identity before atomically replacing the report."""
        _require_matching_report(self._plan, report)
        _write_json_atomically(self._path, report.model_dump(mode="json"))


def create_plan_from_database(
    *,
    campaign_id: UUID,
    corpus_path: Path,
    database_path: Path,
) -> BenchmarkPlan:
    """Snapshot all three configured presets and the cloud writer baseline."""
    corpus = load_benchmark_corpus(corpus_path)
    engine = create_sqlite_engine(database_path)
    try:
        records = ModelProfileStore(create_session_factory(engine)).list_profiles()
    finally:
        engine.dispose()
    profiles = {
        record.mode: BenchmarkProfileSnapshot.from_configuration(
            profile_id=record.id,
            configuration=record.configuration,
        )
        for record in records
    }
    try:
        cloud_configuration = next(
            record.configuration for record in records if record.mode is ModelProfileMode.CLOUD
        )
    except StopIteration as error:
        raise ValueError("the Cloud model preset is missing") from error
    baseline_model = cloud_configuration.selection_for("scene_writer")
    return build_benchmark_plan(
        campaign_id=campaign_id,
        corpus=corpus,
        baseline_model=baseline_model,
        profiles=profiles,
        workflow_versions={
            "story_blueprint": STORY_BLUEPRINT_GRAPH_VERSION,
            "scene_production": SCENE_PRODUCTION_GRAPH_VERSION,
        },
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Open Hollywood frozen-corpus evaluation harness",
    )
    commands = parser.add_subparsers(dest="command", required=True)
    validate = commands.add_parser(
        "validate-corpus",
        help="Validate the frozen corpus and print its immutable digest.",
    )
    validate.add_argument("--corpus", type=Path, default=DEFAULT_CORPUS_PATH)

    plan = commands.add_parser(
        "plan",
        help="Create a 48-case baseline/Local/Cloud/Hybrid campaign plan.",
    )
    plan.add_argument("--corpus", type=Path, default=DEFAULT_CORPUS_PATH)
    plan.add_argument("--database", type=Path, default=DEFAULT_DATABASE_PATH)
    plan.add_argument("--campaign-id", type=UUID, default=None)
    plan.add_argument("--output", type=Path, required=True)
    plan.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace an existing plan file.",
    )

    run_baseline = commands.add_parser(
        "run-baseline",
        help="Run or resume the direct single-model cases through configured Ollama routing.",
    )
    run_baseline.add_argument("--corpus", type=Path, default=DEFAULT_CORPUS_PATH)
    run_baseline.add_argument("--database", type=Path, default=DEFAULT_DATABASE_PATH)
    run_baseline.add_argument("--plan", type=Path, required=True)
    run_baseline.add_argument("--report", type=Path, required=True)
    run_baseline.add_argument("--ollama-base-url", type=str)
    run_baseline.add_argument("--direct-ollama-cloud", action="store_true")
    run_baseline.add_argument("--ollama-cloud-base-url", type=str)
    run_baseline.add_argument("--retry-failed", action="store_true")

    prepare_agentic = commands.add_parser(
        "prepare-agentic",
        help=(
            "Run or replay agentic Blueprint generation and stop at the mandatory "
            "human approval interrupt."
        ),
    )
    _add_agentic_execution_arguments(prepare_agentic)

    approve_blueprints = commands.add_parser(
        "approve-blueprints",
        help="Explicitly approve one or more prepared benchmark Blueprints.",
    )
    _add_agentic_execution_arguments(approve_blueprints)
    approve_blueprints.add_argument(
        "--case-id",
        type=UUID,
        action="append",
        required=True,
        help="Prepared agentic case to approve; repeat for multiple reviewed cases.",
    )

    run_agentic = commands.add_parser(
        "run-agentic",
        help="Run or resume approved Local, Cloud, and Hybrid production cases.",
    )
    _add_agentic_execution_arguments(run_agentic)
    run_agentic.add_argument("--report", type=Path, required=True)
    run_agentic.add_argument("--retry-failed", action="store_true")

    key = commands.add_parser(
        "create-review-key",
        help="Create a private random key used to blind one campaign.",
    )
    key.add_argument("--output", type=Path, required=True)
    key.add_argument("--overwrite", action="store_true")

    package = commands.add_parser(
        "package-review",
        help="Create a provenance-free reviewer packet and separate private answer key.",
    )
    package.add_argument("--corpus", type=Path, default=DEFAULT_CORPUS_PATH)
    package.add_argument("--plan", type=Path, required=True)
    package.add_argument("--report", type=Path, required=True)
    package.add_argument("--blinding-key", type=Path, required=True)
    package.add_argument("--public-output", type=Path, required=True)
    package.add_argument("--answer-key-output", type=Path, required=True)
    package.add_argument("--overwrite", action="store_true")

    summary = commands.add_parser(
        "summarize",
        help="Aggregate technical results and optional validated blind reviews.",
    )
    summary.add_argument("--plan", type=Path, required=True)
    summary.add_argument("--report", type=Path, required=True)
    summary.add_argument("--answer-key", type=Path)
    summary.add_argument("--reviews", type=Path)
    summary.add_argument("--normal-cloud-run-budget-usd", type=float, default=2.0)
    summary.add_argument("--output", type=Path, required=True)
    summary.add_argument("--overwrite", action="store_true")
    return parser


def _add_agentic_execution_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--corpus", type=Path, default=DEFAULT_CORPUS_PATH)
    parser.add_argument("--database", type=Path, default=DEFAULT_DATABASE_PATH)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument(
        "--target",
        action="append",
        choices=sorted(AGENTIC_TARGET_KEYS),
        help="Agentic profile target; repeat as needed. Defaults to all three profiles.",
    )
    parser.add_argument("--ollama-base-url", type=str)
    parser.add_argument(
        "--direct-ollama-cloud",
        action="store_true",
        help="Route cloud deployments directly to Ollama Cloud using OLLAMA_API_KEY.",
    )
    parser.add_argument("--ollama-cloud-base-url", type=str)


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.command == "validate-corpus":
        corpus = load_benchmark_corpus(args.corpus)
        print(
            json.dumps(
                {
                    "corpus_id": corpus.corpus_id,
                    "corpus_version": corpus.corpus_version,
                    "content_sha256": corpus.content_sha256,
                    "prompt_count": len(corpus.prompts),
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 0

    if args.command == "create-review-key":
        output = args.output
        _require_writable_outputs((output,), overwrite=args.overwrite)
        _write_bytes_atomically(output, secrets.token_bytes(32))
        print(
            json.dumps(
                {
                    "output": str(output.resolve()),
                    "bytes": 32,
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 0

    if args.command == "plan":
        output = args.output
        _require_writable_outputs((output,), overwrite=args.overwrite)
        plan = create_plan_from_database(
            campaign_id=args.campaign_id or uuid4(),
            corpus_path=args.corpus,
            database_path=args.database,
        )
        _write_json_atomically(output, plan.model_dump(mode="json"))
        print(
            json.dumps(
                {
                    "campaign_id": str(plan.campaign_id),
                    "case_count": len(plan.cases),
                    "output": str(output.resolve()),
                    "plan_sha256": plan.content_sha256,
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 0

    plan = BenchmarkPlan.model_validate(_read_json(args.plan))
    if args.command == "run-baseline":
        report_path = args.report
        prior_report = (
            BenchmarkRunReport.model_validate(_read_json(report_path))
            if report_path.exists()
            else None
        )
        if prior_report is not None:
            _require_matching_report(plan, prior_report)
        report = asyncio.run(
            _run_direct_baseline(
                plan=plan,
                corpus_path=args.corpus,
                database_path=args.database,
                report_path=report_path,
                prior_report=prior_report,
                ollama_base_url=args.ollama_base_url,
                direct_ollama_cloud=args.direct_ollama_cloud,
                ollama_cloud_base_url=args.ollama_cloud_base_url,
                retry_failed=args.retry_failed,
            )
        )
        baseline_results = [
            result
            for result in report.results
            if next(case for case in plan.cases if case.case_id == result.case_id).target_key
            == "baseline"
        ]
        print(
            json.dumps(
                {
                    "campaign_id": str(plan.campaign_id),
                    "baseline_completed": len(baseline_results),
                    "baseline_succeeded": sum(
                        result.status.value == "succeeded" for result in baseline_results
                    ),
                    "report": str(report_path.resolve()),
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 0

    if args.command == "prepare-agentic":
        target_keys = _agentic_target_keys(args.target)
        preparations = asyncio.run(
            _prepare_agentic_with_ollama(
                plan=plan,
                corpus_path=args.corpus,
                database_path=args.database,
                target_keys=target_keys,
                ollama_base_url=args.ollama_base_url,
                direct_ollama_cloud=args.direct_ollama_cloud,
                ollama_cloud_base_url=args.ollama_cloud_base_url,
            )
        )
        print(
            json.dumps(
                {
                    "campaign_id": str(plan.campaign_id),
                    "prepared": len(preparations),
                    "awaiting_approval": sum(
                        preparation.awaiting_approval for preparation in preparations
                    ),
                    "cases": [
                        {
                            "case_id": str(preparation.case_id),
                            "workflow_run_id": str(preparation.workflow_run_id),
                            "awaiting_approval": preparation.awaiting_approval,
                            "interrupt_id": preparation.interrupt_id,
                        }
                        for preparation in preparations
                    ],
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 0

    if args.command == "approve-blueprints":
        target_keys = _agentic_target_keys(args.target)
        approved = asyncio.run(
            _approve_agentic_with_ollama(
                plan=plan,
                corpus_path=args.corpus,
                database_path=args.database,
                case_ids=tuple(args.case_id),
                target_keys=target_keys,
                ollama_base_url=args.ollama_base_url,
                direct_ollama_cloud=args.direct_ollama_cloud,
                ollama_cloud_base_url=args.ollama_cloud_base_url,
            )
        )
        print(
            json.dumps(
                {
                    "campaign_id": str(plan.campaign_id),
                    "approved": len(approved),
                    "cases": [
                        {
                            "case_id": str(preparation.case_id),
                            "workflow_run_id": str(preparation.workflow_run_id),
                        }
                        for preparation in approved
                    ],
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 0

    if args.command == "run-agentic":
        target_keys = _agentic_target_keys(args.target)
        report_path = args.report
        prior_report = (
            BenchmarkRunReport.model_validate(_read_json(report_path))
            if report_path.exists()
            else None
        )
        if prior_report is not None:
            _require_matching_report(plan, prior_report)
        report = asyncio.run(
            _run_agentic_with_ollama(
                plan=plan,
                corpus_path=args.corpus,
                database_path=args.database,
                report_path=report_path,
                prior_report=prior_report,
                target_keys=target_keys,
                ollama_base_url=args.ollama_base_url,
                direct_ollama_cloud=args.direct_ollama_cloud,
                ollama_cloud_base_url=args.ollama_cloud_base_url,
                retry_failed=args.retry_failed,
            )
        )
        selected_case_ids = {case.case_id for case in plan.cases if case.target_key in target_keys}
        selected_results = [
            result for result in report.results if result.case_id in selected_case_ids
        ]
        print(
            json.dumps(
                {
                    "campaign_id": str(plan.campaign_id),
                    "agentic_completed": len(selected_results),
                    "agentic_succeeded": sum(
                        result.status.value == "succeeded" for result in selected_results
                    ),
                    "report": str(report_path.resolve()),
                    "targets": sorted(target_keys),
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 0

    report = BenchmarkRunReport.model_validate(_read_json(args.report))
    _require_matching_report(plan, report)

    if args.command == "package-review":
        public_output = args.public_output
        answer_key_output = args.answer_key_output
        _require_distinct_paths(public_output, answer_key_output)
        _require_writable_outputs(
            (public_output, answer_key_output),
            overwrite=args.overwrite,
        )
        public, answer_key = build_blind_bundle(
            plan=plan,
            corpus=load_benchmark_corpus(args.corpus),
            results=report.results,
            blinding_key=args.blinding_key.read_bytes(),
        )
        _write_json_atomically(public_output, public.model_dump(mode="json"))
        _write_json_atomically(answer_key_output, answer_key.model_dump(mode="json"))
        print(
            json.dumps(
                {
                    "campaign_id": str(plan.campaign_id),
                    "comparison_count": len(public.comparisons),
                    "public_output": str(public_output.resolve()),
                    "answer_key_output": str(answer_key_output.resolve()),
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 0

    if args.reviews is not None and args.answer_key is None:
        raise ValueError("--reviews requires --answer-key")
    loaded_answer_key = (
        BlindAnswerKey.model_validate(_read_json(args.answer_key))
        if args.answer_key is not None
        else None
    )
    review_bundle = (
        HumanReviewBundle.model_validate(_read_json(args.reviews))
        if args.reviews is not None
        else HumanReviewBundle(
            schema_version=BENCHMARK_SCHEMA_VERSION,
            campaign_id=plan.campaign_id,
            reviews=(),
        )
    )
    if review_bundle.campaign_id != plan.campaign_id:
        raise ValueError("human reviews belong to a different campaign")
    output = args.output
    _require_writable_outputs((output,), overwrite=args.overwrite)
    summary = summarize_benchmark(
        plan=plan,
        results=report.results,
        answer_key=loaded_answer_key,
        reviews=review_bundle.reviews,
        normal_cloud_run_budget_usd=args.normal_cloud_run_budget_usd,
    )
    _write_json_atomically(output, summary.model_dump(mode="json"))
    print(
        json.dumps(
            {
                "campaign_id": str(plan.campaign_id),
                "human_review_count": summary.human_review_count,
                "output": str(output.resolve()),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


async def _run_direct_baseline(
    *,
    plan: BenchmarkPlan,
    corpus_path: Path,
    database_path: Path,
    report_path: Path,
    prior_report: BenchmarkRunReport | None,
    ollama_base_url: str | None,
    direct_ollama_cloud: bool,
    ollama_cloud_base_url: str | None,
    retry_failed: bool,
) -> BenchmarkRunReport:
    engine = create_sqlite_engine(database_path)
    gateway = _ollama_campaign_gateway(
        plan,
        target_keys=frozenset({"baseline"}),
        ollama_base_url=ollama_base_url,
        direct_ollama_cloud=direct_ollama_cloud,
        ollama_cloud_base_url=ollama_cloud_base_url,
    )
    try:
        executor = DirectBaselineBenchmarkExecutor(
            campaign_id=plan.campaign_id,
            session_factory=create_session_factory(engine),
            gateway=gateway,
        )
        return await run_benchmark_plan(
            plan=plan,
            corpus=load_benchmark_corpus(corpus_path),
            executor=executor,
            prior_results=prior_report.results if prior_report is not None else (),
            checkpoint=AtomicJsonReportCheckpoint(report_path, plan),
            retry_failed=retry_failed,
            target_keys=frozenset({"baseline"}),
        )
    finally:
        await gateway.close()
        engine.dispose()


async def _prepare_agentic_with_ollama(
    *,
    plan: BenchmarkPlan,
    corpus_path: Path,
    database_path: Path,
    target_keys: frozenset[str],
    ollama_base_url: str | None,
    direct_ollama_cloud: bool,
    ollama_cloud_base_url: str | None,
) -> tuple[AgenticBlueprintPreparation, ...]:
    engine = create_sqlite_engine(database_path)
    gateway = _ollama_campaign_gateway(
        plan,
        target_keys=target_keys,
        ollama_base_url=ollama_base_url,
        direct_ollama_cloud=direct_ollama_cloud,
        ollama_cloud_base_url=ollama_cloud_base_url,
    )
    try:
        return await prepare_agentic_cases(
            plan=plan,
            corpus=load_benchmark_corpus(corpus_path),
            database_path=database_path,
            session_factory=create_session_factory(engine),
            gateway=gateway,
            target_keys=target_keys,
        )
    finally:
        await gateway.close()
        engine.dispose()


async def _approve_agentic_with_ollama(
    *,
    plan: BenchmarkPlan,
    corpus_path: Path,
    database_path: Path,
    case_ids: tuple[UUID, ...],
    target_keys: frozenset[str],
    ollama_base_url: str | None,
    direct_ollama_cloud: bool,
    ollama_cloud_base_url: str | None,
) -> tuple[AgenticBlueprintPreparation, ...]:
    engine = create_sqlite_engine(database_path)
    gateway = _ollama_campaign_gateway(
        plan,
        target_keys=target_keys,
        ollama_base_url=ollama_base_url,
        direct_ollama_cloud=direct_ollama_cloud,
        ollama_cloud_base_url=ollama_cloud_base_url,
    )
    try:
        return await approve_agentic_cases(
            plan=plan,
            corpus=load_benchmark_corpus(corpus_path),
            database_path=database_path,
            session_factory=create_session_factory(engine),
            gateway=gateway,
            case_ids=case_ids,
            target_keys=target_keys,
        )
    finally:
        await gateway.close()
        engine.dispose()


async def _run_agentic_with_ollama(
    *,
    plan: BenchmarkPlan,
    corpus_path: Path,
    database_path: Path,
    report_path: Path,
    prior_report: BenchmarkRunReport | None,
    target_keys: frozenset[str],
    ollama_base_url: str | None,
    direct_ollama_cloud: bool,
    ollama_cloud_base_url: str | None,
    retry_failed: bool,
) -> BenchmarkRunReport:
    engine = create_sqlite_engine(database_path)
    gateway = _ollama_campaign_gateway(
        plan,
        target_keys=target_keys,
        ollama_base_url=ollama_base_url,
        direct_ollama_cloud=direct_ollama_cloud,
        ollama_cloud_base_url=ollama_cloud_base_url,
    )
    try:
        return await run_agentic_cases(
            plan=plan,
            corpus=load_benchmark_corpus(corpus_path),
            database_path=database_path,
            session_factory=create_session_factory(engine),
            gateway=gateway,
            prior_report=prior_report,
            checkpoint=AtomicJsonReportCheckpoint(report_path, plan),
            target_keys=target_keys,
            retry_failed=retry_failed,
        )
    finally:
        await gateway.close()
        engine.dispose()


def _agentic_target_keys(raw_targets: list[str] | None) -> frozenset[str]:
    target_keys = frozenset(raw_targets or AGENTIC_TARGET_KEYS)
    if not target_keys or not target_keys.issubset(AGENTIC_TARGET_KEYS):
        raise ValueError("agentic targets must select Local, Cloud, or Hybrid")
    return target_keys


def _ollama_campaign_gateway(
    plan: BenchmarkPlan,
    *,
    target_keys: frozenset[str],
    ollama_base_url: str | None,
    direct_ollama_cloud: bool,
    ollama_cloud_base_url: str | None,
) -> ModelGateway:
    if ollama_cloud_base_url is not None and not direct_ollama_cloud:
        raise ValueError("--ollama-cloud-base-url requires --direct-ollama-cloud")
    model_deployments = _campaign_model_deployments(plan, target_keys)
    if not direct_ollama_cloud:
        return OllamaGateway(
            host=OllamaHost.LOCAL,
            base_url=ollama_base_url,
        )

    deployments: dict[ModelDeployment, ModelGateway] = {}
    required_deployments = set(model_deployments.values())
    if ModelDeployment.LOCAL in required_deployments:
        deployments[ModelDeployment.LOCAL] = OllamaGateway(
            host=OllamaHost.LOCAL,
            base_url=ollama_base_url,
        )
    if ModelDeployment.CLOUD in required_deployments:
        deployments[ModelDeployment.CLOUD] = OllamaGateway.from_secret_store(
            EnvironmentSecretStore(),
            host=OllamaHost.CLOUD,
            base_url=ollama_cloud_base_url,
        )
    return CampaignModelGateway(
        provider="ollama",
        deployments=deployments,
        model_deployments=model_deployments,
    )


def _campaign_model_deployments(
    plan: BenchmarkPlan,
    target_keys: frozenset[str],
) -> dict[str, ModelDeployment]:
    selections: list[ModelSelection] = []
    for case in plan.cases:
        if case.target_key not in target_keys:
            continue
        if case.baseline_model is not None:
            selections.append(case.baseline_model.to_selection())
            continue
        if case.profile is None:
            raise ValueError(f"agentic campaign case {case.case_id} has no profile")
        configuration = ModelProfileConfiguration.from_data(case.profile.configuration)
        selections.extend(
            selection for selection in configuration.models.values() if selection is not None
        )
    if not selections:
        raise ValueError("the campaign has no model selections for the requested targets")
    providers = {selection.provider for selection in selections}
    if providers != {"ollama"}:
        formatted = ", ".join(sorted(providers))
        raise ValueError(
            "the current operator runtime supports only Ollama campaign selections; "
            f"found: {formatted}"
        )
    model_deployments: dict[str, ModelDeployment] = {}
    for selection in selections:
        existing = model_deployments.get(selection.model_identifier)
        if existing is not None and existing is not selection.deployment:
            raise ValueError(
                f"model identifier {selection.model_identifier!r} is frozen as both "
                "local and cloud; direct deployment routing would be ambiguous"
            )
        model_deployments[selection.model_identifier] = selection.deployment
    return model_deployments


def _read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as source:
        return json.load(source)


def _require_matching_report(
    plan: BenchmarkPlan,
    report: BenchmarkRunReport,
) -> None:
    if report.campaign_id != plan.campaign_id or report.plan_sha256 != plan.content_sha256:
        raise ValueError("benchmark report does not match the supplied campaign plan")


def _require_distinct_paths(first: Path, second: Path) -> None:
    if first.resolve() == second.resolve():
        raise ValueError("public review packet and private answer key need distinct paths")


def _require_writable_outputs(
    paths: tuple[Path, ...],
    *,
    overwrite: bool,
) -> None:
    existing = [path for path in paths if path.exists()]
    if existing and not overwrite:
        formatted = ", ".join(str(path) for path in existing)
        raise FileExistsError(f"output already exists: {formatted}; pass --overwrite to replace it")


def _write_json_atomically(path: Path, value: Any) -> None:
    encoded = (
        json.dumps(
            value,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n"
    ).encode()
    _write_bytes_atomically(path, encoded)


def _write_bytes_atomically(path: Path, value: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid4().hex}.tmp")
    try:
        temporary.write_bytes(value)
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


if __name__ == "__main__":
    raise SystemExit(main())
