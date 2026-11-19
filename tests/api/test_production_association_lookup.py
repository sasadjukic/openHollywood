"""Read-only exact-version lookup on disposable SQLite workspaces; no network."""

from __future__ import annotations

import json
import shutil
import socket
import sqlite3
from dataclasses import replace
from pathlib import Path
from typing import Any
from uuid import UUID

import httpx
import pytest
from open_hollywood_api.services import production_association_export as archive
from open_hollywood_api.services import production_association_lookup as service
from open_hollywood_api.services import production_association_rows as rows
from open_hollywood_api.services.workspace import WorkspaceStore
from open_hollywood_engine.evaluations.assessment_completion import encoded
from open_hollywood_engine.secrets import SecretLeakError, SecretLeakGuard, SecretValue

from tests.production_association_fixtures import uid
from tests.production_lookup_fixtures import selections, workspace


@pytest.fixture(autouse=True)
def no_network(monkeypatch: pytest.MonkeyPatch) -> None:
    def deny(*args: Any, **kwargs: Any) -> Any:
        raise AssertionError("No network in lookup tests")

    for owner, name in (
        (socket, "socket"),
        (socket, "create_connection"),
        (socket, "getaddrinfo"),
        (httpx, "Client"),
        (httpx, "AsyncClient"),
    ):
        monkeypatch.setattr(owner, name, deny)


@pytest.fixture
def registered(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> tuple[archive._Registration, service._Workspace]:
    original, current = workspace(tmp_path)
    monkeypatch.setattr(archive, "REGISTERED", (original,))
    monkeypatch.setattr(service, "REGISTERED", (current,))
    monkeypatch.setattr(service, "database_path_from_environment", lambda: current.path)
    return original, current


def request(
    registered: tuple[archive._Registration, service._Workspace], *, all_rows: bool = False
) -> service.LookupRequest:
    original, current = registered
    selected = selections(original)
    return service.LookupRequest(
        workspace=current.name, selections=selected if all_rows else selected[:1]
    )


def change(path: Path, sql: str, values: tuple[Any, ...] = ()) -> None:
    with sqlite3.connect(path) as connection:
        connection.execute(sql, values)


def test_twelve_exact_selections_preserve_history_and_hold_assessment(
    registered: tuple[archive._Registration, service._Workspace],
) -> None:
    original, current = registered
    before = (current.path.read_bytes(), current.path.stat().st_mtime_ns)
    value = request(registered, all_rows=True)
    result = service.lookup(value)
    assert len(result.entries) == 12
    assert all(e.status == "identity_verified" for e in result.entries)
    assert result == service.lookup(value)
    for index, entry in enumerate(result.entries):
        identity = entry.identity
        assert identity is not None
        assert (
            identity.application_exact_version_read_verified and identity.selected_rows_revalidated
        )
        assert (
            not identity.assessment_attachment_eligible and not identity.writer_dispatch_authorized
        )
        assert identity.historical.evidence.eligibility.source_contract == "unsupported_contract"
        assert identity.historical.evidence.eligibility.native_assessment_delivery == "missing"
        assert not identity.historical.source.current_database_revalidated
        assert identity.semantic_support == identity.historical.craft == "unassessed"
        if index in (4, 5, 8, 9):
            assert not identity.draft_lineage_at_lookup.selected_is_latest
    assert not result.portable_workspace_identity and result.live_calls == 0
    assert (current.path.read_bytes(), current.path.stat().st_mtime_ns) == before
    assert len(archive._collect(original)) == 11


@pytest.mark.parametrize(
    "field", ["project_id", "artifact_id", "content_sha256", "version_id", "role"]
)
def test_selection_mismatches_are_explicit_unavailable(
    registered: tuple[archive._Registration, service._Workspace],
    field: str,
) -> None:
    value = request(registered)
    replacement = (
        "f" * 64
        if field == "content_sha256"
        else ("reviewed_draft" if field == "role" else uid(9999))
    )
    selected = value.selections[0].model_copy(update={field: replacement})
    result = service.lookup(value.model_copy(update={"selections": (selected,)}))
    assert result.entries[0].status == "unavailable" and result.entries[0].identity is None
    assert result.entries[0].reason == (
        "no_registered_association" if field in ("version_id", "role") else "selection_mismatch"
    )


@pytest.mark.parametrize(
    "kind", ["unknown", "missing", "copied", "config", "archive", "duplicate", "empty", "overbound"]
)
def test_unqualified_source_or_request_aborts_before_results(
    registered: tuple[archive._Registration, service._Workspace],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    kind: str,
) -> None:
    original, current = registered
    value = request(registered)
    if kind == "unknown":
        value = value.model_copy(update={"workspace": "unknown"})
    elif kind == "missing":
        current.path.unlink()
    elif kind in ("copied", "config"):
        other = tmp_path / "copy.db"
        shutil.copyfile(current.path, other)
        if kind == "copied":
            other.replace(current.path)
        else:
            monkeypatch.setattr(service, "database_path_from_environment", lambda: other)
    elif kind == "archive":
        (original.archive / "R01.snapshot.json").write_bytes(b"{}")
    elif kind == "duplicate":
        value = value.model_copy(update={"selections": value.selections * 2})
    else:
        value = value.model_copy(
            update={"selections": () if kind == "empty" else value.selections * 13}
        )
    with pytest.raises(ValueError):
        service.lookup(value)


@pytest.mark.parametrize(
    "sql",
    [
        "DELETE FROM artifact_versions WHERE id=?",
        "UPDATE artifact_versions SET content='{}' WHERE id=?",
        "UPDATE artifact_versions SET content_sha256='wrong' WHERE id=?",
        "UPDATE artifact_versions SET parent_version_id="
        "'00000000000000000000000000000001' WHERE id=?",
        "UPDATE artifact_versions SET version_number=3 WHERE id=?",
        "UPDATE artifact_versions SET created_by_invocation_id=NULL WHERE id=?",
        "UPDATE artifact_versions SET schema_version='changed' WHERE id=?",
    ],
)
def test_changed_selected_rows_never_keep_identity(
    registered: tuple[archive._Registration, service._Workspace],
    sql: str,
) -> None:
    value = request(registered)
    change(registered[1].path, sql, (UUID(value.selections[0].version_id).hex,))
    result = service.lookup(value)
    assert result.entries[0].status == "unavailable" and result.entries[0].identity is None


@pytest.mark.parametrize(
    "fault",
    [
        "input_link",
        "plan",
        "target",
        "prompt",
        "run",
        "creator",
        "foreign_project",
        "logical_key",
        "output",
        "old_parent",
    ],
)
def test_current_provenance_closure_must_still_match(
    registered: tuple[archive._Registration, service._Workspace],
    fault: str,
) -> None:
    original, current = registered
    packet = json.loads((original.archive / "R01.snapshot.json").read_bytes())
    critic = UUID(packet["invocation"]["id"]).hex
    if fault == "input_link":
        change(
            current.path,
            "DELETE FROM agent_invocation_inputs WHERE agent_invocation_id=?",
            (critic,),
        )
    elif fault in ("plan", "target"):
        version = packet["inputs"][1 if fault == "plan" else 0]["id"]
        change(
            current.path,
            "UPDATE artifact_versions SET content='{}' WHERE id=?",
            (UUID(version).hex,),
        )
    elif fault == "prompt":
        change(
            current.path,
            "UPDATE agent_invocations SET prompt_text='different' WHERE id=?",
            (critic,),
        )
    elif fault == "run":
        change(
            current.path,
            "UPDATE workflow_runs SET graph_version='10' WHERE id=?",
            (UUID(packet["invocation"]["workflow_run_id"]).hex,),
        )
    elif fault == "creator":
        change(
            current.path,
            "UPDATE agent_invocations SET status='FAILED' WHERE id=?",
            (UUID(packet["draft_creator"]["id"]).hex,),
        )
    elif fault in ("foreign_project", "logical_key"):
        column, new = (
            ("project_id", UUID(uid(201)).hex)
            if fault == "foreign_project"
            else ("artifact_key", "wrong")
        )
        change(
            current.path,
            f"UPDATE artifacts SET {column}=? WHERE id=?",
            (new, UUID(packet["review"]["artifact_id"]).hex),
        )
    elif fault == "output":
        change(
            current.path,
            "UPDATE artifact_versions SET created_by_invocation_id=? WHERE id=?",
            (critic, UUID(uid(212)).hex),
        )
    else:
        packet = json.loads((original.archive / "R03.snapshot.json").read_bytes())
        change(
            current.path,
            "UPDATE artifact_versions SET parent_version_id=NULL WHERE id=?",
            (UUID(packet["draft_lineage"][1]["id"]).hex,),
        )
    value = request(registered, all_rows=True)
    result = service.lookup(value)
    affected = result.entries[4:6] if fault == "old_parent" else result.entries[:2]
    assert all(e.status == "unavailable" and e.identity is None for e in affected)


def test_unrelated_commit_and_new_head_between_lookups_do_not_replace_selection(
    registered: tuple[archive._Registration, service._Workspace],
) -> None:
    original, current = registered
    value = request(registered)
    first = service.lookup(value)
    before = current.path.read_bytes()
    change(
        current.path,
        "UPDATE projects SET name='Unrelated rename' WHERE id=?",
        (UUID(uid(101)).hex,),
    )
    assert current.path.read_bytes() != before
    assert service.lookup(value).entries == first.entries
    packet = json.loads((original.archive / "R01.snapshot.json").read_bytes())
    row = packet["review"]
    change(
        current.path,
        "INSERT INTO artifact_versions (id,artifact_id,parent_version_id,version_number,"
        "schema_version,content,content_sha256) VALUES (?,?,?,?,?,?,?)",
        (
            UUID(uid(9999)).hex,
            UUID(row["artifact_id"]).hex,
            UUID(row["id"]).hex,
            2,
            "1",
            json.dumps(row["content"]),
            row["content_sha256"],
        ),
    )
    result = service.lookup(value)
    identity = result.entries[0].identity
    assert identity is not None
    assert identity.historical.evidence.review_lineage.selected_is_latest_at_capture
    assert not identity.review_lineage_at_lookup.selected_is_latest
    assert result.entries[0].selection == value.selections[0]


@pytest.mark.parametrize(
    "kind",
    [
        "ambiguous",
        "wrong_read_model",
        "wrong_read_metadata",
        "write_attempt",
        "secret",
        "archive_drift",
        "code_drift",
    ],
)
def test_source_and_application_read_boundaries(
    registered: tuple[archive._Registration, service._Workspace],
    monkeypatch: pytest.MonkeyPatch,
    kind: str,
) -> None:
    original, _ = registered
    value = request(registered)
    candidates = service._candidates
    revalidate = rows.revalidate
    get_version = WorkspaceStore.get_artifact_version
    if kind == "ambiguous":

        def ambiguous(r: archive._Registration, files: dict[str, bytes]) -> Any:
            result = candidates(r, files)
            return (*result, result[0])

        monkeypatch.setattr(service, "_candidates", ambiguous)
    if kind in ("wrong_read_model", "wrong_read_metadata"):

        def wrong(self: WorkspaceStore, version: UUID) -> Any:
            if kind == "wrong_read_metadata":
                value = get_version(self, version)
                return replace(value, artifact=replace(value.artifact, artifact_key="wrong"))
            return get_version(self, UUID(uid(212)))

        monkeypatch.setattr(WorkspaceStore, "get_artifact_version", wrong)

    def inspect(connection: sqlite3.Connection, snapshot: Any) -> Any:
        assert connection.in_transaction
        if kind == "write_attempt":
            with pytest.raises(sqlite3.OperationalError, match="readonly"):
                connection.execute("UPDATE projects SET name='forbidden'")
        elif kind == "secret":
            guard = SecretLeakGuard((SecretValue("Fixture"),))
            monkeypatch.setattr(rows, "active_secret_guard", lambda: guard)
        elif kind == "archive_drift":
            (original.archive / "R01.snapshot.json").write_bytes(b"{}")
        elif kind == "code_drift":
            monkeypatch.setattr(service, "_implementation", lambda: {"changed": "yes"})
        return revalidate(connection, snapshot)

    monkeypatch.setattr(rows, "revalidate", inspect)
    if kind in ("secret", "archive_drift", "code_drift"):
        with pytest.raises(SecretLeakError if kind == "secret" else ValueError):
            service.lookup(value)
    else:
        result = service.lookup(value)
        assert result.entries[0].status == (
            "identity_verified" if kind == "write_attempt" else "unavailable"
        )
        if kind == "ambiguous":
            assert result.entries[0].reason == "ambiguous_association"


def test_wal_reads_include_committed_changes_and_concurrent_changes_abort_batch(
    registered: tuple[archive._Registration, service._Workspace],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _, current = registered
    writer = sqlite3.connect(current.path)
    try:
        writer.execute("PRAGMA journal_mode=WAL")
        writer.execute("UPDATE projects SET name='In WAL'")
        writer.commit()
        assert Path(str(current.path) + "-wal").stat().st_size > 0
        assert service.lookup(request(registered)).entries[0].status == "identity_verified"
        original = rows.revalidate

        def concurrent(connection: sqlite3.Connection, snapshot: Any) -> Any:
            result = original(connection, snapshot)
            writer.execute("UPDATE projects SET name='Concurrent WAL commit'")
            writer.commit()
            assert connection.in_transaction
            return result

        monkeypatch.setattr(rows, "revalidate", concurrent)
        with pytest.raises(ValueError, match="workspace_changed_during_read"):
            service.lookup(request(registered))
        monkeypatch.setattr(rows, "revalidate", original)
        writer.execute(
            "UPDATE artifact_versions SET content='{}' WHERE id=?", (UUID(uid(112)).hex,)
        )
        writer.commit()
        result = service.lookup(request(registered))
        assert result.entries[0].status == "unavailable"
    finally:
        writer.close()


def test_snapshot_inputs_are_not_taken_from_caller_hashes(
    registered: tuple[archive._Registration, service._Workspace],
) -> None:
    value = request(registered)
    raw = json.loads(value.model_dump_json())
    raw["trusted"] = True
    with pytest.raises(ValueError):
        service.LookupRequest.model_validate_json(encoded(raw))


@pytest.mark.parametrize("kind", ["history", "evaluations"])
def test_read_model_work_is_bounded_before_loading_details(
    registered: tuple[archive._Registration, service._Workspace],
    monkeypatch: pytest.MonkeyPatch,
    kind: str,
) -> None:
    original, current = registered
    selected = request(registered).selections[0]
    with sqlite3.connect(current.path) as connection:
        if kind == "history":
            row = json.loads((original.archive / "R01.snapshot.json").read_bytes())["review"]
            connection.executemany(
                "INSERT INTO artifact_versions (id,artifact_id,version_number,schema_version,"
                "content,content_sha256) VALUES (?,?,?,?,?,?)",
                [
                    (
                        UUID(uid(10000 + i)).hex,
                        UUID(selected.artifact_id).hex,
                        i + 2,
                        "1",
                        json.dumps(row["content"]),
                        selected.content_sha256,
                    )
                    for i in range(64)
                ],
            )
        else:
            connection.executemany(
                "INSERT INTO evaluations (id,project_id,artifact_version_id,rubric_name,"
                "rubric_version,scores) VALUES (?,?,?,?,?,?)",
                [
                    (
                        UUID(uid(10000 + i)).hex,
                        UUID(selected.project_id).hex,
                        UUID(selected.version_id).hex,
                        "fixture",
                        "1",
                        "{}",
                    )
                    for i in range(129)
                ],
            )

    def forbidden(*args: Any, **kwargs: Any) -> Any:
        raise AssertionError("Unbounded detail read")

    monkeypatch.setattr(WorkspaceStore, "get_artifact_version", forbidden)
    assert service.lookup(request(registered)).entries[0].status == "unavailable"
