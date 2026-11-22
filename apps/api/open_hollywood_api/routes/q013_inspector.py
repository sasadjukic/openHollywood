"""Exact-version read-only assessment lookup, with application-owned registration."""

from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, Query, Request, Response

from open_hollywood_api.services.production_association_records import ArtifactSelection
from open_hollywood_api.services.q013_inspector import (
    Q013InspectorService,
    Q013InspectorView,
    unavailable,
)

router = APIRouter(tags=["workspace"])


@router.get(
    "/artifact-versions/{artifact_version_id}/q013-assessment",
    operation_id="getQ013Assessment",
    response_model=Q013InspectorView,
    summary="Read the saved Q013 assessment for an exact workspace version",
)
def get_q013_assessment(
    artifact_version_id: UUID,
    project_id: UUID,
    artifact_id: UUID,
    content_sha256: Annotated[str, Query(pattern=r"^[0-9a-f]{64}$")],
    role: Literal["original_review", "reviewed_draft"],
    request: Request,
    response: Response,
) -> Q013InspectorView:
    response.headers["Cache-Control"] = "no-store"
    selected = ArtifactSelection(
        project_id=str(project_id),
        artifact_id=str(artifact_id),
        version_id=str(artifact_version_id),
        role=role,
        content_sha256=content_sha256,
    )
    service = getattr(request.app.state, "q013_inspector", None)
    if not isinstance(service, Q013InspectorService):
        return unavailable(selected, "unregistered_workspace")
    return service.view(selected)
