"""Small, stateless OpenAI Responses adapter using the existing HTTP transport."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from contextlib import suppress
from datetime import UTC, datetime
from decimal import Decimal
from time import monotonic
from typing import Any, Self

import httpx

from open_hollywood_engine.models.contracts import (
    JsonValue,
    ModelCapabilities,
    ModelDeployment,
    ModelDescriptor,
    ModelRequest,
    ModelResponse,
    ModelTiming,
    ModelUsage,
)
from open_hollywood_engine.models.gateway import ModelGatewayError, ModelGatewayErrorCode
from open_hollywood_engine.models.openai_catalog import OpenAIModelSpec, load_model_specs
from open_hollywood_engine.models.openai_schema import strict_response_schema
from open_hollywood_engine.secrets import (
    EnvironmentSecretStore,
    MissingSecretError,
    ModelSecret,
    SecretLeakError,
    SecretLeakGuard,
    SecretStore,
)


class OpenAIGateway:
    """No SDK retries, hosted tools, conversation state, or stored responses."""

    provider = "openai"

    def __init__(
        self,
        *,
        secret_store: SecretStore | None = None,
        model_specs: Mapping[str, OpenAIModelSpec] | None = None,
        timeout_seconds: float = 120,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        self._store = secret_store or EnvironmentSecretStore()
        self._specs = dict(load_model_specs() if model_specs is None else model_specs)
        self._client = httpx.AsyncClient(
            base_url="https://api.openai.com/v1/",
            timeout=timeout_seconds,
            transport=transport,
            follow_redirects=False,
        )

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *_exc_info: object) -> None:
        await self.close()

    async def close(self) -> None:
        await self._client.aclose()

    def model_spec(self, identifier: str) -> OpenAIModelSpec:
        """Reject guessed capabilities/pricing, including unknown future aliases."""
        try:
            return self._specs[identifier]
        except KeyError:
            raise ModelGatewayError(
                ModelGatewayErrorCode.UNSUPPORTED_CAPABILITY,
                "OpenAI model needs a reviewed capability and pricing record",
                retryable=False,
            ) from None

    async def list_models(self) -> tuple[ModelDescriptor, ...]:
        payload = await self._request_json("GET", "models")
        entries = payload.get("data")
        if not isinstance(entries, list):
            raise _invalid()
        available: set[str] = set()
        for item in entries:
            if not isinstance(item, dict) or not isinstance(item.get("id"), str):
                raise _invalid()
            available.add(item["id"])
        return tuple(
            ModelDescriptor(
                provider=self.provider, model_identifier=name, deployment=ModelDeployment.CLOUD
            )
            for name in sorted(available.intersection(self._specs))
            if self._specs[name].supports_structured_output
        )

    async def capabilities(self, model_identifier: str) -> ModelCapabilities:
        spec = self.model_spec(model_identifier)
        return ModelCapabilities(
            provider=self.provider,
            model_identifier=model_identifier,
            deployment=ModelDeployment.CLOUD,
            context_window=spec.context_window,
            supports_chat=True,
            supports_tools=False,
            supports_vision=False,
            supports_thinking=bool(spec.reasoning_efforts),
            supports_embeddings=False,
            supports_structured_output=spec.supports_structured_output,
            raw_capability_names=("responses_text", "reviewed_capability_record"),
        )

    async def generate(self, request: ModelRequest) -> ModelResponse:
        spec = self.model_spec(request.model_identifier)
        if request.provider not in (None, self.provider) or request.deployment not in (
            None,
            ModelDeployment.CLOUD,
        ):
            raise _invalid("OpenAI request has a mismatched provider or deployment")
        body, metadata = self._body(request, spec)
        try:
            return await self._generate(request, spec, body, metadata)
        except ModelGatewayError as error:
            error.metadata = metadata
            raise

    async def _generate(
        self,
        request: ModelRequest,
        spec: OpenAIModelSpec,
        body: dict[str, Any],
        metadata: dict[str, JsonValue],
    ) -> ModelResponse:
        budget = request.budget
        if budget.max_output_tokens > spec.max_output_tokens:
            raise _budget("Output budget exceeds the reviewed model limit")
        if _cost(spec, 0, budget.max_output_tokens) > budget.max_cost_usd:
            raise _budget("Output reservation exceeds the call dollar budget")
        started = monotonic()
        # Count exactly the same model/input/schema before any generation. Counting
        # does not generate tokens and has no automatic fallback to an estimate.
        counted = await self._request_json(
            "POST",
            "responses/input_tokens",
            {
                key: value
                for key, value in body.items()
                if key in ("model", "input", "text", "reasoning")
            },
        )
        input_tokens = _integer(counted.get("input_tokens"))
        if input_tokens > min(budget.max_input_tokens, spec.max_input_tokens):
            raise _budget("Counted input exceeds the call or reviewed model input limit")
        if input_tokens + budget.max_output_tokens > spec.context_window:
            raise _budget("Input and output reservation exceed the model context window")
        reserved = _cost(spec, input_tokens, budget.max_output_tokens)
        if reserved > budget.max_cost_usd:
            raise _budget("Counted input and output reservation exceed the call dollar budget")
        metadata.update(
            {
                "counted_input_tokens": input_tokens,
                "reserved_cost_usd": str(reserved),
                "request_sha256": hashlib.sha256(
                    json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
                ).hexdigest(),
            }
        )
        payload = await self._request_json("POST", "responses", body)
        try:
            response = self._parse(payload, request, spec, metadata, started)
        except (ValueError, TypeError, OverflowError, AttributeError):
            raise _invalid() from None
        if (
            response.usage.input_tokens > budget.max_input_tokens
            or response.usage.output_tokens > budget.max_output_tokens
            or response.estimated_cost_usd > budget.max_cost_usd
        ):
            raise ModelGatewayError(
                ModelGatewayErrorCode.BUDGET_EXCEEDED,
                "OpenAI reported usage beyond the call budget",
                retryable=False,
                response=response,
            )
        return response

    def _body(
        self,
        request: ModelRequest,
        spec: OpenAIModelSpec,
    ) -> tuple[dict[str, Any], dict[str, JsonValue]]:
        return render_responses_body(request, spec)

    def _parse(
        self,
        payload: dict[str, Any],
        request: ModelRequest,
        spec: OpenAIModelSpec,
        metadata: dict[str, JsonValue],
        started: float,
    ) -> ModelResponse:
        model = payload.get("model")
        if model not in (spec.model_identifier, *spec.response_model_identifiers):
            raise _invalid("OpenAI returned an unregistered model identifier")
        raw_usage = payload.get("usage")
        if not isinstance(raw_usage, dict):
            raise _invalid()
        usage = ModelUsage(
            input_tokens=_integer(raw_usage.get("input_tokens")),
            output_tokens=_integer(raw_usage.get("output_tokens")),
            reasoning_tokens=_integer(
                (raw_usage.get("output_tokens_details") or {}).get("reasoning_tokens", 0)
            ),
            cached_input_tokens=_integer(
                (raw_usage.get("input_tokens_details") or {}).get("cached_tokens", 0)
            ),
        )
        output = payload.get("output")
        if not isinstance(output, list):
            raise _invalid()
        texts: list[str] = []
        refused = False
        for item in output:
            if not isinstance(item, dict):
                raise _invalid()
            if item.get("type") == "reasoning":
                continue  # Never persist raw/encrypted reasoning.
            if item.get("type") != "message" or item.get("role") != "assistant":
                raise _invalid()
            for part in item.get("content", []):
                if part.get("type") == "refusal":
                    refused = True
                elif part.get("type") == "output_text" and isinstance(part.get("text"), str):
                    texts.append(part["text"])
                else:
                    raise _invalid()
        status = payload.get("status")
        if (payload.get("incomplete_details") or {}).get("reason") == "content_filter":
            refused = True
        content = "".join(texts)
        metadata.update(
            {
                "reasoning_tokens": usage.reasoning_tokens,
                "cached_input_tokens": usage.cached_input_tokens,
                "response_status": status,
            }
        )
        response = ModelResponse(
            provider=self.provider,
            model_identifier=request.model_identifier,
            provider_model_identifier=model,
            deployment=ModelDeployment.CLOUD,
            content=content or "[No usable text returned]",
            thinking=None,
            finish_reason="stop" if status == "completed" and not refused else "incomplete",
            created_at=datetime.fromtimestamp(_integer(payload.get("created_at")), UTC),
            usage=usage,
            timing=ModelTiming(total_ms=max(0, int((monotonic() - started) * 1000))),
            estimated_cost_usd=_cost(
                spec, usage.input_tokens, usage.output_tokens, usage.cached_input_tokens
            ),
            metadata=metadata,
        )
        if refused or status != "completed" or not content:
            code = (
                ModelGatewayErrorCode.REFUSAL
                if refused
                else ModelGatewayErrorCode.TRUNCATED
                if status == "incomplete"
                else ModelGatewayErrorCode.INVALID_RESPONSE
            )
            raise ModelGatewayError(
                code,
                (
                    "OpenAI refused the selected specialist request"
                    if refused
                    else "OpenAI did not return a complete usable response"
                ),
                retryable=False,
                response=response,
            )
        return response

    async def _request_json(
        self,
        method: str,
        path: str,
        body: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        guard = SecretLeakGuard(
            self._store.configured_values()
            if isinstance(self._store, EnvironmentSecretStore)
            else tuple(
                value for handle in ModelSecret if (value := self._store.get(handle)) is not None
            )
        )
        try:
            guard.ensure_safe(body, destination="model request")
            secret = self._store.require(ModelSecret.OPENAI_API_KEY)
        except SecretLeakError:
            raise _secret_error() from None
        except MissingSecretError:
            raise ModelGatewayError(
                ModelGatewayErrorCode.AUTHENTICATION,
                "Set OPENAI_OH_KEY in the API/worker process environment",
                retryable=False,
            ) from None
        try:
            response = await self._client.request(
                method,
                path,
                json=body,
                headers={
                    "Authorization": f"Bearer {secret.reveal()}",
                    "Accept": "application/json",
                },
            )
        except httpx.TimeoutException:
            # Retrying an uncertain generation may charge twice; workflow/operator
            # recovery is explicit. Only definite rejection errors are retryable.
            raise ModelGatewayError(
                ModelGatewayErrorCode.PROVIDER_TIMEOUT,
                "OpenAI request timed out",
                retryable=False,
            ) from None
        except httpx.TransportError:
            raise ModelGatewayError(
                ModelGatewayErrorCode.PROVIDER_UNAVAILABLE,
                "OpenAI is unavailable",
                retryable=False,
            ) from None
        if response.status_code >= 300:
            status = response.status_code
            code = (
                ModelGatewayErrorCode.AUTHENTICATION
                if status in (401, 403)
                else ModelGatewayErrorCode.MODEL_NOT_FOUND
                if status == 404
                else ModelGatewayErrorCode.RATE_LIMITED
                if status == 429
                else ModelGatewayErrorCode.PROVIDER_UNAVAILABLE
                if status >= 500
                else ModelGatewayErrorCode.INVALID_RESPONSE
            )
            quota = False
            if status == 429:
                with suppress(ValueError, AttributeError):
                    quota = response.json().get("error", {}).get("code") in (
                        "insufficient_quota",
                        "billing_hard_limit_reached",
                    )
            raise ModelGatewayError(
                code,
                (
                    "OpenAI account quota or billing limit prevents the request"
                    if quota
                    else f"OpenAI request failed with HTTP {status}"
                ),
                retryable=status == 429 and not quota,
            )
        try:
            payload = response.json()
            guard.ensure_safe(payload, destination="provider response")
        except SecretLeakError:
            raise _secret_error() from None
        except ValueError:
            raise _invalid() from None
        if not isinstance(payload, dict):
            raise _invalid()
        return payload


def _cost(spec: OpenAIModelSpec, inputs: int, outputs: int, cached: int = 0) -> Decimal:
    return (
        Decimal(inputs - cached)
        * Decimal(spec.input_usd_per_million)
        * Decimal(spec.input_charge_multiplier)
        + Decimal(cached) * Decimal(spec.cached_input_usd_per_million)
        + Decimal(outputs) * Decimal(spec.output_usd_per_million)
    ) / Decimal(1_000_000)


def _integer(value: object) -> int:
    if type(value) is not int or value < 0:
        raise _invalid()
    return value


def _invalid(message: str = "OpenAI response metadata has an invalid shape") -> ModelGatewayError:
    return ModelGatewayError(ModelGatewayErrorCode.INVALID_RESPONSE, message, retryable=False)


def _budget(message: str) -> ModelGatewayError:
    return ModelGatewayError(ModelGatewayErrorCode.BUDGET_EXCEEDED, message, retryable=False)


def _secret_error() -> ModelGatewayError:
    return ModelGatewayError(
        ModelGatewayErrorCode.SECRET_EXPOSURE,
        "OpenAI payload rejected by the secret policy",
        retryable=False,
    )


def render_responses_body(
    request: ModelRequest, spec: OpenAIModelSpec
) -> tuple[dict[str, Any], dict[str, JsonValue]]:
    """Pure shared serializer; no client, credentials, catalog lookup or network."""
    settings = request.settings
    if settings.stop:
        raise ModelGatewayError(
            ModelGatewayErrorCode.UNSUPPORTED_CAPABILITY,
            "OpenAI Responses does not support stop sequences",
            retryable=False,
        )
    effort = spec.default_reasoning_effort
    if isinstance(settings.thinking, str):
        if settings.thinking not in spec.reasoning_efforts:
            raise ModelGatewayError(
                ModelGatewayErrorCode.UNSUPPORTED_CAPABILITY,
                "The requested reasoning effort is unsupported for this model",
                retryable=False,
            )
        effort = settings.thinking
    elif settings.thinking is True:
        if "medium" not in spec.reasoning_efforts:
            raise ModelGatewayError(
                ModelGatewayErrorCode.UNSUPPORTED_CAPABILITY,
                "This model does not support reasoning",
                retryable=False,
            )
        effort = "medium"
    body: dict[str, Any] = {
        "model": request.model_identifier,
        "input": [
            {"role": message.role.value, "content": message.content} for message in request.messages
        ],
        "store": False,
        "background": False,
        "stream": False,
        "service_tier": "default",
        "truncation": "disabled",
        "max_output_tokens": request.budget.max_output_tokens,
    }
    if effort is not None:
        body["reasoning"] = {"effort": effort}
    omitted: list[JsonValue] = []
    if settings.seed is not None:
        omitted.append("seed")  # Responses has no deterministic seed parameter.
    for name, value in (("temperature", settings.temperature), ("top_p", settings.top_p)):
        if value is not None:
            if effort in (None, "none"):
                if name == "temperature" and value > 2:
                    raise ModelGatewayError(
                        ModelGatewayErrorCode.UNSUPPORTED_CAPABILITY,
                        "OpenAI temperature must be between zero and two",
                        retryable=False,
                    )
                body[name] = value
            else:
                omitted.append(name)
    if request.response_schema is not None:
        if not spec.supports_structured_output:
            raise ModelGatewayError(
                ModelGatewayErrorCode.UNSUPPORTED_CAPABILITY,
                "This OpenAI model does not support strict structured output",
                retryable=False,
            )
        body["text"] = {
            "format": {
                "type": "json_schema",
                "name": "open_hollywood_output",
                "strict": True,
                "schema": strict_response_schema(request.response_schema),
            }
        }
    metadata: dict[str, JsonValue] = {
        "adapter_version": "openai-responses-1",
        "effective_settings": {
            key: value for key, value in body.items() if key not in ("input", "model", "text")
        },
        "omitted_portable_settings": omitted,
        "schema_enforced": request.response_schema is not None,
        "pricing": spec.model_dump(mode="json"),
        "cost_estimate_kind": "published_rates_conservative_cache_write_bound",
    }
    if "text" in body:
        metadata["schema_sha256"] = hashlib.sha256(
            json.dumps(body["text"], sort_keys=True).encode()
        ).hexdigest()
    return body, metadata
