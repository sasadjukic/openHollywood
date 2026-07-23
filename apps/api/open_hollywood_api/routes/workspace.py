"""Read-only routes for projects, chat, runs, artifacts, and versions."""

from typing import Annotated
from uuid import UUID

import anyio
from fastapi import APIRouter, Depends, HTTPException, status

from open_hollywood_api.dependencies import get_workspace_store
from open_hollywood_api.services.workspace import (
    WorkspaceArtifactVersionNotFoundError,
    WorkspaceProjectNotFoundError,
    WorkspaceStore,
)
from open_hollywood_api.workspace_models import (
    ArtifactVersionDetail,
    ProjectList,
    ProjectSummary,
    ProjectWorkspace,
)

router = APIRouter(tags=["workspace"])
WorkspaceStoreDependency = Annotated[WorkspaceStore, Depends(get_workspace_store)]


@router.get(
    "/projects",
    operation_id="listProjects",
    response_model=ProjectList,
    summary="List locally persisted story projects",
)
async def list_projects(store: WorkspaceStoreDependency) -> ProjectList:
    """Return project navigation data ordered by recent activity."""
    records = await anyio.to_thread.run_sync(store.list_projects)
    return ProjectList(projects=[ProjectSummary.from_record(record) for record in records])


@router.get(
    "/projects/{project_id}/workspace",
    operation_id="getProjectWorkspace",
    response_model=ProjectWorkspace,
    responses={404: {"description": "Project not found"}},
    summary="Load one persisted creative workspace",
)
async def get_project_workspace(
    project_id: UUID,
    store: WorkspaceStoreDependency,
) -> ProjectWorkspace:
    """Load chat, workflow status, artifacts, and version metadata."""
    try:
        record = await anyio.to_thread.run_sync(
            store.get_project_workspace,
            project_id,
        )
    except WorkspaceProjectNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        ) from error
    return ProjectWorkspace.from_record(record)


@router.get(
    "/artifact-versions/{artifact_version_id}",
    operation_id="getArtifactVersion",
    response_model=ArtifactVersionDetail,
    responses={404: {"description": "Artifact version not found"}},
    summary="Load immutable artifact content and provenance",
)
async def get_artifact_version(
    artifact_version_id: UUID,
    store: WorkspaceStoreDependency,
) -> ArtifactVersionDetail:
    """Return one version body, lineage, provider-safe provenance, and scores."""
    try:
        record = await anyio.to_thread.run_sync(
            store.get_artifact_version,
            artifact_version_id,
        )
    except WorkspaceArtifactVersionNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Artifact version not found",
        ) from error
    return ArtifactVersionDetail.from_record(record)
