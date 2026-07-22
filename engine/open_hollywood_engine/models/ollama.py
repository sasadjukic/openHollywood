"""Ollama adapter supporting local inference and direct Ollama Cloud access."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import Any, Self, cast

import httpx

from open_hollywood_engine.models.contracts import (
    ModelCapabilities,
    ModelDeployment,
    ModelDescriptor,
    ModelRequest,
    ModelResponse,
    ModelTiming,
    ModelUsage,
)
from open_hollywood_engine.models.gateway import ModelGatewayError, ModelGatewayErrorCode

OLLAMA_PROVIDER = "ollama"
DEFAULT_LOCAL_BASE_URL = "http://127.0.0.1:11434"
DEFAULT_CLOUD_BASE_URL = "https://ollama.com"


class OllamaHost(StrEnum):
    """Configured Ollama API host."""

    LOCAL = "local"
    CLOUD = "cloud"


class OllamaGateway:
    """Translate Ollama's HTTP API into provider-neutral domain contracts."""

    def __init__(
        self,
        *,
        host: OllamaHost = OllamaHost.LOCAL,
        base_url: str | None = None,
        api_key: str | None = None,
        timeout_seconds: float = 120.0,
        client: httpx.AsyncClient | None = None,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        if host is OllamaHost.CLOUD and client is None and not api_key:
            raise ValueError("an API key is required for direct Ollama Cloud access")
        if client is not None and transport is not None:
            raise ValueError("client and transport are mutually exclusive")

        resolved_base_url = base_url or (
            DEFAULT_CLOUD_BASE_URL if host is OllamaHost.CLOUD else DEFAULT_LOCAL_BASE_URL
        )
        headers = {"Accept": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        self._host = host
        self._owns_client = client is None
        self._client = client or httpx.AsyncClient(
            base_url=resolved_base_url.rstrip("/"),
            headers=headers,
            timeout=timeout_seconds,
            transport=transport,
        )

    @property
    def provider(self) -> str:
        """Return the stable provider identifier."""
        return OLLAMA_PROVIDER

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *_exc_info: object) -> None:
        await self.close()

    async def close(self) -> None:
        """Close only clients created by this gateway."""
        if self._owns_client:
            await self._client.aclose()

    async def list_models(self) -> tuple[ModelDescriptor, ...]:
        """Return the model catalog advertised by the configured Ollama host."""
        payload = await self._request_json("GET", "/api/tags")
        raw_models = _require_sequence(payload.get("models"), field_name="models")
        models: list[ModelDescriptor] = []
        for raw_model in raw_models:
            model = _require_mapping(raw_model, field_name="models[]")
            identifier = _require_string(model.get("model", model.get("name")), field_name="model")
            raw_details = model.get("details")
            details = (
                _require_mapping(raw_details, field_name="details")
                if raw_details is not None
                else {}
            )
            models.append(
                ModelDescriptor(
                    provider=self.provider,
                    model_identifier=identifier,
                    deployment=self._deployment_for(identifier),
                    digest=_optional_string(model.get("digest"), field_name="digest"),
                    parameter_size=_optional_string(
                        details.get("parameter_size"), field_name="parameter_size"
                    ),
                    quantization_level=_optional_string(
                        details.get("quantization_level"), field_name="quantization_level"
                    ),
                    size_bytes=_optional_integer(model.get("size"), field_name="size"),
                )
            )
        return tuple(models)

    async def capabilities(self, model_identifier: str) -> ModelCapabilities:
        """Inspect one model and combine model and deployment-level features."""
        if not model_identifier:
            raise ValueError("model_identifier must not be empty")
        payload = await self._request_json(
            "POST", "/api/show", json={"model": model_identifier, "verbose": False}
        )
        raw_names = _require_sequence(payload.get("capabilities", ()), field_name="capabilities")
        capability_names = tuple(
            sorted(_require_string(value, field_name="capabilities[]") for value in raw_names)
        )
        capability_set = set(capability_names)
        model_info_value = payload.get("model_info", {})
        model_info = _require_mapping(model_info_value, field_name="model_info")
        deployment = self._deployment_for(model_identifier)
        supports_chat = "completion" in capability_set
        return ModelCapabilities(
            provider=self.provider,
            model_identifier=model_identifier,
            deployment=deployment,
            context_window=_context_window(model_info),
            supports_chat=supports_chat,
            supports_tools="tools" in capability_set,
            supports_vision="vision" in capability_set,
            supports_thinking="thinking" in capability_set,
            supports_embeddings="embedding" in capability_set,
            supports_structured_output=(supports_chat and deployment is ModelDeployment.LOCAL),
            raw_capability_names=capability_names,
        )

    async def generate(self, request: ModelRequest) -> ModelResponse:
        """Generate a complete chat response with bounded Ollama options."""
        deployment = self._deployment_for(request.model_identifier)
        if request.response_schema is not None and deployment is ModelDeployment.CLOUD:
            raise ModelGatewayError(
                ModelGatewayErrorCode.UNSUPPORTED_CAPABILITY,
                "Ollama Cloud does not support schema-enforced structured output",
                retryable=False,
            )

        options: dict[str, Any] = {
            "num_ctx": request.budget.max_context_tokens,
            "num_predict": request.budget.max_output_tokens,
        }
        if request.settings.temperature is not None:
            options["temperature"] = request.settings.temperature
        if request.settings.top_p is not None:
            options["top_p"] = request.settings.top_p
        if request.settings.seed is not None:
            options["seed"] = request.settings.seed
        if request.settings.stop:
            options["stop"] = list(request.settings.stop)

        body: dict[str, Any] = {
            "model": request.model_identifier,
            "messages": [
                {"role": message.role.value, "content": message.content}
                for message in request.messages
            ],
            "options": options,
            "stream": False,
        }
        if request.settings.thinking is not None:
            body["think"] = request.settings.thinking
        if request.response_schema is not None:
            body["format"] = dict(request.response_schema)

        payload = await self._request_json("POST", "/api/chat", json=body)
        try:
            response = self._parse_response(payload, deployment=deployment)
        except ModelGatewayError:
            raise
        except (ValueError, OverflowError) as exc:
            raise ModelGatewayError(
                ModelGatewayErrorCode.INVALID_RESPONSE,
                "Ollama response metadata is invalid",
                retryable=False,
            ) from exc
        if response.usage.input_tokens > request.budget.max_input_tokens:
            raise ModelGatewayError(
                ModelGatewayErrorCode.BUDGET_EXCEEDED,
                "provider-reported input token usage exceeded the call budget",
                retryable=False,
            )
        if response.usage.output_tokens > request.budget.max_output_tokens:
            raise ModelGatewayError(
                ModelGatewayErrorCode.BUDGET_EXCEEDED,
                "provider-reported output token usage exceeded the call budget",
                retryable=False,
            )
        return response

    def _deployment_for(self, model_identifier: str) -> ModelDeployment:
        model_tag = model_identifier.rsplit(":", maxsplit=1)[-1]
        if self._host is OllamaHost.CLOUD or model_tag == "cloud" or model_tag.endswith("-cloud"):
            return ModelDeployment.CLOUD
        return ModelDeployment.LOCAL

    async def _request_json(
        self,
        method: str,
        path: str,
        *,
        json: Mapping[str, Any] | None = None,
    ) -> Mapping[str, Any]:
        try:
            response = await self._client.request(method, path, json=json)
        except httpx.TransportError as exc:
            raise ModelGatewayError(
                ModelGatewayErrorCode.PROVIDER_UNAVAILABLE,
                "Ollama is unavailable",
                retryable=True,
            ) from exc
        self._raise_for_status(response)
        try:
            payload = response.json()
        except ValueError as exc:
            raise ModelGatewayError(
                ModelGatewayErrorCode.INVALID_RESPONSE,
                "Ollama returned invalid JSON",
                retryable=False,
            ) from exc
        return _require_mapping(payload, field_name="response")

    def _raise_for_status(self, response: httpx.Response) -> None:
        status_code = response.status_code
        if status_code < 400:
            return
        if status_code in (401, 403):
            code = ModelGatewayErrorCode.AUTHENTICATION
            retryable = False
        elif status_code == 404:
            code = ModelGatewayErrorCode.MODEL_NOT_FOUND
            retryable = False
        elif status_code == 429:
            code = ModelGatewayErrorCode.RATE_LIMITED
            retryable = True
        elif status_code >= 500:
            code = ModelGatewayErrorCode.PROVIDER_UNAVAILABLE
            retryable = True
        else:
            code = ModelGatewayErrorCode.INVALID_RESPONSE
            retryable = False
        raise ModelGatewayError(
            code,
            f"Ollama request failed with HTTP {status_code}",
            retryable=retryable,
        )

    def _parse_response(
        self, payload: Mapping[str, Any], *, deployment: ModelDeployment
    ) -> ModelResponse:
        if payload.get("done") is not True:
            raise _invalid_field("done")
        message = _require_mapping(payload.get("message"), field_name="message")
        content = _require_string(message.get("content"), field_name="message.content")
        created_at_text = _require_string(payload.get("created_at"), field_name="created_at")
        try:
            created_at = datetime.fromisoformat(created_at_text.replace("Z", "+00:00"))
        except ValueError as exc:
            raise _invalid_field("created_at") from exc
        return ModelResponse(
            provider=self.provider,
            model_identifier=_require_string(payload.get("model"), field_name="model"),
            deployment=deployment,
            content=content,
            thinking=_optional_string(message.get("thinking"), field_name="message.thinking"),
            finish_reason=_optional_string(payload.get("done_reason"), field_name="done_reason"),
            created_at=created_at,
            usage=ModelUsage(
                input_tokens=_require_integer(
                    payload.get("prompt_eval_count"), field_name="prompt_eval_count"
                ),
                output_tokens=_require_integer(payload.get("eval_count"), field_name="eval_count"),
            ),
            timing=ModelTiming(
                total_ms=_nanoseconds_to_milliseconds(
                    payload.get("total_duration"), field_name="total_duration"
                ),
                load_ms=_optional_nanoseconds_to_milliseconds(
                    payload.get("load_duration"), field_name="load_duration"
                ),
                prompt_evaluation_ms=_optional_nanoseconds_to_milliseconds(
                    payload.get("prompt_eval_duration"), field_name="prompt_eval_duration"
                ),
                generation_ms=_optional_nanoseconds_to_milliseconds(
                    payload.get("eval_duration"), field_name="eval_duration"
                ),
            ),
            estimated_cost_usd=Decimal("0"),
        )


def _require_mapping(value: object, *, field_name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise _invalid_field(field_name)
    return cast(Mapping[str, Any], value)


def _require_sequence(value: object, *, field_name: str) -> Sequence[object]:
    if isinstance(value, (str, bytes)) or not isinstance(value, Sequence):
        raise _invalid_field(field_name)
    return cast(Sequence[object], value)


def _require_string(value: object, *, field_name: str) -> str:
    if not isinstance(value, str):
        raise _invalid_field(field_name)
    return value


def _optional_string(value: object, *, field_name: str) -> str | None:
    if value is None:
        return None
    return _require_string(value, field_name=field_name)


def _require_integer(value: object, *, field_name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise _invalid_field(field_name)
    return value


def _optional_integer(value: object, *, field_name: str) -> int | None:
    if value is None:
        return None
    return _require_integer(value, field_name=field_name)


def _context_window(model_info: Mapping[str, Any]) -> int | None:
    context_lengths = [
        value
        for key, value in model_info.items()
        if key.endswith(".context_length")
        and isinstance(value, int)
        and not isinstance(value, bool)
    ]
    return max(context_lengths, default=None)


def _nanoseconds_to_milliseconds(value: object, *, field_name: str) -> int:
    return _require_integer(value, field_name=field_name) // 1_000_000


def _optional_nanoseconds_to_milliseconds(value: object, *, field_name: str) -> int | None:
    if value is None:
        return None
    return _nanoseconds_to_milliseconds(value, field_name=field_name)


def _invalid_field(field_name: str) -> ModelGatewayError:
    return ModelGatewayError(
        ModelGatewayErrorCode.INVALID_RESPONSE,
        f"Ollama response field {field_name!r} has an invalid shape",
        retryable=False,
    )
