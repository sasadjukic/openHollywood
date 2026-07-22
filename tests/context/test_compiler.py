"""Tests for deterministic, token-bounded context compilation."""

from __future__ import annotations

import hashlib
import json
from dataclasses import replace
from decimal import Decimal
from uuid import UUID

import pytest
from open_hollywood_engine.artifacts import (
    ArtifactKind,
    Character,
    CreativeBrief,
    Location,
    MaturityMode,
    StoryFormat,
)
from open_hollywood_engine.context import (
    AgentDependencyManifest,
    ArtifactDependencyRule,
    ContextBudgetExceededError,
    ContextDependencyError,
    ContextPacketCompiler,
    ContextPacketRequest,
    ContextTokenBudget,
    DependencyManifestRegistry,
    NearbySummary,
    StoryBibleSection,
    StoryBibleSnapshot,
    UnknownSpecialistRoleError,
    Utf8ByteTokenCounter,
    VersionedArtifact,
)
from open_hollywood_engine.models import ModelCallBudget


class CharacterTokenCounter:
    """Exact character counter used to make budget boundaries transparent in tests."""

    identifier = "characters_v1"

    def count(self, text: str) -> int:
        return len(text)


def _brief() -> CreativeBrief:
    return CreativeBrief(
        original_premise="A stroller waits outside an abandoned building.",
        interpretation="A horror story about a town's buried guilt.",
        assumptions=("The town is fictional.",),
        story_format=StoryFormat.SHORT_PROSE,
        genres=("horror",),
        tone=("restrained",),
        maturity=MaturityMode.STANDARD_FICTION,
        intended_effect="Sustain dread and end with accountability.",
        target_audience="Adult readers",
        target_word_count=3000,
        target_scene_count=3,
        target_significant_character_count=2,
        central_dramatic_question="Why is the stroller untouched?",
        themes=("guilt",),
        required_elements=("The stroller is new.",),
    )


def _location(location_id: str, name: str) -> Location:
    return Location(
        id=location_id,
        name=name,
        description=f"The story-relevant place called {name}.",
        atmosphere="Uneasy and exposed.",
        story_function="Concentrates pressure on the characters.",
        sensory_details=("wet concrete",),
    )


def _character() -> Character:
    return Character(
        id="mara",
        name="Mara",
        story_role="Protagonist",
        description="A municipal inspector with a buried connection to the site.",
        external_goal="Inspect the abandoned building.",
        internal_need="Tell the truth.",
        motivation="Keep another family safe.",
        stakes="The town may repeat an old tragedy.",
        primary_conflict="Her duty conflicts with her secret.",
        arc="She moves from concealment to confession.",
        traits=("methodical",),
        contradictions=("She enforces rules while hiding a violation.",),
        voice="Precise and guarded.",
    )


def _artifact(
    kind: ArtifactKind,
    key: str,
    version_number: int,
    content: CreativeBrief | Location | Character,
) -> VersionedArtifact:
    return VersionedArtifact(
        kind=kind,
        artifact_key=key,
        version_id=UUID(int=version_number),
        content=content,
    )


def _manifest() -> AgentDependencyManifest:
    return AgentDependencyManifest(
        specialist_role="character_architect",
        manifest_version="character-context-v1",
        output_artifact_kind=ArtifactKind.CHARACTER,
        artifact_dependencies=(
            ArtifactDependencyRule(
                kind=ArtifactKind.CREATIVE_BRIEF,
                required=True,
                minimum_count=1,
                maximum_count=1,
            ),
            ArtifactDependencyRule(
                kind=ArtifactKind.LOCATION,
                required=False,
                minimum_count=0,
                maximum_count=2,
            ),
        ),
        story_bible_sections=("characters", "world_rules"),
        minimum_nearby_summaries=0,
        maximum_nearby_summaries=2,
    )


def _compiler() -> ContextPacketCompiler:
    return ContextPacketCompiler(
        DependencyManifestRegistry((_manifest(),)),
        CharacterTokenCounter(),
    )


def _story_bible() -> StoryBibleSnapshot:
    return StoryBibleSnapshot(
        source_artifact_version_id=UUID(int=10),
        sections=(
            StoryBibleSection(name="world_rules", content="The haunting reacts to lies."),
            StoryBibleSection(name="unused", content="This must not enter the packet."),
            StoryBibleSection(name="characters", content="Mara knows the building's history."),
        ),
    )


def _summaries() -> tuple[NearbySummary, ...]:
    return (
        NearbySummary(UUID(int=21), "scene_1", 1, "Mara arrives at the lot."),
        NearbySummary(UUID(int=23), "scene_3", 3, "Mara crosses the fence."),
        NearbySummary(UUID(int=22), "scene_2", 2, "The neighbors refuse to speak."),
    )


def _request(*, include_optional: bool = True) -> ContextPacketRequest:
    brief = _artifact(ArtifactKind.CREATIVE_BRIEF, "creative_brief", 1, _brief())
    artifacts: tuple[VersionedArtifact, ...] = (brief,)
    summaries: tuple[NearbySummary, ...] = ()
    if include_optional:
        artifacts = (
            _artifact(ArtifactKind.LOCATION, "tower", 3, _location("tower", "Tower")),
            brief,
            _artifact(ArtifactKind.LOCATION, "alley", 2, _location("alley", "Alley")),
        )
        summaries = _summaries()
    return ContextPacketRequest(
        specialist_role="character_architect",
        assignment="Create a psychologically specific protagonist.",
        evaluation_rubric="Reward causal motives, contradictions, and a usable character arc.",
        budget=ContextTokenBudget(max_input_tokens=100_000, reserved_tokens=500),
        user_constraints=("Do not add another approval checkpoint.",),
        artifacts=artifacts,
        story_bible=_story_bible(),
        nearby_summaries=summaries,
    )


def _payload(content: str) -> dict[str, object]:
    _, serialized = content.split("\n", maxsplit=1)
    parsed = json.loads(serialized)
    assert isinstance(parsed, dict)
    return parsed


def test_compiler_selects_and_orders_only_manifest_declared_context() -> None:
    packet = _compiler().compile(_request())
    payload = _payload(packet.content)

    dependencies = payload["direct_dependencies"]
    assert isinstance(dependencies, list)
    assert [item["artifact_key"] for item in dependencies] == [
        "creative_brief",
        "alley",
        "tower",
    ]
    story_bible = payload["story_bible"]
    assert isinstance(story_bible, dict)
    assert story_bible["source_artifact_version_id"] == str(UUID(int=10))
    sections = story_bible["sections"]
    assert isinstance(sections, list)
    assert [item["name"] for item in sections] == ["characters", "world_rules"]
    summaries = payload["nearby_summaries"]
    assert isinstance(summaries, list)
    assert [item["sequence"] for item in summaries] == [2, 3]
    assert payload["evaluation_rubric"] == (
        "Reward causal motives, contradictions, and a usable character arc."
    )

    output_contract = payload["output_contract"]
    assert isinstance(output_contract, dict)
    assert output_contract["artifact_kind"] == "character"
    assert isinstance(output_contract["json_schema"], dict)
    assert packet.input_artifact_version_ids == (
        UUID(int=1),
        UUID(int=2),
        UUID(int=3),
        UUID(int=10),
        UUID(int=22),
        UUID(int=23),
    )
    assert packet.omitted_context[0].identifier == str(UUID(int=21))
    assert packet.omitted_context[0].reason == "manifest_limit"


def test_compilation_is_reproducible_and_builds_exact_invocation_lineage() -> None:
    compiler = _compiler()
    first = compiler.compile(_request())
    second = compiler.compile(_request())

    assert first == second
    assert first.content_sha256 == hashlib.sha256(first.content.encode()).hexdigest()
    assert first.estimated_tokens == len(first.content)
    assert first.remaining_tokens == first.budget.packet_tokens - len(first.content)
    invocation = first.invocation_context(prompt_template_version="character-v1")
    assert invocation.specialist_role == "character_architect"
    assert invocation.input_artifact_version_ids == first.input_artifact_version_ids


def test_budget_omits_only_optional_context_and_records_each_decision() -> None:
    compiler = _compiler()
    mandatory = compiler.compile(_request(include_optional=False))
    exact_budget = ContextTokenBudget(
        max_input_tokens=mandatory.estimated_tokens + 50,
        reserved_tokens=50,
    )

    packet = compiler.compile(replace(_request(), budget=exact_budget))
    payload = _payload(packet.content)

    dependencies = payload["direct_dependencies"]
    summaries = payload["nearby_summaries"]
    assert isinstance(dependencies, list)
    assert isinstance(summaries, list)
    assert [item["artifact_key"] for item in dependencies] == ["creative_brief"]
    assert summaries == []
    assert {(item.category, item.reason) for item in packet.omitted_context} == {
        ("artifact", "token_budget"),
        ("nearby_summary", "manifest_limit"),
        ("nearby_summary", "token_budget"),
    }
    assert len(packet.omitted_context) == 5
    assert packet.estimated_tokens == exact_budget.packet_tokens


def test_budget_fails_closed_when_mandatory_context_does_not_fit() -> None:
    compiler = _compiler()
    mandatory = compiler.compile(_request(include_optional=False))
    request = replace(
        _request(include_optional=False),
        budget=ContextTokenBudget(
            max_input_tokens=mandatory.estimated_tokens,
            reserved_tokens=1,
        ),
    )

    with pytest.raises(ContextBudgetExceededError) as captured:
        compiler.compile(request)

    assert captured.value.required_tokens == mandatory.estimated_tokens
    assert captured.value.available_tokens == mandatory.estimated_tokens - 1


def test_compiler_rejects_missing_unexpected_and_ambiguous_dependencies() -> None:
    compiler = _compiler()
    request = _request(include_optional=False)

    with pytest.raises(ContextDependencyError, match="requires at least 1"):
        compiler.compile(replace(request, artifacts=()))

    unexpected = _artifact(ArtifactKind.CHARACTER, "mara", 40, _character())
    with pytest.raises(ContextDependencyError, match="undeclared artifact"):
        compiler.compile(replace(request, artifacts=(*request.artifacts, unexpected)))

    duplicate_key = replace(request.artifacts[0], version_id=UUID(int=50))
    with pytest.raises(ContextDependencyError, match="one version per artifact_key"):
        compiler.compile(replace(request, artifacts=(*request.artifacts, duplicate_key)))


def test_compiler_rejects_missing_story_bible_sections_and_unknown_roles() -> None:
    compiler = _compiler()
    request = _request(include_optional=False)
    incomplete_bible = StoryBibleSnapshot(
        source_artifact_version_id=UUID(int=60),
        sections=(StoryBibleSection("characters", "Mara is the protagonist."),),
    )

    with pytest.raises(ContextDependencyError, match="missing story-bible sections"):
        compiler.compile(replace(request, story_bible=incomplete_bible))
    with pytest.raises(UnknownSpecialistRoleError, match="not_registered"):
        compiler.compile(replace(request, specialist_role="not_registered"))


def test_manifest_and_registry_reject_ambiguous_configuration() -> None:
    rule = ArtifactDependencyRule(ArtifactKind.CREATIVE_BRIEF, True, 1, 1)
    with pytest.raises(ValueError, match="artifact dependency kinds must be unique"):
        replace(_manifest(), artifact_dependencies=(rule, rule))
    with pytest.raises(ValueError, match="duplicate dependency manifest"):
        DependencyManifestRegistry((_manifest(), _manifest()))
    with pytest.raises(ValueError, match="budget-optional"):
        ArtifactDependencyRule(ArtifactKind.LOCATION, False, 1)


def test_versioned_artifact_rejects_kind_content_mismatch() -> None:
    with pytest.raises(ValueError, match="content must be Character"):
        _artifact(ArtifactKind.CHARACTER, "mara", 1, _brief())


def test_token_budget_can_derive_from_model_budget_and_reserve_framing() -> None:
    model_budget = ModelCallBudget(
        max_input_tokens=4096,
        max_output_tokens=1024,
        max_cost_usd=Decimal("0"),
    )

    budget = ContextTokenBudget.from_model_budget(model_budget, reserved_tokens=96)

    assert budget.max_input_tokens == 4096
    assert budget.packet_tokens == 4000


def test_utf8_fallback_is_deterministic_and_conservative_for_unicode() -> None:
    counter = Utf8ByteTokenCounter()

    assert counter.identifier == "utf8_bytes_v1"
    assert counter.count("story") == 5
    assert counter.count("priča") == len("priča".encode())
    assert counter.count("priča") > len("priča")
