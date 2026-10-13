"""Source-basis guidance preserves evidence, wire contracts and structural retries."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import replace

import pytest
from open_hollywood_api.services.production_critic_obligations import (
    MINIMUM_REPAIR_RULE,
    OBLIGATION_RULE,
    REQUIREMENT_BASIS_RULE,
)
from open_hollywood_api.services.production_model_executor import (
    _INSTRUCTIONS,
    _messages,
    _Operation,
    _output_schema,
)
from open_hollywood_api.services.production_repair_conditions import condition_obligation_rule
from open_hollywood_engine.models import ModelDeployment

from tests.api.test_production_v29 import _materialize
from tests.api.test_production_v37 import _fixture, _payload
from tests.api.test_production_v41 import _revision
from tests.api.test_production_v45 import _claim
from tests.api.test_production_v46 import _broken, _retry_execution


@pytest.mark.parametrize("deployment", [ModelDeployment.LOCAL, ModelDeployment.CLOUD])
@pytest.mark.parametrize("revision", [False, True])
def test_basis_instruction_preserves_review_context_schema_and_other_roles(
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
    assert messages[0].content.count(REQUIREMENT_BASIS_RULE) == 1
    assert messages[0].content.count(condition_obligation_rule(OBLIGATION_RULE)) == 1
    assert messages[0].content.count(MINIMUM_REPAIR_RULE) == 1
    for operation, instruction in _INSTRUCTIONS.items():
        if operation is not _Operation.CRITIQUE:
            assert REQUIREMENT_BASIS_RULE not in instruction
    monkeypatch.setitem(
        _INSTRUCTIONS,
        _Operation.CRITIQUE,
        _INSTRUCTIONS[_Operation.CRITIQUE].replace(REQUIREMENT_BASIS_RULE + " ", ""),
    )
    prior = _messages(
        _Operation.CRITIQUE,
        execution,
        schema,
        continuity_schema_variant=None,
        continuity_model_context=None,
    )
    assert messages[0].content.replace(REQUIREMENT_BASIS_RULE + " ", "") == prior[0].content
    assert messages[1:] == prior[1:] and execution.inputs == inputs
    assert schema == _output_schema(
        _Operation.CRITIQUE, continuity_schema_variant=None, critic_execution=execution
    )


@pytest.mark.parametrize("deployment", [ModelDeployment.LOCAL, ModelDeployment.CLOUD])
@pytest.mark.parametrize("repeated", [False, True])
def test_basis_guidance_reaches_retry_without_reclassifying_or_rewriting_claims(
    deployment: ModelDeployment, repeated: bool, monkeypatch: pytest.MonkeyPatch
) -> None:
    source, raw = _broken(repeated=repeated)
    execution = replace(source, selection=replace(source.selection, deployment=deployment))
    retry = _retry_execution(execution, raw)
    packet = _payload(_Operation.CRITIQUE, retry)
    assert packet["schema_repair"]["policy_version"] == "20"
    assert packet["schema_repair"]["preserved_classifications"][0]["assignment_finding_refs"] == [
        "assignment:outcome" if repeated else None
    ]
    schema = _output_schema(
        _Operation.CRITIQUE, continuity_schema_variant=None, critic_execution=retry
    )
    messages = _messages(
        _Operation.CRITIQUE,
        retry,
        schema,
        continuity_schema_variant=None,
        continuity_model_context=None,
    )
    assert messages[0].content.count(REQUIREMENT_BASIS_RULE) == 1
    repaired = deepcopy(raw)
    repaired["issues"][0]["assignment_comparison"] = _claim(execution, repeated=repeated)[
        "assignment_comparison"
    ]
    expected = _materialize(repaired, retry)
    monkeypatch.setitem(
        _INSTRUCTIONS,
        _Operation.CRITIQUE,
        _INSTRUCTIONS[_Operation.CRITIQUE].replace(REQUIREMENT_BASIS_RULE + " ", ""),
    )
    assert _payload(_Operation.CRITIQUE, retry) == packet
    assert _materialize(repaired, retry) == expected == _materialize(repaired, execution)
