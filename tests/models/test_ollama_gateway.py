"""Ollama local and cloud adapter tests."""

from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any

import httpx
import pytest
from open_hollywood_engine.models import (
    InvocationContext,
    MessageRole,
    ModelCallBudget,
    ModelDeployment,
    ModelGatewayError,
    ModelGatewayErrorCode,
    ModelMessage,
    ModelRequest,
    ModelSettings,
    OllamaGateway,
    OllamaHost,
)

pytestmark = pytest.mark.anyio


@pytest.fixture
def anyio_backend() -> str:
    """Keep gateway tests on the production asyncio backend."""
    return "asyncio"


def _transport(handler: Callable[[httpx.Request], httpx.Response]) -> httpx.MockTransport:
    return httpx.MockTransport(handler)


def _request(*, response_schema: dict[str, Any] | None = None) -> ModelRequest:
    return ModelRequest(
        model_identifier="gemma4:e4b",
        messages=(
            ModelMessage(MessageRole.SYSTEM, "You are a story architect."),
            ModelMessage(MessageRole.USER, "Create a supernatural premise."),
        ),
        budget=ModelCallBudget(max_input_tokens=100, max_output_tokens=50),
        invocation=InvocationContext(
            specialist_role="architect",
            prompt_template_version="architect-v1",
        ),
        settings=ModelSettings(
            temperature=0.8,
            top_p=0.9,
            seed=7,
            stop=("END",),
            thinking="medium",
        ),
        response_schema=response_schema,
    )


def _chat_response(**overrides: Any) -> dict[str, Any]:
    response: dict[str, Any] = {
        "model": "gemma4:e4b",
        "created_at": "2026-07-22T10:30:00Z",
        "message": {
            "role": "assistant",
            "content": "A caretaker hears a baby crying inside an unfinished building.",
            "thinking": "I should preserve the stroller image.",
        },
        "done": True,
        "done_reason": "stop",
        "total_duration": 2_500_000_000,
        "load_duration": 500_000_000,
        "prompt_eval_count": 80,
        "prompt_eval_duration": 700_000_000,
        "eval_count": 40,
        "eval_duration": 1_300_000_000,
    }
    response.update(overrides)
    return response


async def test_lists_local_and_cloud_offloaded_models_without_hard_coding_catalog() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/tags"
        return httpx.Response(
            200,
            json={
                "models": [
                    {
                        "name": "gemma4:e4b",
                        "model": "gemma4:e4b",
                        "size": 9_600_000_000,
                        "digest": "local-digest",
                        "details": {
                            "parameter_size": "8B",
                            "quantization_level": "Q4_K_M",
                        },
                    },
                    {
                        "name": "nemotron-3-super:120b-cloud",
                        "model": "nemotron-3-super:120b-cloud",
                        "size": 0,
                        "digest": "cloud-digest",
                        "details": {"parameter_size": "120B"},
                    },
                ]
            },
        )

    async with OllamaGateway(transport=_transport(handler)) as gateway:
        models = await gateway.list_models()

    assert [model.model_identifier for model in models] == [
        "gemma4:e4b",
        "nemotron-3-super:120b-cloud",
    ]
    assert models[0].deployment is ModelDeployment.LOCAL
    assert models[0].quantization_level == "Q4_K_M"
    assert models[1].deployment is ModelDeployment.CLOUD


async def test_discovers_model_capabilities_and_context_window() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/show"
        assert json.loads(request.content) == {"model": "gemma4:e4b", "verbose": False}
        return httpx.Response(
            200,
            json={
                "capabilities": ["completion", "vision", "tools", "thinking"],
                "model_info": {
                    "gemma4.context_length": 131_072,
                    "gemma4.vision.context_length": 8_192,
                },
            },
        )

    async with OllamaGateway(transport=_transport(handler)) as gateway:
        capabilities = await gateway.capabilities("gemma4:e4b")

    assert capabilities.context_window == 131_072
    assert capabilities.supports_chat is True
    assert capabilities.supports_tools is True
    assert capabilities.supports_vision is True
    assert capabilities.supports_thinking is True
    assert capabilities.supports_embeddings is False
    assert capabilities.supports_structured_output is True


async def test_cloud_offload_disables_structured_output_capability() -> None:
    transport = _transport(
        lambda _request: httpx.Response(
            200,
            json={
                "capabilities": ["completion", "tools", "thinking"],
                "model_info": {"nemotron.context_length": 262_144},
            },
        )
    )
    async with OllamaGateway(transport=transport) as gateway:
        capabilities = await gateway.capabilities("nemotron-3-super:120b-cloud")

    assert capabilities.deployment is ModelDeployment.CLOUD
    assert capabilities.supports_structured_output is False


async def test_generic_cloud_tag_is_classified_as_cloud_inference() -> None:
    transport = _transport(
        lambda _request: httpx.Response(
            200,
            json={"capabilities": ["completion"], "model_info": {}},
        )
    )
    async with OllamaGateway(transport=transport) as gateway:
        capabilities = await gateway.capabilities("gemma4:cloud")

    assert capabilities.deployment is ModelDeployment.CLOUD
    assert capabilities.supports_structured_output is False


async def test_generate_maps_portable_settings_budget_schema_and_usage() -> None:
    captured_body: dict[str, Any] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured_body.update(json.loads(request.content))
        return httpx.Response(200, json=_chat_response())

    schema = {
        "type": "object",
        "properties": {"premise": {"type": "string"}},
        "required": ["premise"],
    }
    async with OllamaGateway(transport=_transport(handler)) as gateway:
        response = await gateway.generate(_request(response_schema=schema))

    assert captured_body == {
        "model": "gemma4:e4b",
        "messages": [
            {"role": "system", "content": "You are a story architect."},
            {"role": "user", "content": "Create a supernatural premise."},
        ],
        "options": {
            "num_ctx": 150,
            "num_predict": 50,
            "temperature": 0.8,
            "top_p": 0.9,
            "seed": 7,
            "stop": ["END"],
        },
        "stream": False,
        "think": "medium",
        "format": schema,
    }
    assert response.content.startswith("A caretaker")
    assert response.usage.input_tokens == 80
    assert response.usage.output_tokens == 40
    assert response.timing.total_ms == 2_500
    assert response.timing.generation_ms == 1_300
    assert response.estimated_cost_usd == 0


async def test_direct_cloud_uses_bearer_authentication() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["Authorization"] == "Bearer cloud-secret"
        return httpx.Response(200, json={"models": []})

    async with OllamaGateway(
        host=OllamaHost.CLOUD,
        api_key="cloud-secret",
        transport=_transport(handler),
    ) as gateway:
        assert await gateway.list_models() == ()


async def test_cloud_structured_output_is_rejected_before_network_call() -> None:
    called = False

    def handler(_request: httpx.Request) -> httpx.Response:
        nonlocal called
        called = True
        return httpx.Response(200, json=_chat_response())

    request = _request(response_schema={"type": "object"})
    request = ModelRequest(
        model_identifier="gemma4:31b",
        messages=request.messages,
        budget=request.budget,
        invocation=request.invocation,
        response_schema=request.response_schema,
    )
    async with OllamaGateway(
        host=OllamaHost.CLOUD,
        api_key="cloud-secret",
        transport=_transport(handler),
    ) as gateway:
        with pytest.raises(ModelGatewayError) as error:
            await gateway.generate(request)

    assert error.value.code is ModelGatewayErrorCode.UNSUPPORTED_CAPABILITY
    assert error.value.retryable is False
    assert called is False


async def test_authentication_failure_is_normalized_without_secret_or_body() -> None:
    transport = _transport(
        lambda _request: httpx.Response(
            401,
            json={"error": "bad cloud-secret for prompt Create a supernatural premise"},
        )
    )
    async with OllamaGateway(
        host=OllamaHost.CLOUD,
        api_key="cloud-secret",
        transport=transport,
    ) as gateway:
        with pytest.raises(ModelGatewayError) as error:
            await gateway.list_models()

    assert error.value.code is ModelGatewayErrorCode.AUTHENTICATION
    assert error.value.retryable is False
    assert "cloud-secret" not in str(error.value)
    assert "supernatural" not in str(error.value)


async def test_provider_reported_usage_cannot_silently_exceed_budget() -> None:
    transport = _transport(
        lambda _request: httpx.Response(200, json=_chat_response(prompt_eval_count=101))
    )
    async with OllamaGateway(transport=transport) as gateway:
        with pytest.raises(ModelGatewayError) as error:
            await gateway.generate(_request())

    assert error.value.code is ModelGatewayErrorCode.BUDGET_EXCEEDED


async def test_incomplete_non_streaming_response_is_rejected() -> None:
    transport = _transport(lambda _request: httpx.Response(200, json=_chat_response(done=False)))
    async with OllamaGateway(transport=transport) as gateway:
        with pytest.raises(ModelGatewayError) as error:
            await gateway.generate(_request())

    assert error.value.code is ModelGatewayErrorCode.INVALID_RESPONSE


async def test_invalid_response_metadata_is_normalized() -> None:
    transport = _transport(
        lambda _request: httpx.Response(200, json=_chat_response(total_duration=-1))
    )
    async with OllamaGateway(transport=transport) as gateway:
        with pytest.raises(ModelGatewayError) as error:
            await gateway.generate(_request())

    assert error.value.code is ModelGatewayErrorCode.INVALID_RESPONSE


async def test_transport_failure_is_retryable_provider_unavailable() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused", request=request)

    async with OllamaGateway(transport=_transport(handler)) as gateway:
        with pytest.raises(ModelGatewayError) as error:
            await gateway.list_models()

    assert error.value.code is ModelGatewayErrorCode.PROVIDER_UNAVAILABLE
    assert error.value.retryable is True
