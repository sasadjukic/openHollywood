"""v26 regression controls: reviewer format is not a manuscript defect."""

from __future__ import annotations

import json
from copy import deepcopy
from dataclasses import replace
from typing import Any

import pytest
from open_hollywood_api.services.production_model_executor import (
    _critic_prompt_inputs,
    _messages,
    _normalize_point_of_view_check,
    _Operation,
    _original_allegation_ledger,
    _output_schema,
    _point_of_view_check_schema,
    _safe_structured_failure_detail,
    _structured_failure_issues,
    _StructuredOutputContractError,
)
from open_hollywood_engine.artifacts import ContinuityReport
from open_hollywood_engine.workflows import ContinuityRevisionLimitError, initial_production_state
from open_hollywood_engine.workflows.production_graph import (
    _adjudication_status,
    _review_disposition,
)

from tests.api.test_production_v26 import _report
from tests.evaluations.test_agentic_production import (
    _schema_test_continuity_context,
    _v17_catalog_test_execution,
)
from tests.workflows.test_scene_production import _passing_production_input


def _review(check: dict[str, Any]) -> dict[str, Any]:
    return {
        "point_of_view_check": check,
        "assignment_violations": [],
        "issues": [],
        "verdict": "pass",
    }


def _violation(**changes: Any) -> dict[str, Any]:
    return {
        "status": "violation",
        "violation_kind": "unauthorized_private_state",
        "subject_character_id": "cora",
        "draft_evidence_refs": ["draft_evidence_0001"],
        "assessment": "Cora's unspoken private knowledge replaces Elara's perspective.",
        "recommended_resolution": "Retain Cora's observable reaction, not private knowledge.",
        **changes,
    }


@pytest.mark.parametrize(
    "prose",
    [
        "I was supposed to be proofreading Chapter Three of the monograph "
        "on late-Byzantine watermarks.",
        "The sheer, unyielding regularity of the anomaly was profoundly compelling to her "
        "observational skills. It suggested a systemic necessity, a cycle encoded within "
        "the building's very bones.",
        "Elara watched Cora flinch and guessed she was frightened.",
    ],
)
def test_aligned_review_needs_no_quotation_even_for_interiority(prose: str) -> None:
    execution = _v17_catalog_test_execution(
        scene_plan={"point_of_view_character_id": "elara"},
        draft_prose=prose,
    )
    result = _normalize_point_of_view_check(_review({"status": "aligned"}), execution)
    assert result == {"assignment_violations": [], "issues": [], "verdict": "pass"}
    aligned = _point_of_view_check_schema()["anyOf"][0]
    assert aligned["required"] == ["status"]


def test_unassigned_viewpoint_is_application_owned() -> None:
    result = _normalize_point_of_view_check(
        _review({"status": "aligned"}),
        _v17_catalog_test_execution(),
    )
    assert not result["issues"]


def test_true_other_mind_violation_resolves_handles_and_still_blocks() -> None:
    prose = "Cora privately knew the body was her father's. Elara did not know."
    execution = _v17_catalog_test_execution(
        scene_plan={"point_of_view_character_id": "elara"},
        draft_prose=prose,
    )
    result = _normalize_point_of_view_check(
        _review(_violation(draft_evidence_refs=["draft_evidence_0001", "draft_evidence_0002"])),
        execution,
    )
    assert result["verdict"] == "revise"
    assert result["issues"][0]["severity"] == "blocking"
    assert result["issues"][0]["evidence"] == [
        "Cora privately knew the body was her father's.",
        "Elara did not know.",
    ]


@pytest.mark.parametrize(
    "changes,reason",
    [
        ({"subject_character_id": "elara"}, "viewpoint_subject_not_other_character"),
        ({"violation_kind": "reviewer_response_error"}, "invalid_viewpoint_audit"),
        ({"draft_evidence_refs": []}, "viewpoint_evidence_reference_invalid"),
        ({"draft_evidence_refs": ["draft_evidence_9999"]}, "viewpoint_evidence_reference_invalid"),
        ({"draft_evidence_refs": ["Elara watches Cora."]}, "viewpoint_evidence_reference_invalid"),
    ],
)
def test_invalid_review_never_becomes_a_story_revision(
    changes: dict[str, Any], reason: str
) -> None:
    execution = _v17_catalog_test_execution(scene_plan={"point_of_view_character_id": "elara"})
    with pytest.raises(_StructuredOutputContractError) as failure:
        _normalize_point_of_view_check(_review(_violation(**changes)), execution)
    assert failure.value.issue_type == reason
    assert _structured_failure_issues(failure.value)[0]["type"] == reason


def test_local_002_metadata_allegation_cannot_bypass_viewpoint_audit() -> None:
    execution = _v17_catalog_test_execution(scene_plan={"point_of_view_character_id": "elara"})
    review = _review({"status": "aligned"})
    review["issues"] = [
        {
            "category": "scene_assignment:point_of_view_character_id",
            "severity": "blocking",
            "recommendation": "No content change is needed, only structural metadata.",
        }
    ]
    with pytest.raises(_StructuredOutputContractError, match="validated assignment audit"):
        _normalize_point_of_view_check(review, execution)


def test_repair_packet_does_not_feed_failure_prose_back_as_story_evidence() -> None:
    failure_prose = "The system flagged a technical violation requiring the exact current evidence."
    execution = replace(
        _v17_catalog_test_execution(),
        previous_failure={
            "error_code": "schema_validation_failed",
            "error_message": failure_prose,
            "validation_issues": [
                {
                    "location": "point_of_view_check",
                    "type": "invalid_viewpoint_audit",
                    "message": failure_prose,
                    "received_value": failure_prose,
                }
            ],
        },
    )
    messages = _messages(
        _Operation.CRITIQUE,
        execution,
        _output_schema(_Operation.CRITIQUE, continuity_schema_variant=None),
        continuity_schema_variant=None,
        continuity_model_context=None,
    )
    payload = json.loads(messages[-1].content)
    assert failure_prose not in json.dumps(payload)
    assert payload["retry_context"]["manuscript_defect_established"] is False
    assert "review JSON" in str(payload["schema_repair"])


def test_critic_receives_current_prose_once_as_evidence_catalog_without_mutating_input() -> None:
    execution = _v17_catalog_test_execution(draft_prose="Elara's inference was her own.")
    original = deepcopy(execution.inputs)
    payload = _critic_prompt_inputs(execution)
    draft = next(item["content"] for item in payload if item["artifact_kind"] == "scene_draft")
    assert "prose" not in draft
    assert draft["evidence_catalog"][0]["exact_excerpt"] == "Elara's inference was her own."
    assert execution.inputs == original


def test_original_allegation_does_not_follow_later_goalpost_changes() -> None:
    context = _schema_test_continuity_context(recheck=True)
    first: dict[str, Any] = {
        "artifact_version_id": "first-report",
        "content": {
            "findings": [
                {
                    "id": "issue_1",
                    "severity": "blocking",
                    "basis": "contradiction",
                    "summary": "The ratio is unsupported.",
                    "evidence": ["a ratio"],
                    "recommended_resolution": "Remove the ratio.",
                    "canonical_source_refs": [],
                }
            ]
        },
    }
    later = deepcopy(first)
    later["artifact_version_id"] = "later-report"
    later["content"]["findings"][0]["summary"] = "Any relationship is unsupported."
    context = replace(context, previous_continuity_report=later, continuity_history=(first, later))
    ledger = _original_allegation_ledger(context)
    assert ledger[0]["original_allegation"] == "The ratio is unsupported."
    assert ledger[0]["original_report_version_id"] == "first-report"
    assert "Any relationship" not in json.dumps(ledger)


def test_terminal_error_exposes_both_gates_and_why_adjudication_was_skipped() -> None:
    production = _passing_production_input()
    state = initial_production_state(production)
    state.update({"critique_blocking_issue_count": 1, "critique_blocking_issue_indexes": [2]})
    report = ContinuityReport.model_validate(_report())
    with pytest.raises(ContinuityRevisionLimitError) as failure:
        _review_disposition(state, production, production.units[0], 2, report)
    diagnostic = json.loads(str(failure.value).split("; review_gates=")[1].split("; blockers=")[0])
    assert diagnostic["critique_issue_indexes"] == [2]
    assert diagnostic["continuity_blocking_finding_ids"] == ["disputed"]
    assert diagnostic["adjudication"] == "skipped_hard_critic_blockers"
    state["critique_blocking_issue_count"] = 0
    assert _adjudication_status(state, production, 2, report) == "eligible"
    state["adjudication_completed"] = True
    assert _adjudication_status(state, production, 2, report) == "completed"


def test_diagnostic_redaction_precedes_truncation(monkeypatch: pytest.MonkeyPatch) -> None:
    secret = "test-only-long-viewpoint-diagnostic-credential"
    monkeypatch.setenv("OLLAMA_API_KEY", secret)
    detail = _safe_structured_failure_detail("x" * 480 + secret + "trailing text")
    assert detail is not None
    assert "test-only-long" not in detail
    assert "[REDACTED]" in detail
