"""First-review shape guidance changes instructions, not obligations or output contracts."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import replace

import pytest
from open_hollywood_api.services.production_critic_comparison import COMPARISON_OBJECT_RULE
from open_hollywood_api.services.production_critic_obligations import OBLIGATION_RULE
from open_hollywood_api.services.production_model_executor import (
    _INSTRUCTIONS,
    _messages,
    _Operation,
    _output_schema,
)
from open_hollywood_engine.models import ModelDeployment

from tests.api.test_production_v29 import _refs
from tests.api.test_production_v37 import _fixture
from tests.api.test_production_v41 import _revision


@pytest.mark.parametrize("deployment", [ModelDeployment.LOCAL, ModelDeployment.CLOUD])
@pytest.mark.parametrize("revision", [False, True])
def test_comparison_clarification_reaches_first_review_without_changing_its_contract(
    deployment: ModelDeployment, revision: bool, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = _revision() if revision else _fixture()
    execution = replace(source, selection=replace(source.selection, deployment=deployment))
    inputs = deepcopy(execution.inputs)
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
    addition = "For every generic issues entry: " + COMPARISON_OBJECT_RULE + " "
    assert messages[0].content.count(addition) == 1
    assert messages[0].content.count(OBLIGATION_RULE) == 1
    assert COMPARISON_OBJECT_RULE not in _INSTRUCTIONS[_Operation.WRITE]
    monkeypatch.setitem(
        _INSTRUCTIONS, _Operation.CRITIQUE, _INSTRUCTIONS[_Operation.CRITIQUE].replace(addition, "")
    )
    prior_messages = _messages(
        _Operation.CRITIQUE,
        execution,
        schema,
        continuity_schema_variant=None,
        continuity_model_context=None,
    )
    assert messages[0].content.replace(addition, "") == prior_messages[0].content
    assert messages[1:] == prior_messages[1:]
    assert execution.inputs == inputs
