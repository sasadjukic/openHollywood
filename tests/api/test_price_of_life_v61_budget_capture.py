"""Keep the fresh budget isolated from the original single-use registration."""

import json

import pytest
from pydantic import ValidationError

from scripts import ordinary_v61_capture as capture
from scripts import price_of_life_v61_budget_capture as fresh
from scripts import price_of_life_v61_capture as original


def test_budget_contract_preserves_one_generation() -> None:
    fields = fresh.BudgetPlan.model_json_schema()["properties"]
    for key, value in {
        "input_tokens": 28000,
        "output_tokens": 8000,
        "context_tokens": 36000,
        "generations": 1,
        "counts": 0,
        "retries": 0,
    }.items():
        assert fields[key]["const"] == value
    assert capture.Plan.model_json_schema()["properties"]["input_tokens"]["const"] == 24000


def test_fresh_manifest_rejects_old_budget_and_preserves_story() -> None:
    if not (fresh.ROOT / "plan.json").exists() or not (original.ROOT / "plan.json").exists():
        pytest.skip("requires both private Price of Life registrations")
    old_bytes = (original.ROOT / "plan.json").read_bytes()
    new_bytes = (fresh.ROOT / "plan.json").read_bytes()
    prior = capture.Plan.model_validate_json(old_bytes)
    plan = fresh.BudgetPlan.model_validate_json(new_bytes)
    assert plan.inputs == prior.inputs and plan.prompt_sha256 == prior.prompt_sha256
    assert plan.run_id != prior.run_id and plan.live_directory != prior.live_directory
    with pytest.raises(ValidationError):
        fresh.BudgetPlan.model_validate_json(old_bytes)
    with pytest.raises(ValidationError):
        capture.Plan.model_validate_json(new_bytes)
    with pytest.raises(ValidationError):
        fresh.BudgetPlan.model_validate_json(
            json.dumps(json.loads(new_bytes) | {"input_tokens": 24000})
        )

    wire = (original.ROOT / "request.json").read_bytes()
    assert wire.count(b'"num_ctx":32000') == 1
    assert (fresh.ROOT / "request.json").read_bytes() == wire.replace(
        b'"num_ctx":32000', b'"num_ctx":36000'
    )
