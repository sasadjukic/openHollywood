"""Authored provider-format fixtures; no live transport, credentials or private captures."""

from __future__ import annotations

import json
import socket
import sqlite3
from dataclasses import replace
from decimal import Decimal
from typing import Any
from uuid import UUID

import httpx
import pytest
from open_hollywood_engine.evaluations.assessment_completion import encoded
from open_hollywood_engine.evaluations.assessment_result import (
    assessment_response_schema,
    bind_assessment_result,
    scope_for_batch,
)
from open_hollywood_engine.evaluations.assessment_work import AssessmentReceipt
from open_hollywood_engine.models import (
    InvocationContext,
    MessageRole,
    ModelCallBudget,
    ModelDeployment,
    ModelMessage,
    ModelRequest,
    ModelSettings,
)
from open_hollywood_engine.models.assessment_openai import (
    OfflineReplay,
    check_outgoing,
    map_response,
    prepare_wire,
)
from open_hollywood_engine.models.openai_catalog import builtin_model_specs
from open_hollywood_engine.secrets import SecretLeakGuard, SecretValue

from tests.authored_completion_fixtures import authored_context, submission_for


@pytest.fixture(autouse=True)
def offline(monkeypatch: pytest.MonkeyPatch) -> None:
    def deny(*args: Any, **kwargs: Any) -> Any:
        raise AssertionError("network, client and database disabled")

    for target, name in (
        (socket, "socket"),
        (sqlite3, "connect"),
        (httpx, "Client"),
        (httpx, "AsyncClient"),
    ):
        monkeypatch.setattr(target, name, deny)


def inputs() -> tuple[Any, Any, ModelRequest, Any, str]:
    context = authored_context()
    work = context.intake.pending_work
    assert work is not None
    scope = scope_for_batch(work, work.batches[0].batch_id, "a" * 64)
    request = ModelRequest(
        model_identifier="gpt-6.1-sol",
        provider="openai",
        deployment=ModelDeployment.CLOUD,
        messages=tuple(ModelMessage(MessageRole(m.role), m.content) for m in work.context.messages),
        invocation=InvocationContext("offline_assessment_mapping", "authored-1", (UUID(int=1),)),
        budget=ModelCallBudget(24000, 32000, Decimal("0.60")),
        settings=ModelSettings(temperature=0.2, top_p=0.95, seed=20261022, thinking="high"),
        response_schema=json.loads(encoded(assessment_response_schema(work, scope))),
    )
    return (
        work,
        scope,
        request,
        builtin_model_specs()["gpt-6.1-sol"],
        submission_for(context).attempts[0].raw_final,
    )


def provider_body(final: str = '{"authored":true}') -> dict[str, Any]:
    return {
        "id": "resp_fixture_1",
        "model": "gpt-6.1-sol",
        "status": "completed",
        "incomplete_details": None,
        "error": None,
        "output": [
            {
                "type": "reasoning",
                "summary": [{"text": "private thinking"}],
                "encrypted_content": "private encrypted reasoning",
            },
            {
                "id": "msg_fixture_1",
                "type": "message",
                "role": "assistant",
                "status": "completed",
                "phase": "final_answer",
                "content": [{"type": "output_text", "text": final, "annotations": []}],
            },
        ],
        "usage": {
            "input_tokens": 100,
            "output_tokens": 20,
            "total_tokens": 120,
            "input_tokens_details": {"cached_tokens": 10},
            "output_tokens_details": {"reasoning_tokens": 5},
        },
    }


def test_shared_wire_retains_exact_context_schema_and_separate_bodies() -> None:
    work, scope, request, spec, _ = inputs()
    mapped = prepare_wire(work, scope, request, spec)
    count, generation = [json.loads(e.body_utf8) for e in mapped.endpoints]
    assert generation["input"] == [m.model_dump(mode="json") for m in work.context.messages]
    assert generation["model"] == request.model_identifier
    assert generation["reasoning"] == {"effort": "high"}
    assert generation["max_output_tokens"] == 32000
    assert generation["store"] is generation["stream"] is generation["background"] is False
    assert generation["truncation"] == "disabled"
    assert generation["text"]["format"]["strict"] is True
    assert set(count) == {"input", "model", "reasoning", "text"}
    assert count == {k: generation[k] for k in count}
    assert not {"temperature", "top_p", "seed"}.intersection(generation)
    omitted = mapped.effective["omitted_portable_settings"]
    assert isinstance(omitted, list)
    assert omitted == ["seed", "temperature", "top_p"]
    assert mapped.native_request_sha256 == scope.request_sha256
    assert all(e.body_bytes_sha256 != mapped.native_request_sha256 for e in mapped.endpoints)
    assert not mapped.live_authorized


@pytest.mark.parametrize(
    "change", ["messages", "scope", "schema", "model", "provider", "output", "cost"]
)
def test_work_request_scope_drift_refused(change: str) -> None:
    work, scope, request, spec, _ = inputs()
    if change == "messages":
        request = replace(request, messages=(ModelMessage(MessageRole.USER, "wrong context"),))
    elif change == "scope":
        scope = scope.model_copy(update={"work_sha256": "b" * 64})
    elif change == "schema":
        request = replace(request, response_schema={"type": "object"})
    elif change == "model":
        request = replace(request, model_identifier="other")
    elif change == "provider":
        request = replace(request, provider="ollama")
    elif change == "output":
        request = replace(request, budget=ModelCallBudget(24000, 200000, Decimal("10")))
    else:
        request = replace(request, budget=ModelCallBudget(24000, 32000, Decimal("0.0001")))
    with pytest.raises(ValueError):
        prepare_wire(work, scope, request, spec)


@pytest.mark.parametrize(
    "change", ["body", "whitespace", "url", "path", "method", "header", "host", "length", "hash"]
)
def test_actual_callback_request_must_match_exact_frozen_endpoint(change: str) -> None:
    work, scope, request, spec, _ = inputs()
    endpoint = prepare_wire(work, scope, request, spec).endpoints[1]
    method, url, body = "POST", endpoint.destination + endpoint.path, endpoint.body_utf8.encode()
    headers = {"Content-Type": "application/json"}
    if change == "body":
        body = b"{}"
    elif change == "whitespace":
        body += b" "
    elif change == "url":
        url = "https://other.invalid/v1/responses"
    elif change == "path":
        url += "/input_tokens"
    elif change == "method":
        method = "GET"
    elif change == "header":
        headers["Authorization"] = "synthetic-fixture-value"
    elif change == "host":
        headers["Host"] = "other.invalid"
    elif change == "length":
        headers["Content-Length"] = "0"
    else:
        endpoint = endpoint.model_copy(update={"body_bytes_sha256": "0" * 64})
    with pytest.raises(ValueError):
        check_outgoing(endpoint, httpx.Request(method, url, content=body, headers=headers))


def test_complete_safe_mapping_binds_original_scope_without_retaining_reasoning() -> None:
    work, scope, _, spec, raw = inputs()
    mapped = map_response("generation", 200, encoded(provider_body(raw)), spec)
    assert mapped.state == "complete" and mapped.raw_final == raw
    assert "private thinking" not in mapped.model_dump_json()
    assert "encrypted" not in mapped.model_dump_json()
    receipt = AssessmentReceipt(
        work_sha256=work.fingerprint,
        batch_id=scope.batch_id,
        request_sha256=scope.request_sha256,
        attempt_id="fixture-1",
        status="valid",
        result_sha256=mapped.raw_final_utf8_sha256,
        assessed_unit_ids=scope.active_unit_ids,
        input_tokens=mapped.usage.input_tokens,
        output_tokens=mapped.usage.output_tokens,
        reasoning_tokens=mapped.usage.reasoning_tokens,
        active_seconds=0,
    )
    result = bind_assessment_result(work, scope, receipt, raw)
    assert result.receipt.binding == "complete"
    assert mapped.authentication == "mapping_only_not_delivery_authentication"
    assert mapped.actual_billed_cost is None and not mapped.writer_dispatch_authorized


@pytest.mark.parametrize(
    "kind,expected",
    [
        ("length", "length"),
        ("filter", "refusal"),
        ("refusal", "refusal"),
        ("failed", "error"),
        ("cancelled", "error"),
        ("in_progress", "invalid"),
        ("queued", "invalid"),
        ("unknown_reason", "invalid"),
        ("empty", "invalid"),
        ("role", "invalid"),
        ("phase", "invalid"),
        ("message_status", "invalid"),
        ("multi_message", "invalid"),
        ("multi_text", "invalid"),
        ("tool", "invalid"),
        ("content", "invalid"),
        ("model", "invalid"),
        ("missing_model", "invalid"),
        ("invalid_id", "invalid"),
        ("usage_shape", "invalid"),
        ("usage_boolean", "invalid"),
        ("usage_negative", "invalid"),
        ("usage_fraction", "invalid"),
        ("usage_total", "invalid"),
        ("usage_reasoning", "invalid"),
        ("usage_cached", "invalid"),
    ],
)
def test_provider_failure_classes_keep_known_usage_without_success(
    kind: str, expected: str
) -> None:
    spec = builtin_model_specs()["gpt-6.1-sol"]
    body = provider_body()
    message = body["output"][1]
    if kind in ("length", "filter", "unknown_reason"):
        body.update(
            status="incomplete",
            incomplete_details={
                "reason": {
                    "length": "max_output_tokens",
                    "filter": "content_filter",
                    "unknown_reason": "new_reason",
                }[kind]
            },
        )
        message["status"] = "incomplete"
    elif kind in ("failed", "cancelled", "queued", "in_progress"):
        body["status"] = kind
    elif kind == "refusal":
        message["content"] = [{"type": "refusal", "refusal": "fixture"}]
    elif kind == "empty":
        message["content"][0]["text"] = "   "
    elif kind == "role":
        message["role"] = "user"
    elif kind == "phase":
        message["phase"] = "commentary"
    elif kind == "message_status":
        message["status"] = "incomplete"
    elif kind == "multi_message":
        body["output"].append(message)
    elif kind == "multi_text":
        message["content"].append(message["content"][0])
    elif kind == "tool":
        body["output"].append({"type": "function_call"})
    elif kind == "content":
        message["content"] = None
    elif kind == "model":
        body["model"] = "unregistered-model"
    elif kind == "missing_model":
        del body["model"]
    elif kind == "invalid_id":
        body["id"] = "not a safe identifier"
    elif kind == "usage_shape":
        body["usage"]["output_tokens_details"] = []
    elif kind == "usage_boolean":
        body["usage"]["output_tokens"] = True
    elif kind == "usage_negative":
        body["usage"]["output_tokens"] = -1
    elif kind == "usage_fraction":
        body["usage"]["output_tokens"] = 2.5
    elif kind == "usage_total":
        body["usage"]["total_tokens"] = 999
    elif kind == "usage_reasoning":
        body["usage"]["output_tokens_details"]["reasoning_tokens"] = 30
    elif kind == "usage_cached":
        body["usage"]["input_tokens_details"]["cached_tokens"] = 101
    result = map_response("generation", 200, encoded(body), spec)
    assert result.state == expected
    assert result.usage.input_tokens == 100
    assert result.actual_billed_cost is None


@pytest.mark.parametrize("status", [201, 301, 400, 401, 403, 404, 429, 500, 503])
def test_actual_http_failure_overrides_valid_body_and_never_echoes_error_message(
    status: int,
) -> None:
    body = provider_body()
    body["error"] = {"code": "server_error", "message": "Do not retain arbitrary provider text"}
    result = map_response("generation", status, encoded(body), builtin_model_specs()["gpt-6.1-sol"])
    assert result.state == "error" and result.usage.output_tokens == 20
    assert f"http_{status}" in result.error_codes
    assert result.raw_final is None
    assert "arbitrary provider text" not in result.model_dump_json()


@pytest.mark.parametrize(
    "body",
    [b"{", b"[]", b'{"usage":{},"usage":{}}', b'{"value":NaN}', b"\xff", b"x" * (1024 * 1024 + 1)],
    ids=["bad-json", "array", "duplicate", "nan", "bad-utf8", "oversize"],
)
def test_malformed_response_preserves_unknown_usage(body: bytes) -> None:
    result = map_response("generation", 500, body, builtin_model_specs()["gpt-6.1-sol"])
    assert result.state == "invalid" and result.http_status == 500
    assert result.usage.input_tokens is None and result.raw_final is None


@pytest.mark.parametrize(
    "usage", [None, {}, {"input_tokens": 100}, {"input_tokens": 0, "output_tokens": 0}]
)
def test_absent_usage_is_never_invented_or_filled_from_count(usage: Any) -> None:
    body = provider_body()
    body["usage"] = usage
    result = map_response("generation", 200, encoded(body), builtin_model_specs()["gpt-6.1-sol"])
    assert result.state == "complete"
    assert result.usage.output_tokens == (usage or {}).get("output_tokens")
    assert result.usage.reasoning_tokens is result.usage.cached_input_tokens is None
    assert result.counted_input_tokens is None


def test_known_secret_guard_rejects_without_leaking_or_rewriting_bound_content() -> None:
    body = provider_body("synthetic-secret-value")
    guard = SecretLeakGuard((SecretValue("synthetic-secret-value"),))
    result = map_response(
        "generation", 200, encoded(body), builtin_model_specs()["gpt-6.1-sol"], guard=guard
    )
    assert result.state == "invalid" and result.raw_final is None
    assert "synthetic-secret-value" not in result.model_dump_json()


@pytest.mark.parametrize("count", [None, True, -1, 1.5, 24001, 500000])
def test_failed_unknown_or_overbudget_count_prevents_generation(count: Any) -> None:
    work, scope, request, spec, _ = inputs()
    mapping = prepare_wire(work, scope, request, spec)
    called: list[str] = []

    def handler(req: httpx.Request) -> httpx.Response:
        called.append(req.url.path)
        return httpx.Response(200, json={"input_tokens": count})

    replay = OfflineReplay(mapping, mapping, httpx.MockTransport(handler))
    assert len(replay.run()) == 1
    assert called == ["/v1/responses/input_tokens"]
    with pytest.raises(ValueError, match="already_used"):
        replay.run()


@pytest.mark.parametrize(
    "failure",
    ["none", "count_http", "timeout", "interrupt", "cancel_before", "unknown_usage", "oversize"],
)
def test_injected_endpoint_order_interrupt_and_no_retry(failure: str) -> None:
    work, scope, request, spec, raw = inputs()
    mapping = prepare_wire(work, scope, request, spec)
    called: list[str] = []

    def handler(req: httpx.Request) -> httpx.Response:
        assert len(replay.observations) == len(called) + 1
        assert replay.observations[-1].disposition == "intent_unknown"
        called.append(req.url.path)
        if len(called) == 1:
            return httpx.Response(
                500 if failure == "count_http" else 200, json={"input_tokens": 100}
            )
        if failure == "timeout":
            raise httpx.ReadTimeout("fixture", request=req)
        if failure == "interrupt":
            raise KeyboardInterrupt
        if failure == "oversize":
            return httpx.Response(200, content=b"x" * (1024 * 1024 + 1))
        body = provider_body(raw)
        if failure == "unknown_usage":
            body.pop("usage")
        return httpx.Response(200, json=body)

    replay = OfflineReplay(mapping, mapping, httpx.MockTransport(handler))
    if failure == "interrupt":
        with pytest.raises(KeyboardInterrupt):
            replay.run()
        assert replay.observations[-1].disposition == "intent_unknown"
    else:
        result = replay.run(cancelled=failure == "cancel_before")
        assert len(result) == (
            0 if failure == "cancel_before" else 1 if failure == "count_http" else 2
        )
        if failure in ("none", "unknown_usage"):
            assert result[-1].response is not None and result[-1].response.state == "complete"
        elif failure in ("timeout", "oversize"):
            assert result[-1].response is None
    with pytest.raises(ValueError, match="already_used"):
        replay.run()


@pytest.mark.parametrize("kind", ["malformed", "duplicate", "missing", "extra", "citation"])
def test_terminal_success_does_not_bypass_native_final_validation(kind: str) -> None:
    work, scope, _, spec, raw = inputs()
    if kind == "malformed":
        raw = "{"
    elif kind == "duplicate":
        raw = raw.replace('"assessments":', '"assessments":{},"assessments":')
    else:
        body = json.loads(raw)
        key = next(iter(body["assessments"]))
        if kind == "missing":
            del body["assessments"][key]
        elif kind == "extra":
            body["assessments"]["unknown"] = body["assessments"][key]
        else:
            body["assessments"][key]["evidence"] = ["unregistered"]
        raw = json.dumps(body)
    mapped = map_response("generation", 200, encoded(provider_body(raw)), spec)
    assert mapped.state == "complete"  # Terminal envelope only; native validation is separate.
    receipt = AssessmentReceipt(
        work_sha256=work.fingerprint,
        batch_id=scope.batch_id,
        request_sha256=scope.request_sha256,
        attempt_id="authored-invalid",
        status="valid",
        result_sha256=mapped.raw_final_utf8_sha256,
        assessed_unit_ids=scope.active_unit_ids,
        active_seconds=0,
    )
    with pytest.raises(ValueError):
        bind_assessment_result(work, scope, receipt, raw)


def test_declared_alias_is_allowed_but_absent_id_and_details_stay_absent() -> None:
    spec = builtin_model_specs()["gpt-6.1-sol"].model_copy(
        update={"response_model_identifiers": ("fixture-alias",)}
    )
    body = provider_body()
    body["model"] = "fixture-alias"
    body.pop("id")
    body["usage"].pop("input_tokens_details")
    body["usage"].pop("output_tokens_details")
    mapped = map_response("generation", 200, encoded(body), spec)
    assert mapped.state == "complete" and mapped.returned_model == "fixture-alias"
    assert mapped.response_id is None
    assert mapped.usage.cached_input_tokens is mapped.usage.reasoning_tokens is None


@pytest.mark.parametrize("status,with_error", [(500, False), (200, True)])
def test_http_or_provider_error_each_prevents_success(status: int, with_error: bool) -> None:
    body = provider_body()
    if with_error:
        body["error"] = {"code": "unlisted", "message": "discard me"}
    result = map_response("generation", status, encoded(body), builtin_model_specs()["gpt-6.1-sol"])
    assert result.state == "error"
    assert result.usage.input_tokens == 100 and result.raw_final is None


def test_changed_mapping_or_real_transport_is_refused_without_callback() -> None:
    work, scope, request, spec, _ = inputs()
    mapped = prepare_wire(work, scope, request, spec)
    transport = httpx.MockTransport(
        lambda req: (_ for _ in ()).throw(AssertionError("no callback"))
    )
    with pytest.raises(ValueError, match="mapping_changed"):
        OfflineReplay(
            mapped.model_copy(update={"native_request_sha256": "c" * 64}), mapped, transport
        )
    with pytest.raises(ValueError, match="mock_transport_required"):
        OfflineReplay(mapped, mapped, None)  # type: ignore[arg-type]


@pytest.mark.parametrize("constraint", ["context", "cost", "model_input"])
def test_count_reservation_checks_all_limits(constraint: str) -> None:
    work, scope, request, spec, _ = inputs()
    if constraint == "context":
        spec = spec.model_copy(update={"context_window": 32050})
    elif constraint == "model_input":
        spec = spec.model_copy(update={"max_input_tokens": 50})
    else:
        request = replace(request, budget=ModelCallBudget(24000, 32000, Decimal("0.32")))
    mapped = prepare_wire(work, scope, request, spec)
    called: list[str] = []

    def handler(req: httpx.Request) -> httpx.Response:
        called.append(req.url.path)
        return httpx.Response(200, json={"input_tokens": 100})

    assert len(OfflineReplay(mapped, mapped, httpx.MockTransport(handler)).run()) == 1
    assert called == ["/v1/responses/input_tokens"]


def test_invalid_unicode_final_keeps_known_usage_without_throwing_or_repair() -> None:
    body = json.dumps(provider_body("\ud800"), ensure_ascii=True).encode()
    mapped = map_response("generation", 200, body, builtin_model_specs()["gpt-6.1-sol"])
    assert mapped.state == "invalid" and mapped.raw_final is None
    assert mapped.usage.input_tokens == 100
    assert "invalid_final_unicode" in mapped.issues


def test_excessive_json_nesting_is_an_invalid_capture() -> None:
    body = b'{"nested":' + b"[" * 2000 + b"0" + b"]" * 2000 + b"}"
    mapped = map_response("generation", 200, body, builtin_model_specs()["gpt-6.1-sol"])
    assert mapped.state == "invalid" and mapped.usage.input_tokens is None
