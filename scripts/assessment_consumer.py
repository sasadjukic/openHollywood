"""Export one fixed diagnostic registration locally; no transport, credentials or writer calls."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from open_hollywood_api.services.assessment_consumer import REGISTERED, export_consumer
from open_hollywood_engine.secrets import SecretLeakError


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, choices=[r.name for r in REGISTERED])
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        status = export_consumer(args.source, args.output)
    except SecretLeakError:
        print(json.dumps({"error": "secret_guard_rejected_consumer_export"}))
        return 2
    except (OSError, ValueError, TypeError, KeyError, StopIteration):
        print(json.dumps({"error": "consumer_source_or_destination_invalid"}))
        return 2
    print(
        json.dumps(
            {
                "status": status,
                "state": "observed_bound_unassessed",
                "live_calls": 0,
                "writer_dispatch_authorized": False,
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
