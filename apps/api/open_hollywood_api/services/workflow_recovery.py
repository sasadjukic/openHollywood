"""Reconcile provider calls whose owning execution has already ended."""

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from open_hollywood_api.persistence.models import AgentInvocation, InvocationStatus


def reconcile_interrupted_invocations(session: Session, workflow_run_id: UUID) -> tuple[UUID, ...]:
    """Close orphaned calls without inventing their provider outcome or cost."""
    interrupted = session.scalars(
        select(AgentInvocation).where(
            AgentInvocation.workflow_run_id == workflow_run_id,
            AgentInvocation.status == InvocationStatus.RUNNING,
        )
    ).all()
    detected_at = datetime.now(UTC)
    for invocation in interrupted:
        invocation.status = InvocationStatus.FAILED
        invocation.completed_at = detected_at
        invocation.error_code = "interrupted_execution"
        invocation.error_message = "The previous process ended before recording a terminal result."
        invocation.request_settings = {
            **invocation.request_settings,
            "failure_layer": "interrupted_execution",
            "interruption": {
                "detected_at": detected_at.isoformat(),
                "completed_at_basis": "recovery_detection_not_provider_completion",
                "provider_outcome": "unknown",
            },
        }
    return tuple(invocation.id for invocation in interrupted)
