"""FastAPI application-service dependencies."""

from fastapi import HTTPException, Request, status

from open_hollywood_api.services.workflow_events import WorkflowEventStore


def get_workflow_event_store(request: Request) -> WorkflowEventStore:
    """Return the app-owned event store or report an unavailable database."""
    event_store = getattr(request.app.state, "workflow_event_store", None)
    if not isinstance(event_store, WorkflowEventStore):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Workflow event storage is unavailable",
        )
    return event_store
