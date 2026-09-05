"""Nonblocking name observations must not turn prose guesses into canon gates."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from open_hollywood_engine.artifacts import StoryBlueprint
from open_hollywood_engine.artifacts.blueprint_integrity import blueprint_name_observations

from tests.artifacts.test_schemas import _blueprint


def _with_place_description(description: str, location_name: str) -> StoryBlueprint:
    blueprint = _blueprint()
    character = blueprint.characters[0].model_copy(update={"description": description})
    location = blueprint.locations[0].model_copy(update={"name": location_name})
    return blueprint.model_copy(
        update={
            "characters": (character, *blueprint.characters[1:]),
            "locations": (location, *blueprint.locations[1:]),
        }
    )


def test_v24_unregistered_building_is_advisory_and_does_not_rewrite_blueprint() -> None:
    fixture_path = Path(__file__).parents[1] / "fixtures" / "production_v24_regressions.json"
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))["blueprint_place_mention"]
    blueprint = _with_place_description(fixture["character_description"], fixture["location_name"])
    frozen_content = blueprint.model_dump_json()

    observations = blueprint_name_observations(blueprint)

    assert len(observations) == 1
    assert observations[0].observed_name == "Hawthorne building"
    assert observations[0].source_path == "characters[0].description"
    assert observations[0].source_entity_id == blueprint.characters[0].id
    assert observations[0].to_data()["blocks_production"] is False
    assert "not a proven contradiction" in str(observations[0].to_data()["interpretation"])
    assert blueprint.model_dump_json() == frozen_content


@pytest.mark.parametrize(
    ("description", "location_name"),
    [
        ("She lives in the building.", "The Hallways of Blackwood Tower"),
        ("She lives in Blackwood Tower.", "The Hallways of Blackwood Tower"),
        ("She lives in The Blackwood Tower.", "The Hallways of Blackwood Tower"),
        ("She lives in Hawthorne building.", "The Hawthorne Building"),
        ("She sees the tower in a dream.", "The Hallways of Blackwood Tower"),
    ],
)
def test_registered_names_and_generic_prose_do_not_warn(
    description: str, location_name: str
) -> None:
    assert blueprint_name_observations(_with_place_description(description, location_name)) == ()


def test_distinct_place_is_reported_as_uncertain_not_as_renaming_instruction() -> None:
    blueprint = _with_place_description(
        "She left Hawthorne building before moving to Blackwood Tower. "
        "She remembers Hawthorne building fondly.",
        "The Hallways of Blackwood Tower",
    )

    observations = blueprint_name_observations(blueprint)

    assert len(observations) == 1
    assert observations[0].observed_name == "Hawthorne building"
    assert observations[0].to_data()["severity"] == "warning"
    assert "distinct place or an alias" in str(observations[0].to_data()["interpretation"])
