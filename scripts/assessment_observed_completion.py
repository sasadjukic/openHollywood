"""Publish the registered observed assessment completions locally; no live calls."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from open_hollywood_api.services.assessment_observed_completion import publish_observed
from open_hollywood_engine.secrets import SecretLeakError


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        status = publish_observed(args.source, args.output)
    except SecretLeakError:
        print(json.dumps({"error": "secret_guard_rejected_observed_completion"}))
        return 2
    except (OSError, ValueError, TypeError, KeyError, StopIteration):
        print(json.dumps({"error": "observed_completion_source_or_destination_invalid"}))
        return 2
    print(
        json.dumps(
            {
                "status": status,
                "origin": "observed_openai_transport",
                "live_calls": 0,
                "writer_dispatch_authorized": False,
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
