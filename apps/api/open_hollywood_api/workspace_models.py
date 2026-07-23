"""Public API contracts for the persisted creative workspace."""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from open_hollywood_api.services.workspace import (
    ArtifactRecord,
    ArtifactVersionDetailRecord,
    ArtifactVersionSummaryRecord,
    ConversationRecord,
    EvaluationRecord,
    MessageRecord,
    ProjectSummaryRecord,
    ProjectWorkspaceRecord,
    WorkflowRunRecord,
)


class WorkspaceModel(BaseModel):
    """Shared immutable API model configuration."""

    model_config = ConfigDict(frozen=True)


class ProjectSummary(WorkspaceModel):
    """One project in the workspace navigation."""

    id: UUID
    name: str
    description: str | None
    story_format: str
    status: str
    updated_at: datetime
    conversation_count: int
    artifact_count: int
    latest_workflow_run_id: UUID | None
    latest_workflow_status: str | None

    @classmethod
    def from_record(cls, record: ProjectSummaryRecord) -> ProjectSummary:
        return cls(**asdict(record))


class ProjectList(WorkspaceModel):
    """All locally persisted projects."""

    projects: list[ProjectSummary]


class WorkspaceMessage(WorkspaceModel):
    """One persisted message in sequence order."""

    id: UUID
    workflow_run_id: UUID | None
    sequence_number: int
    role: str
    content: str
    created_at: datetime

    @classmethod
    def from_record(cls, record: MessageRecord) -> WorkspaceMessage:
        return cls(**asdict(record))


class WorkspaceConversation(WorkspaceModel):
    """One conversation and its durable messages."""

    id: UUID
    title: str
    status: str
    messages: list[WorkspaceMessage]

    @classmethod
    def from_record(cls, record: ConversationRecord) -> WorkspaceConversation:
        return cls(
            id=record.id,
            title=record.title,
            status=record.status,
            messages=[WorkspaceMessage.from_record(message) for message in record.messages],
        )


class WorkspaceRun(WorkspaceModel):
    """Workflow status and active human checkpoint."""

    id: UUID
    parent_workflow_run_id: UUID | None
    workflow_name: str
    graph_version: str
    status: str
    current_node: str | None
    active_interrupt_id: str | None
    started_at: datetime | None
    completed_at: datetime | None
    updated_at: datetime
    error_code: str | None
    error_message: str | None

    @classmethod
    def from_record(cls, record: WorkflowRunRecord) -> WorkspaceRun:
        return cls(**asdict(record))


class ArtifactVersionSummary(WorkspaceModel):
    """Version lineage and provider-safe provenance."""

    id: UUID
    version_number: int
    parent_version_id: UUID | None
    schema_version: str
    change_summary: str | None
    created_at: datetime
    specialist_role: str | None
    provider: str | None
    model_identifier: str | None

    @classmethod
    def from_record(
        cls,
        record: ArtifactVersionSummaryRecord,
    ) -> ArtifactVersionSummary:
        return cls(**asdict(record))


class WorkspaceArtifact(WorkspaceModel):
    """Logical artifact with newest-first immutable versions."""

    id: UUID
    artifact_key: str
    artifact_type: str
    title: str
    status: str
    active_version_id: UUID | None
    versions: list[ArtifactVersionSummary]

    @classmethod
    def from_record(cls, record: ArtifactRecord) -> WorkspaceArtifact:
        return cls(
            id=record.id,
            artifact_key=record.artifact_key,
            artifact_type=record.artifact_type,
            title=record.title,
            status=record.status,
            active_version_id=record.active_version_id,
            versions=[ArtifactVersionSummary.from_record(version) for version in record.versions],
        )


class ProjectWorkspace(WorkspaceModel):
    """Persisted project shell consumed by the three-panel client."""

    project: ProjectSummary
    conversations: list[WorkspaceConversation]
    workflow_runs: list[WorkspaceRun]
    artifacts: list[WorkspaceArtifact]

    @classmethod
    def from_record(cls, record: ProjectWorkspaceRecord) -> ProjectWorkspace:
        return cls(
            project=ProjectSummary.from_record(record.project),
            conversations=[
                WorkspaceConversation.from_record(conversation)
                for conversation in record.conversations
            ],
            workflow_runs=[
                WorkspaceRun.from_record(workflow_run) for workflow_run in record.workflow_runs
            ],
            artifacts=[WorkspaceArtifact.from_record(artifact) for artifact in record.artifacts],
        )


class WorkspaceEvaluation(WorkspaceModel):
    """Evaluation summary for an artifact version."""

    id: UUID
    rubric_name: str
    rubric_version: str
    scores: dict[str, Any]
    weighted_score: Decimal | None
    summary: str | None
    created_at: datetime

    @classmethod
    def from_record(cls, record: EvaluationRecord) -> WorkspaceEvaluation:
        return cls(**asdict(record))


class ArtifactVersionDetail(WorkspaceModel):
    """Full immutable artifact content and review context."""

    artifact: WorkspaceArtifact
    selected_version: ArtifactVersionSummary
    content: dict[str, Any]
    content_sha256: str
    evaluations: list[WorkspaceEvaluation]

    @classmethod
    def from_record(
        cls,
        record: ArtifactVersionDetailRecord,
    ) -> ArtifactVersionDetail:
        return cls(
            artifact=WorkspaceArtifact.from_record(record.artifact),
            selected_version=ArtifactVersionSummary.from_record(record.selected_version),
            content=record.content,
            content_sha256=record.content_sha256,
            evaluations=[
                WorkspaceEvaluation.from_record(evaluation) for evaluation in record.evaluations
            ],
        )
