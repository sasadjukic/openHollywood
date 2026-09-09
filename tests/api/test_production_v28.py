"""Viewpoint guidance and response-boundary controls, not live semantic evaluations."""

from __future__ import annotations

import json
from copy import deepcopy
from dataclasses import replace
from pathlib import Path
from typing import Any
from uuid import uuid4

import pytest
from open_hollywood_api.services.production_model_executor import (
    _critic_evidence_catalog,
    _Execution,
    _messages,
    _normalize_point_of_view_check,
    _Operation,
    _output_schema,
    _point_of_view_check_schema,
)
from open_hollywood_engine.models import ModelDeployment
from open_hollywood_engine.workflows import (
    SCENE_PRODUCTION_GRAPH_VERSION,
    SCENE_PRODUCTION_PROMPT_TEMPLATE_VERSION,
)

from tests.api.test_production_v27 import _review, _violation
from tests.evaluations.test_agentic_production import _v17_catalog_test_execution

ROOT = Path(__file__).parents[2]
LOCAL_005_EXCERPT = "Cora felt the familiar, hot burn of being intellectually dismissed."


def _execution(
    prose: str,
    *,
    style: str = "Highly literary and internalized, with emotional counterpoints.",
    deployment: ModelDeployment = ModelDeployment.LOCAL,
    scene_plan: dict[str, object] | None = None,
    other_character_id: str = "cora",
) -> _Execution:
    execution = _v17_catalog_test_execution(
        scene_plan={"point_of_view_character_id": "elara"} if scene_plan is None else scene_plan,
        draft_prose=prose,
    )
    blueprint = {
        "artifact_kind": "story_blueprint",
        "artifact_key": "approved_blueprint",
        "artifact_version_id": str(uuid4()),
        "content": {
            "voice_and_style_guide": style,
            "characters": [
                {"id": "elara", "name": "Elara"},
                {"id": other_character_id, "name": other_character_id.title()},
            ],
        },
    }
    return replace(
        execution,
        specialist_role="scene_critic",
        selection=replace(execution.selection, deployment=deployment),
        inputs=(*execution.inputs, blueprint),
    )


def _prompt(execution: _Execution) -> tuple[str, dict[str, Any]]:
    messages = _messages(
        _Operation.CRITIQUE,
        execution,
        _output_schema(_Operation.CRITIQUE, continuity_schema_variant=None),
        continuity_schema_variant=None,
        continuity_model_context=None,
    )
    return messages[0].content, json.loads(messages[-1].content.rsplit("\n\n", 1)[-1])


@pytest.mark.parametrize("deployment", [ModelDeployment.LOCAL, ModelDeployment.CLOUD])
def test_both_routes_receive_balanced_viewpoint_guidance(deployment: ModelDeployment) -> None:
    execution = _execution(LOCAL_005_EXCERPT, deployment=deployment)
    original = deepcopy(execution.inputs)
    instructions, payload = _prompt(execution)
    contract = payload["viewpoint_contract"]
    assert contract["policy_version"] == "2"
    assert contract["assigned_character_id"] == "elara"
    assert contract["assignment_origin"] == "explicit_scene_plan"
    assert "literary, internalized, emotional" in instructions
    assert "do not authorize another character's private perspective" in instructions
    assert "A brief unauthorized intrusion still counts" in instructions
    assert "inference needs no special label" in instructions
    assert "not isolated verbs" in instructions
    assert "specifically authorizes that access" in instructions
    examples = contract["boundary_examples"]
    assert "not story facts or evidence" in examples["scope"]
    assert len(examples["allowed"]) == 3
    assert "Direct access to another character" in examples["unauthorized_private_state"]
    draft = next(
        a["content"] for a in payload["input_artifacts"] if a["artifact_kind"] == "scene_draft"
    )
    assert draft["evidence_catalog"] == [
        {
            "evidence_ref": _critic_evidence_catalog(execution)[0]["evidence_ref"],
            "exact_excerpt": LOCAL_005_EXCERPT,
        }
    ]
    assert "prose" not in draft
    assert execution.inputs == original


@pytest.mark.parametrize(
    "style",
    [
        "Use omniscient narration with access to both siblings' private thoughts in this scene.",
        "Alternate between Elara's and Cora's private perspectives within this scene.",
        "Avoid omniscient narration. Remain in Elara's perspective throughout this scene.",
    ],
)
def test_style_authority_is_preserved_without_keyword_inference(style: str) -> None:
    execution = _execution(LOCAL_005_EXCERPT, style=style)
    instructions, payload = _prompt(execution)
    assert payload["viewpoint_contract"]["approved_voice_and_style_guide"] == style
    assert "explicitly authorized perspective shifts must not be blocked" in instructions
    # No regex-derived permission or new model-authored certificate overrides approved prose.
    assert "shift_authorized" not in payload["viewpoint_contract"]
    assert _point_of_view_check_schema()["anyOf"][0]["required"] == ["status"]


@pytest.mark.parametrize(
    "prose,style",
    [
        ("I felt ashamed as I studied the handwriting.", "First-person, internalized prose."),
        ("Elara realized the pattern followed prime factors.", "Close third-person deductions."),
        ("Cora flinched; Elara recognized the old shame in that gesture.", "Close third person."),
        ("'I feel ashamed,' Cora said.", "Dialogue-driven, close third person."),
        ("Cora felt ashamed.", "Use omniscient access to both siblings' minds in this scene."),
    ],
)
def test_simulated_aligned_judgments_remain_certificate_free(prose: str, style: str) -> None:
    # Simulated correct decisions check transport/materialization, not model understanding.
    result = _normalize_point_of_view_check(
        _review({"status": "aligned"}), _execution(prose, style=style)
    )
    assert result["verdict"] == "pass"
    assert result["issues"] == []


@pytest.mark.parametrize(
    "prose,subject",
    [
        (LOCAL_005_EXCERPT, "cora"),
        ("Ivo privately felt a surge of shame.", "ivo"),
    ],
)
def test_reported_private_feeling_becomes_exact_blocker_despite_high_craft_score(
    prose: str, subject: str
) -> None:
    execution = _execution(prose, other_character_id=subject)
    review = _review(
        _violation(
            draft_evidence_refs=[_critic_evidence_catalog(execution)[0]["evidence_ref"]],
            subject_character_id=subject,
            assessment=f"{subject.title()}'s private feeling lacks an authorized shift.",
            recommended_resolution="Use observable behavior or the assigned viewpoint's inference.",
        )
    )
    review["overall_score"] = 5
    result = _normalize_point_of_view_check(review, execution)
    assert result["overall_score"] == 5
    assert result["verdict"] == "revise"
    assert result["issues"][0]["category"] == "scene_assignment:point_of_view_character_id"
    assert result["issues"][0]["severity"] == "blocking"
    assert result["issues"][0]["evidence"] == [prose]


def test_validated_false_negative_is_not_a_semantic_pass() -> None:
    # Reproduce the v27 limitation honestly: the boundary cannot infer literary truth.
    result = _normalize_point_of_view_check(
        _review({"status": "aligned"}), _execution(LOCAL_005_EXCERPT)
    )
    assert result["verdict"] == "pass"
    assert result["issues"] == []
    # The live probe's separately declared expectation must catch this wrong judgment.
    registry = json.loads(
        (ROOT / "benchmarks/v0.1/production-probes-v28.json").read_text(encoding="utf-8")
    )
    positive = next(case for case in registry["cases"] if case["name"] == "local-005-critic")
    assert positive["expected_viewpoint_outcome"] == "blocking_unauthorized_private_state"
    assert positive["reference_evidence_excerpt"] == LOCAL_005_EXCERPT


@pytest.mark.parametrize(
    "plan,origin,assigned",
    [
        ({}, "unassigned", None),
        ({"character_ids": ["elara"]}, "single_character_fallback", "elara"),
    ],
)
def test_assignment_origin_does_not_invent_a_narrative_mode(
    plan: dict[str, object], origin: str, assigned: str | None
) -> None:
    _, payload = _prompt(_execution("Elara took a breath.", scene_plan=plan))
    contract = payload["viewpoint_contract"]
    assert contract["assignment_origin"] == origin
    assert contract["assigned_character_id"] == assigned
    assert "Do not invent an assignment or a stricter narrative mode" in contract["policy"]


def test_targeted_probe_registry_preserves_inputs_and_does_not_claim_live_success() -> None:
    previous = json.loads(
        (ROOT / "benchmarks/v0.1/production-probes-v27.json").read_text(encoding="utf-8")
    )
    current = json.loads(
        (ROOT / "benchmarks/v0.1/production-probes-v28.json").read_text(encoding="utf-8")
    )
    assert current["status"] == "prepared_not_run"
    assert current["candidate_prompt_version"] == "28"  # Historical registry stays pinned.
    assert SCENE_PRODUCTION_PROMPT_TEMPLATE_VERSION == "29"
    assert current["candidate_graph_version"] == SCENE_PRODUCTION_GRAPH_VERSION == "7"
    assert current["maximum_calls_per_probe"] == 2
    assert [case["name"] for case in current["cases"]] == [
        "local-002-critic",
        "local-003-critic",
        "local-005-critic",
    ]
    for case in current["cases"]:
        original = next(item for item in previous["cases"] if item["name"] == case["name"])
        assert (case["source"], case["invocation_id"]) == (
            original["source"],
            original["invocation_id"],
        )
