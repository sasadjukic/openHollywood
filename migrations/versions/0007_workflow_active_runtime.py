"""Persist active workflow runtime independently from paused elapsed time.

Revision ID: 0007
Revises: 0006
Create Date: 2026-08-10
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0007"
down_revision: str | None = "0006"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add the durable accumulator and currently open execution interval."""
    op.add_column(
        "workflow_runs",
        sa.Column("active_started_at", sa.DateTime(timezone=True)),
    )
    op.add_column(
        "workflow_runs",
        sa.Column(
            "active_elapsed_seconds",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
    )


def downgrade() -> None:
    """Remove active-runtime accounting fields."""
    op.drop_column("workflow_runs", "active_elapsed_seconds")
    op.drop_column("workflow_runs", "active_started_at")
