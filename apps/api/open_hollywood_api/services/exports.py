"""SQLite-backed assembly of approved scenes into deterministic exports."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from hashlib import sha256
from typing import Any
from uuid import UUID

from open_hollywood_engine.artifacts import ArtifactKind, SceneDraft
from open_hollywood_engine.rendering import (
    ProseManuscript,
    RenderingInvariantError,
    export_docx,
    export_pdf,
    render_markdown,
)
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload, sessionmaker

from open_hollywood_api.persistence.models import (
    Artifact,
    ArtifactStatus,
    ArtifactVersion,
    Project,
)

EXPORT_FORMATS = ("markdown", "pdf", "docx")


@dataclass(frozen=True, slots=True)
class ExportSourceVersionRecord:
    """One exact scene version included in a rendered manuscript."""

    artifact_key: str
    artifact_version_id: UUID
    scene_number: int


@dataclass(frozen=True, slots=True)
class ExportManifestRecord:
    """Export readiness and immutable source lineage."""

    project_id: UUID
    available_formats: tuple[str, ...]
    source_versions: tuple[ExportSourceVersionRecord, ...]
    unavailable_reason: str | None


@dataclass(frozen=True, slots=True)
class ProjectExportRecord:
    """Rendered bytes plus download and cache metadata."""

    content: bytes
    content_sha256: str
    filename: str
    media_type: str
    source_versions: tuple[ExportSourceVersionRecord, ...]


class ExportProjectNotFoundError(LookupError):
    """Raised when an export references an unknown project."""


class ExportNotReadyError(RuntimeError):
    """Raised when approved scene artifacts cannot form a complete manuscript."""


class ProjectExportStore:
    """Read immutable scene versions and render local project downloads."""

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def get_manifest(self, project_id: UUID) -> ExportManifestRecord:
        """Describe current export readiness without rendering binary output."""
        project = self._load_project(project_id)
        try:
            _, sources = _assemble_manuscript(project)
        except ExportNotReadyError as error:
            return ExportManifestRecord(
                project_id=project.id,
                available_formats=(),
                source_versions=(),
                unavailable_reason=str(error),
            )
        return ExportManifestRecord(
            project_id=project.id,
            available_formats=EXPORT_FORMATS,
            source_versions=sources,
            unavailable_reason=None,
        )

    def render(self, project_id: UUID, export_format: str) -> ProjectExportRecord:
        """Render one format from the exact latest approved scene versions."""
        if export_format not in EXPORT_FORMATS:
            raise ValueError(f"unsupported export format: {export_format}")
        project = self._load_project(project_id)
        manuscript, sources = _assemble_manuscript(project)
        renderers = {
            "markdown": lambda: render_markdown(manuscript).encode("utf-8"),
            "pdf": lambda: export_pdf(manuscript),
            "docx": lambda: export_docx(manuscript),
        }
        media_types = {
            "markdown": "text/markdown; charset=utf-8",
            "pdf": "application/pdf",
            "docx": ("application/vnd.openxmlformats-officedocument.wordprocessingml.document"),
        }
        extensions = {"markdown": "md", "pdf": "pdf", "docx": "docx"}
        content = renderers[export_format]()
        return ProjectExportRecord(
            content=content,
            content_sha256=sha256(content).hexdigest(),
            filename=f"{_filename_slug(project.name)}.{extensions[export_format]}",
            media_type=media_types[export_format],
            source_versions=sources,
        )

    def _load_project(self, project_id: UUID) -> Project:
        with self._session_factory() as session:
            project = session.scalar(
                select(Project)
                .where(Project.id == project_id)
                .options(selectinload(Project.artifacts).selectinload(Artifact.versions))
            )
            if project is None:
                raise ExportProjectNotFoundError(str(project_id))
            session.expunge(project)
            return project


def _assemble_manuscript(
    project: Project,
) -> tuple[ProseManuscript, tuple[ExportSourceVersionRecord, ...]]:
    candidates: list[tuple[Artifact, ArtifactVersion, SceneDraft]] = []
    for artifact in project.artifacts:
        if (
            artifact.artifact_type != ArtifactKind.SCENE_DRAFT.value
            or artifact.status is not ArtifactStatus.APPROVED
            or not artifact.versions
        ):
            continue
        version = max(artifact.versions, key=lambda item: item.version_number)
        try:
            draft = SceneDraft.model_validate(version.content)
        except ValidationError as error:
            raise ExportNotReadyError(
                f"Approved scene artifact {artifact.artifact_key!r} has invalid content."
            ) from error
        candidates.append((artifact, version, draft))

    candidates.sort(key=lambda item: (item[2].scene_number, item[0].artifact_key))
    author = _optional_author(project.settings)
    try:
        manuscript = ProseManuscript.from_scene_drafts(
            title=project.name,
            author=author,
            drafts=tuple(item[2] for item in candidates),
        )
    except RenderingInvariantError as error:
        raise ExportNotReadyError(str(error)) from error
    sources = tuple(
        ExportSourceVersionRecord(
            artifact_key=artifact.artifact_key,
            artifact_version_id=version.id,
            scene_number=draft.scene_number,
        )
        for artifact, version, draft in candidates
    )
    return manuscript, sources


def _optional_author(settings: dict[str, Any]) -> str | None:
    author = settings.get("author")
    if isinstance(author, str) and author.strip():
        return author.strip()
    return None


def _filename_slug(value: str) -> str:
    ascii_value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", ascii_value).strip("-").lower()
    return slug[:80] or "open-hollywood-manuscript"
