"""Read-only persisted workspace queries for the local React client."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from open_hollywood_engine.workflows import (
    BLUEPRINT_RETRYABLE_NODES,
    DEFAULT_MAX_GRAPH_STEPS,
    STORY_BLUEPRINT_WORKFLOW_NAME,
    RunBudget,
    RunPauseReason,
)
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload, sessionmaker

from open_hollywood_api.persistence.models import (
    Artifact,
    ArtifactVersion,
    Conversation,
    Evaluation,
    Project,
    WorkflowEvent,
    WorkflowRun,
)
from open_hollywood_api.services.run_controls import run_usage


@dataclass(frozen=True, slots=True)
class ProjectSummaryRecord:
    """One project card backed by persisted counts and latest run state."""

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


@dataclass(frozen=True, slots=True)
class MessageRecord:
    """One ordered persisted chat message."""

    id: UUID
    workflow_run_id: UUID | None
    sequence_number: int
    role: str
    content: str
    created_at: datetime


@dataclass(frozen=True, slots=True)
class ConversationRecord:
    """One project conversation and its ordered messages."""

    id: UUID
    title: str
    status: str
    messages: tuple[MessageRecord, ...]


@dataclass(frozen=True, slots=True)
class WorkflowRunRecord:
    """UI-safe workflow status without checkpoint or prompt content."""

    id: UUID
    parent_workflow_run_id: UUID | None
    workflow_name: str
    graph_version: str
    status: str
    pause_reason: str | None
    current_node: str | None
    active_interrupt_id: str | None
    started_at: datetime | None
    completed_at: datetime | None
    updated_at: datetime
    error_code: str | None
    error_message: str | None
    budget: dict[str, int | str]
    usage: dict[str, int | str]
    retryable_nodes: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ArtifactVersionSummaryRecord:
    """Immutable version metadata used by the inspector selector."""

    id: UUID
    version_number: int
    parent_version_id: UUID | None
    schema_version: str
    change_summary: str | None
    created_at: datetime
    specialist_role: str | None
    provider: str | None
    model_identifier: str | None


@dataclass(frozen=True, slots=True)
class ArtifactRecord:
    """Logical artifact with newest-first immutable version history."""

    id: UUID
    artifact_key: str
    artifact_type: str
    title: str
    status: str
    active_version_id: UUID | None
    versions: tuple[ArtifactVersionSummaryRecord, ...]


@dataclass(frozen=True, slots=True)
class ProjectWorkspaceRecord:
    """Complete persisted project shell, excluding full artifact bodies."""

    project: ProjectSummaryRecord
    conversations: tuple[ConversationRecord, ...]
    workflow_runs: tuple[WorkflowRunRecord, ...]
    artifacts: tuple[ArtifactRecord, ...]


@dataclass(frozen=True, slots=True)
class EvaluationRecord:
    """Human-facing evaluation attached to one immutable version."""

    id: UUID
    rubric_name: str
    rubric_version: str
    scores: dict[str, Any]
    weighted_score: Decimal | None
    summary: str | None
    created_at: datetime


@dataclass(frozen=True, slots=True)
class ArtifactVersionDetailRecord:
    """Full content and provenance for one immutable artifact version."""

    artifact: ArtifactRecord
    selected_version: ArtifactVersionSummaryRecord
    content: dict[str, Any]
    content_sha256: str
    evaluations: tuple[EvaluationRecord, ...]


class WorkspaceProjectNotFoundError(LookupError):
    """Raised when a requested project does not exist."""


class WorkspaceArtifactVersionNotFoundError(LookupError):
    """Raised when a requested artifact version does not exist."""


class WorkspaceStore:
    """Read persisted workspace records through a small application boundary."""

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def list_projects(self) -> tuple[ProjectSummaryRecord, ...]:
        """Return newest-updated projects with durable workspace counts."""
        with self._session_factory() as session:
            projects = session.scalars(
                select(Project)
                .options(
                    selectinload(Project.conversations),
                    selectinload(Project.artifacts),
                    selectinload(Project.workflow_runs),
                )
                .order_by(Project.updated_at.desc(), Project.name, Project.id)
            ).all()
            return tuple(_project_summary(project) for project in projects)

    def get_project_workspace(self, project_id: UUID) -> ProjectWorkspaceRecord:
        """Load one complete workspace shell from SQLite."""
        with self._session_factory() as session:
            project = session.scalar(
                select(Project)
                .where(Project.id == project_id)
                .options(
                    selectinload(Project.conversations).selectinload(Conversation.messages),
                    selectinload(Project.workflow_runs).selectinload(WorkflowRun.events),
                    selectinload(Project.workflow_runs).selectinload(WorkflowRun.invocations),
                    selectinload(Project.artifacts)
                    .selectinload(Artifact.versions)
                    .joinedload(ArtifactVersion.created_by_invocation),
                )
            )
            if project is None:
                raise WorkspaceProjectNotFoundError(str(project_id))
            return ProjectWorkspaceRecord(
                project=_project_summary(project),
                conversations=tuple(
                    _conversation_record(conversation)
                    for conversation in sorted(
                        project.conversations,
                        key=lambda item: (item.created_at, str(item.id)),
                    )
                ),
                workflow_runs=tuple(
                    _workflow_run_record(workflow_run)
                    for workflow_run in sorted(
                        project.workflow_runs,
                        key=lambda item: (item.updated_at, str(item.id)),
                        reverse=True,
                    )
                ),
                artifacts=tuple(
                    _artifact_record(artifact)
                    for artifact in sorted(
                        project.artifacts,
                        key=lambda item: (
                            item.artifact_type != "story_blueprint",
                            item.title.casefold(),
                            str(item.id),
                        ),
                    )
                ),
            )

    def get_artifact_version(
        self,
        artifact_version_id: UUID,
    ) -> ArtifactVersionDetailRecord:
        """Load full immutable content, lineage, provenance, and evaluations."""
        with self._session_factory() as session:
            version = session.scalar(
                select(ArtifactVersion)
                .where(ArtifactVersion.id == artifact_version_id)
                .options(
                    joinedload(ArtifactVersion.created_by_invocation),
                    joinedload(ArtifactVersion.artifact)
                    .selectinload(Artifact.versions)
                    .joinedload(ArtifactVersion.created_by_invocation),
                    selectinload(ArtifactVersion.evaluations),
                )
            )
            if version is None:
                raise WorkspaceArtifactVersionNotFoundError(str(artifact_version_id))
            return ArtifactVersionDetailRecord(
                artifact=_artifact_record(version.artifact),
                selected_version=_version_summary(version),
                content=dict(version.content),
                content_sha256=version.content_sha256,
                evaluations=tuple(
                    _evaluation_record(evaluation)
                    for evaluation in sorted(
                        version.evaluations,
                        key=lambda item: (item.created_at, str(item.id)),
                        reverse=True,
                    )
                ),
            )


def _project_summary(project: Project) -> ProjectSummaryRecord:
    latest_run = max(
        project.workflow_runs,
        key=lambda item: (item.updated_at, str(item.id)),
        default=None,
    )
    return ProjectSummaryRecord(
        id=project.id,
        name=project.name,
        description=project.description,
        story_format=project.story_format,
        status=project.status.value,
        updated_at=project.updated_at,
        conversation_count=len(project.conversations),
        artifact_count=len(project.artifacts),
        latest_workflow_run_id=latest_run.id if latest_run is not None else None,
        latest_workflow_status=(latest_run.status.value if latest_run is not None else None),
    )


def _conversation_record(conversation: Conversation) -> ConversationRecord:
    return ConversationRecord(
        id=conversation.id,
        title=conversation.title,
        status=conversation.status.value,
        messages=tuple(
            MessageRecord(
                id=message.id,
                workflow_run_id=message.workflow_run_id,
                sequence_number=message.sequence_number,
                role=message.role.value,
                content=message.content,
                created_at=message.created_at,
            )
            for message in sorted(
                conversation.messages,
                key=lambda item: item.sequence_number,
            )
        ),
    )


def _workflow_run_record(workflow_run: WorkflowRun) -> WorkflowRunRecord:
    return WorkflowRunRecord(
        id=workflow_run.id,
        parent_workflow_run_id=workflow_run.parent_workflow_run_id,
        workflow_name=workflow_run.workflow_name,
        graph_version=workflow_run.graph_version,
        status=workflow_run.status.value,
        pause_reason=(
            workflow_run.pause_reason.value if workflow_run.pause_reason is not None else None
        ),
        current_node=workflow_run.current_node,
        active_interrupt_id=(
            _active_interrupt_id(workflow_run.events)
            if workflow_run.pause_reason is RunPauseReason.HUMAN_APPROVAL
            else None
        ),
        started_at=workflow_run.started_at,
        completed_at=workflow_run.completed_at,
        updated_at=workflow_run.updated_at,
        error_code=workflow_run.error_code,
        error_message=workflow_run.error_message,
        budget=RunBudget.from_data(
            workflow_run.budget,
            default_max_graph_steps=DEFAULT_MAX_GRAPH_STEPS,
        ).to_data(),
        usage=run_usage(workflow_run).to_data(),
        retryable_nodes=(
            tuple(node.value for node in BLUEPRINT_RETRYABLE_NODES)
            if workflow_run.workflow_name == STORY_BLUEPRINT_WORKFLOW_NAME
            else ()
        ),
    )


def _active_interrupt_id(events: list[WorkflowEvent]) -> str | None:
    for event in reversed(events):
        if event.event_type != "workflow.awaiting_approval":
            continue
        interrupt_id = event.payload.get("interrupt_id")
        return interrupt_id if isinstance(interrupt_id, str) else None
    return None


def _artifact_record(artifact: Artifact) -> ArtifactRecord:
    versions = tuple(
        _version_summary(version)
        for version in sorted(
            artifact.versions,
            key=lambda item: item.version_number,
            reverse=True,
        )
    )
    return ArtifactRecord(
        id=artifact.id,
        artifact_key=artifact.artifact_key,
        artifact_type=artifact.artifact_type,
        title=artifact.title,
        status=artifact.status.value,
        active_version_id=versions[0].id if versions else None,
        versions=versions,
    )


def _version_summary(version: ArtifactVersion) -> ArtifactVersionSummaryRecord:
    invocation = version.created_by_invocation
    return ArtifactVersionSummaryRecord(
        id=version.id,
        version_number=version.version_number,
        parent_version_id=version.parent_version_id,
        schema_version=version.schema_version,
        change_summary=version.change_summary,
        created_at=version.created_at,
        specialist_role=invocation.specialist_role if invocation is not None else None,
        provider=invocation.provider if invocation is not None else None,
        model_identifier=invocation.model_identifier if invocation is not None else None,
    )


def _evaluation_record(evaluation: Evaluation) -> EvaluationRecord:
    return EvaluationRecord(
        id=evaluation.id,
        rubric_name=evaluation.rubric_name,
        rubric_version=evaluation.rubric_version,
        scores=dict(evaluation.scores),
        weighted_score=evaluation.weighted_score,
        summary=evaluation.summary,
        created_at=evaluation.created_at,
    )
