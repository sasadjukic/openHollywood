"""Satisfied repair grammar and independently reported current obligations."""

from __future__ import annotations

import json
from copy import deepcopy
from dataclasses import replace
from pathlib import Path
from typing import Any

import pytest
from open_hollywood_api.services.production_model_executor import (
    _INSTRUCTIONS,
    _messages,
    _Operation,
    _output_schema,
    _StructuredOutputContractError,
)
from open_hollywood_engine.evaluations import load_benchmark_corpus
from open_hollywood_engine.models import ModelDeployment, ModelRequest, ModelResponse
from sqlalchemy import Engine

from tests.api.test_production_v26 import _run_gateway
from tests.api.test_production_v29 import _materialize, _refs
from tests.api.test_production_v31 import _review
from tests.api.test_production_v37 import _fixture
from tests.api.test_production_v41 import LinkedRepairGateway, _revision
from tests.evaluations.test_agentic_blueprint import CORPUS_PATH


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.mark.parametrize("deployment", [ModelDeployment.LOCAL, ModelDeployment.CLOUD])
def test_satisfied_repair_schema_has_no_nonempty_link_branch(deployment: ModelDeployment) -> None:
    execution = _revision()
    execution = replace(execution, selection=replace(execution.selection, deployment=deployment))
    schema = _output_schema(
        _Operation.CRITIQUE, continuity_schema_variant=None, critic_execution=execution
    )
    met, unmet = schema["$defs"]["RepairAcceptanceCheck"]["anyOf"]
    assert met["properties"]["status"] == {"type": "string", "const": "met"}
    assert met["properties"]["current_finding_refs"]["maxItems"] == 0
    assert unmet["properties"]["status"] == {"type": "string", "const": "unmet"}
    assert unmet["properties"]["current_finding_refs"]["maxItems"] == 16
    for branch in (met, unmet):
        assert branch["additionalProperties"] is False
        assert set(branch["required"]) == {
            "status",
            "assessment",
            "draft_evidence_refs",
            "current_finding_refs",
        }
        assert "different current defect" in branch["properties"]["assessment"]["description"]
    initial = _output_schema(
        _Operation.CRITIQUE, continuity_schema_variant=None, critic_execution=_fixture()
    )
    assert "RepairAcceptanceCheck" not in initial["$defs"]
    messages = _messages(
        _Operation.CRITIQUE,
        execution,
        schema,
        continuity_schema_variant=None,
        continuity_model_context=None,
    )
    packet = json.loads(messages[-1].content)
    if deployment is ModelDeployment.CLOUD:
        assert packet["output_schema"] == schema
    else:
        assert "output_schema" not in packet
    assert "missing turning_point needs its own" in _INSTRUCTIONS[_Operation.CRITIQUE]


def test_met_repair_links_are_rejected_instead_of_silently_cleared() -> None:
    execution = _revision()
    raw = _review(execution)
    check = next(iter(raw["repair_checks"].values()))
    check["current_finding_refs"] = ["assignment:outcome"]
    before = deepcopy(raw)
    with pytest.raises(_StructuredOutputContractError, match="otherwise"):
        _materialize(raw, execution)
    assert raw == before


@pytest.mark.parametrize("old_status", ["met", "unmet"])
def test_missing_turn_is_an_independent_target_with_either_old_repair_status(
    old_status: str,
) -> None:
    execution = _revision()
    raw = _review(execution, old_status)
    raw["assignment_violations"] = [
        {
            "anchor": "turning_point",
            "draft_evidence_refs": [_refs(execution)[1]],
            "explanation": "The required future-date realization is missing.",
            "recommended_resolution": (
                "Restore the future-date realization while keeping the comparison inconclusive."
            ),
        }
    ]
    result = _materialize(raw, execution)
    assert result["verdict"] == "revise"
    assert [i["category"] for i in result["issues"]] == (
        ["scene_assignment:turning_point"]
        if old_status == "met"
        else ["scene_assignment:turning_point", "scene_assignment:outcome"]
    )
    # A turn may not be swallowed by linking it to an original outcome repair.
    next(iter(raw["repair_checks"].values()))["current_finding_refs"] = ["assignment:turning_point"]
    with pytest.raises(_StructuredOutputContractError):
        _materialize(raw, execution)


def test_assessment_text_alone_does_not_manufacture_a_new_manuscript_defect() -> None:
    execution = _revision()
    raw = _review(execution)
    next(iter(raw["repair_checks"].values()))["assessment"] = (
        "Original repair met. Another turn may be missing."
    )
    assert _materialize(raw, execution)["issues"] == []


class IndependentRepairGateway(LinkedRepairGateway):
    def __init__(self, *args: Any, original_unmet: bool) -> None:
        super().__init__(*args, invalid_once=False)
        self.original_unmet = original_unmet

    async def generate(self, request: ModelRequest) -> ModelResponse:
        response = await super().generate(request)
        payload = json.loads(request.messages[-1].content)
        assignment = payload.get("assignment", {})
        if assignment.get("operation") != "critique" or assignment["revision_number"] != 1:
            return response
        raw = json.loads(response.content)
        raw["scene_boundary_check"]["status"] = "no_overrun"
        if not self.original_unmet:
            raw["assignment_violations"] = []
        raw["assignment_violations"].append(
            {
                "anchor": "turning_point",
                "draft_evidence_refs": raw["scene_boundary_check"]["draft_evidence_refs"],
                "explanation": "Simulated independent missing current turn.",
                "recommended_resolution": "Restore only the missing turn.",
            }
        )
        for check in raw["repair_checks"].values():
            check.update(
                status="unmet" if self.original_unmet else "met",
                current_finding_refs=["assignment:outcome"] if self.original_unmet else [],
                assessment="Only the original outcome obligation is assessed here.",
            )
        return replace(response, content=json.dumps(raw))


@pytest.mark.anyio
@pytest.mark.parametrize("original_unmet", [False, True])
async def test_independent_turn_reaches_next_writer_and_critic_with_its_own_test(
    original_unmet: bool,
    migrated_database_path: Path,
    database_engine: Engine,
) -> None:
    prompt = load_benchmark_corpus(CORPUS_PATH).prompts[0]
    gateway = IndependentRepairGateway(prompt.prompt, prompt, original_unmet=original_unmet)
    result = await _run_gateway(gateway, migrated_database_path, database_engine)
    assert len(result.result.accepted_units) == 3
    payloads = [json.loads(r.messages[-1].content) for r in gateway.requests]
    revised_writers = [
        p
        for p in payloads
        if p.get("assignment", {}).get("operation") == "write"
        and p["assignment"]["revision_number"] > 0
    ]
    old = revised_writers[0]["revision_contract"]["critic_acceptance_tests"]
    following = revised_writers[1]["revision_contract"]["critic_acceptance_tests"]
    assert len(old) == 1 and len(following) == 2 and following[0] == old[0]
    assert following[1]["category"] == "scene_assignment:turning_point"
    assert following[1]["source_critique_version_id"] != old[0]["source_critique_version_id"]
    final_critic = next(
        p
        for p in payloads
        if p.get("assignment", {}).get("operation") == "critique"
        and p["assignment"]["revision_number"] == 2
    )
    assert final_critic["repair_acceptance_tests"] == following
