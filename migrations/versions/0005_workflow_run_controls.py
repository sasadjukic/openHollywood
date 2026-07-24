"""Add durable workflow run controls and pause reasons.

Revision ID: 0005
Revises: 0004
Create Date: 2026-07-24
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0005"
down_revision: str | None = "0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Persist idempotent controls without placing commands in checkpoints."""
    with op.batch_alter_table("workflow_runs") as batch:
        batch.add_column(
            sa.Column(
                "pause_reason",
                sa.Enum(
                    "USER",
                    "BUDGET",
                    "HUMAN_APPROVAL",
                    name="run_pause_reason",
                    native_enum=False,
                    create_constraint=True,
                ),
                nullable=True,
            )
        )
    op.execute(
        sa.text("UPDATE workflow_runs SET pause_reason = 'HUMAN_APPROVAL' WHERE status = 'PAUSED'")
    )
    op.create_table(
        "workflow_run_controls",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("workflow_run_id", sa.Uuid(), nullable=False),
        sa.Column(
            "action",
            sa.Enum(
                "PAUSE",
                "RESUME",
                "STOP",
                "RETRY_FROM_NODE",
                "UPDATE_BUDGET",
                name="run_control_action",
                native_enum=False,
                create_constraint=True,
            ),
            nullable=False,
        ),
        sa.Column("target_node", sa.String(length=100), nullable=True),
        sa.Column("budget_updates", sa.JSON(), nullable=True),
        sa.Column(
            "status",
            sa.Enum(
                "PENDING",
                "APPLIED",
                "FAILED",
                name="run_control_status",
                native_enum=False,
                create_constraint=True,
            ),
            nullable=False,
        ),
        sa.Column("checkpoint_id", sa.String(length=200), nullable=True),
        sa.Column("resulting_workflow_run_id", sa.Uuid(), nullable=True),
        sa.Column("applied_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
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
        sa.ForeignKeyConstraint(
            ["resulting_workflow_run_id"],
            ["workflow_runs.id"],
            name=op.f("fk_workflow_run_controls_resulting_workflow_run_id_workflow_runs"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["workflow_run_id"],
            ["workflow_runs.id"],
            name=op.f("fk_workflow_run_controls_workflow_run_id_workflow_runs"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_workflow_run_controls")),
    )
    op.create_index(
        op.f("ix_workflow_run_controls_resulting_workflow_run_id"),
        "workflow_run_controls",
        ["resulting_workflow_run_id"],
    )
    op.create_index(
        op.f("ix_workflow_run_controls_workflow_run_id"),
        "workflow_run_controls",
        ["workflow_run_id"],
    )


def downgrade() -> None:
    """Remove run-control commands and pause reasons."""
    op.drop_index(
        op.f("ix_workflow_run_controls_workflow_run_id"),
        table_name="workflow_run_controls",
    )
    op.drop_index(
        op.f("ix_workflow_run_controls_resulting_workflow_run_id"),
        table_name="workflow_run_controls",
    )
    op.drop_table("workflow_run_controls")
    with op.batch_alter_table("workflow_runs") as batch:
        batch.drop_constraint(
            op.f("ck_workflow_runs_run_pause_reason"),
            type_="check",
        )
        batch.drop_column(
            "pause_reason",
            existing_type=sa.Enum(
                "USER",
                "BUDGET",
                "HUMAN_APPROVAL",
                name="run_pause_reason",
                native_enum=False,
                create_constraint=True,
            ),
        )
