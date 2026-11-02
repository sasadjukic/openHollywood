"""No-network Responses mapping, budgets, failure accounting, and secret regressions."""

from __future__ import annotations

import asyncio
import json
from collections.abc import Callable
from dataclasses import replace
from decimal import Decimal
from pathlib import Path
from typing import Any
from uuid import uuid4

import httpx
import pytest
from open_hollywood_engine.models import (
    InvocationContext,
    MessageRole,
    ModelCallBudget,
    ModelCostBasis,
    ModelDeployment,
    ModelGatewayError,
    ModelGatewayErrorCode,
    ModelMessage,
    ModelRequest,
    ModelSelection,
    ModelSettings,
    OpenAIGateway,
    ProviderModelGateway,
    supports_selection,
)
from open_hollywood_engine.models.openai_catalog import builtin_model_specs, load_model_specs
from open_hollywood_engine.models.openai_schema import strict_response_schema
from open_hollywood_engine.secrets import EnvironmentSecretStore, ModelSecret

pytestmark = pytest.mark.anyio
SECRET = "synthetic-openai-test-credential"


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


def request() -> ModelRequest:
    return ModelRequest(
        model_identifier="gpt-5.4-nano",
        provider="openai",
        deployment=ModelDeployment.CLOUD,
        messages=(ModelMessage(MessageRole.USER, 'Return {"ok":true}.'),),
        budget=ModelCallBudget(1_000, 128, Decimal("0.01")),
        invocation=InvocationContext("synthetic", "1", (uuid4(),)),
        settings=ModelSettings(temperature=0.2, top_p=0.95, seed=42, thinking=False),
        response_schema={
            "type": "object",
            "properties": {"ok": {"type": "boolean", "default": True}},
            "additionalProperties": False,
        },
    )


def payload() -> dict[str, Any]:
    return {
        "model": "gpt-5.4-nano-2026-03-17",
        "created_at": 1_790_000_000,
        "status": "completed",
        "output": [
            {"type": "reasoning", "encrypted_content": "do-not-persist"},
            {
                "type": "message",
                "role": "assistant",
                "content": [
                    {"type": "output_text", "text": '{"ok":true}'},
                ],
            },
        ],
        "usage": {
            "input_tokens": 100,
            "output_tokens": 20,
            "input_tokens_details": {"cached_tokens": 40},
            "output_tokens_details": {"reasoning_tokens": 12},
        },
    }


def gateway(handler: Callable[[httpx.Request], httpx.Response]) -> OpenAIGateway:
    return OpenAIGateway(
        secret_store=EnvironmentSecretStore({"OPENAI_OH_KEY": SECRET}),
        transport=httpx.MockTransport(handler),
    )


async def test_stateless_schema_settings_provenance_and_reasoning_cost() -> None:
    calls: list[dict[str, Any]] = []

    def handler(req: httpx.Request) -> httpx.Response:
        assert req.headers["authorization"] == f"Bearer {SECRET}"
        body = json.loads(req.content)
        calls.append(body)
        if req.url.path.endswith("input_tokens"):
            return httpx.Response(200, json={"input_tokens": 100})
        return httpx.Response(200, json=payload())

    original = request()
    async with gateway(handler) as client:
        result = await client.generate(original)
    count, body = calls
    assert count["text"] == body["text"]
    assert body["store"] is body["background"] is body["stream"] is False
    assert body["truncation"] == "disabled"
    assert body["service_tier"] == "default"
    assert body["max_output_tokens"] == 128
    assert body["reasoning"] == {"effort": "none"}
    assert "seed" not in body and "stop" not in body and "tools" not in body
    schema = body["text"]["format"]
    assert schema["strict"] is True
    assert schema["schema"]["required"] == ["ok"]
    assert "default" not in schema["schema"]["properties"]["ok"]
    assert original.response_schema is not None
    assert "required" not in original.response_schema  # No source-schema mutation.
    assert result.usage.output_tokens == 20  # Already includes reasoning; never add twice.
    assert result.usage.reasoning_tokens == 12
    assert result.usage.cached_input_tokens == 40
    assert result.estimated_cost_usd == Decimal("0.0000378")
    assert result.cost_basis is ModelCostBasis.UNKNOWN  # Rate estimate is not a bill.
    assert result.provider_model_identifier == "gpt-5.4-nano-2026-03-17"
    assert result.metadata["omitted_portable_settings"] == ["seed"]
    assert "do-not-persist" not in repr(result)
    assert SECRET not in repr(result)


async def test_premium_reasoning_model_uses_reviewed_settings() -> None:
    calls: list[dict[str, Any]] = []

    def handler(req: httpx.Request) -> httpx.Response:
        calls.append(json.loads(req.content))
        if req.url.path.endswith("input_tokens"):
            return httpx.Response(200, json={"input_tokens": 100})
        data = payload()
        data["model"] = "gpt-6.1-sol"
        return httpx.Response(200, json=data)

    async with gateway(handler) as client:
        result = await client.generate(replace(request(), model_identifier="gpt-6.1-sol"))
    assert calls[-1]["reasoning"] == {"effort": "low"}
    assert "temperature" not in calls[-1] and "top_p" not in calls[-1]
    assert result.metadata["omitted_portable_settings"] == ["seed", "temperature", "top_p"]
    assert result.estimated_cost_usd == Decimal("0.000354")


@pytest.mark.parametrize("kind", ["output", "input", "dollars", "context"])
async def test_preflight_never_dispatches_over_budget_generation(kind: str) -> None:
    calls: list[str] = []

    def handler(req: httpx.Request) -> httpx.Response:
        calls.append(req.url.path)
        assert req.url.path.endswith("input_tokens")
        return httpx.Response(200, json={"input_tokens": 1001 if kind == "input" else 100})

    candidate = request()
    if kind == "output":
        candidate = replace(candidate, budget=ModelCallBudget(1000, 128_001, Decimal("1")))
    elif kind == "dollars":
        candidate = replace(candidate, budget=ModelCallBudget(1000, 128, Decimal("0.00017")))
    async with gateway(handler) as client:
        if kind == "context":
            spec = client.model_spec(candidate.model_identifier)
            client._specs[candidate.model_identifier] = spec.model_copy(
                update={"context_window": 200}
            )
        with pytest.raises(ModelGatewayError) as caught:
            await client.generate(candidate)
    assert caught.value.code is ModelGatewayErrorCode.BUDGET_EXCEEDED
    assert all(path.endswith("input_tokens") for path in calls)


@pytest.mark.parametrize(
    "kind,code",
    [
        ("refusal", ModelGatewayErrorCode.REFUSAL),
        ("incomplete", ModelGatewayErrorCode.TRUNCATED),
        ("failed", ModelGatewayErrorCode.INVALID_RESPONSE),
        ("empty", ModelGatewayErrorCode.INVALID_RESPONSE),
        ("over_budget", ModelGatewayErrorCode.BUDGET_EXCEEDED),
    ],
)
async def test_failed_generation_retains_billable_usage(
    kind: str, code: ModelGatewayErrorCode
) -> None:
    data = payload()
    if kind == "refusal":
        data["output"][-1]["content"] = [{"type": "refusal", "refusal": "private refusal"}]
    elif kind == "empty":
        data["output"] = []
    elif kind == "over_budget":
        data["usage"]["output_tokens"] = 129
    else:
        data["status"] = kind

    def handler(req: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200, json={"input_tokens": 100} if req.url.path.endswith("input_tokens") else data
        )

    async with gateway(handler) as client:
        with pytest.raises(ModelGatewayError) as caught:
            await client.generate(request())
    error = caught.value
    assert error.code is code and not error.retryable
    assert error.usage is not None and error.usage.input_tokens == 100
    assert error.response is not None and error.response.estimated_cost_usd > 0
    assert "private refusal" not in str(error)


@pytest.mark.parametrize(
    "status,expected,retry",
    [
        (401, ModelGatewayErrorCode.AUTHENTICATION, False),
        (403, ModelGatewayErrorCode.AUTHENTICATION, False),
        (404, ModelGatewayErrorCode.MODEL_NOT_FOUND, False),
        (429, ModelGatewayErrorCode.RATE_LIMITED, True),
        (503, ModelGatewayErrorCode.PROVIDER_UNAVAILABLE, False),
        (400, ModelGatewayErrorCode.INVALID_RESPONSE, False),
        (307, ModelGatewayErrorCode.INVALID_RESPONSE, False),
    ],
)
async def test_http_errors_are_safe_and_never_retried_inside_adapter(
    status: int,
    expected: ModelGatewayErrorCode,
    retry: bool,
) -> None:
    calls = 0

    def handler(req: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(status, json={"error": {"message": SECRET}})

    async with gateway(handler) as client:
        with pytest.raises(ModelGatewayError) as caught:
            await client.generate(request())
    assert calls == 1
    assert caught.value.code is expected and caught.value.retryable is retry
    assert SECRET not in str(caught.value)


async def test_quota_failure_is_terminal() -> None:
    async with gateway(
        lambda req: httpx.Response(
            429,
            json={
                "error": {"code": "insufficient_quota", "message": SECRET},
            },
        )
    ) as client:
        with pytest.raises(ModelGatewayError, match="quota or billing") as caught:
            await client.generate(request())
    assert not caught.value.retryable


@pytest.mark.parametrize("location", ["prompt", "response"])
async def test_secret_guard_blocks_both_directions(location: str) -> None:
    calls = 0

    def handler(req: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(200, json={"input_tokens": 100, "unsafe": SECRET})

    candidate = request()
    if location == "prompt":
        candidate = replace(candidate, messages=(ModelMessage(MessageRole.USER, SECRET),))
    async with gateway(handler) as client:
        with pytest.raises(ModelGatewayError) as caught:
            await client.generate(candidate)
    assert caught.value.code is ModelGatewayErrorCode.SECRET_EXPOSURE
    assert SECRET not in str(caught.value)
    assert calls == (0 if location == "prompt" else 1)


async def test_missing_key_and_unknown_model_do_not_generate() -> None:
    def unexpected(req: httpx.Request) -> httpx.Response:
        raise AssertionError("unexpected network request")

    async with OpenAIGateway(
        secret_store=EnvironmentSecretStore({}), transport=httpx.MockTransport(unexpected)
    ) as client:
        with pytest.raises(ModelGatewayError) as caught:
            await client.generate(request())
        assert caught.value.code is ModelGatewayErrorCode.AUTHENTICATION
        with pytest.raises(ModelGatewayError) as caught:
            await client.generate(replace(request(), model_identifier="new-unreviewed-model"))
        assert caught.value.code is ModelGatewayErrorCode.UNSUPPORTED_CAPABILITY


async def test_catalog_intersects_account_access_and_reviewed_text_capabilities() -> None:
    async with gateway(
        lambda req: httpx.Response(
            200,
            json={
                "data": [
                    {"id": "gpt-5.4"},
                    {"id": "gpt-6.1-sol"},
                    {"id": "embedding-model"},
                    {"id": "gpt-5.4-pro"},
                    {"id": "future-model"},
                ]
            },
        )
    ) as client:
        models = await client.list_models()
        assert [model.model_identifier for model in models] == ["gpt-5.4", "gpt-6.1-sol"]
        assert (await client.capabilities("gpt-6.1-sol")).supports_structured_output


async def test_cancellation_propagates_and_no_retry_is_dispatched() -> None:
    started = asyncio.Event()
    stopped = asyncio.Event()

    async def handler(req: httpx.Request) -> httpx.Response:
        if req.url.path.endswith("input_tokens"):
            return httpx.Response(200, json={"input_tokens": 100})
        started.set()
        try:
            await asyncio.Event().wait()
        finally:
            stopped.set()
        raise AssertionError("unreachable")

    async with OpenAIGateway(
        secret_store=EnvironmentSecretStore({"OPENAI_OH_KEY": SECRET}),
        transport=httpx.MockTransport(handler),
    ) as client:
        task = asyncio.create_task(client.generate(request()))
        await started.wait()
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
    assert stopped.is_set()


async def test_router_requires_exact_provider_deployment_and_frozen_model() -> None:
    selection = ModelSelection("openai", "gpt-5.4-nano", ModelDeployment.CLOUD)
    client = gateway(
        lambda req: httpx.Response(
            200, json={"input_tokens": 100} if req.url.path.endswith("input_tokens") else payload()
        )
    )
    router = ProviderModelGateway(
        {("openai", ModelDeployment.CLOUD): client}, selections=frozenset({selection})
    )
    try:
        assert supports_selection(router, selection)
        assert not supports_selection(router, replace(selection, provider="ollama"))
        assert (await router.generate(request())).provider == "openai"
        with pytest.raises(ModelGatewayError):
            await router.generate(replace(request(), model_identifier="gpt-5.4"))
        with pytest.raises(ModelGatewayError):
            await router.generate(replace(request(), deployment=ModelDeployment.LOCAL))
        with pytest.raises(ValueError, match="explicit provider"):
            await router.generate(replace(request(), provider=None))
    finally:
        await router.close()


def test_schema_conversion_keeps_application_models_validatable() -> None:
    from open_hollywood_api.services.blueprint_model_executor import _OUTPUT_MODELS as blueprint
    from open_hollywood_api.services.production_model_executor import _OUTPUT_MODELS as production

    for model in [*blueprint.values(), *production.values()]:
        schema = strict_response_schema(model.model_json_schema())
        assert schema["additionalProperties"] is False
        assert schema["required"] == list(schema["properties"])
    with pytest.raises(ModelGatewayError):
        strict_response_schema({"type": "object", "additionalProperties": {"type": "string"}})


def test_safe_explicit_catalog_extension(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    spec = builtin_model_specs()["gpt-5.4"].model_copy(
        update={
            "model_identifier": "new-reviewed-model",
            "response_model_identifiers": (),
        }
    )
    path = tmp_path / "models.json"
    path.write_text(json.dumps([spec.model_dump(mode="json")]), encoding="utf-8")
    monkeypatch.setenv("OPEN_HOLLYWOOD_OPENAI_MODELS_PATH", str(path))
    assert load_model_specs()["new-reviewed-model"] == spec
    path.write_text('[{"api_key":"unsafe"}]', encoding="utf-8")
    with pytest.raises(ValueError, match="configuration is invalid"):
        load_model_specs()


def test_application_secret_handle_resolves_only_authorized_variable() -> None:
    store = EnvironmentSecretStore({"OPENAI_OH_KEY": SECRET, "OPENAI_API_KEY": "unrelated"})
    assert store.require(ModelSecret.OPENAI_API_KEY).reveal() == SECRET


@pytest.mark.parametrize("problem", ["wrong_model", "bad_usage", "bad_json", "timeout"])
async def test_malformed_transport_is_normalized_without_losing_request_metadata(
    problem: str,
) -> None:
    def handler(req: httpx.Request) -> httpx.Response:
        if req.url.path.endswith("input_tokens"):
            return httpx.Response(200, json={"input_tokens": 100})
        if problem == "timeout":
            raise httpx.ReadTimeout(SECRET, request=req)
        if problem == "bad_json":
            return httpx.Response(200, content=b"not-json")
        data = payload()
        if problem == "wrong_model":
            data["model"] = "unexpected-model"
        else:
            data["usage"]["output_tokens_details"] = {"reasoning_tokens": 999}
        return httpx.Response(200, json=data)

    async with gateway(handler) as client:
        with pytest.raises(ModelGatewayError) as caught:
            await client.generate(request())
    assert caught.value.code is (
        ModelGatewayErrorCode.PROVIDER_TIMEOUT
        if problem == "timeout"
        else ModelGatewayErrorCode.INVALID_RESPONSE
    )
    assert caught.value.metadata["counted_input_tokens"] == 100
    assert "request_sha256" in caught.value.metadata
    assert SECRET not in str(caught.value)
    assert not caught.value.retryable


async def test_unsupported_model_settings_fail_before_transport() -> None:
    def unexpected(req: httpx.Request) -> httpx.Response:
        raise AssertionError("unexpected network call")

    async with gateway(unexpected) as client:
        with pytest.raises(ModelGatewayError) as caught:
            await client.generate(replace(request(), settings=ModelSettings(stop=("END",))))
        assert caught.value.code is ModelGatewayErrorCode.UNSUPPORTED_CAPABILITY
        with pytest.raises(ModelGatewayError) as caught:
            await client.generate(replace(request(), settings=ModelSettings(temperature=3)))
        assert caught.value.code is ModelGatewayErrorCode.UNSUPPORTED_CAPABILITY
