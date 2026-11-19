"""Inspector projection and HTTP boundary over authored, disposable saved workspaces."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

import pytest
from httpx import ASGITransport, AsyncClient
from open_hollywood_api.app import create_app, lifespan
from open_hollywood_api.services import production_association_export as archive
from open_hollywood_api.services import production_association_lookup as lookup
from open_hollywood_api.services.artifact_provenance import ArtifactProvenanceService, _project
from open_hollywood_api.services.model_profiles import CatalogSource, ModelCatalogService
from open_hollywood_engine.secrets import SecretLeakError

from tests.api.test_production_association_lookup import registered as registered
from tests.production_lookup_fixtures import selections


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


def params(value: Any) -> dict[str, str]:
    return {k: v for k, v in value.model_dump().items() if k != "version_id"}


@pytest.mark.anyio
async def test_all_twelve_http_views_are_exact_compact_and_readonly(
    registered: tuple[archive._Registration, lookup._Workspace],
) -> None:
    source, current = registered
    app = create_app(artifact_provenance_service=ArtifactProvenanceService(current.path))
    before = current.path.read_bytes()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        for i, selection in enumerate(selections(source)):
            response = await client.get(
                f"/api/v1/artifact-versions/{selection.version_id}/provenance",
                params=params(selection),
            )
            assert response.status_code == 200 and response.headers["cache-control"] == "no-store"
            value = response.json()
            assert value["selection"] == selection.model_dump()
            assert value["status"] == "identity_verified"
            assert (
                not value["assessment_attachment_eligible"]
                and not value["writer_dispatch_authorized"]
            )
            assert value["live_calls"] == 0
            relationship = value["relationship"]
            assert relationship["assessment_source"] == "unsupported_contract"
            assert relationship["captured_assessment_delivery"] == "missing"
            assert relationship["craft"] == relationship["edit_necessity"] == "unassessed"
            assert relationship["selected_is_latest_at_lookup"] is (i not in (4, 5, 8, 9))
            for excluded in (
                "prompt_text",
                "prompt_sha256",
                "database",
                "inode",
                "device",
                "Echo.",
            ):
                assert excluded not in response.text
            assert len(response.content) < 3000
    assert current.path.read_bytes() == before


@pytest.mark.anyio
@pytest.mark.parametrize(
    "field", ["project_id", "artifact_id", "content_sha256", "version_id", "role"]
)
async def test_http_mismatches_never_get_a_relationship(
    registered: tuple[archive._Registration, lookup._Workspace],
    field: str,
) -> None:
    source, current = registered
    selected = selections(source)[0].model_copy(
        update={
            field: "f" * 64
            if field == "content_sha256"
            else "reviewed_draft"
            if field == "role"
            else "00000000-0000-0000-0000-000000009999"
        }
    )
    app = create_app(artifact_provenance_service=ArtifactProvenanceService(current.path))
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(
            f"/api/v1/artifact-versions/{selected.version_id}/provenance", params=params(selected)
        )
    assert response.status_code == 200
    assert response.json()["status"] == "unavailable" and response.json()["relationship"] is None


@pytest.mark.anyio
async def test_no_app_owned_source_and_invalid_requests_do_not_guess_default(
    registered: tuple[archive._Registration, lookup._Workspace],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    selected = selections(registered[0])[0]

    def forbidden(*args: Any, **kwargs: Any) -> Any:
        raise AssertionError("No lookup without an app-owned source")

    monkeypatch.setattr(lookup, "lookup", forbidden)
    async with AsyncClient(
        transport=ASGITransport(app=create_app()), base_url="http://test"
    ) as client:
        path = f"/api/v1/artifact-versions/{selected.version_id}/provenance"
        response = await client.get(path, params=params(selected))
        assert response.json()["reason"] == "unregistered_workspace"
        assert (await client.get(path)).status_code == 422
        assert (
            await client.get(path, params={**params(selected), "content_sha256": "bad"})
        ).status_code == 422
        assert (await client.post(path, json=params(selected))).status_code == 405


@pytest.mark.parametrize(
    "kind", ["archive_missing", "database_replaced", "unregistered", "database_error", "secret"]
)
def test_errors_are_unavailable_without_raw_details(
    registered: tuple[archive._Registration, lookup._Workspace],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    kind: str,
) -> None:
    source, current = registered
    selected = selections(source)[0]
    service = ArtifactProvenanceService(
        current.path if kind != "unregistered" else tmp_path / "foreign.db"
    )
    if kind == "archive_missing":
        (source.archive / "R01.snapshot.json").unlink()
    elif kind == "database_replaced":
        path = tmp_path / "other.db"
        path.write_bytes(current.path.read_bytes())
        path.replace(current.path)
    elif kind in ("database_error", "secret"):

        def failed(*args: Any, **kwargs: Any) -> Any:
            if kind == "secret":
                raise SecretLeakError("fixture", "PRIVATE SOURCE VALUE")
            raise sqlite3.OperationalError("PRIVATE SOURCE VALUE")

        monkeypatch.setattr(lookup, "lookup", failed)
    result = service.view(selected)
    assert result.status == "unavailable" and result.relationship is None
    assert "PRIVATE SOURCE VALUE" not in result.model_dump_json()
    if kind == "secret":
        assert result.reason == "source_unavailable"


@pytest.mark.parametrize(
    "fault", ["selection", "hash", "workspace", "identity_missing", "mixed_state", "writer"]
)
def test_wrong_or_incomplete_lookup_result_is_not_projected(
    registered: tuple[archive._Registration, lookup._Workspace],
    fault: str,
) -> None:
    source, current = registered
    selected = selections(source)[0]
    result = lookup.lookup(lookup.LookupRequest(workspace=current.name, selections=(selected,)))
    raw = json.loads(result.model_dump_json())
    if fault == "hash":
        raw["request_sha256"] = "f" * 64
    elif fault == "workspace":
        raw["workspace"] = "wrong"
    elif fault == "selection":
        raw["entries"][0]["selection"]["role"] = "reviewed_draft"
    elif fault == "identity_missing":
        raw["entries"][0]["identity"] = None
    elif fault == "mixed_state":
        raw["entries"][0]["status"] = "unavailable"
    else:
        raw["writer_dispatch_authorized"] = True
    with pytest.raises(ValueError):
        _project(lookup.LookupResult.model_validate_json(json.dumps(raw)), selected)


@pytest.mark.parametrize(
    "reason",
    [
        "ambiguous_association",
        "no_registered_association",
        "current_source_missing",
        "current_source_mismatch",
    ],
)
def test_unavailable_reasons_are_preserved(
    registered: tuple[archive._Registration, lookup._Workspace],
    monkeypatch: pytest.MonkeyPatch,
    reason: str,
) -> None:
    source, current = registered
    selected = selections(source)[0]
    result = lookup.lookup(lookup.LookupRequest(workspace=current.name, selections=(selected,)))
    raw = json.loads(result.model_dump_json())
    raw["entries"][0].update(status="unavailable", reason=reason, identity=None)
    monkeypatch.setattr(
        lookup, "lookup", lambda request: lookup.LookupResult.model_validate_json(json.dumps(raw))
    )
    view = ArtifactProvenanceService(current.path).view(selected)
    assert view.reason == reason and view.relationship is None


@pytest.mark.anyio
async def test_lifespan_binds_service_to_the_same_owned_database(
    registered: tuple[archive._Registration, lookup._Workspace],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from open_hollywood_api import app as application

    monkeypatch.setattr(application, "database_path_from_environment", lambda: registered[1].path)
    app = create_app(
        model_catalog_service=ModelCatalogService(
            (CatalogSource(key="fixture", label="Offline fixture", gateway=None),)
        )
    )
    async with lifespan(app):
        assert app.state.artifact_provenance_service._database == registered[1].path.absolute()
        selected = selections(registered[0])[0]
        assert app.state.artifact_provenance_service.view(selected).status == "identity_verified"
    assert app.state.artifact_provenance_service is None
