"""Provider-neutral contracts for the isolated character-dialogue subgraph."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from enum import StrEnum
from types import MappingProxyType
from typing import ClassVar, Protocol
from uuid import UUID

from open_hollywood_engine.artifacts import (
    ArtifactKind,
    DialogueBriefing,
    DialogueEvaluation,
    DialogueTurn,
)
from open_hollywood_engine.models.contracts import ModelCallBudget
from open_hollywood_engine.workflows.contracts import ArtifactReference

DIALOGUE_SUBGRAPH_NAME = "character_dialogue"
DIALOGUE_SUBGRAPH_VERSION = "1"
DIALOGUE_PROMPT_TEMPLATE_VERSION = "1"
DEFAULT_MAX_DIALOGUE_ROUNDS = 30
CHARACTER_ACTOR_ROLE = "character_actor"
DIALOGUE_DIRECTOR_ROLE = "dialogue_director"


def _is_integer(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


class DialogueNode(StrEnum):
    """Fixed nodes in the two-character experiment."""

    DIRECTOR_BRIEFING = "director_briefing"
    CHARACTER_ONE = "character_one"
    CHARACTER_TWO = "character_two"
    DIRECTOR_EVALUATION = "director_evaluation"


class DialogueCompletionReason(StrEnum):
    """Deterministic reasons the bounded experiment can stop."""

    DIRECTOR_ENDED = "director_ended"
    MAXIMUM_ROUNDS = "maximum_rounds"


@dataclass(frozen=True, slots=True)
class DialogueNodeDefinition:
    """Registered retry and timeout policy for one explicit graph node."""

    node: DialogueNode
    specialist_role: str
    timeout_seconds: int = 120
    max_attempts: int = 2

    def __post_init__(self) -> None:
        if not self.specialist_role.strip():
            raise ValueError("specialist_role must not be empty")
        if (
            not isinstance(self.timeout_seconds, int)
            or isinstance(self.timeout_seconds, bool)
            or self.timeout_seconds < 1
        ):
            raise ValueError("timeout_seconds must be a positive integer")
        if (
            not isinstance(self.max_attempts, int)
            or isinstance(self.max_attempts, bool)
            or self.max_attempts < 1
        ):
            raise ValueError("max_attempts must be a positive integer")


DIALOGUE_NODE_DEFINITIONS: Mapping[DialogueNode, DialogueNodeDefinition] = MappingProxyType(
    {
        DialogueNode.DIRECTOR_BRIEFING: DialogueNodeDefinition(
            node=DialogueNode.DIRECTOR_BRIEFING,
            specialist_role=DIALOGUE_DIRECTOR_ROLE,
        ),
        DialogueNode.CHARACTER_ONE: DialogueNodeDefinition(
            node=DialogueNode.CHARACTER_ONE,
            specialist_role=CHARACTER_ACTOR_ROLE,
        ),
        DialogueNode.CHARACTER_TWO: DialogueNodeDefinition(
            node=DialogueNode.CHARACTER_TWO,
            specialist_role=CHARACTER_ACTOR_ROLE,
        ),
        DialogueNode.DIRECTOR_EVALUATION: DialogueNodeDefinition(
            node=DialogueNode.DIRECTOR_EVALUATION,
            specialist_role=DIALOGUE_DIRECTOR_ROLE,
        ),
    }
)


@dataclass(frozen=True, slots=True)
class DialogueCharacterReference:
    """One character actor bound to an exact immutable dossier version."""

    character_id: str
    artifact: ArtifactReference

    def __post_init__(self) -> None:
        if not self.character_id.strip():
            raise ValueError("character_id must not be empty")
        if self.artifact.kind is not ArtifactKind.CHARACTER:
            raise ValueError("character actor requires a character artifact")


@dataclass(frozen=True, slots=True)
class DialogueSceneInput:
    """Complete bounded assignment for the isolated two-actor experiment."""

    workflow_run_id: UUID
    model_profile_id: UUID
    scene_id: str
    scene_plan: ArtifactReference
    characters: tuple[DialogueCharacterReference, DialogueCharacterReference]
    context_artifacts: tuple[ArtifactReference, ...]
    ending_options: tuple[str, ...]
    call_budget: ModelCallBudget
    prompt_template_version: str = DIALOGUE_PROMPT_TEMPLATE_VERSION
    minimum_rounds: int = 6
    maximum_rounds: int = DEFAULT_MAX_DIALOGUE_ROUNDS

    def __post_init__(self) -> None:
        if not self.scene_id.strip():
            raise ValueError("scene_id must not be empty")
        if not self.prompt_template_version.strip():
            raise ValueError("prompt_template_version must not be empty")
        if self.scene_plan.kind is not ArtifactKind.SCENE_PLAN:
            raise ValueError("dialogue scene requires a scene_plan artifact")
        character_ids = [character.character_id for character in self.characters]
        if len(set(character_ids)) != 2:
            raise ValueError("dialogue experiment requires two distinct characters")
        character_versions = [character.artifact.version_id for character in self.characters]
        if len(set(character_versions)) != 2:
            raise ValueError("dialogue characters require distinct artifact versions")
        if not _is_integer(self.minimum_rounds) or self.minimum_rounds < 1:
            raise ValueError("minimum_rounds must be a positive integer")
        if (
            not _is_integer(self.maximum_rounds)
            or self.maximum_rounds < self.minimum_rounds
            or self.maximum_rounds > DEFAULT_MAX_DIALOGUE_ROUNDS
        ):
            raise ValueError(
                f"maximum_rounds must be between minimum_rounds and {DEFAULT_MAX_DIALOGUE_ROUNDS}"
            )
        _require_unique_text(self.ending_options, "ending options")
        all_references = (
            self.scene_plan,
            *(character.artifact for character in self.characters),
            *self.context_artifacts,
        )
        version_ids = [reference.version_id for reference in all_references]
        if len(set(version_ids)) != len(version_ids):
            raise ValueError("dialogue input artifact versions must be unique")

    @property
    def max_graph_steps(self) -> int:
        """Return the exact recursion envelope for briefing plus bounded rounds."""
        return 1 + self.maximum_rounds * 3


@dataclass(frozen=True, slots=True)
class DirectorBriefingTask:
    """One director call before either character speaks."""

    specialist_role: ClassVar[str] = DIALOGUE_DIRECTOR_ROLE
    scene: DialogueSceneInput


@dataclass(frozen=True, slots=True)
class DirectorBriefingResult:
    """Typed briefing content and its immutable persisted version."""

    briefing: DialogueBriefing
    artifact: ArtifactReference


@dataclass(frozen=True, slots=True)
class CharacterTurnTask:
    """One isolated actor assignment with reference-only scene history."""

    specialist_role: ClassVar[str] = CHARACTER_ACTOR_ROLE
    scene: DialogueSceneInput
    character: DialogueCharacterReference
    round_number: int
    sequence_number: int
    briefing_artifact: ArtifactReference
    dialogue_history: tuple[ArtifactReference, ...]
    previous_evaluation: ArtifactReference | None


@dataclass(frozen=True, slots=True)
class CharacterTurnResult:
    """Typed dialogue contribution and its immutable persisted version."""

    turn: DialogueTurn
    artifact: ArtifactReference


@dataclass(frozen=True, slots=True)
class DirectorEvaluationTask:
    """One director assessment after both actors complete a round."""

    specialist_role: ClassVar[str] = DIALOGUE_DIRECTOR_ROLE
    scene: DialogueSceneInput
    round_number: int
    briefing_artifact: ArtifactReference
    dialogue_history: tuple[ArtifactReference, ...]
    previous_evaluation: ArtifactReference | None


@dataclass(frozen=True, slots=True)
class DirectorEvaluationResult:
    """Typed round assessment and its immutable persisted version."""

    evaluation: DialogueEvaluation
    artifact: ArtifactReference


@dataclass(frozen=True, slots=True)
class DialogueSceneResult:
    """Reference-only output of one completed dialogue experiment."""

    scene_id: str
    briefing_artifact: ArtifactReference
    dialogue_turn_artifacts: tuple[ArtifactReference, ...]
    evaluation_artifacts: tuple[ArtifactReference, ...]
    rounds_completed: int
    completion_reason: DialogueCompletionReason


class DialogueSubgraphExecutor(Protocol):
    """Application boundary that calls models and persists typed outputs."""

    async def brief(self, task: DirectorBriefingTask) -> DirectorBriefingResult:
        """Choose a dramatic destination before the scene begins."""
        ...

    async def perform(self, task: CharacterTurnTask) -> CharacterTurnResult:
        """Produce and persist one actor's isolated dialogue contribution."""
        ...

    async def evaluate(
        self,
        task: DirectorEvaluationTask,
    ) -> DirectorEvaluationResult:
        """Assess one completed round and provide the next direction."""
        ...


class DialogueWorkflowError(RuntimeError):
    """Base class for safe dialogue-subgraph failures."""


class DialogueStateError(DialogueWorkflowError):
    """Raised when checkpoint or executor output violates the graph contract."""


class RetryableDialogueError(DialogueWorkflowError):
    """Failure category eligible for an explicit node retry."""


def _require_unique_text(values: Iterable[str], label: str) -> None:
    materialized = tuple(values)
    if not materialized or any(not value.strip() for value in materialized):
        raise ValueError(f"{label} must contain non-empty values")
    if len(set(materialized)) != len(materialized):
        raise ValueError(f"{label} must be unique")
