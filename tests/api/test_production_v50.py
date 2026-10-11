"""Met semantics reach initial and structural-retry prompts; no model judgment is simulated."""

from __future__ import annotations

import json
from copy import deepcopy
from dataclasses import replace

import pytest
from open_hollywood_api.services.production_critic_obligations import OBLIGATION_RULE
from open_hollywood_api.services.production_model_executor import (
    _messages,
    _Operation,
    _output_schema,
)
from open_hollywood_engine.models import ModelDeployment

from tests.api.test_production_v29 import _materialize, _raw, _refs
from tests.api.test_production_v37 import _fixture, _payload
from tests.api.test_production_v41 import _revision
from tests.api.test_production_v46 import _retry_execution


@pytest.mark.parametrize("deployment", [ModelDeployment.LOCAL, ModelDeployment.CLOUD])
@pytest.mark.parametrize("revision", [False, True])
def test_complete_fact_rule_reaches_both_profiles_and_preserves_exact_assignments(
    deployment: ModelDeployment, revision: bool
) -> None:
    source = _revision() if revision else _fixture()
    execution = replace(source, selection=replace(source.selection, deployment=deployment))
    original = deepcopy(execution.inputs)
    schema = _output_schema(
        _Operation.CRITIQUE,
        continuity_schema_variant=None,
        critic_execution=execution,
        critic_evidence_refs=tuple(_refs(execution)),
    )
    messages = _messages(
        _Operation.CRITIQUE,
        execution,
        schema,
        continuity_schema_variant=None,
        continuity_model_context=None,
    )
    instruction = messages[0].content
    assert instruction.count(OBLIGATION_RULE) == 1
    assert "including every explicit condition" in instruction
    assert "similar dramatic purpose cannot substitute" in instruction
    assert "literal plan wording is not required" in instruction
    assert "without an explicit decision sentence" in instruction
    payload = json.loads(messages[-1].content)
    plan = next(a["content"] for a in execution.inputs if a["artifact_kind"] == "scene_plan")
    assert payload["scene_assignment_contract"]["turning_point"] == plan["turning_point"]
    assert payload["scene_assignment_contract"]["outcome"] == plan["outcome"]
    assert schema["properties"]["assignment_checks"]["required"] == ["turning_point", "outcome"]
    if deployment is ModelDeployment.CLOUD:
        assert payload["output_schema"] == schema
    else:
        assert payload["output_schema_delivery"] == "enforced_by_local_gateway"
    writer = _messages(
        _Operation.WRITE,
        execution,
        _output_schema(_Operation.WRITE, continuity_schema_variant=None),
        continuity_schema_variant=None,
        continuity_model_context=None,
    )
    assert OBLIGATION_RULE not in writer[0].content
    assert execution.inputs == original


@pytest.mark.parametrize("deployment", [ModelDeployment.LOCAL, ModelDeployment.CLOUD])
@pytest.mark.parametrize("failure", ["missing_assessment", "repair_with_met"])
def test_structural_retry_keeps_full_fact_semantics_without_inventing_a_blocker(
    deployment: ModelDeployment, failure: str
) -> None:
    source = _fixture()
    execution = replace(source, selection=replace(source.selection, deployment=deployment))
    valid = _raw(execution)
    broken = deepcopy(valid)
    check = broken["assignment_checks"]["turning_point"]
    if failure == "missing_assessment":
        del check["assessment"]
    else:
        check["recommended_resolution"] = "Rejected repair prose must not become a story fact."
    retry = _retry_execution(execution, broken)
    payload = _payload(_Operation.CRITIQUE, retry)
    guidance = payload["schema_repair"]
    assert guidance["policy_version"] == "17"
    assert OBLIGATION_RULE in guidance["operation_rules"]
    directive = next(
        d for d in guidance["directives"] if d["location"].startswith("assignment_checks")
    )
    assert directive["action"] == OBLIGATION_RULE
    assert directive["required_checks"] == ["turning_point", "outcome"]
    assert "Rejected repair prose" not in json.dumps(payload)
    assert payload["retry_context"]["manuscript_defect_established"] is False
    assert _materialize(valid, retry) == _materialize(valid, execution)
