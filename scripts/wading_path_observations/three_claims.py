"""Local Wading Path rehearsal of narration, a scene event, and position at the cut."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from uuid import UUID, uuid5

from open_hollywood_engine.evaluations import canonical_sha256
from open_hollywood_engine.evaluations.review_evidence import require, text_hash

from scripts.wading_path_be.rehearsal import FIXTURES, points, read

from . import regression

GOLD_SHA = "e900a94f71e68842950fd762080ccc3389af9c25feb0e4485932ebb7332ccb64"
ANSWERS_SHA = "10abc77cc63bdff363928bd6d9ba36610c1a039a1d43bf05bb86c1332d53fdf0"
DECISIONS_SHA = "654da1ab97c5d69bd7fa4f54a4593da507996492d7052a46d55f50ec61e54d19"


def drafts(archive: Path, gold: dict[str, Any]) -> dict[str, str]:
    require(
        canonical_sha256(gold) == GOLD_SHA and gold["archive_sha256"] == regression.SEAL,
        "three_claims_gold",
    )
    capture = regression.verified(archive)
    locations = read(capture / "operator/cited-locations.json")
    result = {}
    for ending, case in gold["endings"].items():
        source = locations[case["source_case"]]["E1420"]
        prose, version = source["quote"], source["document_version"]
        if "append_paragraph" in case:
            prose += "\n\n" + case["append_paragraph"]
            version = str(
                uuid5(UUID(locations["K1"]["E1420"]["document_version"]), text_hash(prose))
            )
        require(
            version == case["version"] and text_hash(prose) == case["prose_sha256"],
            "three_claims_draft",
        )
        result[ending] = prose
    return result


def evidence_rows(
    gold: dict[str, Any], sources: dict[str, str], fixtures: dict[str, Any]
) -> tuple[dict[str, str], dict[str, Any]]:
    """Resolve the exact cited spans and omit labels and fixture names from the evidence sheet."""
    require(fixtures.keys() == sources.keys() == gold["endings"].keys(), "three_claims_endings")
    index = {}
    masked = {}
    for ending, group in fixtures.items():
        case = gold["endings"][ending]
        prose = sources[ending]
        require(
            group["draft_version"] == case["version"] and text_hash(prose) == case["prose_sha256"],
            "three_claims_source_binding",
        )
        require(set(gold["claims"]) <= group["responses"].keys(), "three_claims_missing_answer")
        for name, answer in group["responses"].items():
            claim = name.split("/")[0]
            require(
                set(answer) == {"support", "reason", "spans"} and bool(answer["reason"].strip()),
                "three_claims_answer_fields",
            )
            require(claim in gold["claims"] and bool(answer["spans"]), "three_claims_scope")
            citations = []
            for start, end in answer["spans"]:
                require(0 <= start < end <= len(prose), "three_claims_span")
                citations.append(dict(start=start, end=end, quote=prose[start:end]))
            view = dict(
                claim=gold["claims"][claim],
                draft_version=group["draft_version"],
                prose_sha256=case["prose_sha256"],
                reason=answer["reason"],
                citations=citations,
            )
            sid = canonical_sha256(view)
            index[f"{ending}/{name}"] = sid
            masked[sid] = view
    return index, dict(sorted(masked.items()))


def grade_answers(
    gold: dict[str, Any],
    sources: dict[str, str],
    fixtures: dict[str, Any],
    decisions: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    require(canonical_sha256(gold) == GOLD_SHA, "three_claims_gold")
    require(canonical_sha256(decisions) == DECISIONS_SHA, "three_claims_evidence_seal")
    index, masked = evidence_rows(gold, sources, fixtures)
    require(set(index.values()) == decisions.keys(), "three_claims_unreviewed_evidence")
    rows = {}
    for ending, group in fixtures.items():
        for name, answer in group["responses"].items():
            claim = name.split("/")[0]
            expected, _ = gold["endings"][ending]["cells"][claim]
            returned = answer["support"]
            require(returned in ("supported", "unsupported", "uncertain"), "three_claims_label")
            key = f"{ending}/{name}"
            sid = index[key]
            decision = decisions[sid]
            rows[key] = dict(
                origin="authored_local_response",
                draft_version=group["draft_version"],
                expected=expected,
                returned=returned,
                evidence_id=sid,
                basis=decision["basis"],
                **points(returned, expected, decision["adequate"]),
            )
    return rows, masked


def rehearse(archive: Path = regression.ARCHIVE) -> dict[str, Any]:
    gold = read(FIXTURES / "wading_path_three_claims_gold.json")
    fixtures = read(FIXTURES / "wading_path_three_claims_answers.json")
    require(canonical_sha256(fixtures) == ANSWERS_SHA, "three_claims_answers")
    decisions = read(FIXTURES / "wading_path_three_claims_evidence.json")
    rows, sheet = grade_answers(gold, drafts(archive, gold), fixtures, decisions)
    historical = regression.replay(archive)
    return dict(
        live_calls=0,
        gold_sha256=GOLD_SHA,
        evidence_decisions_sha256=DECISIONS_SHA,
        answers_sha256=canonical_sha256(fixtures),
        evidence_sheet=sheet,
        rows=rows,
        historical_q008_b=historical["rows"]["Q008-B"],
        historical_evidence_seal=historical["evidence_decisions_sha256"],
    )


if __name__ == "__main__":
    print(json.dumps(rehearse(), ensure_ascii=True, indent=2))
