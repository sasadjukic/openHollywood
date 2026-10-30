"""Export saved diagnostic probes locally. No inference or database operation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from open_hollywood_api.services.probe_review_export import collect_probe_export, write_probe_export
from open_hollywood_engine.evaluations.review_evidence import EvidenceError
from open_hollywood_engine.secrets import SecretLeakError
from pydantic import ValidationError


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--trial-id", action="append", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        export = collect_probe_export(args.archive, tuple(args.trial_id))
        status = write_probe_export(args.output, export)
    except SecretLeakError:
        print(json.dumps({"error": "secret_guard_rejected_export"}))
        return 2
    except EvidenceError as exc:
        print(json.dumps({"error": str(exc)}))
        return 2
    except (OSError, ValueError, TypeError, KeyError, ValidationError):
        print(json.dumps({"error": "probe_source_or_export_unavailable"}))
        return 2
    print(
        json.dumps(
            {
                "status": status,
                "exported": len(export.entries),
                "origin": "diagnostic_probe",
                "live_calls": 0,
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
