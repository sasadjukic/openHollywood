"""Read-only review inventory/export. This command has no inference mode."""

from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path
from uuid import UUID

from open_hollywood_api.services.review_evidence_export import (
    collect_export,
    inventory,
    write_export,
)
from open_hollywood_engine.evaluations.review_evidence import EvidenceError
from open_hollywood_engine.secrets import SecretLeakError
from pydantic import ValidationError


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subcommands = parser.add_subparsers(dest="command", required=True)
    inspect = subcommands.add_parser("inventory", help="Contract metadata only; no prose export")
    inspect.add_argument("--database", type=Path, required=True)
    export = subcommands.add_parser("export", help="Up to twelve exact saved invocation IDs")
    export.add_argument("--database", type=Path, required=True)
    export.add_argument("--invocation-id", action="append", type=UUID, required=True)
    export.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "inventory":
            print(inventory(args.database).model_dump_json(indent=2))
        else:
            result = collect_export(args.database, tuple(args.invocation_id))
            disposition = write_export(args.output, result)
            print(
                json.dumps(
                    {
                        "status": disposition,
                        "selected": len(result.entries),
                        "compatible": sum(e.reason == "compatible" for e in result.entries),
                        "live_calls": 0,
                    }
                )
            )
    except SecretLeakError:
        print(json.dumps({"error": "secret_guard_rejected_export"}))
        return 2
    except EvidenceError as exc:
        print(json.dumps({"error": str(exc)}))
        return 2
    except (OSError, sqlite3.Error, ValidationError, ValueError, TypeError):
        # Never echo database text, Pydantic inputs, credentials or unpublished prose on errors.
        print(json.dumps({"error": "source_or_export_unavailable"}))
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
