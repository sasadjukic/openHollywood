"""Eligible historical links and explicitly declared current assignment repetitions."""

from __future__ import annotations

import json
from copy import deepcopy
from dataclasses import replace
from pathlib import Path

import pytest
from open_hollywood_api.persistence.database import create_session_factory
from open_hollywood_api.persistence.models import AgentInvocation
from open_hollywood_api.services.production_failure_evidence import capture_review_failure
from open_hollywood_api.services.production_model_executor import (
    _critic_assignment_routes,
    _Operation,
    _output_schema,
    _revision_acceptance_audit,
    _scene_boundary_audit,
    _StructuredOutputContractError,
)
from open_hollywood_api.services.production_revision_acceptance import repair_checks_schema
from open_hollywood_engine.evaluations import load_benchmark_corpus
from open_hollywood_engine.models import ModelRequest, ModelResponse
from sqlalchemy import Engine, select

from tests.api.test_production_v26 import _run_gateway
from tests.api.test_production_v29 import _comparison, _materialize, _raw, _refs
from tests.api.test_production_v31 import _review
from tests.api.test_production_v37 import _fixture
from tests.api.test_production_v41 import _linked, _revision
from tests.api.test_production_v42 import IndependentRepairGateway
from tests.evaluations.test_agentic_blueprint import CORPUS_PATH


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.mark.parametrize(
    "category,severity,expected",
    [
        ("scene_assignment:outcome", "blocking", ["assignment:outcome", "boundary"]),
        ("scene_assignment:turning_point", "blocking", ["assignment:turning_point"]),
        ("scene_assignment:point_of_view_character_id", "blocking", ["viewpoint"]),
        ("scene_assignment:outcome", "major", []),
        ("scene_assignment:missing_anchor", "blocking", []),
        ("dramatic_tension", "major", None),
        ("plot", "blocking", None),
    ],
)
def test_repair_choices_follow_original_category_severity_and_populated_plan(
    category: str, severity: str, expected: list[str] | None
) -> None:
    execution = _fixture()
    schema = repair_checks_schema(
        [{"test_id": "original", "category": category, "severity": severity}],
        assignment_routes=_critic_assignment_routes(execution),
    )
    met, unmet = schema["$defs"]["RepairAcceptanceCheck"]["anyOf"]
    assert met["properties"]["current_finding_refs"]["maxItems"] == 0
    links = unmet["properties"]["current_finding_refs"]
    assert category in links["description"] and severity in links["description"]
    if expected is None:
        assert links["items"] == {"type": "string", "pattern": r"^issue:(0|[1-9][0-9]*)$"}
    elif expected:
        assert links["items"]["enum"] == expected
    else:
        assert links["maxItems"] == 0


def test_schema_reuses_compatible_groups_and_respects_boundary_fallback() -> None:
    execution = _fixture()
    execution.inputs[0]["content"]["outcome"] = None
    schema = repair_checks_schema(
        [
            {"test_id": key, "category": category, "severity": "blocking"}
            for key, category in (
                ("first", "scene_assignment:turning_point"),
                ("second", "scene_assignment:turning_point"),
                ("craft", "plot"),
            )
        ],
        assignment_routes=_critic_assignment_routes(execution),
    )
    assert schema["properties"]["first"] == schema["properties"]["second"]
    assert schema["properties"]["craft"] != schema["properties"]["first"]
    assert len(schema["$defs"]) == 2
    links = schema["$defs"]["RepairAcceptanceCheck"]["anyOf"][1]["properties"][
        "current_finding_refs"
    ]
    assert links["items"]["enum"] == ["assignment:turning_point", "boundary"]
    bound = _output_schema(
        _Operation.CRITIQUE, continuity_schema_variant=None, critic_execution=execution
    )
    choices = bound["$defs"]["CritiqueIssue"]["properties"]["assignment_finding_ref"]["enum"]
    assert None in choices and "assignment:outcome" not in choices
    assert "assignment_finding_ref" in bound["$defs"]["CritiqueIssue"]["required"]


@pytest.mark.parametrize("ref", ["assignment:outcome", "boundary", "viewpoint"])
def test_declared_repetition_preserves_both_claims_repairs_and_all_evidence(ref: str) -> None:
    execution = _revision()
    raw = _raw(execution, "pov" if ref == "viewpoint" else "assignment")
    if ref == "boundary":
        raw["assignment_violations"] = []
        raw["scene_boundary_check"]["status"] = "overrun"
    raw["repair_checks"] = _review(execution)["repair_checks"]
    repeat = _raw(execution, "blocking_craft")["issues"][0]
    repeat.update(assignment_finding_ref=ref, draft_evidence_refs=[_refs(execution)[1]])
    repeat["assignment_comparison"] = _comparison(ref)
    raw["issues"] = [repeat]
    before = deepcopy(raw)
    result = _materialize(raw, execution)
    assert result["verdict"] == "revise" and len(result["issues"]) == 1
    target = result["issues"][0]
    assert target["category"].startswith("scene_assignment:")
    assert repeat["description"] in target["description"]
    assert repeat["recommendation"] in target["recommendation"]
    assert "The date was today." in target["evidence"]
    assert "assignment_finding_ref" not in json.dumps(result)
    audit = _scene_boundary_audit(raw, execution)
    assert audit["schema_version"] == "3"
    repetitions = audit["assignment_restatements"]
    assert isinstance(repetitions, list)
    assert repetitions[0]["assignment_finding_ref"] == ref
    assert raw == before


def test_restatement_can_join_original_assignment_without_becoming_a_craft_link_alias() -> None:
    execution = _revision()
    raw = _linked(execution)
    repeat = _raw(execution, "blocking_craft")["issues"][0]
    repeat["assignment_finding_ref"] = "assignment:outcome"
    repeat["assignment_comparison"] = _comparison("assignment:outcome")
    raw["issues"] = [repeat]
    result = _materialize(raw, execution)
    assert len(result["issues"]) == 1
    audit = _revision_acceptance_audit(raw, execution)
    assert audit["linked_current_findings"][0]["finding_refs"] == ["boundary", "assignment:outcome"]
    assert repeat["description"] in audit["linked_current_findings"][0]["description"]
    next(iter(raw["repair_checks"].values()))["current_finding_refs"].append("issue:0")
    with pytest.raises(_StructuredOutputContractError):
        _materialize(raw, execution)


@pytest.mark.parametrize("mode", ["same_evidence", "same_category", "separate_turn"])
def test_unlinked_independent_issues_survive_repetition_consolidation(mode: str) -> None:
    execution = _fixture("The date was today. She read it twice.")
    raw = _raw(execution, "assignment")
    repeated = _raw(execution, "blocking_craft")["issues"][0]
    repeated["assignment_finding_ref"] = "assignment:outcome"
    repeated["assignment_comparison"] = _comparison("assignment:outcome")
    independent = {
        **repeated,
        "description": "A distinct pacing problem.",
        "assignment_finding_ref": None,
    }
    if mode == "same_category":
        independent["draft_evidence_refs"] = [_refs(execution)[-1]]
    raw["issues"] = [repeated, independent]
    if mode == "separate_turn":
        raw["assignment_violations"].append(
            {**raw["assignment_violations"][0], "anchor": "turning_point"}
        )
        independent["assignment_comparison"] = _comparison(
            "assignment:outcome", "assignment:turning_point"
        )
    result = _materialize(raw, execution)
    assert len(result["issues"]) == (3 if mode == "separate_turn" else 2)
    assert result["issues"][0]["description"] == independent["description"]


@pytest.mark.parametrize(
    "bad",
    ["missing_field", "unknown", "inactive", "severity", "evidence", "extra", "blank", "internal"],
)
def test_invalid_restatement_is_rejected_before_any_finding_can_disappear(bad: str) -> None:
    execution = _fixture()
    raw = _raw(execution, "assignment")
    repeated = _raw(execution, "blocking_craft")["issues"][0]
    repeated["assignment_finding_ref"] = "assignment:outcome"
    repeated["assignment_comparison"] = _comparison("assignment:outcome")
    raw["issues"] = [repeated]
    if bad == "missing_field":
        repeated.pop("assignment_finding_ref")
    elif bad == "unknown":
        repeated["assignment_finding_ref"] = "assignment:invented"
    elif bad == "inactive":
        repeated["assignment_finding_ref"] = "boundary"
    elif bad == "severity":
        repeated["severity"] = "invalid-severity"
    elif bad == "evidence":
        repeated["draft_evidence_refs"] = ["stale"]
    elif bad == "extra":
        repeated["unrecognized"] = "must not be discarded"
    elif bad == "blank":
        repeated["recommendation"] = " "
    else:
        repeated["_assignment_finding_ref"] = "boundary"
    before = deepcopy(raw)
    with pytest.raises(_StructuredOutputContractError):
        _materialize(raw, execution)
    assert raw == before


def test_restatement_audit_and_rejected_response_evidence_redact_secrets(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    secret = "v43-only-test-secret-value"
    monkeypatch.setenv("OLLAMA_API_KEY", secret)
    execution = _fixture()
    raw = _raw(execution, "assignment")
    raw["issues"] = [
        {
            **_raw(execution, "blocking_craft")["issues"][0],
            "description": secret,
            "assignment_finding_ref": "assignment:outcome",
            "assignment_comparison": _comparison("assignment:outcome"),
        }
    ]
    audit = _scene_boundary_audit(raw, execution)
    assert secret not in json.dumps(audit)
    capture = capture_review_failure(
        operation="critique",
        response_content=json.dumps(raw),
        request_content="{}",
        input_version_ids=(),
        validation_issues=(),
    )
    assert "assignment_finding_ref" in json.dumps(capture) and secret not in json.dumps(capture)


class RepeatedAssignmentGateway(IndependentRepairGateway):
    async def generate(self, request: ModelRequest) -> ModelResponse:
        response = await super().generate(request)
        payload = json.loads(request.messages[-1].content)
        assignment = payload.get("assignment", {})
        if assignment.get("operation") != "critique" or assignment["revision_number"] != 1:
            return response
        raw = json.loads(response.content)
        turn = next(v for v in raw["assignment_violations"] if v["anchor"] == "turning_point")
        raw["issues"] = [
            {
                "category": "plot",
                "severity": "blocking",
                "description": "Same missing turn.",
                "recommendation": "Retain this additional repair advice.",
                "draft_evidence_refs": turn["draft_evidence_refs"],
                "assignment_finding_ref": "assignment:turning_point",
                "assignment_comparison": _comparison("assignment:turning_point"),
            }
        ]
        return replace(response, content=json.dumps(raw))


@pytest.mark.anyio
@pytest.mark.parametrize("original_unmet", [False, True])
async def test_one_new_turn_target_reaches_writer_and_critic_with_original_target_unchanged(
    original_unmet: bool, migrated_database_path: Path, database_engine: Engine
) -> None:
    prompt = load_benchmark_corpus(CORPUS_PATH).prompts[0]
    gateway = RepeatedAssignmentGateway(prompt.prompt, prompt, original_unmet=original_unmet)
    result = await _run_gateway(gateway, migrated_database_path, database_engine)
    assert len(result.result.accepted_units) == 3
    packets = [json.loads(r.messages[-1].content) for r in gateway.requests]
    writers = [
        p
        for p in packets
        if p.get("assignment", {}).get("operation") == "write"
        and p["assignment"]["revision_number"] > 0
    ]
    old = writers[0]["revision_contract"]["critic_acceptance_tests"]
    following = writers[1]["revision_contract"]["critic_acceptance_tests"]
    assert len(following) == 2 and following[0] == old[0]
    assert following[1]["category"] == "scene_assignment:turning_point"
    assert "additional repair advice" in following[1]["requested_change"]
    critic = next(
        p
        for p in packets
        if p.get("assignment", {}).get("operation") == "critique"
        and p["assignment"]["revision_number"] == 2
    )
    assert critic["repair_acceptance_tests"] == following
    with create_session_factory(database_engine)() as session:
        audited = [
            i
            for i in session.scalars(select(AgentInvocation))
            if i.request_settings.get("scene_boundary_audit", {}).get("assignment_restatements")
        ]
        assert len(audited) == 1
        assert all(i["category"] != "plot" for i in audited[0].output_versions[0].content["issues"])
