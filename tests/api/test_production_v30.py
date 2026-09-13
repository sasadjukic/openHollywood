"""Assignment applicability is application-owned; literary judgments remain model-owned."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any, cast

import pytest
from open_hollywood_api.services.production_model_executor import (
    _critic_evidence_catalog,
    _Execution,
    _messages,
    _Operation,
    _output_schema,
    _scene_assignment_contract,
    _StructuredOutputContractError,
)
from open_hollywood_engine.evaluations import load_benchmark_corpus
from open_hollywood_engine.models import ModelDeployment, ModelRequest, ModelResponse
from sqlalchemy import Engine

from tests.api.test_production_v26 import V26Gateway, _run_gateway
from tests.api.test_production_v28 import _execution
from tests.api.test_production_v29 import _materialize, _raw
from tests.evaluations.test_agentic_blueprint import CORPUS_PATH
from tests.evaluations.test_agentic_production import ProductionFixtureGateway


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


def _schema(execution: _Execution, *, bound: bool = True) -> dict[str, Any]:
    return _output_schema(
        _Operation.CRITIQUE,
        continuity_schema_variant=None,
        critic_evidence_refs=tuple(
            item["evidence_ref"] for item in _critic_evidence_catalog(execution)
        ),
        critic_execution=execution if bound else None,
    )


@pytest.mark.parametrize("deployment", [ModelDeployment.LOCAL, ModelDeployment.CLOUD])
@pytest.mark.parametrize(
    "plan,applicable",
    [
        ({"point_of_view_character_id": None, "character_ids": ["elara", "cora"]}, False),
        ({}, False),
        ({"character_ids": ["elara"]}, True),
        ({"point_of_view_character_id": "elara", "outcome": "The gate opens."}, True),
    ],
)
def test_exact_assignment_removes_impossible_choices_without_growing_requests(
    deployment: ModelDeployment, plan: dict[str, object], applicable: bool
) -> None:
    execution = _execution(
        "Elara opens the gate. Cora privately fears the dark.",
        scene_plan=plan,
        deployment=deployment,
    )
    original = deepcopy(execution.inputs)
    generic = _schema(execution, bound=False)
    bound = _schema(execution)
    check = bound["properties"]["point_of_view_check"]
    if applicable:
        assert check == generic["properties"]["point_of_view_check"]
    else:
        assert check == {
            "type": "object",
            "additionalProperties": False,
            "properties": {"status": {"type": "string", "const": "aligned"}},
            "required": ["status"],
        }
    anchors = bound["properties"]["assignment_violations"]["items"]["properties"]["anchor"]["enum"]
    assignment = _scene_assignment_contract(execution)
    assert all(assignment[anchor] for anchor in anchors)
    assert "point_of_view_character_id" not in anchors
    assert "location_id" not in anchors
    assert ("outcome" in anchors) == bool(plan.get("outcome"))
    assert bound["$defs"] == generic["$defs"]
    assert len(json.dumps(bound)) <= len(json.dumps(generic))
    for schema in (generic, bound):
        messages = _messages(
            _Operation.CRITIQUE,
            execution,
            schema,
            continuity_schema_variant=None,
            continuity_model_context=None,
        )
        payload = json.loads(messages[-1].content)
        assert (
            payload["viewpoint_contract"]["assigned_character_id"]
            == assignment["point_of_view_character_id"]
        )
        if deployment is ModelDeployment.CLOUD:
            assert payload["output_schema"] == schema
    assert execution.inputs == original
    assert _materialize(_raw(execution), execution)["verdict"] == "pass"


def test_unassigned_review_cannot_smuggle_a_hard_pov_finding_through_validation() -> None:
    execution = _execution(
        "Cora privately fears the dark.", scene_plan={"character_ids": ["elara", "cora"]}
    )
    with pytest.raises(_StructuredOutputContractError) as failure:
        _materialize(_raw(execution, "pov"), execution)
    assert failure.value.issue_type == "viewpoint_subject_not_other_character"


def test_populated_assignments_and_real_private_access_still_block() -> None:
    execution = _execution(
        "The gate remains closed. Cora secretly knows the key is gone.",
        scene_plan={"point_of_view_character_id": "elara", "outcome": "The gate opens."},
    )
    for route in ("pov", "assignment", "blocking_craft"):
        result = _materialize(_raw(execution, route), execution)
        assert result["verdict"] == "revise"
        assert result["issues"][0]["severity"] == "blocking"
    invalid = _raw(execution, "assignment")
    invalid["assignment_violations"][0]["anchor"] = "location_id"
    with pytest.raises(_StructuredOutputContractError) as failure:
        _materialize(invalid, execution)
    assert failure.value.issue_type == "invalid_assignment_anchor"


class AssignmentSchemaGateway(V26Gateway):
    critic_calls = 0

    async def generate(self, request: ModelRequest) -> ModelResponse:
        payload = json.loads(request.messages[-1].content)
        if payload.get("assignment", {}).get("operation") == "critique":
            self.critic_calls += 1
            assert request.invocation.prompt_template_version == "31"
            assert request.response_schema is not None
            assignment = payload["scene_assignment_contract"]
            properties = cast(dict[str, Any], request.response_schema["properties"])
            if not assignment["point_of_view_character_id"]:
                assert "anyOf" not in properties["point_of_view_check"]
            anchors = properties["assignment_violations"]["items"]["properties"]["anchor"]["enum"]
            assert all(assignment[anchor] for anchor in anchors)
        return await ProductionFixtureGateway.generate(self, request)


@pytest.mark.anyio
async def test_runtime_uses_bound_schema_and_replays_without_new_calls(
    migrated_database_path: Path, database_engine: Engine
) -> None:
    prompt = load_benchmark_corpus(CORPUS_PATH).prompts[0]
    gateway = AssignmentSchemaGateway(prompt.prompt, prompt, mode="schema")
    result = await _run_gateway(gateway, migrated_database_path, database_engine)
    assert len(result.result.accepted_units) == 3
    assert gateway.critic_calls == 3
