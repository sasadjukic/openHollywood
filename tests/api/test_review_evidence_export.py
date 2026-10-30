"""Real migrated SQLite, fake gateways and offline operator export boundaries."""

from __future__ import annotations

import hashlib
import json
import sqlite3
from copy import deepcopy
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

import httpx
import pytest
from open_hollywood_api.persistence.models import (
    AgentInvocation,
    InvocationStatus,
    agent_invocation_inputs,
)
from open_hollywood_api.services.review_evidence_export import (
    collect_export,
    inventory,
    readonly_connection,
    render_export,
    write_export,
)
from open_hollywood_engine.evaluations.review_evidence import EvidenceError, ReviewEvidenceExport
from open_hollywood_engine.secrets import SecretLeakError
from sqlalchemy import delete, select

from scripts.review_evidence_export import main
from tests.api.test_production_fulfillment import Prepared
from tests.api.test_production_fulfillment import prepared as _prepared

prepared = _prepared


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture(autouse=True)
def no_http(monkeypatch: pytest.MonkeyPatch) -> None:
    def blocked(*args: Any, **kwargs: Any) -> Any:
        raise AssertionError("operator export must never use HTTP")

    monkeypatch.setattr(httpx.HTTPTransport, "handle_request", blocked)
    monkeypatch.setattr(httpx.AsyncHTTPTransport, "handle_async_request", blocked)


def source_id(prepared: Prepared) -> UUID:
    with prepared.sessions() as session:
        return prepared.source(session).id


def database_hashes(path: Path) -> dict[str, str]:
    return {
        p.name: hashlib.sha256(p.read_bytes()).hexdigest()
        for p in (path, Path(str(path) + "-wal"))
        if p.exists()
    }


@pytest.mark.anyio
async def test_export_inventory_and_reopen_are_read_only_and_reproducible(
    prepared: Prepared,
    migrated_database_path: Path,
    tmp_path: Path,
) -> None:
    invocation_id = source_id(prepared)
    before = database_hashes(migrated_database_path)
    meta = inventory(migrated_database_path)
    assert [r.invocation_id for r in meta.rows if r.candidate] == [str(invocation_id)]
    exported = collect_export(migrated_database_path, (invocation_id,))
    entry = exported.entries[0]
    assert entry.reason == "compatible" and entry.snapshot is not None
    assert len(entry.evidence) == 2 and entry.original_critique is not None
    with prepared.sessions() as session:
        source = prepared.source(session)
        assert entry.original_native_audit == source.request_settings["scene_boundary_audit"]
        assert entry.original_critique.content == source.output_versions[0].content
        assert entry.snapshot.invocation.attempt == source.retry_count + 1
    path = tmp_path / "export"
    assert write_export(path, exported) == "created"
    files = {p.name: p.read_bytes() for p in path.iterdir()}
    times = {p.name: p.stat().st_mtime_ns for p in path.iterdir()}
    assert write_export(path, collect_export(migrated_database_path, (invocation_id,))) == "reused"
    assert files == {p.name: p.read_bytes() for p in path.iterdir()}
    assert times == {p.name: p.stat().st_mtime_ns for p in path.iterdir()}
    assert ReviewEvidenceExport.model_validate_json(files["review-evidence.json"]) == exported
    assert before == database_hashes(migrated_database_path)
    assert entry.original_revision_alignment == "unresolved_not_selected"
    assert not entry.writer_dispatch_authorized


@pytest.mark.anyio
@pytest.mark.parametrize("prepared", [True], indirect=True)
async def test_only_successful_retry_creator_supplies_evidence(
    prepared: Prepared,
    migrated_database_path: Path,
) -> None:
    with prepared.sessions() as session:
        success = prepared.source(session)
        failed = next(
            i
            for i in session.scalars(select(AgentInvocation))
            if i.status is InvocationStatus.FAILED
        )
        assert {v.id for v in failed.input_versions} == {v.id for v in success.input_versions}
        result = collect_export(migrated_database_path, (failed.id, success.id))
    assert result.entries[0].reason == "not_successful_ordinary_critic"
    assert result.entries[1].reason == "compatible"
    assert result.entries[1].snapshot is not None
    assert result.entries[1].snapshot.invocation.attempt == 2


@pytest.mark.anyio
@pytest.mark.parametrize(
    "bad,reason",
    [
        ("version", "unsupported_contract"),
        ("run_contract", "unsupported_contract"),
        ("audit", "unsupported_contract"),
        ("prompt", "unavailable_view"),
        ("candidate", "invalid_provenance"),
        ("missing_input", "missing_source"),
        ("incomplete", "invalid_provenance"),
    ],
)
async def test_non_results_preserve_original_review_without_partial_comparisons(
    prepared: Prepared,
    migrated_database_path: Path,
    bad: str,
    reason: str,
) -> None:
    invocation_id = source_id(prepared)
    with prepared.sessions.begin() as session:
        source = prepared.source(session)
        original = deepcopy(source.output_versions[0].content)
        settings = deepcopy(source.request_settings)
        if bad == "version":
            settings["prompt_template_version"] = "59"
        elif bad == "run_contract":
            source.workflow_run.input_state = {
                **source.workflow_run.input_state,
                "production_prompt_template_version": "59",
            }
        elif bad == "audit":
            settings["scene_boundary_audit"]["schema_version"] = "6"
        elif bad == "prompt":
            source.prompt_text = None
        elif bad == "candidate":
            settings["scene_boundary_audit"]["candidate_version_id"] = str(uuid4())
        elif bad == "missing_input":
            # Fault injection into this disposable fixture only; preserve ORM immutability.
            session.execute(
                delete(agent_invocation_inputs).where(
                    agent_invocation_inputs.c.agent_invocation_id == source.id,
                    agent_invocation_inputs.c.artifact_version_id == source.input_versions[-1].id,
                )
            )
        else:
            del settings["scene_boundary_audit"]["assignment_checks"]["outcome"]
        source.request_settings = settings
    result = collect_export(migrated_database_path, (invocation_id,)).entries[0]
    assert result.reason == reason and not result.evidence
    assert result.original_critique is not None and result.original_critique.content == original


@pytest.mark.anyio
async def test_conflicting_audit_does_not_overwrite_existing_export(
    prepared: Prepared,
    migrated_database_path: Path,
    tmp_path: Path,
) -> None:
    invocation_id = source_id(prepared)
    path = tmp_path / "export"
    write_export(path, collect_export(migrated_database_path, (invocation_id,)))
    before = {p.name: p.read_bytes() for p in path.iterdir()}
    with prepared.sessions.begin() as session:
        source = prepared.source(session)
        settings = deepcopy(source.request_settings)
        settings["scene_boundary_audit"]["assignment_checks"]["outcome"]["assessment"] += (
            " Changed."
        )
        source.request_settings = settings
    with pytest.raises(EvidenceError, match="export_conflict"):
        write_export(path, collect_export(migrated_database_path, (invocation_id,)))
    assert before == {p.name: p.read_bytes() for p in path.iterdir()}


@pytest.mark.anyio
async def test_readonly_sqlite_rejects_write_even_if_query_only_disabled(
    prepared: Prepared,
    migrated_database_path: Path,
) -> None:
    with readonly_connection(migrated_database_path) as connection:
        assert connection.execute("PRAGMA query_only").fetchone()[0] == 1
        connection.execute("PRAGMA query_only=OFF")
        with pytest.raises(sqlite3.OperationalError, match="readonly"):
            connection.execute("UPDATE agent_invocations SET prompt_text='changed'")
        assert connection.total_changes == 0


@pytest.mark.anyio
async def test_read_transaction_is_consistent_during_another_writer_commit(
    prepared: Prepared,
    migrated_database_path: Path,
) -> None:
    invocation_id = source_id(prepared)
    with readonly_connection(migrated_database_path) as reader:
        query = "SELECT request_settings FROM agent_invocations WHERE id=?"
        before = reader.execute(query, (invocation_id.hex,)).fetchone()[0]
        with prepared.sessions.begin() as session:
            source = prepared.source(session)
            source.request_settings = {**source.request_settings, "offline_test_marker": True}
        assert reader.execute(query, (invocation_id.hex,)).fetchone()[0] == before
    with readonly_connection(migrated_database_path) as reader:
        assert reader.execute(query, (invocation_id.hex,)).fetchone()[0] != before


@pytest.mark.anyio
async def test_cli_exports_offline_and_bounds_selection(
    prepared: Prepared,
    migrated_database_path: Path,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    invocation_id = source_id(prepared)
    args = [
        "export",
        "--database",
        str(migrated_database_path),
        "--output",
        str(tmp_path / "cli"),
        "--invocation-id",
        str(invocation_id),
    ]
    assert main(args) == 0
    assert json.loads(capsys.readouterr().out)["compatible"] == 1
    assert main(args) == 0
    assert json.loads(capsys.readouterr().out)["status"] == "reused"
    with pytest.raises(EvidenceError, match="invalid_selection"):
        collect_export(migrated_database_path, (invocation_id,) * 2)
    with pytest.raises(EvidenceError, match="invalid_selection"):
        collect_export(migrated_database_path, tuple(uuid4() for _ in range(13)))
    assert collect_export(migrated_database_path, (uuid4(),)).entries[0].reason == "not_found"


@pytest.mark.anyio
async def test_uri_paths_and_absent_database_do_not_create_sources(
    prepared: Prepared,
    migrated_database_path: Path,
    tmp_path: Path,
) -> None:
    special = tmp_path / "source # % café.db"
    with readonly_connection(migrated_database_path) as source, sqlite3.connect(special) as target:
        source.backup(target)
    assert inventory(special).rows == inventory(migrated_database_path).rows
    missing = tmp_path / "missing" / "absent.db"
    with pytest.raises(FileNotFoundError):
        inventory(missing)
    assert not missing.parent.exists()


@pytest.mark.anyio
async def test_secret_guard_fails_before_any_output(
    prepared: Prepared,
    migrated_database_path: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    invocation_id = source_id(prepared)
    sentinel = "local-test-credential-not-a-real-key-918273"
    with prepared.sessions.begin() as session:
        source = prepared.source(session)
        settings = deepcopy(source.request_settings)
        settings["scene_boundary_audit"]["assignment_checks"]["outcome"]["assessment"] = sentinel
        source.request_settings = settings
    monkeypatch.setenv("OLLAMA_API_KEY", sentinel)
    with pytest.raises(SecretLeakError):
        collect_export(migrated_database_path, (invocation_id,))
    destination = tmp_path / "must-not-exist"
    assert (
        main(
            [
                "export",
                "--database",
                str(migrated_database_path),
                "--output",
                str(destination),
                "--invocation-id",
                str(invocation_id),
            ]
        )
        == 2
    )
    assert not destination.exists()
    assert sentinel not in capsys.readouterr().out


@pytest.mark.anyio
async def test_partial_or_tampered_export_is_never_repaired_implicitly(
    prepared: Prepared,
    migrated_database_path: Path,
    tmp_path: Path,
) -> None:
    exported = collect_export(migrated_database_path, (source_id(prepared),))
    destination = tmp_path / "partial"
    destination.mkdir()
    (destination / "review-evidence.json").write_text("partial", encoding="utf-8")
    with pytest.raises(EvidenceError, match="export_conflict"):
        write_export(destination, exported)
    other = tmp_path / "complete"
    write_export(other, exported)
    (other / "review-evidence.md").write_text("changed", encoding="utf-8")
    with pytest.raises(EvidenceError, match="export_conflict"):
        write_export(other, exported)


@pytest.mark.anyio
async def test_model_or_caller_cannot_supply_displayed_equality(
    prepared: Prepared,
    migrated_database_path: Path,
    tmp_path: Path,
) -> None:
    exported = collect_export(migrated_database_path, (source_id(prepared),))
    body = exported.model_dump(mode="json")
    body["entries"][0]["evidence"][0]["comparisons"][0]["statement"] = "Invented certificate"
    changed = ReviewEvidenceExport.model_validate_json(json.dumps(body))
    with pytest.raises(EvidenceError):
        write_export(tmp_path / "bad", changed)
    assert not (tmp_path / "bad").exists()
    assert "Original saved critique" in render_export(exported)
