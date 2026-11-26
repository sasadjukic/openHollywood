"""Check source identity, one-edit pairs and independent coverage scores."""

import socket
from pathlib import Path
from typing import Any, NoReturn

import pytest
from open_hollywood_engine.evaluations.review_evidence import EvidenceError

from scripts.planetarium_scope import boundary_rehearsal as rehearsal

archive = pytest.mark.skipif(
    not (rehearsal.READER / "reader/packet.json").is_file(),
    reason="requires the sealed local independent reading and original deliveries",
)


@archive
def test_offline_replay(monkeypatch: pytest.MonkeyPatch) -> None:
    def deny(*args: Any, **kwargs: Any) -> NoReturn:
        pytest.fail("rehearsal attempted network access")

    monkeypatch.setattr(socket.socket, "connect", deny)
    monkeypatch.setattr(socket, "getaddrinfo", deny)
    result = rehearsal.replay()
    assert result["live_calls"] == 0
    for cell, row in result["pairs"].items():
        saved, revised = row["saved"], row["revision"]
        assert saved["factual_sufficiency"] == int(cell != "SE-SB")
        assert saved["diagnostic_completeness"] == 0
        assert revised["factual_sufficiency"] == revised["diagnostic_completeness"] == 1
        assert saved["explanation"] != revised["explanation"]
        assert row["citation"] == "E1420"
    event = result["pairs"]["SE-SB"]
    assert event["original_returned_label"] == "unsupported" and event["gold"] == "uncertain"
    assert event["alternative"]["factual_sufficiency"] == "pass"
    for name in ("visit_denied", "projection_denied"):
        control = result["controls"][name]
        assert control["missing"] == {"factual": [], "diagnostic": []}
        assert control["unsupported_denial"]
        assert control["factual_sufficiency"] == control["diagnostic_completeness"] == 0


@archive
@pytest.mark.parametrize(
    ("change", "error"),
    [
        ("saved_text", "saved_delivery_drift"),
        ("same_claim_other_explanation", "wrong_saved_explanation"),
        ("wrong_span", "wrong_source_span"),
    ],
)
def test_capture_substitution_is_rejected(
    monkeypatch: pytest.MonkeyPatch, change: str, error: str
) -> None:
    original = rehearsal.sealed

    def substitute(path: Path, expected: str) -> dict[str, Any]:
        data = original(path, expected)
        if path == rehearsal.PAIRS:
            row = data["cases"]["ON-AX"]
            if change == "saved_text":
                row["explanation"] += " Additional assertion."
            if change == "same_claim_other_explanation":
                row["scoring_id"] = data["cases"]["ON-SX"]["scoring_id"]
            if change == "wrong_span":
                data["sources"][row["source_version"]]["witnesses"]["summarized_cues"]["end"] -= 1
        return data

    monkeypatch.setattr(rehearsal, "sealed", substitute)
    with pytest.raises(EvidenceError, match=error):
        rehearsal.replay()


def test_scores_depend_on_evidence_actually_annotated() -> None:
    expected = rehearsal.sealed(rehearsal.EXPECTED, rehearsal.EXPECTED_SHA)
    fixtures = rehearsal.sealed(rehearsal.PAIRS, rehearsal.PAIRS_SHA)
    row = fixtures["cases"]["SN-AX"]
    needs = expected["requirements"]["SN"]
    witnesses = fixtures["sources"][row["source_version"]]["witnesses"]
    original = row["explanation"]
    uses = row["saved_annotations"] | row["revision"]["annotations"]
    with pytest.raises(EvidenceError, match="unbound_annotation"):
        rehearsal.score(original, uses, needs, witnesses)
    for edit in ({"before": "Elias", "after": "Kit"}, {"before": "the dome", "after": "x"}):
        with pytest.raises(EvidenceError, match="ambiguous_edit"):
            rehearsal.edited(original + original, edit)
