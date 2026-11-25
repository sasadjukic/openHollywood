"""Single-use journal for the six Sol-high B visit and cut-position assessments."""

from __future__ import annotations

import argparse
import asyncio
import json
from datetime import UTC, datetime
from pathlib import Path
from time import monotonic
from uuid import uuid4

import httpx
from open_hollywood_api.services.assessment_completion import _read, _unlinked
from open_hollywood_api.services.assessment_delivery import _durable_write
from open_hollywood_api.services.saved_review_openai_fixture import _request
from open_hollywood_engine.evaluations.assessment_completion import encoded
from open_hollywood_engine.evaluations.review_evidence import require
from open_hollywood_engine.models.assessment_openai import check_outgoing
from open_hollywood_engine.secrets import SecretValue

from scripts import ordinary_v61_capture as ledger
from scripts.assessment_openai_authored_smoke import _secret
from scripts.q008_sol_smoke import Terminal, _post
from scripts.q010_uncertainty_plan import (
    COUNT_SECONDS,
    GENERATION_SECONDS,
    digest,
    filename,
    schedule,
)
from scripts.q010_uncertainty_run import Audit, closure, evidence_sheet, intent
from scripts.q011_arrival.run import evaluate

from . import plan


def origin(root: Path) -> str:
    return (
        "observed_openai_transport"
        if _unlinked(root) == plan.ROOT
        else "injected_transport_fixture"
    )


async def dispatch(
    root: Path, approval: str, transport: httpx.MockTransport | None, secret: SecretValue
) -> str:
    observed = origin(root) == "observed_openai_transport"
    require(
        (transport is None if observed else type(transport) is httpx.MockTransport),
        "transport_origin_mismatch",
    )
    cells = plan.verify(root, approval)
    ledger.ledger_state(root, approval, ("ready", "claimed"))
    out = _unlinked(root / "output")
    out.mkdir(exist_ok=False)
    previous = encoded(
        {
            "approval": approval,
            "origin": origin(root),
            "journal_id": str(uuid4()),
            "started_at": datetime.now(UTC).isoformat(),
        }
    )
    _durable_write(out / "header.json", previous)
    expected = {"header.json": previous}
    deadline = monotonic() + plan.WALL_SECONDS
    state = "deadline"
    async with httpx.AsyncClient(
        transport=httpx.AsyncHTTPTransport(retries=0, trust_env=False) if observed else transport,
        trust_env=False,
        follow_redirects=False,
        timeout=None,
    ) as client:
        for index, (cell, end) in enumerate(schedule(cells)):
            req = _request(end)
            check_outgoing(end, req)
            require(
                _read(root / "requests" / filename(cell, end)) == req.content,
                "dispatch_wire_drift",
            )
            require(
                {p.name for p in out.iterdir()} == set(expected)
                and all(_read(out / k) == v for k, v in expected.items()),
                "journal_drift",
            )
            remaining = deadline - monotonic()
            if remaining <= 0:
                state = "deadline"
                break
            name = f"{index + 1:02d}-{cell.name}-{end.stage}"
            message = intent(previous, cell, end)
            _durable_write(out / (name + "-intent.json"), message)
            expected[name + "-intent.json"] = message
            if index == 0:
                ledger.ledger_state(root, approval, ("claimed", "dispatched"))
            limit = COUNT_SECONDS if end.stage == "input_count" else GENERATION_SECONDS
            terminal = await _post(client, req, secret, min(limit, remaining), message)
            previous = encoded(terminal.model_dump(mode="json"))
            _durable_write(out / (name + "-outcome.json"), previous)
            expected[name + "-outcome.json"] = previous
            state, _ = evaluate(cell, end, terminal)
            if state not in ("count_admitted", "bound_unassessed"):
                break
    _durable_write(out / "close.json", closure(previous, state))
    return state


def audit(root: Path, approval: str) -> Audit:
    cells = plan.verify(root, approval)
    ledger_status = ledger.ledger_state(root, approval)
    out = _unlinked(root / "output")
    observed = origin(root) == "observed_openai_transport"
    found = {p.name for p in out.iterdir()} if out.exists() else set()
    require(ledger_status != "ready" or not out.exists(), "output_on_unused_ledger")
    require(ledger_status != "dispatched" or "header.json" in found, "lost_dispatch_evidence")
    used: set[str] = set()
    previous = b""
    if "header.json" in found:
        previous = _read(out / "header.json")
        header = json.loads(previous)
        require(
            header["approval"] == approval
            and header["origin"] == origin(root)
            and ledger_status != "ready",
            "journal_header",
        )
        used.add("header.json")
    rows = []
    stopped = False
    last = "unused" if ledger_status == "ready" else "interrupted"
    for i, (cell, end) in enumerate(schedule(cells), 1):
        prefix = f"{i:02d}-{cell.name}-{end.stage}"
        a, b = prefix + "-intent.json", prefix + "-outcome.json"
        row: dict[str, object] = {
            "cell": cell.name,
            "stage": end.stage,
            "state": "not_attempted",
            "eligible": False,
        }
        if a in found:
            require(
                bool(previous) and not stopped and ledger_status != "ready", "unexpected_dispatch"
            )
            message = _read(out / a)
            require(message == intent(previous, cell, end), "intent_chain")
            used.add(a)
            if b in found:
                require(ledger_status == "dispatched", "terminal_without_dispatch")
                previous = _read(out / b)
                terminal = Terminal.model_validate_json(previous)
                require(terminal.intent_sha256 == digest(message), "outcome_chain")
                last, details = evaluate(cell, end, terminal)
                row.update(details, state=last)
                used.add(b)
                stopped = last not in ("bound_unassessed", "count_admitted")
            else:
                stopped = True
                last = "intent_without_terminal"
                row.update(state=last, usage=None)
        else:
            stopped = True
        rows.append(row)
    closed = "close.json" in found
    if closed:
        close = _read(out / "close.json")
        if (
            json.loads(close)["state"] == "deadline"
            and any(r["state"] == "not_attempted" for r in rows)
            and last in ("interrupted", "count_admitted", "bound_unassessed")
        ):
            last = "deadline"
        require(
            last != "intent_without_terminal" and close == closure(previous, last), "closure_chain"
        )
        require(
            stopped
            and last not in ("bound_unassessed", "count_admitted")
            or all(r["state"] in ("bound_unassessed", "count_admitted") for r in rows),
            "early_closure",
        )
        used.add("close.json")
    require(found == used, "unexpected_journal_member")
    for row in rows:
        row["eligible"] = closed and observed and row["state"] == "bound_unassessed"
    return {
        "approval": approval,
        "origin": origin(root),
        "ledger": ledger_status,
        "closed": closed,
        "state": last,
        "slots": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("freeze")
    for mode in ("verify", "audit", "evidence-sheet", "run"):
        cmd = commands.add_parser(mode)
        cmd.add_argument("--approved-plan-sha256", required=True)
        if mode == "run":
            cmd.add_argument(
                "--confirm-full-prose-openai-both-endpoints", action="store_true", required=True
            )
    args = parser.parse_args()
    if args.command == "freeze":
        print(plan.issue(plan.ROOT))
    elif args.command == "run":
        plan.verify(plan.ROOT, args.approved_plan_sha256)
        require(
            ledger.ledger_state(plan.ROOT, args.approved_plan_sha256) == "ready"
            and not (plan.ROOT / "output").exists(),
            "already_used",
        )
        secret = _secret()
        print(asyncio.run(dispatch(plan.ROOT, args.approved_plan_sha256, None, secret)))
    else:
        report = audit(plan.ROOT, args.approved_plan_sha256)
        if args.command == "evidence-sheet":
            print(json.dumps(evidence_sheet(report), indent=2))
        elif args.command == "verify":
            print(json.dumps({k: v for k, v in report.items() if k != "slots"}, indent=2))
        else:
            print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
