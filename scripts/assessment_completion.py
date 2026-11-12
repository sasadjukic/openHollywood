"""Prepare or publish authored fixture completions; no model calls or writer dispatch."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from open_hollywood_api.services.assessment_completion import prepare_inputs, publish_completion
from open_hollywood_engine.secrets import SecretLeakError


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("prepare", "publish"):
        command = commands.add_parser(name)
        command.add_argument("--intake", type=Path, required=True)
        command.add_argument("--output", type=Path, required=True)
        if name == "publish":
            command.add_argument("--submission", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        status = (
            prepare_inputs(args.intake, args.output)
            if args.command == "prepare"
            else publish_completion(args.intake, args.submission, args.output)
        )
    except SecretLeakError:
        print(json.dumps({"error": "secret_guard_rejected_completion"}))
        return 2
    except (OSError, ValueError, TypeError, KeyError, StopIteration):
        print(json.dumps({"error": "completion_source_submission_or_destination_invalid"}))
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
