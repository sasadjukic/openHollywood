"""Prepare fixture manifests, capture injected fixtures or audit terminals; no live inference."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from open_hollywood_api.services.assessment_delivery import (
    FixtureInterrupted,
    audit_terminal,
    capture_fixtures,
    prepare_requests,
)
from open_hollywood_engine.secrets import SecretLeakError


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("prepare", "capture-fixture", "audit"):
        command = commands.add_parser(name)
        command.add_argument("--intake", type=Path, required=True)
        command.add_argument("--output", type=Path, required=True)
        if name == "prepare":
            command.add_argument("--run-id", required=True)
            command.add_argument("--without-count", action="store_true")
        else:
            command.add_argument("--preparation", type=Path, required=True)
            command.add_argument(
                "--fixtures" if name == "capture-fixture" else "--journal", type=Path, required=True
            )
    args = parser.parse_args(argv)
    status: str
    try:
        if args.command == "prepare":
            status = prepare_requests(
                args.intake, args.output, run_id=args.run_id, with_count=not args.without_count
            )
        elif args.command == "capture-fixture":
            status = capture_fixtures(args.intake, args.preparation, args.fixtures, args.output)
        else:
            status = audit_terminal(args.intake, args.preparation, args.journal, args.output)
    except (FixtureInterrupted, KeyboardInterrupt):
        print(json.dumps({"status": "interrupted_no_retry", "live_calls": 0}))
        return 130
    except SecretLeakError:
        print(json.dumps({"error": "secret_guard_rejected_delivery_fixture"}))
        return 2
    except (OSError, ValueError, TypeError, KeyError, StopIteration):
        print(json.dumps({"error": "delivery_source_fixture_journal_or_destination_invalid"}))
        return 2
    print(
        json.dumps(
            {
                "status": status,
                "mode": args.command,
                "origin": "authored_fixture",
                "live_calls": 0,
                "writer_dispatch_authorized": False,
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
