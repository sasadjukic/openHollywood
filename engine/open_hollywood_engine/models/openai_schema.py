"""Adapt closed domain schemas to the strict Responses JSON Schema subset."""

from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy
from typing import Any

from open_hollywood_engine.models.gateway import ModelGatewayError, ModelGatewayErrorCode


def strict_response_schema(schema: Mapping[str, Any]) -> dict[str, Any]:
    """Preserve domain constraints; reject unrepresentable open dictionaries."""
    result = deepcopy(dict(schema))
    if result.get("type") != "object" or "anyOf" in result:
        raise _unsupported()
    _convert(result)
    return result


def _convert(node: dict[str, Any]) -> None:
    if any(
        key in node
        for key in (
            "allOf",
            "not",
            "if",
            "then",
            "else",
            "dependentRequired",
            "dependentSchemas",
            "patternProperties",
            "prefixItems",
            "unevaluatedProperties",
        )
    ):
        raise _unsupported()
    for key in ("default", "title", "discriminator"):
        node.pop(key, None)
    if "const" in node:
        node["enum"] = [node.pop("const")]
    if "oneOf" in node:
        node["anyOf"] = node.pop("oneOf")
    # UUID format is validated by Pydantic at the application boundary.
    if node.get("format") == "uuid":
        node.pop("format")
    if node.get("type") == "object":
        if node.get("additionalProperties", False) is not False:
            raise _unsupported()
        properties = node.setdefault("properties", {})
        if not isinstance(properties, dict):
            raise _unsupported()
        node["additionalProperties"] = False
        node["required"] = list(properties)
    for key in ("properties", "$defs"):
        for child in node.get(key, {}).values():
            _convert(child)
    for key in ("anyOf",):
        for child in node.get(key, []):
            _convert(child)
    if isinstance(node.get("items"), dict):
        _convert(node["items"])


def _unsupported() -> ModelGatewayError:
    return ModelGatewayError(
        ModelGatewayErrorCode.UNSUPPORTED_CAPABILITY,
        "The output schema cannot be represented by OpenAI strict structured output",
        retryable=False,
    )
