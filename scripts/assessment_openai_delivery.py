"""Prepare intake-bound OpenAI wires, capture fixtures, or audit; no live transport option."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from open_hollywood_api.services import assessment_completion as storage
from open_hollywood_api.services.assessment_delivery import FixtureInterrupted
from open_hollywood_api.services.assessment_openai_delivery import (
    audit_terminal,
    capture_fixtures,
    prepare_requests,
)
from open_hollywood_engine.evaluations.assessment_completion import encoded
from open_hollywood_engine.evaluations.review_evidence import strict_object
from open_hollywood_engine.models.assessment_openai_manifest import Settings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("prepare", "capture-fixture", "audit"):
        command = commands.add_parser(name)
        command.add_argument("--intake", type=Path, required=True)
        command.add_argument("--output", type=Path, required=True)
        if name == "prepare":
            command.add_argument("--settings", type=Path, required=True)
            command.add_argument("--run-id", required=True)
        else:
            command.add_argument("--preparation", type=Path, required=True)
            command.add_argument(
                "--fixtures" if name == "capture-fixture" else "--journal", type=Path, required=True
            )
    args = parser.parse_args(argv)
    status: str
    try:
        if args.command == "prepare":
            storage._destination(args.output, (args.settings,))
            settings = Settings.model_validate_json(
                encoded(strict_object(storage._read(args.settings, 1024 * 1024).decode()))
            )
            status = prepare_requests(
                args.intake, args.output, run_id=args.run_id, settings=settings
            )
        elif args.command == "capture-fixture":
            status = capture_fixtures(args.intake, args.preparation, args.fixtures, args.output)
        else:
            status = audit_terminal(args.intake, args.preparation, args.journal, args.output)
    except (FixtureInterrupted, KeyboardInterrupt):
        print(json.dumps({"status": "interrupted_no_retry", "live_calls": 0}))
        return 130
    except (OSError, ValueError, TypeError, KeyError, StopIteration):
        print(
            json.dumps({"error": "openai_rehearsal_source_settings_journal_or_destination_invalid"})
        )
        return 2
    print(
        json.dumps(
            {
                "status": status,
                "mode": args.command,
                "origin": "injected_fixture",
                "live_calls": 0,
                "model_evidence": False,
                "writer_dispatch_authorized": False,
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
