"""Run the Q008 inspector against loopback FastAPI adapters for the registered DB and a copy."""

from __future__ import annotations

import json
import os
import shutil
import socket
import subprocess
import threading
import time
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from xml.etree import ElementTree

import httpx
import uvicorn
from open_hollywood_api.app import LOCAL_WEB_ORIGINS, create_q008_readonly_app
from open_hollywood_api.persistence.database import DATABASE_PATH_VARIABLE
from open_hollywood_api.services import assessment_completion as storage
from open_hollywood_api.services import q008_inspector as api
from open_hollywood_api.services.production_association_records import ArtifactSelection
from open_hollywood_engine.evaluations.assessment_completion import encoded
from open_hollywood_engine.evaluations.review_evidence import require

from scripts import lookup_q008_completion as consumer
from scripts.qualify_q008_inspector import prepare

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data/diagnostics/q008-api-2026-11-21"


@contextmanager
def _serve(database: Path) -> Iterator[str]:
    with patch.dict(os.environ, {DATABASE_PATH_VARIABLE: str(database)}):
        app = create_q008_readonly_app(consumer.lookup)
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
        server = uvicorn.Server(uvicorn.Config(app, log_level="warning", access_log=False))
        worker = threading.Thread(target=server.run, kwargs={"sockets": [sock]}, daemon=True)
        worker.start()
        try:
            deadline = time.monotonic() + 20
            while not server.started:
                require(worker.is_alive() and time.monotonic() < deadline, "inspector_server_start")
                time.sleep(0.02)
            yield f"http://127.0.0.1:{port}"
        finally:
            server.should_exit = True
            worker.join(timeout=15)
            require(not worker.is_alive(), "inspector_server_shutdown")


def _read(client: httpx.Client, base: str, selection: ArtifactSelection) -> api.Q008InspectorView:
    response = client.get(
        f"{base}/api/v1/artifact-versions/{selection.version_id}/q008-assessment",
        params=selection.model_dump(exclude={"version_id"}),
    )
    response.raise_for_status()
    require(response.headers.get("cache-control") == "no-store", "inspector_cached_response")
    require(
        response.headers.get("access-control-allow-origin") == LOCAL_WEB_ORIGINS[0],
        "inspector_origin_unavailable",
    )
    view = api.Q008InspectorView.model_validate_json(response.content)
    require(view.lookups[0].selection == selection, "inspector_wrong_version")
    return view


def qualify() -> None:
    replay = json.loads(prepare().read_bytes())
    OUTPUT.mkdir(parents=True, exist_ok=True)
    review, draft = api._registered_pair()
    adjacent = draft.model_copy(
        update={"version_id": replay["details"]["adjacent"]["selected_version"]["id"]}
    )
    database = api.REGISTERED.path
    original = consumer.PUBLICATION
    originals = (database, *original.iterdir())
    stamps = {p: (storage._sha(p.read_bytes()), p.stat().st_mtime_ns) for p in originals}
    with TemporaryDirectory(prefix="replay-", dir=OUTPUT) as tmp:
        scratch = Path(tmp)
        copy = scratch / "identical.db"
        shutil.copyfile(database, copy)
        require(
            not copy.samefile(database) and copy.read_bytes() == database.read_bytes(),
            "copy_control",
        )
        publication = scratch / "publication"
        shutil.copytree(original, publication)
        with (
            patch.object(consumer, "PUBLICATION", publication),
            _serve(database) as registered,
            _serve(copy) as copied,
            httpx.Client(
                timeout=60, trust_env=False, headers={"Origin": LOCAL_WEB_ORIGINS[0]}
            ) as client,
        ):
            one, two = (_read(client, registered, s) for s in (review, draft))
            require(
                one.lookups[0].status == two.lookups[0].status == "available"
                and len(one.assessments) == len(one.accounting_records) == 1
                and one.assessments == two.assessments
                and one.accounting_records == two.accounting_records,
                "shared_api_delivery",
            )
            other = _read(client, registered, adjacent)
            require(
                other.lookups[0].reason == "exact_selection_unavailable"
                and not other.assessments
                and not other.accounting_records
                and other.generation_totals is None,
                "adjacent_version_admitted",
            )
            for s in (review, draft):
                denied = _read(client, copied, s)
                require(
                    denied.lookups[0].reason == "unregistered_workspace"
                    and not denied.assessments
                    and not denied.accounting_records
                    and denied.generation_totals is None,
                    "copy_admitted",
                )
            web = ROOT / "apps/web"
            report = OUTPUT / "inspector.xml"
            subprocess.run(
                [
                    "node",
                    str(web / "node_modules/vitest/vitest.mjs"),
                    "run",
                    "src/components/Q008Assessment.test.tsx",
                    "--reporter=junit",
                    f"--outputFile={report}",
                ],
                cwd=web,
                env={
                    **os.environ,
                    "OH_Q008_API_REPLAY": "1",
                    "OH_Q008_INSPECTOR_REPLAY": "0",
                    "VITE_API_URL": registered,
                    "OH_Q008_COPY_URL": copied,
                    "OH_Q008_API_SCRATCH": scratch.name,
                },
                check=True,
                timeout=220,
            )
            tests = ElementTree.parse(report).findall(".//testcase")
            require(
                any("refreshes a damaged publication over HTTP" in t.get("name", "") for t in tests)
                and any("identical-ID workspace over HTTP" in t.get("name", "") for t in tests)
                and all(
                    not list(t) or all(c.tag not in {"error", "failure", "skipped"} for c in t)
                    for t in tests
                ),
                "missing_api_inspector_checks",
            )
            for s in (review, draft):
                damaged = _read(client, registered, s)
                require(
                    damaged.lookups[0].reason == "publication_member_changed"
                    and not damaged.assessments
                    and not damaged.accounting_records
                    and damaged.generation_totals is None,
                    "damaged_display",
                )
    require(
        stamps == {p: (storage._sha(p.read_bytes()), p.stat().st_mtime_ns) for p in originals}
        and set(database.parent.iterdir()) == {database},
        "source_changed_during_qualification",
    )
    summary = {
        "registered_versions": [review.version_id, draft.version_id],
        "delivery_id": one.accounting_records[0].delivery_id,
        "generation_usage": one.accounting_records[0].generation_usage.model_dump(),
        "same_text_adjacent_version": "exact_selection_unavailable",
        "identical_copy": "unregistered_workspace",
        "damaged_refresh": "publication_member_changed",
        "inspector_tests": len(tests),
        "original_files_preserved": len(originals),
        "provider_calls": 0,
    }
    (OUTPUT / "verification.json").write_bytes(encoded(summary))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    qualify()
