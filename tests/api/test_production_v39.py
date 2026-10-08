"""Current endpoints bind even when later work remains; no prose keyword inference."""

from __future__ import annotations

import json
from copy import deepcopy
from dataclasses import replace
from pathlib import Path

import pytest
from open_hollywood_api.services.production_model_executor import (
    _Operation,
    _output_schema,
)
from open_hollywood_engine.evaluations import load_benchmark_corpus
from open_hollywood_engine.models import ModelDeployment, ModelRequest, ModelResponse
from sqlalchemy import Engine

from tests.api.test_production_v26 import V26Gateway, _run_gateway
from tests.api.test_production_v29 import _materialize, _raw, _refs
from tests.api.test_production_v37 import _fixture, _payload
from tests.evaluations.test_agentic_blueprint import CORPUS_PATH
from tests.evaluations.test_agentic_production import ProductionFixtureGateway


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.mark.parametrize("deployment", [ModelDeployment.LOCAL, ModelDeployment.CLOUD])
@pytest.mark.parametrize("next_scene", ["present", "absent", "final"])
def test_current_endpoint_can_block_independently_of_future_reservation(
    deployment: ModelDeployment, next_scene: str
) -> None:
    execution = _fixture("Elara decided to check. She verified a general match.")
    execution = replace(execution, selection=replace(execution.selection, deployment=deployment))
    if next_scene == "absent":
        execution.inputs[-1]["content"]["scene_plans"] = []
    elif next_scene == "final":
        execution = replace(execution, unit_count=1)
    original = deepcopy(execution.inputs)
    schema = _output_schema(
        _Operation.CRITIQUE,
        continuity_schema_variant=None,
        critic_execution=execution,
        critic_evidence_refs=tuple(_refs(execution)),
    )
    assert schema["properties"]["scene_boundary_check"]["properties"]["status"]["enum"] == [
        "no_overrun",
        "overrun",
    ]
    raw = _raw(execution)
    raw["scene_boundary_check"].update(
        status="overrun",
        achieved_state="She establishes a handwriting match.",
        current_endpoint_comparison="The assigned decision is exceeded without authorization.",
        next_scene_comparison="A later specific flourish remains, or no next scene is supplied.",
        draft_evidence_refs=[_refs(execution)[-1]],
    )
    result = _materialize(raw, execution)
    assert result["verdict"] == "revise" and result["overall_score"] == 5.0
    issue = result["issues"][0]
    assert issue["category"] == "scene_assignment:outcome" and issue["severity"] == "blocking"
    assert issue["evidence"] == ["She verified a general match."]
    assert "not merely a later detail" in issue["recommendation"]
    assert ("scene_2" in issue["recommendation"]) == (next_scene == "present")
    assert execution.inputs == original


def test_shared_policy_preserves_authority_and_exceptions_through_revision() -> None:
    execution = _fixture()
    for revision in (0, 1):
        revised = replace(execution, revision_number=revision)
        writer = _payload(_Operation.WRITE, revised)
        critic = _payload(_Operation.CRITIQUE, revised)
        assert writer["scene_boundary"] == critic["scene_boundary"]
        policy = writer["scene_boundary"]["policy"]
        assert "even without a next scene" in policy
        assert "more specific later detail or stronger proof does not authorize" in policy
        assert "inconclusive tests and incidental follow-through" in policy
        assert "broad goal/summary cannot override a specific endpoint" in policy


@pytest.mark.parametrize(
    "prose",
    [
        "She tried one letter; the ink smudged. The comparison was inconclusive. "
        "She would try tomorrow.",
        "She decided to investigate tomorrow. She turned off the lamp and checked the lock.",
    ],
)
def test_permitted_tests_and_followthrough_are_not_automatically_blocked(prose: str) -> None:
    execution = _fixture(prose)
    result = _materialize(_raw(execution), execution)
    assert result["verdict"] == "pass" and result["issues"] == []


def test_explicitly_assigned_verification_preserves_current_authority_over_overlap() -> None:
    execution = _fixture("She verified the handwriting but did not trust the warning yet.")
    plan = execution.inputs[0]["content"]
    plan["outcome"] = "She verifies the handwriting while withholding trust in the warning."
    blueprint = execution.inputs[-1]["content"]
    current = next(p for p in blueprint["scene_plans"] if p["id"] == "scene_1")
    current.update(plan)
    payload = _payload(_Operation.CRITIQUE, execution)
    assert payload["scene_assignment_contract"]["outcome"] == plan["outcome"]
    assert payload["scene_boundary"]["next_scene"]["scene_id"] == "scene_2"
    assert _materialize(_raw(execution), execution)["verdict"] == "pass"


class FinalEndpointGateway(V26Gateway):
    async def generate(self, request: ModelRequest) -> ModelResponse:
        response = await ProductionFixtureGateway.generate(self, request)
        payload = json.loads(request.messages[-1].content)
        assignment = payload.get("assignment", {})
        if (
            assignment.get("operation") == "critique"
            and assignment["unit_number"] == assignment["unit_count"]
            and assignment["revision_number"] == 0
        ):
            assert payload["scene_boundary"]["next_scene"] is None
            raw = json.loads(response.content)
            raw["scene_boundary_check"].update(
                status="overrun",
                current_endpoint_comparison="Synthetic material progress past the final endpoint.",
                next_scene_comparison=(
                    "No next scene is supplied; the current endpoint still binds."
                ),
            )
            response = replace(response, content=json.dumps(raw))
        return response


@pytest.mark.anyio
async def test_final_scene_overrun_uses_existing_revision_and_replay(
    migrated_database_path: Path, database_engine: Engine
) -> None:
    prompt = load_benchmark_corpus(CORPUS_PATH).prompts[0]
    gateway = FinalEndpointGateway(prompt.prompt, prompt, mode="endpoint")
    result = await _run_gateway(gateway, migrated_database_path, database_engine)
    assert len(result.result.accepted_units) == 3
    payloads = [json.loads(r.messages[-1].content) for r in gateway.requests]
    writes = [p for p in payloads if p.get("assignment", {}).get("operation") == "write"]
    assert len(writes) == 4
    revised = [p for p in writes if p["assignment"]["revision_number"] == 1]
    assert len(revised) == 1 and revised[0]["scene_boundary"]["next_scene"] is None
    assert (
        revised[0]["revision_contract"]["critic_acceptance_tests"][0]["category"]
        == "scene_assignment:outcome"
    )
