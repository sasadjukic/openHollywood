"""Create the initial Open Hollywood persistence schema.

Revision ID: 0001
Revises: None
Create Date: 2026-07-21
"""

from collections.abc import Sequence
from datetime import datetime

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _timestamps() -> tuple[sa.Column[datetime], sa.Column[datetime]]:
    return (
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
    )


def upgrade() -> None:
    """Create project, workflow, invocation, artifact, and evaluation storage."""
    op.create_table(
        "projects",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("story_format", sa.String(length=50), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "ACTIVE",
                "ARCHIVED",
                name="project_status",
                native_enum=False,
                create_constraint=True,
            ),
            nullable=False,
        ),
        sa.Column("settings", sa.JSON(), nullable=False),
        *_timestamps(),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_projects")),
    )
    op.create_table(
        "model_profiles",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "mode",
            sa.Enum(
                "LOCAL",
                "CLOUD",
                "HYBRID",
                name="model_profile_mode",
                native_enum=False,
                create_constraint=True,
            ),
            nullable=False,
        ),
        sa.Column("configuration", sa.JSON(), nullable=False),
        sa.Column("is_default", sa.Boolean(), nullable=False),
        *_timestamps(),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_model_profiles")),
        sa.UniqueConstraint("name", name=op.f("uq_model_profiles_name")),
    )
    op.create_table(
        "conversations",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "ACTIVE",
                "ARCHIVED",
                name="conversation_status",
                native_enum=False,
                create_constraint=True,
            ),
            nullable=False,
        ),
        *_timestamps(),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["projects.id"],
            name=op.f("fk_conversations_project_id_projects"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_conversations")),
    )
    op.create_index(op.f("ix_conversations_project_id"), "conversations", ["project_id"])
    op.create_table(
        "workflow_runs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("conversation_id", sa.Uuid(), nullable=True),
        sa.Column("workflow_name", sa.String(length=100), nullable=False),
        sa.Column("graph_version", sa.String(length=50), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "PENDING",
                "RUNNING",
                "PAUSED",
                "SUCCEEDED",
                "FAILED",
                "CANCELLED",
                name="run_status",
                native_enum=False,
                create_constraint=True,
            ),
            nullable=False,
        ),
        sa.Column("current_node", sa.String(length=100), nullable=True),
        sa.Column("checkpoint_id", sa.String(length=200), nullable=True),
        sa.Column("input_state", sa.JSON(), nullable=False),
        sa.Column("budget", sa.JSON(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_code", sa.String(length=100), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        *_timestamps(),
        sa.ForeignKeyConstraint(
            ["conversation_id"],
            ["conversations.id"],
            name=op.f("fk_workflow_runs_conversation_id_conversations"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["projects.id"],
            name=op.f("fk_workflow_runs_project_id_projects"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_workflow_runs")),
    )
    op.create_index(op.f("ix_workflow_runs_conversation_id"), "workflow_runs", ["conversation_id"])
    op.create_index(op.f("ix_workflow_runs_project_id"), "workflow_runs", ["project_id"])
    op.create_table(
        "agent_invocations",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("workflow_run_id", sa.Uuid(), nullable=False),
        sa.Column("model_profile_id", sa.Uuid(), nullable=True),
        sa.Column("specialist_role", sa.String(length=100), nullable=False),
        sa.Column("provider", sa.String(length=100), nullable=False),
        sa.Column("model_identifier", sa.String(length=200), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "PENDING",
                "RUNNING",
                "SUCCEEDED",
                "FAILED",
                "CANCELLED",
                name="invocation_status",
                native_enum=False,
                create_constraint=True,
            ),
            nullable=False,
        ),
        sa.Column("request_settings", sa.JSON(), nullable=False),
        sa.Column("prompt_sha256", sa.String(length=64), nullable=False),
        sa.Column("prompt_text", sa.Text(), nullable=True),
        sa.Column("input_tokens", sa.Integer(), nullable=False),
        sa.Column("output_tokens", sa.Integer(), nullable=False),
        sa.Column("estimated_cost_usd", sa.Numeric(precision=12, scale=6), nullable=False),
        sa.Column("latency_ms", sa.Integer(), nullable=True),
        sa.Column("retry_count", sa.Integer(), nullable=False),
        sa.Column("fallback_history", sa.JSON(), nullable=False),
        sa.Column("schema_validation_succeeded", sa.Boolean(), nullable=True),
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_code", sa.String(length=100), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.CheckConstraint(
            "estimated_cost_usd >= 0", name=op.f("ck_agent_invocations_cost_nonnegative")
        ),
        sa.CheckConstraint(
            "input_tokens >= 0", name=op.f("ck_agent_invocations_input_tokens_nonnegative")
        ),
        sa.CheckConstraint(
            "output_tokens >= 0", name=op.f("ck_agent_invocations_output_tokens_nonnegative")
        ),
        sa.CheckConstraint(
            "retry_count >= 0", name=op.f("ck_agent_invocations_retry_count_nonnegative")
        ),
        sa.ForeignKeyConstraint(
            ["model_profile_id"],
            ["model_profiles.id"],
            name=op.f("fk_agent_invocations_model_profile_id_model_profiles"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["workflow_run_id"],
            ["workflow_runs.id"],
            name=op.f("fk_agent_invocations_workflow_run_id_workflow_runs"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_agent_invocations")),
    )
    op.create_index(
        op.f("ix_agent_invocations_model_profile_id"), "agent_invocations", ["model_profile_id"]
    )
    op.create_index(
        op.f("ix_agent_invocations_workflow_run_id"), "agent_invocations", ["workflow_run_id"]
    )
    op.create_table(
        "messages",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("conversation_id", sa.Uuid(), nullable=False),
        sa.Column("workflow_run_id", sa.Uuid(), nullable=True),
        sa.Column("agent_invocation_id", sa.Uuid(), nullable=True),
        sa.Column("sequence_number", sa.Integer(), nullable=False),
        sa.Column(
            "role",
            sa.Enum(
                "USER",
                "ASSISTANT",
                "SYSTEM",
                name="message_role",
                native_enum=False,
                create_constraint=True,
            ),
            nullable=False,
        ),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("metadata", sa.JSON(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "sequence_number >= 1", name=op.f("ck_messages_sequence_number_positive")
        ),
        sa.ForeignKeyConstraint(
            ["agent_invocation_id"],
            ["agent_invocations.id"],
            name=op.f("fk_messages_agent_invocation_id_agent_invocations"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["conversation_id"],
            ["conversations.id"],
            name=op.f("fk_messages_conversation_id_conversations"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["workflow_run_id"],
            ["workflow_runs.id"],
            name=op.f("fk_messages_workflow_run_id_workflow_runs"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_messages")),
        sa.UniqueConstraint(
            "conversation_id", "sequence_number", name=op.f("uq_messages_conversation_id")
        ),
    )
    op.create_index(op.f("ix_messages_agent_invocation_id"), "messages", ["agent_invocation_id"])
    op.create_index(op.f("ix_messages_conversation_id"), "messages", ["conversation_id"])
    op.create_index(op.f("ix_messages_workflow_run_id"), "messages", ["workflow_run_id"])
    op.create_table(
        "artifacts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("artifact_key", sa.String(length=150), nullable=False),
        sa.Column("artifact_type", sa.String(length=100), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "DRAFT",
                "APPROVED",
                "STALE",
                "ARCHIVED",
                name="artifact_status",
                native_enum=False,
                create_constraint=True,
            ),
            nullable=False,
        ),
        *_timestamps(),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["projects.id"],
            name=op.f("fk_artifacts_project_id_projects"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_artifacts")),
        sa.UniqueConstraint("project_id", "artifact_key", name=op.f("uq_artifacts_project_id")),
    )
    op.create_index(op.f("ix_artifacts_project_id"), "artifacts", ["project_id"])
    op.create_table(
        "artifact_versions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("artifact_id", sa.Uuid(), nullable=False),
        sa.Column("parent_version_id", sa.Uuid(), nullable=True),
        sa.Column("created_by_invocation_id", sa.Uuid(), nullable=True),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("schema_version", sa.String(length=50), nullable=False),
        sa.Column("content", sa.JSON(), nullable=False),
        sa.Column("content_sha256", sa.String(length=64), nullable=False),
        sa.Column("change_summary", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "version_number >= 1", name=op.f("ck_artifact_versions_version_number_positive")
        ),
        sa.ForeignKeyConstraint(
            ["artifact_id"],
            ["artifacts.id"],
            name=op.f("fk_artifact_versions_artifact_id_artifacts"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["created_by_invocation_id"],
            ["agent_invocations.id"],
            name=op.f("fk_artifact_versions_created_by_invocation_id_agent_invocations"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["parent_version_id"],
            ["artifact_versions.id"],
            name=op.f("fk_artifact_versions_parent_version_id_artifact_versions"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_artifact_versions")),
        sa.UniqueConstraint(
            "artifact_id", "version_number", name=op.f("uq_artifact_versions_artifact_id")
        ),
    )
    op.create_index(op.f("ix_artifact_versions_artifact_id"), "artifact_versions", ["artifact_id"])
    op.create_index(
        op.f("ix_artifact_versions_created_by_invocation_id"),
        "artifact_versions",
        ["created_by_invocation_id"],
    )
    op.create_index(
        op.f("ix_artifact_versions_parent_version_id"), "artifact_versions", ["parent_version_id"]
    )
    op.create_table(
        "agent_invocation_inputs",
        sa.Column("agent_invocation_id", sa.Uuid(), nullable=False),
        sa.Column("artifact_version_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(
            ["agent_invocation_id"],
            ["agent_invocations.id"],
            name=op.f("fk_agent_invocation_inputs_agent_invocation_id_agent_invocations"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["artifact_version_id"],
            ["artifact_versions.id"],
            name=op.f("fk_agent_invocation_inputs_artifact_version_id_artifact_versions"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint(
            "agent_invocation_id", "artifact_version_id", name=op.f("pk_agent_invocation_inputs")
        ),
    )
    op.create_table(
        "evaluations",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("workflow_run_id", sa.Uuid(), nullable=True),
        sa.Column("artifact_version_id", sa.Uuid(), nullable=True),
        sa.Column("evaluator_invocation_id", sa.Uuid(), nullable=True),
        sa.Column("rubric_name", sa.String(length=100), nullable=False),
        sa.Column("rubric_version", sa.String(length=50), nullable=False),
        sa.Column("scores", sa.JSON(), nullable=False),
        sa.Column("weighted_score", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "weighted_score IS NULL OR (weighted_score >= 0 AND weighted_score <= 100)",
            name=op.f("ck_evaluations_weighted_score_range"),
        ),
        sa.ForeignKeyConstraint(
            ["artifact_version_id"],
            ["artifact_versions.id"],
            name=op.f("fk_evaluations_artifact_version_id_artifact_versions"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["evaluator_invocation_id"],
            ["agent_invocations.id"],
            name=op.f("fk_evaluations_evaluator_invocation_id_agent_invocations"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["projects.id"],
            name=op.f("fk_evaluations_project_id_projects"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["workflow_run_id"],
            ["workflow_runs.id"],
            name=op.f("fk_evaluations_workflow_run_id_workflow_runs"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_evaluations")),
    )
    op.create_index(
        op.f("ix_evaluations_artifact_version_id"), "evaluations", ["artifact_version_id"]
    )
    op.create_index(
        op.f("ix_evaluations_evaluator_invocation_id"), "evaluations", ["evaluator_invocation_id"]
    )
    op.create_index(op.f("ix_evaluations_project_id"), "evaluations", ["project_id"])
    op.create_index(op.f("ix_evaluations_workflow_run_id"), "evaluations", ["workflow_run_id"])


def downgrade() -> None:
    """Drop the initial persistence schema in dependency order."""
    op.drop_index(op.f("ix_evaluations_workflow_run_id"), table_name="evaluations")
    op.drop_index(op.f("ix_evaluations_project_id"), table_name="evaluations")
    op.drop_index(op.f("ix_evaluations_evaluator_invocation_id"), table_name="evaluations")
    op.drop_index(op.f("ix_evaluations_artifact_version_id"), table_name="evaluations")
    op.drop_table("evaluations")
    op.drop_table("agent_invocation_inputs")
    op.drop_index(op.f("ix_artifact_versions_parent_version_id"), table_name="artifact_versions")
    op.drop_index(
        op.f("ix_artifact_versions_created_by_invocation_id"), table_name="artifact_versions"
    )
    op.drop_index(op.f("ix_artifact_versions_artifact_id"), table_name="artifact_versions")
    op.drop_table("artifact_versions")
    op.drop_index(op.f("ix_artifacts_project_id"), table_name="artifacts")
    op.drop_table("artifacts")
    op.drop_index(op.f("ix_messages_workflow_run_id"), table_name="messages")
    op.drop_index(op.f("ix_messages_conversation_id"), table_name="messages")
    op.drop_index(op.f("ix_messages_agent_invocation_id"), table_name="messages")
    op.drop_table("messages")
    op.drop_index(op.f("ix_agent_invocations_workflow_run_id"), table_name="agent_invocations")
    op.drop_index(op.f("ix_agent_invocations_model_profile_id"), table_name="agent_invocations")
    op.drop_table("agent_invocations")
    op.drop_index(op.f("ix_workflow_runs_project_id"), table_name="workflow_runs")
    op.drop_index(op.f("ix_workflow_runs_conversation_id"), table_name="workflow_runs")
    op.drop_table("workflow_runs")
    op.drop_index(op.f("ix_conversations_project_id"), table_name="conversations")
    op.drop_table("conversations")
    op.drop_table("model_profiles")
    op.drop_table("projects")
