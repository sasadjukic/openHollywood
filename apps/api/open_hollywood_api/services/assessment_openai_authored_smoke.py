"""Separate authored-source three-work smoke freeze, one-shot transport and read-only audit.

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
from open_hollywood_engine.evaluations.assessment_authored_source import AuthoredSource
from open_hollywood_engine.evaluations.assessment_authority import (
    AssessmentAuthority,
    render_assessment_authority,
)
from open_hollywood_engine.evaluations.assessment_completion import encoded
from open_hollywood_engine.evaluations.assessment_delivery import Stage
from open_hollywood_engine.evaluations.assessment_result import scope_for_batch
from open_hollywood_engine.evaluations.assessment_work import complete_work
from open_hollywood_engine.evaluations.contracts import canonical_sha256
from open_hollywood_engine.evaluations.review_evidence import (
    Digest,
    JsonObject,
    Record,
    require,
    strict_object,
    text_hash,
)
from open_hollywood_engine.models.assessment_openai import (
    MAX_RESPONSE_BYTES,
    check_outgoing,
    count_admitted,
    map_response,
)
from open_hollywood_engine.models.assessment_openai_authored import (
    Exchange,
    RequestManifest,
    derive_terminal,
    ordered_endpoints,
    wire_for,
)
from open_hollywood_engine.secrets import SecretLeakGuard, SecretValue
from pydantic import Field

from open_hollywood_api.services import assessment_completion as storage
from open_hollywood_api.services import assessment_delivery as io
from open_hollywood_api.services import assessment_openai_authored_delivery as rehearsal

NAMES = ("F01", "F02", "F03")
SCORING = (
    "Three fixed authored works; nine active whole factual claims. Primary: source/request "
    "integrity, count admission, terminal delivery, exact native binding and all-work coverage. "
    "Retain all six slots, failures, undispatched slots and unknown usage. Inspect every delivered "
    "claim against frozen authored admission gold for whole-claim support, "
    "all material components, "
    "source/version citation coverage and explanation materiality. Equivalent complete evidence "
    "is allowed; example citations are not a whitelist. Three supported, three contradicted and "
    "three unavailable controls. Gold is assistant-authored, not independent human ground truth. "
    "Delivery and semantic scores are separate; unavailable deliveries cannot count as semantic "
    "success. No repair, salvage, selection changes, writer dispatch, craft score or promotion."
)
STOPS = (
    "One fixed journal, no retries or resume. Count F01,F02,F03 before any generation, then "
    "generate in the same order. Any failed/unknown/over-budget count stops later calls. "
    "Any delivery/binding failure, unknown usage, reservation violation, timeout, cancellation, "
    "source/request/gold/metadata/code drift or journal failure stops dispatch. "
    "No trimming, replacement, recovery calls, budget increases or successful-subset publication."
)


class Plan(Record):
    contract: Literal["assessment-openai-authored-three-work-smoke-1"]
    source_id: str
    preparation: str
    request_set_sha256: Digest
    preparation_manifest_sha256: Digest
    scoring_path: str
    scoring_bytes_sha256: Digest
    metadata_path: str
    metadata_bytes_sha256: Digest
    live_journal: str
    implementation_sha256: Digest
    count_limit: Literal[3]
    generation_limit: Literal[3]
    retry_limit: Literal[0]
    max_generation_cost_usd: Literal["3.00"]
    count_timeout_seconds: Literal[120]
    generation_timeout_seconds: Literal[600]
    run_wall_seconds: Literal[2700]
    scoring: str
    stops: str
    approval_required: Literal[True]
    writer_dispatch_authorized: Literal[False]


Origin = Literal["injected_transport_fixture", "observed_openai_transport"]


class Header(Record):
    contract: Literal["assessment-openai-authored-smoke-journal-1"]
    source_origin: Literal["authored_diagnostic"]
    delivery_origin: Origin
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
    contract: Literal["assessment-openai-authored-smoke-event-1"]
    sequence: int = Field(ge=1, le=13)
    previous_bytes_sha256: Digest
    recorded_at_utc: str
    payload: Annotated[Intent | Outcome | Stop, Field(discriminator="kind")]


def implementation() -> str:
    return canonical_sha256(
        {
            "rehearsal": rehearsal._implementation(),
            "smoke": io._sha(Path(__file__).read_bytes()),
            "operator_cli": io._sha(
                (
                    Path(__file__).resolve().parents[4]
                    / "scripts/assessment_openai_authored_smoke.py"
                ).read_bytes()
            ),
        }
    )


def scoring_for(prepared: rehearsal._Prepared) -> bytes:
    cases = []
    members = {}
    for collected in prepared.collected:
        source = collected.source
        family = source.source.family
        name = family + "/admission.json"
        raw = collected.authenticated_members[name]
        admission = strict_object(raw.decode())
        require(
            admission.get("family") == family and admission.get("live_calls") == 0,
            "smoke_gold_family",
        )
        rows = admission.get("rows")
        require(isinstance(rows, list) and len(rows) == 3, "smoke_gold_coverage")
        assert isinstance(rows, list)
        labels = []
        for statement, row in zip(source.work.context.statements, rows, strict=True):
            require(isinstance(row, dict), "smoke_gold_row")
            assert isinstance(row, dict)
            require(
                row.get("unit_id") == statement.unit_id
                and row.get("whole_field") == statement.quote
                and row.get("whole_field_sha256") == text_hash(statement.quote),
                "smoke_gold_whole_claim",
            )
            labels.append(str(row.get("judgment")))
        require(sorted(labels) == ["supported", "uncertain", "unsupported"], "smoke_gold_classes")
        members[name] = io._sha(raw)
        cases.append(
            {"family": family, "work_sha256": source.work.fingerprint, "admission": admission}
        )
    return encoded(
        {
            "contract": "assessment-authored-smoke-scoring-1",
            "source_id": prepared.request_set.payload.source_id,
            "origin": "assistant_authored_not_independent_human_gold",
            "gold_in_model_input": False,
            "admitted_gold_members_sha256": members,
            "cases": cases,
            "scoring": SCORING,
            "semantic_adjudication": (
                "inspect_every_delivered_whole_claim_and_all_material_evidence"
            ),
            "writer_dispatch_authorized": False,
        }
    )


def _prepared(plan: Plan) -> rehearsal._Prepared:
    prepared = rehearsal._load(plan.source_id, Path(plan.preparation))
    require(
        prepared.request_set.payload_canonical_sha256 == plan.request_set_sha256
        and io._sha(prepared.files["manifest.json"]) == plan.preparation_manifest_sha256,
        "smoke_preparation_changed",
    )
    require(
        tuple(m.payload.source.family for m in prepared.request_set.payload.requests) == NAMES,
        "smoke_work_order",
    )
    require(
        len({m.payload.work_sha256 for m in prepared.request_set.payload.requests}) == 3,
        "smoke_duplicate_work",
    )
    settings = prepared.request_set.payload.settings
    require(
        settings.model_spec.model_identifier == "gpt-6.1-sol"
        and settings.reasoning == "high"
        and settings.max_input_tokens == 272000
        and settings.max_output_tokens == 32000
        and Decimal(settings.max_cost_usd) == 1,
        "smoke_settings",
    )
    gold = storage._read(Path(plan.scoring_path))
    require(
        io._sha(gold) == plan.scoring_bytes_sha256 and gold == scoring_for(prepared),
        "smoke_gold_changed",
    )
    metadata = storage._read(Path(plan.metadata_path))
    require(io._sha(metadata) == plan.metadata_bytes_sha256, "smoke_metadata_changed")
    note = strict_object(metadata.decode())
    require(
        note.get("model_spec") == settings.model_spec.model_dump(mode="json")
        and note.get("provider_api_calls") == 0,
        "smoke_metadata_binding",
    )
    return prepared


def load_plan(path: Path) -> Plan:
    plan = Plan.model_validate_json(encoded(strict_object(storage._read(path).decode())))
    require(plan.implementation_sha256 == implementation(), "smoke_implementation_changed")
    require(plan.scoring == SCORING and plan.stops == STOPS, "smoke_contract_changed")
    for name in (plan.preparation, plan.scoring_path, plan.metadata_path, plan.live_journal):
        require(Path(name).is_absolute(), "smoke_absolute_paths")
        storage._unlinked(Path(name))
    return plan


def freeze(
    source_id: str,
    preparation: Path,
    scoring_path: Path,
    metadata_path: Path,
    destination: Path,
    live_journal: Path,
) -> str:
    prepared = rehearsal._load(source_id, preparation)
    plan = Plan(
        contract="assessment-openai-authored-three-work-smoke-1",
        source_id=source_id,
        preparation=str(storage._unlinked(preparation)),
        request_set_sha256=prepared.request_set.payload_canonical_sha256,
        preparation_manifest_sha256=io._sha(prepared.files["manifest.json"]),
        scoring_path=str(storage._unlinked(scoring_path)),
        scoring_bytes_sha256=io._sha(storage._read(scoring_path)),
        metadata_path=str(storage._unlinked(metadata_path)),
        metadata_bytes_sha256=io._sha(storage._read(metadata_path)),
        live_journal=str(storage._unlinked(live_journal)),
        implementation_sha256=implementation(),
        count_limit=3,
        generation_limit=3,
        retry_limit=0,
        max_generation_cost_usd="3.00",
        count_timeout_seconds=120,
        generation_timeout_seconds=600,
        run_wall_seconds=2700,
        scoring=SCORING,
        stops=STOPS,
        approval_required=True,
        writer_dispatch_authorized=False,
    )
    require(_prepared(plan) == prepared, "smoke_freeze_source_drift")
    protected = (
        *tuple(p for c in prepared.collected for p in c.protected),
        preparation,
        scoring_path,
        metadata_path,
    )
    destination = storage._destination(destination, protected)
    storage._destination(live_journal, (*protected, destination))
    raw = encoded(plan.model_dump(mode="json"))
    require(not live_journal.exists(), "smoke_live_journal_already_exists")
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
            contract="assessment-openai-authored-smoke-journal-1",
            source_origin="authored_diagnostic",
            delivery_origin=origin,
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
            contract="assessment-openai-authored-smoke-event-1",
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


def _allowed(source: AuthoredSource, manifest: RequestManifest, exchanges: list[Exchange]) -> bool:
    if len(exchanges) == 1:
        response = exchanges[0].response
        return response is not None and count_admitted(wire_for(manifest), response)
    terminal = derive_terminal(source, manifest, tuple(exchanges), 0)
    return terminal.state == "bound_unassessed" and not terminal.accounting_hold


async def _exchange(
    client: httpx.AsyncClient,
    manifest: RequestManifest,
    stage: Stage,
    secret: SecretValue,
    timeout: float,
) -> tuple[Exchange, str | None]:
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
    path: Path, journal_path: Path, client: httpx.AsyncClient, secret: SecretValue, origin: Origin
) -> str:
    plan = load_plan(path)
    prepared = _prepared(plan)
    protected = tuple(p for c in prepared.collected for p in c.protected)
    journal_path = storage._destination(
        journal_path,
        (
            *protected,
            path,
            Path(plan.preparation),
            Path(plan.scoring_path),
            Path(plan.metadata_path),
        ),
    )
    require(
        (origin == "observed_openai_transport") == (journal_path == Path(plan.live_journal)),
        "smoke_origin_path",
    )
    require(not journal_path.exists(), "smoke_no_resume_or_retry")
    journal = Journal(journal_path, path, origin)
    started = perf_counter()
    exchanges: dict[str, list[Exchange]] = {name: [] for name in NAMES}
    for manifest, endpoint in ordered_endpoints(prepared.request_set):
        require(
            load_plan(path) == plan and _prepared(plan) == prepared, "smoke_source_or_plan_drift"
        )
        family, stage = manifest.payload.source.family, endpoint.stage
        remaining = plan.run_wall_seconds - (perf_counter() - started)
        if remaining <= 0:
            journal.append(
                Stop(kind="stop", reason="deadline", elapsed_wall_seconds=perf_counter() - started)
            )
            return "deadline"
        check_outgoing(endpoint, rehearsal._build_request(endpoint))
        SecretLeakGuard((secret,)).ensure_safe(endpoint.body_utf8, destination="smoke input")
        intent = journal.append(
            Intent(
                kind="intent",
                work=family,
                stage=stage,
                request_payload_sha256=manifest.payload_canonical_sha256,
                endpoint_sha256=canonical_sha256(endpoint.model_dump(mode="json")),
                body_bytes_sha256=endpoint.body_bytes_sha256,
            )
        )
        # Revalidate after durable intent too; drift leaves a consumed, pending slot.
        require(
            load_plan(path) == plan and _prepared(plan) == prepared, "smoke_source_or_plan_drift"
        )
        mark = perf_counter()
        remaining = plan.run_wall_seconds - (mark - started)
        if remaining <= 0:
            journal.append(
                Outcome(
                    kind="outcome",
                    intent_bytes_sha256=intent,
                    exchange=rehearsal._interrupted(endpoint).model_copy(
                        update={"disposition": "cancelled", "local_error": "cancelled"}
                    ),
                    request_id=None,
                    elapsed_seconds=0,
                )
            )
            journal.append(
                Stop(kind="stop", reason="deadline", elapsed_wall_seconds=mark - started)
            )
            return "deadline"
        timeout = min(
            remaining,
            plan.count_timeout_seconds
            if stage == "input_count"
            else plan.generation_timeout_seconds,
        )
        exchange, request_id = await _exchange(client, manifest, stage, secret, timeout)
        journal.append(
            Outcome(
                kind="outcome",
                intent_bytes_sha256=intent,
                exchange=exchange,
                request_id=request_id,
                elapsed_seconds=perf_counter() - mark,
            )
        )
        exchanges[family].append(exchange)
        source = rehearsal._source_for(prepared, manifest)
        if not _allowed(source, manifest, exchanges[family]):
            journal.append(
                Stop(kind="stop", reason="halted", elapsed_wall_seconds=perf_counter() - started)
            )
            return "halted"
    journal.append(
        Stop(kind="stop", reason="complete", elapsed_wall_seconds=perf_counter() - started)
    )
    return "complete"


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
    storage._destination(journal, (Path(load_plan(path).live_journal),))
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
    _prepared(plan)  # Authenticate sources and operator gold before constructing real transport.
    # No caller endpoint/proxy/transport override. TLS verification and zero connect retries.
    transport = httpx.AsyncHTTPTransport(retries=0, verify=True, trust_env=False)
    async with _client(transport) as client:
        return await _execute(path, journal, client, secret, "observed_openai_transport")


def audit(path: Path, journal_path: Path, destination: Path) -> str:
    from open_hollywood_engine.evaluations.review_evidence import strict_object

    plan = load_plan(path)
    prepared = _prepared(plan)
    manifests: dict[str, RequestManifest] = {
        m.payload.source.family: m for m in prepared.request_set.payload.requests
    }
    files = io._read_journal(journal_path)
    header = Header.model_validate_json(encoded(strict_object(files["header.json"].decode())))
    require(
        (header.delivery_origin == "observed_openai_transport")
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
    expected: list[tuple[str, Stage]] = [(name, stage) for stage in stages for name in NAMES]
    exchanges: dict[str, list[Exchange]] = {name: [] for name in NAMES}
    seconds: dict[str, float] = {name: 0.0 for name in NAMES}
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
            require(not halted and pending is None and index < 6, "smoke_extra_intent")
            work, stage = expected[index]
            manifest = manifests[work]
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
            manifest = manifests[work]
            derive_terminal(
                rehearsal._source_for(prepared, manifest),
                manifest,
                tuple(exchanges[work]),
                seconds[work],
            )
            halted = not _allowed(
                rehearsal._source_for(prepared, manifest), manifest, exchanges[work]
            )
            slots.append(
                {
                    "work": work,
                    "stage": stage,
                    "state": "observed_terminal"
                    if header.delivery_origin == "observed_openai_transport"
                    else "fixture_terminal",
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
                (p.reason == "complete" and index == 6 and not halted)
                or (p.reason == "halted" and halted)
                or p.reason in ("deadline", "cancelled"),
                "smoke_wrong_stop",
            )
            stopped = p.reason
    if pending is not None:
        work, stage, _ = pending
        manifest = manifests[work]
        endpoint = manifest.payload.endpoints[0 if stage == "input_count" else 1]
        exchanges[work].append(rehearsal._interrupted(endpoint))
        slots.append({"work": work, "stage": stage, "state": "interrupted_unknown_usage"})
    for work, stage in expected[index:]:
        slots.append({"work": work, "stage": stage, "state": "not_dispatched"})
    works: list[JsonObject] = []
    complete: list[bool] = []
    known = {
        k: 0 for k in ("input_tokens", "output_tokens", "reasoning_tokens", "cached_input_tokens")
    }
    unknown_usage = 0
    accounting_holds = 0
    for family in NAMES:
        manifest = manifests[family]
        source = rehearsal._source_for(prepared, manifest)
        terminal = derive_terminal(
            source,
            manifest,
            tuple(exchanges[family]),
            seconds[family],
            pending=pending is not None and pending[0] == family,
        )
        native_work = source.work
        completion = complete_work(
            native_work,
            (terminal.native_receipt,) if terminal.native_receipt else (),
            {manifest.payload.presentation.batch_id: manifest.payload_canonical_sha256},
        )
        complete.append(completion.complete_delivery and completion.binding == "complete")
        if terminal.native_receipt:
            unknown_usage += int(any(v is None for v in terminal.usage.model_dump().values()))
            accounting_holds += int(terminal.accounting_hold)
            for key, value in terminal.usage.model_dump().items():
                if value is not None:
                    known[key] += value
        works.append(
            {
                "work": family,
                "source": source.model_dump(mode="json"),
                "terminal": terminal.model_dump(
                    mode="json",
                    exclude={"contract", "source_origin", "delivery_origin", "model_evidence"},
                ),
                "completion": completion.model_dump(mode="json"),
            }
        )
    eligible = stopped == "complete" and pending is None and accounting_holds == 0 and all(complete)
    for row in works:
        row["completion_eligible"] = eligible
    result = {
        "contract": "assessment-openai-authored-smoke-audit-1",
        "source_origin": "authored_diagnostic",
        "delivery_origin": header.delivery_origin,
        "completion_eligible": eligible,
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
        "generations_with_accounting_hold": accounting_holds,
        "transport_observation": header.delivery_origin == "observed_openai_transport"
        and index > 0,
        "model_observation": header.delivery_origin == "observed_openai_transport"
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
            "READ-ONLY SMOKE AUDIT. Origin: "
            + header.delivery_origin
            + ". Local journal integrity is not "
            "provider attestation or semantic qualification. No writer permission."
        ).encode(),
        1,
    )
    output = {
        "audit.json": encoded(result),
        "view.md": view,
        "plan.json": storage._read(path),
        "request-set.json": prepared.files["request-set.json"],
        "scoring.json": storage._read(Path(plan.scoring_path)),
        "metadata.json": storage._read(Path(plan.metadata_path)),
        "journal.json": encoded({n: strict_object(raw.decode()) for n, raw in files.items()}),
    }
    for collected in prepared.collected:
        family = collected.source.source.family
        source = collected.source
        manifest = manifests[family]
        output[family + "-source.json"] = encoded(source.model_dump(mode="json"))
        output[family + "-source-receipt.json"] = collected.source_receipt
        scope = scope_for_batch(
            source.work, manifest.payload.presentation.batch_id, manifest.payload_canonical_sha256
        )
        authority = AssessmentAuthority.model_validate_json(
            encoded(
                {
                    **source.authority.model_dump(mode="json"),
                    "request_sha256": manifest.payload_canonical_sha256,
                }
            )
        )
        terminal = derive_terminal(
            source,
            manifest,
            tuple(exchanges[family]),
            seconds[family],
            pending=pending is not None and pending[0] == family,
        )
        bound = terminal.bound_result
        native_view = render_assessment_authority(
            source.work,
            scope,
            source.declarations,
            source.briefs,
            authority,
            receipt=terminal.native_receipt if bound else None,
            raw_final=str(bound["raw_final"]) if bound else None,
        )
        output[family + "-evidence.md"] = (
            "READ-ONLY SMOKE AUDIT. Delivery origin: "
            + header.delivery_origin
            + ". Source origin: authored_diagnostic. Projection of `audit.json`; "
            "no semantic or writer approval.\n\n" + native_view
        ).encode()
    output["manifest.json"] = encoded(
        {
            "contract": "assessment-openai-authored-smoke-export-1",
            "files_sha256": {n: io._sha(v) for n, v in output.items()},
            "plan_sha256": header.plan_bytes_sha256,
            "journal_sha256": canonical_sha256({n: io._sha(v) for n, v in files.items()}),
        }
    )

    def recheck() -> None:
        require(
            load_plan(path) == plan and io._read_journal(journal_path) == files, "smoke_audit_drift"
        )
        require(_prepared(plan) == prepared, "smoke_source_drift")

    protected = tuple(p for c in prepared.collected for p in c.protected)
    return storage._publish(
        destination,
        output,
        (
            *protected,
            path,
            journal_path,
            Path(plan.live_journal),
            Path(plan.preparation),
            Path(plan.scoring_path),
            Path(plan.metadata_path),
        ),
        recheck,
    )
