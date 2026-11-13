"""Intake-bound OpenAI wire preparation and durable injected-fixture audit; no live client."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from time import perf_counter
from typing import Annotated, Literal

import httpx
from open_hollywood_engine.evaluations import assessment_presentation
from open_hollywood_engine.evaluations.assessment_completion import CompletionContext, encoded
from open_hollywood_engine.evaluations.assessment_delivery import Name
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
from open_hollywood_engine.models import assessment_openai_manifest as domain
from open_hollywood_engine.models import openai as provider
from open_hollywood_engine.models import openai_catalog, openai_schema
from open_hollywood_engine.models.assessment_openai import (
    WireEndpoint,
    check_outgoing,
    map_response,
)
from open_hollywood_engine.models.assessment_openai_manifest import (
    Exchange,
    RequestManifest,
    RequestSet,
    Settings,
    derive_terminal,
    make_request_set,
    parse_set,
    wire_for,
)
from open_hollywood_engine.secrets import SecretLeakError
from pydantic import Field

from open_hollywood_api.persistence.secret_policy import active_secret_guard
from open_hollywood_api.services import assessment_completion as storage
from open_hollywood_api.services import assessment_delivery as io

MAX_BYTES = io.MAX_BYTES
NOTICE = (
    "OPENAI WIRE REHEARSAL — INJECTED FIXTURES, NO MODEL DELIVERY. "
    "Original intake/source identity is preserved. New diagnostic assessment presentation is "
    "explicit; production prompts are unchanged. Fixture usage is not billing. "
    "Native binding leaves factual support, evidence adequacy, editing and craft unassessed."
)


class TransportFixtures(Record):
    contract: Literal["assessment-openai-transport-fixtures-1"]
    origin: Literal["injected_fixture"]
    authored_by: str = Field(min_length=1, max_length=1200, pattern=r"\S")
    request_set_canonical_sha256: Digest
    cancel_before_dispatch: bool
    replies: tuple[io.FixtureReply, ...] = Field(min_length=2, max_length=24)


class JournalHeader(Record):
    contract: Literal["assessment-openai-fixture-journal-1"]
    origin: Literal["injected_fixture"]
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
    contract: Literal["assessment-openai-fixture-event-1"]
    sequence: Annotated[int, Field(ge=1, le=49)]
    previous_bytes_sha256: Digest
    recorded_at_utc: Name
    payload: Annotated[Intent | Outcome | Stop, Field(discriminator="kind")]


def _implementation() -> str:
    return canonical_sha256(
        {
            "shared_source_and_journal_io": io._implementation(),
            **{
                name: io._sha(Path(str(module.__file__)).read_bytes())
                for name, module in (
                    ("presentation", assessment_presentation),
                    ("manifest", domain),
                    ("wire_mapper", mapper),
                    ("provider", provider),
                    ("schema", openai_schema),
                    ("catalog", openai_catalog),
                )
            },
            "application": io._sha(Path(__file__).read_bytes()),
        }
    )


def _literal(title: str, value: JsonObject) -> bytes:
    # Reuse literal fencing; substitute only the outer authored notice.
    return io._literal(title, value).replace(io.NOTICE.encode(), NOTICE.encode(), 1)


def _manifest(files: dict[str, bytes], request_set: RequestSet, state: str) -> bytes:
    return encoded(
        {
            "contract": "assessment-openai-rehearsal-publication-1",
            "origin": "injected_fixture",
            "state": state,
            "request_set_canonical_sha256": request_set.payload_canonical_sha256,
            "files_sha256": {n: io._sha(b) for n, b in files.items()},
            "implementation_canonical_sha256": _implementation(),
            "live_calls": 0,
            "model_evidence": False,
            "writer_dispatch_authorized": False,
        }
    )


def _files(context: CompletionContext, request_set: RequestSet) -> dict[str, bytes]:
    template = {
        "contract": "assessment-openai-transport-fixtures-1",
        "origin": "injected_fixture",
        "authored_by": "",
        "request_set_canonical_sha256": request_set.payload_canonical_sha256,
        "cancel_before_dispatch": False,
        "replies": [
            {
                "attempt_id": m.payload.attempt_id,
                "stage": e.stage,
                "behavior": "response",
                "http_status": 200,
                "response_body_utf8": "",
            }
            for m in request_set.payload.requests
            for e in m.payload.endpoints
        ],
    }
    result = {
        "intake.json": context.exact_intake,
        "source-receipt.json": encoded(context.adapter_receipt),
        "request-set.json": encoded(request_set.model_dump(mode="json")),
        "fixtures.template.json": encoded(template),
        "view.md": _literal(
            "OpenAI intake requests",
            {
                "intake": context.intake.model_dump(mode="json"),
                "request_set": request_set.model_dump(mode="json"),
                "notice": NOTICE,
            },
        ),
    }
    result["manifest.json"] = _manifest(result, request_set, "openai_wire_preparation_only")
    require(sum(map(len, result.values())) <= MAX_BYTES, "preparation_size")
    return result


def prepare_requests(
    intake: Path, destination: Path, *, run_id: str, settings: Settings
) -> Literal["created", "reused"]:
    collected = storage._collect(intake)
    plan = make_request_set(collected.context, run_id, settings, _implementation())
    files = _files(collected.context, plan)

    def recheck() -> None:
        require(storage._collect(intake) == collected, "openai_source_drift")

    return storage._publish(destination, files, collected.protected, recheck)


@dataclass(frozen=True)
class _Prepared:
    collected: storage._Collected
    request_set: RequestSet
    files: dict[str, bytes]


def _load(intake: Path, preparation: Path) -> _Prepared:
    preparation = storage._unlinked(preparation)
    collected = storage._collect(intake)
    saved = parse_set(storage._read(preparation / "request-set.json", MAX_BYTES))
    expected = make_request_set(
        collected.context, saved.payload.run_id, saved.payload.settings, _implementation()
    )
    require(saved == expected, "openai_preparation_changed")
    files = _files(collected.context, expected)
    storage._verify_output(preparation, files, manifest=True)
    return _Prepared(collected, expected, files)


def parse_fixtures(raw: bytes, request_set: RequestSet) -> TransportFixtures:
    require(len(raw) <= io.MAX_FIXTURE_BYTES, "fixture_size")
    fixture = TransportFixtures.model_validate_json(encoded(strict_object(raw.decode())))
    require(
        fixture.request_set_canonical_sha256 == request_set.payload_canonical_sha256,
        "fixture_request_set_changed",
    )
    expected = [
        (m.payload.attempt_id, e.stage)
        for m in request_set.payload.requests
        for e in m.payload.endpoints
    ]
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
            contract="assessment-openai-fixture-event-1",
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
        prepared.collected.context,
        manifest,
        tuple(o.exchange for o in outcomes),
        sum(o.active_seconds for o in outcomes),
    )
    return terminal.state == "bound_unassessed" and not terminal.accounting_hold


def capture_fixtures(
    intake: Path,
    preparation: Path,
    fixture_path: Path,
    destination: Path,
    *,
    transport: httpx.MockTransport | None = None,
) -> str:
    prepared = _load(intake, preparation)
    raw = storage._read(fixture_path, io.MAX_FIXTURE_BYTES)
    fixture = parse_fixtures(raw, prepared.request_set)
    if transport is not None:
        require(type(transport) is httpx.MockTransport, "mock_transport_required")
    destination = storage._destination(
        destination, (*prepared.collected.protected, preparation, fixture_path)
    )
    require(not destination.exists(), "journal_already_exists_no_retry")
    require(_load(intake, preparation) == prepared, "openai_source_drift")
    require(storage._read(fixture_path, io.MAX_FIXTURE_BYTES) == raw, "fixtures_changed")
    header = JournalHeader(
        contract="assessment-openai-fixture-journal-1",
        origin="injected_fixture",
        request_set_canonical_sha256=prepared.request_set.payload_canonical_sha256,
        preparation_manifest_bytes_sha256=io._sha(prepared.files["manifest.json"]),
        fixture_bytes_sha256=io._sha(raw),
        implementation_canonical_sha256=_implementation(),
        started_at_utc=datetime.now(UTC).isoformat(),
        live_calls=0,
    )
    journal = _Journal(destination, header, raw)
    if fixture.cancel_before_dispatch:
        journal.append(Stop(kind="stop", reason="cancelled_before_dispatch"))
        return "cancelled_before_dispatch"
    replies, total = iter(fixture.replies), 0.0
    for manifest in prepared.request_set.payload.requests:
        outcomes: list[Outcome] = []
        for endpoint in manifest.payload.endpoints:
            reply = next(replies)
            require(_load(intake, preparation) == prepared, "openai_source_drift")
            outcome = _capture(
                _build_request(endpoint),
                endpoint,
                manifest,
                journal,
                transport if transport is not None else io._fixture_transport(reply),
            )
            outcomes.append(outcome)
            total += outcome.active_seconds
            if not _continue(prepared, manifest, outcomes, total):
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
    expected = [(m, e) for m in plan.payload.requests for e in m.payload.endpoints]
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
                prepared.collected.context,
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
            prepared.collected.context,
            m,
            tuple(o.exchange for o in outcomes[m.payload.attempt_id]),
            sum(o.active_seconds for o in outcomes[m.payload.attempt_id]),
            pending=m.payload.attempt_id == pending_attempt,
        )
        for m in plan.payload.requests
    ]
    work = prepared.collected.context.intake.pending_work
    assert work is not None
    completion = complete_work(
        work,
        tuple(t.native_receipt for t in terminals if t.native_receipt is not None),
        {
            m.payload.presentation.batch_id: m.payload_canonical_sha256
            for m in plan.payload.requests
        },
    )
    eligible = (
        stop is not None and completion.complete_delivery and completion.binding == "complete"
    )
    return strict_object(
        encoded(
            {
                "contract": "assessment-openai-rehearsal-audit-1",
                "origin": "injected_fixture",
                "notice": NOTICE,
                "intake": prepared.collected.context.intake.model_dump(mode="json"),
                "source_receipt": prepared.collected.context.adapter_receipt,
                "request_set": plan.model_dump(mode="json"),
                "terminals": [t.model_dump(mode="json") for t in terminals],
                "completion": completion.model_dump(mode="json"),
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


def audit_terminal(intake: Path, preparation: Path, journal: Path, destination: Path) -> str:
    prepared = _load(intake, preparation)
    journal_files = io._read_journal(journal)
    envelope = _audit(prepared, journal_files)
    files = {
        "intake.json": prepared.collected.context.exact_intake,
        "source-receipt.json": encoded(prepared.collected.context.adapter_receipt),
        "request-set.json": prepared.files["request-set.json"],
        "journal.json": encoded({n: strict_object(b.decode()) for n, b in journal_files.items()}),
        "audit.json": encoded(envelope),
        "view.md": _literal("OpenAI rehearsal audit", envelope),
    }
    files["manifest.json"] = _manifest(
        files, prepared.request_set, str(envelope["publication_state"])
    )

    def recheck() -> None:
        require(_load(intake, preparation) == prepared, "openai_source_drift")
        require(io._read_journal(journal) == journal_files, "journal_changed_during_audit")

    return storage._publish(
        destination, files, (*prepared.collected.protected, preparation, journal), recheck
    )
