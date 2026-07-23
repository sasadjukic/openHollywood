"""Human-decision route for the mandatory Story Blueprint interrupt."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from open_hollywood_api.blueprint_models import (
    BlueprintDecisionRequest,
    BlueprintDecisionResponse,
)
from open_hollywood_api.dependencies import get_blueprint_workflow_service
from open_hollywood_api.services.blueprint_workflow import (
    BlueprintWorkflowRunError,
    BlueprintWorkflowService,
)

router = APIRouter(
    prefix="/workflow-runs/{workflow_run_id}/decisions",
    tags=["blueprint-decisions"],
)
BlueprintServiceDependency = Annotated[
    BlueprintWorkflowService,
    Depends(get_blueprint_workflow_service),
]


@router.post(
    "",
    operation_id="submitBlueprintDecision",
    response_model=BlueprintDecisionResponse,
    responses={
        404: {"description": "Workflow run not found"},
        409: {"description": "Decision conflicts with durable workflow state"},
        503: {"description": "Workflow execution service is unavailable"},
    },
    summary="Resolve the active Story Blueprint human interrupt",
)
async def submit_blueprint_decision(
    workflow_run_id: UUID,
    request: BlueprintDecisionRequest,
    service: BlueprintServiceDependency,
) -> BlueprintDecisionResponse:
    """Apply an idempotent approve, revise, reject, or fork command."""
    try:
        result = await service.resume(workflow_run_id, request.to_domain())
    except BlueprintWorkflowRunError as error:
        if str(error).startswith("unknown workflow run"):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workflow run not found",
            ) from error
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error
    return BlueprintDecisionResponse.from_domain(result)
