"""Qualify Q013 archive navigation and return to ordinary provenance in Google Chrome."""

from __future__ import annotations

import json
import os
import shutil
import sqlite3
import subprocess
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import httpx
from open_hollywood_api.persistence.database import DATABASE_PATH_VARIABLE
from open_hollywood_api.readonly_workspace import navigation_app, serve_loopback
from open_hollywood_api.services import assessment_completion as storage
from open_hollywood_api.services import production_association_lookup as associations
from open_hollywood_api.services import q013_inspector as api
from open_hollywood_api.services.assessment_inspector_workspace import registered_image
from open_hollywood_api.workspace_models import ProjectWorkspace
from open_hollywood_engine.evaluations.assessment_completion import encoded
from open_hollywood_engine.evaluations.review_evidence import require
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool

from scripts import lookup_saved_review_completion as consumer
from scripts.open_archive import ROOT, mount_viewer, snapshot
from scripts.qualify_q008_inspector import _details
from scripts.qualify_q013_inspector import _neighbor

OUTPUT = ROOT / "data/diagnostics/q013-browser-2026-11-22"
WEB = ROOT / "apps/web"


@contextmanager
def _server(authority: Path, navigation: Path, site: Path) -> Iterator[str]:
    uri = navigation.as_uri() + "?mode=ro&immutable=1"
    engine = create_engine(
        "sqlite+pysqlite://",
        poolclass=NullPool,
        creator=lambda: sqlite3.connect(uri, uri=True, check_same_thread=False),
    )
    try:
        app = navigation_app(authority, engine, consumer.lookup, assessment_view="Q013")
        mount_viewer(app, site)
        require(all(set(ops) == {"get"} for ops in app.openapi()["paths"].values()), "write_route")
        with serve_loopback(app) as url:
            yield url
    finally:
        engine.dispose()


def _stamps() -> dict[Path, tuple[str, int]]:
    (ordinary,) = associations.REGISTERED
    paths = [
        *api.SOURCE.rglob("*"),
        *consumer.Q013.directory.iterdir(),
        ordinary.path,
        ordinary.path.with_name(ordinary.path.name + "-wal"),
    ]
    return {p: (storage._sha(p.read_bytes()), p.stat().st_mtime_ns) for p in paths if p.is_file()}


def qualify() -> None:
    before = _stamps()
    review, draft = api._registered_pair()
    authority = api.REGISTERED.path
    OUTPUT.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix="replay-", dir=OUTPUT) as tmp:
        scratch = Path(tmp)
        copy = scratch / "identical.db"
        copy.write_bytes(registered_image(authority, api.REGISTERED))
        require(
            not copy.samefile(authority) and copy.read_bytes() == authority.read_bytes(),
            "workspace_copy",
        )
        # Read artifact navigation from a private snapshot. The two API origins each
        # authenticate assessment and provenance against their own physical authority.
        navigation = scratch / "navigation.db"
        shutil.copyfile(copy, navigation)
        selections = {
            "review": review,
            "draft": draft,
            "adjacent": _neighbor(navigation, draft),
            "adjacentReview": _neighbor(navigation, review),
        }
        details = _details(navigation, selections)
        require(
            [details[k].selected_version.version_number for k in selections] == [3, 1, 2, 2],
            "unexpected_versions",
        )
        (claim,) = consumer.lookup((review, draft)).assessments
        site = scratch / "site"
        subprocess.run(
            ["node", str(WEB / "node_modules/vite/bin/vite.js"), "build", "--outDir", str(site)],
            cwd=WEB,
            check=True,
            timeout=120,
        )
        with (
            _server(authority, navigation, site) as registered,
            _server(copy, navigation, site) as copied,
            httpx.Client(trust_env=False) as client,
        ):
            shells = [
                ProjectWorkspace.model_validate_json(
                    client.get(f"{base}/api/v1/projects/{review.project_id}/workspace")
                    .raise_for_status()
                    .content
                )
                for base in (registered, copied)
            ]
            require(
                shells[0] == shells[1] and shells[0].saved_assessment_view == "Q013",
                "workspace_display_registration",
            )
            (scratch / "cases.json").write_bytes(
                encoded(
                    {
                        "project": shells[0].project.name,
                        "selections": {k: s.model_dump(mode="json") for k, s in selections.items()},
                        "titles": {k: d.artifact.title for k, d in details.items()},
                        "delivery": claim.delivery_id,
                        "claim": claim.claim,
                    }
                )
            )

            def run(phase: str) -> None:
                subprocess.run(
                    ["node", "e2e/q013-navigation.mjs", phase, registered, copied, str(scratch)],
                    cwd=WEB,
                    check=True,
                    timeout=360,
                )

            run("archive")
            publication = scratch / "publication"
            shutil.copytree(consumer.Q013.directory, publication)
            with patch.object(consumer, "Q013", replace(consumer.Q013, directory=publication)):
                run("damage")

        ordinary_db = scratch / "ordinary.db"
        ordinary = snapshot("ordinary", ordinary_db)
        with (
            patch.dict(os.environ, {DATABASE_PATH_VARIABLE: str(ordinary)}),
            _server(ordinary, ordinary_db, site) as url,
        ):
            control = subprocess.run(
                ["node", "e2e/archive-launcher.mjs", "ordinary", url, "Q013"],
                cwd=WEB,
                check=True,
                timeout=240,
                stdout=subprocess.PIPE,
            )
        report = {
            "project": shells[0].project.name,
            "archive": json.loads((scratch / "archive-result.json").read_bytes()),
            "damaged_refresh": json.loads((scratch / "damage-result.json").read_bytes()),
            "ordinary_provenance": json.loads(control.stdout),
        }
        require(copy.read_bytes() == authority.read_bytes(), "workspace_copy_changed")
    require(
        before == _stamps() and set(authority.parent.iterdir()) == {authority},
        "original_sources_changed",
    )
    report.update(original_files_preserved=len(before), provider_calls=0)
    (OUTPUT / "verification.json").write_bytes(encoded(report))
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    qualify()
