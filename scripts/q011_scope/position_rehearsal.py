"""Offline Q011 rehearsal of evidence for physical position at the scene cut."""

from __future__ import annotations

from copy import deepcopy
from typing import Any
from uuid import UUID, uuid5

from open_hollywood_engine.evaluations import canonical_sha256
from open_hollywood_engine.evaluations.assessment_completion import encoded
from open_hollywood_engine.evaluations.review_evidence import require, text_hash

from scripts.q010_uncertainty_plan import digest
from scripts.q011_arrival import scope_rehearsal as prior

from . import regression

ROOT = regression.ARCHIVE.parent / "q011-position-rehearsal-2026-11-23"
GAP = "A full stride of bare earth lay between his boots and the sill."
MOTION = "He moved on toward the entrance, his eyes on the darkness inside."
ADDITIONS = {"gap-at-cut": (MOTION, GAP), "gap-before-motion": (GAP, MOTION)}
GOLD = "a184380e82e1f8d7035e5af57c895d58efb5e692c2b1e1f00ecfa25712189005"
FIXTURES = "4d0c564393712979e92e2182afd9f47b3632373bfb469a452e044beec7839ee6"
DECISIONS = "e636407815b6029777ac93e97be22d5fc9c9519a4027e6f982f4b9bafdb28b7c"


def packets() -> dict[str, dict[str, Any]]:
    manifest = prior.pinned(regression.ARCHIVE / "capture-manifest.json", regression.SEAL)
    inputs = {}
    for name in ("approach", "arrival", "stop"):
        member = f"source/{name}.json"
        inputs[name] = prior.pinned(regression.ARCHIVE / "capture" / member, manifest[member])
    for name, sentences in ADDITIONS.items():
        packet = deepcopy(inputs["approach"])
        draft = packet["assessment_draft"]
        draft["content"]["prose"] += " " + " ".join(sentences)
        draft["version"] = str(uuid5(UUID(draft["version"]), canonical_sha256(draft["content"])))
        inputs[name] = packet
    return inputs


def span(draft: dict[str, Any], quote: str) -> dict[str, Any]:
    prose = draft["content"]["prose"]
    require(bool(quote) and prose.count(quote) == 1, "q011_nonunique_witness")
    start = prose.index(quote)
    return dict(draft_version=draft["version"], start=start, end=start + len(quote), quote=quote)


def gold(inputs: dict[str, dict[str, Any]]) -> dict[str, Any]:
    judgments = {
        "approach": ("uncertain", "Direction and attraction leave the final position open."),
        "arrival": ("supported", "Elias is standing at the threshold at the cut."),
        "stop": ("unsupported", "He is planted a full stride short of the sill at the cut."),
        "gap-at-cut": (
            "unsupported",
            "The last observation puts his boots a stride from the sill.",
        ),
        "gap-before-motion": (
            "uncertain",
            "The earlier gap precedes renewed motion with no final distance or posture.",
        ),
    }
    cases = {}
    for name, (label, basis) in judgments.items():
        packet = inputs[name]
        draft = packet["assessment_draft"]
        plan = packet["context"]["scene_plan"]
        prose = draft["content"]["prose"]
        paragraph = prose.rsplit("\n\n", 1)[-1]
        cases[name] = dict(
            label=label,
            basis=basis,
            complete=draft["content"]["is_complete"],
            draft_sha256=canonical_sha256(draft["content"]),
            prose_sha256=text_hash(prose),
            closing_paragraph=span(draft, paragraph),
            gap=span(draft, GAP) if name in ADDITIONS else None,
            motion=span(draft, MOTION) if name in ADDITIONS else None,
            plan_version=plan["version"],
            plan_fields={key: plan["content"][key] for key in ("outcome", "exit_state")},
            historical_review_version=packet["historical_review"]["version"],
        )
    return dict(
        claim=prior.CLAIMS["position"],
        cases=cases,
        judgment_rule="Exact whole-claim label. Attraction is established in every case.",
        evidence_rule=(
            "Withhold the returned label. Resolve the plan assignments and the exact draft. "
            "Credit attraction, then identify the observation, its time and its bearing on "
            "standing at the sill at the cut. Accept equivalent wording. A negative requires "
            "an incompatible fact at that instant or a demonstrated persistence to that instant. "
            "An earlier gap, unquantified approach, an assignment or silence cannot do that alone."
        ),
    )


def check_witness(citations: list[dict[str, Any]], assertion: dict[str, Any]) -> None:
    """Bind the locator without deciding whether its time or inference is right."""
    sources = [
        c
        for c in citations
        if c["document_id"] == "assessment_draft" and c["field_pointer"] == "/prose"
    ]
    require(len(sources) == 1, "q011_position_missing_prose")
    (source,) = sources
    start, end = assertion["start"], assertion["end"]
    require(
        assertion["draft_version"] == source["document_version"]
        and type(start) is int
        and type(end) is int
        and 0 <= start < end <= len(source["quote"])
        and source["quote"][start:end] == assertion["quote"]
        and assertion["instant"] in {"at_cut", "before_cut"}
        and assertion["relation"] in {"establishes", "excludes", "leaves_open"},
        "q011_position_witness_binding",
    )


def observed_approach(original: dict[str, Any]) -> dict[str, Any]:
    """The witness annotates Sol's saved reason locally. The native answer is verbatim."""
    member = "operator/audit.json"
    archive = regression.ARCHIVE
    manifest = prior.pinned(archive / "capture-manifest.json", regression.SEAL)
    audit = prior.pinned(archive / "capture" / member, manifest[member])
    (delivery,) = [s for s in audit["slots"] if s["cell"] == "AP-B" and s["eligible"]]
    quote = "moved toward the dark, open threshold of the monolith"
    return dict(
        id="saved-AP",
        case="approach",
        answer=delivery["final"]["assessments"][prior.UNIT],
        witness=span(original["assessment_draft"], quote)
        | {"instant": "at_cut", "relation": "excludes"},
    )


def worksheet(
    inputs: dict[str, dict[str, Any]], fixtures: list[dict[str, Any]]
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    works = {k: prior.work_pair(k, p)[k + "-position"] for k, p in inputs.items()}
    rows, sheet = [], {}
    for item in fixtures:
        row = prior.bind_fixture(works[item["case"]], item)
        view = row.pop("view")
        assertion = item["witness"]
        check_witness(view["citations"], assertion)
        # Only source material, reason and the proposed reading reach the evidence reviewer.
        view.update(witness=assertion, work_sha256=row["work_sha256"])
        key = digest(encoded(view))
        sheet[key] = view
        rows.append(row | {"evidence_id": key})
    return rows, sheet


def replay() -> dict[str, Any]:
    inputs = packets()
    sealed = prior.pinned(ROOT / "gold.json", GOLD)
    require(sealed == gold(inputs), "q011_position_gold_drift")
    fixtures = prior.pinned(ROOT / "authored-fixtures.json", FIXTURES)
    archived = regression.replay()
    rows, sheet = worksheet(inputs, [*fixtures, observed_approach(inputs["approach"])])
    review = prior.pinned(ROOT / "evidence-decisions.json", DECISIONS)
    decisions = review["decisions"]
    require(
        prior.pinned(ROOT / "evidence-sheet.json", review["sheet_sha256"]) == sheet
        and set(decisions) == set(sheet),
        "q011_position_evidence_drift",
    )
    scores = []
    for row in rows:
        label = sealed["cases"][row["case"]]["label"]
        key = row["evidence_id"]
        scores.append(
            row
            | dict(
                gold=label,
                judgment="pass" if row["label"] == label else "fail",
                witness=sheet[key]["witness"],
                evidence=decisions[key]["outcome"],
                basis=decisions[key]["basis"],
            )
        )
    *authored, observed = scores
    history = archived["original_pair"]["cases"] + archived["clear_controls"]["cases"]
    (original,) = [r for r in history if r["case"] == "approach-position"]
    require(
        observed["id"] == "saved-AP"
        and (observed["label"], observed["judgment"], observed["evidence"])
        == (original["returned"], original["judgment"], original["evidence"]),
        "q011_position_observed_drift",
    )
    return dict(
        gold_sha256=GOLD,
        fixtures_sha256=FIXTURES,
        evidence_decisions_sha256=DECISIONS,
        historical_archive_sha256=regression.SEAL,
        authored=authored,
        saved_approach=dict(
            score=observed, archived_score=original, witness_origin="local_annotation"
        ),
        saved_depictions=[r for r in history if r["case"].endswith("-depiction")],
        historical_decision=archived["decision"],
        live_calls=0,
    )


if __name__ == "__main__":
    import json

    result = replay()
    prior.keep(ROOT / "scores.json", encoded(result))
    for row in [
        *result["authored"],
        result["saved_approach"]["score"],
        *result["saved_depictions"],
    ]:
        print(json.dumps({k: row[k] for k in ("case", "judgment", "evidence")}))
