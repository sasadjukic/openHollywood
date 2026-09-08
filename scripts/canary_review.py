"""Read-only canary diagnostics and separately packaged cross-version human reviews."""

from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
from collections import Counter
from contextlib import closing
from pathlib import Path
from typing import Any
from uuid import UUID

from open_hollywood_engine.evaluations.canary import (
    CanaryAnswerKey,
    CanaryEvidence,
    build_canary_review,
    compare_canaries,
    summarize_canary_reviews,
)
from open_hollywood_engine.evaluations.contracts import (
    BenchmarkPlan,
    BenchmarkRunReport,
    BlindPublicBundle,
)
from open_hollywood_engine.evaluations.corpus import load_benchmark_corpus
from open_hollywood_engine.evaluations.reviews import (
    parse_review_csvs,
    render_review_csv,
    render_review_guide,
)

ROOT = Path(__file__).resolve().parents[1]
BASELINES = ROOT / "benchmarks/v0.1/canary-baselines.json"


def load_canary(
    name: str, directory: Path, *, expected_sha256: str | None = None
) -> CanaryEvidence:
    raw = (directory / "report.json").read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if expected_sha256 is not None and digest != expected_sha256:
        raise ValueError(f"{name} pinned report digest changed; preserve the original baseline")
    evidence = CanaryEvidence(
        name,
        BenchmarkPlan.model_validate_json((directory / "plan.json").read_bytes()),
        BenchmarkRunReport.model_validate_json(raw),
        digest,
    )
    evidence.validate()
    return evidence


def production_metrics(directory: Path, evidence: CanaryEvidence) -> dict[str, Any]:
    """Query production attempts, including recovered failures, without modifying SQLite."""
    path = (directory / "campaign.db").resolve(strict=True)
    with closing(sqlite3.connect(path.as_uri() + "?mode=ro", uri=True)) as connection:
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA query_only = ON")
        rows = connection.execute(
            "SELECT * FROM workflow_runs WHERE workflow_name = 'scene_production'"
        ).fetchall()
        results = {str(result.case_id): result for result in evidence.report.results}
        cases = {str(case.case_id): case for case in evidence.plan.cases}
        progress: dict[str, Any] = {}
        targets: dict[str, Any] = {}
        for row in rows:
            state = json.loads(row["input_state"])
            case_id = state.get("benchmark_case_id")
            if case_id not in results:
                continue
            if case_id in progress:
                raise ValueError("multiple production runs for one case; compare clean canaries")
            if (
                state.get("benchmark_campaign_id") != str(evidence.plan.campaign_id)
                or row["graph_version"] != evidence.plan.workflow_versions["scene_production"]
            ):
                raise ValueError("production database does not match its report/plan")
            output = results[case_id].output
            if output and UUID(row["id"]) != output.workflow_run_id:
                raise ValueError("production run does not match the report output")
            bible_count = connection.execute(
                "SELECT MAX(json_array_length(v.content, '$.accepted_scenes')) "
                "FROM artifact_versions v JOIN artifacts a ON a.id = v.artifact_id "
                "WHERE a.project_id = ? AND a.artifact_key = 'canonical_story_bible'",
                (row["project_id"],),
            ).fetchone()[0]
            blueprint = connection.execute(
                "SELECT content, content_sha256 FROM artifact_versions WHERE id = ?",
                (UUID(state["approved_blueprint_version_id"]).hex,),
            ).fetchone()
            if blueprint is None:
                raise ValueError("approved Blueprint referenced by production is missing")
            progress[case_id] = {
                "accepted_scenes": int(bible_count or 0),
                "planned_scenes": len(json.loads(blueprint["content"])["scene_plans"]),
                "approved_blueprint_sha256": blueprint["content_sha256"],
            }
            target = cases[case_id].target_key
            metrics = targets.setdefault(
                target,
                {
                    "attempts": 0,
                    "schema_valid": 0,
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "provider_latency_ms": 0,
                    "failed_attempts": 0,
                    "failure_layers": Counter(),
                    "adjudication_decisions": Counter(),
                },
            )
            for invocation in connection.execute(
                "SELECT * FROM agent_invocations WHERE workflow_run_id = ?", (row["id"],)
            ):
                settings = json.loads(invocation["request_settings"])
                metrics["attempts"] += 1
                metrics["schema_valid"] += int(invocation["schema_validation_succeeded"] == 1)
                for field in ("input_tokens", "output_tokens"):
                    metrics[field] += invocation[field]
                metrics["provider_latency_ms"] += invocation["latency_ms"] or 0
                if invocation["status"] == "FAILED":
                    metrics["failed_attempts"] += 1
                    metrics["failure_layers"][settings.get("failure_layer", "legacy_unknown")] += 1
                audit = settings.get("continuity_finding_audit", {})
                if audit.get("stage") == "adjudication":
                    for finding in audit.get("findings", []):
                        if isinstance(finding.get("decision"), str):
                            metrics["adjudication_decisions"][finding["decision"]] += 1
        if any(result.output and case_id not in progress for case_id, result in results.items()):
            raise ValueError("a completed report case has no matching production database record")
        return {
            "cases": progress,
            "cases_without_production_record": sorted(results.keys() - progress.keys()),
            "by_target": targets,
            "accepted_scenes": sum(item["accepted_scenes"] for item in progress.values()),
            "planned_scenes": sum(item["planned_scenes"] for item in progress.values()),
            "scope": (
                "Observed production runs, including recovered failures; excludes host wall time."
            ),
        }


def compare_to_baselines(candidate_directory: Path) -> dict[str, Any]:
    candidate = load_canary("candidate", candidate_directory)
    candidate_metrics = production_metrics(candidate_directory, candidate)
    registry = json.loads(BASELINES.read_text(encoding="utf-8"))
    comparisons = []
    for entry in registry["baselines"]:
        directory = ROOT / entry["directory"]
        baseline = load_canary(entry["name"], directory, expected_sha256=entry["report_sha256"])
        comparison = compare_canaries(baseline, candidate)
        metrics = production_metrics(directory, baseline)
        for case_id in metrics["cases"].keys() & candidate_metrics["cases"].keys():
            if (
                metrics["cases"][case_id]["approved_blueprint_sha256"]
                != candidate_metrics["cases"][case_id]["approved_blueprint_sha256"]
            ):
                raise ValueError("canaries did not use the same approved Blueprints")
        comparison["production_metrics"] = {baseline.name: metrics, "candidate": candidate_metrics}
        comparisons.append(comparison)
    return {"schema_version": "1", "baseline_comparisons": comparisons}


def _write_new_files(outputs: dict[Path, str], *, protected_directories: tuple[Path, ...]) -> None:
    paths = [path.resolve() for path in outputs]
    if len(set(paths)) != len(paths):
        raise ValueError("review outputs must have distinct paths")
    for path in paths:
        if path.exists():
            raise ValueError(f"refusing to overwrite existing evidence: {path}")
        if any(path.is_relative_to(directory.resolve()) for directory in protected_directories):
            raise ValueError("store new evidence outside the source canary directories")
    for path, content in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("x", encoding="utf-8", newline="") as stream:
            stream.write(content)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    compare = commands.add_parser("compare")
    compare.add_argument("--candidate", type=Path, required=True)
    package = commands.add_parser("package-review")
    package.add_argument("--left", type=Path, required=True)
    package.add_argument("--right", type=Path, required=True)
    package.add_argument("--blinding-key", type=Path, required=True)
    package.add_argument("--corpus", type=Path, default=ROOT / "benchmarks/v0.1/corpus.json")
    package.add_argument("--public-directory", type=Path, required=True)
    package.add_argument("--private-key-output", type=Path, required=True)
    package.add_argument("--reviewer-id", required=True)
    review = commands.add_parser("summarize-reviews")
    review.add_argument("--public-bundle", type=Path, required=True)
    review.add_argument("--answer-key", type=Path, required=True)
    review.add_argument("--reviews", type=Path, nargs="+", required=True)
    args = parser.parse_args()
    if args.command == "compare":
        print(json.dumps(compare_to_baselines(args.candidate), indent=2))
    elif args.command == "package-review":
        if args.private_key_output.resolve().is_relative_to(args.public_directory.resolve()):
            parser.error("private answer key must be outside the public review directory")
        if args.blinding_key.resolve().is_relative_to(args.public_directory.resolve()):
            parser.error("private blinding key must be outside the public review directory")
        public, private = build_canary_review(
            load_canary(args.left.name, args.left),
            load_canary(args.right.name, args.right),
            load_benchmark_corpus(args.corpus),
            blinding_key=args.blinding_key.read_bytes(),
        )
        _write_new_files(
            {
                args.public_directory / "public-bundle.json": public.model_dump_json(indent=2),
                args.public_directory / "review.csv": render_review_csv(
                    public, reviewer_id=args.reviewer_id
                ),
                args.public_directory / "guide.md": render_review_guide(
                    public, reviewer_id=args.reviewer_id
                ),
                args.private_key_output: private.model_dump_json(indent=2),
            },
            protected_directories=(args.left, args.right),
        )
        print(f"Packaged {len(public.comparisons)} paired completed stories; human scores pending.")
    else:
        public = BlindPublicBundle.model_validate_json(args.public_bundle.read_bytes())
        private = CanaryAnswerKey.model_validate_json(args.answer_key.read_bytes())
        reviews = parse_review_csvs(
            public, [path.read_text(encoding="utf-8-sig") for path in args.reviews]
        )
        print(json.dumps(summarize_canary_reviews(public, private, reviews), indent=2))


if __name__ == "__main__":
    main()
