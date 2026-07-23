"""Provider-neutral contracts for the first story-blueprint workflow."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from enum import StrEnum
from types import MappingProxyType
from typing import Any, Protocol
from uuid import UUID

from open_hollywood_engine.artifacts import ArtifactKind

STORY_BLUEPRINT_WORKFLOW_NAME = "story_blueprint"
STORY_BLUEPRINT_GRAPH_VERSION = "2"
DEFAULT_MAX_GRAPH_STEPS = 12


class BlueprintNode(StrEnum):
    """Fixed nodes in the bounded v0.1 blueprint graph."""

    INTAKE = "intake"
    BRIEF = "brief"
    PREMISE = "premise"
    WORLD_SPECIALIST = "world_specialist"
    CHARACTER_SPECIALIST = "character_specialist"
    INTEGRATION = "integration"
    EVALUATION = "evaluation"
    APPROVAL = "approval"


class BlueprintDecisionAction(StrEnum):
    """Human choices accepted at the mandatory Story Blueprint interrupt."""

    APPROVE = "approve"
    REVISE = "revise"
    REJECT = "reject"
    FORK = "fork"


BLUEPRINT_NODE_ORDER = (
    BlueprintNode.INTAKE,
    BlueprintNode.BRIEF,
    BlueprintNode.PREMISE,
    BlueprintNode.WORLD_SPECIALIST,
    BlueprintNode.CHARACTER_SPECIALIST,
    BlueprintNode.INTEGRATION,
    BlueprintNode.EVALUATION,
    BlueprintNode.APPROVAL,
)
_NODE_INDEX = {node: index for index, node in enumerate(BLUEPRINT_NODE_ORDER)}


@dataclass(frozen=True, slots=True)
class ArtifactReference:
    """Checkpoint-safe pointer to one immutable artifact version."""

    kind: ArtifactKind
    artifact_key: str
    version_id: UUID
    schema_version: str

    def __post_init__(self) -> None:
        if not self.artifact_key or not self.artifact_key.strip():
            raise ValueError("artifact_key must not be empty")
        if not self.schema_version or not self.schema_version.strip():
            raise ValueError("schema_version must not be empty")


@dataclass(frozen=True, slots=True)
class ArtifactOutputRequirement:
    """Completion condition for one artifact kind emitted by a node."""

    kind: ArtifactKind
    minimum_count: int
    maximum_count: int | None = None

    def __post_init__(self) -> None:
        if not _is_integer(self.minimum_count) or self.minimum_count < 1:
            raise ValueError("minimum_count must be a positive integer")
        if self.maximum_count is not None and (
            not _is_integer(self.maximum_count) or self.maximum_count < self.minimum_count
        ):
            raise ValueError("maximum_count must be an integer at least minimum_count")


@dataclass(frozen=True, slots=True)
class BlueprintNodeDefinition:
    """Registered node contract independent from LangGraph runtime types."""

    node: BlueprintNode
    specialist_role: str | None
    input_kinds: tuple[ArtifactKind, ...] = ()
    output_requirements: tuple[ArtifactOutputRequirement, ...] = ()
    timeout_seconds: int = 120
    max_attempts: int = 2

    def __post_init__(self) -> None:
        if self.specialist_role is not None and not self.specialist_role.strip():
            raise ValueError("specialist_role must not be empty")
        _require_unique(self.input_kinds, "input artifact kinds")
        _require_unique(
            (requirement.kind for requirement in self.output_requirements),
            "output artifact kinds",
        )
        if not _is_integer(self.timeout_seconds) or self.timeout_seconds < 1:
            raise ValueError("timeout_seconds must be a positive integer")
        if not _is_integer(self.max_attempts) or self.max_attempts < 1:
            raise ValueError("max_attempts must be a positive integer")


def _require_unique(values: Iterable[object], label: str) -> None:
    materialized = tuple(values)
    if len(set(materialized)) != len(materialized):
        raise ValueError(f"{label} must be unique")


def _is_integer(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


BLUEPRINT_NODE_DEFINITIONS: Mapping[BlueprintNode, BlueprintNodeDefinition] = MappingProxyType(
    {
        BlueprintNode.INTAKE: BlueprintNodeDefinition(
            node=BlueprintNode.INTAKE,
            specialist_role=None,
            max_attempts=1,
        ),
        BlueprintNode.BRIEF: BlueprintNodeDefinition(
            node=BlueprintNode.BRIEF,
            specialist_role="brief_architect",
            output_requirements=(ArtifactOutputRequirement(ArtifactKind.CREATIVE_BRIEF, 1, 1),),
        ),
        BlueprintNode.PREMISE: BlueprintNodeDefinition(
            node=BlueprintNode.PREMISE,
            specialist_role="premise_architect",
            input_kinds=(ArtifactKind.CREATIVE_BRIEF,),
            output_requirements=(ArtifactOutputRequirement(ArtifactKind.PREMISE, 1, 1),),
        ),
        BlueprintNode.WORLD_SPECIALIST: BlueprintNodeDefinition(
            node=BlueprintNode.WORLD_SPECIALIST,
            specialist_role="world_builder",
            input_kinds=(ArtifactKind.CREATIVE_BRIEF, ArtifactKind.PREMISE),
            output_requirements=(
                ArtifactOutputRequirement(ArtifactKind.LOCATION, 1),
                ArtifactOutputRequirement(ArtifactKind.WORLD_RULE, 1),
            ),
        ),
        BlueprintNode.CHARACTER_SPECIALIST: BlueprintNodeDefinition(
            node=BlueprintNode.CHARACTER_SPECIALIST,
            specialist_role="character_architect",
            input_kinds=(ArtifactKind.CREATIVE_BRIEF, ArtifactKind.PREMISE),
            output_requirements=(
                ArtifactOutputRequirement(ArtifactKind.CHARACTER, 2, 5),
                ArtifactOutputRequirement(ArtifactKind.RELATIONSHIP, 1),
            ),
        ),
        BlueprintNode.INTEGRATION: BlueprintNodeDefinition(
            node=BlueprintNode.INTEGRATION,
            specialist_role="blueprint_integrator",
            input_kinds=(
                ArtifactKind.CREATIVE_BRIEF,
                ArtifactKind.PREMISE,
                ArtifactKind.LOCATION,
                ArtifactKind.WORLD_RULE,
                ArtifactKind.CHARACTER,
                ArtifactKind.RELATIONSHIP,
            ),
            output_requirements=(ArtifactOutputRequirement(ArtifactKind.STORY_BLUEPRINT, 1, 1),),
        ),
        BlueprintNode.EVALUATION: BlueprintNodeDefinition(
            node=BlueprintNode.EVALUATION,
            specialist_role="blueprint_critic",
            input_kinds=(ArtifactKind.STORY_BLUEPRINT,),
            output_requirements=(ArtifactOutputRequirement(ArtifactKind.CRITIQUE, 1, 1),),
        ),
        BlueprintNode.APPROVAL: BlueprintNodeDefinition(
            node=BlueprintNode.APPROVAL,
            specialist_role=None,
            input_kinds=(ArtifactKind.STORY_BLUEPRINT, ArtifactKind.CRITIQUE),
            max_attempts=1,
        ),
    }
)


@dataclass(frozen=True, slots=True)
class BlueprintNodeTask:
    """Exact artifact-version assignment passed to a registered specialist."""

    workflow_run_id: UUID
    node: BlueprintNode
    specialist_role: str
    input_artifacts: tuple[ArtifactReference, ...]
    human_decision_id: UUID | None = None
    reviewed_artifacts: tuple[ArtifactReference, ...] = ()


@dataclass(frozen=True, slots=True)
class BlueprintNodeResult:
    """Validated artifact references emitted by a specialist execution."""

    artifacts: tuple[ArtifactReference, ...]


@dataclass(frozen=True, slots=True)
class BlueprintHumanDecision:
    """Validated, idempotent command used to resume one graph interrupt."""

    id: UUID
    interrupt_id: str
    action: BlueprintDecisionAction
    instruction: str | None = None

    def __post_init__(self) -> None:
        if not self.interrupt_id or not self.interrupt_id.strip():
            raise ValueError("interrupt_id must not be empty")
        normalized = self.instruction.strip() if self.instruction is not None else None
        if normalized is not None and len(normalized) > 10_000:
            raise ValueError("instruction must not exceed 10000 characters")
        if (
            self.action
            in {
                BlueprintDecisionAction.REVISE,
                BlueprintDecisionAction.REJECT,
                BlueprintDecisionAction.FORK,
            }
            and not normalized
        ):
            raise ValueError(f"{self.action.value} requires a non-empty instruction")
        if self.action is BlueprintDecisionAction.APPROVE and normalized:
            raise ValueError("approve does not accept an instruction")
        object.__setattr__(self, "instruction", normalized)

    def resume_payload(self) -> dict[str, str]:
        """Return the JSON-safe value supplied to LangGraph's interrupt."""
        return {
            "decision_id": str(self.id),
            "action": self.action.value,
        }


@dataclass(frozen=True, slots=True)
class BlueprintDecisionResume:
    """Coordination-only decision data restored inside the graph."""

    decision_id: UUID
    action: BlueprintDecisionAction

    @classmethod
    def from_payload(cls, payload: Any) -> BlueprintDecisionResume:
        """Validate the coordination-only value returned by an interrupt."""
        if not isinstance(payload, dict):
            raise BlueprintStateError("human decision payload must be an object")
        if set(payload) != {"decision_id", "action"}:
            raise BlueprintStateError(
                "human decision payload must contain only decision_id and action"
            )
        try:
            decision_id = UUID(payload["decision_id"])
            action = BlueprintDecisionAction(payload["action"])
        except (KeyError, TypeError, ValueError) as exc:
            raise BlueprintStateError("human decision payload is invalid") from exc
        return cls(decision_id=decision_id, action=action)


class BlueprintNodeExecutor(Protocol):
    """Registered specialist execution boundary used by the graph."""

    async def execute(self, task: BlueprintNodeTask) -> BlueprintNodeResult:
        """Execute one bounded specialist task and durably store its outputs."""
        ...


class BlueprintWorkflowObserver(Protocol):
    """Persistence-neutral lifecycle observer for run records and event streams."""

    async def node_started(self, workflow_run_id: UUID, node: BlueprintNode) -> None:
        """Record that a node attempt began."""
        ...

    async def node_completed(
        self,
        workflow_run_id: UUID,
        node: BlueprintNode,
        artifacts: tuple[ArtifactReference, ...],
    ) -> None:
        """Record a node completion and its exact outputs."""
        ...

    async def awaiting_approval(
        self,
        workflow_run_id: UUID,
        artifacts: tuple[ArtifactReference, ...],
        interrupt_id: str,
    ) -> None:
        """Record that autonomous blueprint construction reached review."""
        ...

    async def workflow_failed(self, workflow_run_id: UUID, error: Exception) -> None:
        """Record a terminal execution attempt failure."""
        ...


class NullBlueprintWorkflowObserver:
    """No-op observer useful for engine-only tests and embedding."""

    async def node_started(self, workflow_run_id: UUID, node: BlueprintNode) -> None:
        del workflow_run_id, node

    async def node_completed(
        self,
        workflow_run_id: UUID,
        node: BlueprintNode,
        artifacts: tuple[ArtifactReference, ...],
    ) -> None:
        del workflow_run_id, node, artifacts

    async def awaiting_approval(
        self,
        workflow_run_id: UUID,
        artifacts: tuple[ArtifactReference, ...],
        interrupt_id: str,
    ) -> None:
        del workflow_run_id, artifacts, interrupt_id

    async def workflow_failed(self, workflow_run_id: UUID, error: Exception) -> None:
        del workflow_run_id, error


class BlueprintWorkflowError(RuntimeError):
    """Base class for safe blueprint workflow failures."""


class BlueprintStateError(BlueprintWorkflowError):
    """Raised when checkpointed artifact state violates a node contract."""


class RetryableSpecialistError(BlueprintWorkflowError):
    """Failure category eligible for the node's explicit retry policy."""


def node_sort_key(node: BlueprintNode) -> int:
    """Return the stable topology order for a registered node."""
    return _NODE_INDEX[node]
