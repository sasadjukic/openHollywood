"""Provider-neutral model contract tests."""

from decimal import Decimal
from math import nan
from uuid import uuid4

import pytest
from open_hollywood_engine.models import (
    InvocationContext,
    MessageRole,
    ModelCallBudget,
    ModelMessage,
    ModelRequest,
    ModelSettings,
)


def test_call_budget_requires_bounded_positive_token_counts() -> None:
    with pytest.raises(ValueError, match="max_input_tokens"):
        ModelCallBudget(max_input_tokens=0, max_output_tokens=1)
    with pytest.raises(ValueError, match="max_output_tokens"):
        ModelCallBudget(max_input_tokens=1, max_output_tokens=0)
    with pytest.raises(ValueError, match="max_cost_usd"):
        ModelCallBudget(
            max_input_tokens=1,
            max_output_tokens=1,
            max_cost_usd=Decimal("-0.01"),
        )


def test_settings_reject_non_finite_sampling_values() -> None:
    with pytest.raises(ValueError, match="temperature"):
        ModelSettings(temperature=nan)


def test_invocation_context_rejects_duplicate_input_versions() -> None:
    version_id = uuid4()

    with pytest.raises(ValueError, match="must be unique"):
        InvocationContext(
            specialist_role="architect",
            prompt_template_version="architect-v1",
            input_artifact_version_ids=(version_id, version_id),
        )


def test_response_schema_is_copied_into_immutable_request() -> None:
    schema = {"type": "object"}
    request = ModelRequest(
        model_identifier="gemma4:e4b",
        messages=(ModelMessage(MessageRole.USER, "Create a premise."),),
        budget=ModelCallBudget(max_input_tokens=100, max_output_tokens=200),
        invocation=InvocationContext(
            specialist_role="premise",
            prompt_template_version="premise-v1",
        ),
        response_schema=schema,
    )

    schema["type"] = "array"

    assert request.response_schema == {"type": "object"}
