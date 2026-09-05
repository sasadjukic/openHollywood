"""Offline regressions for v24 false critic blockers and v25 assignment certificates."""

from __future__ import annotations

import json
from dataclasses import replace
from typing import Any, cast

import pytest
from open_hollywood_api.services.production_model_executor import (
    _critic_prompt_inputs,
    _critic_requirement_scope,
    _messages,
    _normalize_scene_assignment_critique,
    _Operation,
    _output_schema,
    _StructuredOutputContractError,
)
from open_hollywood_engine.artifacts import ArtifactKind

from tests.evaluations.test_agentic_production import _v17_catalog_test_execution


@pytest.mark.parametrize(
    ("category", "description"),
    [
        (
            "Minor Thematic Foreshadowing",
            "The scene concludes with Elara feeling a sense of victory based on math. "
            "While this is correct for Scene 1, the narrative needs to subtly plant seeds "
            "that this mathematical conclusion is insufficient. "
            "This is a note for the next scene, not a failure of the current one.",
        ),
        (
            "Minor Structural Polish",
            "While the effect is correct, weaving the feeling of that shift more deeply "
            "into Brick's immediate, visceral reaction would elevate the scene by keeping "
            "the focus tightly on the POV character's internal processing.",
        ),
    ],
)
def test_canary_polish_notes_do_not_become_hard_revisions(category: str, description: str) -> None:
    execution = _v17_catalog_test_execution()
    issue = {
        "category": category,
        "severity": "minor",
        "description": description,
        "evidence": ["The scene achieves its intended outcome."],
        "recommendation": "Retain this scene; consider this advice for later polish.",
    }
    critique = {"issues": [issue], "verdict": "pass", "assignment_violations": []}

    result = _normalize_scene_assignment_critique(critique, execution)

    assert result == {"issues": [issue], "verdict": "pass"}


def _violation(**updates: str) -> dict[str, str]:
    return {
        "anchor": "point_of_view_character_id",
        "draft_evidence": "Sylvie listened to the wall.",
        "explanation": "Sylvie replaces Mara as the assigned viewpoint character.",
        "recommended_resolution": "Restore Mara's perspective without replacing the scene.",
        **updates,
    }


def test_assignment_violation_binds_exact_draft_and_plan_before_promotion() -> None:
    execution = _v17_catalog_test_execution(
        scene_plan={"point_of_view_character_id": "mara", "character_ids": ["mara"]},
        draft_prose="Sylvie listened to the wall.",
    )

    result = _normalize_scene_assignment_critique(
        {"issues": [], "verdict": "pass", "assignment_violations": [_violation()]},
        execution,
    )

    assert result["verdict"] == "revise"
    issue = cast(list[dict[str, Any]], result["issues"])[0]
    assert issue["severity"] == "blocking"
    assert issue["category"] == "scene_assignment:point_of_view_character_id"
    assert '"mara"' in issue["description"]
    assert issue["evidence"] == ["Sylvie listened to the wall."]
    assert "assignment_violations" not in result


@pytest.mark.parametrize(
    ("violation", "error_type"),
    [
        (_violation(draft_evidence="Mara ran away."), "assignment_evidence_not_in_current_draft"),
        (_violation(anchor="future_scene"), "invalid_assignment_anchor"),
        (_violation(anchor="turning_point"), "invalid_assignment_anchor"),
        (_violation(explanation=""), "invalid_assignment_violation"),
    ],
)
def test_assignment_violation_rejects_invented_evidence_or_unassigned_anchors(
    violation: dict[str, str], error_type: str
) -> None:
    execution = _v17_catalog_test_execution(
        scene_plan={"point_of_view_character_id": "mara"},
        draft_prose="Sylvie listened to the wall.",
    )

    with pytest.raises(_StructuredOutputContractError) as failure:
        _normalize_scene_assignment_critique(
            {"verdict": "pass", "assignment_violations": [violation]}, execution
        )

    assert failure.value.issue_type == error_type


def test_critic_schema_requires_explicit_empty_assignment_audit() -> None:
    schema = _output_schema(_Operation.CRITIQUE, continuity_schema_variant=None)
    assert "assignment_violations" in schema["required"]
    assert "overall_score" not in schema["properties"]
    with pytest.raises(_StructuredOutputContractError) as failure:
        _normalize_scene_assignment_critique(
            {"issues": [], "verdict": "pass"}, _v17_catalog_test_execution()
        )
    assert failure.value.issue_type == "invalid_assignment_violation"


def test_wrong_location_has_an_explicit_assignment_route() -> None:
    execution = _v17_catalog_test_execution(
        scene_plan={"location_id": "locked_cell"},
        draft_prose="The entire scene takes place on the ocean liner.",
    )
    result = _normalize_scene_assignment_critique(
        {
            "issues": [],
            "verdict": "pass",
            "assignment_violations": [
                _violation(
                    anchor="location_id",
                    draft_evidence="The entire scene takes place on the ocean liner.",
                    explanation="The assigned locked cell is replaced, without a transition.",
                    recommended_resolution="Restore the assigned location.",
                )
            ],
        },
        execution,
    )
    assert result["verdict"] == "revise"
    assert result["issues"][0]["category"] == "scene_assignment:location_id"


def test_critic_obligations_defer_story_requirement_until_final_scene() -> None:
    story_requirement = "The new stroller remains central to the plot."
    execution = replace(
        _v17_catalog_test_execution(
            required_elements=[story_requirement],
            scene_plan={"turning_point": "Mara notices the open window."},
        ),
        unit_count=3,
    )
    scope = _critic_requirement_scope(execution)
    assert story_requirement not in json.dumps(scope)
    assert "Mara notices the open window." in json.dumps(scope)
    plans = [
        item["content"]
        for item in _critic_prompt_inputs(execution)
        if item["artifact_kind"] == ArtifactKind.SCENE_PLAN.value
    ]
    assert plans[0]["required_elements"] == []
    final_scope = _critic_requirement_scope(replace(execution, unit_number=3))
    assert story_requirement in json.dumps(final_scope)


def test_critic_prompt_has_one_explicit_requirement_scope() -> None:
    story_requirement = "The new stroller remains central to the plot."
    execution = replace(
        _v17_catalog_test_execution(required_elements=[story_requirement]), unit_count=3
    )
    schema = _output_schema(_Operation.CRITIQUE, continuity_schema_variant=None)
    messages = _messages(
        _Operation.CRITIQUE,
        execution,
        schema,
        continuity_schema_variant=None,
        continuity_model_context=None,
    )
    payload = json.loads(messages[-1].content)
    assert "required_elements" not in payload["frozen_benchmark_constraints"]
    assert payload["critic_requirement_scope"]["story_wide_requirements_due"] is False
    assert story_requirement not in json.dumps(payload)
