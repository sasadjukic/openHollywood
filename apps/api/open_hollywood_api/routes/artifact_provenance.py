"""One read-only, exact-selection provenance endpoint; no inference or writer action."""

from __future__ import annotations

from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, Query, Request, Response

from open_hollywood_api.services.artifact_provenance import (
    ArtifactProvenance,
    ArtifactProvenanceService,
    unavailable,
)
from open_hollywood_api.services.production_association_records import ArtifactSelection

router = APIRouter(tags=["workspace"])


@router.get(
    "/artifact-versions/{artifact_version_id}/provenance",
    operation_id="getArtifactProvenance",
    response_model=ArtifactProvenance,
    summary="Inspect the exact selected version's registered review relationship",
)
def get_artifact_provenance(
    artifact_version_id: UUID,
    project_id: UUID,
    artifact_id: UUID,
    content_sha256: Annotated[str, Query(pattern=r"^[0-9a-f]{64}$")],
    role: Literal["original_review", "reviewed_draft"],
    request: Request,
    response: Response,
) -> ArtifactProvenance:
    response.headers["Cache-Control"] = "no-store"
    selection = ArtifactSelection(
        role=role,
        project_id=str(project_id),
        artifact_id=str(artifact_id),
        version_id=str(artifact_version_id),
        content_sha256=content_sha256,
    )
    service = getattr(request.app.state, "artifact_provenance_service", None)
    if not isinstance(service, ArtifactProvenanceService):
        return unavailable(selection, "unregistered_workspace")
    return service.view(selection)
