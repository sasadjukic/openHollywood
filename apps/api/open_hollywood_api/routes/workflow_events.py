"""Resumable workflow event replay and Server-Sent Event routes."""

from typing import Annotated
from uuid import UUID

import anyio
from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request, status
from fastapi.responses import StreamingResponse

from open_hollywood_api.dependencies import get_workflow_event_store
from open_hollywood_api.event_models import WorkflowEventPage
from open_hollywood_api.event_stream import stream_workflow_events
from open_hollywood_api.services.workflow_events import (
    WorkflowEventStore,
    WorkflowRunNotFoundError,
)

router = APIRouter(prefix="/workflow-runs/{workflow_run_id}/events", tags=["workflow-events"])
EventStoreDependency = Annotated[WorkflowEventStore, Depends(get_workflow_event_store)]


async def _require_workflow_run(event_store: WorkflowEventStore, workflow_run_id: UUID) -> None:
    exists = await anyio.to_thread.run_sync(event_store.workflow_run_exists, workflow_run_id)
    if not exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow run not found",
        )


@router.get(
    "",
    operation_id="listWorkflowRunEvents",
    response_model=WorkflowEventPage,
    responses={404: {"description": "Workflow run not found"}},
    summary="Replay workflow events after a durable cursor",
)
async def list_workflow_run_events(
    workflow_run_id: UUID,
    event_store: EventStoreDependency,
    after: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
) -> WorkflowEventPage:
    """Return an exclusive-cursor page ordered by global event ID."""
    try:
        page = await anyio.to_thread.run_sync(
            lambda: event_store.page_after(workflow_run_id, after, limit=limit)
        )
    except WorkflowRunNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow run not found",
        ) from error
    return WorkflowEventPage.from_record(page)


@router.get(
    "/stream",
    operation_id="streamWorkflowRunEvents",
    response_class=StreamingResponse,
    responses={
        200: {
            "description": "SSE frames whose data field is a WorkflowEventEnvelope JSON object.",
            "content": {"text/event-stream": {"schema": {"type": "string"}}},
        },
        404: {"description": "Workflow run not found"},
    },
    summary="Stream workflow events from a durable cursor",
)
async def stream_workflow_run_event_route(
    request: Request,
    workflow_run_id: UUID,
    event_store: EventStoreDependency,
    after: Annotated[int, Query(ge=0)] = 0,
    last_event_id: Annotated[int | None, Header(alias="Last-Event-ID", ge=0)] = None,
    follow: Annotated[bool, Query()] = True,
) -> StreamingResponse:
    """Replay missed events, then follow new rows until the client disconnects."""
    await _require_workflow_run(event_store, workflow_run_id)
    cursor = max(after, last_event_id or 0)
    return StreamingResponse(
        stream_workflow_events(
            request,
            event_store,
            workflow_run_id,
            cursor,
            follow=follow,
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-store",
            "X-Accel-Buffering": "no",
        },
    )
