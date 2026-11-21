"""Check the public launcher as a subprocess, including browser navigation and shutdown."""

from __future__ import annotations

import hashlib
import json
import os
import re
import socket
import subprocess
import sys
import time
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.parse import urlsplit

import httpx
from open_hollywood_api.services import production_association_lookup as associations
from open_hollywood_api.services import q008_inspector as q008
from open_hollywood_engine.evaluations.review_evidence import require

from scripts.lookup_q008_completion import PUBLICATION
from scripts.open_archive import ROOT

OUTPUT = ROOT / "data/diagnostics/archive-launcher-2026-11-21"


def source_stamps() -> dict[Path, tuple[str, int]]:
    archive = q008.REGISTERED.path
    ordinary = associations.REGISTERED[0].path
    # SHM is SQLite's reader coordination file. Main and WAL contain the saved rows.
    paths = [*archive.parent.iterdir(), *PUBLICATION.iterdir(), ordinary]
    wal = ordinary.with_name(ordinary.name + "-wal")
    if wal.exists():
        paths.append(wal)
    return {p: (hashlib.sha256(p.read_bytes()).hexdigest(), p.stat().st_mtime_ns) for p in paths}


def exercise(mode: str, port: int, root: Path) -> tuple[int, dict[str, object]]:
    scratch = root / mode
    scratch.mkdir()
    log = root / f"{mode}.log"
    with (
        log.open("wb") as output,
        subprocess.Popen(
            [
                sys.executable,
                "-u",
                "-m",
                "scripts.open_archive",
                "--workspace",
                mode,
                "--port",
                str(port),
            ],
            cwd=ROOT,
            env={**os.environ, "TMP": str(scratch), "TEMP": str(scratch), "TMPDIR": str(scratch)},
            stdin=subprocess.PIPE,
            stdout=output,
            stderr=subprocess.STDOUT,
        ) as proc,
    ):
        try:
            deadline = time.monotonic() + 60
            while True:
                lines = log.read_text(encoding="utf-8", errors="replace")
                match = re.search(
                    rf"Read-only {mode} workspace at (http://127\.0\.0\.1:[0-9]+)", lines
                )
                if match:
                    break
                if proc.poll() is not None or time.monotonic() >= deadline:
                    raise RuntimeError(f"Launcher failed to start: {lines}")
                time.sleep(0.1)
            url = match[1]
            actual_port = urlsplit(url).port
            assert actual_port is not None
            require(port in (0, actual_port), "unexpected_launcher_port")
            (session,) = scratch.glob("open-hollywood-archive-*")
            require((session / "navigation.db").is_file(), "missing_private_snapshot")
            with httpx.Client(base_url=url, trust_env=False) as client:
                methods = client.get("/openapi.json").raise_for_status().json()["paths"]
                require(
                    all(set(ops) == {"get"} for ops in methods.values()), "unexpected_write_route"
                )
                require(
                    client.post("/api/v1/projects", json={}).status_code == 405, "write_allowed"
                )
                require(client.get("/index.html").status_code == 404, "studio_entry_exposed")
            result = subprocess.run(
                ["node", "e2e/archive-launcher.mjs", mode, url],
                cwd=ROOT / "apps/web",
                stdout=subprocess.PIPE,
                check=True,
                timeout=240,
            )
            observation: dict[str, object] = json.loads(result.stdout)
        finally:
            try:
                proc.communicate(input=b"\n", timeout=45)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()
                raise
    require(proc.returncode == 0 and "Archive viewer closed." in log.read_text(), "unclean_exit")
    require(not any(scratch.iterdir()), "snapshot_not_removed")
    # Reacquiring the same listener also distinguishes a shutdown from a timed-out GET.
    with socket.create_server(("127.0.0.1", actual_port)) as probe:
        require(probe.getsockname()[1] == actual_port, "listener_not_released")
    observation.update(
        exit_code=proc.returncode, listener_closed=True, temporary_directory_empty=True
    )
    return actual_port, observation


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    before = source_stamps()
    with TemporaryDirectory(prefix="replay-", dir=OUTPUT) as tmp:
        port, archive = exercise("q008", 0, Path(tmp))
        _, ordinary = exercise("ordinary", port, Path(tmp))
    require(before == source_stamps(), "source_changed")
    report = {
        "runs": [archive, ordinary],
        "port_reused": True,
        "source_files_preserved": len(before),
        "provider_calls": 0,
    }
    raw = json.dumps(report, indent=2) + "\n"
    (OUTPUT / "verification.json").write_text(raw, encoding="utf-8")
    print(raw)


if __name__ == "__main__":
    main()
