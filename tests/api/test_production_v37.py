"""Shared scene reservations and existing hard gates; judgments here are simulated."""

from __future__ import annotations

import json
from copy import deepcopy
from dataclasses import replace
from pathlib import Path
from typing import Any, cast
from uuid import UUID

import pytest
from open_hollywood_api.services.production_model_executor import (
    _critic_prompt_inputs,
    _Execution,
    _messages,
    _Operation,
    _output_schema,
    _scene_boundary_contract,
)
from open_hollywood_engine.evaluations import load_benchmark_corpus
from open_hollywood_engine.models import ModelDeployment, ModelRequest, ModelResponse
from open_hollywood_engine.workflows import SceneProductionError
from sqlalchemy import Engine

from tests.api.test_production_v26 import V26Gateway, _run_gateway
from tests.api.test_production_v28 import _execution
from tests.api.test_production_v29 import _materialize, _raw, _refs
from tests.evaluations.test_agentic_blueprint import CORPUS_PATH
from tests.evaluations.test_agentic_production import ProductionFixtureGateway


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


def _fixture(prose: str = "Elara decides to examine the letter.") -> _Execution:
    execution = _execution(
        prose,
        scene_plan={
            "scene_number": 1,
            "character_ids": ["elara"],
            "turning_point": "The letter is dated ten years ahead.",
            "outcome": "Elara decides to verify the handwriting.",
            "exit_state": "Suspicious, ready to investigate.",
        },
    )
    blueprint = next(a for a in execution.inputs if a["artifact_kind"] == "story_blueprint")
    blueprint["content"].update(
        story_arc="Elara verifies the writing, rejects the offer and leaves town.",
        proposed_ending="She leaves town.",
        scene_plans=[
            {"id": "scene_3", "scene_number": 3, "outcome": "She leaves town."},
            {
                "id": "scene_2",
                "scene_number": 2,
                "turning_point": "A private flourish proves the handwriting is hers.",
                "outcome": "She accepts the letter as a genuine warning.",
                "required_elements": [],
                "summary": "Full future scene detail must not enter the current scope.",
            },
            deepcopy(execution.inputs[0]["content"]),
        ],
    )
    return replace(
        execution,
        unit_count=3,
        input_version_ids=tuple(UUID(a["artifact_version_id"]) for a in execution.inputs),
    )


def _payload(operation: _Operation, execution: _Execution) -> dict[str, Any]:
    messages = _messages(
        operation,
        execution,
        _output_schema(operation, continuity_schema_variant=None),
        continuity_schema_variant=None,
        continuity_model_context=None,
    )
    return cast(dict[str, Any], json.loads(messages[-1].content))


@pytest.mark.parametrize("deployment", [ModelDeployment.LOCAL, ModelDeployment.CLOUD])
@pytest.mark.parametrize("revision", [0, 1])
def test_both_roles_receive_same_exact_adjacent_reservation_without_mutating_sources(
    deployment: ModelDeployment, revision: int
) -> None:
    execution = _fixture()
    execution = replace(
        execution,
        selection=replace(execution.selection, deployment=deployment),
        revision_number=revision,
    )
    inputs = deepcopy(execution.inputs)
    writer = _payload(_Operation.WRITE, execution)
    critic = _payload(_Operation.CRITIQUE, execution)
    assert writer["scene_boundary"] == critic["scene_boundary"]
    boundary = writer["scene_boundary"]
    assert boundary["current_plan_version_id"] == inputs[0]["artifact_version_id"]
    blueprint = next(a for a in inputs if a["artifact_kind"] == "story_blueprint")
    assert boundary["next_scene"] == {
        "blueprint_version_id": blueprint["artifact_version_id"],
        "scene_id": "scene_2",
        "turning_point": blueprint["content"]["scene_plans"][1]["turning_point"],
        "outcome": blueprint["content"]["scene_plans"][1]["outcome"],
    }
    for payload in (writer, critic):
        projected = next(
            a for a in payload["input_artifacts"] if a["artifact_kind"] == "story_blueprint"
        )
        assert "story_arc" not in projected["content"]
        assert "proposed_ending" not in projected["content"]
        assert (
            projected["content"]["voice_and_style_guide"]
            == blueprint["content"]["voice_and_style_guide"]
        )
        assert all(p["id"] == "scene_1" for p in projected["content"].get("scene_plans", []))
        assert {a["artifact_version_id"] for a in payload["input_artifacts"]} == {
            str(value) for value in execution.input_version_ids
        }
    assert execution.inputs == inputs
    # Adjudication keeps its previous context; the new reservation is not its job.
    old_scope = _critic_prompt_inputs(execution, boundary=False)
    old_blueprint = next(a for a in old_scope if a["artifact_kind"] == "story_blueprint")
    assert old_blueprint["content"]["story_arc"] == blueprint["content"]["story_arc"]


def test_final_scene_keeps_approved_ending_and_has_no_invented_reservation() -> None:
    execution = _fixture()
    execution.inputs[0]["content"].update(id="scene_3", scene_number=3)
    execution = replace(execution, unit_id="scene_3", unit_number=3)
    payload = _payload(_Operation.WRITE, execution)
    assert payload["scene_boundary"]["next_scene"] is None
    blueprint = next(
        a for a in payload["input_artifacts"] if a["artifact_kind"] == "story_blueprint"
    )
    assert blueprint["content"]["proposed_ending"] == "She leaves town."


def test_no_distant_or_ambiguous_scene_can_become_the_next_reservation() -> None:
    execution = _fixture()
    blueprint = next(a for a in execution.inputs if a["artifact_kind"] == "story_blueprint")
    plans = blueprint["content"]["scene_plans"]
    next_plan = plans.pop(1)
    assert _scene_boundary_contract(execution)["next_scene"] is None
    plans.extend([next_plan, deepcopy(next_plan)])
    with pytest.raises(SceneProductionError, match="unambiguous"):
        _scene_boundary_contract(execution)


def test_reported_overrun_blocks_despite_achieved_current_outcome_and_perfect_scores() -> None:
    execution = _fixture(
        "Elara decided to verify the writing. The private flourish proved a match."
    )
    raw = _raw(execution)
    raw["assignment_violations"] = [
        {
            "anchor": "outcome",
            "draft_evidence_refs": [_refs(execution)[-1]],
            "explanation": "The decision occurs, but so does scene 2's conclusive verification.",
            "recommended_resolution": "Stop at the decision; reserve verification for scene 2.",
        }
    ]
    result = _materialize(raw, execution)
    assert result["overall_score"] == 5.0
    assert result["verdict"] == "revise"
    issue = result["issues"][0]
    assert issue["category"] == "scene_assignment:outcome"
    assert issue["severity"] == "blocking"
    assert "The private flourish proved a match." in issue["evidence"]


@pytest.mark.parametrize(
    "prose",
    [
        "Elara decided to compare the handwriting tomorrow. She switched off the lamp.",
        "Perhaps her private flourish would reveal a match. She would check tomorrow.",
    ],
)
def test_stopping_and_foreshadowing_do_not_acquire_automatic_keyword_blockers(prose: str) -> None:
    execution = _fixture(prose)
    assert _materialize(_raw(execution), execution)["verdict"] == "pass"


def test_verification_moves_into_current_assignment_and_explicit_overlap_is_preserved() -> None:
    execution = _fixture("The private flourish proved a match.")
    blueprint = next(a for a in execution.inputs if a["artifact_kind"] == "story_blueprint")
    execution.inputs[0]["content"] = deepcopy(blueprint["content"]["scene_plans"][1])
    execution.inputs[1]["content"].update(scene_id="scene_2", scene_number=2)
    execution = replace(execution, unit_id="scene_2", unit_number=2)
    payload = _payload(_Operation.CRITIQUE, execution)
    assert payload["scene_boundary"]["next_scene"]["scene_id"] == "scene_3"
    assert payload["scene_assignment_contract"]["turning_point"].startswith("A private flourish")
    assert _materialize(_raw(execution), execution)["verdict"] == "pass"
    # Compiler preserves approved overlap; it must not invent a textual subtraction rule.
    blueprint["content"]["scene_plans"][0]["outcome"] = execution.inputs[0]["content"]["outcome"]
    overlap = _payload(_Operation.CRITIQUE, execution)
    assert (
        overlap["scene_boundary"]["next_scene"]["outcome"]
        == overlap["scene_assignment_contract"]["outcome"]
    )
    assert "current approved plan governs any overlap" in overlap["scene_boundary"]["policy"]


class BoundaryGateway(V26Gateway):
    async def generate(self, request: ModelRequest) -> ModelResponse:
        response = await ProductionFixtureGateway.generate(self, request)
        payload = json.loads(request.messages[-1].content)
        assignment = payload.get("assignment", {})
        if (
            assignment.get("operation") == "critique"
            and assignment.get("unit_number") == 1
            and assignment.get("revision_number") == 0
        ):
            raw = json.loads(response.content)
            draft = next(
                a for a in payload["input_artifacts"] if a["artifact_kind"] == "scene_draft"
            )
            raw["assignment_violations"] = [
                {
                    "anchor": "outcome",
                    "draft_evidence_refs": [
                        draft["content"]["evidence_catalog"][-1]["evidence_ref"]
                    ],
                    "explanation": "Synthetic boundary overrun for routing verification.",
                    "recommended_resolution": "Reserve the next scene's central turn.",
                }
            ]
            response = replace(response, content=json.dumps(raw))
        return response


@pytest.mark.anyio
async def test_boundary_survives_real_revision_lineage_and_replay(
    migrated_database_path: Path, database_engine: Engine
) -> None:
    prompt = load_benchmark_corpus(CORPUS_PATH).prompts[0]
    gateway = BoundaryGateway(prompt.prompt, prompt, mode="boundary")
    result = await _run_gateway(gateway, migrated_database_path, database_engine)
    assert len(result.result.accepted_units) == 3
    payloads = [json.loads(request.messages[-1].content) for request in gateway.requests]
    reviews = [
        p
        for p in payloads
        if p.get("assignment", {}).get("operation") in {"write", "critique"}
        and p["assignment"]["unit_number"] == 1
    ]
    assert len(reviews) == 4  # writer/critic, initial + revision; no extra boundary role
    assert all(p["scene_boundary"] == reviews[0]["scene_boundary"] for p in reviews)
    revised_writer = next(
        p
        for p in reviews
        if p["assignment"]["operation"] == "write" and p["assignment"]["revision_number"] == 1
    )
    revised_critic = next(
        p
        for p in reviews
        if p["assignment"]["operation"] == "critique" and p["assignment"]["revision_number"] == 1
    )
    assert (
        revised_writer["revision_contract"]["critic_acceptance_tests"]
        == revised_critic["repair_acceptance_tests"]
    )
    assert revised_critic["repair_acceptance_tests"][0]["category"] == "scene_assignment:outcome"
