"""Version-two compact OpenAI manifests and fixture terminals; no I/O or live dispatch."""

from __future__ import annotations

from decimal import Decimal
from typing import Annotated, Literal
from uuid import NAMESPACE_URL, uuid5

from pydantic import Field

from open_hollywood_engine.evaluations.assessment_compact_presentation import (
    CompactPresentation,
    render_compact,
)
from open_hollywood_engine.evaluations.assessment_completion import (
    CompletionContext,
    SourcePin,
    encoded,
)
from open_hollywood_engine.evaluations.assessment_delivery import Name, Usage, unknown_usage
from open_hollywood_engine.evaluations.assessment_result import (
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
    count_admitted,
)
from open_hollywood_engine.models.assessment_openai_compact import prepare_compact_wire
from open_hollywood_engine.models.assessment_openai_manifest import Exchange as Exchange
from open_hollywood_engine.models.assessment_openai_manifest import Settings as Settings
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


class PresentationBinding(Record):
    contract: Literal["assessment-openai-compact-source-binding-2"]
    export_manifest_bytes_sha256: Digest
    local_provenance_bytes_sha256: Digest


class RequestPayload(Record):
    contract: Literal["assessment-openai-compact-request-2"]
    source: SourcePin
    source_receipt_canonical_sha256: Digest
    presentation: CompactPresentation
    presentation_binding: PresentationBinding
    settings: Settings
    endpoints: tuple[WireEndpoint, WireEndpoint]
    effective: JsonObject
    implementation_canonical_sha256: Digest
    attempt_id: Name
    budget_slot: Annotated[int, Field(ge=1, le=12)]
    retry_allowance: Literal[0]
    live_authorized: Literal[False]


class RequestManifest(Record):
    contract: Literal["assessment-openai-compact-manifest-2"]
    payload: RequestPayload
    payload_canonical_sha256: Digest


class RequestSetPayload(Record):
    contract: Literal["assessment-openai-compact-set-payload-2"]
    run_id: Name
    work_canonical_sha256: Digest
    settings: Settings
    presentation_binding: PresentationBinding
    requests: tuple[RequestManifest, ...] = Field(min_length=1, max_length=12)
    count_attempt_limit: Annotated[int, Field(ge=1, le=12)]
    generation_attempt_limit: Annotated[int, Field(ge=1, le=12)]
    retry_limit: Literal[0]
    live_authorized: Literal[False]


class RequestSet(Record):
    contract: Literal["assessment-openai-compact-set-2"]
    payload: RequestSetPayload
    payload_canonical_sha256: Digest


class Terminal(Record):
    contract: Literal["assessment-openai-compact-terminal-2"]
    origin: Literal["injected_fixture"]
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
    require(len(data) <= 64 * 1024 * 1024, "openai_manifest_size")
    return RequestSet.model_validate_json(encoded(strict_object(data.decode())))


def make_request_set(
    context: CompletionContext,
    run_id: str,
    settings: Settings,
    implementation: str,
    presentation_binding: PresentationBinding,
) -> RequestSet:
    settings = Settings.model_validate_json(settings.model_dump_json())
    presentation_binding = PresentationBinding.model_validate_json(
        presentation_binding.model_dump_json()
    )
    work = context.intake.pending_work
    assert work is not None
    require(1 <= len(work.context.statements) <= 12 and len(work.batches) <= 12, "work_bound")
    requests = []
    for index, batch in enumerate(work.batches, 1):
        presentation = render_compact(context, batch.batch_id).presentation
        scope = scope_for_batch(work, batch.batch_id, "0" * 64)
        request = ModelRequest(
            provider="openai",
            deployment=ModelDeployment.CLOUD,
            model_identifier=settings.model_spec.model_identifier,
            messages=tuple(
                ModelMessage(MessageRole(m.role), m.content) for m in presentation.messages
            ),
            invocation=InvocationContext(
                "read_only_compact_assessment",
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
        mapping = prepare_compact_wire(context, scope, request, settings.model_spec)
        identity = canonical_sha256(
            {
                "contract": "assessment-openai-compact-attempt-2",
                "run": run_id,
                "presentation": presentation.messages_canonical_sha256,
                "publication": presentation_binding.model_dump(mode="json"),
                "work": work.fingerprint,
                "batch": batch.batch_id,
                "settings": settings.model_dump(mode="json"),
            }
        )
        payload = RequestPayload(
            contract="assessment-openai-compact-request-2",
            source=context.pin,
            source_receipt_canonical_sha256=canonical_sha256(context.adapter_receipt),
            presentation=presentation,
            presentation_binding=presentation_binding,
            settings=settings,
            endpoints=mapping.endpoints,
            effective=mapping.effective,
            implementation_canonical_sha256=implementation,
            attempt_id="openai-compact-" + identity,
            budget_slot=index,
            retry_allowance=0,
            live_authorized=False,
        )
        requests.append(
            RequestManifest(
                contract="assessment-openai-compact-manifest-2",
                payload=payload,
                payload_canonical_sha256=canonical_sha256(payload.model_dump(mode="json")),
            )
        )
    payload_set = RequestSetPayload(
        contract="assessment-openai-compact-set-payload-2",
        run_id=run_id,
        work_canonical_sha256=work.fingerprint,
        settings=settings,
        presentation_binding=presentation_binding,
        requests=tuple(requests),
        count_attempt_limit=len(requests),
        generation_attempt_limit=len(requests),
        retry_limit=0,
        live_authorized=False,
    )
    return RequestSet(
        contract="assessment-openai-compact-set-2",
        payload=payload_set,
        payload_canonical_sha256=canonical_sha256(payload_set.model_dump(mode="json")),
    )


def wire_for(manifest: RequestManifest) -> WireMapping:
    p, settings = manifest.payload, manifest.payload.settings
    return WireMapping(
        contract="assessment-openai-wire-mapping-1",
        work_sha256=p.source.work_canonical_sha256,
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
    context: CompletionContext,
    manifest: RequestManifest,
    exchanges: tuple[Exchange, ...],
    seconds: float,
    *,
    pending: bool = False,
) -> Terminal:
    """Called only after application regenerates the exact source-bound request set."""
    require(
        manifest.payload_canonical_sha256
        == canonical_sha256(manifest.payload.model_dump(mode="json")),
        "request_payload_changed",
    )
    require(manifest.payload.source == context.pin, "terminal_source_changed")
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
        work = context.intake.pending_work
        assert work is not None
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
        contract="assessment-openai-compact-terminal-2",
        origin="injected_fixture",
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
