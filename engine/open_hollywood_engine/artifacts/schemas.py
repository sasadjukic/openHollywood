"""Provider-neutral schemas for structured creative artifacts."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from enum import StrEnum
from types import MappingProxyType
from typing import Annotated, Any, ClassVar, Protocol, Self
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StrictBool,
    StrictFloat,
    StrictInt,
    StringConstraints,
    model_validator,
)

SCHEMA_VERSION = "1"

NonEmptyText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
ReferenceId = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        max_length=100,
        pattern=r"^[a-z][a-z0-9_-]*$",
    ),
]
ArtifactKey = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        max_length=150,
        pattern=r"^[a-z][a-z0-9_-]*$",
    ),
]


class ArtifactKind(StrEnum):
    """Stable persisted type names for the initial artifact catalog."""

    CREATIVE_BRIEF = "creative_brief"
    PREMISE = "premise"
    CHARACTER = "character"
    RELATIONSHIP = "relationship"
    LOCATION = "location"
    WORLD_RULE = "world_rule"
    BEAT = "beat"
    SCENE_PLAN = "scene_plan"
    CRITIQUE = "critique"
    CONTINUITY_FINDING = "continuity_finding"
    CONTINUITY_REPORT = "continuity_report"
    STORY_BLUEPRINT = "story_blueprint"
    STORY_BIBLE = "story_bible"
    STORY_BIBLE_UPDATE = "story_bible_update"
    DIALOGUE_BRIEFING = "dialogue_briefing"
    DIALOGUE_TURN = "dialogue_turn"
    DIALOGUE_EVALUATION = "dialogue_evaluation"
    SCENE_DRAFT = "scene_draft"


class StoryFormat(StrEnum):
    """Story formats currently accepted by the product contract."""

    SHORT_PROSE = "short_prose"


class MaturityMode(StrEnum):
    """Open Hollywood fiction-content modes, independent of provider policy."""

    STANDARD_FICTION = "standard_fiction"
    MATURE_FICTION = "mature_fiction"


class CritiqueSeverity(StrEnum):
    """Impact of a critique issue on the target artifact."""

    NOTE = "note"
    MINOR = "minor"
    MAJOR = "major"
    BLOCKING = "blocking"


class CritiqueVerdict(StrEnum):
    """Recommended disposition after critique."""

    PASS = "pass"
    REVISE = "revise"
    REJECT = "reject"


class ContinuitySeverity(StrEnum):
    """Impact of a continuity problem on story truth."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    BLOCKING = "blocking"


class ContinuityCategory(StrEnum):
    """Deterministic categories used to route continuity findings."""

    CONSTRAINT = "constraint"
    FACT = "fact"
    TIMELINE = "timeline"
    CHARACTER = "character"
    CHARACTER_KNOWLEDGE = "character_knowledge"
    RELATIONSHIP = "relationship"
    LOCATION = "location"
    WORLD_RULE = "world_rule"
    SETUP_PAYOFF = "setup_payoff"


class StoryThreadKind(StrEnum):
    """Canonical unresolved-thread types maintained during production."""

    MYSTERY = "mystery"
    PROMISE = "promise"


class StoryThreadStatus(StrEnum):
    """Allowed lifecycle states for mysteries and setup/payoff promises."""

    OPEN = "open"
    RESOLVED = "resolved"


class EmotionalArcStage(StrEnum):
    """Bounded dramatic progression tracked by the dialogue director."""

    OPENING = "opening"
    TENSION = "tension"
    CLIMAX = "climax"
    RESOLUTION = "resolution"


class ArtifactSchema(BaseModel):
    """Immutable base for artifact content stored in an ArtifactVersion envelope."""

    schema_version: ClassVar[str] = SCHEMA_VERSION
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
        validate_default=True,
    )


class CreativeBrief(ArtifactSchema):
    """Authoritative interpretation of user intent for the v0.1 story run."""

    original_premise: NonEmptyText
    interpretation: NonEmptyText
    assumptions: tuple[NonEmptyText, ...] = ()
    story_format: StoryFormat
    genres: Annotated[tuple[NonEmptyText, ...], Field(min_length=1)]
    tone: Annotated[tuple[NonEmptyText, ...], Field(min_length=1)]
    maturity: MaturityMode
    intended_effect: NonEmptyText
    target_audience: NonEmptyText
    target_word_count: Annotated[StrictInt, Field(ge=2500, le=5000)]
    target_scene_count: Annotated[StrictInt, Field(ge=3, le=8)]
    target_significant_character_count: Annotated[StrictInt, Field(ge=2, le=5)]
    central_dramatic_question: NonEmptyText
    themes: Annotated[tuple[NonEmptyText, ...], Field(min_length=1)]
    required_elements: tuple[NonEmptyText, ...] = ()
    forbidden_elements: tuple[NonEmptyText, ...] = ()
    style_constraints: tuple[NonEmptyText, ...] = ()
    authorized_ambiguities: tuple[NonEmptyText, ...] = ()


class Premise(ArtifactSchema):
    """Story proposition and thematic direction developed from the creative brief."""

    logline: NonEmptyText
    thematic_thesis: NonEmptyText
    central_conflict: NonEmptyText
    story_arc: NonEmptyText
    proposed_ending: NonEmptyText
    voice_and_style_guide: NonEmptyText
    potential_risks: tuple[NonEmptyText, ...] = ()
    unresolved_decisions: tuple[NonEmptyText, ...] = ()


class Character(ArtifactSchema):
    """A significant character dossier used as canonical story state."""

    id: ReferenceId
    name: NonEmptyText
    story_role: NonEmptyText
    description: NonEmptyText
    external_goal: NonEmptyText
    internal_need: NonEmptyText
    motivation: NonEmptyText
    stakes: NonEmptyText
    primary_conflict: NonEmptyText
    arc: NonEmptyText
    traits: Annotated[tuple[NonEmptyText, ...], Field(min_length=1)]
    contradictions: Annotated[tuple[NonEmptyText, ...], Field(min_length=1)]
    voice: NonEmptyText
    secrets: tuple[NonEmptyText, ...] = ()
    initial_knowledge: tuple[NonEmptyText, ...] = ()


class Relationship(ArtifactSchema):
    """A directed or mutual relationship between two canonical characters."""

    id: ReferenceId
    source_character_id: ReferenceId
    target_character_id: ReferenceId
    label: NonEmptyText
    dynamic: NonEmptyText
    history: NonEmptyText
    tension: NonEmptyText
    arc: NonEmptyText
    is_mutual: StrictBool = True

    @model_validator(mode="after")
    def characters_must_differ(self) -> Self:
        """Reject self-relationships, which cannot express an inter-character link."""
        if self.source_character_id == self.target_character_id:
            raise ValueError("relationship characters must differ")
        return self


class Location(ArtifactSchema):
    """A story-relevant place and its dramatic constraints."""

    id: ReferenceId
    name: NonEmptyText
    description: NonEmptyText
    atmosphere: NonEmptyText
    story_function: NonEmptyText
    sensory_details: Annotated[tuple[NonEmptyText, ...], Field(min_length=1)]
    constraints: tuple[NonEmptyText, ...] = ()
    associated_character_ids: tuple[ReferenceId, ...] = ()


class WorldRule(ArtifactSchema):
    """An invariant governing the physical, social, or narrative world."""

    id: ReferenceId
    statement: NonEmptyText
    rationale: NonEmptyText
    story_consequence: NonEmptyText
    exceptions: tuple[NonEmptyText, ...] = ()
    relevant_location_ids: tuple[ReferenceId, ...] = ()
    relevant_character_ids: tuple[ReferenceId, ...] = ()


class Beat(ArtifactSchema):
    """An ordered causal unit in the story architecture."""

    id: ReferenceId
    sequence: Annotated[StrictInt, Field(ge=1)]
    title: NonEmptyText
    summary: NonEmptyText
    purpose: NonEmptyText
    cause: NonEmptyText
    effect: NonEmptyText
    character_ids: Annotated[tuple[ReferenceId, ...], Field(min_length=1)]
    location_id: ReferenceId | None = None
    depends_on_beat_ids: tuple[ReferenceId, ...] = ()
    pays_off_beat_ids: tuple[ReferenceId, ...] = ()

    @model_validator(mode="after")
    def references_must_not_include_self(self) -> Self:
        """Keep the causal graph free of direct self-references."""
        if self.id in self.depends_on_beat_ids or self.id in self.pays_off_beat_ids:
            raise ValueError("a beat cannot depend on or pay off itself")
        return self


class ScenePlan(ArtifactSchema):
    """A bounded writing assignment with explicit entry and exit state."""

    id: ReferenceId
    scene_number: Annotated[StrictInt, Field(ge=1)]
    title: NonEmptyText
    summary: NonEmptyText
    purpose: NonEmptyText
    point_of_view_character_id: ReferenceId | None = None
    character_ids: Annotated[tuple[ReferenceId, ...], Field(min_length=1)]
    location_id: ReferenceId
    time_context: NonEmptyText
    entry_state: NonEmptyText
    goal: NonEmptyText
    conflict: NonEmptyText
    turning_point: NonEmptyText
    outcome: NonEmptyText
    exit_state: NonEmptyText
    beat_ids: Annotated[tuple[ReferenceId, ...], Field(min_length=1)]
    estimated_word_count: Annotated[StrictInt, Field(ge=1)]
    required_elements: tuple[NonEmptyText, ...] = ()
    continuity_requirements: tuple[NonEmptyText, ...] = ()

    @model_validator(mode="after")
    def point_of_view_character_must_appear(self) -> Self:
        """Ensure a declared point-of-view character participates in the scene."""
        if (
            self.point_of_view_character_id is not None
            and self.point_of_view_character_id not in self.character_ids
        ):
            raise ValueError("point-of-view character must appear in character_ids")
        return self


class RubricScore(ArtifactSchema):
    """One justified 1-to-5 rubric score."""

    dimension: NonEmptyText
    score: Annotated[StrictInt, Field(ge=1, le=5)]
    rationale: NonEmptyText


class CritiqueIssue(ArtifactSchema):
    """One actionable weakness discovered by a critic."""

    category: NonEmptyText
    severity: CritiqueSeverity
    description: NonEmptyText
    evidence: Annotated[tuple[NonEmptyText, ...], Field(min_length=1)]
    recommendation: NonEmptyText


class Critique(ArtifactSchema):
    """Structured evaluation of one exact artifact version."""

    target_artifact_kind: ArtifactKind
    target_artifact_key: ArtifactKey
    target_artifact_version_id: UUID
    rubric_name: NonEmptyText
    rubric_version: NonEmptyText
    summary: NonEmptyText
    strengths: Annotated[tuple[NonEmptyText, ...], Field(min_length=1)]
    issues: tuple[CritiqueIssue, ...] = ()
    scores: Annotated[tuple[RubricScore, ...], Field(min_length=1)]
    overall_score: Annotated[StrictFloat, Field(ge=1, le=5)]
    verdict: CritiqueVerdict

    @model_validator(mode="after")
    def verdict_must_match_blocking_issues(self) -> Self:
        """Prevent a passing verdict when the critic reports a blocking issue."""
        if self.verdict is CritiqueVerdict.PASS and any(
            issue.severity is CritiqueSeverity.BLOCKING for issue in self.issues
        ):
            raise ValueError("a critique with blocking issues cannot pass")
        return self


class ContinuityFinding(ArtifactSchema):
    """One traceable contradiction, risk, or confirmation of story continuity."""

    id: ReferenceId
    severity: ContinuitySeverity
    category: ContinuityCategory
    summary: NonEmptyText
    evidence: Annotated[tuple[NonEmptyText, ...], Field(min_length=1)]
    related_character_ids: tuple[ReferenceId, ...] = ()
    related_location_ids: tuple[ReferenceId, ...] = ()
    related_beat_ids: tuple[ReferenceId, ...] = ()
    related_scene_ids: tuple[ReferenceId, ...] = ()
    recommended_resolution: NonEmptyText | None = None
    blocks_approval: StrictBool = False

    @model_validator(mode="after")
    def blocking_state_must_be_consistent(self) -> Self:
        """Keep the routing flag aligned with severity and remediation details."""
        if self.severity is ContinuitySeverity.BLOCKING and not self.blocks_approval:
            raise ValueError("a blocking finding must block approval")
        if self.blocks_approval and self.recommended_resolution is None:
            raise ValueError("a finding that blocks approval requires a resolution")
        return self


class ContinuityReport(ArtifactSchema):
    """Continuity gate for one exact candidate scene against one exact bible."""

    story_bible_version_id: UUID
    scene_version_id: UUID
    scene_plan_version_id: UUID
    scene_id: ReferenceId
    scene_number: Annotated[StrictInt, Field(ge=1)]
    checked_categories: Annotated[tuple[ContinuityCategory, ...], Field(min_length=1)]
    findings: tuple[ContinuityFinding, ...] = ()

    @model_validator(mode="after")
    def validate_coverage_and_findings(self) -> Self:
        """Require complete category coverage and findings tied to this scene."""
        if self.checked_categories != tuple(ContinuityCategory):
            raise ValueError("continuity report must check every category in canonical order")
        finding_ids = [finding.id for finding in self.findings]
        if len(set(finding_ids)) != len(finding_ids):
            raise ValueError("continuity finding IDs must be unique")
        if any(self.scene_id not in finding.related_scene_ids for finding in self.findings):
            raise ValueError("every continuity finding must reference the candidate scene")
        return self

    @property
    def has_blocking_findings(self) -> bool:
        """Return the deterministic acceptance disposition for this report."""
        return any(
            finding.blocks_approval
            or finding.severity in {ContinuitySeverity.ERROR, ContinuitySeverity.BLOCKING}
            for finding in self.findings
        )


class StoryBibleScene(ArtifactSchema):
    """One canonical accepted scene and its immutable artifact version."""

    scene_id: ReferenceId
    scene_number: Annotated[StrictInt, Field(ge=1)]
    artifact_version_id: UUID


class StoryBibleTimelineEvent(ArtifactSchema):
    """One ordered event established by an accepted scene."""

    id: ReferenceId
    sequence: Annotated[StrictInt, Field(ge=1)]
    scene_id: ReferenceId
    time_context: NonEmptyText
    summary: NonEmptyText
    character_ids: tuple[ReferenceId, ...] = ()
    location_id: ReferenceId | None = None


class StoryBibleFact(ArtifactSchema):
    """One immutable fact established by an accepted scene."""

    id: ReferenceId
    statement: NonEmptyText
    established_scene_id: ReferenceId
    character_ids: tuple[ReferenceId, ...] = ()
    location_ids: tuple[ReferenceId, ...] = ()


class StoryBibleCharacterState(ArtifactSchema):
    """Latest canonical state and knowledge for one blueprint character."""

    character_id: ReferenceId
    current_location_id: ReferenceId | None = None
    physical_state: NonEmptyText
    emotional_state: NonEmptyText
    current_goal: NonEmptyText
    knowledge_fact_ids: tuple[ReferenceId, ...] = ()
    last_updated_scene_id: ReferenceId


class StoryBibleRelationshipState(ArtifactSchema):
    """Latest canonical dynamic for one blueprint relationship."""

    relationship_id: ReferenceId
    state: NonEmptyText
    last_updated_scene_id: ReferenceId


class StoryBibleLocationState(ArtifactSchema):
    """Latest canonical condition of one blueprint location."""

    location_id: ReferenceId
    state: NonEmptyText
    last_updated_scene_id: ReferenceId


class StoryBibleThread(ArtifactSchema):
    """One open mystery or setup/payoff promise with monotonic resolution."""

    id: ReferenceId
    kind: StoryThreadKind
    statement: NonEmptyText
    introduced_scene_id: ReferenceId
    status: StoryThreadStatus
    resolved_scene_id: ReferenceId | None = None
    resolution: NonEmptyText | None = None

    @model_validator(mode="after")
    def resolution_must_match_status(self) -> Self:
        """Keep open and resolved thread states unambiguous."""
        if self.status is StoryThreadStatus.OPEN and (
            self.resolved_scene_id is not None or self.resolution is not None
        ):
            raise ValueError("an open story thread cannot have resolution fields")
        if self.status is StoryThreadStatus.RESOLVED and (
            self.resolved_scene_id is None or self.resolution is None
        ):
            raise ValueError("a resolved story thread requires scene and resolution")
        return self


class StoryBible(ArtifactSchema):
    """Full canonical story state after zero or more accepted scenes."""

    source_blueprint_version_id: UUID
    character_ids: Annotated[tuple[ReferenceId, ...], Field(min_length=1)]
    relationship_ids: tuple[ReferenceId, ...] = ()
    location_ids: tuple[ReferenceId, ...] = ()
    world_rule_ids: tuple[ReferenceId, ...] = ()
    accepted_scenes: tuple[StoryBibleScene, ...] = ()
    timeline: tuple[StoryBibleTimelineEvent, ...] = ()
    established_facts: tuple[StoryBibleFact, ...] = ()
    character_states: tuple[StoryBibleCharacterState, ...] = ()
    relationship_states: tuple[StoryBibleRelationshipState, ...] = ()
    location_states: tuple[StoryBibleLocationState, ...] = ()
    threads: tuple[StoryBibleThread, ...] = ()
    prohibited_contradictions: tuple[NonEmptyText, ...] = ()

    @model_validator(mode="after")
    def validate_canonical_state(self) -> Self:
        """Reject duplicate, dangling, or out-of-order canonical story state."""
        character_ids = _unique_text(self.character_ids, "story-bible character IDs")
        relationship_ids = _unique_text(
            self.relationship_ids,
            "story-bible relationship IDs",
        )
        location_ids = _unique_text(self.location_ids, "story-bible location IDs")
        _unique_text(self.world_rule_ids, "story-bible world-rule IDs")
        _unique_key(
            (scene.scene_id for scene in self.accepted_scenes),
            "accepted scene IDs",
        )
        scene_ids = {scene.scene_id for scene in self.accepted_scenes}
        scene_versions = [scene.artifact_version_id for scene in self.accepted_scenes]
        if len(set(scene_versions)) != len(scene_versions):
            raise ValueError("accepted scene artifact versions must be unique")
        _require_contiguous(
            (scene.scene_number for scene in self.accepted_scenes),
            "accepted scene number",
        )

        _unique_ids(self.timeline, "timeline event")
        _require_contiguous((event.sequence for event in self.timeline), "timeline event sequence")
        _unique_ids(self.established_facts, "established fact")
        fact_ids = {fact.id for fact in self.established_facts}
        _unique_key(
            (state.character_id for state in self.character_states),
            "character state IDs",
        )
        _unique_key(
            (state.relationship_id for state in self.relationship_states),
            "relationship state IDs",
        )
        _unique_key(
            (state.location_id for state in self.location_states),
            "location state IDs",
        )
        _unique_ids(self.threads, "story thread")
        _unique_text(
            self.prohibited_contradictions,
            "prohibited contradictions",
        )

        for event in self.timeline:
            _require_known((event.scene_id,), scene_ids, f"timeline event {event.id} scene")
            _require_known(
                event.character_ids,
                character_ids,
                f"timeline event {event.id} character",
            )
            if event.location_id is not None:
                _require_known(
                    (event.location_id,),
                    location_ids,
                    f"timeline event {event.id} location",
                )
        for fact in self.established_facts:
            _require_known(
                (fact.established_scene_id,),
                scene_ids,
                f"fact {fact.id} scene",
            )
            _require_known(fact.character_ids, character_ids, f"fact {fact.id} character")
            _require_known(fact.location_ids, location_ids, f"fact {fact.id} location")
        for character_state in self.character_states:
            _require_known(
                (character_state.character_id,),
                character_ids,
                "character state character",
            )
            _require_known(
                (character_state.last_updated_scene_id,),
                scene_ids,
                f"character state {character_state.character_id} scene",
            )
            _require_known(
                character_state.knowledge_fact_ids,
                fact_ids,
                f"character state {character_state.character_id} fact",
            )
            if character_state.current_location_id is not None:
                _require_known(
                    (character_state.current_location_id,),
                    location_ids,
                    f"character state {character_state.character_id} location",
                )
        for relationship_state in self.relationship_states:
            _require_known(
                (relationship_state.relationship_id,),
                relationship_ids,
                "relationship state relationship",
            )
            _require_known(
                (relationship_state.last_updated_scene_id,),
                scene_ids,
                f"relationship state {relationship_state.relationship_id} scene",
            )
        for location_state in self.location_states:
            _require_known(
                (location_state.location_id,),
                location_ids,
                "location state location",
            )
            _require_known(
                (location_state.last_updated_scene_id,),
                scene_ids,
                f"location state {location_state.location_id} scene",
            )
        for thread in self.threads:
            _require_known(
                (thread.introduced_scene_id,),
                scene_ids,
                f"story thread {thread.id} introduction",
            )
            if thread.resolved_scene_id is not None:
                _require_known(
                    (thread.resolved_scene_id,),
                    scene_ids,
                    f"story thread {thread.id} resolution",
                )
        return self


class StoryBibleUpdate(ArtifactSchema):
    """Typed delta deterministically reduced into a new StoryBible snapshot."""

    source_story_bible_version_id: UUID
    continuity_report_version_id: UUID
    accepted_scene: StoryBibleScene
    timeline_events: Annotated[tuple[StoryBibleTimelineEvent, ...], Field(min_length=1)]
    established_facts: tuple[StoryBibleFact, ...] = ()
    character_states: tuple[StoryBibleCharacterState, ...] = ()
    relationship_states: tuple[StoryBibleRelationshipState, ...] = ()
    location_states: tuple[StoryBibleLocationState, ...] = ()
    thread_changes: tuple[StoryBibleThread, ...] = ()
    prohibited_contradictions: tuple[NonEmptyText, ...] = ()

    @model_validator(mode="after")
    def updates_must_be_tied_to_accepted_scene(self) -> Self:
        """Ensure all newly established state is sourced to this scene."""
        scene_id = self.accepted_scene.scene_id
        if any(event.scene_id != scene_id for event in self.timeline_events):
            raise ValueError("new timeline events must originate in the accepted scene")
        if any(fact.established_scene_id != scene_id for fact in self.established_facts):
            raise ValueError("new facts must originate in the accepted scene")
        entity_scene_ids = (
            *(state.last_updated_scene_id for state in self.character_states),
            *(state.last_updated_scene_id for state in self.relationship_states),
            *(state.last_updated_scene_id for state in self.location_states),
        )
        if any(last_updated_scene_id != scene_id for last_updated_scene_id in entity_scene_ids):
            raise ValueError("entity-state updates must originate in the accepted scene")
        if any(
            thread.resolved_scene_id is not None and thread.resolved_scene_id != scene_id
            for thread in self.thread_changes
        ):
            raise ValueError("thread resolutions must originate in the accepted scene")
        return self


class DialogueBriefing(ArtifactSchema):
    """Director's one-time dramatic destination and pacing plan."""

    chosen_ending: NonEmptyText
    pacing_notes: NonEmptyText


class DialogueTurn(ArtifactSchema):
    """One character actor's isolated dialogue contribution."""

    scene_id: ReferenceId
    round_number: Annotated[StrictInt, Field(ge=1)]
    sequence_number: Annotated[StrictInt, Field(ge=1)]
    character_id: ReferenceId
    dialogue: NonEmptyText
    director_instruction: NonEmptyText | None = None


class DialogueEvaluation(ArtifactSchema):
    """Director's structured assessment after both actors complete a round."""

    round_number: Annotated[StrictInt, Field(ge=1)]
    emotional_arc: EmotionalArcStage
    arc_stages_hit: Annotated[tuple[EmotionalArcStage, ...], Field(min_length=1)]
    unresolved_threads: tuple[NonEmptyText, ...] = ()
    resolved_threads: tuple[NonEmptyText, ...] = ()
    closure_detected: StrictBool
    ending_type: NonEmptyText | None = None
    stage_direction: NonEmptyText | None = None
    scene_end: StrictBool = False

    @model_validator(mode="after")
    def validate_director_state(self) -> Self:
        """Keep arc history ordered and thread accounting unambiguous."""
        stage_order = tuple(EmotionalArcStage)
        expected_prefix = stage_order[: len(self.arc_stages_hit)]
        if self.arc_stages_hit != expected_prefix or stage_order.index(
            self.arc_stages_hit[-1]
        ) > stage_order.index(self.emotional_arc):
            raise ValueError("arc_stages_hit must be an ordered prefix no later than emotional_arc")
        overlap = set(self.unresolved_threads) & set(self.resolved_threads)
        if overlap:
            raise ValueError(
                f"dialogue threads cannot be both resolved and unresolved: {sorted(overlap)}"
            )
        if self.scene_end and (
            not self.closure_detected
            or self.emotional_arc not in {EmotionalArcStage.CLIMAX, EmotionalArcStage.RESOLUTION}
        ):
            raise ValueError("scene_end requires closure at the climax or resolution stage")
        return self


class SceneDraft(ArtifactSchema):
    """One complete prose scene produced from an exact Scene Plan version."""

    scene_id: ReferenceId
    scene_number: Annotated[StrictInt, Field(ge=1)]
    title: NonEmptyText
    revision_number: Annotated[StrictInt, Field(ge=0)]
    prose: NonEmptyText
    is_complete: StrictBool


class StoryBlueprint(ArtifactSchema):
    """Complete human-review checkpoint assembled from specialist artifacts."""

    creative_brief: CreativeBrief
    logline: NonEmptyText
    thematic_thesis: NonEmptyText
    world_summary: NonEmptyText
    characters: Annotated[tuple[Character, ...], Field(min_length=2, max_length=5)]
    relationships: Annotated[tuple[Relationship, ...], Field(min_length=1)]
    locations: Annotated[tuple[Location, ...], Field(min_length=1)]
    world_rules: Annotated[tuple[WorldRule, ...], Field(min_length=1)]
    central_conflict: NonEmptyText
    story_arc: NonEmptyText
    beats: Annotated[tuple[Beat, ...], Field(min_length=1)]
    scene_plans: Annotated[tuple[ScenePlan, ...], Field(min_length=3, max_length=8)]
    proposed_ending: NonEmptyText
    voice_and_style_guide: NonEmptyText
    potential_risks: tuple[NonEmptyText, ...] = ()
    unresolved_decisions: tuple[NonEmptyText, ...] = ()

    @model_validator(mode="after")
    def validate_blueprint_integrity(self) -> Self:
        """Reject duplicate, dangling, or structurally inconsistent references."""
        character_ids = _unique_ids(self.characters, "character")
        _unique_ids(self.relationships, "relationship")
        location_ids = _unique_ids(self.locations, "location")
        _unique_ids(self.world_rules, "world rule")
        beat_ids = _unique_ids(self.beats, "beat")
        _unique_ids(self.scene_plans, "scene")

        if len(self.characters) != self.creative_brief.target_significant_character_count:
            raise ValueError("character count must match the creative brief")
        if len(self.scene_plans) != self.creative_brief.target_scene_count:
            raise ValueError("scene count must match the creative brief")

        _require_contiguous(
            (beat.sequence for beat in self.beats),
            "beat sequence",
        )
        _require_contiguous(
            (scene.scene_number for scene in self.scene_plans),
            "scene number",
        )

        for relationship in self.relationships:
            _require_known(
                (relationship.source_character_id, relationship.target_character_id),
                character_ids,
                f"relationship {relationship.id} character",
            )
        for location in self.locations:
            _require_known(
                location.associated_character_ids,
                character_ids,
                f"location {location.id} character",
            )
        for rule in self.world_rules:
            _require_known(
                rule.relevant_character_ids,
                character_ids,
                f"world rule {rule.id} character",
            )
            _require_known(
                rule.relevant_location_ids,
                location_ids,
                f"world rule {rule.id} location",
            )
        for beat in self.beats:
            _require_known(beat.character_ids, character_ids, f"beat {beat.id} character")
            if beat.location_id is not None:
                _require_known((beat.location_id,), location_ids, f"beat {beat.id} location")
            _require_known(
                (*beat.depends_on_beat_ids, *beat.pays_off_beat_ids),
                beat_ids,
                f"beat {beat.id} beat",
            )
        for scene in self.scene_plans:
            _require_known(scene.character_ids, character_ids, f"scene {scene.id} character")
            _require_known((scene.location_id,), location_ids, f"scene {scene.id} location")
            _require_known(scene.beat_ids, beat_ids, f"scene {scene.id} beat")

        planned_beat_ids = {beat_id for scene in self.scene_plans for beat_id in scene.beat_ids}
        unplanned_beat_ids = beat_ids - planned_beat_ids
        if unplanned_beat_ids:
            raise ValueError(f"beats missing from scene plans: {sorted(unplanned_beat_ids)}")
        return self


type ArtifactSchemaType = type[ArtifactSchema]

ARTIFACT_SCHEMAS: Mapping[ArtifactKind, ArtifactSchemaType] = MappingProxyType(
    {
        ArtifactKind.CREATIVE_BRIEF: CreativeBrief,
        ArtifactKind.PREMISE: Premise,
        ArtifactKind.CHARACTER: Character,
        ArtifactKind.RELATIONSHIP: Relationship,
        ArtifactKind.LOCATION: Location,
        ArtifactKind.WORLD_RULE: WorldRule,
        ArtifactKind.BEAT: Beat,
        ArtifactKind.SCENE_PLAN: ScenePlan,
        ArtifactKind.CRITIQUE: Critique,
        ArtifactKind.CONTINUITY_FINDING: ContinuityFinding,
        ArtifactKind.CONTINUITY_REPORT: ContinuityReport,
        ArtifactKind.STORY_BLUEPRINT: StoryBlueprint,
        ArtifactKind.STORY_BIBLE: StoryBible,
        ArtifactKind.STORY_BIBLE_UPDATE: StoryBibleUpdate,
        ArtifactKind.DIALOGUE_BRIEFING: DialogueBriefing,
        ArtifactKind.DIALOGUE_TURN: DialogueTurn,
        ArtifactKind.DIALOGUE_EVALUATION: DialogueEvaluation,
        ArtifactKind.SCENE_DRAFT: SceneDraft,
    }
)


def artifact_json_schema(kind: ArtifactKind) -> dict[str, Any]:
    """Return the JSON Schema supplied to structured-output model calls."""
    return ARTIFACT_SCHEMAS[kind].model_json_schema()


def validate_artifact_json(kind: ArtifactKind, content: str | bytes) -> ArtifactSchema:
    """Validate raw model JSON against the registered artifact contract."""
    return ARTIFACT_SCHEMAS[kind].model_validate_json(content)


class _HasId(Protocol):
    @property
    def id(self) -> str: ...


def _unique_ids(items: tuple[_HasId, ...], label: str) -> set[str]:
    ids = [str(item.id) for item in items]
    duplicates = {item_id for item_id in ids if ids.count(item_id) > 1}
    if duplicates:
        raise ValueError(f"duplicate {label} IDs: {sorted(duplicates)}")
    return set(ids)


def _unique_text(items: Iterable[str], label: str) -> set[str]:
    values = tuple(items)
    _unique_key(values, label)
    return set(values)


def _unique_key(items: Iterable[str], label: str) -> None:
    values = tuple(items)
    if len(set(values)) != len(values):
        raise ValueError(f"{label} must be unique")


def _require_known(references: tuple[str, ...], known: set[str], label: str) -> None:
    unknown = set(references) - known
    if unknown:
        raise ValueError(f"unknown {label} IDs: {sorted(unknown)}")


def _require_contiguous(values: Iterable[int], label: str) -> None:
    ordered = list(values)
    expected = list(range(1, len(ordered) + 1))
    if ordered != expected:
        raise ValueError(f"{label}s must be ordered and contiguous from 1")
