"""Gateway interface and normalized model-provider failures."""

from __future__ import annotations

from enum import StrEnum
from typing import Protocol

from open_hollywood_engine.models.contracts import (
    ModelCapabilities,
    ModelDescriptor,
    ModelRequest,
    ModelResponse,
)


class ModelGatewayErrorCode(StrEnum):
    """Stable failure categories for routing and workflow decisions."""

    AUTHENTICATION = "authentication"
    BUDGET_EXCEEDED = "budget_exceeded"
    INVALID_RESPONSE = "invalid_response"
    MODEL_NOT_FOUND = "model_not_found"
    PROVIDER_UNAVAILABLE = "provider_unavailable"
    RATE_LIMITED = "rate_limited"
    SECRET_EXPOSURE = "secret_exposure"
    UNSUPPORTED_CAPABILITY = "unsupported_capability"


class ModelGatewayError(RuntimeError):
    """Provider-neutral exception safe to persist in workflow records."""

    def __init__(
        self,
        code: ModelGatewayErrorCode,
        message: str,
        *,
        retryable: bool,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.retryable = retryable


class ModelGateway(Protocol):
    """Async provider-neutral boundary used by creative workflows."""

    @property
    def provider(self) -> str:
        """Return the stable provider identifier."""
        ...

    async def list_models(self) -> tuple[ModelDescriptor, ...]:
        """Discover models available to this configured endpoint."""
        ...

    async def capabilities(self, model_identifier: str) -> ModelCapabilities:
        """Discover capabilities for one exact model identifier."""
        ...

    async def generate(self, request: ModelRequest) -> ModelResponse:
        """Generate one complete non-streaming response."""
        ...

    async def close(self) -> None:
        """Release network resources owned by the gateway."""
        ...
