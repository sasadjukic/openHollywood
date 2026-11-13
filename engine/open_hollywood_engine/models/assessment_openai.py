"""Offline qualification of assessment wire mapping; no client or live dispatch path."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Annotated, Literal

import httpx
from pydantic import Field

from open_hollywood_engine.evaluations.assessment_completion import CompletionContext, encoded
from open_hollywood_engine.evaluations.assessment_delivery import Stage, Usage, unknown_usage
from open_hollywood_engine.evaluations.assessment_presentation import render_presentation
from open_hollywood_engine.evaluations.assessment_result import (
    AssessmentScope,
    assessment_response_schema,
    scope_for_batch,
)
from open_hollywood_engine.evaluations.assessment_work import AssessmentWork
from open_hollywood_engine.evaluations.contracts import canonical_sha256
from open_hollywood_engine.evaluations.review_evidence import (
    Digest,
    JsonObject,
    Record,
    require,
    strict_object,
    text_hash,
)
from open_hollywood_engine.models.contracts import ModelDeployment, ModelRequest
from open_hollywood_engine.models.openai import _cost, render_responses_body
from open_hollywood_engine.models.openai_catalog import OpenAIModelSpec
from open_hollywood_engine.secrets import SecretLeakError, SecretLeakGuard

MAX_RESPONSE_BYTES = 1024 * 1024
MAX_REQUEST_BYTES = 16 * 1024 * 1024
SafeName = Annotated[str, Field(pattern=r"^[a-zA-Z0-9][a-zA-Z0-9._:-]{0,199}$")]


class WireEndpoint(Record):
    stage: Stage
    method: Literal["POST"]
    destination: Literal["https://api.openai.com"]
    path: Literal["/v1/responses", "/v1/responses/input_tokens"]
    body_utf8: str
    body_bytes_sha256: Digest
    body_canonical_sha256: Digest


class WireMapping(Record):
    contract: Literal["assessment-openai-wire-mapping-1"]
    work_sha256: Digest
    batch_id: str
    active_unit_ids: tuple[str, ...]
    # Preserve the caller's qualified scope; never replace it with a wire-body hash.
    native_request_sha256: Digest
    messages_canonical_sha256: Digest
    schema_canonical_sha256: Digest
    model_spec: OpenAIModelSpec
    endpoints: tuple[WireEndpoint, WireEndpoint]
    effective: JsonObject
    max_input_tokens: int
    max_output_tokens: int
    max_cost_usd: str
    live_authorized: Literal[False]


class MappedResponse(Record):
    contract: Literal["assessment-openai-mapped-response-1"]
    stage: Stage
    http_status: Annotated[int, Field(ge=100, le=599)]
    state: Literal["counted", "complete", "length", "refusal", "error", "invalid"]
    response_id: SafeName | None
    returned_model: SafeName | None
    terminal_status: str | None
    incomplete_reason: str | None
    raw_final: str | None = Field(max_length=64_000)
    raw_final_utf8_sha256: Digest | None
    usage: Usage
    counted_input_tokens: int | None
    issues: tuple[str, ...]
    error_codes: tuple[str, ...]
    actual_billed_cost: None
    authentication: Literal["mapping_only_not_delivery_authentication"]
    writer_dispatch_authorized: Literal[False]


def prepare_wire(
    work: AssessmentWork,
    scope: AssessmentScope,
    request: ModelRequest,
    spec: OpenAIModelSpec,
    *,
    guard: SecretLeakGuard | None = None,
) -> WireMapping:
    """Map an already prepared assessment presentation; never construct/alter its prompt."""
    messages = [{"role": m.role.value, "content": m.content} for m in request.messages]
    require(messages == [m.model_dump(mode="json") for m in work.context.messages], "wire_messages")
    return _prepare_wire(work, scope, request, spec, guard=guard)


def prepare_intake_wire(
    context: CompletionContext,
    scope: AssessmentScope,
    request: ModelRequest,
    spec: OpenAIModelSpec,
    *,
    guard: SecretLeakGuard | None = None,
) -> WireMapping:
    """New presentation over original native work; never replace its historical messages."""
    presentation = render_presentation(context, scope.batch_id)
    require(
        [{"role": m.role.value, "content": m.content} for m in request.messages]
        == [m.model_dump(mode="json") for m in presentation.messages],
        "intake_wire_messages",
    )
    work = context.intake.pending_work
    assert work is not None
    return _prepare_wire(work, scope, request, spec, guard=guard)


def _prepare_wire(
    work: AssessmentWork,
    scope: AssessmentScope,
    request: ModelRequest,
    spec: OpenAIModelSpec,
    *,
    guard: SecretLeakGuard | None,
) -> WireMapping:
    require(scope == scope_for_batch(work, scope.batch_id, scope.request_sha256), "wire_scope")
    require(
        request.provider == "openai" and request.deployment == ModelDeployment.CLOUD,
        "wire_provider",
    )
    require(request.model_identifier == spec.model_identifier, "wire_model")
    messages = [{"role": m.role.value, "content": m.content} for m in request.messages]
    schema = strict_object(encoded(assessment_response_schema(work, scope)).decode())
    require(request.response_schema is not None, "wire_schema")
    require(
        canonical_sha256(dict(request.response_schema or {})) == canonical_sha256(schema),
        "wire_schema",
    )
    require(request.budget.max_output_tokens <= spec.max_output_tokens, "wire_output_budget")
    require(
        _cost(spec, 0, request.budget.max_output_tokens) <= request.budget.max_cost_usd,
        "wire_cost_budget",
    )
    body, effective = render_responses_body(request, spec)
    (guard or SecretLeakGuard()).ensure_safe(body, destination="offline assessment wire")
    count = {k: v for k, v in body.items() if k in ("model", "input", "text", "reasoning")}
    endpoints = []
    for stage, path, value in (
        ("input_count", "/v1/responses/input_tokens", count),
        ("generation", "/v1/responses", body),
    ):
        data = encoded(value)
        require(len(data) <= MAX_REQUEST_BYTES, "wire_size")
        endpoints.append(
            WireEndpoint.model_validate(
                {
                    "stage": stage,
                    "method": "POST",
                    "destination": "https://api.openai.com",
                    "path": path,
                    "body_utf8": data.decode(),
                    "body_bytes_sha256": hashlib.sha256(data).hexdigest(),
                    "body_canonical_sha256": canonical_sha256(value),
                }
            )
        )
    return WireMapping(
        contract="assessment-openai-wire-mapping-1",
        work_sha256=work.fingerprint,
        batch_id=scope.batch_id,
        active_unit_ids=scope.active_unit_ids,
        native_request_sha256=scope.request_sha256,
        messages_canonical_sha256=canonical_sha256(messages),
        schema_canonical_sha256=canonical_sha256(schema),
        model_spec=spec,
        endpoints=(endpoints[0], endpoints[1]),
        effective=effective,
        max_input_tokens=request.budget.max_input_tokens,
        max_output_tokens=request.budget.max_output_tokens,
        max_cost_usd=str(request.budget.max_cost_usd),
        live_authorized=False,
    )


def check_outgoing(endpoint: WireEndpoint, request: httpx.Request) -> None:
    """Check actual bytes, method and URL before invoking a mock; admit no credentials."""
    raw = request.content
    require(request.method == endpoint.method, "wire_method")
    require(str(request.url) == endpoint.destination + endpoint.path, "wire_destination")
    require(set(request.headers) <= {"host", "content-length", "content-type"}, "wire_headers")
    require(request.headers.get("host") == "api.openai.com", "wire_host")
    require(request.headers.get("content-type") in (None, "application/json"), "wire_content_type")
    require(request.headers.get("content-length") == str(len(raw)), "wire_content_length")
    require(raw == endpoint.body_utf8.encode(), "wire_bytes")
    require(hashlib.sha256(raw).hexdigest() == endpoint.body_bytes_sha256, "wire_byte_hash")
    require(
        canonical_sha256(strict_object(raw.decode())) == endpoint.body_canonical_sha256,
        "wire_canonical_hash",
    )


def _counter(value: object, label: str, issues: list[str]) -> int | None:
    if value is None:
        return None
    if type(value) is not int or value < 0:
        issues.append("invalid_" + label)
        return None
    return value


def _usage(payload: JsonObject, issues: list[str]) -> Usage:
    raw = payload.get("usage")
    if raw is None:
        return unknown_usage()
    if not isinstance(raw, dict):
        issues.append("invalid_usage")
        return unknown_usage()
    inputs = _counter(raw.get("input_tokens"), "input_tokens", issues)
    outputs = _counter(raw.get("output_tokens"), "output_tokens", issues)
    details = []
    for key, child in (
        ("input_tokens_details", "cached_tokens"),
        ("output_tokens_details", "reasoning_tokens"),
    ):
        item = raw.get(key)
        if item is not None and not isinstance(item, dict):
            issues.append("invalid_" + key)
        details.append(_counter(item.get(child), child, issues) if isinstance(item, dict) else None)
    cached, reasoning = details
    if cached is not None and (inputs is None or cached > inputs):
        issues.append("inconsistent_cached_tokens")
        cached = None
    if reasoning is not None and (outputs is None or reasoning > outputs):
        issues.append("inconsistent_reasoning_tokens")
        reasoning = None
    total = _counter(raw.get("total_tokens"), "total_tokens", issues)
    if (
        total is not None
        and inputs is not None
        and outputs is not None
        and total != inputs + outputs
    ):
        issues.append("inconsistent_total_tokens")
    return Usage(
        input_tokens=inputs,
        output_tokens=outputs,
        reasoning_tokens=reasoning,
        cached_input_tokens=cached,
    )


def map_response(
    stage: Stage,
    http_status: int,
    body: bytes,
    spec: OpenAIModelSpec,
    *,
    guard: SecretLeakGuard | None = None,
) -> MappedResponse:
    """Normalize bounded observed bytes. No repairs, message concatenation or invented usage."""
    result = MappedResponse(
        contract="assessment-openai-mapped-response-1",
        stage=stage,
        http_status=http_status,
        state="invalid",
        response_id=None,
        returned_model=None,
        terminal_status=None,
        incomplete_reason=None,
        raw_final=None,
        raw_final_utf8_sha256=None,
        usage=unknown_usage(),
        counted_input_tokens=None,
        issues=(),
        error_codes=(),
        actual_billed_cost=None,
        authentication="mapping_only_not_delivery_authentication",
        writer_dispatch_authorized=False,
    )
    issues: list[str] = []
    try:
        require(len(body) <= MAX_RESPONSE_BYTES, "response_size")
        payload = strict_object(body.decode("utf-8"))
        (guard or SecretLeakGuard()).ensure_safe(payload, destination="offline mapped response")
    except (ValueError, SecretLeakError, RecursionError):
        return result.model_copy(update={"issues": ("unsafe_or_invalid_body",)})
    usage = _usage(payload, issues) if stage == "generation" else unknown_usage()
    metadata: dict[str, object] = {"usage": usage}
    for source, target in (("id", "response_id"), ("model", "returned_model")):
        value = payload.get(source)
        if value is not None:
            try:
                candidate = result.model_dump() | {target: value}
                metadata[target] = getattr(MappedResponse.model_validate(candidate), target)
            except ValueError:
                issues.append("invalid_" + source)
    status = payload.get("status")
    if status in ("completed", "incomplete", "failed", "cancelled", "queued", "in_progress"):
        metadata["terminal_status"] = status
    detail = payload.get("incomplete_details")
    reason = detail.get("reason") if isinstance(detail, dict) else None
    if reason in ("max_output_tokens", "content_filter"):
        metadata["incomplete_reason"] = reason
    if http_status != 200 or payload.get("error") is not None:
        error = payload.get("error")
        code = error.get("code") if isinstance(error, dict) else None
        allowed = {
            "insufficient_quota",
            "rate_limit_exceeded",
            "server_error",
            "invalid_api_key",
            "model_not_found",
            "billing_hard_limit_reached",
        }
        metadata.update(
            state="error",
            error_codes=(
                f"http_{http_status}",
                code if isinstance(code, str) and code in allowed else "provider_error",
            ),
        )
    elif stage == "input_count":
        count = _counter(payload.get("input_tokens"), "counted_input_tokens", issues)
        if count is None:
            issues.append("missing_count")
        if payload.get("object") not in (None, "response.input_tokens"):
            issues.append("invalid_count_object")
        metadata.update(counted_input_tokens=count, state="counted" if not issues else "invalid")
    else:
        if metadata.get("returned_model") not in (
            spec.model_identifier,
            *spec.response_model_identifiers,
        ):
            issues.append("model_mismatch")
        output = payload.get("output")
        messages: list[JsonObject] = []
        if not isinstance(output, list):
            issues.append("invalid_output")
        else:
            for item in output:
                if not isinstance(item, dict):
                    issues.append("invalid_output_item")
                elif item.get("type") == "message":
                    messages.append(item)
                elif item.get("type") != "reasoning":
                    issues.append("unexpected_output_item")
        texts: list[str] = []
        refused = False
        if len(messages) != 1:
            issues.append("message_cardinality")
        for message in messages:
            if message.get("role") != "assistant" or message.get("phase") not in (
                None,
                "final_answer",
            ):
                issues.append("invalid_message_role_or_phase")
            if message.get("status") != "completed":
                issues.append("incomplete_message")
            content = message.get("content")
            if not isinstance(content, list):
                issues.append("invalid_content")
                continue
            for part in content:
                if not isinstance(part, dict):
                    issues.append("invalid_content_part")
                elif part.get("type") == "refusal":
                    refused = True
                elif part.get("type") == "output_text" and isinstance(part.get("text"), str):
                    text = part["text"]
                    assert isinstance(text, str)
                    texts.append(text)
                else:
                    issues.append("unexpected_content_part")
        if len(texts) == 1 and len(messages) == 1:
            raw = texts[0]
            try:
                raw_bytes = raw.encode("utf-8")
            except UnicodeEncodeError:
                issues.append("invalid_final_unicode")
            else:
                if len(raw) <= 64_000 and len(raw_bytes) <= 256_000:
                    metadata.update(raw_final=raw, raw_final_utf8_sha256=text_hash(raw))
                else:
                    issues.append("final_size")
        if refused or reason == "content_filter":
            metadata["state"] = "refusal"
        elif status == "incomplete" and reason == "max_output_tokens":
            metadata["state"] = "length"
        elif status in ("failed", "cancelled"):
            metadata["state"] = "error"
        elif status != "completed" or detail is not None:
            issues.append("invalid_terminal_state")
        elif len(texts) != 1 or not texts[0].strip():
            issues.append("empty_or_ambiguous_final")
        elif not issues:
            metadata["state"] = "complete"
    metadata["issues"] = tuple(dict.fromkeys(issues))
    return MappedResponse.model_validate(result.model_dump() | metadata)


def count_admitted(mapping: WireMapping, response: MappedResponse) -> bool:
    from decimal import Decimal

    count, spec = response.counted_input_tokens, mapping.model_spec
    return (
        response.stage == "input_count"
        and response.http_status == 200
        and response.state == "counted"
        and not response.issues
        and not response.error_codes
        and response.raw_final is None
        and count is not None
        and count <= min(mapping.max_input_tokens, spec.max_input_tokens)
        and count + mapping.max_output_tokens <= spec.context_window
        and _cost(spec, count, mapping.max_output_tokens) <= Decimal(mapping.max_cost_usd)
    )


@dataclass(frozen=True)
class FixtureObservation:
    endpoint: WireEndpoint
    disposition: str
    response: MappedResponse | None
    observed_body_bytes_sha256: str | None
    # This digest is of supplied/replayed fixture bytes, never of missing historical HTTP bytes.
    origin: Literal["injected_fixture"] = "injected_fixture"


class OfflineReplay:
    """One-shot in-memory qualification only; the durable journal remains a separate boundary."""

    def __init__(
        self,
        mapping: WireMapping,
        expected: WireMapping,
        transport: httpx.MockTransport,
        *,
        guard: SecretLeakGuard | None = None,
    ) -> None:
        require(type(transport) is httpx.MockTransport, "mock_transport_required")
        require(mapping == expected, "wire_mapping_changed")
        self.mapping, self.transport = mapping, transport
        self.guard = guard or SecretLeakGuard()
        self.observations: list[FixtureObservation] = []
        self.used = False

    def run(self, *, cancelled: bool = False) -> tuple[FixtureObservation, ...]:
        require(not self.used, "fixture_replay_already_used")
        self.used = True
        if cancelled:
            return ()
        for endpoint in self.mapping.endpoints:
            request = httpx.Request(
                "POST",
                endpoint.destination + endpoint.path,
                content=endpoint.body_utf8.encode(),
                headers={"Content-Type": "application/json"},
            )
            check_outgoing(endpoint, request)
            self.observations.append(FixtureObservation(endpoint, "intent_unknown", None, None))
            try:
                response = self.transport.handle_request(request)
                try:
                    chunks = bytearray()
                    for chunk in response.iter_bytes():
                        chunks.extend(chunk)
                        require(len(chunks) <= MAX_RESPONSE_BYTES, "response_size")
                    body = bytes(chunks)
                    mapped = map_response(
                        endpoint.stage,
                        response.status_code,
                        body,
                        self.mapping.model_spec,
                        guard=self.guard,
                    )
                finally:
                    response.close()
            except httpx.TransportError:
                self.observations[-1] = FixtureObservation(endpoint, "transport_error", None, None)
                break
            except ValueError:
                self.observations[-1] = FixtureObservation(endpoint, "capture_error", None, None)
                break
            self.observations[-1] = FixtureObservation(
                endpoint, "response", mapped, hashlib.sha256(body).hexdigest()
            )
            if endpoint.stage == "input_count" and not count_admitted(self.mapping, mapped):
                break
        return tuple(self.observations)
