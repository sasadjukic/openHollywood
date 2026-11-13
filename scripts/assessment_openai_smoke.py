"""Verify/audit a frozen four-work plan; live execution requires its explicit approval hash."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
from pathlib import Path

from open_hollywood_api.services import assessment_completion as storage
from open_hollywood_api.services import assessment_delivery as io
from open_hollywood_api.services import assessment_openai_smoke as service
from open_hollywood_engine.secrets import SecretValue


def _secret() -> SecretValue:
    value = os.environ.get("OPENAI_OH_KEY")
    if not value and os.name == "nt":
        import winreg

        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as key:
            candidate, _ = winreg.QueryValueEx(key, "OPENAI_OH_KEY")
        if isinstance(candidate, str):
            value = candidate
    if not value:
        raise ValueError("application_key_missing")
    return SecretValue(value)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="mode", required=True)
    for name in ("verify", "audit", "run"):
        command = commands.add_parser(name)
        command.add_argument("--plan", type=Path, required=True)
        if name != "verify":
            command.add_argument("--journal", type=Path, required=True)
        if name == "audit":
            command.add_argument("--output", type=Path, required=True)
        if name == "run":
            command.add_argument("--approved-plan-sha256", required=True)
            command.add_argument(
                "--confirm-full-prose-openai-both-endpoints", action="store_true", required=True
            )
    args = parser.parse_args(argv)
    try:
        if args.mode == "verify":
            plan = service.load_plan(args.plan)
            for work in plan.works:
                service._work(work)
            status = "verified_zero_calls"
        elif args.mode == "audit":
            status = service.audit(args.plan, args.journal, args.output)
        else:
            # Check consent and fixed journal before resolving the in-memory application key.
            plan = service.load_plan(args.plan)
            if io._sha(storage._read(args.plan)) != args.approved_plan_sha256:
                raise ValueError("approval_hash")
            if storage._unlinked(args.journal) != Path(plan.live_journal):
                raise ValueError("fixed_journal")
            if args.journal.exists():
                raise ValueError("no_retry")
            status = asyncio.run(
                service.run_live(args.plan, args.journal, args.approved_plan_sha256, _secret())
            )
        print(
            json.dumps({"status": status, "mode": args.mode, "writer_dispatch_authorized": False})
        )
        return 0
    except KeyboardInterrupt:
        print(json.dumps({"status": "interrupted_no_retry_audit_journal"}))
        return 130
    except (OSError, ValueError, TypeError, KeyError):
        print(json.dumps({"error": "smoke_source_plan_transport_or_destination_invalid"}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
