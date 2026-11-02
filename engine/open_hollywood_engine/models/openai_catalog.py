"""Reviewed Responses capabilities and reproducible standard-tier price estimates."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

from open_hollywood_engine.secrets import EnvironmentSecretStore, SecretLeakGuard

type ReasoningEffort = Literal["none", "minimal", "low", "medium", "high", "xhigh", "max"]


class OpenAIModelSpec(BaseModel):
    """Explicit opt-in; a catalog ID alone proves neither features nor prices."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    model_identifier: str = Field(pattern=r"^[a-zA-Z0-9][a-zA-Z0-9._:-]{0,199}$")
    response_model_identifiers: tuple[str, ...] = ()
    context_window: int = Field(gt=0)
    max_output_tokens: int = Field(gt=0)
    # Stay below long-context price transitions unless separately implemented.
    max_input_tokens: int = Field(gt=0, le=272_000)
    supports_text: Literal[True] = True
    supports_structured_output: bool
    reasoning_efforts: tuple[ReasoningEffort, ...] = ()
    default_reasoning_effort: ReasoningEffort | None = None
    input_usd_per_million: str = Field(pattern=r"^\d+(\.\d+)?$")
    cached_input_usd_per_million: str = Field(pattern=r"^\d+(\.\d+)?$")
    output_usd_per_million: str = Field(pattern=r"^\d+(\.\d+)?$")
    # A conservative bound for models with cache-write billing, including when
    # the API does not expose a separate write-token breakdown.
    input_charge_multiplier: str = Field(default="1", pattern=r"^[1-9]\d*(\.\d+)?$")
    pricing_version: str = Field(min_length=1)

    @model_validator(mode="after")
    def validate_effort(self) -> Self:
        if self.default_reasoning_effort is not None:
            if self.default_reasoning_effort not in self.reasoning_efforts:
                raise ValueError("default effort must be supported")
        elif self.reasoning_efforts:
            raise ValueError("reasoning models need an explicit default effort")
        return self


def builtin_model_specs() -> dict[str, OpenAIModelSpec]:
    """Reviewed 2026-11-02; availability is intersected with GET /v1/models."""
    records: list[OpenAIModelSpec] = []
    for identifier, snapshot, context, input_rate, cached, output, efforts, multiplier in (
        (
            "gpt-5.4-nano",
            "2026-03-17",
            400_000,
            "0.20",
            "0.02",
            "1.25",
            ("none", "low", "medium", "high", "xhigh"),
            "1",
        ),
        (
            "gpt-5.4",
            "2026-03-05",
            1_050_000,
            "2.50",
            "0.25",
            "15.00",
            ("none", "low", "medium", "high", "xhigh"),
            "1",
        ),
        (
            "gpt-5.6-luna",
            None,
            1_050_000,
            "0.20",
            "0.02",
            "1.20",
            ("none", "low", "medium", "high", "xhigh", "max"),
            "1.25",
        ),
        (
            "gpt-6.1-sol",
            None,
            1_050_000,
            "2.00",
            "0.10",
            "10.00",
            ("low", "medium", "high", "xhigh", "max"),
            "1.25",
        ),
    ):
        exact = f"{identifier}-{snapshot}" if snapshot else identifier
        for name in dict.fromkeys((identifier, exact)):
            records.append(
                OpenAIModelSpec.model_validate(
                    {
                        "model_identifier": name,
                        "response_model_identifiers": [name, exact],
                        "context_window": context,
                        "max_input_tokens": 272_000,
                        "max_output_tokens": 128_000,
                        "supports_structured_output": True,
                        "reasoning_efforts": efforts,
                        "default_reasoning_effort": efforts[0],
                        "input_usd_per_million": input_rate,
                        "cached_input_usd_per_million": cached,
                        "output_usd_per_million": output,
                        "input_charge_multiplier": multiplier,
                        "pricing_version": "openai-standard-2026-11-02",
                    }
                )
            )
    return {record.model_identifier: record for record in records}


def load_model_specs() -> dict[str, OpenAIModelSpec]:
    """Extend/override reviewed records from a secret-free operator JSON file."""
    records = builtin_model_specs()
    path = os.environ.get("OPEN_HOLLYWOOD_OPENAI_MODELS_PATH")
    if not path:
        return records
    try:
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
        SecretLeakGuard(EnvironmentSecretStore().configured_values()).ensure_safe(
            raw, destination="OpenAI model configuration"
        )
        if not isinstance(raw, list):
            raise ValueError("expected model list")
        additions = [OpenAIModelSpec.model_validate(item) for item in raw]
        if len({item.model_identifier for item in additions}) != len(additions):
            raise ValueError("duplicate model identifiers")
    except (OSError, ValueError, ValidationError):
        # Pydantic diagnostics can contain operator inputs; do not echo them.
        raise ValueError("OpenAI model configuration is invalid") from None
    records.update((item.model_identifier, item) for item in additions)
    return records
