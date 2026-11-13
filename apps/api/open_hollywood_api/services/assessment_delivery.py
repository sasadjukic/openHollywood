"""Registered-source preparation and read-only terminal audit; fixture transport only."""

from __future__ import annotations

import hashlib
import os
import re
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from time import perf_counter
from typing import Annotated, Literal

import httpx
import pydantic
from open_hollywood_engine.evaluations import assessment_delivery as domain
from open_hollywood_engine.evaluations import assessment_intake as intake_domain
from open_hollywood_engine.evaluations import assessment_result as result_domain
from open_hollywood_engine.evaluations import assessment_work as work_domain
from open_hollywood_engine.evaluations.assessment_completion import CompletionContext, encoded
from open_hollywood_engine.evaluations.assessment_delivery import (
    Endpoint,
    ErrorLink,
    Exchange,
    Name,
    RequestManifest,
    RequestSet,
    RetainedResponse,
    Stage,
    TerminalEvidence,
    derive_terminal,
    make_request_set,
    parse_request_set,
)
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
from open_hollywood_engine.secrets import SecretLeakError
from pydantic import Field, model_validator

from open_hollywood_api.persistence.secret_policy import active_secret_guard
from open_hollywood_api.services import assessment_completion as storage
from open_hollywood_api.services import assessment_intake as intake_storage
from open_hollywood_api.services import probe_review_export as probe_storage

MAX_BYTES = 64 * 1024 * 1024
MAX_MEMBER_BYTES = 16 * 1024 * 1024
MAX_RESPONSE_BYTES = 1024 * 1024
MAX_FIXTURE_BYTES = 4 * 1024 * 1024
NOTICE = (
    "AUTHORED TRANSPORT FIXTURE — NO MODEL DELIVERY. No inference or network call. "
    "Token counts are authored test data, not billing. Complete binding leaves truth, "
    "evidence adequacy, editing and craft unassessed; writer permission is false."
)


class FixtureReply(Record):
    attempt_id: Name
    stage: Stage
    behavior: Literal["response", "transport_error", "cancelled", "interrupt"]
    http_status: Annotated[int, Field(ge=100, le=599)] | None
    response_body_utf8: str = Field(max_length=MAX_RESPONSE_BYTES)

    @model_validator(mode="after")
    def outcome(self) -> FixtureReply:
        require(len(self.response_body_utf8.encode("utf-8")) <= MAX_RESPONSE_BYTES, "fixture_size")
        require(
            (self.behavior == "response" and self.http_status is not None)
            or (
                self.behavior != "response"
                and self.http_status is None
                and not self.response_body_utf8
            ),
            "fixture_outcome",
        )
        return self


class TransportFixtures(Record):
    contract: Literal["assessment-transport-fixtures-1"]
    origin: Literal["authored_fixture"]
    authored_by: str = Field(min_length=1, max_length=1200, pattern=r"\S")
    request_set_canonical_sha256: Digest
    cancel_before_dispatch: bool
    replies: tuple[FixtureReply, ...] = Field(min_length=1, max_length=24)


class JournalHeader(Record):
    contract: Literal["assessment-fixture-journal-1"]
    origin: Literal["authored_fixture"]
    request_set_canonical_sha256: Digest
    preparation_manifest_bytes_sha256: Digest
    fixture_bytes_sha256: Digest
    implementation_canonical_sha256: Digest
    started_at_utc: Name
    live_calls: Literal[0]


class Intent(Record):
    kind: Literal["intent"]
    attempt_id: Name
    endpoint: Endpoint


class Outcome(Record):
    kind: Literal["outcome"]
    intent_bytes_sha256: Digest
    exchange: Exchange
    active_seconds: float = Field(ge=0, allow_inf_nan=False)


class Stop(Record):
    kind: Literal["stop"]
    reason: Literal["complete", "halted", "cancelled_before_dispatch"]


class JournalEvent(Record):
    contract: Literal["assessment-fixture-journal-event-1"]
    sequence: Annotated[int, Field(ge=1, le=49)]
    previous_bytes_sha256: Digest
    recorded_at_utc: Name
    payload: Annotated[Intent | Outcome | Stop, Field(discriminator="kind")]


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _implementation() -> str:
    return canonical_sha256(
        {
            "domain": _sha(Path(domain.__file__).read_bytes()),
            "adapter": _sha(Path(__file__).read_bytes()),
            "source_and_publication": _sha(Path(storage.__file__).read_bytes()),
            "intake_domain": _sha(Path(intake_domain.__file__).read_bytes()),
            "result_binding": _sha(Path(result_domain.__file__).read_bytes()),
            "work_completion": _sha(Path(work_domain.__file__).read_bytes()),
            "intake_adapter": _sha(Path(intake_storage.__file__).read_bytes()),
            "registered_probe_adapter": _sha(Path(probe_storage.__file__).read_bytes()),
            "python": sys.version,
            "pydantic": pydantic.__version__,
            "httpx": httpx.__version__,
        }
    )


def _literal(title: str, value: JsonObject) -> bytes:
    content = encoded(value).decode("utf-8")
    fence = "`" * max(3, 1 + max((len(m[0]) for m in re.finditer(r"`+", content)), default=0))
    return (f"# {title}\n\n{NOTICE}\n\n{fence}json\n{content}{fence}\n").encode()


def _publication_manifest(files: dict[str, bytes], request_set: RequestSet, state: str) -> bytes:
    return encoded(
        {
            "contract": "assessment-fixture-publication-1",
            "origin": "authored_fixture",
            "state": state,
            "request_set_canonical_sha256": request_set.payload_canonical_sha256,
            "files_sha256": {n: _sha(b) for n, b in files.items()},
            "implementation_canonical_sha256": _implementation(),
            "model_evidence": False,
            "live_calls": 0,
            "writer_dispatch_authorized": False,
        }
    )


def _preparation_files(context: CompletionContext, request_set: RequestSet) -> dict[str, bytes]:
    template = {
        "contract": "assessment-transport-fixtures-1",
        "origin": "authored_fixture",
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
    view: JsonObject = {
        "notice": NOTICE,
        "intake": context.intake.model_dump(mode="json"),
        "request_set": request_set.model_dump(mode="json"),
    }
    files = {
        "intake.json": context.exact_intake,
        "source-receipt.json": encoded(context.adapter_receipt),
        "request-set.json": encoded(request_set.model_dump(mode="json")),
        "fixtures.template.json": encoded(template),
        "view.md": _literal("Fixture requests", view),
    }
    files["manifest.json"] = _publication_manifest(files, request_set, "fixture_requests_only")
    return files


def prepare_requests(
    intake_path: Path, destination: Path, *, run_id: str, with_count: bool = True
) -> Literal["created", "reused"]:
    collected = storage._collect(intake_path)
    request_set = make_request_set(
        collected.context, run_id, _implementation(), with_count=with_count
    )
    files = _preparation_files(collected.context, request_set)

    def recheck() -> None:
        require(storage._collect(intake_path) == collected, "delivery_source_drift")

    return storage._publish(destination, files, collected.protected, recheck)


@dataclass(frozen=True)
class _Prepared:
    collected: storage._Collected
    request_set: RequestSet
    files: dict[str, bytes]


def _load_preparation(intake: Path, preparation: Path) -> _Prepared:
    preparation = storage._unlinked(preparation)
    collected = storage._collect(intake)
    saved = parse_request_set(storage._read(preparation / "request-set.json", MAX_BYTES))
    expected = make_request_set(
        collected.context,
        saved.payload.run_id,
        _implementation(),
        with_count=saved.payload.count_attempt_limit > 0,
    )
    require(saved == expected, "delivery_preparation_changed")
    files = _preparation_files(collected.context, expected)
    require(sum(map(len, files.values())) <= MAX_BYTES, "delivery_preparation_size")
    storage._verify_output(preparation, files, manifest=True)
    return _Prepared(collected, expected, files)


def parse_fixtures(data: bytes, request_set: RequestSet) -> TransportFixtures:
    require(len(data) <= MAX_FIXTURE_BYTES, "fixture_size")
    fixture = TransportFixtures.model_validate_json(encoded(strict_object(data.decode("utf-8"))))
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


def _durable_write(path: Path, data: bytes) -> None:
    active_secret_guard().ensure_safe(data.decode("utf-8"), destination="fixture journal")
    require(len(data) <= MAX_MEMBER_BYTES, "journal_member_size")
    with storage._unlinked(path).open("xb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())


def _read_journal(path: Path) -> dict[str, bytes]:
    path = storage._unlinked(path)
    members = list(path.iterdir())
    require(2 <= len(members) <= 51, "journal_members")
    result: dict[str, bytes] = {}
    size = 0
    for member in sorted(members):
        data = storage._read(member, min(MAX_MEMBER_BYTES, MAX_BYTES - size))
        size += len(data)
        require(size <= MAX_BYTES, "journal_size")
        result[member.name] = data
    return result


class _Journal:
    def __init__(self, path: Path, header: JournalHeader, fixture_bytes: bytes) -> None:
        self.path = path
        path.mkdir(
            parents=True, exist_ok=False
        )  # Never resume, retry or repair an existing journal.
        self.files = {
            "fixtures.json": fixture_bytes,
            "header.json": encoded(header.model_dump(mode="json")),
        }
        require(sum(map(len, self.files.values())) <= MAX_BYTES, "journal_size")
        for name, data in self.files.items():
            _durable_write(path / name, data)
        self.previous = _sha(self.files["header.json"])
        self.sequence = 0

    def append(self, payload: Intent | Outcome | Stop) -> str:
        require(_read_journal(self.path) == self.files, "journal_changed_during_capture")
        event = JournalEvent(
            contract="assessment-fixture-journal-event-1",
            sequence=self.sequence + 1,
            previous_bytes_sha256=self.previous,
            recorded_at_utc=datetime.now(UTC).isoformat(),
            payload=payload,
        )
        data = encoded(event.model_dump(mode="json"))
        require(sum(map(len, self.files.values())) + len(data) <= MAX_BYTES, "journal_size")
        name = f"event-{event.sequence:04d}.json"
        _durable_write(self.path / name, data)
        self.files[name] = data
        self.previous, self.sequence = _sha(data), event.sequence
        return self.previous


class FixtureInterrupted(BaseException):
    """Simulated process interruption leaves a durable intent without an outcome."""


class FixtureCancelled(Exception):
    """An authored cancellation during a transport callback."""


def _fixture_transport(reply: FixtureReply) -> httpx.MockTransport:
    def handle(request: httpx.Request) -> httpx.Response:
        if reply.behavior == "interrupt":
            raise FixtureInterrupted()
        if reply.behavior == "cancelled":
            raise FixtureCancelled()
        if reply.behavior == "transport_error":
            raise httpx.ConnectError("Authored fixture transport failure", request=request)
        assert reply.http_status is not None
        return httpx.Response(reply.http_status, content=reply.response_body_utf8.encode("utf-8"))

    return httpx.MockTransport(handle)


def _build_request(endpoint: Endpoint) -> httpx.Request:
    return httpx.Request(
        endpoint.method,
        endpoint.destination + endpoint.path,
        content=endpoint.body_utf8.encode("utf-8"),
    )


def _check_request(request: httpx.Request, endpoint: Endpoint) -> Endpoint:
    require(
        request.method == endpoint.method
        and str(request.url) == endpoint.destination + endpoint.path,
        "actual_destination_changed",
    )
    require(request.content == endpoint.body_utf8.encode("utf-8"), "actual_body_changed")
    require(set(request.headers) <= {"host", "content-length"}, "fixture_headers_forbidden")
    raw = request.content.decode("utf-8")
    observed = endpoint.model_copy(
        update={
            "body_utf8": raw,
            "body_bytes_sha256": text_hash(raw),
            "body_canonical_sha256": canonical_sha256(strict_object(raw)),
        }
    )
    require(observed == endpoint, "actual_body_digest_changed")
    return observed


def _interrupted(endpoint: Endpoint) -> Exchange:
    return Exchange(
        stage=endpoint.stage,
        endpoint_canonical_sha256=canonical_sha256(endpoint.model_dump(mode="json")),
        dispatched_body_bytes_sha256=endpoint.body_bytes_sha256,
        dispatched_body_canonical_sha256=endpoint.body_canonical_sha256,
        disposition="interrupted",
        observed_http_status=None,
        retained_response=None,
        retained_response_canonical_sha256=None,
        observed_raw_http_bytes_sha256=None,
        raw_http_bytes_retained=False,
        local_error_chain=(),
    )


def _capture_exchange(
    request: httpx.Request,
    endpoint: Endpoint,
    attempt_id: str,
    journal: _Journal,
    transport: httpx.MockTransport,
) -> Outcome:
    # This is the callback boundary: no httpx.Client, default transport, credentials or network.
    observed = _check_request(request, endpoint)
    intent_sha = journal.append(Intent(kind="intent", attempt_id=attempt_id, endpoint=observed))
    started = perf_counter()
    exchange = _interrupted(observed)
    try:
        response = transport.handle_request(request)
    except (httpx.TransportError, FixtureCancelled) as exc:
        disposition = "cancelled" if isinstance(exc, FixtureCancelled) else "transport_error"
        exchange = exchange.model_copy(
            update={
                "disposition": disposition,
                "local_error_chain": (
                    ErrorLink(
                        layer="client",
                        category=disposition,
                        code=None,
                        safe_message="Fixture transport ended without a response.",
                    ),
                ),
            }
        )
    else:
        exchange = exchange.model_copy(update={"observed_http_status": response.status_code})
        try:
            content = bytearray()
            for chunk in response.iter_bytes():
                require(len(content) + len(chunk) <= MAX_RESPONSE_BYTES, "response_size")
                content.extend(chunk)
            exchange = exchange.model_copy(
                update={"observed_raw_http_bytes_sha256": _sha(bytes(content))}
            )
            text = bytes(content).decode("utf-8")
            active_secret_guard().ensure_safe(text, destination="fixture response capture")
            record = RetainedResponse.model_validate_json(encoded(strict_object(text)))
            require(
                record.raw_final is None
                if endpoint.stage == "input_count"
                else record.counted_input_tokens is None,
                "response_stage_changed",
            )
            # HTTP status is observed at the boundary, never granted by response-body claims.
            record = record.model_copy(update={"http_status": response.status_code})
            exchange = exchange.model_copy(
                update={
                    "disposition": "response",
                    "retained_response": record,
                    "retained_response_canonical_sha256": canonical_sha256(
                        record.model_dump(mode="json")
                    ),
                }
            )
        except (ValueError, SecretLeakError, httpx.TransportError):
            exchange = exchange.model_copy(
                update={
                    "disposition": "capture_error",
                    "local_error_chain": (
                        ErrorLink(
                            layer="client",
                            category="unretained_response",
                            code=None,
                            safe_message=(
                                "Response was unsafe, oversized, interrupted "
                                "or outside the fixture schema."
                            ),
                        ),
                    ),
                }
            )
        finally:
            response.close()
    outcome = Outcome(
        kind="outcome",
        intent_bytes_sha256=intent_sha,
        exchange=exchange,
        active_seconds=perf_counter() - started,
    )
    journal.append(outcome)
    return outcome


def _evidence(
    manifest: RequestManifest, outcomes: list[Outcome], pending: bool = False
) -> TerminalEvidence:
    return TerminalEvidence(
        contract="assessment-fixture-terminal-evidence-1",
        origin="authored_fixture",
        request_payload_canonical_sha256=manifest.payload_canonical_sha256,
        attempt_id=manifest.payload.attempt_id,
        exchanges=tuple(o.exchange for o in outcomes),
        active_seconds=sum(o.active_seconds for o in outcomes),
        unknown_elapsed_endpoints=int(pending),
    )


def _continue(
    context: CompletionContext, manifest: RequestManifest, outcomes: list[Outcome]
) -> bool:
    latest = outcomes[-1].exchange
    if latest.stage == "input_count":
        response = latest.retained_response
        return (
            response is not None
            and response.http_status == 200
            and response.state == "complete"
            and response.counted_input_tokens is not None
            and response.raw_final is None
        )
    terminal = derive_terminal(context, manifest, manifest, _evidence(manifest, outcomes))
    return terminal.state == "bound_unassessed" and terminal.usage_state == "known"


def capture_fixtures(
    intake: Path,
    preparation: Path,
    fixture_path: Path,
    destination: Path,
    *,
    transport: httpx.MockTransport | None = None,
) -> Literal["complete", "halted", "cancelled_before_dispatch"]:
    prepared = _load_preparation(intake, preparation)
    fixture_bytes = storage._read(fixture_path, MAX_FIXTURE_BYTES)
    fixture = parse_fixtures(fixture_bytes, prepared.request_set)
    if transport is not None:
        require(isinstance(transport, httpx.MockTransport), "fixture_transport_required")
    protected = (*prepared.collected.protected, preparation, fixture_path)
    destination = storage._destination(destination, protected)
    require(not destination.exists(), "journal_already_exists_no_retry")
    require(_load_preparation(intake, preparation) == prepared, "delivery_source_drift")
    require(storage._read(fixture_path, MAX_FIXTURE_BYTES) == fixture_bytes, "fixture_changed")
    header = JournalHeader(
        contract="assessment-fixture-journal-1",
        origin="authored_fixture",
        request_set_canonical_sha256=prepared.request_set.payload_canonical_sha256,
        preparation_manifest_bytes_sha256=_sha(prepared.files["manifest.json"]),
        fixture_bytes_sha256=_sha(fixture_bytes),
        implementation_canonical_sha256=_implementation(),
        started_at_utc=datetime.now(UTC).isoformat(),
        live_calls=0,
    )
    journal = _Journal(destination, header, fixture_bytes)
    if fixture.cancel_before_dispatch:
        journal.append(Stop(kind="stop", reason="cancelled_before_dispatch"))
        return "cancelled_before_dispatch"
    replies = iter(fixture.replies)
    for manifest in prepared.request_set.payload.requests:
        outcomes: list[Outcome] = []
        for endpoint in manifest.payload.endpoints:
            reply = next(replies)
            require(_load_preparation(intake, preparation) == prepared, "delivery_source_drift")
            outcome = _capture_exchange(
                _build_request(endpoint),
                endpoint,
                manifest.payload.attempt_id,
                journal,
                transport if transport is not None else _fixture_transport(reply),
            )
            outcomes.append(outcome)
            if not _continue(prepared.collected.context, manifest, outcomes):
                journal.append(Stop(kind="stop", reason="halted"))
                return "halted"
    journal.append(Stop(kind="stop", reason="complete"))
    return "complete"


def _audit(prepared: _Prepared, files: dict[str, bytes]) -> JsonObject:
    require("header.json" in files and "fixtures.json" in files, "missing_journal_header")
    header = JournalHeader.model_validate_json(
        encoded(strict_object(files["header.json"].decode()))
    )
    request_set = prepared.request_set
    require(
        header.request_set_canonical_sha256 == request_set.payload_canonical_sha256
        and header.preparation_manifest_bytes_sha256 == _sha(prepared.files["manifest.json"])
        and header.fixture_bytes_sha256 == _sha(files["fixtures.json"])
        and header.implementation_canonical_sha256 == _implementation(),
        "journal_binding_changed",
    )
    fixture = parse_fixtures(files["fixtures.json"], request_set)
    event_names = [f"event-{i:04d}.json" for i in range(1, len(files) - 1)]
    require(set(files) == {"header.json", "fixtures.json", *event_names}, "journal_members")
    expected = [(m, e) for m in request_set.payload.requests for e in m.payload.endpoints]
    outcomes: dict[str, list[Outcome]] = {
        m.payload.attempt_id: [] for m in request_set.payload.requests
    }
    index, previous = 0, _sha(files["header.json"])
    pending: tuple[RequestManifest, Endpoint, str] | None = None
    stop: Stop | None = None
    halted = False
    for i, name in enumerate(event_names, 1):
        raw = files[name]
        event = JournalEvent.model_validate_json(encoded(strict_object(raw.decode("utf-8"))))
        require(event.sequence == i and event.previous_bytes_sha256 == previous, "journal_chain")
        previous = _sha(raw)
        require(stop is None, "event_after_stop")
        payload = event.payload
        if isinstance(payload, Intent):
            require(
                not halted
                and not fixture.cancel_before_dispatch
                and pending is None
                and index < len(expected),
                "unexpected_intent",
            )
            manifest, endpoint = expected[index]
            require(
                payload.attempt_id == manifest.payload.attempt_id and payload.endpoint == endpoint,
                "journal_intent_changed",
            )
            pending = (manifest, endpoint, previous)
            index += 1
        elif isinstance(payload, Outcome):
            require(pending is not None, "outcome_without_intent")
            assert pending is not None
            manifest, endpoint, intent_sha = pending
            require(
                payload.intent_bytes_sha256 == intent_sha
                and payload.exchange.stage == endpoint.stage,
                "outcome_intent_changed",
            )
            rows = outcomes[manifest.payload.attempt_id]
            rows.append(payload)
            # Validate observed endpoint/body/response identities, including count stops.
            derive_terminal(
                prepared.collected.context, manifest, manifest, _evidence(manifest, rows)
            )
            halted = not _continue(prepared.collected.context, manifest, rows)
            pending = None
        else:
            require(pending is None, "stop_with_pending_intent")
            reason = (
                "cancelled_before_dispatch"
                if fixture.cancel_before_dispatch
                else ("halted" if halted else "complete")
            )
            require(payload.reason == reason, "stop_reason_changed")
            require(
                halted or fixture.cancel_before_dispatch or index == len(expected),
                "early_complete_stop",
            )
            stop = payload
    pending_attempt = None
    if pending is not None:
        manifest, endpoint, intent_sha = pending
        pending_attempt = manifest.payload.attempt_id
        outcomes[pending_attempt].append(
            Outcome(
                kind="outcome",
                intent_bytes_sha256=intent_sha,
                exchange=_interrupted(endpoint),
                active_seconds=0,
            )
        )
    terminals = [
        derive_terminal(
            prepared.collected.context,
            m,
            m,
            _evidence(m, outcomes[m.payload.attempt_id], pending_attempt == m.payload.attempt_id),
        )
        for m in request_set.payload.requests
    ]
    work = prepared.collected.context.intake.pending_work
    assert work is not None
    completion = complete_work(
        work,
        tuple(t.native_receipt for t in terminals if t.native_receipt is not None),
        {m.payload.batch_id: m.payload_canonical_sha256 for m in request_set.payload.requests},
    )
    eligible = (
        stop is not None and completion.complete_delivery and completion.binding == "complete"
    )
    return strict_object(
        encoded(
            {
                "contract": "assessment-fixture-terminal-audit-1",
                "origin": "authored_fixture",
                "notice": NOTICE,
                "intake": prepared.collected.context.intake.model_dump(mode="json"),
                "source_receipt": prepared.collected.context.adapter_receipt,
                "request_set": request_set.model_dump(mode="json"),
                "terminals": [t.model_dump(mode="json") for t in terminals],
                "completion": completion.model_dump(mode="json"),
                "completion_eligible": eligible,
                "journal_closed": stop is not None,
                "stop_reason": None if stop is None else stop.reason,
                "publication_state": "bound_unassessed"
                if eligible
                else "incomplete_terminal_audit",
                "fixture_generation_attempts": sum(
                    t.generation_attempts_consumed for t in terminals
                ),
                "fixture_count_attempts": sum(t.count_attempts_consumed for t in terminals),
                "unknown_elapsed_endpoints": int(pending is not None),
                "latency_basis": "known_fixture_intervals_only_not_model_latency",
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
        ).decode("utf-8")
    )


def audit_terminal(
    intake: Path, preparation: Path, journal: Path, destination: Path
) -> Literal["created", "reused"]:
    prepared = _load_preparation(intake, preparation)
    journal_files = _read_journal(journal)
    envelope = _audit(prepared, journal_files)
    files = {
        "intake.json": prepared.collected.context.exact_intake,
        "source-receipt.json": encoded(prepared.collected.context.adapter_receipt),
        "request-set.json": prepared.files["request-set.json"],
        "journal.json": encoded(
            {name: strict_object(data.decode("utf-8")) for name, data in journal_files.items()}
        ),
        "audit.json": encoded(envelope),
        "view.md": _literal("Fixture terminal audit", envelope),
    }
    files["manifest.json"] = _publication_manifest(
        files, prepared.request_set, str(envelope["publication_state"])
    )

    def recheck() -> None:
        require(_load_preparation(intake, preparation) == prepared, "delivery_source_drift")
        require(_read_journal(journal) == journal_files, "journal_changed_during_audit")

    return storage._publish(
        destination, files, (*prepared.collected.protected, preparation, journal), recheck
    )
