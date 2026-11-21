"""Portable API checks for physical workspace identity, version binding and disclosure."""

from __future__ import annotations

import shutil
from collections.abc import Sequence
from pathlib import Path
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient
from open_hollywood_api.app import create_app, create_q008_readonly_app, lifespan
from open_hollywood_api.services import q008_inspector as adapter
from open_hollywood_api.services.assessment_consumer_projection import Usage
from open_hollywood_api.services.model_profiles import CatalogSource, ModelCatalogService
from open_hollywood_api.services.production_association_records import ArtifactSelection
from open_hollywood_engine.evaluations.assessment_result import ModelAssessment
from pydantic import BaseModel

from scripts import lookup_q008_completion as consumer
from tests.api.test_saved_review_completion import anyio_backend as anyio_backend
from tests.api.test_saved_review_completion import archive as archive
from tests.api.test_saved_review_completion import prepared as prepared
from tests.api.test_saved_review_completion import source as source
from tests.production_assessment_fixtures import FixtureRegistration, sha

pytestmark = pytest.mark.anyio


@pytest.fixture
def database(archive: Path, source: FixtureRegistration, monkeypatch: pytest.MonkeyPatch) -> Path:
    db = archive / "work/database/open_hollywood.db"
    stat = db.stat()
    monkeypatch.setattr(
        adapter,
        "REGISTERED",
        adapter.WorkspacePin(db, stat.st_dev, stat.st_ino, sha(db.read_bytes())),
    )
    monkeypatch.setattr(adapter, "_registered_pair", lambda: source.selections)
    monkeypatch.setenv("OPEN_HOLLYWOOD_DB_PATH", str(db))
    return db


def delivered(selected: ArtifactSelection, review: ArtifactSelection) -> consumer.Inventory:
    usage = Usage(input_tokens=100, output_tokens=20, cached_input_tokens=0, reasoning_tokens=5)
    return consumer.Inventory(
        lookups=(
            consumer.Available(selection=selected, delivery_id="test-delivery", claim_id="Q008"),
        ),
        assessments=(
            consumer.Assessment(
                delivery_id="test-delivery",
                claim_id="Q008",
                claim="A fixture claim.",
                model="fixture",
                model_assessment=ModelAssessment(
                    support="supported", evidence=("E01",), reason="Fixture."
                ),
                operator_score={
                    "passed_judgments": 3,
                    "possible_judgments": 3,
                    "private_gold": "private witness",
                },
                application_status={
                    "semantic_support": "unassessed",
                    "evidence_adequacy": "unassessed",
                    "edit_necessity": "unassessed",
                    "craft": "unassessed",
                    "production_attachment_eligible": False,
                    "writer_dispatch_authorized": False,
                },
            ),
        ),
        accounting_records=(
            consumer.Accounting(
                delivery_id="test-delivery",
                request_selection=review,
                request_manifest_sha256="a" * 64,
                preflight_input_count=100,
                generation_usage=usage,
                actual_billed_cost=None,
            ),
        ),
        generation_totals=usage,
    )


async def get(client: AsyncClient, selection: ArtifactSelection) -> adapter.Q008InspectorView:
    r = await client.get(
        f"/api/v1/artifact-versions/{selection.version_id}/q008-assessment",
        params=selection.model_dump(exclude={"version_id"}),
    )
    assert r.status_code == 200 and r.headers["cache-control"] == "no-store"
    assert "private witness" not in r.text and "request_manifest_sha256" not in r.text
    view = adapter.Q008InspectorView.model_validate_json(r.content)
    assert len(view.lookups) == 1 and view.lookups[0].selection == selection
    return view


def assert_unavailable(view: adapter.Q008InspectorView, reason: str) -> None:
    (row,) = view.lookups
    assert row.status == "unavailable" and row.reason == reason
    assert row.claim_id is None and row.delivery_id is None
    assert not view.assessments and not view.accounting_records and view.generation_totals is None


def offline_catalog() -> ModelCatalogService:
    return ModelCatalogService((CatalogSource(key="fixture", label="Offline", gateway=None),))


async def test_configured_workspace_binds_all_five_fields(
    database: Path, source: FixtureRegistration, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    review, draft = source.selections
    seen = []

    def read(selections: Sequence[ArtifactSelection]) -> BaseModel:
        (selected,) = selections
        seen.append(selected)
        return delivered(selected, review)

    app = create_app(q008_reader=read, model_catalog_service=offline_catalog())
    before = (sha(database.read_bytes()), database.stat().st_mtime_ns)
    async with (
        lifespan(app),
        AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client,
    ):
        one, two = await get(client, review), await get(client, draft)
        assert len(one.assessments) == len(one.accounting_records) == 1
        assert (
            one.assessments == two.assessments and one.accounting_records == two.accounting_records
        )
        for field, value in (
            ("artifact_id", review.artifact_id),
            ("project_id", str(uuid4())),
            ("version_id", str(uuid4())),
            ("content_sha256", review.content_sha256),
            ("role", review.role),
        ):
            assert_unavailable(
                await get(client, draft.model_copy(update={field: value})),
                "exact_selection_unavailable",
            )
        assert seen == [review, draft]
        path = f"/api/v1/artifact-versions/{draft.version_id}/q008-assessment"
        assert (await client.get(path)).status_code == 422 and (
            await client.post(path)
        ).status_code == 405
    assert before == (sha(database.read_bytes()), database.stat().st_mtime_ns)
    assert set(database.parent.iterdir()) == {database}
    assert app.state.q008_inspector is None
    disabled = create_app(model_catalog_service=offline_catalog())
    async with (
        lifespan(disabled),
        AsyncClient(transport=ASGITransport(app=disabled), base_url="http://test") as client,
    ):
        assert_unavailable(await get(client, draft), "unregistered_workspace")
    # A separate operator server must expose only the assessment read, even when misconfigured.
    monkeypatch.setenv("OPEN_HOLLYWOOD_DB_PATH", str(tmp_path / "unregistered.db"))
    isolated = create_q008_readonly_app(read)
    assert {path: list(methods) for path, methods in isolated.openapi()["paths"].items()} == {
        "/api/v1/artifact-versions/{artifact_version_id}/q008-assessment": ["get"]
    }
    async with AsyncClient(transport=ASGITransport(app=isolated), base_url="http://test") as client:
        assert_unavailable(await get(client, draft), "unregistered_workspace")
    assert seen == [review, draft]
    assert not (tmp_path / "unregistered.db").exists()


@pytest.mark.parametrize(
    "fault,reason",
    [
        ("identical_copy", "unregistered_workspace"),
        ("missing", "workspace_unavailable"),
        ("replaced_file", "workspace_unavailable"),
        ("changed_bytes", "workspace_unavailable"),
        ("pending_wal", "workspace_unavailable"),
    ],
)
async def test_workspace_failures_do_not_open_the_delivery(
    database: Path,
    source: FixtureRegistration,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    fault: str,
    reason: str,
) -> None:
    if fault == "identical_copy":
        copy = tmp_path / "copy.db"
        shutil.copyfile(database, copy)
        assert sha(copy.read_bytes()) == sha(database.read_bytes()) and not copy.samefile(database)
        monkeypatch.setenv("OPEN_HOLLYWOOD_DB_PATH", str(copy))
    elif fault in ("missing", "replaced_file"):
        original = database.rename(database.with_suffix(".original"))
        if fault == "replaced_file":
            shutil.copyfile(original, database)
    elif fault == "changed_bytes":
        with database.open("ab") as stream:
            stream.write(b"changed")
    else:
        database.with_name(database.name + "-wal").touch()

    def forbidden(_: Sequence[ArtifactSelection]) -> BaseModel:
        raise AssertionError("Unexpected consumer read")

    app = create_app(q008_reader=forbidden, model_catalog_service=offline_catalog())
    async with (
        lifespan(app),
        AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client,
    ):
        for selected in source.selections:
            assert_unavailable(await get(client, selected), reason)


async def test_selection_and_original_request_rechecked(
    database: Path, source: FixtureRegistration
) -> None:
    review, draft = source.selections
    replies = iter(
        (
            delivered(review, review),
            delivered(draft, review.model_copy(update={"version_id": str(uuid4())})),
        )
    )
    app = create_app(q008_reader=lambda _: next(replies), model_catalog_service=offline_catalog())
    async with (
        lifespan(app),
        AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client,
    ):
        for _ in range(2):
            assert_unavailable(await get(client, draft), "publication_unavailable")
