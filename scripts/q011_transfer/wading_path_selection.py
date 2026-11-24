"""Read-only selection rehearsal over the saved Wading Path review. No provider transport."""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Literal

from open_hollywood_api.services.assessment_intake import collect_intakes
from open_hollywood_engine.evaluations import canonical_sha256
from open_hollywood_engine.evaluations.assessment_claim_scope import (
    ClaimScopeDeclaration,
    DeclaredSourceScope,
    MaterialComponent,
    Predicate,
)
from open_hollywood_engine.evaluations.assessment_intake import (
    IntakeChoice,
    IntakeSource,
    compile_intake,
    empty_intake_plan,
)
from open_hollywood_engine.evaluations.assessment_result import _registry, scope_for_batch
from open_hollywood_engine.evaluations.assessment_work_brief import (
    AuthoredWorkBrief,
    preview_work_briefs,
)
from open_hollywood_engine.evaluations.review_evidence import require

from scripts.ordinary_v61_capture import file_hash
from scripts.q011_arrival.scope_rehearsal import pinned
from scripts.q011_arrival.sources import DATA
from scripts.q011_evidence_check.plan import ADDITION

DATABASE = DATA / "wading-path-v61-capture-2026-11-24/output/workspace.db"
DB_SHA = "34f581318d6fee10d1641a1fba76f099382ba1890c7f0632ebc7ba314feba21f"
SOURCE_SHA = "25d6154278a0f7bae6879f560bbd7fc7fe9af525bd3de0ce5b3a4cf2afce3275"
INVOCATION = "5a6f3522-ece2-477c-b0a9-c55665dbc32e"
GOLD = DATA / "wading-path-v61-results-2026-11-24/gold.json"
GOLD_SHA = "ce5d97d7565455852b452a1792a10cc40acd5ae4cf115d552d43e254fe742956"
PREVIEWS: tuple[tuple[str, Literal["B", "E"]], ...] = (
    ("Q010", "B"),
    ("Q010", "E"),
    ("Q008", "B"),
    ("Q011", "E"),
    ("Q011", "B"),
)


@dataclass(frozen=True)
class FieldBrief:
    pointer: str
    predicates: tuple[Predicate, ...]
    components: tuple[str, ...]
    question: str
    obligation: str
    plan_refs: tuple[str, ...]
    position: str = ""


# Neutral operator nominations. Selection has no dependency on the score key.
FIELDS = {
    "Q010": FieldBrief(
        "/saved_native_audit/check/achieved_state",
        ("observed_event",),
        (
            "Both characters' entry into the service plenum.",
            "Both characters' standing position relative to the master breaker panel housing.",
        ),
        "What does the draft establish about each part of the achieved state?",
        "Locate draft evidence for the pair's entry and claimed standing position.",
        (),
        "Elias and Maya standing before the master breaker panel housing",
    ),
    "Q011": FieldBrief(
        "/saved_native_audit/check/current_endpoint_comparison",
        ("endpoint_compliance",),
        (
            "Fulfillment of reaching the breaker panel housing.",
            "Fulfillment of standing before the final barrier.",
        ),
        "Does the ending fulfill the assigned outcome and exit state?",
        "Locate both assignments and the draft evidence for fulfillment of each.",
        ("E0258", "E0254"),
        "Elias and Maya having reached the housing and standing before the final barrier",
    ),
    "Q008": FieldBrief(
        "/saved_native_audit/assignment_checks/outcome/assessment",
        ("assignment_obligation", "observed_event"),
        (
            "The outcome the plan requires.",
            "The ending's account of entry into the plenum.",
            "The ending's account of arrival at the passage end where the housing stands.",
        ),
        "What outcome was assigned, and what actions does the draft narrate in its conclusion?",
        "Locate the assigned outcome and check the account of both actions through the last line.",
        ("E0258",),
    ),
}


def load_source() -> IntakeSource:
    # Keep SQLite, including any auxiliary files opened by its reader, off the archive.
    with TemporaryDirectory() as tmp:
        copy = Path(tmp) / "workspace.db"
        shutil.copyfile(DATABASE, copy)
        require(file_hash(copy) == DB_SHA, "wading_database_drift")
        (entry,) = collect_intakes("saved_review", copy, (INVOCATION,)).entries
    require(entry.reason == "compatible" and entry.source is not None, "wading_intake")
    assert entry.source is not None
    return entry.source


def select(source: IntakeSource, unit: str, arm: Literal["B", "E"]) -> dict[str, Any]:
    require(source.review_id == INVOCATION and source.source_sha256 == SOURCE_SHA, "wading_source")
    require(unit in FIELDS, "wading_field")
    spec = FIELDS[unit]
    require(arm == "B" or (arm == "E" and bool(spec.position)), "wading_arm")
    ctx = source.inventory_work.context
    (field,) = (f for f in ctx.report_fields if f.field_id == unit)
    (stmt,) = (s for s in ctx.statements if s.unit_id == unit)
    require(
        field.pointer == spec.pointer
        and (stmt.field_id, stmt.start, stmt.end, stmt.quote)
        == (unit, 0, len(field.text), field.text),
        "wading_whole_field",
    )
    scopes: tuple[DeclaredSourceScope, ...] = (
        DeclaredSourceScope(role="draft", coverage="complete_fields", evidence_refs=("E1420",)),
    )
    authority = "Use the complete reviewed scene-four draft."
    if spec.plan_refs:
        scopes += (DeclaredSourceScope(role="assignment", evidence_refs=spec.plan_refs),)
        authority = "Use the scene-four plan for assignments and the full draft for what occurs."
    brief = AuthoredWorkBrief(
        unit_id=unit,
        question=spec.question,
        temporal_scope="Scene four through its final narrated instant.",
        source_authority=authority,
        evidence_obligation=spec.obligation,
    )
    declaration = ClaimScopeDeclaration(
        statement=stmt,
        field_pointer=field.pointer,
        claim_predicates=spec.predicates,
        evidence_predicates=spec.predicates,
        whole_claim_reviewed=True,
        observation_basis="positive_depiction",
        source_scopes=scopes,
        material_components=tuple(
            MaterialComponent(description=c, addressed_by_evidence_contract=True)
            for c in spec.components
        ),
        evidence_requirement=spec.obligation,
    )
    choice = IntakeChoice(
        field_id=unit,
        reading="factual",
        interpretation=spec.question,
        declaration=declaration,
        brief=brief,
    )
    plan = empty_intake_plan(source).model_copy(
        update={
            "authored_by": "Local Wading Path selection rehearsal",
            "choices": (choice,),
            "maximum_units": 1,
        }
    )
    intake = compile_intake(source, plan)
    work, declarations, briefs = intake.pending_work, intake.declarations, intake.briefs
    require(work is not None and declarations is not None and briefs is not None, "wading_no_work")
    assert work is not None and declarations is not None and briefs is not None
    (batch,) = work.batches
    (finding,) = (f for f in intake.findings if f.status != "not_selected")
    require(
        batch.unit_ids == (unit,)
        and finding.field == field
        and finding.status == "pending_assessment"
        and work.context == ctx.model_copy(update={"statements": (stmt,)}),
        "wading_active_scope",
    )
    scope = scope_for_batch(work, batch.batch_id, canonical_sha256(plan.model_dump(mode="json")))
    if arm == "E":
        extra = ADDITION.replace("Elias standing at the threshold", spec.position)
        brief = brief.model_copy(update={"evidence_obligation": spec.obligation + " " + extra})
        briefs = briefs.model_copy(update={"briefs": (brief,)})
    view = preview_work_briefs(work, scope, declarations, briefs)
    (item,), (claim,) = view.units, view.claim_scope_audit.units
    require(
        item.status == "declared_consistent"
        and item.brief == brief
        and claim.declaration == declaration
        and claim.full_report_field == field.text
        and claim.statement == stmt,
        "wading_preview",
    )
    return dict(
        unit=unit,
        arm=arm,
        pointer=field.pointer,
        text=field.text,
        span=[stmt.start, stmt.end],
        active_units=list(scope.active_unit_ids),
        status=finding.status,
        source_sha256=source.source_sha256,
        work_sha256=work.fingerprint,
        scope=scope.model_dump(mode="json"),
        declaration=declaration.model_dump(mode="json"),
        brief=brief.model_dump(mode="json"),
        source_refs=[r.ref for r in claim.source_locations],
        factual_support=intake.factual_support,
        evidence_adequacy=intake.evidence_adequacy,
        assessment_result=intake.assessment_result,
        completion_receipt=intake.completion_receipt,
        model_input=intake.model_input,
        writer_dispatch_authorized=intake.writer_dispatch_authorized,
    )


def verify_gold(source: IntakeSource, rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Join the sealed scoring key after building the previews. Never pass it to intake."""
    gold = pinned(GOLD, GOLD_SHA)
    binding = gold["binding"]
    ctx = source.inventory_work.context
    (doc,) = (d for d in ctx.documents if d.kind == "scope")
    snap = json.loads(doc.content_json)["snapshot"]
    require(
        binding["invocation"] == source.review_id == INVOCATION
        and binding["critique"] == snap["critique"]["version_id"]
        and binding["critique_sha256"] == snap["critique"]["content_sha256"]
        and binding["draft"] == snap["draft_version_id"]
        and binding["plan"] == snap["plan_version_id"]
        and binding["source_response_sha256"] == snap["invocation"]["response_sha256"]
        and binding["snapshot_sha256"] == canonical_sha256(snap)
        and {v["version"]: v["sha256"] for v in binding["inputs"].values()}
        == {s["version_id"]: s["content_sha256"] for s in snap["sources"]},
        "wading_gold_binding",
    )
    refs = {r.ref: r for r in _registry(source.inventory_work).entries}
    full = refs[gold["draft_complete_ref"]]
    require(
        full.document_version == binding["draft"] and full.field_pointer == "/prose",
        "wading_draft_ref",
    )
    visible = json.loads(snap["messages"][1]["content"])["input_artifacts"]
    for w in gold["draft_witnesses"].values():
        loc = refs[w["registered_ref"]]
        _, _, i, _, _, n, leaf = loc.field_pointer.split("/")
        target = visible[int(i)]
        require(
            target["artifact_version_id"] == w["draft_version"] == binding["draft"]
            and target["content"]["evidence_catalog"][int(n)]["evidence_ref"] == w["catalog_ref"]
            and leaf == "exact_excerpt"
            and loc.quote == full.quote[w["start"] : w["end"]] == w["quote"],
            "wading_witness",
        )
    for key, p in gold["plan_witnesses"].items():
        loc = refs[p["registered_ref"]]
        _, _, i, _, leaf = loc.field_pointer.split("/")
        require(
            visible[int(i)]["artifact_version_id"] == p["version"] == binding["plan"]
            and leaf == key
            and loc.quote == p["text"],
            "wading_plan_ref",
        )
    cases = {c["field_id"]: c for c in gold["claims"]}
    require(
        sorted((r["unit"], r["arm"]) for r in rows) == sorted(PREVIEWS),
        "wading_schedule",
    )
    for row in rows:
        c = cases[row["unit"]]
        if row["arm"] == "B":
            require(
                row["brief"]["evidence_obligation"] == FIELDS[row["unit"]].obligation,
                "wading_baseline_drift",
            )
        require(
            (row["pointer"], row["text"], row["span"])
            == (c["pointer"], c["text"], [c["field_start"], c["field_end"]])
            and row["source_refs"] == [full.ref, *c["plan_refs"]],
            "wading_gold_selection",
        )
    for unit in ("Q010", "Q011"):
        b, e = (next(r for r in rows if (r["unit"], r["arm"]) == (unit, arm)) for arm in ("B", "E"))
        extra = ADDITION.replace("Elias standing at the threshold", FIELDS[unit].position)
        require(
            e
            == b
            | {
                "arm": "E",
                "brief": b["brief"]
                | {"evidence_obligation": b["brief"]["evidence_obligation"] + " " + extra},
            },
            "wading_arm_drift",
        )
    return dict(
        gold_sha256=GOLD_SHA,
        binding=binding,
        judgment_scoring=gold["judgment_scoring"],
        evidence_scoring=gold["evidence_scoring"],
        evidence_witnesses_checked=len(gold["draft_witnesses"]),
        criteria={
            u: {"label": c["label"], "evidence_pass_requires": c["evidence_pass_requires"]}
            for u, c in cases.items()
        },
    )


def rehearse() -> dict[str, Any]:
    source = load_source()
    rows = [select(source, unit, arm) for unit, arm in PREVIEWS]
    return dict(selections=rows, operator_verification=verify_gold(source, rows), live_calls=0)


if __name__ == "__main__":
    print(json.dumps(rehearse(), ensure_ascii=True, indent=2))
