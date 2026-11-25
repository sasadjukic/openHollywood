"""Rehearse explicit narration and event truth against three histories with one fixed stop."""

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

GOLD_SHA = "860841fa62b1a951b7778c128d788e106f01f1fde6ca8a117f24b42111724185"
ANSWERS_SHA = "753d0334624132dad4c904137e13dc1d0231f19a9cc2b1a3c56d64576845a7ec"
EVIDENCE_SHA = "73d96f97a1178448f557dbe44c5d93a8ef3a92445ceee79313b78a884540daea"


def sources(archive: Path, gold: dict[str, Any]) -> dict[str, str]:
    require(
        canonical_sha256(gold) == GOLD_SHA and gold["archive_sha256"] == regression.SEAL,
        "narration_event_gold",
    )
    historical, prose = regression.source_drafts(regression.verified(archive))
    endings, stop = gold["endings"], prose["stop"]
    gap = gold["fixed_stop"]
    require(
        stop[gap["start"] :] == gap["quote"] and len(stop) == gap["end"], "narration_event_stop"
    )
    for name in ("stop", "exclusion"):
        require(
            endings[name]["version"] == historical["endings"][name]["version"],
            "narration_event_version",
        )
    drafts = {
        "stop": stop,
        "exclusion": prose["exclusion"],
        "visit": stop + "\n\n" + endings["visit"]["append_paragraph"],
    }
    for name in ("exclusion", "visit"):
        variant = endings[name]
        require(
            drafts[name] == stop + "\n\n" + variant["append_paragraph"]
            and variant["parent_version"] == endings["stop"]["version"]
            and variant["version"]
            == str(uuid5(UUID(variant["parent_version"]), text_hash(drafts[name]))),
            "narration_event_retrospective",
        )
    require(
        all(text_hash(draft) == endings[name]["prose_sha256"] for name, draft in drafts.items()),
        "narration_event_source",
    )
    return drafts


def grade(
    gold: dict[str, Any], drafts: dict[str, str], answers: dict[str, Any], decisions: dict[str, Any]
) -> tuple[dict[str, Any], dict[str, Any]]:
    require(canonical_sha256(gold) == GOLD_SHA, "narration_event_gold")
    require(canonical_sha256(decisions) == EVIDENCE_SHA, "narration_event_evidence_seal")
    index, sheet = evidence_rows(gold, drafts, answers)
    require(sheet.keys() == decisions.keys(), "narration_event_unreviewed_evidence")
    rows = {}
    for history, group in answers.items():
        for name, answer in group["responses"].items():
            key = f"{history}/{name}"
            claim = name.split("/")[0]
            expected = gold["endings"][history]["cells"][claim][0]
            label = answer["support"]
            require(label in ("supported", "unsupported", "uncertain"), "narration_event_label")
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
        read(FIXTURES / f"wading_path_narration_event_{name}.json")
        for name in ("gold", "answers", "evidence")
    )
    require(canonical_sha256(answers) == ANSWERS_SHA, "narration_event_answers")
    rows, sheet = grade(gold, sources(archive, gold), answers, decisions)
    replay = regression.replay(archive)
    return dict(
        live_calls=0,
        gold_sha256=GOLD_SHA,
        answers_sha256=ANSWERS_SHA,
        evidence_decisions_sha256=EVIDENCE_SHA,
        evidence_sheet=sheet,
        rows=rows,
        historical_evidence_seal=replay["evidence_decisions_sha256"],
        historical_rows={key: replay["rows"][key] for key in ("S1-B", "S2-B")},
    )


if __name__ == "__main__":
    print(json.dumps(rehearse(), ensure_ascii=True, indent=2))
