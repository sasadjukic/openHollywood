"""Relational persistence records for the Open Hollywood v0.1 domain."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4

from open_hollywood_engine.workflows import (
    RunControlAction,
    RunControlStatus,
    RunPauseReason,
)
from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    LargeBinary,
    Numeric,
    String,
    Table,
    Text,
    UniqueConstraint,
    Uuid,
    event,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from open_hollywood_api.persistence.base import Base as Base

# LangGraph owns the row format and access patterns for these infrastructure
# tables. Declaring them in application metadata keeps Alembic drift checks
# authoritative without leaking checkpoint types into domain models.
langgraph_checkpoints = Table(
    "checkpoints",
    Base.metadata,
    Column("thread_id", Text, primary_key=True),
    Column("checkpoint_ns", Text, primary_key=True, server_default=""),
    Column("checkpoint_id", Text, primary_key=True),
    Column("parent_checkpoint_id", Text),
    Column("type", Text),
    Column("checkpoint", LargeBinary),
    Column("metadata", LargeBinary),
)

langgraph_writes = Table(
    "writes",
    Base.metadata,
    Column("thread_id", Text, primary_key=True),
    Column("checkpoint_ns", Text, primary_key=True, server_default=""),
    Column("checkpoint_id", Text, primary_key=True),
    Column("task_id", Text, primary_key=True),
    Column("idx", Integer, primary_key=True),
    Column("channel", Text, nullable=False),
    Column("type", Text),
    Column("value", LargeBinary),
)


def utc_now() -> datetime:
    """Return an aware UTC timestamp for application-side defaults."""
    return datetime.now(UTC)


class ProjectStatus(StrEnum):
    """Lifecycle state for a story project."""

    ACTIVE = "active"
    ARCHIVED = "archived"


class ConversationStatus(StrEnum):
    """Lifecycle state for a project conversation."""

    ACTIVE = "active"
    ARCHIVED = "archived"


class MessageRole(StrEnum):
    """Authorship category for a persisted message."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ArtifactStatus(StrEnum):
    """Review state for an artifact and its version lineage."""

    DRAFT = "draft"
    APPROVED = "approved"
    STALE = "stale"
    ARCHIVED = "archived"


class RunStatus(StrEnum):
    """Durable workflow execution state."""

    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


class HumanDecisionStatus(StrEnum):
    """Application state for one idempotent interrupt resolution."""

    PENDING = "pending"
    APPLIED = "applied"
    FAILED = "failed"


class InvocationStatus(StrEnum):
    """Durable state for one budgeted model call."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ModelProfileMode(StrEnum):
    """Inference placement represented by a model profile."""

    LOCAL = "local"
    CLOUD = "cloud"
    HYBRID = "hybrid"


agent_invocation_inputs = Table(
    "agent_invocation_inputs",
    Base.metadata,
    Column(
        "agent_invocation_id",
        Uuid,
        ForeignKey("agent_invocations.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "artifact_version_id",
        Uuid,
        ForeignKey("artifact_versions.id", ondelete="RESTRICT"),
        primary_key=True,
    ),
)


class TimestampedRecord:
    """Creation and modification timestamps for mutable records."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        server_default=func.current_timestamp(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        server_default=func.current_timestamp(),
        nullable=False,
    )


class Project(TimestampedRecord, Base):
    """Top-level local workspace for one story."""

    __tablename__ = "projects"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    story_format: Mapped[str] = mapped_column(String(50), default="short_prose", nullable=False)
    status: Mapped[ProjectStatus] = mapped_column(
        Enum(
            ProjectStatus,
            name="project_status",
            native_enum=False,
            create_constraint=True,
            validate_strings=True,
        ),
        default=ProjectStatus.ACTIVE,
        nullable=False,
    )
    settings: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    conversations: Mapped[list[Conversation]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    artifacts: Mapped[list[Artifact]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    workflow_runs: Mapped[list[WorkflowRun]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    evaluations: Mapped[list[Evaluation]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )


class Conversation(TimestampedRecord, Base):
    """Ordered message thread scoped to a project."""

    __tablename__ = "conversations"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    project_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("projects.id", ondelete="CASCADE"), index=True, nullable=False
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[ConversationStatus] = mapped_column(
        Enum(
            ConversationStatus,
            name="conversation_status",
            native_enum=False,
            create_constraint=True,
            validate_strings=True,
        ),
        default=ConversationStatus.ACTIVE,
        nullable=False,
    )

    project: Mapped[Project] = relationship(back_populates="conversations")
    messages: Mapped[list[Message]] = relationship(
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="Message.sequence_number",
    )
    workflow_runs: Mapped[list[WorkflowRun]] = relationship(back_populates="conversation")


class ModelProfile(TimestampedRecord, Base):
    """Secret-free local, cloud, or hybrid role-to-model configuration."""

    __tablename__ = "model_profiles"
    __table_args__ = (UniqueConstraint("name"),)

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    mode: Mapped[ModelProfileMode] = mapped_column(
        Enum(
            ModelProfileMode,
            name="model_profile_mode",
            native_enum=False,
            create_constraint=True,
            validate_strings=True,
        ),
        nullable=False,
    )
    configuration: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    invocations: Mapped[list[AgentInvocation]] = relationship(back_populates="model_profile")


class WorkflowRun(TimestampedRecord, Base):
    """Durable execution record for a registered workflow graph."""

    __tablename__ = "workflow_runs"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    project_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("projects.id", ondelete="CASCADE"), index=True, nullable=False
    )
    conversation_id: Mapped[UUID | None] = mapped_column(
        Uuid, ForeignKey("conversations.id", ondelete="SET NULL"), index=True
    )
    parent_workflow_run_id: Mapped[UUID | None] = mapped_column(
        Uuid, ForeignKey("workflow_runs.id", ondelete="SET NULL"), index=True
    )
    forked_from_checkpoint_id: Mapped[str | None] = mapped_column(String(200))
    workflow_name: Mapped[str] = mapped_column(String(100), nullable=False)
    graph_version: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[RunStatus] = mapped_column(
        Enum(
            RunStatus,
            name="run_status",
            native_enum=False,
            create_constraint=True,
            validate_strings=True,
        ),
        default=RunStatus.PENDING,
        nullable=False,
    )
    current_node: Mapped[str | None] = mapped_column(String(100))
    checkpoint_id: Mapped[str | None] = mapped_column(String(200))
    input_state: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    budget: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    pause_reason: Mapped[RunPauseReason | None] = mapped_column(
        Enum(
            RunPauseReason,
            name="run_pause_reason",
            native_enum=False,
            create_constraint=True,
            validate_strings=True,
        )
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    error_code: Mapped[str | None] = mapped_column(String(100))
    error_message: Mapped[str | None] = mapped_column(Text)

    project: Mapped[Project] = relationship(back_populates="workflow_runs")
    conversation: Mapped[Conversation | None] = relationship(back_populates="workflow_runs")
    invocations: Mapped[list[AgentInvocation]] = relationship(
        back_populates="workflow_run", cascade="all, delete-orphan"
    )
    messages: Mapped[list[Message]] = relationship(back_populates="workflow_run")
    events: Mapped[list[WorkflowEvent]] = relationship(
        back_populates="workflow_run",
        order_by="WorkflowEvent.id",
        passive_deletes=True,
    )
    parent_workflow_run: Mapped[WorkflowRun | None] = relationship(
        remote_side="WorkflowRun.id",
        back_populates="child_workflow_runs",
        foreign_keys=[parent_workflow_run_id],
    )
    child_workflow_runs: Mapped[list[WorkflowRun]] = relationship(
        back_populates="parent_workflow_run",
        foreign_keys=[parent_workflow_run_id],
    )
    human_decisions: Mapped[list[HumanDecision]] = relationship(
        back_populates="workflow_run",
        cascade="all, delete-orphan",
        foreign_keys="HumanDecision.workflow_run_id",
    )
    control_commands: Mapped[list[WorkflowRunControl]] = relationship(
        back_populates="workflow_run",
        cascade="all, delete-orphan",
        foreign_keys="WorkflowRunControl.workflow_run_id",
    )


class WorkflowRunControl(TimestampedRecord, Base):
    """Durable idempotent pause, resume, stop, retry, or budget command."""

    __tablename__ = "workflow_run_controls"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    workflow_run_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("workflow_runs.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    action: Mapped[RunControlAction] = mapped_column(
        Enum(
            RunControlAction,
            name="run_control_action",
            native_enum=False,
            create_constraint=True,
            validate_strings=True,
        ),
        nullable=False,
    )
    target_node: Mapped[str | None] = mapped_column(String(100))
    budget_updates: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    status: Mapped[RunControlStatus] = mapped_column(
        Enum(
            RunControlStatus,
            name="run_control_status",
            native_enum=False,
            create_constraint=True,
            validate_strings=True,
        ),
        default=RunControlStatus.PENDING,
        nullable=False,
    )
    checkpoint_id: Mapped[str | None] = mapped_column(String(200))
    resulting_workflow_run_id: Mapped[UUID | None] = mapped_column(
        Uuid,
        ForeignKey("workflow_runs.id", ondelete="SET NULL"),
        index=True,
    )
    applied_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    error_message: Mapped[str | None] = mapped_column(Text)

    workflow_run: Mapped[WorkflowRun] = relationship(
        back_populates="control_commands",
        foreign_keys=[workflow_run_id],
    )
    resulting_workflow_run: Mapped[WorkflowRun | None] = relationship(
        foreign_keys=[resulting_workflow_run_id]
    )


class HumanDecision(TimestampedRecord, Base):
    """Durable, idempotent resolution of one LangGraph human interrupt."""

    __tablename__ = "human_decisions"
    __table_args__ = (
        UniqueConstraint("workflow_run_id", "interrupt_id"),
        CheckConstraint(
            "action IN ('approve', 'revise', 'reject', 'fork')",
            name="human_decision_action",
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    workflow_run_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("workflow_runs.id", ondelete="CASCADE"), index=True, nullable=False
    )
    interrupt_id: Mapped[str] = mapped_column(String(200), nullable=False)
    checkpoint_id: Mapped[str] = mapped_column(String(200), nullable=False)
    action: Mapped[str] = mapped_column(String(20), nullable=False)
    instruction: Mapped[str | None] = mapped_column(Text)
    status: Mapped[HumanDecisionStatus] = mapped_column(
        Enum(
            HumanDecisionStatus,
            name="human_decision_status",
            native_enum=False,
            create_constraint=True,
            validate_strings=True,
        ),
        default=HumanDecisionStatus.PENDING,
        nullable=False,
    )
    resulting_workflow_run_id: Mapped[UUID | None] = mapped_column(
        Uuid, ForeignKey("workflow_runs.id", ondelete="SET NULL"), index=True
    )
    applied_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    error_message: Mapped[str | None] = mapped_column(Text)

    workflow_run: Mapped[WorkflowRun] = relationship(
        back_populates="human_decisions",
        foreign_keys=[workflow_run_id],
    )
    resulting_workflow_run: Mapped[WorkflowRun | None] = relationship(
        foreign_keys=[resulting_workflow_run_id]
    )


class AgentInvocation(Base):
    """Observable, reproducible record of one model call."""

    __tablename__ = "agent_invocations"
    __table_args__ = (
        CheckConstraint("input_tokens >= 0", name="input_tokens_nonnegative"),
        CheckConstraint("output_tokens >= 0", name="output_tokens_nonnegative"),
        CheckConstraint("retry_count >= 0", name="retry_count_nonnegative"),
        CheckConstraint("estimated_cost_usd >= 0", name="cost_nonnegative"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    workflow_run_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("workflow_runs.id", ondelete="CASCADE"), index=True, nullable=False
    )
    model_profile_id: Mapped[UUID | None] = mapped_column(
        Uuid, ForeignKey("model_profiles.id", ondelete="SET NULL"), index=True
    )
    specialist_role: Mapped[str] = mapped_column(String(100), nullable=False)
    provider: Mapped[str] = mapped_column(String(100), nullable=False)
    model_identifier: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[InvocationStatus] = mapped_column(
        Enum(
            InvocationStatus,
            name="invocation_status",
            native_enum=False,
            create_constraint=True,
            validate_strings=True,
        ),
        default=InvocationStatus.PENDING,
        nullable=False,
    )
    request_settings: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    prompt_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    prompt_text: Mapped[str | None] = mapped_column(Text)
    input_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    output_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    estimated_cost_usd: Mapped[Decimal] = mapped_column(
        Numeric(12, 6), default=Decimal("0"), nullable=False
    )
    latency_ms: Mapped[int | None] = mapped_column(Integer)
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    fallback_history: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON, default=list, nullable=False
    )
    schema_validation_succeeded: Mapped[bool | None] = mapped_column(Boolean)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        server_default=func.current_timestamp(),
        nullable=False,
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    error_code: Mapped[str | None] = mapped_column(String(100))
    error_message: Mapped[str | None] = mapped_column(Text)

    workflow_run: Mapped[WorkflowRun] = relationship(back_populates="invocations")
    model_profile: Mapped[ModelProfile | None] = relationship(back_populates="invocations")
    input_versions: Mapped[list[ArtifactVersion]] = relationship(
        secondary=agent_invocation_inputs,
        back_populates="input_to_invocations",
    )
    output_versions: Mapped[list[ArtifactVersion]] = relationship(
        back_populates="created_by_invocation",
        foreign_keys="ArtifactVersion.created_by_invocation_id",
    )
    messages: Mapped[list[Message]] = relationship(back_populates="agent_invocation")
    evaluations: Mapped[list[Evaluation]] = relationship(back_populates="evaluator_invocation")


class Message(Base):
    """One immutable-position message in a conversation."""

    __tablename__ = "messages"
    __table_args__ = (
        UniqueConstraint("conversation_id", "sequence_number"),
        CheckConstraint("sequence_number >= 1", name="sequence_number_positive"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    conversation_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("conversations.id", ondelete="CASCADE"), index=True, nullable=False
    )
    workflow_run_id: Mapped[UUID | None] = mapped_column(
        Uuid, ForeignKey("workflow_runs.id", ondelete="SET NULL"), index=True
    )
    agent_invocation_id: Mapped[UUID | None] = mapped_column(
        Uuid, ForeignKey("agent_invocations.id", ondelete="SET NULL"), index=True
    )
    sequence_number: Mapped[int] = mapped_column(Integer, nullable=False)
    role: Mapped[MessageRole] = mapped_column(
        Enum(
            MessageRole,
            name="message_role",
            native_enum=False,
            create_constraint=True,
            validate_strings=True,
        ),
        nullable=False,
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    attributes: Mapped[dict[str, Any]] = mapped_column(
        "metadata", JSON, default=dict, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        server_default=func.current_timestamp(),
        nullable=False,
    )

    conversation: Mapped[Conversation] = relationship(back_populates="messages")
    workflow_run: Mapped[WorkflowRun | None] = relationship(back_populates="messages")
    agent_invocation: Mapped[AgentInvocation | None] = relationship(back_populates="messages")


class Artifact(TimestampedRecord, Base):
    """Logical story artifact with an append-only version lineage."""

    __tablename__ = "artifacts"
    __table_args__ = (UniqueConstraint("project_id", "artifact_key"),)

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    project_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("projects.id", ondelete="CASCADE"), index=True, nullable=False
    )
    artifact_key: Mapped[str] = mapped_column(String(150), nullable=False)
    artifact_type: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[ArtifactStatus] = mapped_column(
        Enum(
            ArtifactStatus,
            name="artifact_status",
            native_enum=False,
            create_constraint=True,
            validate_strings=True,
        ),
        default=ArtifactStatus.DRAFT,
        nullable=False,
    )

    project: Mapped[Project] = relationship(back_populates="artifacts")
    versions: Mapped[list[ArtifactVersion]] = relationship(
        back_populates="artifact",
        cascade="all, delete-orphan",
        order_by="ArtifactVersion.version_number",
    )


class ArtifactVersion(Base):
    """Immutable content snapshot with explicit parent and creator lineage."""

    __tablename__ = "artifact_versions"
    __table_args__ = (
        UniqueConstraint("artifact_id", "version_number"),
        CheckConstraint("version_number >= 1", name="version_number_positive"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    artifact_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("artifacts.id", ondelete="CASCADE"), index=True, nullable=False
    )
    parent_version_id: Mapped[UUID | None] = mapped_column(
        Uuid, ForeignKey("artifact_versions.id", ondelete="RESTRICT"), index=True
    )
    created_by_invocation_id: Mapped[UUID | None] = mapped_column(
        Uuid, ForeignKey("agent_invocations.id", ondelete="SET NULL"), index=True
    )
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    schema_version: Mapped[str] = mapped_column(String(50), nullable=False)
    content: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    content_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    change_summary: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        server_default=func.current_timestamp(),
        nullable=False,
    )

    artifact: Mapped[Artifact] = relationship(back_populates="versions")
    parent_version: Mapped[ArtifactVersion | None] = relationship(
        remote_side="ArtifactVersion.id", back_populates="child_versions"
    )
    child_versions: Mapped[list[ArtifactVersion]] = relationship(back_populates="parent_version")
    created_by_invocation: Mapped[AgentInvocation | None] = relationship(
        back_populates="output_versions", foreign_keys=[created_by_invocation_id]
    )
    input_to_invocations: Mapped[list[AgentInvocation]] = relationship(
        secondary=agent_invocation_inputs,
        back_populates="input_versions",
    )
    evaluations: Mapped[list[Evaluation]] = relationship(back_populates="artifact_version")


class Evaluation(Base):
    """Structured rubric result for an artifact version or workflow run."""

    __tablename__ = "evaluations"
    __table_args__ = (
        CheckConstraint(
            "weighted_score IS NULL OR (weighted_score >= 0 AND weighted_score <= 100)",
            name="weighted_score_range",
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    project_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("projects.id", ondelete="CASCADE"), index=True, nullable=False
    )
    workflow_run_id: Mapped[UUID | None] = mapped_column(
        Uuid, ForeignKey("workflow_runs.id", ondelete="SET NULL"), index=True
    )
    artifact_version_id: Mapped[UUID | None] = mapped_column(
        Uuid, ForeignKey("artifact_versions.id", ondelete="SET NULL"), index=True
    )
    evaluator_invocation_id: Mapped[UUID | None] = mapped_column(
        Uuid, ForeignKey("agent_invocations.id", ondelete="SET NULL"), index=True
    )
    rubric_name: Mapped[str] = mapped_column(String(100), nullable=False)
    rubric_version: Mapped[str] = mapped_column(String(50), nullable=False)
    scores: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    weighted_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    summary: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        server_default=func.current_timestamp(),
        nullable=False,
    )

    project: Mapped[Project] = relationship(back_populates="evaluations")
    workflow_run: Mapped[WorkflowRun | None] = relationship()
    artifact_version: Mapped[ArtifactVersion | None] = relationship(back_populates="evaluations")
    evaluator_invocation: Mapped[AgentInvocation | None] = relationship(
        back_populates="evaluations"
    )


class WorkflowEvent(Base):
    """Append-only, globally ordered event emitted by a workflow run."""

    __tablename__ = "workflow_events"
    __table_args__ = (Index("ix_workflow_events_workflow_run_id_id", "workflow_run_id", "id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    workflow_run_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("workflow_runs.id", ondelete="RESTRICT"), nullable=False
    )
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    source: Mapped[str | None] = mapped_column(String(100))
    schema_version: Mapped[str] = mapped_column(String(50), default="1", nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        server_default=func.current_timestamp(),
        nullable=False,
    )

    workflow_run: Mapped[WorkflowRun] = relationship(back_populates="events")


class ImmutableArtifactVersionError(RuntimeError):
    """Raised when application code attempts to mutate a version snapshot."""


@event.listens_for(ArtifactVersion, "before_update")
def _prevent_artifact_version_update(*_args: object) -> None:
    raise ImmutableArtifactVersionError(
        "ArtifactVersion rows are immutable; create a new version instead"
    )


class AppendOnlyWorkflowEventError(RuntimeError):
    """Raised when application code attempts to mutate or delete an event."""


@event.listens_for(WorkflowEvent, "before_update")
@event.listens_for(WorkflowEvent, "before_delete")
def _prevent_workflow_event_mutation(*_args: object) -> None:
    raise AppendOnlyWorkflowEventError("WorkflowEvent rows are append-only")
