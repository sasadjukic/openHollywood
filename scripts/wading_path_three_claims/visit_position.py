"""Offline rehearsal of two factual claims on five exact Wading Path drafts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from uuid import UUID, uuid5

from open_hollywood_engine.evaluations import canonical_sha256
from open_hollywood_engine.evaluations.review_evidence import require, text_hash

from scripts.wading_path_be.rehearsal import FIXTURES, points, read
from scripts.wading_path_observations.three_claims import evidence_rows

from . import regression

GOLD_SHA = "77f6f1044007dbc79f0b31330b50c66b9beb9bd17ea2960087b0d4919eebc8e6"
ANSWERS_SHA = "ba2f2447dd33e5ed3c11b1f8b43f503381e8877be5db782588e4efc3ed27edff"
DECISIONS_SHA = "4cc04c9bf0576a2bea166a5895dd5a639a3ae3dd5f19100319af69e5eeefbe57"


def drafts(archive: Path, gold: dict[str, Any]) -> dict[str, str]:
    require(
        canonical_sha256(gold) == GOLD_SHA and gold["archive_sha256"] == regression.SEAL,
        "visit_position_gold",
    )
    original, sources = regression.source_drafts(regression.verified(archive))
    for claim, text in gold["claims"].items():
        require(text == original["claims"][claim], "visit_position_claim")
    for ending in sources:
        previous, current = original["endings"][ending], gold["endings"][ending]
        require(
            current["version"] == previous["version"]
            and current["prose_sha256"] == previous["prose_sha256"]
            and all(current["cells"][c] == previous["cells"][c] for c in gold["claims"]),
            "visit_position_historical_binding",
        )
    new = gold["endings"]["exclusion"]
    parent = gold["endings"]["stop"]
    prose = sources["stop"] + "\n\n" + new["append_paragraph"]
    sha = text_hash(prose)
    require(
        new["parent"] == "stop"
        and new["parent_version"] == parent["version"]
        and new["version"] == str(uuid5(UUID(parent["version"]), sha))
        and new["prose_sha256"] == sha,
        "visit_position_exclusion_binding",
    )
    return {**sources, "exclusion": prose}


def grade(
    gold: dict[str, Any],
    sources: dict[str, str],
    answers: dict[str, Any],
    decisions: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    require(canonical_sha256(gold) == GOLD_SHA, "visit_position_gold")
    require(canonical_sha256(decisions) == DECISIONS_SHA, "visit_position_evidence_seal")
    index, sheet = evidence_rows(gold, sources, answers)
    require(set(sheet) == decisions.keys(), "visit_position_unreviewed_evidence")
    rows = {}
    for ending, group in answers.items():
        for name, answer in group["responses"].items():
            claim = name.split("/")[0]
            expected = gold["endings"][ending]["cells"][claim][0]
            label = answer["support"]
            require(label in ("supported", "unsupported", "uncertain"), "visit_position_label")
            key = f"{ending}/{name}"
            sid = index[key]
            decision = decisions[sid]
            rows[key] = dict(
                origin="authored_local_response",
                expected=expected,
                returned=label,
                draft_version=group["draft_version"],
                evidence_id=sid,
                basis=decision["basis"],
                **points(label, expected, decision["adequate"]),
            )
    return rows, sheet


def rehearse(archive: Path = regression.ARCHIVE) -> dict[str, Any]:
    gold, answers, decisions = (
        read(FIXTURES / f"wading_path_visit_position_{name}.json")
        for name in ("gold", "answers", "evidence")
    )
    require(canonical_sha256(answers) == ANSWERS_SHA, "visit_position_answers")
    rows, sheet = grade(gold, drafts(archive, gold), answers, decisions)
    previous = regression.replay(archive)
    return dict(
        live_calls=0,
        gold_sha256=GOLD_SHA,
        answers_sha256=ANSWERS_SHA,
        evidence_decisions_sha256=DECISIONS_SHA,
        evidence_sheet=sheet,
        rows=rows,
        historical_rows=previous["rows"],
        historical_evidence_seal=previous["evidence_decisions_sha256"],
    )


if __name__ == "__main__":
    print(json.dumps(rehearse(), ensure_ascii=True, indent=2))
