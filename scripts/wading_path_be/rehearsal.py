"""Offline Q011 label substitution and source-bound ending controls for The Wading Path."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from uuid import UUID, uuid5

from open_hollywood_engine.evaluations import canonical_sha256
from open_hollywood_engine.evaluations.review_evidence import require, text_hash

from . import regression

FIXTURES = Path(__file__).resolve().parents[2] / "tests/fixtures"
GOLD_SHA = "d5037c4c4498a6833f4c0ddafcb57841d1422dffe46721922b1ddedc93e1daa7"
DECISIONS_SHA = "23e20e74ca4dcf6fd62664adc17cdaaccf300ba77d7792ff3022281f870cacb4"

# Authored after freezing the claims, prose, gold and rubric. These are local answer fixtures.
ANSWERS = {
    "original": (
        "uncertain",
        "The plan requires reaching the housing and standing before the final barrier. Elias and "
        "Maya reach the wall, enter the plenum and look deeper. The housing stands at the far end "
        "and is the barrier. This tells us neither whether they reach it nor where they stand at "
        "the cut.",
    ),
    "arrival": (
        "supported",
        "The plan assigns reaching the housing and standing before the barrier. The preceding "
        "paragraph identifies the housing as that barrier. The last sentence says Elias and Maya "
        "reach the housing and stand side by side before it, fulfilling both assignments.",
    ),
    "stop_short": (
        "unsupported",
        "The plan calls for reaching the housing and standing before the final barrier. The draft "
        "identifies the housing as that barrier. Its last sentence holds both people three strides "
        "short at the cut. This rules out the assigned exit position and defeats the conjunction. "
        "Their position at this instant leaves any earlier arrival open.",
    ),
}


def read(path: Path) -> Any:
    return json.loads(path.read_bytes())


def materials(capture: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    gold = read(FIXTURES / "wading_path_q011_endings.json")
    require(canonical_sha256(gold) == GOLD_SHA, "wading_rehearsal_gold")
    historical = read(capture / "run/gold.json")
    claim = next(c for c in historical["claims"] if c["field_id"] == "Q011")
    binding = historical["binding"]
    require(
        gold["archive_manifest_sha256"] == regression.SEAL
        and (gold["critique_version"], gold["plan_version"], gold["original_draft_version"])
        == (binding["critique"], binding["plan"], binding["draft"])
        and (gold["claim"], gold["plan_refs"]) == (claim["text"], claim["plan_refs"]),
        "wading_rehearsal_binding",
    )
    original = read(capture / "operator/cited-locations.json")["E1420"]["quote"]
    cases = {}
    for name, c in gold["cases"].items():
        paragraph = c["append_paragraph"]
        prose = original + ("\n\n" + paragraph if paragraph else "")
        sha = text_hash(prose)
        require(sha == c["full_draft_sha256"], "wading_rehearsal_prose")
        version = str(uuid5(UUID(binding["draft"]), sha)) if paragraph else binding["draft"]
        cut = paragraph or original[historical["draft_witnesses"]["0063"]["start"] :]
        cases[name] = dict(
            draft_version=version,
            prose_sha256=sha,
            draft_ref=f"local-draft/{version}" if paragraph else "E1420",
            cut_span=[len(prose) - len(cut), len(prose)],
            cut_quote=cut,
            barrier_witness=historical["draft_witnesses"]["0069"]["quote"],
        )
    return gold, cases


def evidence_view(answer: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in answer.items() if k != "support"}


def authored_view(name: str, case: dict[str, Any], gold: dict[str, Any]) -> dict[str, Any]:
    return dict(
        reason=ANSWERS[name][1],
        evidence=[*gold["plan_refs"], case["draft_ref"]],
        plan_version=gold["plan_version"],
        draft_version=case["draft_version"],
        prose_sha256=case["prose_sha256"],
    )


def points(label: str, expected: str, evidence: bool) -> dict[str, int]:
    return dict(judgment=int(label == expected), evidence=int(evidence))


def rehearse(archive: Path = regression.ARCHIVE) -> dict[str, Any]:
    replay = regression.replay(archive)
    capture = archive / "capture"
    gold, cases = materials(capture)
    slots = read(capture / "operator/audit.json")["slots"]
    original_gold = gold["cases"]["original"]["gold"]
    fixed = {}
    stale = {}
    for arm in ("B", "E"):
        cell = f"Q011-{arm}"
        slot = next(s for s in slots if s["cell"] == cell and s["eligible"])
        observed = slot["final"]["assessments"]["Q011"]
        local = {**observed, "support": "uncertain"}
        require(
            {k for k in observed if observed[k] != local[k]} == {"support"}
            and evidence_view(observed) == evidence_view(local),
            "wading_rehearsal_only_label",
        )
        grade = replay["rows"][cell]
        credit = grade["evidence"] == "pass"
        fixed[arm] = dict(
            observed_answer=observed,
            local_label_only_answer=local,
            evidence_view_sha256=canonical_sha256(evidence_view(observed)),
            sealed_evidence_basis=grade["basis"],
            observed_scores=points(observed["support"], original_gold, credit),
            local_scores=points(local["support"], original_gold, credit),
        )
        # Apply the exact same words and citations as a content challenge on each authored ending.
        # The original delivery remains bound exclusively to draft v1.
        for name in ("arrival", "stop_short"):
            require(
                gold["original_draft_version"] in local["reason"]
                and "E1420" in local["evidence"]
                and cases[name]["draft_ref"] not in local["evidence"],
                "wading_rehearsal_stale_control",
            )
            stale[f"{name}-{arm}"] = points(local["support"], gold["cases"][name]["gold"], False)

    form = read(FIXTURES / "wading_path_q011_evidence_decisions.json")
    require(canonical_sha256(form) == DECISIONS_SHA, "wading_rehearsal_evidence_decisions")
    controls = {}
    for name, case in cases.items():
        masked = authored_view(name, case, gold)
        decision = form[name]
        require(canonical_sha256(masked) == decision["evidence_view_sha256"], "ungraded_evidence")
        label = ANSWERS[name][0]
        controls[name] = dict(
            **case,
            **gold["cases"][name],
            response={**masked, "support": label},
            evidence_basis=decision["basis"],
            scores=points(label, gold["cases"][name]["gold"], decision["adequate"]),
        )
    return dict(
        gold_sha256=GOLD_SHA,
        evidence_decisions_sha256=DECISIONS_SHA,
        live_calls=0,
        label_substitutions=fixed,
        unchanged_text_on_other_drafts=stale,
        authored_responses=controls,
        narrated_arrival_control=replay["rows"]["Q008-B"],
    )


if __name__ == "__main__":
    print(json.dumps(rehearse(), indent=2, ensure_ascii=True))
