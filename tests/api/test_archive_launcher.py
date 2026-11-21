"""Portable startup checks for the two read-only operator registrations."""

from __future__ import annotations

import hashlib
import shutil
import sqlite3
from contextlib import closing
from pathlib import Path

import pytest
from open_hollywood_api.services import production_association_lookup as associations
from open_hollywood_api.services import q008_inspector as q008

from scripts.open_archive import snapshot


def test_archive_snapshot_requires_the_registered_sealed_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = tmp_path / "sealed.db"
    source.write_bytes(b"sealed navigation image")
    stat = source.stat()
    monkeypatch.setattr(
        q008,
        "REGISTERED",
        q008.WorkspacePin(
            source, stat.st_dev, stat.st_ino, hashlib.sha256(source.read_bytes()).hexdigest()
        ),
    )
    dest = tmp_path / "viewer.db"
    assert snapshot("q008", dest) == source
    assert dest.read_bytes() == source.read_bytes()
    old = source.rename(tmp_path / "previous.db")
    shutil.copyfile(old, source)
    with pytest.raises(ValueError, match="workspace_replaced"):
        snapshot("q008", tmp_path / "refused.db")
    assert not (tmp_path / "refused.db").exists()


def test_ordinary_snapshot_includes_committed_wal_rows(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = tmp_path / "ordinary.db"
    dest = tmp_path / "navigation.db"
    with closing(sqlite3.connect(source)) as writer:
        writer.execute("PRAGMA journal_mode=WAL")
        writer.execute("PRAGMA wal_autocheckpoint=0")
        writer.execute("CREATE TABLE claims (id INTEGER PRIMARY KEY)")
        writer.execute("INSERT INTO claims VALUES (8)")
        writer.commit()
        stat = source.stat()
        monkeypatch.setattr(
            associations,
            "REGISTERED",
            (associations._Workspace("fixture", source, stat.st_dev, stat.st_ino, "fixture"),),
        )
        wal = source.with_name(source.name + "-wal")
        before = [(path.read_bytes(), path.stat().st_mtime_ns) for path in (source, wal)]
        assert snapshot("ordinary", dest) == source
        assert before == [(path.read_bytes(), path.stat().st_mtime_ns) for path in (source, wal)]
    with closing(sqlite3.connect(dest.as_uri() + "?mode=ro&immutable=1", uri=True)) as reader:
        assert reader.execute("SELECT id FROM claims").fetchall() == [(8,)]
