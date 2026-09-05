"""Nonblocking observations about names in an immutable approved Blueprint.

Explicit entity IDs are validated by StoryBlueprint; this deliberately narrower
check cannot decide whether an unregistered prose name is an alias, another
place, or a contradiction. It must never certify a blocker or rewrite canon.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from open_hollywood_engine.artifacts.schemas import StoryBlueprint

# Only named buildings are inspected. This is not a general proper-noun parser:
# generic "the building" and other creative description are left alone.
_NAMED_BUILDING = re.compile(r"\b(?:[A-Z][A-Za-z'’\-]*[ \t]+){1,3}(?:[Bb]uilding|[Tt]ower)\b")


@dataclass(frozen=True, slots=True)
class BlueprintNameObservation:
    """An uncertain prose-name observation with an exact source field."""

    source_path: str
    source_entity_id: str
    observed_name: str

    def to_data(self) -> dict[str, object]:
        """Return an explicitly advisory, JSON-compatible event record."""
        return {
            "code": "unregistered_building_mention",
            "severity": "warning",
            "blocks_production": False,
            "source_path": self.source_path,
            "source_entity_id": self.source_entity_id,
            "observed_name": self.observed_name,
            "interpretation": (
                "This prose name is absent from registered Location names. It may name "
                "a distinct place or an alias; this is not a proven contradiction. "
                "Review entity naming without changing the approved artifact in place."
            ),
        }


def blueprint_name_observations(
    blueprint: StoryBlueprint,
) -> tuple[BlueprintNameObservation, ...]:
    """Notice unregistered building names in character descriptions without gating."""
    registered_names = tuple(_normalized_name(location.name) for location in blueprint.locations)
    observations: list[BlueprintNameObservation] = []
    for index, character in enumerate(blueprint.characters):
        seen: set[str] = set()
        for match in _NAMED_BUILDING.finditer(character.description):
            mention = match.group(0)
            normalized = _normalized_name(mention)
            if normalized in seen or any(
                re.search(rf"(?<!\w){re.escape(normalized)}(?!\w)", name)
                for name in registered_names
            ):
                continue
            seen.add(normalized)
            observations.append(
                BlueprintNameObservation(
                    source_path=f"characters[{index}].description",
                    source_entity_id=character.id,
                    observed_name=mention,
                )
            )
    return tuple(observations)


def _normalized_name(value: str) -> str:
    normalized = " ".join(value.casefold().split())
    return normalized.removeprefix("the ")
