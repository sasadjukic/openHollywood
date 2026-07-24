"""Public contracts for deterministic project exports."""

from __future__ import annotations

from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from open_hollywood_api.services.exports import ExportManifestRecord


class ProjectExportFormat(StrEnum):
    """Download formats supported for v0.1 short prose."""

    MARKDOWN = "markdown"
    PDF = "pdf"
    DOCX = "docx"


class ExportSourceVersion(BaseModel):
    """One immutable scene version included in an export."""

    model_config = ConfigDict(frozen=True)

    artifact_key: str
    artifact_version_id: UUID
    scene_number: int


class ProjectExportManifest(BaseModel):
    """Export readiness and exact immutable source lineage."""

    model_config = ConfigDict(frozen=True)

    project_id: UUID
    available_formats: tuple[ProjectExportFormat, ...]
    source_versions: tuple[ExportSourceVersion, ...]
    unavailable_reason: str | None

    @classmethod
    def from_record(cls, record: ExportManifestRecord) -> ProjectExportManifest:
        return cls(
            project_id=record.project_id,
            available_formats=tuple(ProjectExportFormat(item) for item in record.available_formats),
            source_versions=tuple(
                ExportSourceVersion(
                    artifact_key=source.artifact_key,
                    artifact_version_id=source.artifact_version_id,
                    scene_number=source.scene_number,
                )
                for source in record.source_versions
            ),
            unavailable_reason=record.unavailable_reason,
        )
