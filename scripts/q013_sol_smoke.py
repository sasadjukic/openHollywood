"""Freeze, verify, audit or execute the single registered critique-selected Q013 smoke."""

from __future__ import annotations

import argparse
import asyncio
import json
import sqlite3
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from time import monotonic
from typing import Literal
from uuid import UUID, uuid4

import httpx
from open_hollywood_api.services import assessment_completion as storage
from open_hollywood_api.services import assessment_delivery as io
from open_hollywood_api.services import saved_review_completion as saved
from open_hollywood_api.services import saved_review_openai_fixture as wire
from open_hollywood_engine.evaluations.assessment_completion import encoded
from open_hollywood_engine.evaluations.assessment_result import (
    BoundAssessmentResult,
    bind_assessment_result,
    scope_for_batch,
)
from open_hollywood_engine.evaluations.assessment_work import AssessmentReceipt
from open_hollywood_engine.evaluations.review_evidence import (
    JsonObject,
    require,
    strict_object,
)
from open_hollywood_engine.models.assessment_openai import (
    MappedResponse,
    WireEndpoint,
    check_outgoing,
    count_admitted,
    map_response,
)
from open_hollywood_engine.models.openai import _cost
from open_hollywood_engine.secrets import SecretValue

from scripts import ordinary_v61_capture as ledger
from scripts import q013_assessment as case
from scripts.assessment_openai_authored_smoke import _secret
from scripts.q008_sol_smoke import (
    COUNT_SECONDS,
    GENERATION_SECONDS,
    STOPS,
    WALL_SECONDS,
    Terminal,
    _post,
    _stop,
)

REPO = Path(__file__).resolve().parents[1]
ROOT = REPO / "data/diagnostics/q013-sol-high-smoke-2026-11-21"
GOLD = ROOT.parent / "second-family-v61-results-2026-11-21/gold.json"
GOLD_SHA = "0e9747397ead04c270566f6e27173a859a5eb50338ab235ced2758d3dc9b40d0"
MANIFEST = "59ad7cd95b4d22e3541e3d7f190d30c37ea8132b02e4e6c76a7d5dec5fce170f"
BODY_HASHES = (
    "a7ed9399c181e48833013be88ac02e1880ef50e47aede640c1b5b645119541a6",
    "527d4d168af04fb7d7ec1d21d0f3ee66221fdc168ba0d829bdc25e41cb6b7778",
)
Origin = Literal["observed_openai_transport", "injected_transport_fixture"]
SCORING = {
    "eligibility": "Score only a closed, observed, complete Q013 delivery bound to this request "
    "and both versions, with known usage inside budget. Otherwise both scores are unscored.",
    "claim": "Pass if and only if the support label is supported for the whole 185-character "
    "turning-point explanation. Record the actual label and score independently of evidence.",
    "evidence": "Pass when the cited exact draft evidence establishes the inscription on the "
    "card (October 14, 2034), the scene's present (October 14, 2024), Elara noticing the numbers, "
    "and the ten-year relation. Record each obligation and its location, independent of label. "
    "The witnesses E0282, E0284, E0286, E0288 and E0290 or equivalent passages qualify. "
    "For E0920, the reason must locate the relevant passage precisely. A plan-only citation "
    "(E0237), an unlocated whole draft, missing coverage or material misattribution "
    "fails evidence.",
    "reporting": "Record claim and evidence separately as pass or fail. Full credit requires "
    "both passes. Preserve each returned citation and reason, both slot dispositions, latency "
    "and known usage. One guided factual claim does not measure story quality.",
}
IMPLEMENTATION = (
    "scripts/q013_sol_smoke.py",
    "scripts/q008_sol_smoke.py",
    "scripts/q013_assessment.py",
    "scripts/ordinary_v61_capture.py",
    "scripts/assessment_openai_authored_smoke.py",
    "apps/api/open_hollywood_api/services/saved_review_completion.py",
    "apps/api/open_hollywood_api/services/saved_review_openai_fixture.py",
    "apps/api/open_hollywood_api/services/assessment_delivery.py",
    "apps/api/open_hollywood_api/services/assessment_completion.py",
    "engine/open_hollywood_engine/evaluations/assessment_result.py",
    "engine/open_hollywood_engine/models/assessment_openai.py",
    "engine/open_hollywood_engine/models/openai.py",
)


def source() -> wire._Plan:
    manifest = saved._CaptureManifest.model_validate_json(
        case._open().read("source-fixture/source-manifest.json")
    )
    review, draft = manifest.selection
    require(
        review.version_id == "ca5915a5-5b82-4bad-82ce-e5c31a519dc0"
        and draft.version_id == "c3689bce-e108-4761-bafe-390f6e7ea1b3",
        "q013_version_pair",
    )
    p = case.prepare(review)
    require(
        p.digest == MANIFEST
        and p.source.selected.role == "original_review"
        and p.wire.active_unit_ids == ("Q013",)
        and tuple(e.body_bytes_sha256 for e in p.wire.endpoints) == BODY_HASHES,
        "wrong_q013_source_or_wire",
    )
    return p


def _plan(p: wire._Plan) -> bytes:
    require(ledger.file_hash(GOLD) == GOLD_SHA, "q013_gold_drift")
    return encoded(
        {
            "contract": "saved-review-q013-sol-high-smoke-1",
            "registration": case.REGISTRATION.name,
            "source_origin": "isolated_provider_capture",
            "selected": p.source.selected.model_dump(mode="json"),
            "reviewed_draft": p.source.pin.draft.model_dump(mode="json"),
            "active_units": p.wire.active_unit_ids,
            "model": p.wire.model_spec.model_identifier,
            "reasoning": "high",
            "count_limit": 1,
            "generation_limit": 1,
            "retries": 0,
            "max_input_tokens": p.wire.max_input_tokens,
            "max_output_tokens": p.wire.max_output_tokens,
            "max_cost_usd": p.wire.max_cost_usd,
            "count_seconds": COUNT_SECONDS,
            "generation_seconds": GENERATION_SECONDS,
            "wall_seconds": WALL_SECONDS,
            "live_journal": (ROOT / "dispatch.sqlite3").relative_to(REPO).as_posix(),
            "live_receipts": (ROOT / "output").relative_to(REPO).as_posix(),
            "endpoints": [
                e.model_dump(mode="json", exclude={"body_utf8"}) for e in p.wire.endpoints
            ],
            "files_sha256": {k: storage._sha(v) for k, v in p.files.items()},
            "gold_sha256": GOLD_SHA,
            "gold_in_model_input": False,
            "scoring": SCORING,
            "stops": STOPS,
            "implementation": {path: ledger.file_hash(REPO / path) for path in IMPLEMENTATION},
            "full_prose_context_at_both_endpoints": True,
            "writer_dispatch_authorized": False,
        }
    )


def freeze() -> str:
    p = source()
    raw = _plan(p)
    approval = storage._sha(raw)
    storage._unlinked(ROOT).mkdir(exist_ok=False)
    for name, body in (p.files | {"plan.json": raw}).items():
        io._durable_write(ROOT / name, body)
    ledger.initialize_ledger(ROOT, approval)
    return approval


def verify(root: Path, approval: str) -> wire._Plan:
    plan = storage._read(root / "plan.json")
    require(storage._sha(plan) == approval, "q013_approval_hash")
    p = source()
    require(plan == _plan(p), "q013_plan_or_source_drift")
    require(
        all(storage._read(root / n) == raw for n, raw in p.files.items()), "q013_frozen_wire_drift"
    )
    return p


def _evaluate(
    p: wire._Plan,
    end: WireEndpoint,
    terminal: Terminal,
) -> tuple[str, MappedResponse | None, BoundAssessmentResult | None]:
    if terminal.error is not None:
        return terminal.error, None, None
    require(terminal.http_status is not None and terminal.body is not None, "q013_missing_response")
    assert terminal.http_status is not None and terminal.body is not None
    body = terminal.body.encode()
    require(storage._sha(body) == terminal.raw_sha256, "q013_terminal_body_drift")
    mapped = map_response(end.stage, terminal.http_status, body, p.wire.model_spec)
    if terminal.http_status != 200 or mapped.issues or mapped.error_codes:
        return "http_error" if terminal.http_status != 200 else "invalid_response", mapped, None
    if end.stage == "input_count":
        admitted = bool(mapped.counted_input_tokens) and count_admitted(p.wire, mapped)
        return ("count_admitted" if admitted else "count_rejected"), mapped, None
    if mapped.state != "complete" or mapped.raw_final is None:
        return mapped.state, mapped, None
    u = mapped.usage
    if (
        u.input_tokens is None
        or u.output_tokens is None
        or (
            u.input_tokens > p.wire.max_input_tokens
            or u.output_tokens > p.wire.max_output_tokens
            or _cost(p.wire.model_spec, u.input_tokens, u.output_tokens)
            > Decimal(p.wire.max_cost_usd)
        )
    ):
        return "accounting_hold", mapped, None
    scope = scope_for_batch(p.work, p.wire.batch_id, p.digest)
    receipt = AssessmentReceipt(
        work_sha256=scope.work_sha256,
        batch_id=scope.batch_id,
        request_sha256=p.digest,
        attempt_id="q013-" + terminal.intent_sha256,
        status="valid",
        result_sha256=mapped.raw_final_utf8_sha256,
        assessed_unit_ids=scope.active_unit_ids,
        input_tokens=u.input_tokens,
        output_tokens=u.output_tokens,
        reasoning_tokens=u.reasoning_tokens,
        active_seconds=terminal.elapsed_seconds,
    )
    try:
        bound = bind_assessment_result(p.work, scope, receipt, mapped.raw_final)
    except ValueError:
        return "invalid_claim_or_citation", mapped, None
    return "bound_unassessed", mapped, bound


def _header(approval: str, origin: Origin, journal_id: str, started: str) -> bytes:
    require(
        UUID(journal_id).version == 4 and datetime.fromisoformat(started).tzinfo is not None,
        "q013_header",
    )
    return encoded(
        {
            "contract": "q013-smoke-journal-1",
            "approval_sha256": approval,
            "origin": origin,
            "journal_id": journal_id,
            "started_at": started,
        }
    )


async def _execute(
    root: Path,
    approval: str,
    transport: httpx.AsyncBaseTransport,
    secret: SecretValue,
    origin: Origin,
) -> str:
    require(
        (storage._unlinked(root) == ROOT) == (origin == "observed_openai_transport"),
        "q013_origin_path",
    )
    p = verify(root, approval)
    ledger.ledger_state(root, approval, ("ready", "claimed"))
    output = storage._unlinked(root / "output")
    output.mkdir(exist_ok=False)
    previous = _header(approval, origin, str(uuid4()), datetime.now(UTC).isoformat())
    io._durable_write(output / "header.json", previous)
    expected = {"header.json": previous}

    def check_journal() -> None:
        require(
            {f.name for f in output.iterdir()} == set(expected)
            and all(storage._read(output / k) == v for k, v in expected.items()),
            "q013_journal_drift",
        )

    def append(name: str, data: bytes) -> None:
        check_journal()
        io._durable_write(output / name, data)
        expected[name] = data

    deadline = monotonic() + WALL_SECONDS
    state = "deadline"
    async with httpx.AsyncClient(
        transport=transport, trust_env=False, follow_redirects=False, timeout=None
    ) as client:
        for end in p.wire.endpoints:
            req = wire._request(end)
            check_outgoing(end, req)
            intent = wire._intent(p, end, previous)
            append(end.stage + "-intent.json", intent)
            if end.stage == "input_count":
                ledger.ledger_state(root, approval, ("claimed", "dispatched"))
            verify(root, approval)  # Rebuild the registered source after intent, before POST.
            check_journal()
            remaining = deadline - monotonic()
            if remaining <= 0:
                terminal = Terminal(
                    intent_sha256=storage._sha(intent),
                    elapsed_seconds=0,
                    http_status=None,
                    request_id=None,
                    raw_sha256=None,
                    body=None,
                    error="deadline",
                )
            else:
                limit = COUNT_SECONDS if end.stage == "input_count" else GENERATION_SECONDS
                terminal = await _post(client, req, secret, min(limit, remaining), intent)
            previous = encoded(terminal.model_dump(mode="json"))
            append(end.stage + "-outcome.json", previous)
            state, _, _ = _evaluate(p, end, terminal)
            if state != "count_admitted":
                break
    append("stop.json", _stop(previous, state))
    return state


async def qualify(root: Path, approval: str, transport: httpx.MockTransport) -> str:
    storage._destination(root, (ROOT, case.REGISTRATION.archive, GOLD.parent))
    require(type(transport) is httpx.MockTransport, "q013_mock_only")
    return await _execute(
        root, approval, transport, SecretValue("q013-local-fixture"), "injected_transport_fixture"
    )


async def run_live(approval: str, *, confirm_full_prose: bool) -> str:
    require(confirm_full_prose, "q013_both_endpoints_confirmation_required")
    verify(ROOT, approval)
    require(
        ledger.ledger_state(ROOT, approval) == "ready" and not (ROOT / "output").exists(),
        "q013_spent",
    )
    secret = _secret()
    transport = httpx.AsyncHTTPTransport(retries=0, verify=True, trust_env=False)
    return await _execute(ROOT, approval, transport, secret, "observed_openai_transport")


def audit(root: Path, approval: str) -> JsonObject:
    p = verify(root, approval)
    ledger_status = ledger.ledger_state(root, approval)
    origin: Origin = (
        "observed_openai_transport"
        if storage._unlinked(root) == ROOT
        else "injected_transport_fixture"
    )
    output = storage._unlinked(root / "output")
    files = {f.name: storage._read(f) for f in output.iterdir()} if output.exists() else {}
    expected: dict[str, bytes] = {}
    previous = b""
    if "header.json" in files:
        header = strict_object(files["header.json"].decode())
        previous = _header(approval, origin, str(header["journal_id"]), str(header["started_at"]))
        expected["header.json"] = previous
    require(ledger_status != "ready" or not output.exists(), "q013_unclaimed_output")
    if ledger_status == "dispatched":
        require("input_count-intent.json" in files, "q013_missing_committed_intent")
    slots: list[JsonObject] = []
    state = "ready" if ledger_status == "ready" else "claimed_without_dispatch"
    result = None
    for end in p.wire.endpoints:
        key = end.stage + "-intent.json"
        if key not in files:
            slots.append({"stage": end.stage, "state": "not_dispatched"})
            continue
        require(
            bool(previous)
            and state in ("claimed_without_dispatch", "count_admitted")
            and (end.stage == "input_count" or state == "count_admitted"),
            "q013_slot_order",
        )
        intent = wire._intent(p, end, previous)
        expected[key] = intent
        key = end.stage + "-outcome.json"
        if key not in files:
            slots.append({"stage": end.stage, "state": "possibly_sent", "usage": None})
            state = "possibly_sent"
            continue
        terminal = Terminal.model_validate_json(encoded(strict_object(files[key].decode())))
        require(
            ledger_status == "dispatched" and terminal.intent_sha256 == storage._sha(intent),
            "q013_outcome_binding",
        )
        previous = encoded(terminal.model_dump(mode="json"))
        expected[key] = previous
        state, mapped, bound = _evaluate(p, end, terminal)
        result = bound.model_dump(mode="json") if bound else None
        slots.append(
            {
                "stage": end.stage,
                "state": state,
                "http_status": terminal.http_status,
                "request_id": terminal.request_id,
                "elapsed_seconds": terminal.elapsed_seconds,
                "raw_sha256": terminal.raw_sha256,
                "mapped": mapped.model_dump(mode="json") if mapped else None,
            }
        )
    closed = "stop.json" in files
    if closed:
        require(
            state not in ("ready", "possibly_sent", "claimed_without_dispatch", "count_admitted"),
            "q013_incomplete_stop",
        )
        expected["stop.json"] = _stop(previous, state)
    require(files == expected, "q013_journal_chain")
    return {
        "contract": "q013-smoke-audit-1",
        "plan_sha256": approval,
        "delivery_origin": origin,
        "ledger": ledger_status,
        "slots": list(slots),
        "closed": closed,
        "state": state,
        "bound_result": result if closed else None,
        "eligible_for_scoring": closed
        and state == "bound_unassessed"
        and origin == "observed_openai_transport",
        "actual_billed_cost": None,
        "writer_dispatch_authorized": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="mode", required=True)
    for name in ("freeze", "verify", "audit", "run"):
        cmd = sub.add_parser(name)
        if name == "run":
            cmd.add_argument("--approved-plan-sha256", required=True)
            cmd.add_argument(
                "--confirm-full-prose-openai-both-endpoints", action="store_true", required=True
            )
    args = parser.parse_args(argv)
    try:
        if args.mode == "freeze":
            print(json.dumps({"plan_sha256": freeze()}))
        elif args.mode == "run":
            status = asyncio.run(
                run_live(
                    args.approved_plan_sha256,
                    confirm_full_prose=args.confirm_full_prose_openai_both_endpoints,
                )
            )
            print(json.dumps({"state": status}))
            return 0 if status == "bound_unassessed" else 1
        else:
            approval = ledger.file_hash(ROOT / "plan.json")
            report = audit(ROOT, approval)
            print(
                json.dumps(
                    report
                    if args.mode == "audit"
                    else {
                        "plan_sha256": approval,
                        "ledger": report["ledger"],
                        "state": report["state"],
                    },
                    ensure_ascii=True,
                )
            )
        return 0
    except (OSError, ValueError, sqlite3.Error, KeyError):
        print(json.dumps({"status": "refused_or_interrupted_inspect_single_use_journal"}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
