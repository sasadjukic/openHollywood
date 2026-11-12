"""Intake → native binding/completion/rendering, with authored responses only."""

from __future__ import annotations

import json
import socket
import sqlite3
from pathlib import Path
from typing import Any

import httpx
import pytest
from open_hollywood_api.services.assessment_archive_export import collect_assessment_export
from open_hollywood_engine.evaluations.assessment_intake import IntakeResult, compile_intake
from open_hollywood_engine.evaluations.assessment_result import (
    EvidenceRegistry,
    bind_assessment_result,
    render_assessment_result,
)
from open_hollywood_engine.evaluations.assessment_work import complete_work
from open_hollywood_engine.evaluations.assessment_work_brief import render_work_briefs
from open_hollywood_engine.evaluations.review_evidence import text_hash

from scripts.assessment_archive_export import main as export_cli
from tests.assessment_completion_fixtures import AUTHORED_NOTICE, authored_receipt, local_input
from tests.assessment_intake_fixtures import authored_source, choice_for, plan_for


@pytest.fixture(autouse=True)
def offline(monkeypatch: pytest.MonkeyPatch) -> None:
    def deny(*_args: Any, **_kwargs: Any) -> Any:
        raise AssertionError("Offline authored rehearsal only")

    for owner, name in (
        (httpx.Client, "send"),
        (httpx.AsyncClient, "send"),
        (socket.socket, "connect"),
        (socket.socket, "connect_ex"),
        (socket, "create_connection"),
        (socket, "getaddrinfo"),
        (sqlite3, "connect"),
    ):
        monkeypatch.setattr(owner, name, deny)


@pytest.fixture
def intake() -> IntakeResult:
    source = authored_source()
    return compile_intake(
        source,
        plan_for(
            source,
            choice_for(source, "Q001"),
            choice_for(source, "Q002", "literal_procedure"),
            choice_for(source, "Q003", "editorial_effect"),
            choice_for(source, "Q004", "ambiguous"),
        ),
    )


def rows_for(intake: IntakeResult) -> dict[str, Any]:
    assert intake.pending_work is not None and intake.declarations is not None
    return {
        d.statement.unit_id: {
            "support": "supported",
            "evidence": list(dict.fromkeys(r for s in d.source_scopes for r in s.evidence_refs)),
            "reason": AUTHORED_NOTICE,
        }
        for d in intake.declarations.declarations
    }


@pytest.mark.parametrize("label", ["supported", "unsupported", "uncertain", "inadequate_locator"])
def test_authored_complete_results_keep_semantics_unassessed(
    intake: IntakeResult, label: str
) -> None:
    before = intake.model_dump_json()
    local, scope = local_input(intake)
    work, declarations, briefs = intake.pending_work, intake.declarations, intake.briefs
    assert work is not None and declarations is not None and briefs is not None
    assert text_hash(local) == scope.request_sha256
    rows = rows_for(intake)
    for row in rows.values():
        row["support"] = "supported" if label == "inadequate_locator" else label
        if label == "uncertain":
            row["evidence"] = []
        if label == "inadequate_locator":
            row["evidence"] = row["evidence"][:1]
    raw = json.dumps({"assessments": rows})
    receipt = authored_receipt(work, scope, raw)
    unbound = complete_work(work, (receipt,), {scope.batch_id: scope.request_sha256})
    assert unbound.complete_delivery and unbound.binding == "unresolved"
    bound = bind_assessment_result(work, scope, receipt, raw)
    completion = complete_work(work, (bound.receipt,), {scope.batch_id: scope.request_sha256})
    assert completion.complete_delivery and completion.binding == "complete"
    assert completion.unknown_usage_attempts == 1
    assert receipt.input_tokens is receipt.output_tokens is None
    assert (
        bound.support
        == bound.evidence_adequacy
        == bound.edit_necessity
        == bound.craft
        == "unassessed"
    )
    assert not bound.writer_dispatch_authorized and not completion.writer_dispatch_authorized
    assert not completion.whole_relation_credit
    for view in (
        render_assessment_result(work, scope, receipt, raw),
        render_work_briefs(work, scope, declarations, briefs, receipt=receipt, raw_final=raw),
    ):
        payload = json.loads(view.split("```json\n", 1)[1].rsplit("\n```", 1)[0])
        assert payload["full_work"] == work.model_dump(mode="json")
    assert work.context.documents == intake.source.inventory_work.context.documents
    assert work.context.report_fields == intake.source.inventory_work.context.report_fields
    assert len(work.context.statements) == 2
    assert sum(f.status == "hold" for f in intake.findings) == 2
    assert sum(f.status == "not_selected" for f in intake.findings) == 2
    assert intake.model_dump_json() == before
    assert intake.assessment_result is intake.completion_receipt is None


@pytest.mark.parametrize(
    "mutation",
    [
        "malformed",
        "duplicate_id",
        "missing",
        "extra",
        "unknown_ref",
        "duplicate_ref",
        "no_evidence",
        "stale_request",
        "stale_work",
        "wrong_units",
        "raw_digest",
        "forbidden_identity",
        "hidden_provenance",
    ],
)
def test_invalid_authored_completion_is_not_salvaged(intake: IntakeResult, mutation: str) -> None:
    _, scope = local_input(intake)
    work = intake.pending_work
    assert work is not None
    rows = rows_for(intake)
    first = scope.active_unit_ids[0]
    if mutation == "missing":
        rows.pop(first)
    elif mutation == "extra":
        rows["held-or-unselected"] = rows[first]
    elif mutation == "unknown_ref":
        rows[first]["evidence"] = ["not-a-location"]
    elif mutation == "hidden_provenance":
        rows[first]["evidence"] = ["operator-provenance-not-visible-authority"]
    elif mutation == "duplicate_ref":
        rows[first]["evidence"] *= 2
    elif mutation == "no_evidence":
        rows[first]["evidence"] = []
    elif mutation == "forbidden_identity":
        rows[first]["unit_id"] = first
    raw = json.dumps({"assessments": rows})
    if mutation == "malformed":
        raw = "{"
    if mutation == "duplicate_id":
        raw = (
            '{"assessments":{'
            + json.dumps(first)
            + ":"
            + json.dumps(rows[first])
            + ","
            + json.dumps(first)
            + ":"
            + json.dumps(rows[first])
            + "}}"
        )
    receipt = authored_receipt(work, scope, raw)
    if mutation == "stale_request":
        receipt = receipt.model_copy(update={"request_sha256": "1" * 64})
    if mutation == "stale_work":
        receipt = receipt.model_copy(update={"work_sha256": "1" * 64})
    if mutation == "wrong_units":
        receipt = receipt.model_copy(update={"assessed_unit_ids": ("held",)})
    if mutation == "raw_digest":
        raw += " "
    with pytest.raises(ValueError):
        bind_assessment_result(work, scope, receipt, raw)
    assert intake.assessment_result is None


@pytest.mark.parametrize("status", ["invalid", "length", "refusal", "transport_error", "cancelled"])
def test_failed_delivery_and_missing_batch_remain_incomplete(
    intake: IntakeResult, status: Any
) -> None:
    _, scope = local_input(intake)
    work = intake.pending_work
    assert work is not None
    raw = json.dumps({"assessments": rows_for(intake)})
    receipt = authored_receipt(work, scope, raw, status=status)
    with pytest.raises(ValueError):
        bind_assessment_result(work, scope, receipt, raw)
    for receipts in ((receipt,), ()):
        completed = complete_work(work, receipts, {scope.batch_id: scope.request_sha256})
        assert not completed.complete_delivery and completed.binding == "unresolved"
        assert completed.delivered_units == 0 and not completed.writer_dispatch_authorized


def test_scoped_refs_are_not_a_citation_whitelist(intake: IntakeResult) -> None:
    _, scope = local_input(intake)
    work = intake.pending_work
    assert work is not None and intake.declarations is not None
    registry = EvidenceRegistry.model_validate_json(
        next(d.content_json for d in work.context.documents if d.kind == "registry")
    )
    refs = {
        r
        for d in intake.declarations.declarations
        for s in d.source_scopes
        for r in s.evidence_refs
    }
    outside = next(e.ref for e in registry.entries if e.ref not in refs)
    rows = rows_for(intake)
    for row in rows.values():
        row["evidence"] = [outside]
    raw = json.dumps({"assessments": rows})
    result = bind_assessment_result(work, scope, authored_receipt(work, scope, raw), raw)
    assert result.binding == "complete" and result.evidence_adequacy == "unassessed"


@pytest.mark.parametrize("trial", ["authored-only", "BH-1-A-B-SC"])
def test_authored_results_cannot_enter_registered_archive_export(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], trial: str
) -> None:
    with pytest.raises((OSError, ValueError)):
        collect_assessment_export(tmp_path, (trial,))
    destination = tmp_path / "rejected-export"
    assert (
        export_cli(["--archive", str(tmp_path), "--trial-id", trial, "--output", str(destination)])
        == 2
    )
    assert not destination.exists()
    assert json.loads(capsys.readouterr().out) == {
        "error": "assessment_source_or_export_unavailable"
    }
