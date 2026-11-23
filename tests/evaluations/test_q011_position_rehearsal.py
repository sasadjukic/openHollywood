"""Check the identical gap at two instants and replay the authenticated Q011 controls."""

from __future__ import annotations

import json
import socket
from typing import Any, NoReturn

import pytest
from open_hollywood_engine.evaluations.review_evidence import EvidenceError

from scripts.q011_arrival import scope_rehearsal as prior
from scripts.q011_scope import position_rehearsal as rehearsal
from scripts.q011_scope import regression


@pytest.fixture
def inputs() -> dict[str, dict[str, Any]]:
    if not regression.ARCHIVE.exists():
        pytest.skip("requires the private Q011 scope archive")
    return rehearsal.packets()


def test_only_sentence_order_changes(inputs: dict[str, dict[str, Any]]) -> None:
    original = inputs["approach"]
    draft = original["assessment_draft"]
    versions = set()
    for name, (first, last) in {
        "gap-at-cut": (rehearsal.MOTION, rehearsal.GAP),
        "gap-before-motion": (rehearsal.GAP, rehearsal.MOTION),
    }.items():
        candidate = inputs[name]["assessment_draft"]
        prose = candidate["content"]["prose"]
        assert inputs[name] == original | {"assessment_draft": candidate}
        assert candidate["content"] == draft["content"] | {
            "prose": " ".join([draft["content"]["prose"], first, last])
        }
        versions.add(candidate["version"])
        work = prior.work_pair(name, inputs[name])[name + "-position"]
        visible = json.loads(work.context.messages[-1].content)
        assert set(visible) == {"claim", "documents", "active_unit_ids", "work_brief"}
        assert visible["claim"]["text"] == prior.CLAIMS["position"]
        docs = {d["identity"]: d for d in visible["documents"]}
        assert docs["assessment_draft"]["version"] == candidate["version"]
        assert docs["assessment_draft"]["structured_content"] == candidate["content"] | {
            "ending_excerpt": prose.rsplit("\n\n", 1)[-1]
        }
        assert docs["historical-review"]["structured_content"] == original["historical_review"]
        for role, source in original["context"].items():
            assert docs[role]["version"] == source["version"]
            assert docs[role]["structured_content"] == source["content"]
        assert all(
            token not in work.context.messages[-1].content
            for token in ('"judgment_rule"', '"evidence_rule"', '"basis"', rehearsal.GOLD)
        )
    assert len({*versions, draft["version"]}) == 3


def test_scores_and_saved_subjects(
    inputs: dict[str, dict[str, Any]], monkeypatch: pytest.MonkeyPatch
) -> None:
    if not (rehearsal.ROOT / "evidence-decisions.json").is_file():
        pytest.skip("requires the private authored rehearsal and sealed evidence worksheet")

    def offline(*args: object, **kwargs: object) -> NoReturn:
        pytest.fail("position rehearsal attempted network access")

    monkeypatch.setattr(socket, "getaddrinfo", offline)
    monkeypatch.setattr(socket.socket, "connect", offline)
    monkeypatch.setattr(socket.socket, "connect_ex", offline)
    result = rehearsal.replay()
    assert result == json.loads((rehearsal.ROOT / "scores.json").read_bytes())
    assert (result["live_calls"], result["historical_decision"]) == (0, "hold")
    rows = result["authored"]
    assert len(rows) == 8
    assert [(r["case"], r["gold"], r["judgment"], r["evidence"]) for r in rows[:5]] == [
        ("approach", "uncertain", "pass", "pass"),
        ("arrival", "supported", "pass", "pass"),
        ("stop", "unsupported", "pass", "pass"),
        ("gap-at-cut", "unsupported", "pass", "pass"),
        ("gap-before-motion", "uncertain", "pass", "pass"),
    ]
    assert [(r["judgment"], r["evidence"]) for r in rows[5:]] == [
        ("fail", "fail"),
        ("pass", "fail"),
        ("fail", "pass"),
    ]
    cut, renewed, stale, _, flipped = rows[3:]
    assert cut["witness"]["quote"] == stale["witness"]["quote"] == rehearsal.GAP
    assert cut["witness"]["end"] == len(
        inputs["gap-at-cut"]["assessment_draft"]["content"]["prose"]
    )
    assert stale["witness"]["end"] < renewed["witness"]["start"]
    assert renewed["evidence_id"] == flipped["evidence_id"]
    assert renewed["final_sha256"] != flipped["final_sha256"]
    saved = result["saved_approach"]
    assert saved["witness_origin"] == "local_annotation"
    assert (saved["score"]["label"], saved["score"]["judgment"], saved["score"]["evidence"]) == (
        "unsupported",
        "fail",
        "fail",
    )
    assert [
        (r["case"], r["returned"], r["judgment"], r["evidence"]) for r in result["saved_depictions"]
    ] == [
        ("approach-depiction", "unsupported", "pass", "pass"),
        ("arrival-depiction", "supported", "pass", "pass"),
        ("stop-depiction", "unsupported", "pass", "pass"),
    ]


@pytest.mark.parametrize(
    "damage",
    [
        {"draft_version": "adjacent"},
        {"start": -1},
        {"end": 20},
        {"quote": "same gap."},
        {"start": False},
        {"instant": "unknown"},
        {"relation": "unknown"},
    ],
)
def test_rejects_damaged_witness(damage: dict[str, Any]) -> None:
    source = dict(
        document_id="assessment_draft",
        field_pointer="/prose",
        document_version="v1",
        quote="The gap.",
    )
    witness = dict(
        draft_version="v1", start=0, end=8, quote="The gap.", instant="at_cut", relation="excludes"
    )
    rehearsal.check_witness([source], witness)
    with pytest.raises(EvidenceError, match="q011_position_witness_binding"):
        rehearsal.check_witness([source], witness | damage)
    with pytest.raises(EvidenceError, match="q011_position_missing_prose"):
        rehearsal.check_witness([source | {"field_pointer": "/ending_excerpt"}], witness)
