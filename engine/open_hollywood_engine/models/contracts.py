"""Provider-neutral contracts for model discovery and generation."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from math import isfinite
from types import MappingProxyType
from typing import Literal
from uuid import UUID

type JsonPrimitive = str | int | float | bool | None
type JsonValue = JsonPrimitive | list[JsonValue] | dict[str, JsonValue]


class ModelDeployment(StrEnum):
    """Where inference for a model is performed."""

    LOCAL = "local"
    CLOUD = "cloud"


class MessageRole(StrEnum):
    """Provider-neutral chat message role."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


@dataclass(frozen=True, slots=True)
class ModelMessage:
    """One message supplied to a chat-capable model."""

    role: MessageRole
    content: str

    def __post_init__(self) -> None:
        if not self.content:
            raise ValueError("message content must not be empty")


@dataclass(frozen=True, slots=True)
class ModelCallBudget:
    """Hard token and monetary envelope for one model call."""

    max_input_tokens: int
    max_output_tokens: int
    max_cost_usd: Decimal = Decimal("0")

    def __post_init__(self) -> None:
        if self.max_input_tokens < 1:
            raise ValueError("max_input_tokens must be positive")
        if self.max_output_tokens < 1:
            raise ValueError("max_output_tokens must be positive")
        if not self.max_cost_usd.is_finite() or self.max_cost_usd < 0:
            raise ValueError("max_cost_usd must be finite and not negative")

    @property
    def max_context_tokens(self) -> int:
        """Return the largest permitted prompt-plus-output context."""
        return self.max_input_tokens + self.max_output_tokens


@dataclass(frozen=True, slots=True)
class ModelSettings:
    """Portable generation controls supported by the initial gateway."""

    temperature: float | None = None
    top_p: float | None = None
    seed: int | None = None
    stop: tuple[str, ...] = ()
    thinking: bool | Literal["low", "medium", "high"] | None = None

    def __post_init__(self) -> None:
        if self.temperature is not None and (
            not isfinite(self.temperature) or self.temperature < 0
        ):
            raise ValueError("temperature must be finite and not negative")
        if self.top_p is not None and (not isfinite(self.top_p) or not 0 <= self.top_p <= 1):
            raise ValueError("top_p must be between 0 and 1")
        if any(not value for value in self.stop):
            raise ValueError("stop sequences must not be empty")


@dataclass(frozen=True, slots=True)
class InvocationContext:
    """Reproducibility identifiers that must accompany a model call."""

    specialist_role: str
    prompt_template_version: str
    input_artifact_version_ids: tuple[UUID, ...] = ()
    model_profile_id: UUID | None = None

    def __post_init__(self) -> None:
        if not self.specialist_role:
            raise ValueError("specialist_role must not be empty")
        if not self.prompt_template_version:
            raise ValueError("prompt_template_version must not be empty")
        if len(set(self.input_artifact_version_ids)) != len(self.input_artifact_version_ids):
            raise ValueError("input artifact version IDs must be unique")


@dataclass(frozen=True, slots=True)
class ModelRequest:
    """Complete provider-neutral input for one observable model call."""

    model_identifier: str
    messages: tuple[ModelMessage, ...]
    budget: ModelCallBudget
    invocation: InvocationContext
    settings: ModelSettings = field(default_factory=ModelSettings)
    response_schema: Mapping[str, JsonValue] | None = None

    def __post_init__(self) -> None:
        if not self.model_identifier:
            raise ValueError("model_identifier must not be empty")
        if not self.messages:
            raise ValueError("at least one message is required")
        if self.response_schema is not None:
            object.__setattr__(self, "response_schema", _freeze_mapping(self.response_schema))


@dataclass(frozen=True, slots=True)
class ModelDescriptor:
    """Stable model-catalog fields returned without provider SDK types."""

    provider: str
    model_identifier: str
    deployment: ModelDeployment
    digest: str | None = None
    parameter_size: str | None = None
    quantization_level: str | None = None
    size_bytes: int | None = None

    def __post_init__(self) -> None:
        if not self.provider or not self.model_identifier:
            raise ValueError("provider and model_identifier must not be empty")
        if self.size_bytes is not None and self.size_bytes < 0:
            raise ValueError("size_bytes must not be negative")


@dataclass(frozen=True, slots=True)
class ModelCapabilities:
    """Discovered features and limits for one exact model identifier."""

    provider: str
    model_identifier: str
    deployment: ModelDeployment
    context_window: int | None
    supports_chat: bool
    supports_tools: bool
    supports_vision: bool
    supports_thinking: bool
    supports_embeddings: bool
    supports_structured_output: bool
    raw_capability_names: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.provider or not self.model_identifier:
            raise ValueError("provider and model_identifier must not be empty")
        if self.context_window is not None and self.context_window < 1:
            raise ValueError("context_window must be positive")


@dataclass(frozen=True, slots=True)
class ModelUsage:
    """Token accounting normalized across providers."""

    input_tokens: int
    output_tokens: int

    def __post_init__(self) -> None:
        if self.input_tokens < 0 or self.output_tokens < 0:
            raise ValueError("token counts must not be negative")


@dataclass(frozen=True, slots=True)
class ModelTiming:
    """Provider timing values normalized to milliseconds."""

    total_ms: int
    load_ms: int | None = None
    prompt_evaluation_ms: int | None = None
    generation_ms: int | None = None

    def __post_init__(self) -> None:
        values = (
            self.total_ms,
            self.load_ms,
            self.prompt_evaluation_ms,
            self.generation_ms,
        )
        if any(value is not None and value < 0 for value in values):
            raise ValueError("timing values must not be negative")


@dataclass(frozen=True, slots=True)
class ModelResponse:
    """Provider-neutral result and observability metadata."""

    provider: str
    model_identifier: str
    deployment: ModelDeployment
    content: str
    thinking: str | None
    finish_reason: str | None
    created_at: datetime
    usage: ModelUsage
    timing: ModelTiming
    estimated_cost_usd: Decimal

    def __post_init__(self) -> None:
        if not self.provider or not self.model_identifier:
            raise ValueError("provider and model_identifier must not be empty")
        if not self.content:
            raise ValueError("response content must not be empty")
        if self.created_at.utcoffset() is None:
            raise ValueError("created_at must include a timezone")
        if self.estimated_cost_usd < 0:
            raise ValueError("estimated_cost_usd must not be negative")


def _freeze_mapping(value: Mapping[str, JsonValue]) -> Mapping[str, JsonValue]:
    """Copy the top-level schema so callers cannot mutate a frozen request."""
    return MappingProxyType(dict(value))
