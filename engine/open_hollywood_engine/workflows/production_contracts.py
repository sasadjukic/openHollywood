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
    Critique,
    SceneDraft,
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


def _is_integer(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


class ProductionNode(StrEnum):
    """Fixed nodes in the scene-by-scene production graph."""

    DRAFT = "draft"
    DIALOGUE_PASS = "dialogue_pass"
    DIALOGUE_INTEGRATION = "dialogue_integration"
    CRITIQUE = "critique"
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
    units: tuple[ProductionUnitInput, ...]
    global_context_artifacts: tuple[ArtifactReference, ...]
    call_budget: ModelCallBudget
    prompt_template_version: str = SCENE_PRODUCTION_PROMPT_TEMPLATE_VERSION
    maximum_revision_cycles: int = DEFAULT_MAX_REVISION_CYCLES

    def __post_init__(self) -> None:
        if self.approved_blueprint.kind is not ArtifactKind.STORY_BLUEPRINT:
            raise ValueError("scene production requires an approved story_blueprint artifact")
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
            per_attempt = 2  # writer and critic
            if unit.dialogue_pass is not None:
                per_attempt += unit.dialogue_pass.max_graph_steps + 1
            total += attempts * per_attempt + 1  # deterministic acceptance
        return total


@dataclass(frozen=True, slots=True)
class SceneWritingTask:
    """Write or revise one scene against exact dependency versions."""

    specialist_role: ClassVar[str] = SCENE_WRITER_ROLE
    production: SceneProductionInput
    unit: ProductionUnitInput
    accepted_units: tuple[ArtifactReference, ...]
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
    revision_number: int


@dataclass(frozen=True, slots=True)
class SceneCritiqueResult:
    """Typed rubric result and its immutable persisted version."""

    critique: Critique
    artifact: ArtifactReference


@dataclass(frozen=True, slots=True)
class AcceptedProductionUnit:
    """Reference-only record for one canonical produced scene."""

    unit_id: str
    unit_number: int
    artifact: ArtifactReference
    critique_artifact: ArtifactReference
    revision_cycles_used: int
    dialogue_runs: int
    acceptance_reason: UnitAcceptanceReason


@dataclass(frozen=True, slots=True)
class SceneProductionResult:
    """Reference-only output of the complete bounded production run."""

    workflow_run_id: UUID
    accepted_units: tuple[AcceptedProductionUnit, ...]


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
