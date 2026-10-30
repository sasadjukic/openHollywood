"""Real file IO with authored, sealed probes; no gateway, network or SQLite use."""

from __future__ import annotations

import hashlib
import json
import socket
import sqlite3
from pathlib import Path
from typing import Any

import pytest
from open_hollywood_api.services import probe_review_export as service
from open_hollywood_engine.evaluations.probe_review_evidence import relative_path
from open_hollywood_engine.evaluations.review_evidence import EvidenceError
from open_hollywood_engine.secrets import SecretLeakError

from scripts.probe_review_export import main
from tests.probe_review_fixtures import encoded, make_probe_fixture


@pytest.fixture(autouse=True)
def no_external_io(monkeypatch: pytest.MonkeyPatch) -> None:
    def forbidden(*_args: Any, **_kwargs: Any) -> Any:
        raise AssertionError("Probe exports must not use a network or database")

    monkeypatch.setattr(socket.socket, "connect", forbidden)
    monkeypatch.setattr(socket, "create_connection", forbidden)
    monkeypatch.setattr(sqlite3, "connect", forbidden)


@pytest.mark.parametrize(
    "retry,unmet,post",
    [(False, False, False), (True, False, False), (False, True, False), (False, False, True)],
)
def test_authored_archive_export_and_identical_replay(
    tmp_path: Path, retry: bool, unmet: bool, post: bool
) -> None:
    fixture = make_probe_fixture(tmp_path, retry=retry, unmet=unmet, post=post)
    contract = fixture.seal()
    before = {p: p.read_bytes() for p in tmp_path.rglob("*.json")}
    export = service.collect_probe_export(fixture.live, (fixture.trial,), _contract=contract)
    projection = export.entries[0].projection
    assert projection.production_invocation_id is projection.canonical_critique_version_id is None
    assert projection.successful_attempt == (2 if retry else 1)
    assert len(projection.failed_predecessors) == int(retry)
    assert all(c.saved_check.status == ("unmet" if unmet else "met") for c in projection.checks)
    assert all(c.raw_check["recommended_resolution"] is None for c in projection.checks)
    if unmet:
        assert all(
            c.advice_origin == "application_rendered_shared_conditions" for c in projection.checks
        )
    if post:
        old = [s for s in projection.sources if s.old_prose_recovered_after_review]
        assert len(old) == 1 and old[0].visible_repair_quotations == ("She waits.",)
    else:
        span = projection.checks[1].comparisons[0].selected
        assert span.quote == "She decides to investigate." and span.start > 0
    destination = tmp_path / "export"
    assert service.write_probe_export(destination, export, _contract=contract) == "created"
    assert len(list(destination.iterdir())) == 4
    saved = service.ProbeExportEntry.model_validate_json(
        (destination / (fixture.trial + ".json")).read_text(encoding="utf-8")
    )
    assert saved == export.entries[0]
    manifest = json.loads((destination / "manifest.json").read_text())
    for name, digest in manifest["files_sha256"].items():
        assert hashlib.sha256((destination / name).read_bytes()).hexdigest() == digest
    mtimes = {p: p.stat().st_mtime_ns for p in destination.iterdir()}
    assert service.write_probe_export(destination, export, _contract=contract) == "reused"
    assert mtimes == {p: p.stat().st_mtime_ns for p in destination.iterdir()}
    assert all(p.read_bytes() == data for p, data in before.items())


@pytest.mark.parametrize(
    "corruption", ["capture", "missing_receipt", "changed_seal", "unsealed_extra"]
)
def test_missing_or_modified_archive_never_exports(tmp_path: Path, corruption: str) -> None:
    fixture = make_probe_fixture(tmp_path)
    contract = fixture.seal()
    if corruption == "capture":
        fixture.path("live", f"probes/{fixture.trial}/attempt-1-model-output.json").write_text(
            "{}", encoding="utf-8"
        )
    elif corruption == "missing_receipt":
        fixture.path("live", f"probes/{fixture.trial}/attempt-1-result.json").unlink()
    elif corruption == "changed_seal":
        fixture.path("live", "closure.json").write_text("{}", encoding="utf-8")
    else:
        fixture.path("live", f"probes/{fixture.trial}/manifest.json").write_text(
            "{}", encoding="utf-8"
        )
    with pytest.raises(ValueError):
        service.collect_probe_export(fixture.live, (fixture.trial,), _contract=contract)
    assert not (tmp_path / "export").exists()


@pytest.mark.parametrize(
    "corruption", ["attempt", "failed", "advice", "target", "handle", "summary", "prompt", "origin"]
)
def test_even_trusted_authored_archives_require_consistent_records(
    tmp_path: Path, corruption: str
) -> None:
    fixture = make_probe_fixture(tmp_path, unmet=True)
    receipt = fixture.documents["live", f"probes/{fixture.trial}/attempt-1-result.json"]
    if corruption == "attempt":
        receipt["attempt"] = 2
    elif corruption == "failed":
        receipt["status"] = "failed"
    elif corruption == "advice":
        receipt["scene_boundary_audit"]["assignment_checks"]["outcome"][
            "recommended_resolution"
        ] = "Invented advice."
    elif corruption == "target":
        receipt["result"]["target_artifact_version_id"] = "00000000-0000-0000-0000-000000000001"
    elif corruption == "handle":
        receipt["scene_boundary_audit"]["assignment_checks"]["outcome"]["draft_evidence_refs"] = [
            "foreign"
        ]
    elif corruption == "summary":
        fixture.documents["live", f"probes/{fixture.trial}/summary.json"]["attempts"] = 2
    elif corruption == "prompt":
        receipt["prompt_sha256"] = "0" * 64
    else:
        fixture.documents["live", f"probes/{fixture.trial}/manifest.json"][
            "synthetic_unapproved_context"
        ] = False
    contract = fixture.seal()
    with pytest.raises(ValueError):
        service.collect_probe_export(fixture.live, (fixture.trial,), _contract=contract)


def test_post_review_requires_exact_writer_result(tmp_path: Path) -> None:
    fixture = make_probe_fixture(tmp_path, post=True)
    fixture.documents["live", "probes/s1-control-writer-evidence/attempt-1-result.json"]["result"][
        "prose"
    ] = "Substituted revision."
    contract = fixture.seal()
    with pytest.raises(EvidenceError, match="probe_writer_lineage_mismatch"):
        service.collect_probe_export(fixture.live, (fixture.trial,), _contract=contract)


@pytest.mark.parametrize("mutation", ["comparison", "dependency", "original_review"])
def test_supplied_export_claims_are_recomputed(tmp_path: Path, mutation: str) -> None:
    fixture = make_probe_fixture(tmp_path)
    contract = fixture.seal()
    export = service.collect_probe_export(fixture.live, (fixture.trial,), _contract=contract)
    body = export.model_dump(mode="json")
    entry = body["entries"][0]
    if mutation == "comparison":
        entry["projection"]["checks"][0]["comparisons"][0]["status"] = "exact"
    elif mutation == "dependency":
        entry["snapshot"]["dependencies"] = []
    else:
        entry["projection"]["normalized_review"]["verdict"] = "reject"
    changed = service.ProbeExport.model_validate_json(json.dumps(body))
    with pytest.raises(EvidenceError):
        service.write_probe_export(tmp_path / "bad", changed, _contract=contract)
    assert not (tmp_path / "bad").exists()


@pytest.mark.parametrize("kind", ["partial", "changed", "source_changed", "protected", "oversized"])
def test_publication_refuses_conflicts_without_overwriting(
    tmp_path: Path, kind: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    fixture = make_probe_fixture(tmp_path)
    contract = fixture.seal()
    export = service.collect_probe_export(fixture.live, (fixture.trial,), _contract=contract)
    destination = tmp_path / "export"
    if kind == "partial":
        destination.mkdir()
        (destination / "index.md").write_text("Existing partial output.", encoding="utf-8")
    elif kind == "changed":
        service.write_probe_export(destination, export, _contract=contract)
        (destination / "index.md").write_text("Existing changed output.", encoding="utf-8")
    elif kind == "source_changed":
        fixture.path("live", f"probes/{fixture.trial}/summary.json").write_text(
            "{}", encoding="utf-8"
        )
    elif kind == "protected":
        destination = fixture.live / "new-output"
    else:
        monkeypatch.setattr(service, "MAX_EXPORT_BYTES", 1)
    before = {p: p.read_bytes() for p in destination.iterdir()} if destination.exists() else {}
    with pytest.raises(EvidenceError):
        service.write_probe_export(destination, export, _contract=contract)
    assert all(p.read_bytes() == data for p, data in before.items())
    if not before:
        assert not destination.exists()


def test_credentials_abort_before_publication(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fixture = make_probe_fixture(tmp_path)
    sentinel = "fake-local-export-key-9182736450"
    fixture.documents["live", f"probes/{fixture.trial}/attempt-1-result.json"]["result"][
        "summary"
    ] = sentinel
    contract = fixture.seal()
    monkeypatch.setenv("OLLAMA_API_KEY", sentinel)
    with pytest.raises(SecretLeakError):
        service.collect_probe_export(fixture.live, (fixture.trial,), _contract=contract)
    assert not (tmp_path / "export").exists()


@pytest.mark.parametrize(
    "path", ["../escape", "/absolute", "C:/drive", "folder\\file", "a/../b", "a//b"]
)
def test_paths_cannot_escape_archive(path: str) -> None:
    with pytest.raises(EvidenceError):
        relative_path(path)


def test_even_trusted_seal_cannot_escape_root(tmp_path: Path) -> None:
    fixture = make_probe_fixture(tmp_path)
    contract = fixture.seal()
    path = fixture.path("live", "closure.json")
    closure = json.loads(path.read_text())
    closure["evidence_sha256"]["../escape.json"] = "0" * 64
    path.write_bytes(encoded(closure))
    contract = contract.model_copy(
        update={"live_closure_sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
    )
    with pytest.raises(EvidenceError, match="unsafe_archive_path"):
        service.collect_probe_export(fixture.live, (fixture.trial,), _contract=contract)


@pytest.mark.parametrize("ids", [(), ("same", "same"), tuple(f"trial-{i}" for i in range(13))])
def test_selection_limit_precedes_archive_reads(tmp_path: Path, ids: tuple[str, ...]) -> None:
    with pytest.raises(EvidenceError, match="invalid_probe_selection"):
        service.collect_probe_export(tmp_path / "absent", ids)


def test_cli_unknown_contract_errors_do_not_expose_source(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    fixture = make_probe_fixture(tmp_path)
    fixture.seal()
    assert (
        main(
            [
                "--archive",
                str(fixture.live),
                "--trial-id",
                fixture.trial,
                "--output",
                str(tmp_path / "output"),
            ]
        )
        == 2
    )
    assert "Authored fixture" not in capsys.readouterr().out
    assert not (tmp_path / "output").exists()
