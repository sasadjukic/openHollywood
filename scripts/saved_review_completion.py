"""Prepare, audit or publish an authored completion for a registered saved review."""

import argparse
import json
import sqlite3
from pathlib import Path

from open_hollywood_api.services import assessment_completion as storage
from open_hollywood_api.services.production_association_records import ArtifactSelection
from open_hollywood_api.services.saved_review_completion import export_saved_review
from open_hollywood_engine.evaluations.assessment_completion import encoded
from open_hollywood_engine.evaluations.review_evidence import strict_object
from open_hollywood_engine.secrets import SecretLeakError


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="mode", required=True)
    for mode in ("prepare", "audit", "publish"):
        command = commands.add_parser(mode)
        command.add_argument("--source", required=True)
        command.add_argument("--output", type=Path, required=True)
        command.add_argument("--selection", type=Path, help="Exact artifact selection JSON")
        if mode != "prepare":
            command.add_argument(
                "--journal", choices=("complete", "absent", "intent-only"), required=True
            )
    args = parser.parse_args(argv)
    try:
        selected = None
        if args.selection:
            value = strict_object(storage._read(args.selection, 8192).decode())
            selected = ArtifactSelection.model_validate_json(encoded(value))
        status = export_saved_review(
            args.mode,
            args.source,
            args.output,
            selection=selected,
            journal=getattr(args, "journal", None),
        )
    except (SecretLeakError, OSError, ValueError, KeyError, sqlite3.Error):
        print(json.dumps({"error": "saved_review_source_delivery_or_output_refused"}))
        return 2
    print(
        json.dumps(
            {"status": status, "mode": args.mode, "origin": "authored_fixture", "live_calls": 0}
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
