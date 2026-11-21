"""Exercise ordinary artifact navigation in Chromium over read-only local API instances."""

from __future__ import annotations

import json
import os
import shutil
import sqlite3
import subprocess
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from uuid import UUID

from fastapi.staticfiles import StaticFiles
from open_hollywood_api.app import create_q008_readonly_app
from open_hollywood_api.persistence.database import DATABASE_PATH_VARIABLE, create_session_factory
from open_hollywood_api.routes import (
    artifact_provenance,
    exports,
    health,
    workflow_events,
    workspace,
)
from open_hollywood_api.services import assessment_completion as storage
from open_hollywood_api.services import q008_inspector as api
from open_hollywood_api.services.artifact_provenance import ArtifactProvenanceService
from open_hollywood_api.services.exports import ProjectExportStore
from open_hollywood_api.services.workflow_events import WorkflowEventStore
from open_hollywood_api.services.workspace import WorkspaceStore
from open_hollywood_engine.evaluations.assessment_completion import encoded
from open_hollywood_engine.evaluations.review_evidence import require
from sqlalchemy import Engine, create_engine
from sqlalchemy.pool import NullPool

from scripts import lookup_q008_completion as consumer
from scripts.qualify_q008_inspector import _add_successor, _details
from scripts.qualify_q008_inspector_api import ROOT, serve_local

OUTPUT = ROOT / "data/diagnostics/q008-browser-2026-11-21"
WEB = ROOT / "apps/web"


@contextmanager
def navigation_server(authority: Path, engine: Engine, site: Path) -> Iterator[str]:
    with patch.dict(os.environ, {DATABASE_PATH_VARIABLE: str(authority)}):
        app = create_q008_readonly_app(consumer.lookup)
    sessions = create_session_factory(engine)
    app.state.workspace_store = WorkspaceStore(sessions)
    app.state.project_export_store = ProjectExportStore(sessions)
    app.state.workflow_event_store = WorkflowEventStore(sessions)
    app.state.artifact_provenance_service = ArtifactProvenanceService(authority)
    app.include_router(artifact_provenance.router, prefix="/api/v1")
    # Only the GET handlers the regular artifact navigation actually uses.
    for path, handler in (
        ("/health", health.get_health),
        ("/projects", workspace.list_projects),
        ("/projects/{project_id}/workspace", workspace.get_project_workspace),
        ("/artifact-versions/{artifact_version_id}", workspace.get_artifact_version),
        ("/projects/{project_id}/exports", exports.list_project_exports),
        ("/workflow-runs/{workflow_run_id}/events", workflow_events.list_workflow_run_events),
    ):
        app.add_api_route("/api/v1" + path, handler, methods=["GET"])
    require(all(set(ops) == {"get"} for ops in app.openapi()["paths"].values()), "write_route")
    app.mount("/", StaticFiles(directory=site, html=True))
    with serve_local(app) as base:
        yield base


def qualify() -> None:
    review, draft = api._registered_pair()
    registered = api.REGISTERED.path
    original = consumer.PUBLICATION
    originals = [registered, *original.iterdir()]
    stamps = {p: (storage._sha(p.read_bytes()), p.stat().st_mtime_ns) for p in originals}
    require(stamps[registered][0] == api.REGISTERED.sha256, "wrong_registered_database")
    OUTPUT.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix="replay-", dir=OUTPUT) as tmp:
        scratch = Path(tmp)
        copy = scratch / "identical.db"
        shutil.copyfile(registered, copy)
        require(
            not copy.samefile(registered) and copy.read_bytes() == registered.read_bytes(), "copy"
        )
        navigation = scratch / "navigation.db"
        shutil.copyfile(copy, navigation)
        adjacent = _add_successor(navigation, draft)
        selections = {"review": review, "draft": draft, "adjacent": adjacent}
        details = _details(navigation, selections)
        require(
            details["adjacent"].selected_version.parent_version_id == UUID(draft.version_id)
            and details["adjacent"].content == details["draft"].content,
            "same_text_lineage",
        )
        site = scratch / "site"
        subprocess.run(
            ["node", str(WEB / "node_modules/vite/bin/vite.js"), "build", "--outDir", str(site)],
            cwd=WEB,
            env={**os.environ, "VITE_API_URL": ""},
            check=True,
            timeout=120,
        )
        publication = scratch / "publication"
        shutil.copytree(original, publication)
        uri = navigation.as_uri() + "?mode=ro&immutable=1"
        engine = create_engine(
            "sqlite+pysqlite://",
            poolclass=NullPool,
            creator=lambda: sqlite3.connect(uri, uri=True, check_same_thread=False),
        )
        try:
            store = WorkspaceStore(create_session_factory(engine))
            project = store.get_project_workspace(UUID(review.project_id)).project
            (expected,) = consumer.lookup((review, draft)).assessments
            (scratch / "cases.json").write_bytes(
                encoded(
                    {
                        "project": project.name,
                        "selections": {k: v.model_dump(mode="json") for k, v in selections.items()},
                        "titles": {k: v.artifact.title for k, v in details.items()},
                        "delivery": expected.delivery_id,
                        "claim": expected.claim,
                    }
                )
            )
            with (
                patch.object(consumer, "PUBLICATION", publication),
                navigation_server(registered, engine, site) as registered_url,
                navigation_server(copy, engine, site) as copy_url,
            ):
                subprocess.run(
                    ["node", "e2e/q008-navigation.mjs", registered_url, copy_url, str(scratch)],
                    cwd=WEB,
                    timeout=360,
                    check=True,
                )
            result = json.loads((scratch / "browser-result.json").read_bytes())
        finally:
            engine.dispose()
    require(
        stamps == {p: (storage._sha(p.read_bytes()), p.stat().st_mtime_ns) for p in originals}
        and set(registered.parent.iterdir()) == {registered},
        "original_changed",
    )
    result["original_files_preserved"] = len(originals)
    (OUTPUT / "verification.json").write_bytes(encoded(result))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    qualify()
