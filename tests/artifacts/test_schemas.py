"""Tests for provider-neutral structured creative artifacts."""

from __future__ import annotations

from typing import Any
from uuid import uuid4

import pytest
from open_hollywood_engine.artifacts import (
    ARTIFACT_SCHEMAS,
    SCHEMA_VERSION,
    ArtifactKind,
    Beat,
    Character,
    ContinuityCategory,
    ContinuityFinding,
    ContinuitySeverity,
    CreativeBrief,
    Critique,
    CritiqueIssue,
    CritiqueSeverity,
    CritiqueVerdict,
    Location,
    MaturityMode,
    Relationship,
    RubricScore,
    ScenePlan,
    StoryBlueprint,
    StoryFormat,
    WorldRule,
    artifact_json_schema,
    validate_artifact_json,
)
from pydantic import ValidationError


def _brief() -> CreativeBrief:
    return CreativeBrief(
        original_premise="A new stroller waits outside an abandoned building.",
        interpretation="A grounded horror story about grief exploiting uncertainty.",
        assumptions=("The building is in a declining industrial town.",),
        story_format=StoryFormat.SHORT_PROSE,
        genres=("supernatural horror",),
        tone=("dread-filled", "intimate"),
        maturity=MaturityMode.MATURE_FICTION,
        intended_effect="Sustain dread before an emotionally costly revelation.",
        target_audience="Adult horror readers",
        target_word_count=3000,
        target_scene_count=3,
        target_significant_character_count=2,
        central_dramatic_question="Who left the stroller, and why does it remain untouched?",
        themes=("grief", "collective guilt"),
        required_elements=("The stroller must be new.",),
        forbidden_elements=("No dream ending.",),
        style_constraints=("Close third-person prose.",),
        authorized_ambiguities=("The town and protagonist names may be invented.",),
    )


def _characters() -> tuple[Character, Character]:
    return (
        Character(
            id="mara",
            name="Mara Vukovic",
            story_role="Protagonist",
            description="A municipal inspector who grew up beside the abandoned tower.",
            external_goal="Determine whether the site is safe.",
            internal_need="Admit her role in an old neighborhood lie.",
            motivation="Protect a child who keeps approaching the stroller.",
            stakes="Another family may repeat her loss.",
            primary_conflict="Her investigation threatens the town's shared story.",
            arc="She moves from guarded complicity to public truth-telling.",
            traits=("methodical", "protective"),
            contradictions=("She enforces rules while hiding a foundational violation.",),
            voice="Precise, dry, and clipped until her defenses fail.",
            secrets=("She saw the original accident.",),
            initial_knowledge=("The tower was never structurally completed.",),
        ),
        Character(
            id="nikola",
            name="Nikola Petrovic",
            story_role="Opposing force and former friend",
            description="The caretaker who unofficially watches the condemned property.",
            external_goal="Keep everyone out of the tower.",
            internal_need="Accept that silence no longer protects the dead.",
            motivation="Preserve the promise he made to Mara years ago.",
            stakes="Exposure will destroy his remaining family ties.",
            primary_conflict="He obstructs Mara while needing her help.",
            arc="He shifts from intimidation to a confession.",
            traits=("watchful", "superstitious"),
            contradictions=("He denies ghosts but performs rituals at the entrance.",),
            voice="Indirect and folkloric, with sudden blunt admissions.",
            secrets=("He bought the stroller as an offering.",),
            initial_knowledge=("The stroller appeared after his failed ritual.",),
        ),
    )


def _location() -> Location:
    return Location(
        id="tower_lot",
        name="The unfinished tower",
        description="A six-story concrete shell without windows.",
        atmosphere="Exposed, wind-scoured, and watched despite being deserted.",
        story_function="Concentrates the town's buried history in one visible place.",
        sensory_details=("wet concrete", "weeds rasping against plastic"),
        constraints=("No working electricity.",),
        associated_character_ids=("mara", "nikola"),
    )


def _beats() -> tuple[Beat, Beat, Beat]:
    return (
        Beat(
            id="arrival",
            sequence=1,
            title="The untouched stroller",
            summary="Mara finds that nobody will approach the new stroller.",
            purpose="Establish the mystery and the town's avoidance.",
            cause="A safety complaint brings Mara to the tower.",
            effect="She chooses to inspect the property after dark.",
            character_ids=("mara",),
            location_id="tower_lot",
        ),
        Beat(
            id="confrontation",
            sequence=2,
            title="Nikola intervenes",
            summary="Nikola blocks Mara and exposes details only a witness could know.",
            purpose="Turn the external mystery into a shared moral conflict.",
            cause="Mara crosses the condemned fence.",
            effect="She realizes Nikola placed the stroller.",
            character_ids=("mara", "nikola"),
            location_id="tower_lot",
            depends_on_beat_ids=("arrival",),
        ),
        Beat(
            id="confession",
            sequence=3,
            title="The public truth",
            summary="Mara and Nikola confess what happened before the tower was abandoned.",
            purpose="Resolve the central question through an irreversible choice.",
            cause="The stroller begins rolling toward the open stairwell.",
            effect="The haunting stops after the truth is recorded.",
            character_ids=("mara", "nikola"),
            location_id="tower_lot",
            depends_on_beat_ids=("confrontation",),
            pays_off_beat_ids=("arrival",),
        ),
    )


def _scene_plans() -> tuple[ScenePlan, ScenePlan, ScenePlan]:
    return (
        ScenePlan(
            id="scene_1",
            scene_number=1,
            title="Inspection",
            summary="Mara arrives and tests the neighborhood's fear.",
            purpose="Introduce the mystery.",
            point_of_view_character_id="mara",
            character_ids=("mara",),
            location_id="tower_lot",
            time_context="One autumn night",
            entry_state="Mara expects an ordinary dumping complaint.",
            goal="Document the stroller and inspect the fence.",
            conflict="Neighbors refuse to provide statements.",
            turning_point="The stroller's wheels are dry despite the rain.",
            outcome="Mara enters the lot.",
            exit_state="She suspects deliberate staging.",
            beat_ids=("arrival",),
            estimated_word_count=900,
            continuity_requirements=("The stroller remains pristine.",),
        ),
        ScenePlan(
            id="scene_2",
            scene_number=2,
            title="The caretaker",
            summary="Nikola intercepts Mara inside the fence.",
            purpose="Reveal the personal history behind the mystery.",
            point_of_view_character_id="mara",
            character_ids=("mara", "nikola"),
            location_id="tower_lot",
            time_context="Later that night",
            entry_state="Mara is alert and professionally detached.",
            goal="Reach the tower entrance.",
            conflict="Nikola threatens to report her trespass.",
            turning_point="He names the stroller's brand without seeing its label.",
            outcome="Mara forces him to admit he bought it.",
            exit_state="Their old pact is exposed.",
            beat_ids=("confrontation",),
            estimated_word_count=1000,
            continuity_requirements=("The stroller remains pristine.",),
        ),
        ScenePlan(
            id="scene_3",
            scene_number=3,
            title="What the tower kept",
            summary="The moving stroller forces both witnesses to confess.",
            purpose="Deliver the moral and supernatural resolution.",
            point_of_view_character_id="mara",
            character_ids=("mara", "nikola"),
            location_id="tower_lot",
            time_context="Before dawn",
            entry_state="Mara and Nikola blame each other.",
            goal="Stop the stroller before it reaches the stairwell.",
            conflict="Neither can touch it while preserving the lie.",
            turning_point="Mara records the truth on her inspection line.",
            outcome="Nikola completes the confession and the stroller stops.",
            exit_state="Dawn exposes the tower and their culpability.",
            beat_ids=("confession",),
            estimated_word_count=1100,
            required_elements=("End with the stroller still physically present.",),
            continuity_requirements=("The stroller remains pristine.",),
        ),
    )


def _blueprint() -> StoryBlueprint:
    return StoryBlueprint(
        creative_brief=_brief(),
        logline=(
            "An inspector must break a childhood pact when a pristine stroller appears "
            "outside the condemned tower where her neighborhood buried a death."
        ),
        thematic_thesis="Silence preserves guilt, not the people it claims to protect.",
        world_summary="A declining town treats an unfinished tower as both hazard and shrine.",
        characters=_characters(),
        relationships=(
            Relationship(
                id="mara_nikola",
                source_character_id="mara",
                target_character_id="nikola",
                label="Estranged childhood friends",
                dynamic="Mutual protection hardened into mutual surveillance.",
                history="They concealed a fatal accident at the tower as teenagers.",
                tension="Each believes the other may confess first.",
                arc="Their pact breaks and becomes shared accountability.",
            ),
        ),
        locations=(_location(),),
        world_rules=(
            WorldRule(
                id="truth_moves_stroller",
                statement="The stroller moves only when a witness repeats the old lie.",
                rationale="The haunting externalizes the witnesses' maintained fiction.",
                story_consequence="Each evasion brings it closer to the stairwell.",
                relevant_location_ids=("tower_lot",),
                relevant_character_ids=("mara", "nikola"),
            ),
        ),
        central_conflict="Mara must expose the pact that Nikola has organized his life to keep.",
        story_arc=(
            "Investigation becomes confrontation, then confession under supernatural pressure."
        ),
        beats=_beats(),
        scene_plans=_scene_plans(),
        proposed_ending=(
            "Their recorded confession stops the stroller but begins a public reckoning."
        ),
        voice_and_style_guide=(
            "Close third-person, concrete sensory detail, restrained supernaturalism."
        ),
        potential_risks=("The reveal could become overly expository.",),
        unresolved_decisions=("Whether the public believes the supernatural detail.",),
    )


def _replace_blueprint_field(blueprint: StoryBlueprint, key: str, value: Any) -> dict[str, Any]:
    content = blueprint.model_dump(mode="json")
    content[key] = value
    return content


def test_complete_story_blueprint_round_trips_as_json() -> None:
    blueprint = _blueprint()

    restored = StoryBlueprint.model_validate_json(blueprint.model_dump_json())

    assert restored == blueprint
    assert sum(scene.estimated_word_count for scene in restored.scene_plans) == 3000
    assert restored.schema_version == SCHEMA_VERSION


def test_artifact_models_are_deeply_immutable_and_reject_unknown_fields() -> None:
    brief = _brief()

    with pytest.raises(ValidationError, match="frozen"):
        brief.interpretation = "A different interpretation."
    with pytest.raises(TypeError):
        brief.themes[0] = "changed"  # type: ignore[index]
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        CreativeBrief.model_validate({**brief.model_dump(), "provider": "secret"})


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("target_word_count", 2499),
        ("target_word_count", 5001),
        ("target_scene_count", 2),
        ("target_scene_count", 9),
        ("target_significant_character_count", 1),
        ("target_significant_character_count", 6),
    ],
)
def test_creative_brief_enforces_v01_scope(field: str, value: int) -> None:
    content = _brief().model_dump()
    content[field] = value

    with pytest.raises(ValidationError):
        CreativeBrief.model_validate(content)


def test_local_artifact_invariants_reject_invalid_relationships_and_scenes() -> None:
    relationship = _blueprint().relationships[0].model_dump()
    relationship["target_character_id"] = "mara"
    with pytest.raises(ValidationError, match="characters must differ"):
        Relationship.model_validate(relationship)

    scene = _blueprint().scene_plans[0].model_dump()
    scene["point_of_view_character_id"] = "nikola"
    with pytest.raises(ValidationError, match="must appear"):
        ScenePlan.model_validate(scene)


def test_blueprint_rejects_dangling_references() -> None:
    blueprint = _blueprint()
    scenes = [scene.model_dump(mode="json") for scene in blueprint.scene_plans]
    scenes[0]["location_id"] = "unknown_place"

    with pytest.raises(ValidationError, match="unknown scene scene_1 location IDs"):
        StoryBlueprint.model_validate(_replace_blueprint_field(blueprint, "scene_plans", scenes))


def test_blueprint_rejects_duplicate_ids_and_unplanned_beats() -> None:
    blueprint = _blueprint()
    duplicate_characters = [character.model_dump(mode="json") for character in blueprint.characters]
    duplicate_characters[1]["id"] = "mara"
    with pytest.raises(ValidationError, match="duplicate character IDs"):
        StoryBlueprint.model_validate(
            _replace_blueprint_field(blueprint, "characters", duplicate_characters)
        )

    scenes = [scene.model_dump(mode="json") for scene in blueprint.scene_plans]
    scenes[2]["beat_ids"] = ["confrontation"]
    with pytest.raises(ValidationError, match="beats missing from scene plans"):
        StoryBlueprint.model_validate(_replace_blueprint_field(blueprint, "scene_plans", scenes))


def test_blueprint_requires_ordered_contiguous_scene_numbers() -> None:
    blueprint = _blueprint()
    scenes = [scene.model_dump(mode="json") for scene in blueprint.scene_plans]
    scenes[1]["scene_number"] = 3

    with pytest.raises(ValidationError, match="scene numbers must be ordered and contiguous"):
        StoryBlueprint.model_validate(_replace_blueprint_field(blueprint, "scene_plans", scenes))


def test_critique_cannot_pass_with_a_blocking_issue() -> None:
    content = {
        "target_artifact_kind": ArtifactKind.STORY_BLUEPRINT,
        "target_artifact_key": "story_blueprint",
        "target_artifact_version_id": uuid4(),
        "rubric_name": "Blueprint readiness",
        "rubric_version": "1",
        "summary": "The structure is strong but one required element is absent.",
        "strengths": ("Clear causal architecture.",),
        "issues": (
            CritiqueIssue(
                category="constraint adherence",
                severity=CritiqueSeverity.BLOCKING,
                description="The new stroller is not present in the ending.",
                evidence=("Scene 3 removes the stroller before the confession.",),
                recommendation="Keep the stroller physically present.",
            ),
        ),
        "scores": (
            RubricScore(
                dimension="Causal coherence and structure",
                score=4,
                rationale="Every scene changes the dramatic state.",
            ),
        ),
        "overall_score": 3.5,
        "verdict": CritiqueVerdict.PASS,
    }

    with pytest.raises(ValidationError, match="blocking issues cannot pass"):
        Critique.model_validate(content)

    content["verdict"] = CritiqueVerdict.REVISE
    assert Critique.model_validate(content).verdict is CritiqueVerdict.REVISE


def test_continuity_finding_aligns_severity_routing_and_resolution() -> None:
    content = {
        "id": "stroller_weather",
        "severity": ContinuitySeverity.BLOCKING,
        "category": ContinuityCategory.FACT,
        "summary": "The stroller changes from dry to rain-soaked without explanation.",
        "evidence": ("Scene 1 establishes dry wheels.", "Scene 2 calls the fabric soaked."),
        "related_scene_ids": ("scene_1", "scene_2"),
        "blocks_approval": False,
    }
    with pytest.raises(ValidationError, match="must block approval"):
        ContinuityFinding.model_validate(content)

    content["blocks_approval"] = True
    with pytest.raises(ValidationError, match="requires a resolution"):
        ContinuityFinding.model_validate(content)

    content["recommended_resolution"] = "Preserve the established dryness in Scene 2."
    assert ContinuityFinding.model_validate(content).blocks_approval is True


def test_registry_covers_catalog_and_validates_raw_model_json() -> None:
    assert set(ARTIFACT_SCHEMAS) == set(ArtifactKind)
    for kind in ArtifactKind:
        schema = artifact_json_schema(kind)
        assert schema["type"] == "object"
        assert schema["additionalProperties"] is False

    brief = _brief()
    validated = validate_artifact_json(ArtifactKind.CREATIVE_BRIEF, brief.model_dump_json())
    assert isinstance(validated, CreativeBrief)

    with pytest.raises(ValidationError, match="target_word_count"):
        validate_artifact_json(
            ArtifactKind.CREATIVE_BRIEF,
            brief.model_dump_json().replace('"target_word_count":3000', '"target_word_count":1'),
        )
