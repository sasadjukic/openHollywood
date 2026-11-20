"""Freeze, verify, audit or execute the single registered critique-selected Q008 smoke."""

from __future__ import annotations

import argparse
import asyncio
import json
import re
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
    Digest,
    JsonObject,
    Record,
    require,
    strict_object,
)
from open_hollywood_engine.models.assessment_openai import (
    MAX_RESPONSE_BYTES,
    MappedResponse,
    WireEndpoint,
    check_outgoing,
    count_admitted,
    map_response,
)
from open_hollywood_engine.models.openai import _cost
from open_hollywood_engine.secrets import SecretLeakGuard, SecretValue
from pydantic import Field

from scripts import ordinary_v61_capture as ledger
from scripts.assessment_openai_authored_smoke import _secret

REPO = Path(__file__).resolve().parents[1]
ROOT = REPO / "data/diagnostics/q008-sol-high-smoke-2026-11-20"
GOLD = ROOT.parent / "ordinary-v61-single-capture-results-2026-11-20/gold.json"
GOLD_SHA = "5c22a997adb4b8a533c4e3442f4e779149fd0179dd79a20ab4aeac2580cafbb0"
MANIFEST = "0aa8d63ce59895017f07750146b267997c85e2f54777f5d0e916e18954549b93"
BODY_HASHES = (
    "9c29c18a3e2c9f3322785f25ccc61e8889898ae770e3ab78669c359870cfce1a",
    "6c05c8c449abb43de995b7f5bad490e9b30bb5c8428b3cc870c916d01dcc790e",
)
COUNT_SECONDS, GENERATION_SECONDS, WALL_SECONDS = 120, 600, 900
Origin = Literal["observed_openai_transport", "injected_transport_fixture"]
SCORING = (
    "Score only a closed, version-bound Q008 delivery. Record attempted and undispatched slots.",
    "Label passes only for supported on the whole 307-character outcome assessment.",
    "Plan coverage requires cited version-bound evidence of the assigned draw to the entrance "
    "(E0233 or equivalent).",
    "Draft coverage requires passing the shoes, movement toward the threshold and the narrated "
    "motive (E0321 or equivalent). A whole-draft citation requires a reason locating that ending.",
    "Arrival, entry or contact asserted as observed fails draft coverage. Inspect all citations "
    "for material misattribution.",
    "Record label, plan coverage and draft coverage separately as pass/fail. All three must pass "
    "for full credit. An ineligible delivery is unscored. Story quality and edit necessity "
    "are outside scope.",
)
STOPS = (
    "Approval, source, implementation, selection, request or gold drift prevents dispatch.",
    "One run claim. Each committed intent spends its slot. No resume, retry, replacement "
    "or fallback.",
    "Generate only after a positive HTTP 200 count within input, context and catalog cost limits.",
    "Stop on cancellation, timeout, transport error, non-200, invalid response, refusal, "
    "truncation, wrong model, invalid citations or missing/extra claims.",
    "Hold completion for missing input/output totals or usage above the frozen limits. "
    "Preserve known usage and leave missing values null.",
)
IMPLEMENTATION = (
    "scripts/q008_sol_smoke.py",
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
    p = wire._prepare(saved.CAPTURED_Q008.name, None)
    require(
        p.digest == MANIFEST
        and p.source.selected.role == "original_review"
        and p.wire.active_unit_ids == ("Q008",)
        and tuple(e.body_bytes_sha256 for e in p.wire.endpoints) == BODY_HASHES,
        "wrong_q008_source_or_wire",
    )
    return p


def _plan(p: wire._Plan) -> bytes:
    require(ledger.file_hash(GOLD) == GOLD_SHA, "q008_gold_drift")
    return encoded(
        {
            "contract": "saved-review-q008-sol-high-smoke-1",
            "registration": saved.CAPTURED_Q008.name,
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
    require(storage._sha(plan) == approval, "q008_approval_hash")
    p = source()
    require(plan == _plan(p), "q008_plan_or_source_drift")
    require(
        all(storage._read(root / n) == raw for n, raw in p.files.items()), "q008_frozen_wire_drift"
    )
    return p


class Terminal(Record):
    intent_sha256: Digest
    elapsed_seconds: float = Field(ge=0, allow_inf_nan=False)
    http_status: int | None = Field(ge=100, le=599)
    request_id: str | None = Field(max_length=200)
    raw_sha256: Digest | None
    body: str | None
    error: Literal["timeout", "transport_error", "capture_error", "deadline"] | None


async def _post(
    client: httpx.AsyncClient,
    request: httpx.Request,
    secret: SecretValue,
    timeout: float,
    intent: bytes,
) -> Terminal:
    started = monotonic()
    status = request_id = raw_sha = body = None
    error: Literal["timeout", "transport_error", "capture_error", "deadline"] | None = None
    guard = SecretLeakGuard((secret,))
    guard.ensure_safe(request.content.decode(), destination="Q008 request")
    request.headers["Authorization"] = "Bearer " + secret.reveal()
    try:
        async with asyncio.timeout(timeout):
            response = await client.send(request, stream=True)
            try:
                status = response.status_code
                candidate = response.headers.get("x-request-id", "")
                if re.fullmatch(r"[A-Za-z0-9_.:-]{1,200}", candidate):
                    guard.ensure_safe(candidate, destination="Q008 request id")
                    request_id = candidate
                data = bytearray()
                async for chunk in response.aiter_bytes():
                    require(len(data) + len(chunk) <= MAX_RESPONSE_BYTES, "q008_response_size")
                    data.extend(chunk)
                raw_sha = storage._sha(bytes(data))
                decoded = data.decode("utf-8")
                guard.ensure_safe(decoded, destination="Q008 terminal")
                # Check structured fields too, including escaped credential values.
                try:
                    payload = json.loads(decoded)
                except ValueError:
                    payload = None
                guard.ensure_safe(payload, destination="Q008 structured terminal")
                body = decoded
            finally:
                await response.aclose()
    except (TimeoutError, httpx.TimeoutException):
        error = "timeout"
    except httpx.HTTPError:
        error = "transport_error"
    except (ValueError, RecursionError):
        error = "capture_error"
    return Terminal(
        intent_sha256=storage._sha(intent),
        elapsed_seconds=monotonic() - started,
        http_status=status,
        request_id=request_id,
        raw_sha256=raw_sha,
        body=body,
        error=error,
    )


def _evaluate(
    p: wire._Plan,
    end: WireEndpoint,
    terminal: Terminal,
) -> tuple[str, MappedResponse | None, BoundAssessmentResult | None]:
    if terminal.error is not None:
        return terminal.error, None, None
    require(terminal.http_status is not None and terminal.body is not None, "q008_missing_response")
    assert terminal.http_status is not None and terminal.body is not None
    body = terminal.body.encode()
    require(storage._sha(body) == terminal.raw_sha256, "q008_terminal_body_drift")
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
        attempt_id="q008-" + terminal.intent_sha256,
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
        "q008_header",
    )
    return encoded(
        {
            "contract": "q008-smoke-journal-1",
            "approval_sha256": approval,
            "origin": origin,
            "journal_id": journal_id,
            "started_at": started,
        }
    )


def _stop(previous: bytes, state: str) -> bytes:
    return encoded({"kind": "stop", "state": state, "previous_sha256": storage._sha(previous)})


async def _execute(
    root: Path,
    approval: str,
    transport: httpx.AsyncBaseTransport,
    secret: SecretValue,
    origin: Origin,
) -> str:
    require(
        (storage._unlinked(root) == ROOT) == (origin == "observed_openai_transport"),
        "q008_origin_path",
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
            "q008_journal_drift",
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
    storage._destination(root, (ROOT, saved.CAPTURED_Q008.archive, GOLD.parent))
    require(type(transport) is httpx.MockTransport, "q008_mock_only")
    return await _execute(
        root, approval, transport, SecretValue("q008-local-fixture"), "injected_transport_fixture"
    )


async def run_live(approval: str, *, confirm_full_prose: bool) -> str:
    require(confirm_full_prose, "q008_both_endpoints_confirmation_required")
    verify(ROOT, approval)
    require(
        ledger.ledger_state(ROOT, approval) == "ready" and not (ROOT / "output").exists(),
        "q008_spent",
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
    require(ledger_status != "ready" or not output.exists(), "q008_unclaimed_output")
    if ledger_status == "dispatched":
        require("input_count-intent.json" in files, "q008_missing_committed_intent")
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
            "q008_slot_order",
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
            "q008_outcome_binding",
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
            "q008_incomplete_stop",
        )
        expected["stop.json"] = _stop(previous, state)
    require(files == expected, "q008_journal_chain")
    return {
        "contract": "q008-smoke-audit-1",
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
