"""Prepare registered authored controls or publish fixture completion; no live transport."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from open_hollywood_api.services.assessment_authored_source import prepare, publish_fixture
from open_hollywood_engine.secrets import SecretLeakError


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("prepare", "publish-fixture"):
        command = commands.add_parser(name)
        command.add_argument("--source", required=True)
        command.add_argument("--family", required=True, choices=("F01", "F02", "F03"))
        command.add_argument("--output", type=Path, required=True)
        if name == "publish-fixture":
            command.add_argument("--submission", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        status = (
            prepare(args.source, args.family, args.output)
            if args.command == "prepare"
            else publish_fixture(args.source, args.family, args.submission, args.output)
        )
    except SecretLeakError:
        print(json.dumps({"error": "secret_guard_rejected_authored_source"}))
        return 2
    except (OSError, ValueError, TypeError, KeyError, StopIteration):
        print(json.dumps({"error": "authored_source_submission_or_destination_invalid"}))
        return 2
    print(
        json.dumps(
            {
                "status": status,
                "source_origin": "authored_diagnostic",
                "mode": args.command,
                "live_calls": 0,
                "writer_dispatch_authorized": False,
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
