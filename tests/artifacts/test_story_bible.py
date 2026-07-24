"""Deterministic canonical story-bible update and continuity tests."""

from __future__ import annotations

from uuid import NAMESPACE_URL, UUID, uuid5

import pytest
from open_hollywood_engine.artifacts import (
    ContinuityCategory,
    ContinuityFinding,
    ContinuityReport,
    ContinuitySeverity,
    StoryBible,
    StoryBibleCharacterState,
    StoryBibleFact,
    StoryBibleInvariantError,
    StoryBibleScene,
    StoryBibleThread,
    StoryBibleTimelineEvent,
    StoryBibleUpdate,
    StoryThreadKind,
    StoryThreadStatus,
    apply_story_bible_update,
    validate_story_bible_transition,
)
from pydantic import ValidationError


def test_story_bible_update_is_exact_monotonic_and_reproducible() -> None:
    initial = _initial_bible()
    update = _scene_one_update()

    first = apply_story_bible_update(initial, update)
    second = apply_story_bible_update(initial, update)

    assert first == second
    assert first.accepted_scenes == (update.accepted_scene,)
    assert first.established_facts[0].id == "dry_wheels"
    assert first.character_states[0].knowledge_fact_ids == ("dry_wheels",)
    assert first.threads[0].status is StoryThreadStatus.OPEN
    validate_story_bible_transition(initial, update, first)


def test_story_bible_rejects_duplicate_facts_and_nonsequential_events() -> None:
    current = apply_story_bible_update(_initial_bible(), _scene_one_update())
    duplicate = _scene_two_update(fact_id="dry_wheels")

    with pytest.raises(StoryBibleInvariantError, match="already exist"):
        apply_story_bible_update(current, duplicate)

    wrong_sequence = _scene_two_update(timeline_sequence=3)
    with pytest.raises(StoryBibleInvariantError, match="continue the canonical sequence"):
        apply_story_bible_update(current, wrong_sequence)


def test_resolved_threads_cannot_reopen_or_change_identity() -> None:
    scene_one = apply_story_bible_update(_initial_bible(), _scene_one_update())
    resolved = apply_story_bible_update(scene_one, _scene_two_update())
    reopened = StoryBibleUpdate(
        source_story_bible_version_id=_id("bible-2"),
        continuity_report_version_id=_id("continuity-3"),
        accepted_scene=StoryBibleScene(
            scene_id="scene_3",
            scene_number=3,
            artifact_version_id=_id("scene-3"),
        ),
        timeline_events=(
            StoryBibleTimelineEvent(
                id="event_3",
                sequence=3,
                scene_id="scene_3",
                time_context="Before dawn",
                summary="Mara records the confession.",
                character_ids=("mara",),
                location_id="tower_lot",
            ),
        ),
        thread_changes=(
            StoryBibleThread(
                id="stroller_origin",
                kind=StoryThreadKind.MYSTERY,
                statement="Who placed the stroller outside the tower?",
                introduced_scene_id="scene_1",
                status=StoryThreadStatus.OPEN,
            ),
        ),
    )

    with pytest.raises(StoryBibleInvariantError, match="cannot reopen"):
        apply_story_bible_update(resolved, reopened)


def test_transition_must_equal_the_deterministic_reducer() -> None:
    initial = _initial_bible()
    update = _scene_one_update()
    wrong = StoryBible(
        **{
            **apply_story_bible_update(initial, update).model_dump(),
            "prohibited_contradictions": (
                "The stroller cannot become rain-soaked without explanation.",
                "An untraceable extra invariant.",
            ),
        }
    )

    with pytest.raises(StoryBibleInvariantError, match="does not equal"):
        validate_story_bible_transition(initial, update, wrong)


def test_continuity_report_requires_full_coverage_and_routes_severe_findings() -> None:
    finding = ContinuityFinding(
        id="wet_stroller",
        severity=ContinuitySeverity.ERROR,
        category=ContinuityCategory.FACT,
        summary="The accepted bible says the wheels are dry, but the draft says soaked.",
        evidence=("Story bible fact dry_wheels.", "Candidate Scene 2 opening."),
        related_scene_ids=("scene_1", "scene_2"),
        recommended_resolution="Keep the stroller dry.",
    )
    report = ContinuityReport(
        story_bible_version_id=_id("bible-1"),
        scene_version_id=_id("scene-2"),
        scene_plan_version_id=_id("scene-plan-2"),
        scene_id="scene_2",
        scene_number=2,
        checked_categories=tuple(ContinuityCategory),
        findings=(finding,),
    )

    assert report.has_blocking_findings

    with pytest.raises(ValidationError, match="every category"):
        ContinuityReport.model_validate(
            {
                **report.model_dump(),
                "checked_categories": (ContinuityCategory.FACT,),
            }
        )


def _initial_bible() -> StoryBible:
    return StoryBible(
        source_blueprint_version_id=_id("blueprint"),
        character_ids=("mara", "nikola"),
        relationship_ids=("mara_nikola",),
        location_ids=("tower_lot",),
        world_rule_ids=("truth_moves_stroller",),
    )


def _scene_one_update() -> StoryBibleUpdate:
    return StoryBibleUpdate(
        source_story_bible_version_id=_id("bible-0"),
        continuity_report_version_id=_id("continuity-1"),
        accepted_scene=StoryBibleScene(
            scene_id="scene_1",
            scene_number=1,
            artifact_version_id=_id("scene-1"),
        ),
        timeline_events=(
            StoryBibleTimelineEvent(
                id="event_1",
                sequence=1,
                scene_id="scene_1",
                time_context="One autumn night",
                summary="Mara finds the untouched stroller.",
                character_ids=("mara",),
                location_id="tower_lot",
            ),
        ),
        established_facts=(
            StoryBibleFact(
                id="dry_wheels",
                statement="The stroller wheels remain dry despite the rain.",
                established_scene_id="scene_1",
                character_ids=("mara",),
                location_ids=("tower_lot",),
            ),
        ),
        character_states=(
            StoryBibleCharacterState(
                character_id="mara",
                current_location_id="tower_lot",
                physical_state="Uninjured and inside the fence.",
                emotional_state="Professionally guarded but unsettled.",
                current_goal="Inspect the tower entrance.",
                knowledge_fact_ids=("dry_wheels",),
                last_updated_scene_id="scene_1",
            ),
        ),
        thread_changes=(
            StoryBibleThread(
                id="stroller_origin",
                kind=StoryThreadKind.MYSTERY,
                statement="Who placed the stroller outside the tower?",
                introduced_scene_id="scene_1",
                status=StoryThreadStatus.OPEN,
            ),
        ),
        prohibited_contradictions=("The stroller cannot become rain-soaked without explanation.",),
    )


def _scene_two_update(
    *,
    fact_id: str = "nikola_bought_stroller",
    timeline_sequence: int = 2,
) -> StoryBibleUpdate:
    return StoryBibleUpdate(
        source_story_bible_version_id=_id("bible-1"),
        continuity_report_version_id=_id("continuity-2"),
        accepted_scene=StoryBibleScene(
            scene_id="scene_2",
            scene_number=2,
            artifact_version_id=_id("scene-2"),
        ),
        timeline_events=(
            StoryBibleTimelineEvent(
                id="event_2",
                sequence=timeline_sequence,
                scene_id="scene_2",
                time_context="Later that night",
                summary="Nikola admits that he bought the stroller.",
                character_ids=("mara", "nikola"),
                location_id="tower_lot",
            ),
        ),
        established_facts=(
            StoryBibleFact(
                id=fact_id,
                statement="Nikola bought the stroller.",
                established_scene_id="scene_2",
                character_ids=("nikola",),
                location_ids=("tower_lot",),
            ),
        ),
        thread_changes=(
            StoryBibleThread(
                id="stroller_origin",
                kind=StoryThreadKind.MYSTERY,
                statement="Who placed the stroller outside the tower?",
                introduced_scene_id="scene_1",
                status=StoryThreadStatus.RESOLVED,
                resolved_scene_id="scene_2",
                resolution="Nikola bought and placed it as an offering.",
            ),
        ),
    )


def _id(label: str) -> UUID:
    return uuid5(NAMESPACE_URL, label)
