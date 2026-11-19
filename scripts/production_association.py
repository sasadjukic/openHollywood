"""Export the fixed historical review association archive locally; no database or live calls."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from open_hollywood_api.services.production_association_export import (
    REGISTERED,
    export_associations,
)
from open_hollywood_engine.secrets import SecretLeakError


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, choices=[r.name for r in REGISTERED])
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        status = export_associations(args.source, args.output)
    except SecretLeakError:
        print(json.dumps({"error": "secret_guard_rejected_association_export"}))
        return 2
    except (OSError, ValueError, TypeError, KeyError, StopIteration):
        print(json.dumps({"error": "association_source_or_destination_invalid"}))
        return 2
    print(
        json.dumps(
            {
                "status": status,
                "identity_basis": "registered_audit_snapshot",
                "assessment_attachment_eligible": False,
                "live_calls": 0,
                "writer_dispatch_authorized": False,
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
