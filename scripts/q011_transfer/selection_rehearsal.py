"""Rehearse four explicit field selections using the saved-review intake and read-only preview."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

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
    build_intake_source,
    compile_intake,
    empty_intake_plan,
)
from open_hollywood_engine.evaluations.assessment_result import scope_for_batch
from open_hollywood_engine.evaluations.assessment_work import ReportField, SelectedStatement
from open_hollywood_engine.evaluations.assessment_work_brief import (
    AuthoredWorkBrief,
    preview_work_briefs,
)
from open_hollywood_engine.evaluations.review_evidence import (
    ReviewExportEntry,
    project_review,
    require,
    string_value,
)

from scripts.q011_arrival.scope_rehearsal import pinned
from scripts.q011_arrival.sources import REPO
from scripts.q011_evidence_check.plan import ADDITION

from . import scope_audit as audit

# Operator nominations carry both review and field identity. Q numbers are local to a review.
FIELDS = {
    "Q010": ("S01", "achieved_state", "E"),
    "Q011": ("S01", "current_endpoint_comparison", "E"),
    "Q012": ("S01", "next_scene_comparison", "B"),
    "Q016": ("S02", "current_endpoint_comparison", "hold"),
}


@dataclass(frozen=True)
class PositionTarget:
    literal: str
    proposition: str
    landmark: str


POSITION = {
    "Q010": PositionTarget(
        "is entering the threshold of the monolith",
        "entering the threshold of the monolith",
        "the threshold of the monolith",
    ),
    "Q011": PositionTarget("stands at the threshold", "standing at the threshold", "the threshold"),
}
CURRENT = "Scene one through its final narrated instant."
READER_HOLD = "The claimed obsession with proving a fake is a reading of Elara's motivation."


@dataclass(frozen=True)
class Review:
    case: str
    source: IntakeSource
    ruling: dict[str, Any]
    versions: dict[str, str]
    blueprint_version: str


def load_reviews() -> dict[str, Review]:
    members = pinned(audit.ROOT / "audit-seal.json", audit.SEAL)
    decisions = pinned(audit.ROOT / "scope-decisions.json", members["scope-decisions.json"])
    protocol = pinned(audit.ROOT / "protocol.json", audit.PROTOCOL)
    reviews = {}
    for case, row in zip(("S01", "S02"), protocol["reviews"][:2], strict=True):
        packet = audit.registered(row)
        require(
            packet == pinned(audit.ROOT / f"packets/{case}.json", members[f"packets/{case}.json"]),
            "selection_source_drift",
        )
        ruling = decisions[case]
        audit.check_decisions(packet, ruling)
        (raw_entry,) = pinned(REPO / row["source"], row["source_sha256"])["entries"]
        entry = ReviewExportEntry.model_validate_json(json.dumps(raw_entry))
        snap = entry.snapshot
        require(entry.reason == "compatible" and snap is not None, "selection_incompatible")
        assert snap is not None and snap.critique.content is not None
        require(project_review(snap) == entry.evidence, "selection_export_drift")
        (draft,) = (s for s in snap.sources if s.version_id == snap.draft_version_id)
        assert draft.content is not None
        source = build_intake_source(
            origin="saved_review",
            review_id=entry.invocation_id,
            report_origin="saved_normalized_and_audit",
            messages=snap.messages,
            current_version=draft.version_id,
            current_prose=string_value(draft.content["prose"]),
            report={
                "saved_critique": snap.critique.content,
                "saved_native_audit": snap.native_audit,
            },
            operator_provenance=entry.model_dump(mode="json"),
        )
        (blueprint,) = (s for s in snap.sources if s.artifact_kind == "story_blueprint")
        visible = json.loads(snap.messages[1].content)
        boundary = visible["scene_boundary"]
        next_plan = boundary["next_scene"]
        assert blueprint.content is not None
        scene_plans = blueprint.content["scene_plans"]
        assert isinstance(scene_plans, list)
        (next_scene,) = (
            s for s in scene_plans if isinstance(s, dict) and s["id"] == next_plan["scene_id"]
        )
        require(
            boundary["current_plan_version_id"] == packet["plan"]["version"]
            and next_plan == packet["native"]["next_scene"]
            and next_plan["blueprint_version_id"] == blueprint.version_id
            and all(next_plan[k] == next_scene[k] for k in ("turning_point", "outcome")),
            "selection_boundary_authority",
        )
        versions = {k: packet[k]["version"] for k in ("review", "draft", "plan")}
        reviews[case] = Review(case, source, ruling, versions, blueprint.version_id)
    return reviews


def choice_for(field: ReportField, stmt: SelectedStatement) -> IntakeChoice:
    unit = field.field_id
    if unit == "Q016":
        return IntakeChoice(
            field_id=unit,
            reading="mixed",
            interpretation=READER_HOLD,
            hold_reason="Reader interpretation of the implied motive is required.",
        )
    draft = DeclaredSourceScope(role="draft", coverage="complete_fields", evidence_refs=("E0883",))
    scopes: tuple[DeclaredSourceScope, ...] = (draft,)
    predicates: tuple[Predicate, ...]
    if unit == "Q010":
        components = (
            "Elias moving past the circle of shoes.",
            "Elias entering the threshold of the monolith at the scene cut.",
        )
        predicates = ("observed_event",)
        authority = "Use the complete reviewed draft to assess both actions."
        question = (
            "What does the scene establish about moving past the shoes and entering the threshold?"
        )
        obligation = "Locate the evidence for each action."
    elif unit == "Q011":
        components = (
            "Fulfillment of the assigned outcome of being drawn to the entrance.",
            "Fulfillment of the exit state that Elias stands at the threshold.",
        )
        predicates = ("endpoint_compliance",)
        scopes += (DeclaredSourceScope(role="assignment", evidence_refs=("E0233", "E0229")),)
        authority = (
            "Use the scene plan for both assignments and the reviewed draft for fulfillment."
        )
        question = (
            "Does the achieved state fulfill both the outcome and the exit state in the plan?"
        )
        obligation = "Locate both assignments and the relevant draft evidence for each."
    else:
        require(unit == "Q012", "selection_unregistered")
        components = (
            "Where the draft stops in its narration of the threshold and building.",
            "Whether the draft introduces Julian Vane's voice reserved for scene two.",
        )
        predicates = ("endpoint_compliance",)
        scopes += (
            DeclaredSourceScope(role="assignment", evidence_refs=("E0233", "E0229", "E0865")),
        )
        authority = (
            "Use the complete draft for narrative coverage, the current plan for the endpoint, "
            "and the Blueprint's next-scene turning point for the reserved voice."
        )
        question = (
            "Where does the narration stop, and does the draft advance into the building "
            "or introduce the voice reserved for scene two?"
        )
        obligation = (
            "Check the complete draft for both claimed boundaries and locate the next-scene "
            "assignment."
        )
    if unit in POSITION:
        target = POSITION[unit]
        require(field.text.count(target.literal) == 1, "selection_position_predicate")
        obligation += " " + ADDITION.replace("standing at the threshold", target.proposition)
    declaration = ClaimScopeDeclaration(
        statement=stmt,
        field_pointer=field.pointer,
        claim_predicates=predicates,
        evidence_predicates=predicates,
        source_scopes=scopes,
        material_components=tuple(
            MaterialComponent(description=c, addressed_by_evidence_contract=True)
            for c in components
        ),
        evidence_requirement=obligation,
        whole_claim_reviewed=True,
        observation_basis="absence_in_complete_scope" if unit == "Q012" else "positive_depiction",
    )
    return IntakeChoice(
        field_id=unit,
        reading="factual",
        interpretation=question,
        declaration=declaration,
        brief=AuthoredWorkBrief(
            unit_id=unit,
            question=question,
            evidence_obligation=obligation,
            source_authority=authority,
            temporal_scope=CURRENT,
        ),
    )


def select(review: Review, unit: str) -> dict[str, Any]:
    require(unit in FIELDS, "selection_unregistered")
    case, field_name, route = FIELDS[unit]
    require(
        review.case == case and review.versions == review.ruling["versions"], "selection_versions"
    )
    pointer = "/saved_native_audit/check/" + field_name
    ruling = review.ruling["fields"]["/native/check/" + field_name]
    source = review.source
    ctx = source.inventory_work.context
    (provenance,) = (d for d in ctx.documents if d.kind == "scope")
    snap = json.loads(provenance.content_json)["snapshot"]
    require(
        snap["invocation"]["invocation_id"] == source.review_id
        and review.versions
        == dict(
            review=snap["critique"]["version_id"],
            draft=snap["draft_version_id"],
            plan=snap["plan_version_id"],
        )
        and review.blueprint_version == snap["native_audit"]["next_scene"]["blueprint_version_id"],
        "selection_source_versions",
    )
    (field,) = (f for f in ctx.report_fields if f.field_id == unit)
    (stmt,) = (s for s in ctx.statements if s.unit_id == unit)
    require(
        field.pointer == pointer
        and ruling["route"] == route
        and field.text == ruling["text"]
        and (stmt.field_id, stmt.start, stmt.end, stmt.quote)
        == (unit, 0, len(field.text), field.text),
        "selection_whole_field",
    )
    choice = choice_for(field, stmt)
    plan = empty_intake_plan(source).model_copy(
        update={
            "authored_by": "Local operator field-selection rehearsal",
            "choices": (choice,),
            "maximum_units": 1,
        }
    )
    intake = compile_intake(source, plan)
    (finding,) = (f for f in intake.findings if f.status != "not_selected")
    require(finding.field == field and finding.choice == choice, "selection_active_field")
    result: dict[str, Any] = dict(
        review_invocation=source.review_id,
        versions=review.versions,
        blueprint_version=review.blueprint_version,
        source_sha256=source.source_sha256,
        unit=unit,
        pointer=pointer,
        text=field.text,
        route=route,
        status=finding.status,
        factual_support=intake.factual_support,
        model_input=intake.model_input,
        assessment_result=intake.assessment_result,
        completion_receipt=intake.completion_receipt,
        writer_dispatch_authorized=intake.writer_dispatch_authorized,
    )
    if route == "E":
        target = POSITION[unit]
        start = stmt.quote.index(target.literal)
        result["position_target"] = dict(
            subject="Elias",
            landmark=target.landmark,
            instant="Scene one's final narrated instant.",
            literal=target.literal,
            start=start,
            end=start + len(target.literal),
        )
    work, briefs, decl = intake.pending_work, intake.briefs, intake.declarations
    if route == "hold":
        require(
            finding.status == "hold"
            and "authored_hold" in finding.issues
            and work is None
            and briefs is None
            and decl is None,
            "selection_hold",
        )
        return dict(**result, active_units=[], brief=None, hold_reason=choice.hold_reason)
    require(
        finding.status == "pending_assessment"
        and work is not None
        and decl is not None
        and briefs is not None,
        "selection_missing_work",
    )
    assert work is not None and decl is not None and briefs is not None
    (batch,) = work.batches
    require(
        batch.unit_ids == (unit,)
        and work.context.documents == ctx.documents
        and work.context.messages == ctx.messages,
        "selection_context",
    )
    scope = scope_for_batch(work, batch.batch_id, canonical_sha256(plan.model_dump(mode="json")))
    view = preview_work_briefs(work, scope, decl, briefs)
    (item,) = view.units
    (claim,) = view.claim_scope_audit.units
    require(
        item.status == "declared_consistent"
        and item.brief == choice.brief
        and claim.statement == stmt
        and claim.full_report_field == field.text
        and claim.field_pointer == pointer
        and claim.declaration == choice.declaration,
        "selection_preview_drift",
    )
    assert item.brief is not None and claim.declaration is not None
    return dict(
        **result,
        active_units=list(batch.unit_ids),
        work_sha256=work.fingerprint,
        brief=item.brief.model_dump(mode="json"),
        components=[c.description for c in claim.declaration.material_components],
        observation_basis=claim.declaration.observation_basis,
        evidence_locations=[
            dict(
                ref=e.ref,
                document=e.document_id,
                document_version=e.document_version,
                pointer=e.field_pointer,
                field_sha256=e.field_sha256,
            )
            for e in claim.source_locations
        ],
    )


def rehearse() -> dict[str, Any]:
    reviews = load_reviews()
    return dict(
        audit_sha256=audit.SEAL,
        live_calls=0,
        selections=[select(reviews[case], unit) for unit, (case, _, _) in FIELDS.items()],
    )


if __name__ == "__main__":
    print(json.dumps(rehearse(), indent=2))
