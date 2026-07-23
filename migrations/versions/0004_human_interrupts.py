"""Add durable human decisions and workflow fork lineage.

Revision ID: 0004
Revises: 0003
Create Date: 2026-07-23
"""

from collections.abc import Sequence
from datetime import datetime

import sqlalchemy as sa
from alembic import op

revision: str = "0004"
down_revision: str | None = "0003"
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
    """Persist idempotent interrupt decisions and parent/child run lineage."""
    with op.batch_alter_table("workflow_runs") as batch:
        batch.add_column(sa.Column("parent_workflow_run_id", sa.Uuid(), nullable=True))
        batch.add_column(sa.Column("forked_from_checkpoint_id", sa.String(200), nullable=True))
        batch.create_foreign_key(
            op.f("fk_workflow_runs_parent_workflow_run_id_workflow_runs"),
            "workflow_runs",
            ["parent_workflow_run_id"],
            ["id"],
            ondelete="SET NULL",
        )
        batch.create_index(
            op.f("ix_workflow_runs_parent_workflow_run_id"),
            ["parent_workflow_run_id"],
        )

    op.create_table(
        "human_decisions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("workflow_run_id", sa.Uuid(), nullable=False),
        sa.Column("interrupt_id", sa.String(200), nullable=False),
        sa.Column("checkpoint_id", sa.String(200), nullable=False),
        sa.Column("action", sa.String(20), nullable=False),
        sa.Column("instruction", sa.Text(), nullable=True),
        sa.Column(
            "status",
            sa.Enum(
                "PENDING",
                "APPLIED",
                "FAILED",
                name="human_decision_status",
                native_enum=False,
                create_constraint=True,
            ),
            nullable=False,
        ),
        sa.Column("resulting_workflow_run_id", sa.Uuid(), nullable=True),
        sa.Column("applied_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        *_timestamps(),
        sa.CheckConstraint(
            "action IN ('approve', 'revise', 'reject', 'fork')",
            name=op.f("ck_human_decisions_human_decision_action"),
        ),
        sa.ForeignKeyConstraint(
            ["resulting_workflow_run_id"],
            ["workflow_runs.id"],
            name=op.f("fk_human_decisions_resulting_workflow_run_id_workflow_runs"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["workflow_run_id"],
            ["workflow_runs.id"],
            name=op.f("fk_human_decisions_workflow_run_id_workflow_runs"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_human_decisions")),
        sa.UniqueConstraint(
            "workflow_run_id",
            "interrupt_id",
            name=op.f("uq_human_decisions_workflow_run_id"),
        ),
    )
    op.create_index(
        op.f("ix_human_decisions_resulting_workflow_run_id"),
        "human_decisions",
        ["resulting_workflow_run_id"],
    )
    op.create_index(
        op.f("ix_human_decisions_workflow_run_id"),
        "human_decisions",
        ["workflow_run_id"],
    )


def downgrade() -> None:
    """Remove human decisions and fork lineage."""
    op.drop_index(
        op.f("ix_human_decisions_workflow_run_id"),
        table_name="human_decisions",
    )
    op.drop_index(
        op.f("ix_human_decisions_resulting_workflow_run_id"),
        table_name="human_decisions",
    )
    op.drop_table("human_decisions")

    with op.batch_alter_table("workflow_runs") as batch:
        batch.drop_index(op.f("ix_workflow_runs_parent_workflow_run_id"))
        batch.drop_constraint(
            op.f("fk_workflow_runs_parent_workflow_run_id_workflow_runs"),
            type_="foreignkey",
        )
        batch.drop_column("forked_from_checkpoint_id")
        batch.drop_column("parent_workflow_run_id")
