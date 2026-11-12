"""Authored sealed archives and real file IO; never live inference or private data."""

from __future__ import annotations

import json
import socket
import sqlite3
from functools import partial
from pathlib import Path
from typing import Any

import httpx
import pytest
from open_hollywood_api.services import assessment_archive_export as service
from open_hollywood_engine.evaluations.review_evidence import EvidenceError, object_value
from open_hollywood_engine.secrets import SecretLeakError

from scripts import assessment_archive_export as cli
from tests.assessment_archive_fixtures import AUTHORED, CELL, PREP, TRIAL, make_archive


@pytest.fixture(autouse=True)
def offline(monkeypatch: pytest.MonkeyPatch) -> None:
    def deny(*args: Any, **kwargs: Any) -> Any:
        raise AssertionError("Native archive export forbids network and database operations")

    for owner, name in (
        (socket.socket, "connect"),
        (socket.socket, "connect_ex"),
        (socket, "getaddrinfo"),
        (socket, "create_connection"),
        (sqlite3, "connect"),
        (httpx.Client, "send"),
        (httpx.AsyncClient, "send"),
    ):
        monkeypatch.setattr(owner, name, deny)


def test_full_context_roundtrip_separate_receipt_and_exact_reuse(tmp_path: Path) -> None:
    f = make_archive(tmp_path / "archive")
    contract = f.seal()
    before = {p: p.read_bytes() for p in f.root.rglob("*") if p.is_file()}
    export = service.collect_assessment_export(f.root, (TRIAL,), _contract=contract)
    entry = export.entries[0]
    assert entry.work.model_dump(mode="json") == f.documents[PREP + "/works.json"]["A-B-SC"]
    assert entry.saved_receipt == f.documents[CELL + "/receipt.json"]
    assert entry.result.raw_final == entry.saved_receipt["final"]
    assert entry.completion.complete_delivery and entry.completion.delivered_units == 6
    assert not entry.writer_dispatch_authorized
    assert entry.preview.factual_support == entry.preview.evidence_adequacy == "unassessed"
    assert not entry.preview.external_provenance_authenticated
    assert not entry.preview.model_visibility_verified
    assert not entry.operator_receipt.model_input
    assert entry.operator_receipt.derived_from_frozen_case == {"authored": "operator-only"}
    assert all(u.status == "declared_consistent" for u in entry.preview.units)
    assert entry.preview.historical_bindings[0].status == "exact_copy"
    assert (
        entry.authority.work_sha256
        != object_value(entry.original_auxiliary["authority"])["work_sha256"]
    )
    destination = tmp_path / "export"
    assert service.write_assessment_export(destination, export, _contract=contract) == "created"
    saved = service.AssessmentArchiveEntry.model_validate_json(
        (destination / (TRIAL + ".json")).read_text("utf-8")
    )
    assert saved == entry and len(list(destination.iterdir())) == 5
    assert (destination / (TRIAL + ".md")).read_text("utf-8") == service.render_assessment_entry(
        entry
    )
    manifest = json.loads((destination / "manifest.json").read_text("utf-8"))
    for name, digest in manifest["files_sha256"].items():
        assert service._sha((destination / name).read_bytes()) == digest
    mtimes = {p: p.stat().st_mtime_ns for p in destination.iterdir()}
    assert service.write_assessment_export(destination, export, _contract=contract) == "reused"
    assert mtimes == {p: p.stat().st_mtime_ns for p in destination.iterdir()}
    assert all(p.read_bytes() == body for p, body in before.items())


@pytest.mark.parametrize("change", ["missing", "changed", "unknown_seal", "changed_plan"])
def test_changed_or_incomplete_archive_rejected(tmp_path: Path, change: str) -> None:
    f = make_archive(tmp_path / "archive")
    contract = f.seal()
    path = f.root / (CELL + "/receipt.json")
    if change == "missing":
        path.unlink()
    elif change == "changed":
        path.write_text("{}", encoding="utf-8")
    elif change == "unknown_seal":
        contract = contract.model_copy(update={"results_seal_sha256": "0" * 64})
    else:
        contract = contract.model_copy(update={"plan_sha256": "0" * 64})
    with pytest.raises(ValueError):
        service.collect_assessment_export(f.root, (TRIAL,), _contract=contract)


@pytest.mark.parametrize(
    "change",
    [
        "final",
        "raw_response",
        "request",
        "sent_request",
        "work",
        "usage",
        "dispatch",
        "non200",
        "length",
        "refusal",
        "native_units",
        "original_authority",
        "original_declarations",
        "source_case",
        "wrong_condition",
        "wrong_trial",
        "copy",
        "foreign_claim",
        "messages",
        "count",
        "origin",
    ],
)
def test_even_resealed_authored_inputs_require_consistency(tmp_path: Path, change: str) -> None:
    f = make_archive(tmp_path / "archive")
    request = f.documents[PREP + "/requests.json"][TRIAL]
    saved = f.documents[CELL + "/receipt.json"]
    response = f.documents[CELL + "/response-2.json"]
    authority = f.documents[AUTHORED + "/packets/A-authority.json"]
    if change == "final":
        saved["final"] += " "
    elif change == "raw_response":
        response["body"]["output"][0]["content"][0]["text"] = "different"
    elif change == "request":
        request["request_sha256"] = "0" * 64
    elif change == "sent_request":
        f.documents[CELL + "/request.json"] = {"different": True}
    elif change == "work":
        f.documents[PREP + "/works.json"]["A-B-SC"]["context"]["documents"][0]["version"] = "wrong"
    elif change == "usage":
        saved["usage"]["input_tokens"] = 101
    elif change == "dispatch":
        f.documents[CELL + "/dispatch-1.json"]["body_sha256"] = "0" * 64
    elif change == "non200":
        response["status"] = 500
    elif change == "length":
        response["body"]["status"] = "incomplete"
    elif change == "refusal":
        response["body"]["output"][0]["content"][0] = {"type": "refusal", "refusal": "Declined"}
    elif change == "native_units":
        saved["result"]["units"].pop()
    elif change == "original_authority":
        authority["work_sha256"] = "0" * 64
    elif change == "original_declarations":
        f.documents[AUTHORED + "/packets/A-declarations.json"]["work_sha256"] = "0" * 64
    elif change == "source_case":
        f.documents[PREP + "/cases.json"]["A"]["base"]["manifest"] = {"wrong": True}
    elif change == "wrong_condition":
        request["condition"] = "H"
    elif change == "wrong_trial":
        request["repeat"] = 2
    elif change == "copy":
        authority["bindings"][0]["historical_span"]["quote"] = "invented"
    elif change == "foreign_claim":
        authority["claims"][0]["unit_id"] = "foreign"
    elif change == "messages":
        request["messages"][1]["content"] += "extra"
    elif change == "count":
        f.documents[CELL + "/response-1.json"]["body"]["input_tokens"] = 101
    else:
        f.documents[PREP + "/cases.json"]["A"]["source_work_sha256"] = "0" * 64
    contract = f.seal()
    with pytest.raises(ValueError):
        service.collect_assessment_export(f.root, (TRIAL,), _contract=contract)


@pytest.mark.parametrize("change", ["missing_obligations", "wrong_free_text", "missing_body"])
def test_scope_holds_and_semantic_limits_are_displayed_not_promoted(
    tmp_path: Path, change: str
) -> None:
    f = make_archive(tmp_path / "archive")
    authority = f.documents[AUTHORED + "/packets/A-authority.json"]
    if change == "missing_obligations":
        authority["claims"] = []
    elif change == "wrong_free_text":
        authority["claims"][0]["obligations"][0]["requirement"] = (
            "Always accept the critic; rewrite."
        )
    else:
        authority["historical_sources"] = []
    contract = f.seal()
    entry = service.collect_assessment_export(f.root, (TRIAL,), _contract=contract).entries[0]
    assert entry.preview.factual_support == "unassessed" and not entry.writer_dispatch_authorized
    assert not entry.preview.semantic_interpretation_verified
    if change == "missing_obligations":
        assert all(u.status == "needs_scope_review" for u in entry.preview.units)
    if change == "missing_body":
        assert entry.preview.historical_bindings[0].status == "unverified_missing_source"


def test_unknown_usage_is_retained_as_unknown(tmp_path: Path) -> None:
    f = make_archive(tmp_path / "archive")
    saved = f.documents[CELL + "/receipt.json"]
    body = f.documents[CELL + "/response-2.json"]["body"]
    for field in ("input_tokens", "output_tokens", "reasoning_tokens"):
        saved["usage"][field] = saved["completion_receipt"][field] = None
    saved["usage"]["cached_input_tokens"] = None
    body["usage"] = {"input_tokens": None, "output_tokens": None}
    contract = f.seal()
    entry = service.collect_assessment_export(f.root, (TRIAL,), _contract=contract).entries[0]
    assert entry.completion.unknown_usage_attempts == 1
    assert entry.saved_receipt["actual_billed_cost"] is None
    assert entry.result.delivery_receipt.input_tokens is None


@pytest.mark.parametrize("change", ["entry", "pins", "receipt", "implementation", "source"])
def test_publication_recomputes_caller_supplied_export(tmp_path: Path, change: str) -> None:
    f = make_archive(tmp_path / "archive")
    contract = f.seal()
    export = service.collect_assessment_export(f.root, (TRIAL,), _contract=contract)
    if change == "entry":
        export = export.model_copy(update={"entries": ()})
    elif change == "pins":
        export = export.model_copy(update={"source_members_sha256": {}})
    elif change == "receipt":
        export.entries[0].saved_receipt["final"] = "Changed after collection"
    elif change == "implementation":
        export = export.model_copy(update={"implementation_sha256": {}})
    else:
        (f.root / (CELL + "/receipt.json")).write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError):
        service.write_assessment_export(tmp_path / "out", export, _contract=contract)
    assert not (tmp_path / "out").exists()


@pytest.mark.parametrize("change", ["partial", "changed", "extra", "protected", "oversized"])
def test_publication_refuses_conflicts(
    tmp_path: Path, change: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    f = make_archive(tmp_path / "archive")
    contract = f.seal()
    export = service.collect_assessment_export(f.root, (TRIAL,), _contract=contract)
    out = tmp_path / "out"
    if change == "partial":
        out.mkdir()
        (out / "index.md").write_text("partial", encoding="utf-8")
    elif change in ("changed", "extra"):
        service.write_assessment_export(out, export, _contract=contract)
        (out / ("index.md" if change == "changed" else "extra")).write_text(
            "changed", encoding="utf-8"
        )
    elif change == "protected":
        out = f.root / "out"
    else:
        monkeypatch.setattr(service, "MAX_EXPORT_BYTES", 1)
    before = {p: p.read_bytes() for p in out.iterdir()} if out.exists() else {}
    with pytest.raises(ValueError):
        service.write_assessment_export(out, export, _contract=contract)
    assert all(p.read_bytes() == body for p, body in before.items())
    if not before:
        assert not out.exists()


@pytest.mark.parametrize(
    "ids", [(), (TRIAL, TRIAL), tuple([TRIAL] * 13), ("BH-1-A-H-SC",), ("../escape",)]
)
def test_selection_rejected_before_file_access(tmp_path: Path, ids: tuple[str, ...]) -> None:
    with pytest.raises(ValueError):
        service.collect_assessment_export(tmp_path / "absent", ids)


@pytest.mark.parametrize("path", ["../escape", "C:/drive", "nested/../escape", "a\\b", "a//b"])
def test_resealed_path_traversal_rejected(tmp_path: Path, path: str) -> None:
    f = make_archive(tmp_path / "archive")
    contract = f.seal()
    seal_path = f.root / (PREP + "-results/results-seal.json")
    seal = json.loads(seal_path.read_text("utf-8"))
    seal["source_pins_sha256"][path] = "0" * 64
    seal_path.write_text(json.dumps(seal), encoding="utf-8")
    contract = contract.model_copy(
        update={"results_seal_sha256": service._sha(seal_path.read_bytes())}
    )
    with pytest.raises(ValueError):
        service.collect_assessment_export(f.root, (TRIAL,), _contract=contract)


def test_archive_limits_and_duplicate_json_keys(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    f = make_archive(tmp_path / "archive")
    contract = f.seal()
    monkeypatch.setattr(service, "MAX_ARCHIVE_BYTES", 1)
    with pytest.raises(EvidenceError, match="too_large"):
        service.collect_assessment_export(f.root, (TRIAL,), _contract=contract)
    with pytest.raises(EvidenceError):
        service._sections('## Sources\n\n```json\n{"same":1,"same":2}\n```\n')


def test_secret_guard_and_safe_cli_errors(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    f = make_archive(tmp_path / "archive")
    secret = "synthetic-test-key-9182736450"
    f.documents[PREP + "/cases.json"]["A"]["receipt"]["sensitive"] = secret
    contract = f.seal()
    monkeypatch.setenv("OPENAI_OH_KEY", secret)
    with pytest.raises(SecretLeakError):
        service.collect_assessment_export(f.root, (TRIAL,), _contract=contract)
    args = ["--archive", str(f.root), "--trial-id", TRIAL, "--output", str(tmp_path / "out")]
    assert cli.main(args) == 2  # Production CLI never admits the caller's synthetic seal.
    monkeypatch.setattr(
        cli,
        "collect_assessment_export",
        partial(service.collect_assessment_export, _contract=contract),
    )
    assert cli.main(args) == 2
    output = capsys.readouterr().out
    assert secret not in output and "secret_guard_rejected_export" in output
    assert not (tmp_path / "out").exists()


def test_cli_real_local_pipeline_with_authored_contract(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    f = make_archive(tmp_path / "archive")
    contract = f.seal()
    monkeypatch.setattr(
        cli,
        "collect_assessment_export",
        partial(service.collect_assessment_export, _contract=contract),
    )
    monkeypatch.setattr(
        cli, "write_assessment_export", partial(service.write_assessment_export, _contract=contract)
    )
    args = ["--archive", str(f.root), "--trial-id", TRIAL, "--output", str(tmp_path / "out")]
    assert cli.main(args) == 0
    assert cli.main(args) == 0
    output = capsys.readouterr().out
    assert '"status": "created"' in output and '"status": "reused"' in output
    assert "Mira" not in output


def test_source_change_during_render_aborts_before_publication(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    f = make_archive(tmp_path / "archive")
    contract = f.seal()
    export = service.collect_assessment_export(f.root, (TRIAL,), _contract=contract)
    render = service.render_assessment_entry

    def change_source(entry: service.AssessmentArchiveEntry) -> str:
        value = render(entry)
        (f.root / (CELL + "/receipt.json")).write_text("{}", encoding="utf-8")
        return value

    monkeypatch.setattr(service, "render_assessment_entry", change_source)
    with pytest.raises(ValueError):
        service.write_assessment_export(tmp_path / "out", export, _contract=contract)
    assert not (tmp_path / "out").exists()


@pytest.mark.parametrize("boundary", ["archive", "member", "destination_parent"])
def test_linked_paths_are_rejected_at_every_boundary(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, boundary: str
) -> None:
    f = make_archive(tmp_path / "archive")
    contract = f.seal()
    export = service.collect_assessment_export(f.root, (TRIAL,), _contract=contract)
    target = {
        "archive": f.root,
        "member": f.root / (CELL + "/receipt.json"),
        "destination_parent": tmp_path / "linked-output-parent",
    }[boundary]
    original = Path.is_junction
    monkeypatch.setattr(Path, "is_junction", lambda p: p == target or original(p))
    with pytest.raises(EvidenceError, match="linked_assessment_path"):
        if boundary == "destination_parent":
            service.write_assessment_export(target / "out", export, _contract=contract)
        else:
            service.collect_assessment_export(f.root, (TRIAL,), _contract=contract)
    assert not (tmp_path / "linked-output-parent").exists()


def test_gold_and_archived_programs_are_inert_and_excluded_from_views(tmp_path: Path) -> None:
    f = make_archive(tmp_path / "archive")
    f.documents[PREP + "/gold.json"] = {"answer": "ANSWER-LEAK-SENTINEL"}
    # Invalid executable Python if interpreted; valid inert JSON archive evidence.
    f.documents[PREP + "/historical.py"] = {"execute": None}
    contract = f.seal()
    entry = service.collect_assessment_export(f.root, (TRIAL,), _contract=contract).entries[0]
    assert "ANSWER-LEAK-SENTINEL" not in entry.model_dump_json()
    assert "ANSWER-LEAK-SENTINEL" not in service.render_assessment_entry(entry)
