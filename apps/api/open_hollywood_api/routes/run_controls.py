"""Workflow pause, resume, stop, retry, and budget command route."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from open_hollywood_api.dependencies import get_blueprint_workflow_service
from open_hollywood_api.run_control_models import (
    RunControlRequest,
    RunControlResponse,
)
from open_hollywood_api.services.blueprint_workflow import (
    BlueprintWorkflowRunError,
    BlueprintWorkflowService,
)
from open_hollywood_api.services.run_controls import RunControlError

router = APIRouter(
    prefix="/workflow-runs/{workflow_run_id}/controls",
    tags=["run-controls"],
)
BlueprintServiceDependency = Annotated[
    BlueprintWorkflowService,
    Depends(get_blueprint_workflow_service),
]


@router.post(
    "",
    operation_id="controlWorkflowRun",
    response_model=RunControlResponse,
    responses={
        404: {"description": "Workflow run not found"},
        409: {"description": "Command conflicts with durable workflow state"},
        503: {"description": "Workflow execution service is unavailable"},
    },
    summary="Pause, resume, stop, retry, or update a run budget",
)
async def control_workflow_run(
    workflow_run_id: UUID,
    request: RunControlRequest,
    service: BlueprintServiceDependency,
) -> RunControlResponse:
    """Apply one idempotent command to the registered workflow runtime."""
    try:
        result = await service.apply_control(workflow_run_id, request.to_domain())
    except (RunControlError, BlueprintWorkflowRunError) as error:
        if str(error).startswith("unknown workflow run"):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workflow run not found",
            ) from error
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error
    return RunControlResponse.from_domain(result)
