"""Authored-source OpenAI preparation, durable fixture journal and audit; no live client."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
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
from open_hollywood_engine.evaluations.assessment_delivery import Name
from open_hollywood_engine.evaluations.assessment_result import scope_for_batch
from open_hollywood_engine.evaluations.assessment_work import complete_work
from open_hollywood_engine.evaluations.contracts import canonical_sha256
from open_hollywood_engine.evaluations.review_evidence import (
    Digest,
    JsonObject,
    Record,
    require,
    strict_object,
)
from open_hollywood_engine.models import assessment_openai as mapper
from open_hollywood_engine.models import assessment_openai_authored as domain
from open_hollywood_engine.models import assessment_openai_manifest as shared_records
from open_hollywood_engine.models import openai as provider
from open_hollywood_engine.models import openai_catalog, openai_schema
from open_hollywood_engine.models.assessment_openai import (
    WireEndpoint,
    check_outgoing,
    map_response,
)
from open_hollywood_engine.models.assessment_openai_authored import (
    Exchange,
    RequestManifest,
    RequestSet,
    Settings,
    derive_terminal,
    make_request_set,
    ordered_endpoints,
    parse_set,
    wire_for,
)
from open_hollywood_engine.secrets import SecretLeakError
from pydantic import Field

from open_hollywood_api.persistence.secret_policy import active_secret_guard
from open_hollywood_api.services import assessment_authored_source as sources
from open_hollywood_api.services import assessment_completion as storage
from open_hollywood_api.services import assessment_delivery as io

MAX_BYTES = io.MAX_BYTES
NOTICE = (
    "AUTHORED SOURCE / INJECTED OPENAI TRANSPORT FIXTURE. No live delivery or model evidence. "
    "Source origin is authored_diagnostic; delivery origin is injected_fixture. Full original "
    "source context is retained. Fixture counts and usage are invented, "
    "not measurements or billing. "
    "Binding leaves factual support, evidence adequacy, editing and craft unassessed. "
    "Production prompts unchanged; writer permission false; canary on hold."
)


class TransportFixtures(Record):
    contract: Literal["assessment-openai-authored-transport-fixtures-1"]
    source_origin: Literal["authored_diagnostic"]
    delivery_origin: Literal["injected_fixture"]
    authored_by: str = Field(min_length=1, max_length=1200, pattern=r"\S")
    request_set_canonical_sha256: Digest
    cancel_before_dispatch: bool
    replies: tuple[io.FixtureReply, ...] = Field(min_length=6, max_length=6)


class JournalHeader(Record):
    contract: Literal["assessment-openai-authored-fixture-journal-1"]
    source_origin: Literal["authored_diagnostic"]
    delivery_origin: Literal["injected_fixture"]
    request_set_canonical_sha256: Digest
    preparation_manifest_bytes_sha256: Digest
    fixture_bytes_sha256: Digest
    implementation_canonical_sha256: Digest
    started_at_utc: Name
    live_calls: Literal[0]


class Intent(Record):
    kind: Literal["intent"]
    attempt_id: Name
    request_payload_canonical_sha256: Digest
    endpoint: WireEndpoint


class Outcome(Record):
    kind: Literal["outcome"]
    intent_bytes_sha256: Digest
    exchange: Exchange
    active_seconds: float = Field(ge=0, allow_inf_nan=False)


class Stop(Record):
    kind: Literal["stop"]
    reason: Literal["complete", "halted", "cancelled_before_dispatch"]


class JournalEvent(Record):
    contract: Literal["assessment-openai-authored-fixture-event-1"]
    sequence: Annotated[int, Field(ge=1, le=13)]
    previous_bytes_sha256: Digest
    recorded_at_utc: Name
    payload: Annotated[Intent | Outcome | Stop, Field(discriminator="kind")]


def _implementation() -> str:
    return canonical_sha256(
        {
            "source_adapter": sources._implementation(),
            "shared_journal_io": io._implementation(),
            **{
                name: io._sha(Path(str(module.__file__)).read_bytes())
                for name, module in (
                    ("manifest", domain),
                    ("wire_mapper", mapper),
                    ("settings_and_exchange", shared_records),
                    ("provider", provider),
                    ("catalog", openai_catalog),
                    ("schema", openai_schema),
                )
            },
            "application": io._sha(Path(__file__).read_bytes()),
            "cli": io._sha(
                (sources.ROOT / "scripts/assessment_openai_authored_delivery.py").read_bytes()
            ),
        }
    )


def _literal(title: str, value: JsonObject) -> bytes:
    return io._literal(title, value).replace(io.NOTICE.encode(), NOTICE.encode(), 1)


def _manifest(files: dict[str, bytes], plan: RequestSet, state: str) -> bytes:
    return encoded(
        {
            "contract": "assessment-openai-authored-publication-1",
            "source_origin": "authored_diagnostic",
            "delivery_origin": "injected_fixture",
            "state": state,
            "request_set_canonical_sha256": plan.payload_canonical_sha256,
            "files_sha256": {n: io._sha(raw) for n, raw in files.items()},
            "implementation_canonical_sha256": _implementation(),
            "live_calls": 0,
            "model_evidence": False,
            "writer_dispatch_authorized": False,
        }
    )


def _collect(source_id: str) -> tuple[sources.Collected, ...]:
    return tuple(sources.collect(source_id, family) for family in ("F01", "F02", "F03"))


def _make(collected: tuple[sources.Collected, ...], run_id: str, settings: Settings) -> RequestSet:
    return make_request_set(
        tuple(c.source for c in collected),
        tuple(strict_object(c.source_receipt.decode()) for c in collected),
        run_id,
        settings,
        _implementation(),
    )


def _files(collected: tuple[sources.Collected, ...], plan: RequestSet) -> dict[str, bytes]:
    template = {
        "contract": "assessment-openai-authored-transport-fixtures-1",
        "source_origin": "authored_diagnostic",
        "delivery_origin": "injected_fixture",
        "authored_by": "",
        "request_set_canonical_sha256": plan.payload_canonical_sha256,
        "cancel_before_dispatch": False,
        "replies": [
            {
                "attempt_id": m.payload.attempt_id,
                "stage": e.stage,
                "behavior": "response",
                "http_status": 200,
                "response_body_utf8": "",
            }
            for m, e in ordered_endpoints(plan)
        ],
    }
    files = {}
    for c in collected:
        family = c.source.source.family
        files[family + "-source.json"] = encoded(c.source.model_dump(mode="json"))
        files[family + "-source-receipt.json"] = c.source_receipt
    files["request-set.json"] = encoded(plan.model_dump(mode="json"))
    files["fixtures.template.json"] = encoded(template)
    files["view.md"] = _literal(
        "Authored-source OpenAI preparation",
        {"request_set": plan.model_dump(mode="json"), "notice": NOTICE},
    )
    files["manifest.json"] = _manifest(files, plan, "fixture_preparation_only")
    require(sum(map(len, files.values())) <= MAX_BYTES, "preparation_size")
    return files


def prepare_requests(source_id: str, destination: Path, *, run_id: str, settings: Settings) -> str:
    collected = _collect(source_id)
    plan = _make(collected, run_id, settings)
    files = _files(collected, plan)

    def recheck() -> None:
        require(_collect(source_id) == collected, "authored_openai_source_drift")
        require(_make(collected, run_id, settings) == plan, "authored_openai_implementation_drift")

    return storage._publish(
        destination, files, tuple(p for c in collected for p in c.protected), recheck
    )


@dataclass(frozen=True)
class _Prepared:
    collected: tuple[sources.Collected, ...]
    request_set: RequestSet
    files: dict[str, bytes]


def _load(source_id: str, preparation: Path) -> _Prepared:
    collected = _collect(source_id)
    storage._destination(preparation, tuple(p for c in collected for p in c.protected))
    saved = parse_set(storage._read(preparation / "request-set.json", MAX_BYTES))
    expected = _make(collected, saved.payload.run_id, saved.payload.settings)
    require(saved == expected, "authored_openai_preparation_changed")
    files = _files(collected, expected)
    storage._verify_output(preparation, files, manifest=True)
    return _Prepared(collected, expected, files)


def _source_for(prepared: _Prepared, manifest: RequestManifest) -> AuthoredSource:
    return next(c.source for c in prepared.collected if c.source.source == manifest.payload.source)


def parse_fixtures(raw: bytes, request_set: RequestSet) -> TransportFixtures:
    require(len(raw) <= io.MAX_FIXTURE_BYTES, "fixture_size")
    fixture = TransportFixtures.model_validate_json(encoded(strict_object(raw.decode())))
    require(
        fixture.request_set_canonical_sha256 == request_set.payload_canonical_sha256,
        "fixture_request_set_changed",
    )
    expected = [(m.payload.attempt_id, e.stage) for m, e in ordered_endpoints(request_set)]
    require([(r.attempt_id, r.stage) for r in fixture.replies] == expected, "fixture_coverage")
    return fixture


class _Journal:
    def __init__(self, path: Path, header: JournalHeader, fixtures: bytes) -> None:
        self.path = path
        path.mkdir(parents=True, exist_ok=False)
        self.files = {
            "fixtures.json": fixtures,
            "header.json": encoded(header.model_dump(mode="json")),
        }
        for name, data in self.files.items():
            io._durable_write(path / name, data)
        self.sequence, self.previous = 0, io._sha(self.files["header.json"])

    def append(self, payload: Intent | Outcome | Stop) -> str:
        require(io._read_journal(self.path) == self.files, "journal_changed_during_capture")
        event = JournalEvent(
            contract="assessment-openai-authored-fixture-event-1",
            sequence=self.sequence + 1,
            previous_bytes_sha256=self.previous,
            recorded_at_utc=datetime.now(UTC).isoformat(),
            payload=payload,
        )
        raw = encoded(event.model_dump(mode="json"))
        require(sum(map(len, self.files.values())) + len(raw) <= MAX_BYTES, "journal_size")
        name = f"event-{event.sequence:04d}.json"
        io._durable_write(self.path / name, raw)
        self.files[name] = raw
        self.sequence, self.previous = event.sequence, io._sha(raw)
        return self.previous


def _interrupted(endpoint: WireEndpoint) -> Exchange:
    return Exchange(
        stage=endpoint.stage,
        endpoint_canonical_sha256=canonical_sha256(endpoint.model_dump(mode="json")),
        dispatched_body_bytes_sha256=endpoint.body_bytes_sha256,
        dispatched_body_canonical_sha256=endpoint.body_canonical_sha256,
        disposition="interrupted",
        observed_http_status=None,
        response=None,
        retained_response_canonical_sha256=None,
        observed_raw_http_bytes_sha256=None,
        raw_http_bytes_retained=False,
        local_error=None,
    )


def _build_request(endpoint: WireEndpoint) -> httpx.Request:
    return httpx.Request(
        "POST",
        endpoint.destination + endpoint.path,
        content=endpoint.body_utf8.encode(),
        headers={"Content-Type": "application/json"},
    )


def _capture(
    request: httpx.Request,
    endpoint: WireEndpoint,
    manifest: RequestManifest,
    journal: _Journal,
    transport: httpx.MockTransport,
    recheck: Callable[[], None],
) -> Outcome:
    check_outgoing(endpoint, request)
    intent = journal.append(
        Intent(
            kind="intent",
            attempt_id=manifest.payload.attempt_id,
            request_payload_canonical_sha256=manifest.payload_canonical_sha256,
            endpoint=endpoint,
        )
    )
    recheck()  # Intent remains consumed if source/fixture drift interrupts before dispatch.
    started, exchange = perf_counter(), _interrupted(endpoint)
    try:
        response = transport.handle_request(request)
    except (httpx.TransportError, io.FixtureCancelled) as exc:
        label = "cancelled" if isinstance(exc, io.FixtureCancelled) else "transport_error"
        exchange = exchange.model_copy(update={"disposition": label, "local_error": label})
    else:
        exchange = exchange.model_copy(update={"observed_http_status": response.status_code})
        try:
            content = bytearray()
            for chunk in response.iter_bytes():
                require(len(content) + len(chunk) <= mapper.MAX_RESPONSE_BYTES, "response_size")
                content.extend(chunk)
            raw = bytes(content)
            exchange = exchange.model_copy(update={"observed_raw_http_bytes_sha256": io._sha(raw)})
            mapped = map_response(
                endpoint.stage,
                response.status_code,
                raw,
                manifest.payload.settings.model_spec,
                guard=active_secret_guard(),
            )
            exchange = exchange.model_copy(
                update={
                    "disposition": "response",
                    "response": mapped,
                    "retained_response_canonical_sha256": canonical_sha256(
                        mapped.model_dump(mode="json")
                    ),
                }
            )
        except (ValueError, SecretLeakError, httpx.TransportError):
            exchange = exchange.model_copy(
                update={"disposition": "capture_error", "local_error": "capture_error"}
            )
        finally:
            response.close()
    outcome = Outcome(
        kind="outcome",
        intent_bytes_sha256=intent,
        exchange=exchange,
        active_seconds=perf_counter() - started,
    )
    journal.append(outcome)
    return outcome


def _continue(
    prepared: _Prepared, manifest: RequestManifest, outcomes: list[Outcome], total_seconds: float
) -> bool:
    if total_seconds >= prepared.request_set.payload.settings.max_transport_seconds:
        return False
    last = outcomes[-1].exchange
    if last.stage == "input_count":
        return last.response is not None and mapper.count_admitted(
            wire_for(manifest), last.response
        )
    terminal = derive_terminal(
        _source_for(prepared, manifest),
        manifest,
        tuple(o.exchange for o in outcomes),
        sum(o.active_seconds for o in outcomes),
    )
    return terminal.state == "bound_unassessed" and not terminal.accounting_hold


def capture_fixtures(
    source_id: str,
    preparation: Path,
    fixture_path: Path,
    destination: Path,
    *,
    transport: httpx.MockTransport | None = None,
) -> str:
    prepared = _load(source_id, preparation)
    protected = tuple(p for c in prepared.collected for p in c.protected)
    storage._destination(fixture_path, protected)
    raw = storage._read(fixture_path, io.MAX_FIXTURE_BYTES)
    fixture = parse_fixtures(raw, prepared.request_set)
    if transport is not None:
        require(type(transport) is httpx.MockTransport, "mock_transport_required")
    destination = storage._destination(destination, (*protected, preparation, fixture_path))
    require(not destination.exists(), "journal_already_exists_no_retry")

    def recheck() -> None:
        require(_load(source_id, preparation) == prepared, "authored_openai_source_drift")
        require(storage._read(fixture_path, io.MAX_FIXTURE_BYTES) == raw, "fixtures_changed")

    recheck()
    journal = _Journal(
        destination,
        JournalHeader(
            contract="assessment-openai-authored-fixture-journal-1",
            source_origin="authored_diagnostic",
            delivery_origin="injected_fixture",
            request_set_canonical_sha256=prepared.request_set.payload_canonical_sha256,
            preparation_manifest_bytes_sha256=io._sha(prepared.files["manifest.json"]),
            fixture_bytes_sha256=io._sha(raw),
            implementation_canonical_sha256=_implementation(),
            started_at_utc=datetime.now(UTC).isoformat(),
            live_calls=0,
        ),
        raw,
    )
    if fixture.cancel_before_dispatch:
        journal.append(Stop(kind="stop", reason="cancelled_before_dispatch"))
        return "cancelled_before_dispatch"
    outcomes: dict[str, list[Outcome]] = {
        m.payload.attempt_id: [] for m in prepared.request_set.payload.requests
    }
    total = 0.0
    for (manifest, endpoint), reply in zip(
        ordered_endpoints(prepared.request_set), fixture.replies, strict=True
    ):
        recheck()
        outcome = _capture(
            _build_request(endpoint),
            endpoint,
            manifest,
            journal,
            transport if transport is not None else io._fixture_transport(reply),
            recheck,
        )
        rows = outcomes[manifest.payload.attempt_id]
        rows.append(outcome)
        total += outcome.active_seconds
        if not _continue(prepared, manifest, rows, total):
            journal.append(Stop(kind="stop", reason="halted"))
            return "halted"
    journal.append(Stop(kind="stop", reason="complete"))
    return "complete"


def _audit(prepared: _Prepared, files: dict[str, bytes]) -> JsonObject:
    require("header.json" in files and "fixtures.json" in files, "journal_header_missing")
    header = JournalHeader.model_validate_json(
        encoded(strict_object(files["header.json"].decode()))
    )
    plan = prepared.request_set
    require(
        header.request_set_canonical_sha256 == plan.payload_canonical_sha256
        and header.preparation_manifest_bytes_sha256 == io._sha(prepared.files["manifest.json"])
        and header.fixture_bytes_sha256 == io._sha(files["fixtures.json"])
        and header.implementation_canonical_sha256 == _implementation(),
        "journal_binding_changed",
    )
    fixture = parse_fixtures(files["fixtures.json"], plan)
    names = [f"event-{i:04d}.json" for i in range(1, len(files) - 1)]
    require(set(files) == {"header.json", "fixtures.json", *names}, "journal_members")
    expected = ordered_endpoints(plan)
    outcomes: dict[str, list[Outcome]] = {m.payload.attempt_id: [] for m in plan.payload.requests}
    index, previous, total, halted = 0, io._sha(files["header.json"]), 0.0, False
    pending: tuple[RequestManifest, WireEndpoint, str] | None = None
    stop: Stop | None = None
    for sequence, name in enumerate(names, 1):
        raw = files[name]
        event = JournalEvent.model_validate_json(encoded(strict_object(raw.decode())))
        require(
            event.sequence == sequence and event.previous_bytes_sha256 == previous, "journal_chain"
        )
        previous = io._sha(raw)
        require(stop is None, "event_after_stop")
        p = event.payload
        if isinstance(p, Intent):
            require(
                not halted
                and not fixture.cancel_before_dispatch
                and pending is None
                and index < len(expected),
                "unexpected_intent",
            )
            m, e = expected[index]
            require(
                p.attempt_id == m.payload.attempt_id
                and p.endpoint == e
                and p.request_payload_canonical_sha256 == m.payload_canonical_sha256,
                "intent_changed",
            )
            pending = m, e, previous
            index += 1
        elif isinstance(p, Outcome):
            require(pending is not None, "outcome_without_intent")
            assert pending is not None
            m, e, intent = pending
            require(
                p.intent_bytes_sha256 == intent and p.exchange.stage == e.stage,
                "outcome_intent_changed",
            )
            rows = outcomes[m.payload.attempt_id]
            rows.append(p)
            total += p.active_seconds
            derive_terminal(
                _source_for(prepared, m),
                m,
                tuple(o.exchange for o in rows),
                sum(o.active_seconds for o in rows),
            )
            halted = not _continue(prepared, m, rows, total)
            pending = None
        else:
            require(pending is None, "stop_with_pending_intent")
            reason = (
                "cancelled_before_dispatch"
                if fixture.cancel_before_dispatch
                else "halted"
                if halted
                else "complete"
            )
            require(p.reason == reason, "stop_reason_changed")
            require(
                halted or fixture.cancel_before_dispatch or index == len(expected),
                "early_complete_stop",
            )
            stop = p
    pending_attempt = None
    if pending is not None:
        m, e, intent = pending
        pending_attempt = m.payload.attempt_id
        outcomes[pending_attempt].append(
            Outcome(
                kind="outcome",
                intent_bytes_sha256=intent,
                exchange=_interrupted(e),
                active_seconds=0,
            )
        )
    terminals = [
        derive_terminal(
            _source_for(prepared, m),
            m,
            tuple(o.exchange for o in outcomes[m.payload.attempt_id]),
            sum(o.active_seconds for o in outcomes[m.payload.attempt_id]),
            pending=m.payload.attempt_id == pending_attempt,
        )
        for m in plan.payload.requests
    ]
    completions = []
    for m, terminal in zip(plan.payload.requests, terminals, strict=True):
        source = _source_for(prepared, m)
        completion = complete_work(
            source.work,
            (terminal.native_receipt,) if terminal.native_receipt is not None else (),
            {m.payload.presentation.batch_id: m.payload_canonical_sha256},
        )
        completions.append(completion)
    eligible = (
        stop is not None
        and stop.reason == "complete"
        and pending is None
        and all(c.complete_delivery and c.binding == "complete" for c in completions)
        and all(not t.accounting_hold for t in terminals)
    )
    slots = []
    for m, endpoint in expected:
        exchange = next(
            (
                o.exchange
                for o in outcomes[m.payload.attempt_id]
                if o.exchange.stage == endpoint.stage
            ),
            None,
        )
        slots.append(
            {
                "family": m.payload.source.family,
                "stage": endpoint.stage,
                "request_payload_canonical_sha256": m.payload_canonical_sha256,
                "status": "undispatched" if exchange is None else exchange.disposition,
                "consumed": exchange is not None,
            }
        )
    return strict_object(
        encoded(
            {
                "contract": "assessment-openai-authored-audit-1",
                "source_origin": "authored_diagnostic",
                "delivery_origin": "injected_fixture",
                "notice": NOTICE,
                "sources": [c.source.model_dump(mode="json") for c in prepared.collected],
                "source_receipts": [
                    strict_object(c.source_receipt.decode()) for c in prepared.collected
                ],
                "request_set": plan.model_dump(mode="json"),
                "terminals": [t.model_dump(mode="json") for t in terminals],
                "completions": [c.model_dump(mode="json") for c in completions],
                "slots": slots,
                "completion_eligible": eligible,
                "journal_closed": stop is not None,
                "stop_reason": stop.reason if stop else None,
                "publication_state": "bound_unassessed"
                if eligible
                else "incomplete_terminal_audit",
                "fixture_count_attempts": sum(
                    e.stage == "input_count" for t in terminals for e in t.exchanges
                ),
                "fixture_generation_attempts": sum(t.native_receipt is not None for t in terminals),
                "known_transport_seconds": total,
                "unknown_elapsed_endpoints": int(pending is not None),
                "transport_time_limit_reached": total
                >= plan.payload.settings.max_transport_seconds,
                "accounting_hold": any(t.accounting_hold for t in terminals),
                "generations_with_unknown_usage": sum(
                    t.native_receipt is not None
                    and any(v is None for v in t.usage.model_dump().values())
                    for t in terminals
                ),
                "next_dispatch_allowed": False,
                "usage_applicability": "authored_transport_fixture_not_billing",
                "actual_billed_cost": None,
                "model_evidence": False,
                "live_calls": 0,
                "writer_dispatch_authorized": False,
                "factual_support": "unassessed",
                "evidence_adequacy": "unassessed",
                "editorial_effect": "unassessed",
                "edit_necessity": "unassessed",
                "craft": "unassessed",
            }
        ).decode()
    )


def audit_terminal(source_id: str, preparation: Path, journal: Path, destination: Path) -> str:
    prepared = _load(source_id, preparation)
    journal_files = io._read_journal(journal)
    envelope = _audit(prepared, journal_files)
    files = {
        name: raw
        for name, raw in prepared.files.items()
        if name.endswith("-source.json") or name.endswith("-source-receipt.json")
    }
    files.update(
        {
            "request-set.json": prepared.files["request-set.json"],
            "journal.json": encoded(
                {n: strict_object(b.decode()) for n, b in journal_files.items()}
            ),
            "audit.json": encoded(envelope),
            "view.md": _literal("Authored-source OpenAI terminal audit", envelope),
        }
    )
    raw_terminals = envelope["terminals"]
    assert isinstance(raw_terminals, list)
    for m, raw_terminal in zip(prepared.request_set.payload.requests, raw_terminals, strict=True):
        terminal = domain.Terminal.model_validate_json(encoded(raw_terminal))
        source = _source_for(prepared, m)
        scope = scope_for_batch(
            source.work, m.payload.presentation.batch_id, m.payload_canonical_sha256
        )
        authority = AssessmentAuthority.model_validate_json(
            encoded(
                {
                    **source.authority.model_dump(mode="json"),
                    "request_sha256": m.payload_canonical_sha256,
                }
            )
        )
        bound = terminal.bound_result
        view = render_assessment_authority(
            source.work,
            scope,
            source.declarations,
            source.briefs,
            authority,
            receipt=terminal.native_receipt if bound else None,
            raw_final=str(bound["raw_final"]) if bound else None,
        )
        files[m.payload.source.family + "-evidence.md"] = (
            NOTICE + "\n\nProjection of `audit.json`.\n\n" + view
        ).encode()
    files["manifest.json"] = _manifest(
        files, prepared.request_set, str(envelope["publication_state"])
    )

    def recheck() -> None:
        require(_load(source_id, preparation) == prepared, "authored_openai_source_drift")
        require(io._read_journal(journal) == journal_files, "journal_changed_during_audit")

    return storage._publish(
        destination,
        files,
        (*tuple(p for c in prepared.collected for p in c.protected), preparation, journal),
        recheck,
    )
