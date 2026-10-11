"""Compliance/craft delivery and routing; fixtures do not establish model semantics."""

from __future__ import annotations

import json
from copy import deepcopy
from dataclasses import replace
from pathlib import Path

import pytest
from open_hollywood_api.persistence.database import create_session_factory
from open_hollywood_api.persistence.models import AgentInvocation
from open_hollywood_api.services.production_critic_obligations import COMPLIANCE_CRAFT_RULE
from open_hollywood_api.services.production_model_executor import (
    _INSTRUCTIONS,
    _messages,
    _Operation,
    _output_schema,
)
from open_hollywood_engine.evaluations import load_benchmark_corpus
from open_hollywood_engine.models import ModelDeployment, ModelRequest, ModelResponse
from sqlalchemy import Engine, select

from tests.api.test_production_v26 import V26Gateway, _run_gateway
from tests.api.test_production_v29 import _materialize
from tests.api.test_production_v37 import _fixture, _payload
from tests.api.test_production_v41 import _revision
from tests.api.test_production_v45 import _claim
from tests.api.test_production_v46 import _broken, _retry_execution
from tests.api.test_production_v49 import _unmet
from tests.evaluations.test_agentic_blueprint import CORPUS_PATH
from tests.evaluations.test_agentic_production import ProductionFixtureGateway


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.mark.parametrize("deployment", [ModelDeployment.LOCAL, ModelDeployment.CLOUD])
@pytest.mark.parametrize("revision", [False, True])
def test_compliance_craft_instruction_changes_only_critic_system_message(
    deployment: ModelDeployment, revision: bool, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = _revision() if revision else _fixture()
    execution = replace(source, selection=replace(source.selection, deployment=deployment))
    inputs = deepcopy(execution.inputs)
    schema = _output_schema(
        _Operation.CRITIQUE, continuity_schema_variant=None, critic_execution=execution
    )
    messages = _messages(
        _Operation.CRITIQUE,
        execution,
        schema,
        continuity_schema_variant=None,
        continuity_model_context=None,
    )
    assert messages[0].content.count(COMPLIANCE_CRAFT_RULE) == 1
    for operation, instruction in _INSTRUCTIONS.items():
        if operation is not _Operation.CRITIQUE:
            assert COMPLIANCE_CRAFT_RULE not in instruction
    monkeypatch.setitem(
        _INSTRUCTIONS,
        _Operation.CRITIQUE,
        _INSTRUCTIONS[_Operation.CRITIQUE].replace(COMPLIANCE_CRAFT_RULE + " ", ""),
    )
    prior = _messages(
        _Operation.CRITIQUE,
        execution,
        schema,
        continuity_schema_variant=None,
        continuity_model_context=None,
    )
    assert messages[0].content.replace(COMPLIANCE_CRAFT_RULE + " ", "") == prior[0].content
    assert messages[1:] == prior[1:] and execution.inputs == inputs
    assert schema == _output_schema(
        _Operation.CRITIQUE, continuity_schema_variant=None, critic_execution=execution
    )


@pytest.mark.parametrize("deployment", [ModelDeployment.LOCAL, ModelDeployment.CLOUD])
@pytest.mark.parametrize("repeated", [False, True])
def test_structural_retry_keeps_guidance_and_classification_without_rewriting_judgment(
    deployment: ModelDeployment, repeated: bool, monkeypatch: pytest.MonkeyPatch
) -> None:
    source, raw = _broken(repeated=repeated)
    execution = replace(source, selection=replace(source.selection, deployment=deployment))
    retry = _retry_execution(execution, raw)
    packet = _payload(_Operation.CRITIQUE, retry)
    assert packet["schema_repair"]["policy_version"] == "17"
    assert packet["schema_repair"]["preserved_classifications"][0]["assignment_finding_refs"] == [
        "assignment:outcome" if repeated else None
    ]
    messages = _messages(
        _Operation.CRITIQUE,
        retry,
        _output_schema(_Operation.CRITIQUE, continuity_schema_variant=None, critic_execution=retry),
        continuity_schema_variant=None,
        continuity_model_context=None,
    )
    assert messages[0].content.count(COMPLIANCE_CRAFT_RULE) == 1
    repaired = deepcopy(raw)
    repaired["issues"][0]["assignment_comparison"] = _claim(execution, repeated=repeated)[
        "assignment_comparison"
    ]
    expected = _materialize(repaired, retry)
    monkeypatch.setitem(
        _INSTRUCTIONS,
        _Operation.CRITIQUE,
        _INSTRUCTIONS[_Operation.CRITIQUE].replace(COMPLIANCE_CRAFT_RULE + " ", ""),
    )
    assert _payload(_Operation.CRITIQUE, retry) == packet
    assert _materialize(repaired, retry) == expected == _materialize(repaired, execution)


class ComplianceCraftGateway(V26Gateway):
    async def generate(self, request: ModelRequest) -> ModelResponse:
        response = await ProductionFixtureGateway.generate(self, request)
        payload = json.loads(request.messages[-1].content)
        assignment = payload.get("assignment", {})
        if (
            assignment.get("operation") != "critique"
            or assignment["unit_number"] != 1
            or assignment["revision_number"] != 0
        ):
            return response
        assert COMPLIANCE_CRAFT_RULE in request.messages[0].content
        raw = json.loads(response.content)
        if self.mode == "unmet_turn":
            _unmet(raw, "turning_point")
            raw["verdict"] = "pass"  # A real native blocker still overrides this.
        else:
            evidence = raw["assignment_checks"]["turning_point"]["draft_evidence_refs"]
            raw["issues"] = [
                {
                    "category": "prose",
                    "severity": "major" if self.mode == "craft_defect" else "minor",
                    "description": "Simulated repeated explanation obscures the action."
                    if self.mode == "craft_defect"
                    else "Simulated preference for a different staging of the fulfilled turn.",
                    "recommendation": "Condense the repetition without changing assigned facts."
                    if self.mode == "craft_defect"
                    else "Optional: consider a different staging; no assigned fact is missing.",
                    "draft_evidence_refs": evidence,
                    "assignment_finding_ref": None,
                    "assignment_comparison": {
                        "finding_refs": [],
                        "assessment": "No current assignment findings. This is a simulated "
                        "independent craft assessment, not evidence of model reasoning.",
                    },
                }
            ]
            raw["verdict"] = "pass" if self.mode == "optional_pass" else "revise"
        return replace(response, content=json.dumps(raw))


@pytest.mark.anyio
@pytest.mark.parametrize("mode", ["optional_pass", "craft_defect", "unmet_turn", "optional_revise"])
async def test_persisted_verdict_drives_revision_without_hiding_optional_revise_failures(
    mode: str, migrated_database_path: Path, database_engine: Engine
) -> None:
    prompt = load_benchmark_corpus(CORPUS_PATH).prompts[0]
    gateway = ComplianceCraftGateway(prompt.prompt, prompt, mode=mode)
    result = await _run_gateway(gateway, migrated_database_path, database_engine)
    assert len(result.result.accepted_units) == 3
    writes = [
        json.loads(r.messages[-1].content)
        for r in gateway.requests
        if json.loads(r.messages[-1].content).get("assignment", {}).get("operation") == "write"
    ]
    assert len(writes) == (3 if mode == "optional_pass" else 4)
    if mode != "optional_pass":
        revised = next(p for p in writes if p["assignment"]["revision_number"] == 1)
        repairs = revised["revision_contract"]["critic_acceptance_tests"]
        # Zero mandatory targets is not proof the graph avoids a writer revision.
        assert len(repairs) == (0 if mode == "optional_revise" else 1)
        if mode == "unmet_turn":
            assert repairs[0]["category"] == "scene_assignment:turning_point"
        elif mode == "craft_defect":
            assert repairs[0]["category"] == "prose"
    with create_session_factory(database_engine)() as session:
        reviews = [
            i
            for i in session.scalars(select(AgentInvocation)).all()
            if i.specialist_role == "scene_critic"
        ]
        assert reviews and all(i.schema_validation_succeeded for i in reviews)
        first = next(i for i in reviews if any(v.content.get("issues") for v in i.output_versions))
        critique = first.output_versions[0].content
        assert critique["verdict"] == ("pass" if mode == "optional_pass" else "revise")
        assert (
            critique["issues"][0]["severity"]
            == {
                "optional_pass": "minor",
                "optional_revise": "minor",
                "craft_defect": "major",
                "unmet_turn": "blocking",
            }[mode]
        )
