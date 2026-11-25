"""Resolve the evidence used for the S1 whole-scene rejection against sealed sources."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from open_hollywood_engine.evaluations.assessment_result import _paragraphs
from open_hollywood_engine.evaluations.review_evidence import require

from scripts.wading_path_three_claims.coverage import PASSAGES

from . import regression


def audit(archive: Path = regression.ARCHIVE) -> dict[str, Any]:
    capture = regression.verified(archive)
    gold, drafts = regression.source_drafts(capture)
    sheet = json.loads((capture / "operator/evidence-sheet.json").read_bytes())
    answers = {r["case"]: r for r in sheet["rows"]}
    prior_loc = json.loads((capture / "source/prior-locations.json").read_bytes())
    retreat = prior_loc["R2"]["E1420"]
    drafts["retreat"] = retreat["quote"]
    require(drafts["retreat"].startswith(drafts["arrival"] + "\n\n"), "audit_retreat_parent")
    bounds = {**PASSAGES, "exclusion": (4947, 5149)}
    common = ("opening", "crossing", "entry", "look", "housing")
    endings = {
        "stop": ("persistent_gap",),
        "exclusion": ("persistent_gap", "exclusion"),
        "arrival": ("arrival",),
        "retreat": ("arrival", "retreat"),
    }
    sources = {}
    for ending, extra in endings.items():
        prose = drafts[ending]
        paragraphs = set(_paragraphs(prose))
        passages = {}
        for name in (*common, *extra):
            start, end = bounds[name]
            require((start, end) in paragraphs, "scope_passage_bounds")
            passages[name] = dict(start=start, end=end, quote=prose[start:end])
        require(end == len(prose), "scope_passage_ending")
        version = (
            retreat["document_version"]
            if ending == "retreat"
            else gold["endings"][ending]["version"]
        )
        sources[ending] = dict(version=version, ref="E1420", passages=passages)

    # Compare the instructions Sol received for the two visit claims and the endpoint control.
    packets = {}
    systems = []
    for case in ("S1", "X1", "S2"):
        request = capture / f"run/requests/{case}-B-generation.json"
        messages = json.loads(request.read_bytes())["input"]
        systems.append(messages[0]["content"])
        packets[case] = json.loads(messages[1]["content"])
    scope = packets["S1"]["claim_scope"]
    brief = packets["S1"]["work_brief"]
    require(
        len(set(systems)) == 1
        and scope == packets["X1"]["claim_scope"]
        and all(p["work_brief"] == brief for p in packets.values())
        and scope["statement"]["quote"] == gold["claims"]["reached"]
        and packets["S2"]["claim_scope"]["statement"]["quote"] == gold["claims"]["at_cut"]
        and scope["source_scopes"]
        == [dict(coverage="complete_fields", evidence_refs=["E1420"], role="draft")],
        "scope_request_binding",
    )
    prior_scores = json.loads((capture / "source/prior-scores.json").read_bytes())["rows"]
    return dict(
        manifest_sha256=regression.SEAL,
        live_calls=0,
        visit_claim=scope["statement"]["quote"],
        cut_claim=gold["claims"]["at_cut"],
        brief=brief,
        sources=sources,
        reasons={case: row["reason"] for case, row in answers.items()},
        historical_retreat_visit=prior_scores["R2-B"],
    )


if __name__ == "__main__":
    print(json.dumps(audit(), ensure_ascii=True, indent=2))
