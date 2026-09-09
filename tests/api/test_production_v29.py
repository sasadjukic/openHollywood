"""v29 critic wire boundaries; simulated judgments are not live semantic evidence."""

from __future__ import annotations

import json
from copy import deepcopy
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from uuid import UUID, uuid4

import pytest
from open_hollywood_api.services.production_model_executor import (
    _CRITIC_RUBRIC_DIMENSIONS,
    _critic_evidence_catalog,
    _Execution,
    _materialize_output_data,
    _messages,
    _Operation,
    _output_schema,
    _StructuredOutputContractError,
)
from open_hollywood_engine.artifacts import ContinuityCategory, ContinuityReport, Critique
from open_hollywood_engine.models import ModelDeployment
from open_hollywood_engine.workflows import (
    CritiqueRevisionLimitError,
    initial_production_state,
)
from open_hollywood_engine.workflows.production_graph import _review_disposition

from tests.api.test_production_v28 import _execution
from tests.workflows.test_scene_production import _passing_production_input


def _refs(execution: _Execution) -> list[str]:
    return [entry["evidence_ref"] for entry in _critic_evidence_catalog(execution)]


def _raw(execution: _Execution, route: str = "none") -> dict[str, Any]:
    ref = _refs(execution)[-1] if route == "pov" else _refs(execution)[0]
    raw: dict[str, Any] = {
        "summary": "Offline boundary fixture, not a model judgment.",
        "strengths": ["Distinct voices."],
        "scores": [
            {"dimension": dimension, "score": 5, "rationale": "Offline craft score."}
            for dimension in _CRITIC_RUBRIC_DIMENSIONS
        ],
        "issues": [],
        "assignment_violations": [],
        "point_of_view_check": {"status": "aligned"},
        "verdict": "pass",
    }
    if route == "assignment":
        raw["assignment_violations"] = [
            {
                "anchor": "outcome",
                "draft_evidence_refs": [ref],
                "explanation": "The gate-opening outcome is replaced by leaving it closed.",
                "recommended_resolution": "Realize the planned outcome without unrelated changes.",
            }
        ]
    elif route in {"craft", "blocking_craft"}:
        raw["issues"] = [
            {
                "category": "pacing",
                "severity": "blocking" if route == "blocking_craft" else "minor",
                "description": "The already achieved turn could be dramatized more strongly.",
                "draft_evidence_refs": [ref],
                "recommendation": "Optional polish, without inventing a new event.",
            }
        ]
    elif route == "pov":
        raw["point_of_view_check"] = {
            "status": "violation",
            "subject_character_id": "cora",
            "violation_kind": "unauthorized_private_state",
            "draft_evidence_refs": [ref],
            "assessment": "Direct access to the other character's private knowledge.",
            "recommended_resolution": "Use the assigned character's perspective.",
        }
    return raw


def _materialize(raw: dict[str, Any], execution: _Execution) -> dict[str, Any]:
    draft = next(item for item in execution.inputs if item["artifact_kind"] == "scene_draft")
    task = SimpleNamespace(
        draft=SimpleNamespace(
            artifact_key=draft["artifact_key"], version_id=UUID(draft["artifact_version_id"])
        )
    )
    normalized = _materialize_output_data(_Operation.CRITIQUE, task, execution, raw)
    Critique.model_validate(normalized)
    return normalized


def _fixture() -> _Execution:
    return _execution(
        "The gate stayed closed. Cora secretly knew the spare key was gone.",
        scene_plan={"point_of_view_character_id": "elara", "outcome": "The gate opens."},
    )


@pytest.mark.parametrize("deployment", [ModelDeployment.LOCAL, ModelDeployment.CLOUD])
def test_all_three_wire_routes_share_one_version_scoped_reference_enum(
    deployment: ModelDeployment,
) -> None:
    execution = replace(_fixture(), selection=replace(_fixture().selection, deployment=deployment))
    original = deepcopy(execution.inputs)
    schema = _output_schema(
        _Operation.CRITIQUE,
        continuity_schema_variant=None,
        critic_evidence_refs=tuple(_refs(execution)),
    )
    assert schema["$defs"]["CriticDraftEvidenceReference"]["enum"] == _refs(execution)
    expected = {"$ref": "#/$defs/CriticDraftEvidenceReference"}
    properties = schema["properties"]
    assert (
        properties["assignment_violations"]["items"]["properties"]["draft_evidence_refs"]["items"]
        == expected
    )
    assert (
        schema["$defs"]["CritiqueIssue"]["properties"]["draft_evidence_refs"]["items"] == expected
    )
    assert (
        properties["point_of_view_check"]["anyOf"][1]["properties"]["draft_evidence_refs"]["items"]
        == expected
    )
    assert "evidence" not in schema["$defs"]["CritiqueIssue"]["properties"]
    assert "draft_evidence" not in properties["assignment_violations"]["items"]["properties"]
    assert not {"rubric_name", "rubric_version", "overall_score"} & properties.keys()
    messages = _messages(
        _Operation.CRITIQUE,
        execution,
        schema,
        continuity_schema_variant=None,
        continuity_model_context=None,
    )
    payload = json.loads(messages[-1].content)
    assert payload["critic_rubric"]["dimensions"] == _CRITIC_RUBRIC_DIMENSIONS
    draft = next(a for a in payload["input_artifacts"] if a["artifact_kind"] == "scene_draft")
    assert draft["content"]["evidence_catalog"] == list(_critic_evidence_catalog(execution))
    assert "prose" not in draft["content"]
    assert "an extra action unless the approved plan actually requires it" in messages[0].content
    assert "merely wanting a more explicit" in messages[0].content
    assert "A high mean cannot clear a blocking finding" in payload["critic_rubric"]["policy"]
    if deployment is ModelDeployment.CLOUD:
        assert payload["output_schema"] == schema
    assert execution.inputs == original


@pytest.mark.parametrize(
    "route,verdict",
    [
        ("assignment", "revise"),
        ("pov", "revise"),
        ("craft", "pass"),
        ("blocking_craft", "revise"),
        ("none", "pass"),
    ],
)
def test_exact_evidence_and_hard_verdict_survive_high_craft_scores(
    route: str, verdict: str
) -> None:
    execution = _fixture()
    raw = _raw(execution, route)
    original = deepcopy(raw)
    result = _materialize(raw, execution)
    assert raw == original
    assert result["verdict"] == verdict
    assert result["overall_score"] == 5.0
    assert result["rubric_name"] == "scene_craft" and result["rubric_version"] == "1"
    for issue in result["issues"]:
        assert issue["evidence"] == [
            "Cora secretly knew the spare key was gone."
            if route == "pov"
            else "The gate stayed closed."
        ]
        assert "draft_evidence_refs" not in issue
    assert "assignment_violations" not in result and "point_of_view_check" not in result


@pytest.mark.parametrize("route", ["assignment", "pov", "craft"])
@pytest.mark.parametrize(
    "bad_kind",
    [
        "unknown",
        "quotation",
        "unscoped",
        "duplicate",
        "empty",
        "too_many",
        "other_version",
    ],
)
def test_no_invalid_reference_can_create_an_accepted_finding(route: str, bad_kind: str) -> None:
    execution = _fixture()
    ref = _refs(execution)[0]
    invalid = {
        "unknown": ["draft_evidence_9999"],
        "quotation": ["The gate stayed closed."],
        "unscoped": ["draft_evidence_0001"],
        "duplicate": [ref, ref],
        "empty": [],
        "too_many": [ref] * 4,
        "other_version": _refs(_fixture())[:1],  # Same sentence/ordinal, different immutable ID.
    }[bad_kind]
    raw = _raw(execution, route)
    finding = (
        raw["point_of_view_check"]
        if route == "pov"
        else raw["assignment_violations"][0]
        if route == "assignment"
        else raw["issues"][0]
    )
    finding["draft_evidence_refs"] = invalid
    with pytest.raises(_StructuredOutputContractError) as failure:
        _materialize(raw, execution)
    assert failure.value.issue_type.endswith("evidence_reference_invalid")


@pytest.mark.parametrize(
    "route,old_field", [("assignment", "draft_evidence"), ("craft", "evidence")]
)
def test_legacy_wire_fields_are_not_silently_reinterpreted(route: str, old_field: str) -> None:
    execution = _fixture()
    raw = _raw(execution, route)
    finding = raw["assignment_violations"][0] if route == "assignment" else raw["issues"][0]
    finding.pop("draft_evidence_refs")
    finding[old_field] = "draft_evidence_0001" if route == "assignment" else ["draft_evidence_0001"]
    with pytest.raises(_StructuredOutputContractError):
        _materialize(raw, execution)


@pytest.mark.parametrize("change", ["missing", "duplicate", "invented"])
def test_fixed_rubric_does_not_accept_self_selected_dimensions(change: str) -> None:
    execution = _fixture()
    raw = _raw(execution)
    if change == "missing":
        raw["scores"].pop()
    elif change == "duplicate":
        raw["scores"][1]["dimension"] = raw["scores"][0]["dimension"]
    else:
        raw["scores"][1]["dimension"] = "automatic_contract_clearance"
    with pytest.raises(_StructuredOutputContractError) as failure:
        _materialize(raw, execution)
    assert failure.value.issue_type == "invalid_rubric_dimensions"


def test_legacy_persisted_critique_remains_readable_without_wire_migration() -> None:
    execution = _fixture()
    legacy = _materialize(_raw(execution), execution)
    legacy["rubric_name"] = "historical-review"
    legacy["scores"] = [
        {"dimension": "historical_dimension", "score": 4, "rationale": "Historical."}
    ]
    legacy["overall_score"] = 4.0
    assert Critique.model_validate(legacy).rubric_name == "historical-review"


def test_missing_and_achieved_outcomes_remain_distinct_simulated_judgments() -> None:
    # The runtime validates these declared judgments; it cannot infer literary truth.
    missing = _fixture()
    assert _materialize(_raw(missing, "assignment"), missing)["verdict"] == "revise"
    achieved = _execution(
        "Elara turned the key and pushed the gate open.",
        scene_plan={"point_of_view_character_id": "elara", "outcome": "The gate opens."},
    )
    assert _materialize(_raw(achieved, "craft"), achieved)["verdict"] == "pass"


def test_high_score_cannot_bypass_revision_cap_with_a_hard_critic_issue() -> None:
    production = _passing_production_input()
    state = initial_production_state(production)
    state.update({"critique_requires_revision": True, "critique_blocking_issue_count": 1})
    report = ContinuityReport(
        story_bible_version_id=production.initial_story_bible.version_id,
        scene_version_id=uuid4(),
        scene_plan_version_id=production.units[0].plan.version_id,
        scene_id=production.units[0].unit_id,
        scene_number=1,
        checked_categories=tuple(ContinuityCategory),
    )
    with pytest.raises(CritiqueRevisionLimitError):
        _review_disposition(
            state, production, production.units[0], production.maximum_revision_cycles, report
        )


def test_new_registry_preserves_old_review_and_does_not_promote_the_model() -> None:
    root = Path(__file__).parents[2]
    registry = json.loads((root / "benchmarks/v0.1/critic-transfer-v29.json").read_text("utf-8"))
    assert registry["candidate_prompt_version"] == "29"
    assert registry["candidate_graph_version"] == "7"
    assert registry["status"] == "prepared_not_run"
    assert registry["production_model_promotion"] is False
    assert registry["human_adjudication"]["local-002-outcome"] == "pending"
    assert registry["human_adjudication"]["local-003-quality"] == "pending"
    assert len(registry["frozen_scenes"]) == 3
