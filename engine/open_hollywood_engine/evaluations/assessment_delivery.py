"""Pure intake-bound fixture request and terminal contracts; no I/O or provider SDK types."""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import Field, model_validator

from open_hollywood_engine.evaluations.assessment_completion import (
    CompletionContext,
    SourcePin,
    encoded,
    expected_pin,
)
from open_hollywood_engine.evaluations.assessment_intake import compile_intake
from open_hollywood_engine.evaluations.assessment_result import (
    assessment_response_schema,
    bind_assessment_result,
    scope_for_batch,
)
from open_hollywood_engine.evaluations.assessment_work import (
    AssessmentReceipt,
    Completion,
    complete_work,
)
from open_hollywood_engine.evaluations.contracts import canonical_sha256
from open_hollywood_engine.evaluations.review_evidence import (
    Digest,
    JsonObject,
    Record,
    require,
    strict_object,
    text_hash,
)

Name = Annotated[str, Field(min_length=1, max_length=200, pattern=r"\S")]
Count = Annotated[int, Field(ge=0)]
Stage = Literal["input_count", "generation"]


class Endpoint(Record):
    stage: Stage
    method: Literal["POST"]
    # Only the synthetic, network-free transport is supported by this runtime version.
    destination: Literal["https://assessment-fixture.invalid"]
    path: Literal["/fixture/count", "/fixture/generate"]
    body_utf8: str = Field(min_length=1, max_length=16 * 1024 * 1024)
    body_bytes_sha256: Digest
    body_canonical_sha256: Digest


class RequestPayload(Record):
    contract: Literal["assessment-fixture-request-payload-1"]
    origin: Literal["authored_fixture"]
    source: SourcePin
    source_receipt_canonical_sha256: Digest
    batch_id: Name
    active_unit_ids: tuple[Name, ...] = Field(min_length=1, max_length=12)
    presentation_contract: Literal["assessment-fixture-presentation-1"]
    presentation_utf8: str = Field(min_length=1, max_length=16 * 1024 * 1024)
    presentation_bytes_sha256: Digest
    response_schema_canonical_sha256: Digest
    provider_adapter_contract: Literal["fixture-wire-1"]
    implementation_canonical_sha256: Digest
    provider: Literal["fixture"]
    model: Literal["fixture-only-no-model"]
    settings: JsonObject
    endpoints: tuple[Endpoint, ...] = Field(min_length=1, max_length=2)
    attempt_id: Name
    budget_slot: Annotated[int, Field(ge=1, le=12)]
    generation_allowance: Literal[1]
    retry_allowance: Literal[0]
    # Mechanical allowance is not authorization to contact a provider.
    live_authorized: Literal[False]


class RequestManifest(Record):
    contract: Literal["assessment-fixture-request-manifest-1"]
    payload: RequestPayload
    payload_canonical_sha256: Digest


class RequestSetPayload(Record):
    contract: Literal["assessment-fixture-request-set-payload-1"]
    origin: Literal["authored_fixture"]
    run_id: Name
    work_canonical_sha256: Digest
    requests: tuple[RequestManifest, ...] = Field(min_length=1, max_length=12)
    generation_attempt_limit: Annotated[int, Field(ge=1, le=12)]
    count_attempt_limit: Annotated[int, Field(ge=0, le=12)]
    retry_limit: Literal[0]
    live_authorized: Literal[False]


class RequestSet(Record):
    contract: Literal["assessment-fixture-request-set-1"]
    payload: RequestSetPayload
    payload_canonical_sha256: Digest


class Usage(Record):
    input_tokens: Count | None
    output_tokens: Count | None
    reasoning_tokens: Count | None
    cached_input_tokens: Count | None

    @model_validator(mode="after")
    def bounds(self) -> Usage:
        if self.reasoning_tokens is not None:
            require(
                self.output_tokens is not None and self.reasoning_tokens <= self.output_tokens,
                "reasoning_usage_inconsistent",
            )
        if self.cached_input_tokens is not None:
            require(
                self.input_tokens is not None and self.cached_input_tokens <= self.input_tokens,
                "cached_usage_inconsistent",
            )
        return self


class ErrorLink(Record):
    layer: Literal["client", "daemon", "gateway", "provider"]
    category: Name
    code: Name | None
    # Sanitized by a future qualified adapter, never an exception/header dump.
    safe_message: str = Field(max_length=1200)


class RetainedResponse(Record):
    contract: Literal["assessment-fixture-safe-response-1"]
    http_status: Annotated[int, Field(ge=100, le=599)]
    state: Literal["complete", "length", "refusal", "error", "unrecognized"]
    response_id: Name | None
    returned_model: Name | None
    finish_reason: Name | None
    raw_final: str | None = Field(max_length=64_000)
    usage: Usage
    counted_input_tokens: Count | None
    error_chain: tuple[ErrorLink, ...] = Field(max_length=8)
    # No arbitrary fields, headers, credentials or reasoning text.


class Exchange(Record):
    stage: Stage
    endpoint_canonical_sha256: Digest
    dispatched_body_bytes_sha256: Digest
    dispatched_body_canonical_sha256: Digest
    # Persist intent before send. Intent without response might have reached the provider.
    disposition: Literal["response", "interrupted", "transport_error", "cancelled", "capture_error"]
    observed_http_status: Annotated[int, Field(ge=100, le=599)] | None
    retained_response: RetainedResponse | None
    retained_response_canonical_sha256: Digest | None
    observed_raw_http_bytes_sha256: Digest | None
    raw_http_bytes_retained: Literal[False]
    local_error_chain: tuple[ErrorLink, ...] = Field(max_length=8)


class TerminalEvidence(Record):
    contract: Literal["assessment-fixture-terminal-evidence-1"]
    origin: Literal["authored_fixture"]
    request_payload_canonical_sha256: Digest
    attempt_id: Name
    # Zero exchanges is cancelled before dispatch, not proof of provider success.
    exchanges: tuple[Exchange, ...] = Field(max_length=2)
    active_seconds: float = Field(ge=0, allow_inf_nan=False)
    unknown_elapsed_endpoints: Annotated[int, Field(ge=0, le=2)]


class TerminalReceipt(Record):
    contract: Literal["assessment-fixture-terminal-receipt-1"]
    evidence: TerminalEvidence
    terminal_evidence_canonical_sha256: Digest
    state: Literal["bound_unassessed", "failed", "generation_not_started"]
    failure_code: str | None
    generation_attempts_consumed: Literal[0, 1]
    count_attempts_consumed: Literal[0, 1]
    generation_usage: Usage
    usage_state: Literal["known", "partial", "unknown", "not_dispatched"]
    raw_final_utf8_sha256: Digest | None
    native_receipt: AssessmentReceipt | None
    bound_result: JsonObject | None
    next_dispatch_allowed: Literal[False]
    model_evidence: Literal[False]
    delivery_authentication: Literal["authored_fixture_only"]
    usage_applicability: Literal["authored_transport_fixture_not_billing"]
    actual_billed_cost: None
    factual_support: Literal["unassessed"]
    evidence_adequacy: Literal["unassessed"]
    editorial_effect: Literal["unassessed"]
    edit_necessity: Literal["unassessed"]
    craft: Literal["unassessed"]
    writer_dispatch_authorized: Literal[False]


def parse_manifest(data: bytes) -> RequestManifest:
    require(len(data) <= 64 * 1024 * 1024, "manifest_too_large")
    return RequestManifest.model_validate_json(encoded(strict_object(data.decode("utf-8"))))


def parse_terminal(data: bytes) -> TerminalEvidence:
    require(len(data) <= 1024 * 1024, "terminal_too_large")
    return TerminalEvidence.model_validate_json(encoded(strict_object(data.decode("utf-8"))))


def parse_request_set(data: bytes) -> RequestSet:
    require(len(data) <= 64 * 1024 * 1024, "request_set_too_large")
    return RequestSet.model_validate_json(encoded(strict_object(data.decode("utf-8"))))


def unknown_usage() -> Usage:
    return Usage(
        input_tokens=None, output_tokens=None, reasoning_tokens=None, cached_input_tokens=None
    )


def presentation(context: CompletionContext, batch_id: str) -> str:
    intake = context.intake
    require(intake == compile_intake(intake.source, intake.plan), "intake_changed")
    require(
        expected_pin(intake, context.exact_manifest, context.exact_intake) == context.pin,
        "source_pins_changed",
    )
    require(
        intake.model_dump(mode="json") == strict_object(context.exact_intake.decode()),
        "intake_snapshot_changed",
    )
    work = intake.pending_work
    assert work is not None and intake.declarations is not None and intake.briefs is not None
    scope = scope_for_batch(work, batch_id, "0" * 64)
    return encoded(
        {
            "contract": "assessment-fixture-presentation-1",
            "notice": (
                "TRANSPORT FIXTURE. No production prompt, provider request or inference authorized."
            ),
            "work": work.model_dump(mode="json"),
            "declarations": intake.declarations.model_dump(mode="json"),
            "briefs": intake.briefs.model_dump(mode="json"),
            "batch_id": batch_id,
            "active_unit_ids": list(scope.active_unit_ids),
            "response_schema": assessment_response_schema(work, scope),
        }
    ).decode("utf-8")


def make_manifest(
    context: CompletionContext,
    batch_id: str,
    attempt_id: str,
    implementation_sha: str,
    *,
    with_count: bool = True,
) -> RequestManifest:
    content = presentation(context, batch_id)
    packet = strict_object(content)
    work = context.intake.pending_work
    assert work is not None
    scope = scope_for_batch(work, batch_id, "0" * 64)
    settings: JsonObject = {"output_token_limit": 32000, "stream": False, "store": False}
    endpoints = []
    stages: tuple[Stage, ...] = ("input_count", "generation") if with_count else ("generation",)
    for stage in stages:
        body: JsonObject = {
            "model": "fixture-only-no-model",
            "input": content,
            "response_schema": packet["response_schema"],
        }
        if stage == "generation":
            body["settings"] = settings
        raw = encoded(body).decode("utf-8")
        endpoints.append(
            Endpoint(
                stage=stage,
                method="POST",
                destination="https://assessment-fixture.invalid",
                path="/fixture/count" if stage == "input_count" else "/fixture/generate",
                body_utf8=raw,
                body_bytes_sha256=text_hash(raw),
                body_canonical_sha256=canonical_sha256(body),
            )
        )
    payload = RequestPayload(
        contract="assessment-fixture-request-payload-1",
        origin="authored_fixture",
        source=context.pin,
        source_receipt_canonical_sha256=canonical_sha256(context.adapter_receipt),
        batch_id=batch_id,
        active_unit_ids=scope.active_unit_ids,
        presentation_contract="assessment-fixture-presentation-1",
        presentation_utf8=content,
        presentation_bytes_sha256=text_hash(content),
        response_schema_canonical_sha256=canonical_sha256(packet["response_schema"]),
        provider_adapter_contract="fixture-wire-1",
        implementation_canonical_sha256=implementation_sha,
        provider="fixture",
        model="fixture-only-no-model",
        settings=settings,
        endpoints=tuple(endpoints),
        attempt_id=attempt_id,
        budget_slot=next(i for i, b in enumerate(work.batches, 1) if b.batch_id == batch_id),
        generation_allowance=1,
        retry_allowance=0,
        live_authorized=False,
    )
    return RequestManifest(
        contract="assessment-fixture-request-manifest-1",
        payload=payload,
        payload_canonical_sha256=canonical_sha256(payload.model_dump(mode="json")),
    )


def validate_manifest(
    context: CompletionContext, candidate: RequestManifest, frozen: RequestManifest
) -> None:
    candidate = parse_manifest(encoded(candidate.model_dump(mode="json")))
    regenerated = make_manifest(
        context,
        frozen.payload.batch_id,
        frozen.payload.attempt_id,
        frozen.payload.implementation_canonical_sha256,
        with_count=len(frozen.payload.endpoints) == 2,
    )
    require(candidate == frozen == regenerated, "manifest_source_or_request_changed")


def make_request_set(
    context: CompletionContext, run_id: str, implementation_sha: str, *, with_count: bool = True
) -> RequestSet:
    work = context.intake.pending_work
    require(work is not None, "no_pending_work")
    assert work is not None
    require(1 <= len(work.context.statements) <= 12 and len(work.batches) <= 12, "work_bound")
    requests = tuple(
        make_manifest(
            context,
            batch.batch_id,
            "fixture-"
            + canonical_sha256({"run": run_id, "work": work.fingerprint, "batch": batch.batch_id})[
                :24
            ],
            implementation_sha,
            with_count=with_count,
        )
        for batch in work.batches
    )
    payload = RequestSetPayload(
        contract="assessment-fixture-request-set-payload-1",
        origin="authored_fixture",
        run_id=run_id,
        work_canonical_sha256=work.fingerprint,
        requests=requests,
        generation_attempt_limit=len(requests),
        count_attempt_limit=len(requests) if with_count else 0,
        retry_limit=0,
        live_authorized=False,
    )
    result = RequestSet(
        contract="assessment-fixture-request-set-1",
        payload=payload,
        payload_canonical_sha256=canonical_sha256(payload.model_dump(mode="json")),
    )
    parse_request_set(encoded(result.model_dump(mode="json")))
    return result


def derive_terminal(
    context: CompletionContext,
    manifest: RequestManifest,
    frozen: RequestManifest,
    evidence: TerminalEvidence,
) -> TerminalReceipt:
    """Fixture derivation. A frozen argument is not an external authentication root."""
    validate_manifest(context, manifest, frozen)
    evidence = parse_terminal(encoded(evidence.model_dump(mode="json")))
    digest = manifest.payload_canonical_sha256
    require(evidence.request_payload_canonical_sha256 == digest, "wrong_manifest_namespace")
    require(evidence.attempt_id == manifest.payload.attempt_id, "wrong_attempt")
    endpoints = manifest.payload.endpoints
    require(len(evidence.exchanges) <= len(endpoints), "extra_exchange")
    for index, exchange in enumerate(evidence.exchanges):
        endpoint = endpoints[index]
        require(exchange.stage == endpoint.stage, "endpoint_order_or_duplicate")
        require(
            exchange.endpoint_canonical_sha256 == canonical_sha256(endpoint.model_dump(mode="json"))
            and exchange.dispatched_body_bytes_sha256 == endpoint.body_bytes_sha256
            and exchange.dispatched_body_canonical_sha256 == endpoint.body_canonical_sha256,
            "dispatch_body_or_endpoint_changed",
        )
        response = exchange.retained_response
        require((exchange.disposition == "response") == (response is not None), "response_presence")
        require(
            exchange.retained_response_canonical_sha256
            == (canonical_sha256(response.model_dump(mode="json")) if response else None),
            "retained_response_changed",
        )
        if response is not None:
            require(response.http_status == exchange.observed_http_status, "http_status_changed")
            if response.raw_final is not None:
                require(len(response.raw_final.encode("utf-8")) <= 256000, "final_byte_bound")
        if endpoint.stage == "input_count":
            require(response is None or response.raw_final is None, "count_has_final")
            if index + 1 < len(evidence.exchanges):
                require(
                    response is not None
                    and response.http_status == 200
                    and response.state == "complete"
                    and response.counted_input_tokens is not None,
                    "generation_after_failed_count",
                )
        elif response is not None:
            require(response.counted_input_tokens is None, "generation_has_count")
    generation = next((e for e in evidence.exchanges if e.stage == "generation"), None)
    response = generation.retained_response if generation is not None else None
    usage = response.usage if response is not None else unknown_usage()
    raw = response.raw_final if response is not None else None
    state: Literal["bound_unassessed", "failed", "generation_not_started"] = (
        "generation_not_started"
    )
    failure: str | None = "generation_not_started"
    if generation is None and evidence.exchanges:
        failure = "generation_not_started_after_count"
    receipt = None
    bound: JsonObject | None = None
    if generation is not None:
        state = "failed"
        status: Literal["valid", "invalid", "length", "refusal", "transport_error", "cancelled"]
        status = "transport_error"
        failure = generation.disposition
        if generation.disposition == "cancelled":
            status = "cancelled"
        if response is not None:
            failure = response.state
            if response.http_status != 200:
                failure = "non_200"
            elif response.state in ("length", "refusal"):
                status = response.state
            elif response.state == "complete":
                status = "invalid"
                failure = "empty_final" if not raw else "native_binding_failed"
        work = context.intake.pending_work
        assert work is not None
        receipt = AssessmentReceipt(
            work_sha256=work.fingerprint,
            batch_id=manifest.payload.batch_id,
            request_sha256=digest,
            attempt_id=evidence.attempt_id,
            status=status,
            input_tokens=usage.input_tokens,
            output_tokens=usage.output_tokens,
            reasoning_tokens=usage.reasoning_tokens,
            active_seconds=evidence.active_seconds,
        )
        if (
            response is not None
            and response.http_status == 200
            and response.state == "complete"
            and response.returned_model != manifest.payload.model
        ):
            failure = "unexpected_returned_model"
        if (
            response is not None
            and response.http_status == 200
            and response.state == "complete"
            and response.returned_model == manifest.payload.model
            and raw
        ):
            scope = scope_for_batch(work, manifest.payload.batch_id, digest)
            provisional = receipt.model_copy(
                update={
                    "status": "valid",
                    "result_sha256": text_hash(raw),
                    "assessed_unit_ids": scope.active_unit_ids,
                }
            )
            try:
                result = bind_assessment_result(work, scope, provisional, raw)
            except ValueError:
                pass  # Keep exact final and failure; never salvage successful slots.
            else:
                receipt = result.receipt
                bound = result.model_dump(mode="json")
                state, failure = "bound_unassessed", None
    usage_state: Literal["known", "partial", "unknown", "not_dispatched"]
    if generation is None:
        usage_state = "not_dispatched"
    elif usage.input_tokens is not None and usage.output_tokens is not None:
        usage_state = "known"
    elif any(v is not None for v in usage.model_dump().values()):
        usage_state = "partial"
    else:
        usage_state = "unknown"
    return TerminalReceipt(
        contract="assessment-fixture-terminal-receipt-1",
        evidence=evidence,
        terminal_evidence_canonical_sha256=canonical_sha256(evidence.model_dump(mode="json")),
        state=state,
        failure_code=failure,
        generation_attempts_consumed=0 if generation is None else 1,
        count_attempts_consumed=1
        if any(e.stage == "input_count" for e in evidence.exchanges)
        else 0,
        generation_usage=usage,
        usage_state=usage_state,
        raw_final_utf8_sha256=None if raw is None else text_hash(raw),
        native_receipt=receipt,
        bound_result=bound,
        next_dispatch_allowed=False,
        model_evidence=False,
        delivery_authentication="authored_fixture_only",
        usage_applicability="authored_transport_fixture_not_billing",
        actual_billed_cost=None,
        factual_support="unassessed",
        evidence_adequacy="unassessed",
        editorial_effect="unassessed",
        edit_necessity="unassessed",
        craft="unassessed",
        writer_dispatch_authorized=False,
    )


def complete_terminals(
    context: CompletionContext,
    frozen: tuple[RequestManifest, ...],
    evidence: tuple[TerminalEvidence, ...],
) -> Completion:
    """All original batches exactly once; terminal coverage is not successful coverage."""
    work = context.intake.pending_work
    assert work is not None
    require(len(frozen) == len(work.batches) <= 12, "manifest_batch_coverage")
    require(
        {m.payload.batch_id for m in frozen} == {b.batch_id for b in work.batches},
        "manifest_batch_coverage",
    )
    require(len({m.payload.attempt_id for m in frozen}) == len(frozen), "duplicate_attempt")
    require(len(evidence) == len(frozen), "terminal_coverage")
    require(len({e.attempt_id for e in evidence}) == len(evidence), "duplicate_terminal")
    by_attempt = {e.attempt_id: e for e in evidence}
    require(set(by_attempt) == {m.payload.attempt_id for m in frozen}, "terminal_attempt_coverage")
    terminals = [derive_terminal(context, m, m, by_attempt[m.payload.attempt_id]) for m in frozen]
    return complete_work(
        work,
        tuple(t.native_receipt for t in terminals if t.native_receipt is not None),
        {m.payload.batch_id: m.payload_canonical_sha256 for m in frozen},
    )
