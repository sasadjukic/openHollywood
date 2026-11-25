"""Check the pre-annotation source freeze, score mask and ambiguity in six saved explanations."""

import socket
from pathlib import Path
from typing import Any, NoReturn

import pytest
from open_hollywood_engine.evaluations import canonical_sha256
from open_hollywood_engine.evaluations.review_evidence import EvidenceError

from scripts.q011_scope import coverage_transfer as transfer
from scripts.q011_scope import regression
from scripts.wading_path_be.rehearsal import read


def test_portable_seals_and_inventory() -> None:
    freeze = transfer.frozen()
    assert len(freeze["drafts"]) == 3 and len(freeze["cases"]) == 6
    assert len({c["terminal_sha256"] for c in freeze["cases"].values()}) == 6
    assert canonical_sha256(transfer.masked_decisions()) == transfer.DECISIONS_SHA
    assert {
        r["decision"] for v in transfer.masked_decisions().values() for r in v["alternatives"]
    } == {"flag"}


@pytest.fixture
def archive() -> Path:
    if not regression.ARCHIVE.is_dir():
        pytest.skip("requires the private Q011 scope archive")
    return regression.ARCHIVE


def test_masking_does_not_open_historical_scores(
    archive: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    freeze = transfer.frozen()
    allowed = {transfer.FREEZE, archive / "capture-manifest.json"}
    for case, row in freeze["cases"].items():
        allowed.add(archive / "capture" / row["terminal_path"])
        allowed.add(archive / "capture/run/requests" / f"{case}-B-generation.json")
    packet = read(transfer.PACKET)
    original = Path.open

    def guarded(path: Path, *args: Any, **kwargs: Any) -> Any:
        assert path in allowed, path
        return original(path, *args, **kwargs)

    monkeypatch.setattr(Path, "open", guarded)
    rebuilt, _ = transfer.masked_packet(archive)
    assert rebuilt == packet
    assert all(
        set(r) == {"reason", "draft_version", "claim", "citations"} for r in rebuilt.values()
    )


def test_offline_replay_and_ambiguity(archive: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    def offline(*args: object, **kwargs: object) -> NoReturn:
        pytest.fail("network access in local rehearsal")

    monkeypatch.setattr(socket, "getaddrinfo", offline)
    monkeypatch.setattr(socket.socket, "connect", offline)
    monkeypatch.setattr(socket.socket, "connect_ex", offline)
    result = transfer.rehearse(archive)
    rows = result["rows"]
    assert result["live_calls"] == 0 and set(rows) == {"AP", "AD", "RP", "RD", "SP", "SD"}
    assert {k for k, v in rows.items() if v["primary"]["decision"] == "flag"} == {"AP"}
    assert {k for k, v in rows.items() if v["sensitive"]} == {"SD"}
    assert rows["SD"]["alternatives"] == [
        {"decision": "flag", "findings": ["depiction_scope_unanswered"]}
    ]
    assert rows["AP"]["primary"]["findings"] == ["insufficient_evidence_for_away_at_cut"]
    assert rows["AP"]["alternatives"][0]["findings"] == ["position_scope_unanswered"]
    assert all(
        (r["historical"]["evidence"] == "pass") == (r["primary"]["decision"] == "pass")
        for r in rows.values()
    )


def test_wrong_version_or_uncited_evidence() -> None:
    freeze = transfer.frozen()
    key = "586a76ca6d7bb757"
    row, r = read(transfer.PACKET)[key], read(transfer.READINGS)[key]
    wrong = row | {"draft_version": freeze["drafts"]["approach"]["version"]}
    with pytest.raises(EvidenceError, match="wrong_witness"):
        transfer.assess(wrong, r["uses"], r["asserts"], freeze)
    only_plan = row | {"citations": ["E0233", "E0229"]}
    findings = transfer.assess(only_plan, r["uses"], r["asserts"], freeze)["findings"]
    assert "insufficient_evidence_for_away_at_cut" in findings and "uncited_gap" in findings
    with pytest.raises(EvidenceError, match="reason_anchor"):
        transfer.assess(row | {"reason": "silence"}, r["uses"], r["asserts"], freeze)


def test_open_position_requires_an_unsettled_ending() -> None:
    freeze = transfer.frozen()
    key = "b2874807c198a586"
    row, reading = read(transfer.PACKET)[key], read(transfer.READINGS)[key]
    # An authored unit control outside the six historical explanations.
    qualification = "The complete closing paragraph leaves his position at the cut open."
    row = row | {"reason": row["reason"].split(" But its complete")[0] + " " + qualification}
    uses = reading["uses"] | {"closing": "The complete closing paragraph"}
    assertions = {"drawn": uses["draw"], "open_at_cut": qualification}
    assert transfer.assess(row, uses, assertions, freeze)["decision"] == "pass"
    placement = row | {"draft_version": freeze["drafts"]["arrival"]["version"]}
    assert transfer.assess(placement, uses, assertions, freeze)["findings"] == [
        "insufficient_evidence_for_open_at_cut"
    ]


def test_join_refuses_changed_masked_reading_before_opening_scores(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(transfer, "masked_decisions", lambda: {})
    with pytest.raises(EvidenceError, match="prejoin_decisions"):
        transfer.rehearse(Path("archive-must-not-be-read"))
