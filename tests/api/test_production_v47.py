"""Consolidated complaints cannot own separate original craft repair links."""

from __future__ import annotations

import json
from copy import deepcopy
from dataclasses import replace
from pathlib import Path
from typing import Any
from uuid import uuid4

import pytest
from open_hollywood_api.persistence.database import create_session_factory
from open_hollywood_api.persistence.models import AgentInvocation
from open_hollywood_api.services.production_failure_evidence import capture_review_failure
from open_hollywood_api.services.production_model_executor import (
    _Operation,
    _output_schema,
    _revision_acceptance_audit,
    _StructuredOutputContractError,
)
from open_hollywood_api.services.production_revision_acceptance import critic_repair_tests
from open_hollywood_engine.evaluations import load_benchmark_corpus
from open_hollywood_engine.models import ModelDeployment, ModelRequest, ModelResponse
from sqlalchemy import Engine, select

from tests.api.test_production_v26 import _run_gateway
from tests.api.test_production_v29 import _comparison, _materialize, _raw, _refs
from tests.api.test_production_v31 import _review
from tests.api.test_production_v37 import _payload
from tests.api.test_production_v41 import LinkedRepairGateway, _revision
from tests.api.test_production_v46 import _retry_execution
from tests.evaluations.test_agentic_blueprint import CORPUS_PATH


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


def _craft() -> Any:
    execution = _revision("blocking_craft")
    raw = _raw(execution, "blocking_craft")
    raw["repair_checks"] = _review(execution, "unmet")["repair_checks"]
    target = next(iter(raw["repair_checks"]))
    raw["issues"][0]["repair_test_id"] = target
    return execution, raw, target


@pytest.mark.parametrize("deployment", [ModelDeployment.LOCAL, ModelDeployment.CLOUD])
def test_schema_only_offers_craft_repair_id_with_null_classification_and_exact_labels(
    deployment: ModelDeployment,
) -> None:
    execution, _, target = _craft()
    execution = replace(execution, selection=replace(execution.selection, deployment=deployment))
    schema = _output_schema(
        _Operation.CRITIQUE, continuity_schema_variant=None, critic_execution=execution
    )
    issue = schema["$defs"]["CritiqueIssue"]
    assert "repair_test_id" not in issue["required"]
    empty, linked = issue["anyOf"]
    assert empty == {"properties": {"repair_test_id": {"type": "null"}}}
    assert linked["required"] == ["repair_test_id"]
    assert linked["properties"] == {
        "category": {"const": "pacing"},
        "severity": {"const": "blocking"},
        "assignment_finding_ref": {"type": "null"},
        "repair_test_id": {"type": "string", "enum": [target]},
    }
    for status in schema["$defs"]["RepairAcceptanceCheck"]["anyOf"]:
        assert status["properties"]["current_finding_refs"]["maxItems"] == 0
    packet = _payload(_Operation.CRITIQUE, execution)
    assert ("output_schema" in packet) == (deployment is ModelDeployment.CLOUD)


@pytest.mark.parametrize(
    "classification", ["assignment:outcome", "boundary", "viewpoint", "assignment:turning_point"]
)
def test_assignment_repetition_cannot_link_original_craft_even_with_matching_labels(
    classification: str,
) -> None:
    execution, raw, _ = _craft()
    raw["issues"][0]["assignment_finding_ref"] = classification
    raw["issues"][0]["assignment_comparison"] = _comparison(classification)
    before = deepcopy(raw)
    retry = _retry_execution(execution, raw)
    directives = _payload(_Operation.CRITIQUE, retry)["schema_repair"]["directives"]
    directive = next(d for d in directives if d["location"] == "issues.0.repair_test_id")
    assert directive["eligible_repair_test_ids"] == []
    assert raw == before


@pytest.mark.parametrize(
    "bad",
    [
        "wrong_id",
        "wrong_category",
        "wrong_severity",
        "met",
        "assignment_test",
        "list_id",
        "blank_claim",
        "stale_evidence",
        "extra_field",
    ],
)
def test_invalid_direct_link_never_hides_a_malformed_or_incompatible_finding(bad: str) -> None:
    execution, raw, target = _craft()
    if bad == "wrong_id":
        raw["issues"][0]["repair_test_id"] = "repair_unknown"
    elif bad == "wrong_category":
        raw["issues"][0]["category"] = "Pacing"
    elif bad == "wrong_severity":
        raw["issues"][0]["severity"] = "major"
    elif bad == "met":
        raw["repair_checks"][target]["status"] = "met"
    elif bad == "assignment_test":
        original = next(a for a in execution.inputs if a["artifact_kind"] == "critique")
        original["content"]["issues"][0]["category"] = "scene_assignment:outcome"
        raw["issues"][0]["category"] = "scene_assignment:outcome"
    elif bad == "list_id":
        raw["issues"][0]["repair_test_id"] = [target, target]
    elif bad == "blank_claim":
        raw["issues"][0]["description"] = " "
    elif bad == "stale_evidence":
        raw["issues"][0]["draft_evidence_refs"] = ["old"]
    else:
        raw["issues"][0]["_current_finding_refs"] = ["issue:0"]
    before = deepcopy(raw)
    with pytest.raises(_StructuredOutputContractError):
        _materialize(raw, execution)
    assert raw == before


@pytest.mark.parametrize("status", ["met", "unmet"])
def test_legacy_index_link_is_rejected_instead_of_silently_cleared(status: str) -> None:
    execution, raw, target = _craft()
    raw["issues"][0].pop("repair_test_id")
    raw["repair_checks"][target].update(status=status, current_finding_refs=["issue:0"])
    before = deepcopy(raw)
    retry = _retry_execution(execution, raw)
    packet = _payload(_Operation.CRITIQUE, retry)
    directive = next(d for d in packet["schema_repair"]["directives"] if "expected_category" in d)
    assert directive["eligible_refs_if_independent_craft_is_retained"] == []
    assert "repair_test_id" in directive["action"]
    assert raw == before


@pytest.mark.parametrize("reverse", [False, True])
def test_independent_ownership_is_order_independent_and_preserves_evidence_and_original_id(
    reverse: bool,
) -> None:
    execution, raw, target = _craft()
    raw["issues"][0]["draft_evidence_refs"] = [_refs(execution)[-1]]
    raw["issues"][0]["description"] = "Same original weakness with different current words."
    distinct = deepcopy(raw["issues"][0])
    distinct.update(repair_test_id=None, description="A distinct defect in the same category.")
    raw["issues"].append(distinct)
    if reverse:
        raw["issues"].reverse()
    before = deepcopy(raw)
    result = _materialize(raw, execution)
    tests = critic_repair_tests(execution.inputs, execution.unit_id)
    assert len(result["issues"]) == 2
    assert result["issues"][0]["description"] == distinct["description"]
    assert result["issues"][1]["description"] == tests[0]["claim"]
    assert "She still trusted it." in result["issues"][1]["evidence"]
    assert "repair_test_id" not in json.dumps(result)
    review = {
        "artifact_kind": "critique",
        "artifact_key": "next",
        "artifact_version_id": str(uuid4()),
        "content": result,
    }
    next_tests = critic_repair_tests((*execution.inputs, review), execution.unit_id)
    assert tests[0] in next_tests and len(next_tests) == 2
    audit = _revision_acceptance_audit(raw, execution)
    assert audit["schema_version"] == "3"
    assert audit["wire_checks"][target]["current_finding_refs"] == []
    assert audit["checks"][target]["current_finding_refs"] == [f"issue:{int(reverse)}"]
    assert audit["declared_craft_repair_links"] == [
        {"raw_issue_index": int(reverse), "repair_test_id": target}
    ]
    assert raw == before


def test_multiple_independent_reports_can_link_one_original_without_new_repair_ids() -> None:
    execution, raw, _ = _craft()
    raw["issues"].append(deepcopy(raw["issues"][0]))
    raw["issues"][1]["draft_evidence_refs"] = [_refs(execution)[-1]]
    assert len(_materialize(raw, execution)["issues"]) == 1


def test_repair_reference_survives_bounded_failure_capture_with_secrets_redacted(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _, raw, target = _craft()
    monkeypatch.setenv("OLLAMA_API_KEY", "test-only-secret")
    raw["issues"][0]["description"] = "test-only-secret"
    evidence = capture_review_failure(
        operation="critique",
        response_content=json.dumps(raw),
        request_content="{}",
        input_version_ids=(),
        validation_issues=(),
    )
    encoded = json.dumps(evidence)
    assert target in encoded and "test-only-secret" not in encoded


class IndependentLinkGateway(LinkedRepairGateway):
    async def generate(self, request: ModelRequest) -> ModelResponse:
        response = await super().generate(request)
        payload = json.loads(request.messages[-1].content)
        assignment = payload.get("assignment", {})
        if (
            assignment.get("operation") != "critique"
            or assignment["unit_number"] != 1
            or assignment["revision_number"] > 1
        ):
            return response
        raw = json.loads(response.content)
        craft = {
            "category": "prose",
            "severity": "major",
            "assignment_finding_ref": None,
            "assignment_comparison": _comparison("assignment:outcome"),
            "draft_evidence_refs": raw["scene_boundary_check"]["draft_evidence_refs"],
            "description": "Repeated explanations slow the prose.",
            "recommendation": "Condense repeated explanations.",
        }
        raw["issues"] = [craft]
        if assignment["revision_number"] == 1:
            target = next(
                t["test_id"] for t in payload["repair_acceptance_tests"] if t["category"] == "prose"
            )
            raw["repair_checks"][target]["current_finding_refs"] = []
            craft["repair_test_id"] = target
            repeated = deepcopy(craft)
            repeated.update(
                assignment_finding_ref="assignment:outcome",
                repair_test_id=None,
                description="The outcome is missed, also reducing tension.",
            )
            raw["issues"].append(repeated)
        return replace(response, content=json.dumps(raw))


@pytest.mark.anyio
async def test_persisted_writer_and_next_critic_keep_both_original_targets_without_duplicates(
    migrated_database_path: Path, database_engine: Engine
) -> None:
    prompt = load_benchmark_corpus(CORPUS_PATH).prompts[0]
    gateway = IndependentLinkGateway(prompt.prompt, prompt, invalid_once=False)
    result = await _run_gateway(gateway, migrated_database_path, database_engine)
    assert len(result.result.accepted_units) == 3
    packets = [json.loads(r.messages[-1].content) for r in gateway.requests]
    writers = [p for p in packets if p.get("assignment", {}).get("operation") == "write"]
    assert len(writers) == 5
    revised = [
        p["revision_contract"]["critic_acceptance_tests"]
        for p in writers
        if p["assignment"]["revision_number"] > 0
    ]
    assert len(revised[0]) == 2 and revised[0] == revised[1]
    critic = next(
        p
        for p in packets
        if p.get("assignment", {}).get("operation") == "critique"
        and p["assignment"]["revision_number"] == 2
    )
    assert critic["repair_acceptance_tests"] == revised[0]
    with create_session_factory(database_engine)() as session:
        calls = list(session.scalars(select(AgentInvocation)))
        assert not any(call.error_code for call in calls)
        audits = [
            call.request_settings["revision_acceptance_audit"]
            for call in calls
            if call.request_settings.get("revision_acceptance_audit", {}).get("schema_version")
            == "3"
        ]
        assert len(audits) == 1 and len(audits[0]["declared_craft_repair_links"]) == 1
