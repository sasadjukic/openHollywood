"""Resolve the local visit and cut-position audit against four exact Wading Path drafts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from open_hollywood_engine.evaluations.assessment_result import _paragraphs
from open_hollywood_engine.evaluations.review_evidence import require

from . import regression

# Operator readings of these versions. A complete draft can still omit a physical event.
PASSAGES = {
    "opening": (0, 488),
    "crossing": (3558, 3993),
    "entry": (3995, 4323),
    "look": (4325, 4571),
    "housing": (4573, 4804),
    "arrival": (4806, 4920),
    "persistent_gap": (4806, 4945),
    "retreat": (4922, 5008),
}
EXTRA = {
    "original": (),
    "arrival": ("arrival",),
    "stop": ("persistent_gap",),
    "retreat": ("arrival", "retreat"),
}
FINDINGS = {
    "original": {
        "reached": (
            "uncertain",
            "The opening and crossing lead to the wall and plenum. The "
            "complete scene gives no arrival and no exclusion spanning the scene.",
        ),
        "at_cut": (
            "uncertain",
            "The pair enter and look deeper. The final description locates "
            "the housing. Their distance from it at the cut remains open.",
        ),
    },
    "arrival": {
        "reached": ("supported", "Both people reach the named housing during the scene."),
        "at_cut": ("supported", "The final sentence places both people at the housing."),
    },
    "stop": {
        "reached": ("uncertain", "The final gap leaves any earlier visit open."),
        "at_cut": ("unsupported", "Both people remain three strides short through the ending."),
    },
    "retreat": {
        "reached": ("supported", "Both people reach the housing before withdrawing."),
        "at_cut": ("unsupported", "After arrival, both withdraw three strides and stay there."),
    },
}


def audit(archive: Path = regression.ARCHIVE) -> dict[str, Any]:
    capture = regression.verified(archive)
    gold, drafts = regression.source_drafts(capture)
    require(drafts["retreat"].startswith(drafts["arrival"] + "\n\n"), "retreat_after_arrival")
    rows = {}
    for ending, prose in drafts.items():
        version = gold["endings"][ending]
        require(prose.startswith(drafts["original"]), "different_scene_prefix")
        paragraphs = set(_paragraphs(prose))
        locators = {}
        for name in ("opening", "crossing", "entry", "look", "housing", *EXTRA[ending]):
            start, end = PASSAGES[name]
            require((start, end) in paragraphs, "audit_passage_bounds")
            locators[name] = dict(start=start, end=end, quote=prose[start:end])
        require(end == len(prose), "audit_ending_coverage")
        findings = {}
        for claim, (label, basis) in FINDINGS[ending].items():
            require(label == version["cells"][claim][0], "audit_conflicts_with_gold")
            findings[claim] = dict(label=label, basis=basis)
        rows[ending] = dict(
            version=version["version"],
            prose_sha256=version["prose_sha256"],
            ref="E1420",
            passages=locators,
            findings=findings,
        )
    old = json.loads((capture / "source/previous-locations.json").read_bytes())
    plan_outcome = old["Q008"]["E0258"]
    return dict(
        archive_sha256=regression.SEAL,
        live_calls=0,
        drafts=rows,
        assignment=dict(
            ref="E0258",
            version=plan_outcome["source_artifact_version"],
            quote=plan_outcome["quote"],
        ),
        whole_scene_exclusions=[
            k for k, row in rows.items() if row["findings"]["reached"]["label"] == "unsupported"
        ],
    )


if __name__ == "__main__":
    print(json.dumps(audit(), ensure_ascii=True, indent=2))
