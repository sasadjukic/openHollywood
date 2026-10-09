"""Consolidated current-review routes preserve every obligation and validation gate."""

from __future__ import annotations

import json
from copy import deepcopy
from dataclasses import replace
from pathlib import Path
from typing import Any

import pytest
from open_hollywood_api.persistence.database import create_session_factory
from open_hollywood_api.persistence.models import AgentInvocation
from open_hollywood_api.services.production_model_executor import (
    _Execution,
    _scene_boundary_audit,
    _StructuredOutputContractError,
)
from open_hollywood_engine.evaluations import load_benchmark_corpus
from open_hollywood_engine.models import ModelRequest, ModelResponse
from sqlalchemy import Engine, select

from tests.api.test_production_v26 import V26Gateway, _run_gateway
from tests.api.test_production_v29 import _materialize, _raw, _refs
from tests.api.test_production_v37 import _fixture
from tests.evaluations.test_agentic_blueprint import CORPUS_PATH
from tests.evaluations.test_agentic_production import ProductionFixtureGateway


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


def _duplicate(execution: _Execution) -> dict[str, Any]:
    raw = _raw(execution, "assignment")
    refs = _refs(execution)[:2]
    raw["scene_boundary_check"].update(
        status="overrun",
        draft_evidence_refs=refs,
        current_endpoint_comparison="The draft establishes a result reserved by the endpoint.",
    )
    raw["assignment_violations"][0].update(
        draft_evidence_refs=list(reversed(refs)),
        explanation="The result exceeds the current outcome; retain this assessment.",
        recommended_resolution="Keep the result unresolved; retain this targeted advice.",
    )
    return raw


@pytest.mark.parametrize("anchor", ["outcome", "turning_point"])
def test_same_anchor_and_handle_set_produces_one_lossless_blocker(anchor: str) -> None:
    execution = _fixture("She matched the writing. She accepted the match.")
    if anchor == "turning_point":
        execution.inputs[0]["content"]["outcome"] = None
    raw = _duplicate(execution)
    raw["assignment_violations"][0]["anchor"] = anchor
    before = deepcopy((raw, execution.inputs))
    result = _materialize(raw, execution)
    assert result["verdict"] == "revise" and result["overall_score"] == 5.0
    assert len(result["issues"]) == 1
    issue = result["issues"][0]
    assert issue["category"] == f"scene_assignment:{anchor}"
    assert issue["severity"] == "blocking"
    assert issue["evidence"] == ["She matched the writing.", "She accepted the match."]
    assert raw["scene_boundary_check"]["current_endpoint_comparison"] in issue["description"]
    assert raw["assignment_violations"][0]["explanation"] in issue["description"]
    assert "remove unassigned material advancement" in issue["recommendation"]
    assert raw["assignment_violations"][0]["recommended_resolution"] in issue["recommendation"]
    assert _scene_boundary_audit(raw, execution)["check"] == raw["scene_boundary_check"]
    assert (raw, execution.inputs) == before


@pytest.mark.parametrize("difference", ["anchor", "subset", "disjoint", "same_text"])
def test_distinct_obligations_or_evidence_are_not_consolidated(difference: str) -> None:
    execution = _fixture("The writing matched. The date was wrong. The writing matched.")
    raw = _duplicate(execution)
    violation = raw["assignment_violations"][0]
    if difference == "anchor":
        violation["anchor"] = "turning_point"
    elif difference == "subset":
        violation["draft_evidence_refs"] = [_refs(execution)[0]]
    else:
        raw["scene_boundary_check"]["draft_evidence_refs"] = [_refs(execution)[0]]
        violation["draft_evidence_refs"] = [
            _refs(execution)[-1 if difference == "same_text" else 1]
        ]
    result = _materialize(raw, execution)
    assert result["verdict"] == "revise" and len(result["issues"]) == 2


def test_no_overrun_does_not_consolidate_or_clear_assignment_finding() -> None:
    execution = _fixture()
    raw = _duplicate(execution)
    raw["scene_boundary_check"]["status"] = "no_overrun"
    result = _materialize(raw, execution)
    assert result["verdict"] == "revise" and len(result["issues"]) == 1
    assert "Assignment assessment:" not in result["issues"][0]["description"]


@pytest.mark.parametrize("invalid", ["assignment_evidence", "boundary_evidence", "blank", "twice"])
def test_consolidation_never_bypasses_route_validation(invalid: str) -> None:
    execution = _fixture()
    raw = _duplicate(execution)
    if invalid == "assignment_evidence":
        raw["assignment_violations"][0]["draft_evidence_refs"] = ["stale_handle"]
    elif invalid == "boundary_evidence":
        raw["scene_boundary_check"]["draft_evidence_refs"] = ["stale_handle"]
    elif invalid == "blank":
        raw["assignment_violations"][0]["explanation"] = " "
    else:
        raw["assignment_violations"] *= 2
    with pytest.raises(_StructuredOutputContractError):
        _materialize(raw, execution)


def test_craft_pov_and_missing_turn_survive_consolidation() -> None:
    execution = _fixture("Elara matched it. Cora privately knew it was forged.")
    raw = _duplicate(execution)
    raw["issues"] = _raw(execution, "blocking_craft")["issues"]
    raw["point_of_view_check"] = _raw(execution, "pov")["point_of_view_check"]
    raw["assignment_violations"].append(
        {**raw["assignment_violations"][0], "anchor": "turning_point"}
    )
    result = _materialize(raw, execution)
    assert result["verdict"] == "revise"
    assert {issue["category"] for issue in result["issues"]} == {
        "pacing",
        "scene_assignment:point_of_view_character_id",
        "scene_assignment:turning_point",
        "scene_assignment:outcome",
    }
    assert len(result["issues"]) == 4
    assert all(issue["severity"] == "blocking" for issue in result["issues"])


class ConsolidationGateway(V26Gateway):
    async def generate(self, request: ModelRequest) -> ModelResponse:
        response = await ProductionFixtureGateway.generate(self, request)
        payload = json.loads(request.messages[-1].content)
        assignment = payload.get("assignment", {})
        if (
            assignment.get("operation") == "critique"
            and assignment["unit_number"] == 1
            and assignment["revision_number"] == 0
        ):
            raw = json.loads(response.content)
            raw["scene_boundary_check"]["status"] = "overrun"
            raw["assignment_violations"] = [
                {
                    "anchor": anchor,
                    "draft_evidence_refs": raw["scene_boundary_check"]["draft_evidence_refs"],
                    "explanation": f"Simulated {anchor} mismatch.",
                    "recommended_resolution": f"Restore the assigned {anchor}.",
                }
                for anchor in ("outcome", "turning_point")
            ]
            return replace(response, content=json.dumps(raw))
        return response


@pytest.mark.anyio
async def test_persisted_consolidation_creates_one_shared_repair_test_and_replays(
    migrated_database_path: Path, database_engine: Engine
) -> None:
    prompt = load_benchmark_corpus(CORPUS_PATH).prompts[0]
    gateway = ConsolidationGateway(prompt.prompt, prompt, mode="consolidation")
    result = await _run_gateway(gateway, migrated_database_path, database_engine)
    assert len(result.result.accepted_units) == 3
    payloads = [json.loads(r.messages[-1].content) for r in gateway.requests]
    revised = [p for p in payloads if p.get("assignment", {}).get("revision_number") == 1]
    writer = next(p for p in revised if p["assignment"]["operation"] == "write")
    critic = next(p for p in revised if p["assignment"]["operation"] == "critique")
    tests = writer["revision_contract"]["critic_acceptance_tests"]
    assert critic["repair_acceptance_tests"] == tests
    assert len(tests) == 2
    assert {t["category"] for t in tests} == {
        "scene_assignment:outcome",
        "scene_assignment:turning_point",
    }
    with create_session_factory(database_engine)() as session:
        critics = [
            i
            for i in session.scalars(select(AgentInvocation)).all()
            if i.specialist_role == "scene_critic"
        ]
        assert len(critics) == 4 and all(i.schema_validation_succeeded for i in critics)
        first = next(
            i
            for i in critics
            if i.request_settings["scene_boundary_audit"]["check"]["status"] == "overrun"
        )
        assert len(first.output_versions[0].content["issues"]) == 2
        assert len(first.input_versions) == len(set(v.id for v in first.input_versions))
