"""Provider-neutral contracts for bounded scene production."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from enum import StrEnum
from types import MappingProxyType
from typing import ClassVar, Protocol
from uuid import UUID

from open_hollywood_engine.artifacts import (
    ArtifactKind,
    ContinuityReport,
    Critique,
    SceneDraft,
    StoryBible,
    StoryBibleUpdate,
)
from open_hollywood_engine.models.contracts import ModelCallBudget
from open_hollywood_engine.workflows.contracts import ArtifactReference
from open_hollywood_engine.workflows.dialogue_contracts import (
    DEFAULT_MAX_DIALOGUE_ROUNDS,
    DialogueCharacterReference,
    DialogueSceneResult,
)

SCENE_PRODUCTION_WORKFLOW_NAME = "scene_production"
SCENE_PRODUCTION_GRAPH_VERSION = "1"
SCENE_PRODUCTION_PROMPT_TEMPLATE_VERSION = "1"
DEFAULT_MAX_REVISION_CYCLES = 2
MAX_REVISION_CYCLES = 5
MIN_PRODUCTION_UNITS = 3
MAX_PRODUCTION_UNITS = 8
SCENE_WRITER_ROLE = "scene_writer"
SCENE_CRITIC_ROLE = "scene_critic"
CONTINUITY_SUPERVISOR_ROLE = "continuity_supervisor"
STORY_BIBLE_MAINTAINER_ROLE = "story_bible_maintainer"


def _is_integer(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


class ProductionNode(StrEnum):
    """Fixed nodes in the scene-by-scene production graph."""

    DRAFT = "draft"
    DIALOGUE_PASS = "dialogue_pass"
    DIALOGUE_INTEGRATION = "dialogue_integration"
    CRITIQUE = "critique"
    CONTINUITY = "continuity"
    STORY_BIBLE_UPDATE = "story_bible_update"
    ACCEPT = "accept"


class UnitAcceptanceReason(StrEnum):
    """Deterministic reason a produced unit became canonical."""

    PASSED_RUBRIC = "passed_rubric"
    REVISION_LIMIT_REACHED = "revision_limit_reached"


@dataclass(frozen=True, slots=True)
class ProductionNodeDefinition:
    """Registered role, timeout, and retry policy for one production node."""

    node: ProductionNode
    specialist_role: str | None
    timeout_seconds: int = 120
    max_attempts: int = 2

    def __post_init__(self) -> None:
        if self.specialist_role is not None and not self.specialist_role.strip():
            raise ValueError("specialist_role must not be empty")
        if not _is_integer(self.timeout_seconds) or self.timeout_seconds < 1:
            raise ValueError("timeout_seconds must be a positive integer")
        if not _is_integer(self.max_attempts) or self.max_attempts < 1:
            raise ValueError("max_attempts must be a positive integer")


PRODUCTION_NODE_DEFINITIONS: Mapping[ProductionNode, ProductionNodeDefinition] = MappingProxyType(
    {
        ProductionNode.DRAFT: ProductionNodeDefinition(
            node=ProductionNode.DRAFT,
            specialist_role=SCENE_WRITER_ROLE,
        ),
        ProductionNode.DIALOGUE_PASS: ProductionNodeDefinition(
            node=ProductionNode.DIALOGUE_PASS,
            specialist_role=None,
            max_attempts=1,
        ),
        ProductionNode.DIALOGUE_INTEGRATION: ProductionNodeDefinition(
            node=ProductionNode.DIALOGUE_INTEGRATION,
            specialist_role=SCENE_WRITER_ROLE,
        ),
        ProductionNode.CRITIQUE: ProductionNodeDefinition(
            node=ProductionNode.CRITIQUE,
            specialist_role=SCENE_CRITIC_ROLE,
        ),
        ProductionNode.CONTINUITY: ProductionNodeDefinition(
            node=ProductionNode.CONTINUITY,
            specialist_role=CONTINUITY_SUPERVISOR_ROLE,
        ),
        ProductionNode.STORY_BIBLE_UPDATE: ProductionNodeDefinition(
            node=ProductionNode.STORY_BIBLE_UPDATE,
            specialist_role=STORY_BIBLE_MAINTAINER_ROLE,
        ),
        ProductionNode.ACCEPT: ProductionNodeDefinition(
            node=ProductionNode.ACCEPT,
            specialist_role=None,
            max_attempts=1,
        ),
    }
)


@dataclass(frozen=True, slots=True)
class ProductionCharacterReference:
    """A participating character bound to one immutable dossier."""

    character_id: str
    artifact: ArtifactReference

    def __post_init__(self) -> None:
        if not self.character_id.strip():
            raise ValueError("character_id must not be empty")
        if self.artifact.kind is not ArtifactKind.CHARACTER:
            raise ValueError("production character requires a character artifact")

    def as_dialogue_character(self) -> DialogueCharacterReference:
        """Adapt the shared character input to the dialogue subgraph contract."""
        return DialogueCharacterReference(
            character_id=self.character_id,
            artifact=self.artifact,
        )


@dataclass(frozen=True, slots=True)
class DialoguePassConfiguration:
    """Optional bounded use of the two-character dialogue experiment."""

    character_ids: tuple[str, str]
    ending_options: tuple[str, ...]
    minimum_rounds: int = 2
    maximum_rounds: int = 6

    def __post_init__(self) -> None:
        if len(self.character_ids) != 2:
            raise ValueError("dialogue pass requires exactly two character IDs")
        _require_unique_text(self.character_ids, "dialogue character IDs")
        _require_unique_text(self.ending_options, "dialogue ending options")
        if not _is_integer(self.minimum_rounds) or self.minimum_rounds < 1:
            raise ValueError("minimum dialogue rounds must be a positive integer")
        if (
            not _is_integer(self.maximum_rounds)
            or self.maximum_rounds < self.minimum_rounds
            or self.maximum_rounds > DEFAULT_MAX_DIALOGUE_ROUNDS
        ):
            raise ValueError(
                "maximum dialogue rounds must be between the minimum and "
                f"{DEFAULT_MAX_DIALOGUE_ROUNDS}"
            )

    @property
    def max_graph_steps(self) -> int:
        """Return the Step 14 subgraph's exact recursion envelope."""
        return 1 + self.maximum_rounds * 3


@dataclass(frozen=True, slots=True)
class ProductionUnitInput:
    """One planned prose scene and its exact deterministic dependencies."""

    unit_id: str
    unit_number: int
    plan: ArtifactReference
    characters: tuple[ProductionCharacterReference, ...]
    context_artifacts: tuple[ArtifactReference, ...] = ()
    dialogue_pass: DialoguePassConfiguration | None = None

    def __post_init__(self) -> None:
        if not self.unit_id.strip():
            raise ValueError("unit_id must not be empty")
        if not _is_integer(self.unit_number) or self.unit_number < 1:
            raise ValueError("unit_number must be a positive integer")
        if self.plan.kind is not ArtifactKind.SCENE_PLAN:
            raise ValueError("v0.1 production units require a scene_plan artifact")
        if not self.characters:
            raise ValueError("production unit requires at least one character")
        character_ids = tuple(character.character_id for character in self.characters)
        _require_unique_text(character_ids, "production character IDs")
        if self.dialogue_pass is not None and not set(self.dialogue_pass.character_ids).issubset(
            character_ids
        ):
            raise ValueError("dialogue characters must participate in the production unit")
        _require_unique_versions(
            (
                self.plan,
                *(character.artifact for character in self.characters),
                *self.context_artifacts,
            ),
            "production unit inputs",
        )

    def dialogue_characters(
        self,
    ) -> tuple[DialogueCharacterReference, DialogueCharacterReference]:
        """Resolve the configured actors in the declared stable order."""
        if self.dialogue_pass is None:
            raise ValueError("production unit has no dialogue pass")
        by_id = {character.character_id: character for character in self.characters}
        first, second = self.dialogue_pass.character_ids
        return (
            by_id[first].as_dialogue_character(),
            by_id[second].as_dialogue_character(),
        )


@dataclass(frozen=True, slots=True)
class SceneProductionInput:
    """Complete bounded assignment for an approved short-story blueprint."""

    workflow_run_id: UUID
    model_profile_id: UUID
    approved_blueprint: ArtifactReference
    initial_story_bible: ArtifactReference
    units: tuple[ProductionUnitInput, ...]
    global_context_artifacts: tuple[ArtifactReference, ...]
    call_budget: ModelCallBudget
    prompt_template_version: str = SCENE_PRODUCTION_PROMPT_TEMPLATE_VERSION
    maximum_revision_cycles: int = DEFAULT_MAX_REVISION_CYCLES

    def __post_init__(self) -> None:
        if self.approved_blueprint.kind is not ArtifactKind.STORY_BLUEPRINT:
            raise ValueError("scene production requires an approved story_blueprint artifact")
        if self.initial_story_bible.kind is not ArtifactKind.STORY_BIBLE:
            raise ValueError("scene production requires an initial story_bible artifact")
        if not self.prompt_template_version.strip():
            raise ValueError("prompt_template_version must not be empty")
        if not MIN_PRODUCTION_UNITS <= len(self.units) <= MAX_PRODUCTION_UNITS:
            raise ValueError(
                f"scene production requires {MIN_PRODUCTION_UNITS} to {MAX_PRODUCTION_UNITS} units"
            )
        expected_numbers = tuple(range(1, len(self.units) + 1))
        if tuple(unit.unit_number for unit in self.units) != expected_numbers:
            raise ValueError("production units must be ordered and contiguous from 1")
        _require_unique_text(
            (unit.unit_id for unit in self.units),
            "production unit IDs",
        )
        if (
            not _is_integer(self.maximum_revision_cycles)
            or self.maximum_revision_cycles < 0
            or self.maximum_revision_cycles > MAX_REVISION_CYCLES
        ):
            raise ValueError(f"maximum_revision_cycles must be between 0 and {MAX_REVISION_CYCLES}")
        _require_unique_versions(
            (
                self.approved_blueprint,
                self.initial_story_bible,
                *self.global_context_artifacts,
                *(unit.plan for unit in self.units),
            ),
            "run-level production inputs",
        )

    @property
    def max_graph_steps(self) -> int:
        """Return a safe envelope including every nested dialogue step."""
        attempts = 1 + self.maximum_revision_cycles
        total = 0
        for unit in self.units:
            per_attempt = 3  # writer, critic, and worst-case continuity
            if unit.dialogue_pass is not None:
                per_attempt += unit.dialogue_pass.max_graph_steps + 1
            total += attempts * per_attempt + 2  # bible update and deterministic acceptance
        return total


@dataclass(frozen=True, slots=True)
class SceneWritingTask:
    """Write or revise one scene against exact dependency versions."""

    specialist_role: ClassVar[str] = SCENE_WRITER_ROLE
    production: SceneProductionInput
    unit: ProductionUnitInput
    accepted_units: tuple[ArtifactReference, ...]
    story_bible: ArtifactReference
    revision_number: int
    previous_draft: ArtifactReference | None = None
    previous_critique: ArtifactReference | None = None


@dataclass(frozen=True, slots=True)
class SceneDraftResult:
    """Typed prose content and its immutable persisted version."""

    draft: SceneDraft
    artifact: ArtifactReference


@dataclass(frozen=True, slots=True)
class DialogueIntegrationTask:
    """Reconcile an isolated dialogue run into one coherent prose scene."""

    specialist_role: ClassVar[str] = SCENE_WRITER_ROLE
    production: SceneProductionInput
    unit: ProductionUnitInput
    source_draft: ArtifactReference
    dialogue: DialogueSceneResult
    revision_number: int


@dataclass(frozen=True, slots=True)
class SceneCritiqueTask:
    """Evaluate one exact scene version independently of its writer."""

    specialist_role: ClassVar[str] = SCENE_CRITIC_ROLE
    production: SceneProductionInput
    unit: ProductionUnitInput
    draft: ArtifactReference
    accepted_units: tuple[ArtifactReference, ...]
    story_bible: ArtifactReference
    revision_number: int


@dataclass(frozen=True, slots=True)
class SceneCritiqueResult:
    """Typed rubric result and its immutable persisted version."""

    critique: Critique
    artifact: ArtifactReference


@dataclass(frozen=True, slots=True)
class ContinuityCheckTask:
    """Check one exact candidate scene against current canonical story truth."""

    specialist_role: ClassVar[str] = CONTINUITY_SUPERVISOR_ROLE
    production: SceneProductionInput
    unit: ProductionUnitInput
    story_bible: ArtifactReference
    draft: ArtifactReference
    accepted_units: tuple[ArtifactReference, ...]
    revision_number: int


@dataclass(frozen=True, slots=True)
class ContinuityCheckResult:
    """Typed continuity gate and its immutable persisted artifact."""

    report: ContinuityReport
    artifact: ArtifactReference


@dataclass(frozen=True, slots=True)
class StoryBibleUpdateTask:
    """Produce one typed delta from a continuity-cleared accepted scene."""

    specialist_role: ClassVar[str] = STORY_BIBLE_MAINTAINER_ROLE
    production: SceneProductionInput
    unit: ProductionUnitInput
    source_story_bible: ArtifactReference
    accepted_draft: ArtifactReference
    continuity_report: ArtifactReference
    accepted_units: tuple[ArtifactReference, ...]


@dataclass(frozen=True, slots=True)
class StoryBibleUpdateResult:
    """Source content, deterministic delta, and exact persisted successor."""

    source_story_bible: StoryBible
    update: StoryBibleUpdate
    story_bible: StoryBible
    update_artifact: ArtifactReference
    story_bible_artifact: ArtifactReference


@dataclass(frozen=True, slots=True)
class AcceptedProductionUnit:
    """Reference-only record for one canonical produced scene."""

    unit_id: str
    unit_number: int
    artifact: ArtifactReference
    critique_artifact: ArtifactReference
    continuity_artifact: ArtifactReference
    story_bible_update_artifact: ArtifactReference
    story_bible_artifact: ArtifactReference
    revision_cycles_used: int
    dialogue_runs: int
    acceptance_reason: UnitAcceptanceReason

    def __post_init__(self) -> None:
        if not self.unit_id.strip():
            raise ValueError("accepted production unit ID must not be empty")
        if not _is_integer(self.unit_number) or self.unit_number < 1:
            raise ValueError("accepted production unit number must be positive")
        expected_kinds = (
            (self.artifact, ArtifactKind.SCENE_DRAFT),
            (self.critique_artifact, ArtifactKind.CRITIQUE),
            (self.continuity_artifact, ArtifactKind.CONTINUITY_REPORT),
            (
                self.story_bible_update_artifact,
                ArtifactKind.STORY_BIBLE_UPDATE,
            ),
            (self.story_bible_artifact, ArtifactKind.STORY_BIBLE),
        )
        if any(reference.kind is not expected for reference, expected in expected_kinds):
            raise ValueError("accepted production unit has an invalid artifact kind")
        if not _is_integer(self.revision_cycles_used) or self.revision_cycles_used < 0:
            raise ValueError("accepted revision count must be a non-negative integer")
        if not _is_integer(self.dialogue_runs) or self.dialogue_runs < 0:
            raise ValueError("accepted dialogue count must be a non-negative integer")


@dataclass(frozen=True, slots=True)
class SceneProductionResult:
    """Reference-only output of the complete bounded production run."""

    workflow_run_id: UUID
    accepted_units: tuple[AcceptedProductionUnit, ...]
    final_story_bible: ArtifactReference

    def __post_init__(self) -> None:
        if not self.accepted_units:
            raise ValueError("scene production result requires accepted units")
        if tuple(unit.unit_number for unit in self.accepted_units) != tuple(
            range(1, len(self.accepted_units) + 1)
        ):
            raise ValueError("accepted production units must be ordered and contiguous")
        if (
            self.final_story_bible.kind is not ArtifactKind.STORY_BIBLE
            or self.final_story_bible != self.accepted_units[-1].story_bible_artifact
        ):
            raise ValueError(
                "final story bible must equal the last accepted unit's canonical version"
            )


class SceneProductionExecutor(Protocol):
    """Application boundary for budgeted model calls and artifact persistence."""

    async def write(self, task: SceneWritingTask) -> SceneDraftResult:
        """Produce and persist an initial or revised prose scene."""
        ...

    async def integrate_dialogue(
        self,
        task: DialogueIntegrationTask,
    ) -> SceneDraftResult:
        """Persist a prose revision incorporating the dialogue subgraph."""
        ...

    async def critique(self, task: SceneCritiqueTask) -> SceneCritiqueResult:
        """Score and persist an independent critique of one exact draft."""
        ...

    async def check_continuity(
        self,
        task: ContinuityCheckTask,
    ) -> ContinuityCheckResult:
        """Persist a complete continuity gate for one exact candidate scene."""
        ...

    async def update_story_bible(
        self,
        task: StoryBibleUpdateTask,
    ) -> StoryBibleUpdateResult:
        """Persist a deterministic canonical successor after continuity passes."""
        ...


class SceneProductionError(RuntimeError):
    """Base class for safe production-loop failures."""


class SceneProductionStateError(SceneProductionError):
    """Raised when checkpoint or executor output violates the graph contract."""


class RetryableSceneProductionError(SceneProductionError):
    """Failure category eligible for a registered bounded retry."""


def _require_unique_text(values: Iterable[str], label: str) -> None:
    materialized = tuple(values)
    if not materialized or any(not value.strip() for value in materialized):
        raise ValueError(f"{label} must contain non-empty values")
    if len(set(materialized)) != len(materialized):
        raise ValueError(f"{label} must be unique")


def _require_unique_versions(
    references: Iterable[ArtifactReference],
    label: str,
) -> None:
    version_ids = tuple(reference.version_id for reference in references)
    if len(set(version_ids)) != len(version_ids):
        raise ValueError(f"{label} must reference unique artifact versions")
