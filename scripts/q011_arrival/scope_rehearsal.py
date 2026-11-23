"""Offline Q011 position and paragraph-coverage rehearsal on authenticated Elias prose."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any
from uuid import UUID, uuid5

from open_hollywood_engine.evaluations import canonical_sha256
from open_hollywood_engine.evaluations.assessment_authored_source import _document
from open_hollywood_engine.evaluations.assessment_compact_presentation import SYSTEM, compact
from open_hollywood_engine.evaluations.assessment_completion import encoded
from open_hollywood_engine.evaluations.assessment_result import (
    bind_assessment_result,
    scope_for_batch,
)
from open_hollywood_engine.evaluations.assessment_work import (
    AssessmentReceipt,
    AssessmentWork,
    ReportField,
    SelectedStatement,
    partition_work,
)
from open_hollywood_engine.evaluations.review_evidence import SavedMessage, require, text_hash

from scripts import verify_q010_endpoint_controls as controls
from scripts.q010_uncertainty_plan import digest

from . import plan, regression, sources

ROOT = sources.DATA / "q011-scope-rehearsal-2026-11-23"
UNIT = "Q011-scope"
GOLD = "b903a9bed15c12df89ab684653bb95829ce5d762d0b42649dd1669d1faa0fa92"
FIXTURES = "d21b7f21ef9fc3bffa52a137df8851f73fa052ae222b82467b6d1e414e5971e7"
DECISIONS = "e5702942f045a25b1d40821a7efee2031b98bb249eb038944d28978aa5330c2a"
CLAIMS = {
    "position": "Elias is drawn to the entrance. At the scene cut he stands at the threshold.",
    "depiction": "Elias is drawn to the entrance. The complete closing paragraph depicts him "
    "standing at the threshold at the scene cut.",
}
STOP = "He came to a standstill a full stride short of the sill, both feet planted in the dirt."
LABELS = {
    "approach": {"position": "uncertain", "depiction": "unsupported"},
    "arrival": {"position": "supported", "depiction": "supported"},
    "stop": {"position": "unsupported", "depiction": "unsupported"},
}


def pinned(path: Path, sha: str) -> Any:
    raw = path.read_bytes()
    require(digest(raw) == sha, "q011_scope_source_drift")
    return json.loads(raw)


def packets() -> dict[str, dict[str, Any]]:
    archive = regression.ARCHIVE
    members = pinned(archive / "capture-manifest.json", regression.SEAL)
    a, b = (
        pinned(archive / "capture" / member, members[member])
        for member in ("source/A.json", "source/B.json")
    )
    frozen = controls.ROOT / "frozen"
    index = pinned(frozen / "seal.json", controls.SEAL)
    p07_raw = (frozen / "packets/P07.json").read_bytes()
    require(digest(p07_raw) == index["packets_sha256"]["P07"], "q011_scope_p07_drift")
    p07 = controls.Packet.model_validate_json(p07_raw)
    (donor,) = [s for s in p07.sources if s.ref == "S02"]
    original = a["assessment_draft"]
    prose = original["content"]["prose"]
    require(
        p07.claim_id == "Q010"
        and donor.version == p07.scene_draft_version
        and donor.text_sha256 == text_hash(donor.text)
        and donor.text == prose + " " + STOP
        and b["assessment_draft"]["content"]
        == original["content"] | {"prose": prose + " " + sources.ADDED}
        and {k: v for k, v in a.items() if k != "assessment_draft"}
        == {k: v for k, v in b.items() if k != "assessment_draft"},
        "q011_scope_source_binding",
    )
    c = deepcopy(a)
    draft = c["assessment_draft"]
    draft["content"]["prose"] = donor.text
    draft["version"] = str(uuid5(UUID(original["version"]), canonical_sha256(draft["content"])))
    require(
        len(
            {original["version"], b["assessment_draft"]["version"], draft["version"], donor.version}
        )
        == 4,
        "q011_scope_version_alias",
    )
    return {"approach": a, "arrival": b, "stop": c}


def gold(inputs: dict[str, dict[str, Any]]) -> dict[str, Any]:
    rows = {}
    for ending, packet in inputs.items():
        draft, plan = packet["assessment_draft"], packet["context"]["scene_plan"]
        prose = draft["content"]["prose"]
        paragraph = prose.rsplit("\n\n", 1)[-1]
        start = len(prose) - len(paragraph)
        require(
            start == 3085 and draft["content"]["is_complete"], "q011_scope_incomplete_paragraph"
        )
        for subject, claim in CLAIMS.items():
            rows[f"{ending}-{subject}"] = dict(
                derived_claim=claim,
                parent_Q011=packet["claim"],
                historical_critique=packet["historical_review"]["version"],
                plan_version=plan["version"],
                draft_version=draft["version"],
                draft_content_sha256=canonical_sha256(draft["content"]),
                prose_sha256=text_hash(prose),
                plan_witnesses={k: plan["content"][k] for k in ("outcome", "exit_state")},
                paragraph=paragraph,
                paragraph_span=[start, len(prose)],
                gold=LABELS[ending][subject],
            )
    return dict(
        cases=rows,
        rules={
            "judgment": "Exact label for the whole authored claim, with attraction established "
            "in each ending.",
            "shared_evidence": "Locate the two assignments in the plan and credit the depicted "
            "attraction in the assessed draft. The plan supplies no observed position.",
            "position": "Evaluate physical standing at the cut. A negative requires a same-instant "
            "incompatible observation. An earlier stop or silence at the cut is insufficient.",
            "depiction": "Inspect the entire closing paragraph for affirmative placement at the "
            "threshold, including equivalent descriptions. A complete paragraph can disprove the "
            "textual assertion without determining the physical position.",
            "evidence": "Score the cited passage and reasoning with the answer label withheld. Any "
            "material overread fails. Accept located full-draft citations and semantic "
            "equivalents.",
        },
    )


def keep(path: Path, raw: bytes) -> None:
    if path.exists():
        require(path.read_bytes() == raw, "q011_scope_replay_drift")
    else:
        with path.open("xb") as handle:
            handle.write(raw)


def work_pair(ending: str, packet: dict[str, Any]) -> dict[str, AssessmentWork]:
    # Reuse the registered Q011 renderer only for the unchanged story, parent and locations.
    original = plan.render("A" if ending == "approach" else "B", packet).work.context
    docs = tuple(
        d.model_copy(update={"kind": "source"}) if d.kind == "report" else d
        for d in original.documents
    )
    visible: list[dict[str, Any]] = json.loads(original.messages[0].content)["native_work_view"][
        "context"
    ]["documents"]
    for entry in visible:
        if entry["identity"] == "historical-review":
            entry["kind"] = "source"
    brief = {
        "unit_id": UNIT,
        "question": "Assess the whole active claim according to its stated subject.",
        "temporal_scope": "Scene one through its final narrated instant.",
        "source_authority": "Use the plan for the assignment and the assessed draft for the story "
        "and its closing paragraph. The historical review records the parent claim.",
        "evidence_obligation": "Locate both plan fields and the relevant passage. Explain what "
        "each material part of the claim requires and what the cited source establishes.",
    }
    works = {}
    for subject, claim in CLAIMS.items():
        report = _document("authored-claim", "report", {"claim": claim, "parent_field": "Q011"})
        report = report.model_copy(update={"version": report.content_sha256})
        field = ReportField(field_id=UNIT, pointer="/claim", text=claim)
        stmt = SelectedStatement(unit_id=UNIT, field_id=UNIT, start=0, end=len(claim), quote=claim)
        authored = report.model_dump(mode="json", exclude={"content_json"})
        authored["structured_content"] = json.loads(report.content_json)
        user = compact(
            {
                "active_unit_ids": [UNIT],
                "claim": field.model_dump(mode="json"),
                "work_brief": brief,
                "documents": [*visible, authored],
            }
        )
        ctx = original.model_copy(
            update=dict(
                provenance="synthetic_fixture",
                origin_sha256=text_hash(user),
                documents=(*docs, report),
                report_fields=(field,),
                statements=(stmt,),
                messages=(
                    SavedMessage(role="system", content=SYSTEM),
                    SavedMessage(role="user", content=user),
                ),
            )
        )
        works[ending + "-" + subject] = partition_work(ctx, 1)
    return works


def bind_fixture(work: AssessmentWork, item: dict[str, Any]) -> dict[str, Any]:
    (batch,) = work.batches
    scope = scope_for_batch(work, batch.batch_id, work.context.origin_sha256)
    raw = compact({"assessments": {UNIT: item["answer"]}})
    receipt = AssessmentReceipt(
        work_sha256=work.fingerprint,
        request_sha256=scope.request_sha256,
        batch_id=batch.batch_id,
        attempt_id=item["id"],
        result_sha256=text_hash(raw),
        assessed_unit_ids=(UNIT,),
        status="valid",
        active_seconds=0,
    )
    bound = bind_assessment_result(work, scope, receipt, raw)
    (unit,) = bound.units
    view = dict(
        case=item["case"],
        claim=unit.statement.quote,
        reason=unit.model_assessment.reason,
        citations=[e.model_dump(mode="json") for e in unit.evidence_locations],
    )
    return dict(
        id=item["id"],
        case=item["case"],
        work_sha256=work.fingerprint,
        final_sha256=text_hash(raw),
        label=unit.model_assessment.support,
        evidence_id=digest(encoded(view)),
        view=view,
    )


def worksheet(
    inputs: dict[str, dict[str, Any]], fixtures: list[dict[str, Any]]
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    works = {
        k: work
        for ending, packet in inputs.items()
        for k, work in work_pair(ending, packet).items()
    }
    require(len({w.fingerprint for w in works.values()}) == 6, "q011_scope_work_identity")
    rows, sheet = [], {}
    for item in fixtures:
        row = bind_fixture(works[item["case"]], item)
        sheet[row["evidence_id"]] = row.pop("view")
        rows.append(row)
    return rows, sheet


def replay() -> dict[str, Any]:
    inputs = packets()
    sealed = pinned(ROOT / "gold.json", GOLD)
    require(sealed == gold(inputs), "q011_scope_gold_drift")
    fixtures = pinned(ROOT / "authored-fixtures.json", FIXTURES)
    rows, sheet = worksheet(inputs, fixtures)
    reviews = pinned(ROOT / "evidence-decisions.json", DECISIONS)
    require(
        pinned(ROOT / "evidence-sheet.json", reviews["sheet_sha256"]) == sheet
        and set(reviews["decisions"]) == set(sheet),
        "q011_scope_inspection_binding",
    )
    scored = []
    for row in rows:
        case = sealed["cases"][row["case"]]
        judgment = "pass" if row["label"] == case["gold"] else "fail"
        review = reviews["decisions"][row["evidence_id"]]
        scored.append(
            dict(
                **row,
                gold=case["gold"],
                judgment=judgment,
                evidence=review["outcome"],
                basis=review["basis"],
            )
        )
    return dict(
        origin="authored_local_fixtures",
        live_calls=0,
        gold_sha256=GOLD,
        evidence_decisions_sha256=DECISIONS,
        scores=scored,
    )


if __name__ == "__main__":
    result = replay()
    keep(ROOT / "scores.json", encoded(result))
    for row in result["scores"]:
        print(row["id"], row["label"], row["judgment"], row["evidence"])
