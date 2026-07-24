"""Integration coverage for immutable-scene manuscript exports."""

from __future__ import annotations

from collections.abc import AsyncIterator
from hashlib import sha256
from io import BytesIO
from uuid import UUID

import pytest
from docx import Document
from httpx import ASGITransport, AsyncClient
from open_hollywood_api.app import create_app
from open_hollywood_api.persistence.database import create_session_factory
from open_hollywood_api.persistence.models import (
    Artifact,
    ArtifactStatus,
    ArtifactVersion,
    Project,
)
from open_hollywood_api.services.exports import ProjectExportStore
from open_hollywood_engine.artifacts import SceneDraft
from pypdf import PdfReader
from sqlalchemy import Engine

pytestmark = pytest.mark.anyio


@pytest.fixture
def anyio_backend() -> str:
    """Keep API tests on the asyncio backend used by FastAPI."""
    return "asyncio"


@pytest.fixture
async def export_client(
    database_engine: Engine,
) -> AsyncIterator[tuple[AsyncClient, UUID, tuple[UUID, ...]]]:
    """Expose a project with three approved immutable scene drafts."""
    session_factory = create_session_factory(database_engine)
    with session_factory.begin() as session:
        project = Project(
            name="The Untouched Stroller",
            settings={"author": "Ada Writer"},
        )
        source_version_ids: list[UUID] = []
        for number in range(1, 4):
            artifact = Artifact(
                project=project,
                artifact_key=f"scene_{number}",
                artifact_type="scene_draft",
                title=f"Scene {number}",
                status=ArtifactStatus.APPROVED,
            )
            draft = SceneDraft(
                scene_id=f"scene_{number}",
                scene_number=number,
                title=f"Threshold {number}",
                revision_number=1,
                prose=(
                    f"Mara reaches threshold {number}.\n\nThe untouched stroller waits in the dust."
                ),
                is_complete=True,
            )
            content = draft.model_dump(mode="json")
            version = ArtifactVersion(
                artifact=artifact,
                version_number=1,
                schema_version=draft.schema_version,
                content=content,
                content_sha256=sha256(draft.model_dump_json().encode("utf-8")).hexdigest(),
            )
            session.add(artifact)
            session.flush()
            source_version_ids.append(version.id)
        session.add(project)
        session.flush()
        project_id = project.id

    application = create_app(project_export_store=ProjectExportStore(session_factory))
    transport = ASGITransport(app=application)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client, project_id, tuple(source_version_ids)


async def test_export_manifest_exposes_formats_and_exact_source_versions(
    export_client: tuple[AsyncClient, UUID, tuple[UUID, ...]],
) -> None:
    client, project_id, source_version_ids = export_client

    response = await client.get(f"/api/v1/projects/{project_id}/exports")

    assert response.status_code == 200
    manifest = response.json()
    assert manifest["available_formats"] == ["markdown", "pdf", "docx"]
    assert [item["scene_number"] for item in manifest["source_versions"]] == [1, 2, 3]
    assert {UUID(item["artifact_version_id"]) for item in manifest["source_versions"]} == set(
        source_version_ids
    )
    assert manifest["unavailable_reason"] is None


@pytest.mark.parametrize(
    ("export_format", "content_type", "extension"),
    [
        ("markdown", "text/markdown; charset=utf-8", "md"),
        ("pdf", "application/pdf", "pdf"),
        (
            "docx",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "docx",
        ),
    ],
)
async def test_downloads_are_deterministic_and_traceable(
    export_client: tuple[AsyncClient, UUID, tuple[UUID, ...]],
    export_format: str,
    content_type: str,
    extension: str,
) -> None:
    client, project_id, source_version_ids = export_client
    url = f"/api/v1/projects/{project_id}/exports/{export_format}"

    first = await client.get(url)
    second = await client.get(url)

    assert first.status_code == 200
    assert first.content == second.content
    assert first.headers["content-type"] == content_type
    assert first.headers["content-disposition"] == (
        f'attachment; filename="the-untouched-stroller.{extension}"'
    )
    assert first.headers["etag"] == f'"{sha256(first.content).hexdigest()}"'
    assert set(first.headers["x-open-hollywood-source-versions"].split(",")) == {
        str(item) for item in source_version_ids
    }

    if export_format == "markdown":
        assert "# The Untouched Stroller" in first.text
        assert "## Scene 3: Threshold 3" in first.text
    elif export_format == "pdf":
        text = "\n".join(
            page.extract_text() or "" for page in PdfReader(BytesIO(first.content)).pages
        )
        assert "Scene 3: Threshold 3" in text
    else:
        document = Document(BytesIO(first.content))
        assert any(paragraph.text == "Scene 3: Threshold 3" for paragraph in document.paragraphs)


async def test_incomplete_project_reports_unavailable_and_conflicts_on_download(
    database_engine: Engine,
) -> None:
    session_factory = create_session_factory(database_engine)
    with session_factory.begin() as session:
        project = Project(name="Not Ready")
        session.add(project)
        session.flush()
        project_id = project.id
    application = create_app(project_export_store=ProjectExportStore(session_factory))
    transport = ASGITransport(app=application)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        manifest = await client.get(f"/api/v1/projects/{project_id}/exports")
        download = await client.get(f"/api/v1/projects/{project_id}/exports/pdf")

    assert manifest.status_code == 200
    assert manifest.json()["available_formats"] == []
    assert "requires 3 to 8 scenes" in manifest.json()["unavailable_reason"]
    assert download.status_code == 409


async def test_unknown_export_project_returns_not_found(
    export_client: tuple[AsyncClient, UUID, tuple[UUID, ...]],
) -> None:
    client, _, _ = export_client
    missing_id = "00000000-0000-0000-0000-000000000000"

    manifest = await client.get(f"/api/v1/projects/{missing_id}/exports")
    download = await client.get(f"/api/v1/projects/{missing_id}/exports/pdf")

    assert manifest.status_code == 404
    assert download.status_code == 404
