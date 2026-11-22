"""Exact workspace, version, delivery and disclosure boundaries for the Q013 inspector."""

from collections.abc import Sequence
from pathlib import Path
from shutil import copyfile
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient
from open_hollywood_api.app import create_app, create_q013_readonly_app, lifespan
from open_hollywood_api.services import q013_inspector as api
from open_hollywood_api.services.production_association_records import ArtifactSelection
from pydantic import BaseModel

from scripts import lookup_saved_review_completion as lookup
from tests.api.test_q008_inspector_api import anyio_backend as anyio_backend
from tests.api.test_q008_inspector_api import archive as archive
from tests.api.test_q008_inspector_api import delivered, offline_catalog
from tests.api.test_q008_inspector_api import prepared as prepared
from tests.api.test_q008_inspector_api import source as source
from tests.production_assessment_fixtures import FixtureRegistration, sha

pytestmark = pytest.mark.anyio


def result(selected: ArtifactSelection, review: ArtifactSelection) -> lookup.Inventory:
    old = delivered(selected, review)
    (row,), (assessment,) = old.lookups, old.assessments
    assert row.status == "available"
    return lookup.Inventory(
        lookups=(row.model_copy(update={"claim_id": "Q013"}),),
        assessments=(
            assessment.model_copy(
                update={
                    "claim_id": "Q013",
                    "operator_score": {
                        "claim_correctness": {"score": "pass", "gold": "private witness"},
                        "evidence_coverage": {"score": "fail", "obligations": {"private": True}},
                    },
                }
            ),
        ),
        accounting_records=old.accounting_records,
        generation_totals=old.generation_totals,
    )


async def read(client: AsyncClient, selected: ArtifactSelection) -> api.Q013InspectorView:
    response = await client.get(
        f"/api/v1/artifact-versions/{selected.version_id}/q013-assessment",
        params=selected.model_dump(exclude={"version_id"}),
    )
    assert response.status_code == 200 and response.headers["cache-control"] == "no-store"
    assert all(
        key not in response.text
        for key in ("private witness", "obligations", "request_manifest_sha256")
    )
    view = api.Q013InspectorView.model_validate_json(response.content)
    (row,) = view.lookups
    assert row.selection == selected
    return view


def empty(view: api.Q013InspectorView, reason: str) -> None:
    (row,) = view.lookups
    assert row.status == "unavailable" and row.reason == reason
    assert row.claim_id is None and row.delivery_id is None
    assert not view.assessments and not view.accounting_records and view.generation_totals is None


async def test_workspace_pair_copy_and_source_refresh(
    archive: Path, source: FixtureRegistration, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    db = archive / "work/database/open_hollywood.db"
    stat = db.stat()
    monkeypatch.setattr(
        api, "REGISTERED", api.WorkspacePin(db, stat.st_dev, stat.st_ino, sha(db.read_bytes()))
    )
    monkeypatch.setattr(api, "_registered_pair", lambda: source.selections)
    review, draft = source.selections
    damaged = False
    opened: list[ArtifactSelection] = []

    def reader(selections: Sequence[ArtifactSelection]) -> lookup.Inventory:
        (selected,) = selections
        opened.append(selected)
        if damaged:
            return lookup.Inventory(
                lookups=(
                    lookup.Unavailable(selection=selected, reason="publication_member_changed"),
                )
            )
        return result(selected, review)

    copy = tmp_path / "identical.db"
    copyfile(db, copy)
    assert not copy.samefile(db) and copy.read_bytes() == db.read_bytes()
    for path in (copy, db):
        app = create_q013_readonly_app(path, reader)
        assert {key: list(ops) for key, ops in app.openapi()["paths"].items()} == {
            "/api/v1/artifact-versions/{artifact_version_id}/q013-assessment": ["get"]
        }
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            if path == copy:
                for selection in (review, draft):
                    empty(await read(client, selection), "unregistered_workspace")
                assert not opened
                continue
            first, second = await read(client, review), await read(client, draft)
            assert first.assessments == second.assessments and len(first.assessments) == 1
            assert (
                first.accounting_records == second.accounting_records
                and len(first.accounting_records) == 1
            )
            assert first.accounting_records[0].request_selection == review
            assert first.assessments[0].operator_score.model_dump() == {
                "claim_correctness": "pass",
                "evidence_coverage": "fail",
            }
            for field, value in (
                ("version_id", str(uuid4())),
                ("project_id", str(uuid4())),
                ("artifact_id", review.artifact_id),
                ("role", review.role),
                ("content_sha256", review.content_sha256),
            ):
                empty(
                    await read(client, draft.model_copy(update={field: value})),
                    "exact_selection_unavailable",
                )
            assert opened == [review, draft]
            damaged = True
            empty(await read(client, draft), "publication_member_changed")
            damaged = False
            assert await read(client, draft) == second

    # Also exercise the optional route through the normal application lifecycle.
    monkeypatch.setenv("OPEN_HOLLYWOOD_DB_PATH", str(db))
    for configured in (False, True):
        app = create_app(
            q013_reader=reader if configured else None, model_catalog_service=offline_catalog()
        )
        async with (
            lifespan(app),
            AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client,
        ):
            reply = await read(client, draft)
            if configured:
                assert reply == second
            else:
                empty(reply, "unregistered_workspace")
            endpoint = f"/api/v1/artifact-versions/{draft.version_id}/q013-assessment"
            assert (await client.get(endpoint)).status_code == 422
            assert (await client.post(endpoint)).status_code == 405
        assert app.state.q013_inspector is None


async def test_foreign_or_misbound_delivery_is_refused(source: FixtureRegistration) -> None:
    review, draft = source.selections
    wrong_score = result(draft, review)
    wrong_score.assessments[0].operator_score["evidence_coverage"] = {"score": "private"}
    controls: tuple[BaseModel, ...] = (
        delivered(draft, review),
        result(review, review),
        result(draft, draft),
        wrong_score,
        result(draft, review).model_copy(update={"generation_totals": None}),
    )
    for reply in controls:
        with pytest.raises(ValueError):
            api._project(reply, draft, review)
