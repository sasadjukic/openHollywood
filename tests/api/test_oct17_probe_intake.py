"""Registered archive formats, external lineage and literal E1 reconstruction."""

from __future__ import annotations

import json
import socket
import sqlite3
from copy import deepcopy
from pathlib import Path
from typing import Any

import pytest
from open_hollywood_api.services import probe_review_export as service
from open_hollywood_api.services.assessment_intake import collect_intakes, write_intake
from open_hollywood_engine.evaluations.probe_review_evidence import (
    EDITS,
    CrossArchiveProbeSnapshot,
    ProbeAttempt,
    ProbeFile,
    ProbeRequest,
    verify_exact_edit_materialization,
)
from open_hollywood_engine.evaluations.review_evidence import EvidenceError, text_hash

from tests.oct17_probe_fixtures import make_oct17, refresh
from tests.probe_review_fixtures import make_probe_fixture


@pytest.fixture(autouse=True)
def offline(monkeypatch: pytest.MonkeyPatch) -> None:
    def forbidden(*_args: Any, **_kwargs: Any) -> Any:
        raise AssertionError("No network or database in archive qualification")

    monkeypatch.setattr(socket.socket, "connect", forbidden)
    monkeypatch.setattr(socket, "create_connection", forbidden)
    monkeypatch.setattr(sqlite3, "connect", forbidden)


@pytest.mark.parametrize("mode", ["contrast", "craft", "post"])
def test_registered_format_export_and_intake(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, mode: str
) -> None:
    fixture, parent = make_oct17(tmp_path, mode)
    contracts = [refresh(fixture)]
    if parent:
        contracts.append(refresh(parent))
    monkeypatch.setattr(service, "REGISTERED", tuple(contracts))
    before = {p: p.read_bytes() for p in tmp_path.rglob("*.json")}
    export = service.collect_probe_export(fixture.live, (fixture.trial,))
    assert service.write_probe_export(tmp_path / "export", export) == "created"
    assert service.write_probe_export(tmp_path / "export", export) == "reused"
    snapshot = export.entries[0].snapshot
    assert isinstance(snapshot, CrossArchiveProbeSnapshot) == (mode == "post")
    if isinstance(snapshot, CrossArchiveProbeSnapshot):
        assert parent is not None
        assert snapshot.parent_snapshot.proof.contract.experiment == parent.experiment
        with pytest.raises(EvidenceError, match="protected_probe_archive"):
            service.write_probe_export(parent.live / "bad", export)
    intake = collect_intakes("diagnostic_probe", fixture.live, (fixture.trial,))
    assert write_intake(tmp_path / "intake", intake) == "created"
    assert write_intake(tmp_path / "intake", intake) == "reused"
    if parent:
        with pytest.raises(EvidenceError, match="intake_protected_source"):
            write_intake(parent.live / "bad-intake", intake)
    assert all(p.read_bytes() == content for p, content in before.items())


@pytest.mark.parametrize("mode", ["contrast", "craft", "post"])
def test_allowlist_and_unregistered_seal_refused(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, mode: str
) -> None:
    fixture, _ = make_oct17(tmp_path, mode)
    contract = refresh(fixture)
    with pytest.raises(EvidenceError, match="unsupported_probe_archive"):
        service.collect_probe_export(fixture.live, (fixture.trial,))
    monkeypatch.setattr(service, "REGISTERED", (contract,))
    with pytest.raises(EvidenceError, match="unsupported_probe_review"):
        service.collect_probe_export(fixture.live, ("s19401-elara-embedded-initial-J1",))


@pytest.mark.parametrize(
    "failure", ["sent", "receipt", "length", "projection", "parent", "revision", "prepared"]
)
def test_oct17_inconsistency_even_under_authored_seal(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, failure: str
) -> None:
    fixture, parent = make_oct17(tmp_path, "post")
    assert parent is not None
    contract = refresh(fixture)
    parent_contract = refresh(parent)
    docs = fixture.documents
    trial = fixture.trial
    writer = "s19401-elara-embedded-writer-E0"
    if failure == "sent":
        docs["live", f"probes/{trial}/attempt-1-request.json"]["settings"]["temperature"] = 99
    elif failure == "receipt":
        docs["live", f"probes/{trial}/attempt-1-result.json"]["finish_reason"] = "stop"
    elif failure == "length":
        docs["live", f"probes/{trial}/attempt-1-model-output.json"]["finish_reason"] = "length"
    elif failure == "projection":
        docs["live", f"probes/{trial}/manifest.json"]["request_projection"] = "exact_edits"
    elif failure == "parent":
        parent.documents["live", f"probes/{parent.trial}/attempt-1-result.json"]["result"][
            "verdict"
        ] = "reject"
        parent_contract = parent.seal()
    elif failure == "revision":
        docs["live", f"probes/{writer}/attempt-1-result.json"]["result"]["prose"] = "Substituted."
    else:
        docs["prepared", f"prepared/{writer}.json"]["settings"]["temperature"] = 99
    contract = fixture.seal()
    monkeypatch.setattr(service, "REGISTERED", (contract, parent_contract))
    with pytest.raises(ValueError):
        service.collect_probe_export(fixture.live, (trial,))


def test_oct16_still_requires_its_complete_receipt(tmp_path: Path) -> None:
    fixture = make_probe_fixture(tmp_path)
    fixture.documents["live", f"probes/{fixture.trial}/attempt-1-result.json"].pop("finish_reason")
    with pytest.raises(EvidenceError, match="probe_incomplete_response"):
        service.collect_probe_export(fixture.live, (fixture.trial,), _contract=fixture.seal())


@pytest.mark.parametrize(
    "failure", [None, "base", "occurrence", "overlap", "order", "materialized", "bytes", "extra"]
)
def test_exact_edit_materialization_and_refusals(tmp_path: Path, failure: str | None) -> None:
    fixture, _ = make_oct17(tmp_path, "post")
    trial = "s19401-elara-embedded-writer-E0"
    body = deepcopy(fixture.documents["live", f"requests/{trial}-attempt-1.json"])
    body["manifest"].update(arm="E1", request_projection="exact_edits")
    assert body["manifest"]["experiment"] == EDITS
    request = ProbeRequest.model_validate_json(json.dumps(body))
    base = next(a for a in request.inputs if a.artifact_kind == "scene_draft")
    prose = str(base.content["prose"])
    raw: dict[str, Any] = {
        "base_draft_version_id": base.artifact_version_id,
        "base_prose_sha256": text_hash(prose),
        "scene_id": "scene_1",
        "scene_number": 1,
        "title": "Authored",
        "revision_number": 1,
        "is_complete": True,
        "edits": [
            {"old_text": "She decides to investigate.", "occurrence": 2, "new_text": "She goes."}
        ],
    }
    start = prose.rfind("She decides to investigate.")
    materialized = prose[:start] + "She goes."
    result = {
        k: v
        for k, v in raw.items()
        if k not in {"base_draft_version_id", "base_prose_sha256", "edits"}
    }
    result["prose"] = materialized
    receipt = {
        "result": result,
        "edit_audit": {
            "base_version_id": base.artifact_version_id,
            "materialized_prose_sha256": text_hash(materialized),
            "ranges": [
                {
                    "start": start,
                    "end": len(prose),
                    "start_byte": len(prose[:start].encode()),
                    "end_byte": len(prose.encode()),
                    "new_text": "She goes.",
                }
            ],
        },
    }
    if failure == "base":
        raw["base_prose_sha256"] = "0" * 64
    elif failure == "occurrence":
        raw["edits"][0]["occurrence"] = 3
    elif failure == "overlap":
        raw["edits"].append(deepcopy(raw["edits"][0]))
    elif failure == "order":
        raw["edits"].append({"old_text": "She waits.", "occurrence": 1, "new_text": ""})
    elif failure == "materialized":
        result["prose"] = "Invented replacement"
    elif failure == "bytes":
        receipt["edit_audit"]["ranges"][0]["start_byte"] += 1
    elif failure == "extra":
        raw["prose"] = "Forbidden field"

    def file(name: str, value: Any) -> ProbeFile:
        text = json.dumps(value)
        return ProbeFile(area="live", path=name, text=text, sha256=text_hash(text))

    attempt = ProbeAttempt(
        number=1,
        files={
            "receipt": file("receipt.json", receipt),
            "capture": file("capture.json", {"content": json.dumps(raw)}),
        },
    )
    if failure:
        with pytest.raises(EvidenceError):
            verify_exact_edit_materialization(request, attempt)
    else:
        verify_exact_edit_materialization(request, attempt)
