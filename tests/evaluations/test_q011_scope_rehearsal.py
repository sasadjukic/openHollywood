"""Keep rehearsal truth in the scorer and the two active authored claims source-bound."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from open_hollywood_engine.evaluations.assessment_compact_presentation import SYSTEM, compact
from open_hollywood_engine.evaluations.assessment_result import (
    assessment_response_schema,
    bind_assessment_result,
    scope_for_batch,
)
from open_hollywood_engine.evaluations.assessment_work import AssessmentReceipt
from open_hollywood_engine.evaluations.review_evidence import EvidenceError, text_hash

from scripts import verify_q010_endpoint_controls as controls
from scripts.q011_arrival import regression
from scripts.q011_arrival import scope_rehearsal as rehearsal

pytestmark = pytest.mark.skipif(
    not (rehearsal.ROOT / "evidence-decisions.json").is_file(),
    reason="requires the private Q011 scope rehearsal",
)


@pytest.mark.parametrize("ending", ["approach", "arrival", "stop"])
def test_subject_is_only_material_difference(ending: str) -> None:
    packet = rehearsal.packets()[ending]
    pair = rehearsal.work_pair(ending, packet)
    comparable = []
    for subject, claim in rehearsal.CLAIMS.items():
        work = pair[ending + "-" + subject]
        system, user = work.context.messages
        assert system.content == SYSTEM
        payload = json.loads(user.content)
        assert set(payload) == {"active_unit_ids", "claim", "work_brief", "documents"}
        assert payload["active_unit_ids"] == [rehearsal.UNIT]
        assert payload.pop("claim") == {
            "field_id": rehearsal.UNIT,
            "pointer": "/claim",
            "text": claim,
        }
        documents = {doc["identity"]: doc for doc in payload.pop("documents")}
        authored = documents.pop("authored-claim")
        assert authored["kind"] == "report" and authored["structured_content"] == {
            "parent_field": "Q011",
            "claim": claim,
        }
        history = documents["historical-review"]
        assert (
            history["kind"] == "source"
            and history["structured_content"] == packet["historical_review"]
        )
        assert (
            history["structured_content"]["saved_native_audit"]["check"][
                "current_endpoint_comparison"
            ]
            == packet["claim"]
        )
        for role, source in packet["context"].items():
            assert documents[role]["version"] == source["version"]
            assert documents[role]["structured_content"] == source["content"]
        draft = documents["assessment_draft"]
        expected = packet["assessment_draft"]
        paragraph = expected["content"]["prose"].rsplit("\n\n", 1)[-1]
        assert draft["version"] == expected["version"] and draft["structured_content"] == expected[
            "content"
        ] | {"ending_excerpt": paragraph}
        scope = scope_for_batch(work, work.batches[0].batch_id, work.context.origin_sha256)
        schema = assessment_response_schema(work, scope)
        comparable.append((payload, documents, schema))
    assert comparable[0] == comparable[1]
    assert len({work.fingerprint for work in pair.values()}) == 2


def test_claim_and_evidence_scored_independently() -> None:
    result = rehearsal.replay()
    assert result["live_calls"] == 0
    assert result == json.loads((rehearsal.ROOT / "scores.json").read_bytes())
    rows = result["scores"]
    assert {(r["case"], r["gold"]) for r in rows if r["id"].startswith("grounded-")} == {
        ("approach-position", "uncertain"),
        ("approach-depiction", "unsupported"),
        ("arrival-position", "supported"),
        ("arrival-depiction", "supported"),
        ("stop-position", "unsupported"),
        ("stop-depiction", "unsupported"),
    }
    assert all(
        r["judgment"] == r["evidence"] == "pass" for r in rows if r["id"].startswith("grounded-")
    )
    assert {
        r["id"]: (r["judgment"], r["evidence"]) for r in rows if not r["id"].startswith("grounded-")
    } == {
        "cut-rules-out-arrival": ("fail", "fail"),
        "label-only": ("fail", "pass"),
        "word-search": ("pass", "fail"),
        "earlier-stop": ("pass", "fail"),
    }
    by_id = {r["id"]: r for r in rows}
    assert by_id["grounded-approach-position"]["evidence_id"] == by_id["label-only"]["evidence_id"]


def test_building_work_needs_only_source_files(monkeypatch: pytest.MonkeyPatch) -> None:
    arc = regression.ARCHIVE
    frozen = controls.ROOT / "frozen"
    allowed = {
        arc / "capture-manifest.json",
        arc / "capture/source/A.json",
        arc / "capture/source/B.json",
        frozen / "seal.json",
        frozen / "packets/P07.json",
    }
    read_bytes = Path.read_bytes
    seen = set()

    def source_only(path: Path) -> bytes:
        assert path in allowed, path
        seen.add(path)
        return read_bytes(path)

    monkeypatch.setattr(Path, "read_bytes", source_only)
    for ending, source in rehearsal.packets().items():
        assert len(rehearsal.work_pair(ending, source)) == 2
    assert seen == allowed


def test_different_claim_or_draft_rejects_same_receipt() -> None:
    inputs = rehearsal.packets()
    position, depiction = rehearsal.work_pair("approach", inputs["approach"]).values()
    stop = rehearsal.work_pair("stop", inputs["stop"])["stop-position"]
    fixtures: list[dict[str, Any]] = rehearsal.pinned(
        rehearsal.ROOT / "authored-fixtures.json", rehearsal.FIXTURES
    )
    raw = compact({"assessments": {rehearsal.UNIT: fixtures[0]["answer"]}})
    receipt = AssessmentReceipt(
        work_sha256=position.fingerprint,
        batch_id=position.batches[0].batch_id,
        request_sha256=position.context.origin_sha256,
        attempt_id="fixture",
        status="valid",
        result_sha256=text_hash(raw),
        assessed_unit_ids=(rehearsal.UNIT,),
        active_seconds=0,
    )
    for target in (depiction, stop):
        scope = scope_for_batch(target, target.batches[0].batch_id, target.context.origin_sha256)
        with pytest.raises(EvidenceError, match="mixed_work_scope"):
            bind_assessment_result(target, scope, receipt, raw)
