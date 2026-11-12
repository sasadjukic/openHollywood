"""Export up to twelve registered native B assessments locally, without inference."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from open_hollywood_api.services.assessment_archive_export import (
    collect_assessment_export,
    write_assessment_export,
)
from open_hollywood_engine.secrets import SecretLeakError


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--trial-id", action="append", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        export = collect_assessment_export(args.archive, tuple(args.trial_id))
        status = write_assessment_export(args.output, export)
    except SecretLeakError:
        print(json.dumps({"error": "secret_guard_rejected_export"}))
        return 2
    except (OSError, ValueError, TypeError, KeyError):
        # Native validation errors can contain source text; never print exception details.
        print(json.dumps({"error": "assessment_source_or_export_unavailable"}))
        return 2
    print(
        json.dumps(
            {
                "status": status,
                "exported": len(export.entries),
                "origin": export.origin,
                "live_calls": 0,
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
