"""Explicit four-work smoke freeze, one-shot transport and read-only audit.

The existing rehearsal contracts stay fixture-only. A separate prospective plan
and application-owned journal record observations without promoting old captures.
"""

from __future__ import annotations

import asyncio
import re
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from time import perf_counter
from typing import Annotated, Literal

import httpx
from open_hollywood_engine.evaluations.assessment_completion import encoded
from open_hollywood_engine.evaluations.assessment_delivery import Stage
from open_hollywood_engine.evaluations.assessment_work import complete_work
from open_hollywood_engine.evaluations.contracts import canonical_sha256
from open_hollywood_engine.evaluations.review_evidence import Digest, JsonObject, Record, require
from open_hollywood_engine.models.assessment_openai import (
    MAX_RESPONSE_BYTES,
    check_outgoing,
    count_admitted,
    map_response,
)
from open_hollywood_engine.models.assessment_openai_manifest import (
    Exchange,
    derive_terminal,
    wire_for,
)
from open_hollywood_engine.secrets import SecretLeakGuard, SecretValue
from pydantic import Field

from open_hollywood_api.services import assessment_completion as storage
from open_hollywood_api.services import assessment_delivery as io
from open_hollywood_api.services import assessment_openai_delivery as rehearsal

WorkName = Literal["N06", "N07", "N10", "N11"]
NAMES: tuple[WorkName, ...] = ("N06", "N07", "N10", "N11")
SCORING = (
    "Four fixed whole works; six active claims. Primary: source/request integrity, "
    "count admission, terminal delivery, exact native binding and complete original-work coverage. "
    "Record all eight slots, including not dispatched, failures and unknown usage. "
    "Inspect every delivered claim for whole-claim support, citation coverage and explanation "
    "materiality against original declarations/briefs; no new automated semantic gold. "
    "Prior authored finals are fixtures, not semantic ground truth. No repair, salvage, "
    "selection changes, writer dispatch, craft score or production qualification."
)
STOPS = (
    "One fixed journal; never resume or retry. Count N06,N07,N10,N11 before any generation. "
    "Any failed/unknown/over-budget count halts all later calls. Then generate in the same order. "
    "Any delivery/binding failure, unknown usage, usage over reservation, timeout, cancellation, "
    "source/request/code drift or journal failure stops further dispatch. No input trimming, "
    "replacement work/model, recovery count or automatic budget increase."
)


class Work(Record):
    name: WorkName
    intake: str
    preparation: str
    request_set_sha256: Digest
    preparation_manifest_sha256: Digest


class Plan(Record):
    contract: Literal["assessment-openai-four-work-smoke-1"]
    works: tuple[Work, ...] = Field(min_length=4, max_length=4)
    live_journal: str
    implementation_sha256: Digest
    count_limit: Literal[4]
    generation_limit: Literal[4]
    retry_limit: Literal[0]
    max_generation_cost_usd: Literal["4.00"]
    count_timeout_seconds: Literal[120]
    generation_timeout_seconds: Literal[600]
    run_wall_seconds: Literal[3600]
    scoring: str
    stops: str
    approval_required: Literal[True]
    writer_dispatch_authorized: Literal[False]


Origin = Literal["injected_transport_fixture", "observed_openai_transport"]


class Header(Record):
    contract: Literal["assessment-openai-smoke-journal-1"]
    origin: Origin
    plan_bytes_sha256: Digest
    implementation_sha256: Digest
    started_at_utc: str


class Intent(Record):
    kind: Literal["intent"]
    work: str
    stage: Stage
    request_payload_sha256: Digest
    endpoint_sha256: Digest
    body_bytes_sha256: Digest


class Outcome(Record):
    kind: Literal["outcome"]
    intent_bytes_sha256: Digest
    exchange: Exchange
    request_id: str | None
    elapsed_seconds: float = Field(ge=0, allow_inf_nan=False)


class Stop(Record):
    kind: Literal["stop"]
    reason: Literal["complete", "halted", "deadline", "cancelled"]
    elapsed_wall_seconds: float = Field(ge=0, allow_inf_nan=False)


class Event(Record):
    contract: Literal["assessment-openai-smoke-event-1"]
    sequence: int = Field(ge=1, le=17)
    previous_bytes_sha256: Digest
    recorded_at_utc: str
    payload: Annotated[Intent | Outcome | Stop, Field(discriminator="kind")]


def implementation() -> str:
    return canonical_sha256(
        {"rehearsal": rehearsal._implementation(), "smoke": io._sha(Path(__file__).read_bytes())}
    )


def _read_model(path: Path, cls: type[Plan]) -> Plan:
    from open_hollywood_engine.evaluations.review_evidence import strict_object

    return cls.model_validate_json(encoded(strict_object(storage._read(path).decode())))


def _work(work: Work) -> rehearsal._Prepared:
    prepared = rehearsal._load(Path(work.intake), Path(work.preparation))
    require(
        prepared.request_set.payload_canonical_sha256 == work.request_set_sha256
        and io._sha(prepared.files["manifest.json"]) == work.preparation_manifest_sha256,
        "smoke_work_changed",
    )
    require(len(prepared.request_set.payload.requests) == 1, "smoke_single_batch")
    settings = prepared.request_set.payload.settings
    require(
        settings.model_spec.model_identifier == "gpt-6.1-sol"
        and settings.reasoning == "high"
        and settings.max_input_tokens == 272000
        and settings.max_output_tokens == 32000
        and Decimal(settings.max_cost_usd) == 1,
        "smoke_settings",
    )
    return prepared


def load_plan(path: Path) -> Plan:
    plan = _read_model(path, Plan)
    require(tuple(w.name for w in plan.works) == NAMES, "smoke_work_order")
    require(plan.implementation_sha256 == implementation(), "smoke_implementation_changed")
    require(plan.scoring == SCORING and plan.stops == STOPS, "smoke_contract_changed")
    return plan


def freeze(works: tuple[Work, ...], destination: Path, live_journal: Path) -> str:
    plan = Plan(
        contract="assessment-openai-four-work-smoke-1",
        works=works,
        live_journal=str(storage._unlinked(live_journal)),
        implementation_sha256=implementation(),
        count_limit=4,
        generation_limit=4,
        retry_limit=0,
        max_generation_cost_usd="4.00",
        count_timeout_seconds=120,
        generation_timeout_seconds=600,
        run_wall_seconds=3600,
        scoring=SCORING,
        stops=STOPS,
        approval_required=True,
        writer_dispatch_authorized=False,
    )
    require(tuple(w.name for w in works) == NAMES, "smoke_work_order")
    prepared = [_work(w) for w in works]
    require(
        len({p.request_set.payload.work_canonical_sha256 for p in prepared}) == 4,
        "smoke_duplicate_work",
    )
    protected = tuple(p for row in prepared for p in row.collected.protected)
    destination = storage._destination(
        destination, (*protected, *(Path(w.preparation) for w in works))
    )
    storage._destination(
        live_journal, (*protected, destination, *(Path(w.preparation) for w in works))
    )
    raw = encoded(plan.model_dump(mode="json"))
    if destination.exists():
        require(storage._read(destination) == raw, "smoke_plan_exists_changed")
        return "reused"
    destination.parent.mkdir(parents=True, exist_ok=True)
    io._durable_write(destination, raw)
    return "created"


class Journal:
    def __init__(self, path: Path, plan: Path, origin: Origin) -> None:
        self.path = path
        path.mkdir(parents=True, exist_ok=False)
        header = Header(
            contract="assessment-openai-smoke-journal-1",
            origin=origin,
            plan_bytes_sha256=io._sha(storage._read(plan)),
            implementation_sha256=implementation(),
            started_at_utc=datetime.now(UTC).isoformat(),
        )
        self.files = {
            "header.json": encoded(header.model_dump(mode="json")),
            "plan.json": storage._read(plan),
        }
        for name, raw in self.files.items():
            io._durable_write(path / name, raw)
        self.previous = io._sha(self.files["header.json"])
        self.sequence = 0

    def append(self, payload: Intent | Outcome | Stop) -> str:
        require(io._read_journal(self.path) == self.files, "smoke_journal_drift")
        event = Event(
            contract="assessment-openai-smoke-event-1",
            sequence=self.sequence + 1,
            previous_bytes_sha256=self.previous,
            recorded_at_utc=datetime.now(UTC).isoformat(),
            payload=payload,
        )
        raw = encoded(event.model_dump(mode="json"))
        io._durable_write(self.path / f"event-{event.sequence:04d}.json", raw)
        self.files[f"event-{event.sequence:04d}.json"] = raw
        self.sequence, self.previous = event.sequence, io._sha(raw)
        return self.previous


def _allowed(prepared: rehearsal._Prepared, exchanges: list[Exchange]) -> bool:
    manifest = prepared.request_set.payload.requests[0]
    if len(exchanges) == 1:
        response = exchanges[0].response
        return response is not None and count_admitted(wire_for(manifest), response)
    terminal = derive_terminal(prepared.collected.context, manifest, tuple(exchanges), 0)
    usage = terminal.usage
    return (
        terminal.state == "bound_unassessed"
        and not terminal.accounting_hold
        and usage.input_tokens is not None
        and usage.input_tokens <= 272000
        and usage.output_tokens is not None
        and usage.output_tokens <= 32000
    )


async def _exchange(
    client: httpx.AsyncClient,
    prepared: rehearsal._Prepared,
    stage: Stage,
    secret: SecretValue,
    timeout: float,
) -> tuple[Exchange, str | None]:
    manifest = prepared.request_set.payload.requests[0]
    endpoint = manifest.payload.endpoints[0 if stage == "input_count" else 1]
    request = rehearsal._build_request(endpoint)
    check_outgoing(endpoint, request)
    guard = SecretLeakGuard((secret,))
    guard.ensure_safe(endpoint.model_dump(mode="json"), destination="smoke request")
    request.headers["Authorization"] = "Bearer " + secret.reveal()
    request.extensions["timeout"] = {
        k: min(timeout, 30) if k == "connect" else timeout
        for k in ("connect", "read", "write", "pool")
    }
    exchange, request_id = rehearsal._interrupted(endpoint), None
    try:
        async with asyncio.timeout(timeout):
            response = await client.send(request, stream=True)
            exchange = exchange.model_copy(update={"observed_http_status": response.status_code})
            try:
                body = bytearray(response.content if response.is_stream_consumed else b"")
                require(len(body) <= MAX_RESPONSE_BYTES, "smoke_response_limit")
                if not response.is_stream_consumed:
                    async for chunk in response.aiter_raw():
                        require(
                            len(body) + len(chunk) <= MAX_RESPONSE_BYTES, "smoke_response_limit"
                        )
                        body.extend(chunk)
                raw = bytes(body)
                exchange = exchange.model_copy(
                    update={"observed_raw_http_bytes_sha256": io._sha(raw)}
                )
                mapped = map_response(
                    stage,
                    response.status_code,
                    raw,
                    manifest.payload.settings.model_spec,
                    guard=guard,
                )
                candidate = response.headers.get("x-request-id")
                if candidate and re.fullmatch(r"[A-Za-z0-9_.:-]{1,200}", candidate):
                    guard.ensure_safe(candidate, destination="smoke request id")
                    request_id = candidate
                exchange = exchange.model_copy(
                    update={
                        "disposition": "response",
                        "response": mapped,
                        "retained_response_canonical_sha256": canonical_sha256(
                            mapped.model_dump(mode="json")
                        ),
                    }
                )
            finally:
                await response.aclose()
    except asyncio.CancelledError:
        raise  # Durable pending intent; never auto-replay a possibly received request.
    except (TimeoutError, httpx.HTTPError):
        exchange = exchange.model_copy(
            update={"disposition": "transport_error", "local_error": "transport_error"}
        )
    except ValueError:
        exchange = exchange.model_copy(
            update={"disposition": "capture_error", "local_error": "capture_error"}
        )
    return exchange, request_id


async def _execute(
    path: Path,
    journal_path: Path,
    client: httpx.AsyncClient,
    secret: SecretValue,
    origin: Origin,
) -> str:
    plan = load_plan(path)
    prepared = [_work(w) for w in plan.works]
    protected = tuple(p for row in prepared for p in row.collected.protected)
    journal_path = storage._destination(
        journal_path, (*protected, path, *(Path(w.preparation) for w in plan.works))
    )
    require(not journal_path.exists(), "smoke_no_resume_or_retry")
    journal = Journal(journal_path, path, origin)
    started = perf_counter()
    exchanges: dict[str, list[Exchange]] = {w.name: [] for w in plan.works}
    try:
        for stage in ("input_count", "generation"):
            for work in plan.works:
                require(load_plan(path) == plan, "smoke_plan_drift")
                current = _work(work)  # Fresh source authentication before each dispatch.
                remaining = plan.run_wall_seconds - (perf_counter() - started)
                if remaining <= 0:
                    journal.append(
                        Stop(
                            kind="stop",
                            reason="deadline",
                            elapsed_wall_seconds=perf_counter() - started,
                        )
                    )
                    return "deadline"
                manifest = current.request_set.payload.requests[0]
                endpoint = manifest.payload.endpoints[0 if stage == "input_count" else 1]
                check_outgoing(endpoint, rehearsal._build_request(endpoint))
                SecretLeakGuard((secret,)).ensure_safe(
                    endpoint.body_utf8, destination="smoke input"
                )
                intent = journal.append(
                    Intent(
                        kind="intent",
                        work=work.name,
                        stage=stage,
                        request_payload_sha256=manifest.payload_canonical_sha256,
                        endpoint_sha256=canonical_sha256(endpoint.model_dump(mode="json")),
                        body_bytes_sha256=endpoint.body_bytes_sha256,
                    )
                )
                mark = perf_counter()
                timeout = min(
                    remaining,
                    plan.count_timeout_seconds
                    if stage == "input_count"
                    else plan.generation_timeout_seconds,
                )
                exchange, request_id = await _exchange(client, current, stage, secret, timeout)
                journal.append(
                    Outcome(
                        kind="outcome",
                        intent_bytes_sha256=intent,
                        exchange=exchange,
                        request_id=request_id,
                        elapsed_seconds=perf_counter() - mark,
                    )
                )
                exchanges[work.name].append(exchange)
                if not _allowed(current, exchanges[work.name]):
                    journal.append(
                        Stop(
                            kind="stop",
                            reason="halted",
                            elapsed_wall_seconds=perf_counter() - started,
                        )
                    )
                    return "halted"
        journal.append(
            Stop(kind="stop", reason="complete", elapsed_wall_seconds=perf_counter() - started)
        )
        return "complete"
    except asyncio.CancelledError:
        # No synthetic outcome or stop is written over an interrupted request.
        raise


def _client(transport: httpx.AsyncBaseTransport) -> httpx.AsyncClient:
    return httpx.AsyncClient(
        transport=transport,
        trust_env=False,
        follow_redirects=False,
        timeout=None,
        limits=httpx.Limits(max_connections=1),
    )


async def qualify(path: Path, journal: Path, transport: httpx.MockTransport) -> str:
    require(type(transport) is httpx.MockTransport, "smoke_mock_required")
    require(
        storage._unlinked(journal) != Path(load_plan(path).live_journal), "fixture_live_journal"
    )
    async with _client(transport) as client:
        return await _execute(
            path,
            journal,
            client,
            SecretValue("local-smoke-fixture-token"),
            "injected_transport_fixture",
        )


async def run_live(
    path: Path, journal: Path, approved_plan_sha256: str, secret: SecretValue
) -> str:
    require(approved_plan_sha256 == io._sha(storage._read(path)), "smoke_approval_hash_required")
    plan = load_plan(path)
    require(storage._unlinked(journal) == Path(plan.live_journal), "smoke_fixed_live_journal")
    require(not journal.exists(), "smoke_no_resume_or_retry")
    # No caller endpoint/proxy/transport override. TLS verification and zero connect retries.
    transport = httpx.AsyncHTTPTransport(retries=0, verify=True, trust_env=False)
    async with _client(transport) as client:
        return await _execute(path, journal, client, secret, "observed_openai_transport")


def audit(path: Path, journal_path: Path, destination: Path) -> str:
    from open_hollywood_engine.evaluations.review_evidence import strict_object

    plan = load_plan(path)
    prepared: dict[str, rehearsal._Prepared] = {w.name: _work(w) for w in plan.works}
    files = io._read_journal(journal_path)
    header = Header.model_validate_json(encoded(strict_object(files["header.json"].decode())))
    require(
        (header.origin == "observed_openai_transport")
        == (storage._unlinked(journal_path) == Path(plan.live_journal)),
        "smoke_origin_path",
    )
    require(
        files["plan.json"] == storage._read(path)
        and header.plan_bytes_sha256 == io._sha(files["plan.json"])
        and header.implementation_sha256 == implementation(),
        "smoke_journal_binding",
    )
    names = [f"event-{i:04d}.json" for i in range(1, len(files) - 1)]
    require(set(files) == {"header.json", "plan.json", *names}, "smoke_journal_members")
    stages: tuple[Stage, ...] = ("input_count", "generation")
    expected: list[tuple[str, Stage]] = [(w.name, stage) for stage in stages for w in plan.works]
    exchanges: dict[str, list[Exchange]] = {w.name: [] for w in plan.works}
    seconds: dict[str, float] = {w.name: 0.0 for w in plan.works}
    slots: list[JsonObject] = []
    pending: tuple[str, Stage, str] | None = None
    previous, index, stopped, halted = io._sha(files["header.json"]), 0, None, False
    for sequence, name in enumerate(names, 1):
        raw = files[name]
        event = Event.model_validate_json(encoded(strict_object(raw.decode())))
        require(
            event.sequence == sequence and event.previous_bytes_sha256 == previous,
            "smoke_journal_chain",
        )
        previous = io._sha(raw)
        require(stopped is None, "smoke_after_stop")
        p = event.payload
        if isinstance(p, Intent):
            require(not halted and pending is None and index < 8, "smoke_extra_intent")
            work, stage = expected[index]
            manifest = prepared[work].request_set.payload.requests[0]
            endpoint = manifest.payload.endpoints[0 if stage == "input_count" else 1]
            require(
                p.work == work
                and p.stage == stage
                and p.request_payload_sha256 == manifest.payload_canonical_sha256
                and p.endpoint_sha256 == canonical_sha256(endpoint.model_dump(mode="json"))
                and p.body_bytes_sha256 == endpoint.body_bytes_sha256,
                "smoke_intent_changed",
            )
            pending = work, p.stage, previous
            index += 1
        elif isinstance(p, Outcome):
            require(pending is not None, "smoke_outcome_without_intent")
            assert pending is not None
            work, stage, intent = pending
            require(
                p.intent_bytes_sha256 == intent and p.exchange.stage == stage,
                "smoke_outcome_changed",
            )
            exchanges[work].append(p.exchange)
            seconds[work] += p.elapsed_seconds
            manifest = prepared[work].request_set.payload.requests[0]
            derive_terminal(
                prepared[work].collected.context, manifest, tuple(exchanges[work]), seconds[work]
            )
            halted = not _allowed(prepared[work], exchanges[work])
            slots.append(
                {
                    "work": work,
                    "stage": stage,
                    "state": "observed_terminal",
                    "outcome": p.model_dump(mode="json"),
                }
            )
            pending = None
        else:
            require(pending is None, "smoke_stop_with_pending")
            require(
                p.reason != "deadline" or p.elapsed_wall_seconds >= plan.run_wall_seconds,
                "smoke_unsubstantiated_deadline",
            )
            require(
                (p.reason == "complete" and index == 8 and not halted)
                or (p.reason == "halted" and halted)
                or p.reason in ("deadline", "cancelled"),
                "smoke_wrong_stop",
            )
            stopped = p.reason
    if pending is not None:
        work, stage, _ = pending
        manifest = prepared[work].request_set.payload.requests[0]
        endpoint = manifest.payload.endpoints[0 if stage == "input_count" else 1]
        exchanges[work].append(rehearsal._interrupted(endpoint))
        slots.append({"work": work, "stage": stage, "state": "interrupted_unknown_usage"})
    for work, stage in expected[index:]:
        slots.append({"work": work, "stage": stage, "state": "not_dispatched"})
    works = []
    known = {
        k: 0 for k in ("input_tokens", "output_tokens", "reasoning_tokens", "cached_input_tokens")
    }
    unknown_usage = 0
    for work_ref in plan.works:
        current = prepared[work_ref.name]
        terminal = derive_terminal(
            current.collected.context,
            current.request_set.payload.requests[0],
            tuple(exchanges[work_ref.name]),
            seconds[work_ref.name],
            pending=pending is not None and pending[0] == work_ref.name,
        )
        native_work = current.collected.context.intake.pending_work
        assert native_work is not None
        manifest = current.request_set.payload.requests[0]
        completion = complete_work(
            native_work,
            (terminal.native_receipt,) if terminal.native_receipt else (),
            {manifest.payload.presentation.batch_id: manifest.payload_canonical_sha256},
        )
        if terminal.native_receipt:
            unknown_usage += int(terminal.accounting_hold)
            for key, value in terminal.usage.model_dump().items():
                if value is not None:
                    known[key] += value
        works.append(
            {
                "work": work_ref.name,
                "intake": current.collected.context.intake.model_dump(mode="json"),
                "terminal": terminal.model_dump(
                    mode="json", exclude={"contract", "origin", "model_evidence"}
                ),
                "completion": completion.model_dump(mode="json"),
                "completion_eligible": stopped is not None
                and completion.complete_delivery
                and completion.binding == "complete",
            }
        )
    result = {
        "contract": "assessment-openai-smoke-audit-1",
        "origin": header.origin,
        "plan_sha256": header.plan_bytes_sha256,
        "slots": slots,
        "works": works,
        "count_intents": sum(stage == "input_count" for _, stage in expected[:index]),
        "generation_intents": sum(stage == "generation" for _, stage in expected[:index]),
        "journal_closed": stopped is not None,
        "stop_reason": stopped,
        "unknown_elapsed_endpoints": int(pending is not None),
        "known_generation_usage_subtotal": known,
        "generations_with_unknown_usage": unknown_usage,
        "transport_observation": header.origin == "observed_openai_transport" and index > 0,
        "model_observation": header.origin == "observed_openai_transport"
        and any(
            e.stage == "generation" and e.response is not None and e.response.raw_final is not None
            for rows in exchanges.values()
            for e in rows
        ),
        "provenance_limit": "Application-owned local journal, not provider-signed attestation",
        "actual_billed_cost": None,
        "semantic_support": "unassessed",
        "evidence_adequacy": "unassessed",
        "writer_dispatch_authorized": False,
    }
    view = io._literal(
        "Read-only OpenAI smoke audit", strict_object(encoded(result).decode())
    ).replace(
        io.NOTICE.encode(),
        (
            "READ-ONLY SMOKE AUDIT. Origin: " + header.origin + ". Local journal integrity is not "
            "provider attestation or semantic qualification. No writer permission."
        ).encode(),
        1,
    )
    output = {"audit.json": encoded(result), "view.md": view}
    output["manifest.json"] = encoded(
        {
            "contract": "assessment-openai-smoke-export-1",
            "files_sha256": {n: io._sha(v) for n, v in output.items()},
            "plan_sha256": header.plan_bytes_sha256,
            "journal_sha256": canonical_sha256({n: io._sha(v) for n, v in files.items()}),
        }
    )

    def recheck() -> None:
        require(
            load_plan(path) == plan and io._read_journal(journal_path) == files, "smoke_audit_drift"
        )
        for work in plan.works:
            require(_work(work) == prepared[work.name], "smoke_source_drift")

    protected = tuple(p for row in prepared.values() for p in row.collected.protected)
    return storage._publish(
        destination,
        output,
        (*protected, path, journal_path, *(Path(w.preparation) for w in plan.works)),
        recheck,
    )
