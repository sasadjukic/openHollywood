"""Comparison retries restate exact structure without changing claim judgments."""

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
    _Operation,
    _output_schema,
    _StructuredOutputContractError,
)
from open_hollywood_engine.evaluations import load_benchmark_corpus
from open_hollywood_engine.models import ModelDeployment, ModelRequest, ModelResponse
from sqlalchemy import Engine, select

from tests.api.test_production_v26 import _run_gateway
from tests.api.test_production_v29 import _materialize, _raw
from tests.api.test_production_v37 import _fixture, _payload
from tests.api.test_production_v45 import _claim
from tests.api.test_production_v46 import _broken, _retry_execution
from tests.api.test_production_v47 import IndependentLinkGateway
from tests.evaluations.test_agentic_blueprint import CORPUS_PATH


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


def _comparison_directive(packet: dict[str, Any]) -> dict[str, Any]:
    return next(d for d in packet["schema_repair"]["directives"] if "required_shape" in d)


@pytest.mark.parametrize("deployment", [ModelDeployment.LOCAL, ModelDeployment.CLOUD])
@pytest.mark.parametrize("repeated", [False, True])
def test_retry_explains_both_fields_without_replaying_prose_or_changing_output_contract(
    deployment: ModelDeployment, repeated: bool
) -> None:
    execution, raw = _broken(repeated=repeated)
    execution = replace(execution, selection=replace(execution.selection, deployment=deployment))
    retry = _retry_execution(execution, raw)
    packet = _payload(_Operation.CRITIQUE, retry)
    directive = _comparison_directive(packet)
    shape = directive["required_shape"]
    assert shape["type"] == "object" and shape["additionalProperties"] is False
    assert set(shape["required"]) == {"finding_refs", "assessment"}
    assert set(shape["properties"]) == {"finding_refs", "assessment"}
    refs = shape["properties"]["finding_refs"]
    assert refs["type"] == "array" and refs["uniqueItems"] is True and refs["maxItems"] == 8
    assert refs["items"] == {"type": "string", "enum": ["assignment:outcome"]}
    assert shape["properties"]["assessment"] == {
        "type": "string",
        "minLength": 1,
        "maxLength": 1000,
    }
    assert "exactly two required fields" in directive["action"]
    assert "nonblank" in directive["action"] and "same defect and repair" in directive["action"]
    assert packet["schema_repair"]["policy_version"] == "15"
    assert packet["schema_repair"]["preserved_classifications"][0]["assignment_finding_refs"] == [
        "assignment:outcome" if repeated else None
    ]
    assert "Malformed comparison" not in json.dumps(packet)
    assert raw["issues"][0]["description"] not in json.dumps(packet)
    assert _output_schema(
        _Operation.CRITIQUE, continuity_schema_variant=None, critic_execution=execution
    ) == _output_schema(_Operation.CRITIQUE, continuity_schema_variant=None, critic_execution=retry)
    assert "schema_repair" not in _payload(_Operation.CRITIQUE, execution)
    assert ("output_schema" in packet) == (deployment is ModelDeployment.CLOUD)
    before = deepcopy(raw)
    with pytest.raises(_StructuredOutputContractError):
        _materialize(raw, retry)
    assert raw == before  # The application does not wrap the string automatically.
    raw["issues"][0]["assignment_comparison"] = _claim(execution, repeated=repeated)[
        "assignment_comparison"
    ]
    assert _materialize(raw, retry) == _materialize(raw, execution)


def test_no_reported_assignment_findings_still_requires_assessment_and_empty_array() -> None:
    execution = _fixture()
    raw = _raw(execution, "craft")
    valid = deepcopy(raw)
    raw["issues"][0]["assignment_comparison"] = None
    retry = _retry_execution(execution, raw)
    directive = _comparison_directive(_payload(_Operation.CRITIQUE, retry))
    assert directive["reported_assignment_finding_groups"] == []
    refs = directive["required_shape"]["properties"]["finding_refs"]
    assert refs["maxItems"] == 0 and "enum" not in refs["items"]
    assert "assessment" in directive["required_shape"]["required"]
    assert _materialize(valid, retry) == _materialize(valid, execution)


def test_shape_limits_references_to_reported_groups_without_choosing_the_comparison() -> None:
    execution, raw = _broken(repeated=False)
    raw["scene_boundary_check"]["status"] = "overrun"
    other = deepcopy(raw["assignment_violations"][0])
    other["anchor"] = "turning_point"
    raw["assignment_violations"].append(other)
    retry = _retry_execution(execution, raw)
    directive = _comparison_directive(_payload(_Operation.CRITIQUE, retry))
    groups = directive["reported_assignment_finding_groups"]
    assert len(groups) == 2 and ["assignment:turning_point"] in groups
    choices = directive["required_shape"]["properties"]["finding_refs"]["items"]["enum"]
    assert set(choices) == {"boundary", "assignment:outcome", "assignment:turning_point"}
    assert len(choices) == 3
    assert "default" not in directive["required_shape"]["properties"]["assessment"]
    raw["issues"][0]["assignment_comparison"] = {
        "finding_refs": ["assignment:outcome", "assignment:turning_point"],
        "assessment": "Excess explanation remains even after both assignment defects are fixed.",
    }
    assert len(_materialize(raw, retry)["issues"]) == 3


class ComparisonShapeGateway(IndependentLinkGateway):
    def __init__(self, *args: Any, broken_index: int) -> None:
        super().__init__(*args, invalid_once=False)
        self.broken_index = broken_index

    async def generate(self, request: ModelRequest) -> ModelResponse:
        response = await super().generate(request)
        packet = json.loads(request.messages[-1].content)
        assignment = packet.get("assignment", {})
        if (
            assignment.get("operation") != "critique"
            or assignment["unit_number"] != 1
            or assignment["revision_number"] != 1
        ):
            return response
        raw = json.loads(response.content)
        if self.revision_one_reviews == 1:
            raw["issues"][self.broken_index]["assignment_comparison"] = "Rejected comparison text."
        else:
            directive = _comparison_directive(packet)
            assert directive["location"] == f"issues.{self.broken_index}.assignment_comparison"
            assert set(directive["required_shape"]["required"]) == {"finding_refs", "assessment"}
            assert packet["schema_repair"]["preserved_classifications"]
            assert "Rejected comparison text" not in json.dumps(packet)
        return replace(response, content=json.dumps(raw))


@pytest.mark.anyio
@pytest.mark.parametrize("broken_index", [0, 1])
async def test_persisted_retry_preserves_independent_link_and_consolidated_repetition(
    broken_index: int, migrated_database_path: Path, database_engine: Engine
) -> None:
    prompt = load_benchmark_corpus(CORPUS_PATH).prompts[0]
    gateway = ComparisonShapeGateway(prompt.prompt, prompt, broken_index=broken_index)
    result = await _run_gateway(gateway, migrated_database_path, database_engine)
    assert len(result.result.accepted_units) == 3 and gateway.revision_one_reviews == 2
    packets = [json.loads(r.messages[-1].content) for r in gateway.requests]
    writers = [p for p in packets if p.get("assignment", {}).get("operation") == "write"]
    assert len(writers) == 5
    tests = [
        p["revision_contract"]["critic_acceptance_tests"]
        for p in writers
        if p["assignment"]["revision_number"] > 0
    ]
    assert len(tests[0]) == 2 and tests[0] == tests[1]
    retries = [p for p in packets if "schema_repair" in p]
    assert len(retries) == 1 and retries[0]["repair_acceptance_tests"] == tests[0]
    first = next(
        p
        for p in packets
        if p.get("assignment", {}).get("operation") == "critique"
        and p["assignment"]["revision_number"] == 1
    )
    assert first["input_artifacts"] == retries[0]["input_artifacts"]
    with create_session_factory(database_engine)() as session:
        calls = list(session.scalars(select(AgentInvocation)))
        failed = [call for call in calls if call.error_code]
        assert len(failed) == 1 and not failed[0].output_versions
        assert (
            failed[0].request_settings["structured_failure"]["issues"][0]["type"]
            == "invalid_assignment_comparison"
        )
        linked = [
            call
            for call in calls
            if call.request_settings.get("revision_acceptance_audit", {}).get("schema_version")
            == "3"
        ]
        assert len(linked) == 1
        audit = linked[0].request_settings["revision_acceptance_audit"]
        assert audit["tests"] == tests[0] and len(audit["declared_craft_repair_links"]) == 1
        assert len(linked[0].output_versions[0].content["issues"]) == 2
