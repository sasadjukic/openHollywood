"""Explicit authored-source OpenAI mapping/manifests and fixture terminal reduction; no I/O."""

from __future__ import annotations

from decimal import Decimal
from typing import Annotated, Literal
from uuid import NAMESPACE_URL, uuid5

from pydantic import Field

from open_hollywood_engine.evaluations.assessment_authored_source import (
    AuthoredPresentation,
    AuthoredSource,
    AuthoredSourcePin,
    render_presentation,
    validate_source,
)
from open_hollywood_engine.evaluations.assessment_completion import encoded
from open_hollywood_engine.evaluations.assessment_delivery import Name, Usage, unknown_usage
from open_hollywood_engine.evaluations.assessment_result import (
    AssessmentScope,
    bind_assessment_result,
    scope_for_batch,
)
from open_hollywood_engine.evaluations.assessment_work import AssessmentReceipt
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
    WireEndpoint,
    WireMapping,
    _prepare_wire,
    count_admitted,
)
from open_hollywood_engine.models.assessment_openai_manifest import (
    Exchange as Exchange,
)
from open_hollywood_engine.models.assessment_openai_manifest import (
    Settings as Settings,
)
from open_hollywood_engine.models.contracts import (
    InvocationContext,
    MessageRole,
    ModelCallBudget,
    ModelDeployment,
    ModelMessage,
    ModelRequest,
    ModelSettings,
)
from open_hollywood_engine.models.openai import _cost
from open_hollywood_engine.models.openai_catalog import OpenAIModelSpec
from open_hollywood_engine.secrets import SecretLeakGuard


class RequestPayload(Record):
    contract: Literal["assessment-openai-authored-request-1"]
    source: AuthoredSourcePin
    work_sha256: Digest
    source_receipt_canonical_sha256: Digest
    presentation: AuthoredPresentation
    settings: Settings
    endpoints: tuple[WireEndpoint, WireEndpoint]
    effective: JsonObject
    implementation_canonical_sha256: Digest
    attempt_id: Name
    budget_slot: Annotated[int, Field(ge=1, le=3)]
    retry_allowance: Literal[0]
    live_authorized: Literal[False]


class RequestManifest(Record):
    contract: Literal["assessment-openai-authored-manifest-1"]
    payload: RequestPayload
    payload_canonical_sha256: Digest


class RequestSetPayload(Record):
    contract: Literal["assessment-openai-authored-set-payload-1"]
    source_id: Name
    run_id: Name
    settings: Settings
    requests: tuple[RequestManifest, ...] = Field(min_length=3, max_length=3)
    dispatch_order: Literal["all_three_counts_before_any_generation"]
    count_attempt_limit: Literal[3]
    generation_attempt_limit: Literal[3]
    retry_limit: Literal[0]
    live_authorized: Literal[False]


class RequestSet(Record):
    contract: Literal["assessment-openai-authored-set-1"]
    payload: RequestSetPayload
    payload_canonical_sha256: Digest


class Terminal(Record):
    contract: Literal["assessment-openai-authored-terminal-1"]
    source_origin: Literal["authored_diagnostic"]
    delivery_origin: Literal["injected_fixture"]
    request_payload_canonical_sha256: Digest
    attempt_id: Name
    exchanges: tuple[Exchange, ...]
    active_seconds: float = Field(ge=0, allow_inf_nan=False)
    unknown_elapsed_endpoints: Annotated[int, Field(ge=0, le=1)]
    native_receipt: AssessmentReceipt | None
    bound_result: JsonObject | None
    usage: Usage
    budget_violations: tuple[Literal["input", "output", "context", "cost"], ...]
    accounting_hold: bool
    state: Literal["bound_unassessed", "failed", "generation_not_started"]
    model_evidence: Literal[False]
    writer_dispatch_authorized: Literal[False]


def parse_set(data: bytes) -> RequestSet:
    require(len(data) <= 64 * 1024 * 1024, "authored_openai_manifest_size")
    return RequestSet.model_validate_json(encoded(strict_object(data.decode())))


def prepare_authored_wire(
    source: AuthoredSource,
    scope: AssessmentScope,
    request: ModelRequest,
    spec: OpenAIModelSpec,
    *,
    guard: SecretLeakGuard | None = None,
) -> WireMapping:
    source = validate_source(source)
    presentation = render_presentation(source)
    require(
        [{"role": m.role.value, "content": m.content} for m in request.messages]
        == [m.model_dump(mode="json") for m in presentation.messages],
        "authored_wire_messages",
    )
    return _prepare_wire(source.work, scope, request, spec, guard=guard)


def make_request_set(
    sources: tuple[AuthoredSource, ...],
    receipts: tuple[JsonObject, ...],
    run_id: str,
    settings: Settings,
    implementation: str,
) -> RequestSet:
    sources = tuple(validate_source(s) for s in sources)
    settings = Settings.model_validate_json(settings.model_dump_json())
    require(
        tuple(s.source.family for s in sources) == ("F01", "F02", "F03"), "authored_family_coverage"
    )
    require(
        len({s.source.source_id for s in sources}) == 1
        and len({s.source.manifest_bytes_sha256 for s in sources}) == 1,
        "mixed_authored_archive",
    )
    require(len(receipts) == 3, "authored_source_receipt_coverage")
    requests = []
    for index, (source, receipt) in enumerate(zip(sources, receipts, strict=True), 1):
        require(
            receipt.get("source") == source.source.model_dump(mode="json"),
            "authored_source_receipt",
        )
        work = source.work
        presentation = render_presentation(source)
        scope = scope_for_batch(work, presentation.batch_id, "0" * 64)
        request = ModelRequest(
            provider="openai",
            deployment=ModelDeployment.CLOUD,
            model_identifier=settings.model_spec.model_identifier,
            messages=tuple(
                ModelMessage(MessageRole(m.role), m.content) for m in presentation.messages
            ),
            invocation=InvocationContext(
                "read_only_authored_assessment",
                presentation.contract,
                tuple(
                    uuid5(NAMESPACE_URL, d.identity + ":" + d.content_sha256)
                    for d in work.context.documents
                ),
            ),
            settings=ModelSettings(thinking=settings.reasoning),
            budget=ModelCallBudget(
                settings.max_input_tokens,
                settings.max_output_tokens,
                Decimal(settings.max_cost_usd),
            ),
            response_schema=presentation.response_schema,
        )
        mapping = prepare_authored_wire(source, scope, request, settings.model_spec)
        identity = canonical_sha256(
            {
                "run": run_id,
                "source": source.source.model_dump(mode="json"),
                "work": work.fingerprint,
                "settings": settings.model_dump(mode="json"),
            }
        )
        payload = RequestPayload(
            contract="assessment-openai-authored-request-1",
            source=source.source,
            work_sha256=work.fingerprint,
            source_receipt_canonical_sha256=canonical_sha256(receipt),
            presentation=presentation,
            settings=settings,
            endpoints=mapping.endpoints,
            effective=mapping.effective,
            implementation_canonical_sha256=implementation,
            attempt_id="openai-authored-" + identity,
            budget_slot=index,
            retry_allowance=0,
            live_authorized=False,
        )
        requests.append(
            RequestManifest(
                contract="assessment-openai-authored-manifest-1",
                payload=payload,
                payload_canonical_sha256=canonical_sha256(payload.model_dump(mode="json")),
            )
        )
    payload_set = RequestSetPayload(
        contract="assessment-openai-authored-set-payload-1",
        source_id=sources[0].source.source_id,
        run_id=run_id,
        settings=settings,
        requests=tuple(requests),
        dispatch_order="all_three_counts_before_any_generation",
        count_attempt_limit=3,
        generation_attempt_limit=3,
        retry_limit=0,
        live_authorized=False,
    )
    return RequestSet(
        contract="assessment-openai-authored-set-1",
        payload=payload_set,
        payload_canonical_sha256=canonical_sha256(payload_set.model_dump(mode="json")),
    )


def ordered_endpoints(plan: RequestSet) -> tuple[tuple[RequestManifest, WireEndpoint], ...]:
    return tuple((m, m.payload.endpoints[index]) for index in (0, 1) for m in plan.payload.requests)


def wire_for(manifest: RequestManifest) -> WireMapping:
    p, settings = manifest.payload, manifest.payload.settings
    return WireMapping(
        contract="assessment-openai-wire-mapping-1",
        work_sha256=p.work_sha256,
        batch_id=p.presentation.batch_id,
        active_unit_ids=p.presentation.active_unit_ids,
        native_request_sha256=manifest.payload_canonical_sha256,
        messages_canonical_sha256=p.presentation.messages_canonical_sha256,
        schema_canonical_sha256=p.presentation.schema_canonical_sha256,
        model_spec=settings.model_spec,
        endpoints=p.endpoints,
        effective=p.effective,
        max_input_tokens=settings.max_input_tokens,
        max_output_tokens=settings.max_output_tokens,
        max_cost_usd=settings.max_cost_usd,
        live_authorized=False,
    )


def derive_terminal(
    source: AuthoredSource,
    manifest: RequestManifest,
    exchanges: tuple[Exchange, ...],
    seconds: float,
    *,
    pending: bool = False,
) -> Terminal:
    """Called only after application regenerates the exact source-bound request set."""
    source = validate_source(source)
    require(manifest.payload.work_sha256 == source.work.fingerprint, "terminal_work_changed")
    require(
        manifest.payload.presentation == render_presentation(source),
        "terminal_presentation_changed",
    )
    require(
        manifest.payload_canonical_sha256
        == canonical_sha256(manifest.payload.model_dump(mode="json")),
        "request_payload_changed",
    )
    require(manifest.payload.source == source.source, "terminal_source_changed")
    require(len(exchanges) <= 2, "exchange_coverage")
    for i, exchange in enumerate(exchanges):
        e = manifest.payload.endpoints[i]
        require(
            exchange.stage == e.stage
            and exchange.endpoint_canonical_sha256 == canonical_sha256(e.model_dump(mode="json"))
            and exchange.dispatched_body_bytes_sha256 == e.body_bytes_sha256
            and exchange.dispatched_body_canonical_sha256 == e.body_canonical_sha256,
            "terminal_endpoint_changed",
        )
        response = exchange.response
        require((exchange.disposition == "response") == (response is not None), "response_presence")
        require(
            exchange.retained_response_canonical_sha256
            == (canonical_sha256(response.model_dump(mode="json")) if response else None),
            "response_hash",
        )
        if response is not None:
            require(
                response.stage == e.stage and response.http_status == exchange.observed_http_status,
                "response_stage_or_status",
            )
            if response.state == "complete":
                require(
                    response.http_status == 200
                    and response.terminal_status == "completed"
                    and response.incomplete_reason is None
                    and not response.issues
                    and not response.error_codes
                    and response.returned_model
                    in (
                        manifest.payload.settings.model_spec.model_identifier,
                        *manifest.payload.settings.model_spec.response_model_identifiers,
                    )
                    and response.raw_final is not None
                    and response.counted_input_tokens is None,
                    "inconsistent_complete_response",
                )
                assert response.raw_final is not None
                require(
                    response.raw_final_utf8_sha256 == text_hash(response.raw_final),
                    "response_final_hash",
                )
        if i == 0 and len(exchanges) == 2:
            require(
                response is not None and count_admitted(wire_for(manifest), response),
                "generation_after_count_failure",
            )
    generation = next((e for e in exchanges if e.stage == "generation"), None)
    response = generation.response if generation else None
    usage = response.usage if response else unknown_usage()
    receipt, bound = None, None
    state: Literal["bound_unassessed", "failed", "generation_not_started"] = (
        "generation_not_started"
    )
    if generation is not None:
        state = "failed"
        work = source.work
        scope = scope_for_batch(
            work, manifest.payload.presentation.batch_id, manifest.payload_canonical_sha256
        )
        status: Literal["invalid", "length", "refusal", "transport_error", "cancelled"] = "invalid"
        if generation.disposition in ("transport_error", "interrupted", "capture_error"):
            status = "transport_error"
        elif generation.disposition == "cancelled":
            status = "cancelled"
        elif response is not None and response.state in ("length", "refusal"):
            status = response.state
        receipt = AssessmentReceipt(
            work_sha256=work.fingerprint,
            batch_id=scope.batch_id,
            request_sha256=scope.request_sha256,
            attempt_id=manifest.payload.attempt_id,
            status=status,
            input_tokens=usage.input_tokens,
            output_tokens=usage.output_tokens,
            reasoning_tokens=usage.reasoning_tokens,
            active_seconds=seconds,
        )
        if (
            response is not None
            and response.state == "complete"
            and response.http_status == 200
            and response.raw_final
        ):
            candidate = receipt.model_copy(
                update={
                    "status": "valid",
                    "result_sha256": response.raw_final_utf8_sha256,
                    "assessed_unit_ids": scope.active_unit_ids,
                }
            )
            try:
                result = bind_assessment_result(work, scope, candidate, response.raw_final)
            except ValueError:
                pass
            else:
                receipt, bound, state = (
                    result.receipt,
                    result.model_dump(mode="json"),
                    "bound_unassessed",
                )
    violations: list[Literal["input", "output", "context", "cost"]] = []
    settings = manifest.payload.settings
    spec = settings.model_spec
    inputs, outputs = usage.input_tokens, usage.output_tokens
    if inputs is not None and inputs > min(settings.max_input_tokens, spec.max_input_tokens):
        violations.append("input")
    if outputs is not None and outputs > settings.max_output_tokens:
        violations.append("output")
    if inputs is not None and outputs is not None:
        if inputs + outputs > spec.context_window:
            violations.append("context")
        # Conservative local estimate, never a claim of actual billed cost.
        if _cost(spec, inputs, outputs) > Decimal(settings.max_cost_usd):
            violations.append("cost")
    return Terminal(
        contract="assessment-openai-authored-terminal-1",
        source_origin="authored_diagnostic",
        delivery_origin="injected_fixture",
        request_payload_canonical_sha256=manifest.payload_canonical_sha256,
        attempt_id=manifest.payload.attempt_id,
        exchanges=exchanges,
        active_seconds=seconds,
        unknown_elapsed_endpoints=int(pending),
        native_receipt=receipt,
        bound_result=bound,
        usage=usage,
        budget_violations=tuple(violations),
        accounting_hold=generation is not None
        and (bool(violations) or any(v is None for v in usage.model_dump().values())),
        state=state,
        model_evidence=False,
        writer_dispatch_authorized=False,
    )
