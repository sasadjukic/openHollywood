"""Bind both diagnostic drafts to the archived review and its independently frozen gold."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from uuid import UUID, uuid5

from open_hollywood_api.services.assessment_completion import _read
from open_hollywood_engine.evaluations import canonical_sha256
from open_hollywood_engine.evaluations.assessment_completion import encoded
from open_hollywood_engine.evaluations.review_evidence import require

from scripts.q010_uncertainty_plan import digest

REPO = Path(__file__).resolve().parents[2]
DATA = REPO / "data/diagnostics"
PRIOR = DATA / "q010-motion-endpoint-audit-2026-11-23"
REHEARSAL = DATA / "q011-rehearsal-2026-11-23/rendered/generation.json"
EXPORT = DATA / "ordinary-v61-single-capture-2026-11-20/output/export/review-evidence.json"
ROOT = DATA / "q011-arrival-comparison-2026-11-23"
SNAPSHOT = "ad0e734c1867e07263270310b64f9ddbee5cfd5ffefa0216cdb9c234d7a749fc"
GOLD = "d8717921ea635eb6d9d5ff548ff448d5ce37e4025ac487efb4350284c15aab8e"
REHEARSED = "fc5573a59bb78c94a3b4e49731b8ca83e5c4e1c363fecae432916a183db54f3a"
ADDED = "Elias stood at the threshold."
CASES = ("A", "B")
AUTHORITY = (
    "Assess Q011 against the supplied scene_plan and assessment_draft. The review and "
    "its candidate version are historical. Only assessment_draft establishes what is "
    "depicted in the draft under assessment. Its ending_excerpt repeats its last paragraph."
)
SCORING = {
    "eligibility": "Score a complete, budgeted, source-bound generation in a closed observed "
    "journal. Otherwise both axes are unscored. An incomplete pair is inconclusive.",
    "judgment": "Exact returned support label versus frozen whole-claim gold.",
    "evidence": "Read citations and reason against the specific version before joining the "
    "returned label. Locate both plan fields and credit depicted attraction/motion. "
    "Locate what the draft establishes about standing at the threshold at the cut. "
    "Accept precise equivalents and a located full-draft citation. A bare full-draft "
    "reference, a plan used as observed fulfillment or a material overread fails.",
    "success": "Both eligible cases must independently pass both axes. "
    "One complete pair tests sensitivity on this passage only.",
}


def packets() -> dict[str, dict[str, Any]]:
    """Only authenticated inputs and the neutral rehearsed brief enter this renderer."""
    (entry,) = json.loads(_read(EXPORT))["entries"]
    snap = entry["snapshot"]
    require(canonical_sha256(snap) == entry["snapshot_sha256"] == SNAPSHOT, "q011_snapshot")
    prior = _read(REHEARSAL)
    require(digest(prior) == REHEARSED, "q011_rehearsal")
    rehearsal = json.loads(json.loads(prior)["input"][1]["content"])
    (brief,) = rehearsal["original_work_briefs"]["briefs"]
    (active,) = rehearsal["native_work_view"]["context"]["statements"]
    review = snap["critique"]
    claim = snap["native_audit"]["check"]["current_endpoint_comparison"]
    require(
        active["unit_id"] == brief["unit_id"] == "Q011" and claim == active["quote"], "q011_claim"
    )
    sources = {a["artifact_kind"]: a for a in snap["sources"]}
    require(
        set(sources) == {"story_bible", "story_blueprint", "scene_plan", "scene_draft"},
        "q011_sources",
    )
    for art in [review, *sources.values()]:
        require(canonical_sha256(art["content"]) == art["content_sha256"], "q011_artifact")
    original = sources.pop("scene_draft")
    original_version = original["version_id"]
    require(
        snap["draft_version_id"]
        == snap["native_audit"]["candidate_version_id"]
        == review["content"]["target_artifact_version_id"]
        == original_version,
        "q011_historical_target",
    )
    require(
        snap["native_audit"]["current_plan_version_id"] == sources["scene_plan"]["version_id"],
        "q011_historical_plan",
    )
    history = {
        "version": review["version_id"],
        "invocation": snap["invocation"]["invocation_id"],
        "original_candidate_version": original_version,
        "content": review["content"],
        "saved_native_audit": snap["native_audit"],
    }
    result = {}
    for case in CASES:
        content = dict(original["content"])
        version = original_version
        if case == "B":
            content["prose"] += " " + ADDED
            version = str(uuid5(UUID(original_version), canonical_sha256(content)))
        result[case] = {
            "claim": claim,
            "work_brief": brief,
            "authority": AUTHORITY,
            "historical_review": history,
            "context": {
                k: {"version": v["version_id"], "content": v["content"]} for k, v in sources.items()
            },
            "assessment_draft": {"version": version, "content": content},
        }
    return result


def scorer(packets_by_case: dict[str, dict[str, Any]]) -> dict[str, Any]:
    raw = _read(PRIOR / "gold.json")
    require(digest(raw) == GOLD, "q011_original_gold")
    old = json.loads(raw)
    rows = {}
    for case, p in packets_by_case.items():
        plan = p["context"]["scene_plan"]
        draft = p["assessment_draft"]
        prose = draft["content"]["prose"]
        require(
            old["whole_field"]["text"] == p["claim"]
            and old["whole_claim_gold"] == "uncertain"
            and old["critique_version"] == p["historical_review"]["version"]
            and old["draft_version"] == p["historical_review"]["original_candidate_version"],
            "q011_gold_scope",
        )
        for witness in old["authority"]:
            key = witness["pointer"].rsplit("/", 1)[1]
            require(
                plan["version"] == witness["version"] and plan["content"][key] == witness["text"],
                "q011_gold_plan",
            )
        movement = old["draft_witnesses"][-1]
        start, end = movement["start"], movement["end"]
        require(
            prose[start:end] == movement["quote"]
            and digest(prose[:end].encode()) == old["prose_sha256"],
            "q011_motion",
        )
        require(prose[end:] == ("" if case == "A" else " " + ADDED), "q011_only_change")
        rows[case] = {
            "origin": "original_saved_draft"
            if case == "A"
            else "separately_authored_counterfactual",
            "draft_version": draft["version"],
            "draft_sha256": canonical_sha256(draft["content"]),
            "plan_version": plan["version"],
            "claim": p["claim"],
            "whole_claim_gold": old["whole_claim_gold"] if case == "A" else "supported",
            "assignment": [
                {
                    "ref": w["ref"],
                    "document": "scene_plan",
                    "version": plan["version"],
                    "pointer": "/" + w["pointer"].rsplit("/", 1)[1],
                    "quote": w["text"],
                }
                for w in old["authority"]
            ],
            "draft_locations": {
                "version": draft["version"],
                "E0883": "/prose",
                "D01": "/ending_excerpt",
            },
            "movement": {"span": [start, end], "text": movement["quote"]},
            "arrival": None if case == "A" else {"span": [end + 1, len(prose)], "text": ADDED},
            "ending_rule": (
                "Explain that approach with attraction leaves final position open. "
                "Neither arrival nor stopping short is established."
            )
            if case == "A"
            else "Locate the new final observation that places Elias standing at the threshold.",
        }
    require(
        rows["A"]["draft_version"] == old["draft_version"] != rows["B"]["draft_version"],
        "q011_variant_identity",
    )
    return {
        "original_gold_sha256": GOLD,
        "snapshot_sha256": SNAPSHOT,
        "cases": rows,
        "rules": SCORING,
        "scoring_contract_sha256": digest(encoded(SCORING)),
    }
