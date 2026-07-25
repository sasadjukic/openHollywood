"""Validate the frozen corpus and create exact Step 19 campaign plans."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from uuid import UUID, uuid4

from open_hollywood_api.persistence.database import (
    create_session_factory,
    create_sqlite_engine,
)
from open_hollywood_api.services.model_profiles import ModelProfileStore
from open_hollywood_engine.evaluations import (
    BenchmarkPlan,
    BenchmarkProfileSnapshot,
    build_benchmark_plan,
    load_benchmark_corpus,
)
from open_hollywood_engine.models import ModelProfileMode
from open_hollywood_engine.workflows import (
    SCENE_PRODUCTION_GRAPH_VERSION,
    STORY_BLUEPRINT_GRAPH_VERSION,
)

WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CORPUS_PATH = WORKSPACE_ROOT / "benchmarks" / "v0.1" / "corpus.json"
DEFAULT_DATABASE_PATH = WORKSPACE_ROOT / "data" / "open_hollywood.db"


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
    return parser


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

    output: Path = args.output
    if output.exists() and not args.overwrite:
        raise FileExistsError(
            f"campaign plan already exists: {output}; pass --overwrite to replace it"
        )
    plan = create_plan_from_database(
        campaign_id=args.campaign_id or uuid4(),
        corpus_path=args.corpus,
        database_path=args.database,
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(
            plan.model_dump(mode="json"),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
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


if __name__ == "__main__":
    raise SystemExit(main())
