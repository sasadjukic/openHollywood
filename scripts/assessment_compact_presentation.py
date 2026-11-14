"""Prepare or verify version-two diagnostic inputs; no provider or live command."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from open_hollywood_api.services.assessment_compact_presentation import prepare, verify


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("prepare", "verify"))
    parser.add_argument("--intake", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        status = (prepare if args.command == "prepare" else verify)(args.intake, args.output)
    except (ValueError, TypeError, KeyError, OSError):
        print(json.dumps({"error": "compact_source_presentation_or_destination_invalid"}))
        return 2
    print(
        json.dumps(
            {
                "status": status,
                "mode": args.command,
                "live_calls": 0,
                "model_evidence": False,
                "writer_dispatch_authorized": False,
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
