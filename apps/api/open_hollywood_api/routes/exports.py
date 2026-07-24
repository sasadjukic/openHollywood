"""Deterministic manuscript export routes."""

from typing import Annotated
from uuid import UUID

import anyio
from fastapi import APIRouter, Depends, HTTPException, Response, status

from open_hollywood_api.dependencies import get_project_export_store
from open_hollywood_api.export_models import ProjectExportFormat, ProjectExportManifest
from open_hollywood_api.services.exports import (
    ExportNotReadyError,
    ExportProjectNotFoundError,
    ProjectExportStore,
)

router = APIRouter(tags=["exports"])
ProjectExportStoreDependency = Annotated[
    ProjectExportStore,
    Depends(get_project_export_store),
]


@router.get(
    "/projects/{project_id}/exports",
    operation_id="listProjectExports",
    response_model=ProjectExportManifest,
    responses={404: {"description": "Project not found"}},
    summary="List deterministic exports available for one project",
)
async def list_project_exports(
    project_id: UUID,
    store: ProjectExportStoreDependency,
) -> ProjectExportManifest:
    """Return export readiness and the exact source artifact versions."""
    try:
        record = await anyio.to_thread.run_sync(store.get_manifest, project_id)
    except ExportProjectNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        ) from error
    return ProjectExportManifest.from_record(record)


@router.get(
    "/projects/{project_id}/exports/{export_format}",
    operation_id="downloadProjectExport",
    response_class=Response,
    responses={
        200: {
            "content": {"application/octet-stream": {}},
            "description": "Rendered manuscript download",
        },
        404: {"description": "Project not found"},
        409: {"description": "Project is not ready to export"},
    },
    summary="Download one deterministic manuscript export",
)
async def download_project_export(
    project_id: UUID,
    export_format: ProjectExportFormat,
    store: ProjectExportStoreDependency,
) -> Response:
    """Render the current approved scene versions into the requested format."""
    try:
        record = await anyio.to_thread.run_sync(
            store.render,
            project_id,
            export_format.value,
        )
    except ExportProjectNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        ) from error
    except ExportNotReadyError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error
    source_header = ",".join(str(source.artifact_version_id) for source in record.source_versions)
    return Response(
        content=record.content,
        media_type=record.media_type,
        headers={
            "Content-Disposition": f'attachment; filename="{record.filename}"',
            "ETag": f'"{record.content_sha256}"',
            "X-Open-Hollywood-Source-Versions": source_header,
        },
    )
