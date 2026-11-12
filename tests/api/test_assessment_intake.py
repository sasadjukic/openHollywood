"""Supported offline source adapters, real file publication and read-only SQLite."""

from __future__ import annotations

import hashlib
import json
import socket
import sqlite3
from pathlib import Path
from typing import Any

import httpx
import pytest
from open_hollywood_api.services import assessment_intake as service
from open_hollywood_engine.evaluations.assessment_intake import IntakeResult, render_intake
from open_hollywood_engine.evaluations.review_evidence import EvidenceError
from open_hollywood_engine.secrets import SecretLeakError

from scripts import assessment_intake as cli
from tests.api.test_production_fulfillment import Prepared
from tests.api.test_production_fulfillment import prepared as _prepared
from tests.assessment_intake_fixtures import choice_for, plan_for
from tests.probe_review_fixtures import make_probe_fixture

prepared = _prepared


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture(autouse=True)
def offline(monkeypatch: pytest.MonkeyPatch, request: pytest.FixtureRequest) -> None:
    def deny(*args: Any, **kwargs: Any) -> Any:
        raise AssertionError("No network in intake")

    for owner, name in (
        (httpx.Client, "send"),
        (httpx.AsyncClient, "send"),
    ):
        monkeypatch.setattr(owner, name, deny)
    # Windows asyncio creates a local socket pair before the saved-review fixture.
    if request.node.get_closest_marker("anyio") is None:
        monkeypatch.setattr(socket.socket, "connect", deny)
        monkeypatch.setattr(socket, "create_connection", deny)


def batch_plan(collection: service.IntakeCollection) -> service.IntakeBatchPlan:
    source = collection.entries[0].source
    assert source is not None
    fields = source.inventory_work.context.report_fields
    choices = [choice_for(source, fields[0].field_id)]
    if len(fields) > 1:
        choices.append(choice_for(source, fields[1].field_id, "ambiguous"))
    return service.IntakeBatchPlan(plans={source.review_id: plan_for(source, *choices)})


@pytest.mark.parametrize("retry,post", [(False, False), (True, False), (False, True)])
def test_registered_probe_export_preserves_raw_normalized_history_and_reuse(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    retry: bool,
    post: bool,
) -> None:
    fixture = make_probe_fixture(tmp_path, retry=retry, post=post)
    contract = fixture.seal()

    def no_database(*args: Any, **kwargs: Any) -> Any:
        raise AssertionError("Probe intake must not open SQLite")

    monkeypatch.setattr(sqlite3, "connect", no_database)
    before = {p: p.read_bytes() for p in tmp_path.rglob("*.json")}
    collection = service.collect_intakes(
        "diagnostic_probe", fixture.live, (fixture.trial,), _contract=contract
    )
    source = collection.entries[0].source
    assert source is not None and source.report_origin == "raw_model"
    provenance = next(d for d in source.inventory_work.context.documents if d.kind == "scope")
    value = json.loads(provenance.content_json)
    assert value["projection"]["successful_attempt"] == (2 if retry else 1)
    assert len(value["projection"]["failed_predecessors"]) == int(retry)
    assert value["projection"]["production_invocation_id"] is None
    if post:
        registry = next(d for d in source.inventory_work.context.documents if d.kind == "registry")
        assert "operator-provenance-not-visible-authority" not in registry.content_json
        assert value["snapshot"]["dependencies"]
    destination = tmp_path / "intake"
    plan = batch_plan(collection)
    assert service.write_intake(destination, collection, plan, _contract=contract) == "created"
    result = IntakeResult.model_validate_json((destination / "review-01.json").read_bytes())
    assert result.pending_work is not None
    assert sum(f.status == "hold" for f in result.findings) == 1
    assert result.pending_work.context.report_fields == source.inventory_work.context.report_fields
    files = {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in destination.iterdir()}
    assert service.write_intake(destination, collection, plan, _contract=contract) == "reused"
    assert files == {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in destination.iterdir()}
    assert all(p.read_bytes() == data for p, data in before.items())


@pytest.mark.parametrize(
    "mutation",
    [
        "partial",
        "changed",
        "extra",
        "source_changed",
        "during_render",
        "supplied_source",
        "plan_coverage",
        "protected",
        "oversized",
    ],
)
def test_publication_refuses_drift_and_conflicts(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    mutation: str,
) -> None:
    fixture = make_probe_fixture(tmp_path)
    contract = fixture.seal()
    collection = service.collect_intakes(
        "diagnostic_probe", fixture.live, (fixture.trial,), _contract=contract
    )
    destination = tmp_path / "output"
    plan = batch_plan(collection)
    if mutation in ("partial", "changed", "extra"):
        service.write_intake(destination, collection, plan, _contract=contract)
        if mutation == "partial":
            (destination / "manifest.json").unlink()
        elif mutation == "changed":
            (destination / "review-01.json").write_bytes(b"changed")
        else:
            (destination / "extra").write_bytes(b"extra")
    if mutation == "source_changed":
        fixture.path("live", "closure.json").write_bytes(b"{}")
    elif mutation == "during_render":
        real_render = render_intake

        def drifting(result: IntakeResult) -> str:
            text = real_render(result)
            fixture.path("live", "closure.json").write_bytes(b"{}")
            return text

        monkeypatch.setattr(service, "render_intake", drifting)
    elif mutation == "supplied_source":
        entry = collection.entries[0]
        assert entry.source is not None
        collection = collection.model_copy(
            update={
                "entries": (
                    entry.model_copy(
                        update={
                            "source": entry.source.model_copy(update={"source_sha256": "0" * 64})
                        }
                    ),
                )
            }
        )
    elif mutation == "plan_coverage":
        plan = service.IntakeBatchPlan(plans={})
    elif mutation == "protected":
        destination = fixture.live / "inside"
    elif mutation == "oversized":
        monkeypatch.setattr(service, "MAX_OUTPUT_BYTES", 1)
    before = {p: p.read_bytes() for p in destination.iterdir()} if destination.exists() else {}
    with pytest.raises((EvidenceError, ValueError)):
        service.write_intake(destination, collection, plan, _contract=contract)
    if before:
        assert before == {p: p.read_bytes() for p in destination.iterdir()}
    else:
        assert not destination.exists()


@pytest.mark.parametrize("ids", [(), ("same", "same"), tuple(str(i) for i in range(13))])
def test_bounded_selection_before_io(tmp_path: Path, ids: tuple[str, ...]) -> None:
    with pytest.raises(EvidenceError, match="intake_selection"):
        service.collect_intakes("diagnostic_probe", tmp_path / "missing", ids)


def test_unregistered_archive_is_refused(tmp_path: Path) -> None:
    fixture = make_probe_fixture(tmp_path)
    fixture.seal()
    with pytest.raises((EvidenceError, OSError)):
        service.collect_intakes("diagnostic_probe", fixture.live, (fixture.trial,))


@pytest.mark.parametrize(
    "value", ['{"plans":{},"plans":{}}', '{"plans":{},"gold":"supported"}', '{"plans":NaN}']
)
def test_bad_plan_rejected(tmp_path: Path, value: str) -> None:
    path = tmp_path / "plan.json"
    path.write_text(value, encoding="utf-8")
    with pytest.raises(ValueError):
        service.read_plan(path)


def test_plan_size_bound_and_cli_error_redaction(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    path = tmp_path / "plan.json"
    path.write_bytes(b'{"plans":{}}')
    monkeypatch.setattr(service, "MAX_INPUT_BYTES", 1)
    with pytest.raises(EvidenceError, match="intake_plan_too_large"):
        service.read_plan(path)

    def fails(*args: Any, **kwargs: Any) -> Any:
        raise ValueError("UNPUBLISHED_PROSE_AND_SECRET")

    monkeypatch.setattr(cli, "collect_intakes", fails)
    assert (
        cli.main(
            [
                "probe",
                "--archive",
                str(tmp_path),
                "--review-id",
                "test",
                "--output",
                str(tmp_path / "output"),
            ]
        )
        == 2
    )
    output = capsys.readouterr().out
    assert "UNPUBLISHED" not in output and "invalid" in output


def test_secret_guard_precedes_destination_creation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fixture = make_probe_fixture(tmp_path)
    contract = fixture.seal()
    collection = service.collect_intakes(
        "diagnostic_probe", fixture.live, (fixture.trial,), _contract=contract
    )

    class Guard:
        def ensure_safe(self, *args: Any, **kwargs: Any) -> None:
            raise SecretLeakError("intake", "$")

    monkeypatch.setattr(service, "active_secret_guard", lambda: Guard())
    with pytest.raises(SecretLeakError):
        service.write_intake(tmp_path / "output", collection, _contract=contract)
    assert not (tmp_path / "output").exists()


def test_linked_path_is_refused_without_following(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    target = tmp_path / "linked"
    real = Path.is_symlink
    monkeypatch.setattr(Path, "is_symlink", lambda p: p == target or real(p))
    with pytest.raises(EvidenceError, match="intake_linked_path"):
        service.collect_intakes("diagnostic_probe", target, ("test",))


@pytest.mark.anyio
@pytest.mark.parametrize("incompatible", [False, True])
async def test_saved_adapter_keeps_lineage_and_does_not_write_database(
    prepared: Prepared,
    migrated_database_path: Path,
    tmp_path: Path,
    incompatible: bool,
) -> None:
    with prepared.sessions() as session:
        invocation = prepared.source(session)
        identity = str(invocation.id)
        if incompatible:
            invocation.request_settings = {
                **invocation.request_settings,
                "prompt_template_version": "60",
            }
            session.commit()

    def database_bytes() -> dict[str, str]:
        return {
            p.name: hashlib.sha256(p.read_bytes()).hexdigest()
            for p in (migrated_database_path, Path(str(migrated_database_path) + "-wal"))
            if p.exists()
        }

    before = database_bytes()
    collection = service.collect_intakes("saved_review", migrated_database_path, (identity,))
    if incompatible:
        assert collection.entries[0].source is None
        plan = service.template(collection)
    else:
        source = collection.entries[0].source
        assert source is not None and source.report_origin == "saved_normalized_and_audit"
        assert source.inventory_work.context.canonical_review_id is None
        assert identity in next(
            d.content_json for d in source.inventory_work.context.documents if d.kind == "scope"
        )
        plan = batch_plan(collection)
    destination = tmp_path / "saved-intake"
    assert service.write_intake(destination, collection, plan) == "created"
    assert before == database_bytes()
    saved = json.loads((destination / "review-01.json").read_text("utf-8"))
    if incompatible:
        assert saved["source"] is None and saved["incompatible_export"]
    else:
        assert saved["assessment_result"] is None and saved["pending_work"]
