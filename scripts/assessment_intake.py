"""Inspect or declare read-only ordinary-review intake; no provider calls."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from open_hollywood_api.services.assessment_intake import collect_intakes, read_plan, write_intake
from open_hollywood_engine.secrets import SecretLeakError


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="origin", required=True)
    for origin, option in (("probe", "archive"), ("saved", "database")):
        command = commands.add_parser(origin)
        command.add_argument("--" + option, type=Path, required=True)
        command.add_argument("--review-id", action="append", required=True)
        command.add_argument("--plan", type=Path)
        command.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        plan = read_plan(args.plan) if args.plan else None
        collection = collect_intakes(
            "diagnostic_probe" if args.origin == "probe" else "saved_review",
            args.archive if args.origin == "probe" else args.database,
            tuple(args.review_id),
        )
        status = write_intake(args.output, collection, plan)
    except SecretLeakError:
        print(json.dumps({"error": "secret_guard_rejected_intake"}))
        return 2
    except (OSError, ValueError, TypeError, KeyError, StopIteration):
        # Validation inputs and source prose must never appear in operator errors.
        print(json.dumps({"error": "intake_source_plan_or_destination_invalid"}))
        return 2
    print(
        json.dumps(
            {
                "status": status,
                "reviews": len(collection.entries),
                "live_calls": 0,
                "mode": "declared_intake" if plan else "inventory",
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
