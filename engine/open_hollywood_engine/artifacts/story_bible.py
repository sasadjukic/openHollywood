"""Deterministic reduction and invariants for canonical story-bible snapshots."""

from __future__ import annotations

from collections.abc import Callable, Iterable

from open_hollywood_engine.artifacts.schemas import (
    StoryBible,
    StoryBibleUpdate,
    StoryThreadStatus,
)


class StoryBibleInvariantError(ValueError):
    """Raised when a proposed canonical transition is not monotonic or traceable."""


def apply_story_bible_update(
    current: StoryBible,
    update: StoryBibleUpdate,
) -> StoryBible:
    """Apply one typed scene delta using a stable, fail-closed reducer."""
    next_scene_number = len(current.accepted_scenes) + 1
    scene = update.accepted_scene
    if scene.scene_number != next_scene_number:
        raise StoryBibleInvariantError(f"story-bible scene number must be {next_scene_number}")
    if scene.scene_id in {item.scene_id for item in current.accepted_scenes}:
        raise StoryBibleInvariantError("accepted scene ID is already present in the story bible")
    if scene.artifact_version_id in {item.artifact_version_id for item in current.accepted_scenes}:
        raise StoryBibleInvariantError(
            "accepted scene version is already present in the story bible"
        )

    _require_new_ids(
        (event.id for event in update.timeline_events),
        (event.id for event in current.timeline),
        "timeline event",
    )
    expected_timeline_sequences = tuple(
        range(
            len(current.timeline) + 1,
            len(current.timeline) + len(update.timeline_events) + 1,
        )
    )
    if tuple(event.sequence for event in update.timeline_events) != expected_timeline_sequences:
        raise StoryBibleInvariantError("new timeline events must continue the canonical sequence")
    _require_new_ids(
        (fact.id for fact in update.established_facts),
        (fact.id for fact in current.established_facts),
        "established fact",
    )
    _require_known_ids(
        (state.character_id for state in update.character_states),
        current.character_ids,
        "character-state character",
    )
    _require_known_ids(
        (state.relationship_id for state in update.relationship_states),
        current.relationship_ids,
        "relationship-state relationship",
    )
    _require_known_ids(
        (state.location_id for state in update.location_states),
        current.location_ids,
        "location-state location",
    )

    accepted_scene_ids = {
        *(item.scene_id for item in current.accepted_scenes),
        scene.scene_id,
    }
    current_threads = {thread.id: thread for thread in current.threads}
    for thread in update.thread_changes:
        existing = current_threads.get(thread.id)
        if existing is None:
            if thread.introduced_scene_id not in accepted_scene_ids:
                raise StoryBibleInvariantError(
                    f"new story thread {thread.id!r} has an unknown introduction scene"
                )
            continue
        if (
            thread.kind is not existing.kind
            or thread.statement != existing.statement
            or thread.introduced_scene_id != existing.introduced_scene_id
        ):
            raise StoryBibleInvariantError(f"story thread {thread.id!r} changed immutable identity")
        if (
            existing.status is StoryThreadStatus.RESOLVED
            and thread.status is StoryThreadStatus.OPEN
        ):
            raise StoryBibleInvariantError(f"resolved story thread {thread.id!r} cannot reopen")

    new_prohibitions = set(update.prohibited_contradictions)
    if len(new_prohibitions) != len(update.prohibited_contradictions):
        raise StoryBibleInvariantError("new prohibited contradictions must be unique")
    duplicate_prohibitions = set(current.prohibited_contradictions) & new_prohibitions
    if duplicate_prohibitions:
        raise StoryBibleInvariantError("prohibited contradictions must be new canonical entries")

    return StoryBible(
        source_blueprint_version_id=current.source_blueprint_version_id,
        character_ids=current.character_ids,
        relationship_ids=current.relationship_ids,
        location_ids=current.location_ids,
        world_rule_ids=current.world_rule_ids,
        accepted_scenes=(*current.accepted_scenes, scene),
        timeline=(*current.timeline, *update.timeline_events),
        established_facts=(*current.established_facts, *update.established_facts),
        character_states=_upsert(
            current.character_states,
            update.character_states,
            key=lambda item: item.character_id,
        ),
        relationship_states=_upsert(
            current.relationship_states,
            update.relationship_states,
            key=lambda item: item.relationship_id,
        ),
        location_states=_upsert(
            current.location_states,
            update.location_states,
            key=lambda item: item.location_id,
        ),
        threads=_upsert(
            current.threads,
            update.thread_changes,
            key=lambda item: item.id,
        ),
        prohibited_contradictions=(
            *current.prohibited_contradictions,
            *sorted(update.prohibited_contradictions),
        ),
    )


def validate_story_bible_transition(
    current: StoryBible,
    update: StoryBibleUpdate,
    candidate: StoryBible,
) -> None:
    """Require persisted output to equal the deterministic reducer exactly."""
    expected = apply_story_bible_update(current, update)
    if candidate != expected:
        raise StoryBibleInvariantError(
            "updated story bible does not equal the deterministic transition"
        )


def _upsert[T](
    current: tuple[T, ...],
    changes: tuple[T, ...],
    *,
    key: Callable[[T], str],
) -> tuple[T, ...]:
    """Replace existing records in place and append new records by stable key."""
    change_by_key = {key(item): item for item in changes}
    if len(change_by_key) != len(changes):
        raise StoryBibleInvariantError("story-bible update keys must be unique")
    result = [change_by_key.pop(key(item), item) for item in current]
    result.extend(change_by_key[item_key] for item_key in sorted(change_by_key))
    return tuple(result)


def _require_new_ids(
    proposed: Iterable[str],
    existing: Iterable[str],
    label: str,
) -> None:
    proposed_ids = tuple(proposed)
    existing_ids = set(existing)
    if len(set(proposed_ids)) != len(proposed_ids):
        raise StoryBibleInvariantError(f"new {label} IDs must be unique")
    duplicates = set(proposed_ids) & existing_ids
    if duplicates:
        raise StoryBibleInvariantError(f"{label} IDs already exist: {sorted(duplicates)}")


def _require_known_ids(
    proposed: Iterable[str],
    known: tuple[str, ...],
    label: str,
) -> None:
    proposed_ids = tuple(proposed)
    if len(set(proposed_ids)) != len(proposed_ids):
        raise StoryBibleInvariantError(f"{label} IDs must be unique")
    unknown = set(proposed_ids) - set(known)
    if unknown:
        raise StoryBibleInvariantError(f"unknown {label} IDs: {sorted(unknown)}")
