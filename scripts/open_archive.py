"""Open the registered Q008, Q013 or ordinary workspace in a read-only local viewer."""

from __future__ import annotations

import argparse
import os
import sqlite3
from contextlib import closing, suppress
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Literal

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from open_hollywood_api.persistence.database import DATABASE_PATH_VARIABLE
from open_hollywood_api.readonly_workspace import navigation_app, serve_loopback
from open_hollywood_api.services import production_association_lookup as associations
from open_hollywood_api.services import q008_inspector as q008
from open_hollywood_api.services import q013_inspector as q013
from open_hollywood_api.services.assessment_inspector_workspace import registered_image
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
from starlette.middleware.trustedhost import TrustedHostMiddleware

from scripts import lookup_q008_completion, lookup_saved_review_completion

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "apps/web/dist"
Workspace = Literal["q008", "q013", "ordinary"]


def snapshot(workspace: Workspace, destination: Path) -> Path:
    """Return the physical authority after making a private navigation snapshot."""
    if workspace in ("q008", "q013"):
        pin = q013.REGISTERED if workspace == "q013" else q008.REGISTERED
        destination.write_bytes(registered_image(pin.path, pin))
        return pin.path

    (registered,) = associations.REGISTERED
    associations._source_stamp(registered)
    source = registered.path
    # A live SQLite workspace may have committed rows in the WAL. Use its backup
    # API for a consistent snapshot, retaining the original as the provenance authority.
    with (
        closing(sqlite3.connect(source.as_uri() + "?mode=ro", uri=True)) as reader,
        closing(sqlite3.connect(destination)) as writer,
    ):
        reader.backup(writer)
    associations._source_stamp(registered)
    return source


def mount_viewer(app: FastAPI, site: Path) -> None:
    entry = site / "archive.html"
    if not entry.is_file() or not (site / "assets").is_dir():
        raise ValueError("Build the archive viewer first with pnpm build from the project root.")
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["127.0.0.1", "localhost"])

    @app.get("/", include_in_schema=False)
    def index() -> FileResponse:
        return FileResponse(entry, headers={"Cache-Control": "no-store"})

    @app.get("/open_hollywood_logo_no_bg.png", include_in_schema=False)
    def logo() -> FileResponse:
        return FileResponse(site / "open_hollywood_logo_no_bg.png")

    app.mount("/assets", StaticFiles(directory=site / "assets"))


def launch(workspace: Workspace, port: int) -> None:
    with TemporaryDirectory(prefix="open-hollywood-archive-") as temp:
        navigation = Path(temp) / "navigation.db"
        authority = snapshot(workspace, navigation)
        # This dedicated process must revalidate against the selected registration.
        os.environ[DATABASE_PATH_VARIABLE] = str(authority)
        uri = navigation.as_uri() + "?mode=ro&immutable=1"
        engine = create_engine(
            "sqlite+pysqlite://",
            poolclass=NullPool,
            creator=lambda: sqlite3.connect(uri, uri=True, check_same_thread=False),
        )
        try:
            if workspace == "q013":
                app = navigation_app(
                    authority, engine, lookup_saved_review_completion.lookup, assessment_view="Q013"
                )
            else:
                app = navigation_app(authority, engine, lookup_q008_completion.lookup)
            mount_viewer(app, SITE)
            with serve_loopback(app, port) as url:
                print(f"Read-only {workspace} workspace at {url}", flush=True)
                with suppress(KeyboardInterrupt, EOFError):
                    input("Press Enter or Ctrl+C to close the viewer.\n")
        finally:
            engine.dispose()
    print("Archive viewer closed.", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", choices=("q008", "q013", "ordinary"), default="q008")
    parser.add_argument(
        "--port", type=int, default=0, help="Loopback port (default: automatically assigned)"
    )
    args = parser.parse_args()
    if not 0 <= args.port <= 65535:
        parser.error("--port must be between 0 and 65535")
    try:
        launch(args.workspace, args.port)
    except (ValueError, OSError, sqlite3.Error, RuntimeError) as exc:
        parser.exit(1, f"Could not open archive viewer: {exc}\n")


if __name__ == "__main__":
    main()
