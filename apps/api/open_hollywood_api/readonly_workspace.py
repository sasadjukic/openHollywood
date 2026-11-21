"""The workspace reads used by the local archive viewer."""

import socket
import threading
import time
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from sqlalchemy import Engine

from open_hollywood_api.persistence.database import create_session_factory
from open_hollywood_api.routes import (
    artifact_provenance,
    exports,
    health,
    q008_inspector,
    workflow_events,
    workspace,
)
from open_hollywood_api.services.artifact_provenance import ArtifactProvenanceService
from open_hollywood_api.services.exports import ProjectExportStore
from open_hollywood_api.services.q008_inspector import Q008InspectorService, Q008Reader
from open_hollywood_api.services.workflow_events import WorkflowEventStore
from open_hollywood_api.services.workspace import WorkspaceStore


def navigation_app(authority: Path, engine: Engine, reader: Q008Reader) -> FastAPI:
    app = FastAPI(title="Open Hollywood read-only workspace", docs_url=None, redoc_url=None)
    sessions = create_session_factory(engine)
    app.state.workspace_store = WorkspaceStore(sessions)
    app.state.project_export_store = ProjectExportStore(sessions)
    app.state.workflow_event_store = WorkflowEventStore(sessions)
    app.state.artifact_provenance_service = ArtifactProvenanceService(authority)
    app.state.q008_inspector = Q008InspectorService(authority, reader)
    app.include_router(artifact_provenance.router, prefix="/api/v1")
    app.include_router(q008_inspector.router, prefix="/api/v1")
    for path, handler in (
        ("/health", health.get_health),
        ("/projects", workspace.list_projects),
        ("/projects/{project_id}/workspace", workspace.get_project_workspace),
        ("/artifact-versions/{artifact_version_id}", workspace.get_artifact_version),
        ("/projects/{project_id}/exports", exports.list_project_exports),
        ("/workflow-runs/{workflow_run_id}/events", workflow_events.list_workflow_run_events),
    ):
        app.add_api_route("/api/v1" + path, handler, methods=["GET"])
    return app


@contextmanager
def serve_loopback(app: FastAPI, port: int = 0) -> Iterator[str]:
    """Hold one loopback listener and drain outstanding requests before returning."""
    with socket.create_server(("127.0.0.1", port)) as sock:
        server = uvicorn.Server(uvicorn.Config(app, log_level="warning", access_log=False))
        worker = threading.Thread(target=server.run, kwargs={"sockets": [sock]})
        worker.start()
        try:
            deadline = time.monotonic() + 20
            while not server.started:
                if not worker.is_alive() or time.monotonic() >= deadline:
                    raise RuntimeError("The local archive server could not start.")
                time.sleep(0.02)
            yield f"http://127.0.0.1:{sock.getsockname()[1]}"
        finally:
            server.should_exit = True
            worker.join()
