"""Capture and inspect injected OpenAI exchanges for the registered saved-review fixture."""

import argparse
import json
import sqlite3
from pathlib import Path

from open_hollywood_api.services import assessment_completion as storage
from open_hollywood_api.services import saved_review_completion as saved
from open_hollywood_api.services import saved_review_openai_fixture as fixture
from open_hollywood_api.services.production_association_records import ArtifactSelection
from open_hollywood_engine.evaluations.assessment_completion import encoded
from open_hollywood_engine.evaluations.review_evidence import strict_object
from open_hollywood_engine.secrets import SecretLeakError


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="mode", required=True)
    for mode in ("capture", "audit", "publish"):
        cmd = commands.add_parser(mode)
        cmd.add_argument("--source", default=saved.REGISTERED.name)
        cmd.add_argument(
            "--selection", type=Path, help="Exact review or reviewed-draft selection JSON"
        )
        cmd.add_argument(
            "--scenario", required=True, choices=("complete", "missing-terminal", "count-rejected")
        )
        cmd.add_argument("--journal", type=Path, required=True)
        if mode != "capture":
            cmd.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        selection = None
        if args.selection:
            selection = ArtifactSelection.model_validate_json(
                encoded(strict_object(storage._read(args.selection, 8192).decode()))
            )
        if args.mode == "capture":
            fixture.capture(args.source, selection, args.journal, args.scenario)
            status = "captured"
        else:
            status = fixture.export(
                args.source,
                selection,
                args.journal,
                args.scenario,
                args.output,
                publish=args.mode == "publish",
            )
    except (OSError, KeyError, ValueError, sqlite3.Error, SecretLeakError):
        print(json.dumps({"error": "saved_review_openai_fixture_refused"}))
        return 2
    print(
        json.dumps(
            {"status": status, "mode": args.mode, "origin": "injected_fixture", "live_calls": 0}
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
