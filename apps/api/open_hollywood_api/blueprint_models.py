"""Public API contracts for Story Blueprint human decisions."""

from __future__ import annotations

from typing import Self
from uuid import UUID

from open_hollywood_engine.artifacts import ArtifactKind
from open_hollywood_engine.workflows import (
    ArtifactReference,
    BlueprintDecisionAction,
    BlueprintHumanDecision,
)
from pydantic import BaseModel, ConfigDict, Field, model_validator

from open_hollywood_api.services.blueprint_workflow import BlueprintWorkflowExecution


class BlueprintDecisionRequest(BaseModel):
    """One idempotent command resolving the active blueprint interrupt."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    decision_id: UUID
    interrupt_id: str = Field(min_length=1, max_length=200)
    action: BlueprintDecisionAction
    instruction: str | None = Field(default=None, max_length=10_000)

    @model_validator(mode="after")
    def validate_domain_contract(self) -> Self:
        """Apply the provider-neutral decision invariants at the API boundary."""
        self.to_domain()
        return self

    def to_domain(self) -> BlueprintHumanDecision:
        """Convert the API request into the engine command."""
        return BlueprintHumanDecision(
            id=self.decision_id,
            interrupt_id=self.interrupt_id,
            action=self.action,
            instruction=self.instruction,
        )


class ArtifactReferenceEnvelope(BaseModel):
    """Immutable artifact-version pointer safe for UI consumption."""

    model_config = ConfigDict(frozen=True)

    artifact_kind: ArtifactKind
    artifact_key: str
    artifact_version_id: UUID
    schema_version: str

    @classmethod
    def from_domain(cls, artifact: ArtifactReference) -> ArtifactReferenceEnvelope:
        """Convert the provider-neutral reference into an API response."""
        return cls(
            artifact_kind=artifact.kind,
            artifact_key=artifact.artifact_key,
            artifact_version_id=artifact.version_id,
            schema_version=artifact.schema_version,
        )


class BlueprintDecisionResponse(BaseModel):
    """Workflow state after the decision reaches a durable checkpoint."""

    model_config = ConfigDict(frozen=True)

    workflow_run_id: UUID
    checkpoint_id: str
    artifacts: list[ArtifactReferenceEnvelope]
    awaiting_approval: bool
    interrupt_id: str | None

    @classmethod
    def from_domain(
        cls,
        execution: BlueprintWorkflowExecution,
    ) -> BlueprintDecisionResponse:
        """Convert a durable execution result into the public contract."""
        return cls(
            workflow_run_id=execution.workflow_run_id,
            checkpoint_id=execution.checkpoint_id,
            artifacts=[
                ArtifactReferenceEnvelope.from_domain(artifact) for artifact in execution.artifacts
            ],
            awaiting_approval=execution.awaiting_approval,
            interrupt_id=execution.interrupt_id,
        )
