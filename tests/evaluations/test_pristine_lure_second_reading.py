"""Verify reader isolation and both seals for the paired coverage comparison."""

import json
import socket
from pathlib import Path
from typing import Any, NoReturn

import pytest
from open_hollywood_engine.evaluations import canonical_sha256
from open_hollywood_engine.evaluations.review_evidence import EvidenceError

from scripts.q011_scope import coverage_transfer as first
from scripts.q011_scope import second_reading as second
from scripts.wading_path_be.rehearsal import read


def test_packet_and_prejoin_use_only_masked_inputs(monkeypatch: pytest.MonkeyPatch) -> None:
    allowed = {first.FREEZE, first.PACKET}
    original = Path.open
    opened = set()

    def guard(p: Path, *args: Any, **kwargs: Any) -> Any:
        assert p in allowed
        opened.add(p)
        return original(p, *args, **kwargs)

    monkeypatch.setattr(Path, "open", guard)
    packet, index = second.packet()
    assert opened == allowed
    assert canonical_sha256(packet) == second.PACKET_SHA
    assert list(index.values()) != sorted(index.values()) and len(set(index.values())) == 6
    assert all(
        set(row) == {"reason", "draft_version", "draft_spans", "citations", "claim"}
        for row in packet["rows"].values()
    )
    opened.clear()
    allowed.add(second.READINGS)
    receipt = second.prejoin()
    assert opened == allowed and receipt["rows"].keys() == index.keys()


def test_seal_must_pass_before_first_reader_opens(monkeypatch: pytest.MonkeyPatch) -> None:
    def forbidden() -> NoReturn:
        pytest.fail("opened first reader before verifying second-reader seal")

    monkeypatch.setattr(first, "masked_decisions", forbidden)
    monkeypatch.setattr(second, "prejoin", lambda: {"rows": {}})
    with pytest.raises(EvidenceError, match="second_reader_seal"):
        second.compare()


def test_edited_reader_rationale_refused_even_with_identical_scores(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    notes = read(second.READINGS)
    notes["R01"]["basis"] += " Extra commentary."
    edited = tmp_path / "notes.json"
    edited.write_text(json.dumps(notes), encoding="utf-8")
    monkeypatch.setattr(second, "READINGS", edited)
    assert second.prejoin()["rows"] == read(second.SEALED)["rows"]
    with pytest.raises(EvidenceError, match="second_reader_seal"):
        second.compare()


def test_offline_comparison_reproduces_agreement_and_coverage_changes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def forbidden(*args: object, **kwargs: object) -> NoReturn:
        pytest.fail("attempted a network connection during reader comparison")

    for target, name in (
        (socket, "getaddrinfo"),
        (socket.socket, "connect"),
        (socket.socket, "connect_ex"),
    ):
        monkeypatch.setattr(target, name, forbidden)
    report = second.compare()
    assert report["live_calls"] == 0
    rows = report["rows"]
    assert set(rows) == {"AP", "AD", "RP", "RD", "SP", "SD"}
    assert all(r["primary_reader_agreement"] for r in rows.values())
    assert all(s["declared"] == s["decision"] for r in rows.values() for s in r["second"])
    assert {k for k, r in rows.items() if r["second"][0]["declared"] == "flag"} == {"AP"}
    assert {k for k, r in rows.items() if r["alternate_changes_first"]} == {"SD"}
    assert not any(r["alternate_changes_second"] for r in rows.values())
    assert all(r["first"][0]["witnesses"] == r["second"][0]["witnesses"] for r in rows.values())
    differences = {
        k: set(r["second"][0]["assertions"]) - set(r["first"][0]["assertions"])
        for k, r in rows.items()
        if r["second"][0]["assertions"] != r["first"][0]["assertions"]
    }
    assert differences == {"AP": {"no_depiction"}, "RP": {"depicts_placement"}}
    assert (
        [r["findings"] for r in rows["AP"]["first"]]
        == [r["findings"] for r in rows["AP"]["second"]]
        == [["insufficient_evidence_for_away_at_cut"], ["position_scope_unanswered"]]
    )


def test_receipt_binds_the_recorded_readings_and_all_alternatives() -> None:
    sealed = read(second.SEALED)
    assert sealed == second.prejoin()
    assert (
        sealed["annotations_sha256"]
        == "d6d0a258327f20a9fd5bf47bb2207be7bf6a885facec083cab2ee3c49b078751"
    )
    assert len(sealed["rows"]) == 6
    assert sum(len(r["alternatives"]) for r in sealed["rows"].values()) == 1
