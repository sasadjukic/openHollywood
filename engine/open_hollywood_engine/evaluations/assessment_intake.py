"""Whole-field ordinary-review intake. Authored scope, no inference or edit authority."""

from __future__ import annotations

import json
import re
from typing import Literal, Self

from pydantic import Field, JsonValue, model_validator

from open_hollywood_engine.evaluations.assessment_claim_scope import (
    ClaimScopeDeclaration,
    ClaimScopeDeclarations,
    Text,
)
from open_hollywood_engine.evaluations.assessment_result import (
    EvidenceLocation,
    EvidenceRegistry,
    scope_for_batch,
)
from open_hollywood_engine.evaluations.assessment_work import (
    AssessmentContext,
    AssessmentWork,
    ContextDocument,
    Name,
    ReportField,
    SelectedStatement,
    partition_work,
)
from open_hollywood_engine.evaluations.assessment_work_brief import (
    AssessmentWorkBriefs,
    AuthoredWorkBrief,
    preview_work_briefs,
)
from open_hollywood_engine.evaluations.contracts import canonical_sha256
from open_hollywood_engine.evaluations.review_evidence import (
    Digest,
    JsonObject,
    Record,
    SavedMessage,
    require,
    strict_object,
    text_hash,
)

EXPLANATORY_KEYS = frozenset(
    {
        "assessment",
        "achieved_state",
        "current_endpoint_comparison",
        "next_scene_comparison",
        "rationale",
        "summary",
        "description",
        "evidence",
        "suggestion",
        "recommendation",
        "recommended_resolution",
        "explanation",
        "reason",
    }
)
Reading = Literal["factual", "literal_procedure", "editorial_effect", "mixed", "ambiguous"]


class IntakeSource(Record):
    contract: Literal["ordinary-review-intake-source-1"] = "ordinary-review-intake-source-1"
    origin: Literal["saved_review", "diagnostic_probe"]
    review_id: Name
    source_sha256: Digest
    report_origin: Literal["raw_model", "saved_normalized_and_audit"]
    # All fields are selected here only to establish inventory identities, not pending work.
    inventory_work: AssessmentWork
    model_input: Literal[False] = False
    writer_dispatch_authorized: Literal[False] = False

    @model_validator(mode="after")
    def check_binding(self) -> Self:
        context = self.inventory_work.context
        require(context.origin_sha256 == self.source_sha256, "intake_origin_binding")
        expected = {
            "visible-request": "source",
            "catalog-complete-current-draft": "source",
            "whole-review": "report",
            "evidence-registry": "registry",
            "operator-provenance-not-visible-authority": "scope",
        }
        require(
            {d.identity: d.kind for d in context.documents} == expected, "intake_document_roles"
        )
        provenance = next(d for d in context.documents if d.kind == "scope")
        require(
            canonical_sha256(strict_object(provenance.content_json)) == self.source_sha256,
            "intake_provenance_binding",
        )
        require(
            self.report_origin
            == ("raw_model" if self.origin == "diagnostic_probe" else "saved_normalized_and_audit"),
            "intake_report_origin",
        )
        return self


class IntakeChoice(Record):
    field_id: Name
    reading: Reading
    interpretation: Text
    hold_reason: Text | None = None
    declaration: ClaimScopeDeclaration | None = None
    brief: AuthoredWorkBrief | None = None


class IntakePlan(Record):
    contract: Literal["ordinary-review-intake-plan-1"] = "ordinary-review-intake-plan-1"
    source_sha256: Digest
    inventory_work_sha256: Digest
    authored_by: Text
    choices: tuple[IntakeChoice, ...] = Field(default=(), max_length=128)
    maximum_units: int = Field(default=6, ge=1, le=12)
    model_input: Literal[False] = False
    writer_dispatch_authorized: Literal[False] = False


class IntakeFinding(Record):
    field: ReportField
    choice: IntakeChoice | None
    status: Literal["pending_assessment", "hold", "not_selected"]
    issues: tuple[str, ...] = ()


class IntakeResult(Record):
    contract: Literal["ordinary-review-intake-1"] = "ordinary-review-intake-1"
    source: IntakeSource
    plan: IntakePlan
    findings: tuple[IntakeFinding, ...]
    pending_work: AssessmentWork | None
    declarations: ClaimScopeDeclarations | None
    briefs: AssessmentWorkBriefs | None
    assessment_result: None = None
    completion_receipt: None = None
    semantic_interpretation_verified: Literal[False] = False
    brief_neutrality_verified: Literal[False] = False
    factual_support: Literal["unassessed"] = "unassessed"
    evidence_adequacy: Literal["unassessed"] = "unassessed"
    editorial_effect: Literal["unassessed"] = "unassessed"
    edit_necessity: Literal["unassessed"] = "unassessed"
    craft: Literal["unassessed"] = "unassessed"
    model_input: Literal[False] = False
    writer_dispatch_authorized: Literal[False] = False


def string_fields(value: JsonValue, pointer: str = "") -> tuple[tuple[str, str], ...]:
    """Deterministic literal field inventory, not a claim extractor or classifier."""
    if isinstance(value, str):
        return ((pointer, value),)
    if isinstance(value, dict):
        return tuple(
            row
            for key in sorted(value)
            for row in string_fields(
                value[key], pointer + "/" + key.replace("~", "~0").replace("/", "~1")
            )
        )
    if isinstance(value, list):
        return tuple(
            row for i, item in enumerate(value) for row in string_fields(item, pointer + f"/{i}")
        )
    return ()


def _document(
    identity: str,
    kind: Literal["source", "report", "registry", "scope"],
    value: JsonObject,
    version: str = "saved",
) -> ContextDocument:
    text = json.dumps(value, ensure_ascii=False, sort_keys=True)
    return ContextDocument(
        identity=identity,
        version=version,
        kind=kind,
        content_json=text,
        content_sha256=text_hash(text),
    )


def build_intake_source(
    *,
    origin: Literal["saved_review", "diagnostic_probe"],
    review_id: str,
    report_origin: Literal["raw_model", "saved_normalized_and_audit"],
    messages: tuple[SavedMessage, ...],
    current_prose: str,
    current_version: str,
    report: JsonObject,
    operator_provenance: JsonObject,
) -> IntakeSource:
    """Adapter must authenticate lineage and complete catalog visibility before calling."""
    require(tuple(m.role for m in messages) == ("system", "user"), "intake_message_contract")
    visible = strict_object(messages[1].content)
    fields = tuple(
        ReportField(field_id=f"Q{i:03d}", pointer=pointer, text=text)
        for i, (pointer, text) in enumerate(
            (
                (pointer, text)
                for pointer, text in string_fields(report)
                if text
                and (
                    pointer.rsplit("/", 1)[-1] in EXPLANATORY_KEYS
                    or "/strengths/" in pointer
                    or "/evidence/" in pointer
                )
            ),
            1,
        )
    )
    require(0 < len(fields) <= 256, "intake_field_limit")
    source_hash = canonical_sha256(operator_provenance)
    documents = [
        _document("visible-request", "source", visible),
        _document(
            "catalog-complete-current-draft", "source", {"prose": current_prose}, current_version
        ),
    ]
    registry: list[EvidenceLocation] = []
    for doc in documents:
        for pointer, text in string_fields(strict_object(doc.content_json)):
            if text:
                registry.append(
                    EvidenceLocation(
                        ref=f"E{len(registry) + 1:04d}",
                        document_id=doc.identity,
                        document_version=doc.version,
                        document_sha256=doc.content_sha256,
                        field_pointer=pointer,
                        field_sha256=text_hash(text),
                        start=0,
                        end=len(text),
                        quote=text,
                    )
                )
    documents.extend(
        (
            _document("whole-review", "report", report),
            _document(
                "evidence-registry",
                "registry",
                EvidenceRegistry(entries=tuple(registry)).model_dump(mode="json"),
            ),
            _document("operator-provenance-not-visible-authority", "scope", operator_provenance),
        )
    )
    context = AssessmentContext(
        provenance="diagnostic_capture",
        origin_sha256=source_hash,
        documents=tuple(documents),
        report_fields=fields,
        messages=messages,
        statements=tuple(
            SelectedStatement(
                unit_id=f.field_id, field_id=f.field_id, start=0, end=len(f.text), quote=f.text
            )
            for f in fields
        ),
    )
    return IntakeSource(
        origin=origin,
        review_id=review_id,
        source_sha256=source_hash,
        report_origin=report_origin,
        inventory_work=partition_work(context, 12),
    )


def empty_intake_plan(source: IntakeSource) -> IntakePlan:
    return IntakePlan(
        source_sha256=source.source_sha256,
        inventory_work_sha256=source.inventory_work.fingerprint,
        authored_by="Unassigned; replace before declaring any choices",
    )


def _sidecars(
    work: AssessmentWork, plan: IntakePlan, choices: tuple[IntakeChoice, ...]
) -> tuple[ClaimScopeDeclarations, AssessmentWorkBriefs]:
    declarations = ClaimScopeDeclarations(
        work_sha256=work.fingerprint,
        authored_by=plan.authored_by,
        declarations=tuple(c.declaration for c in choices if c.declaration is not None),
    )
    briefs = AssessmentWorkBriefs(
        work_sha256=work.fingerprint,
        declarations_sha256=canonical_sha256(declarations.model_dump(mode="json")),
        authored_by=plan.authored_by,
        briefs=tuple(c.brief for c in choices if c.brief is not None),
    )
    return declarations, briefs


def compile_intake(source: IntakeSource, plan: IntakePlan) -> IntakeResult:
    source = IntakeSource.model_validate_json(source.model_dump_json())
    plan = IntakePlan.model_validate_json(plan.model_dump_json())
    original = source.inventory_work
    require(
        plan.source_sha256 == source.source_sha256
        and plan.inventory_work_sha256 == original.fingerprint,
        "intake_source_mismatch",
    )
    choices = {c.field_id: c for c in plan.choices}
    fields = {f.field_id: f for f in original.context.report_fields}
    require(len(choices) == len(plan.choices) and set(choices) <= set(fields), "intake_selection")
    require(not original.context.declared_links, "intake_unsupported_relations")
    statements = {s.field_id: s for s in original.context.statements}
    require(set(statements) == set(fields), "intake_inventory_coverage")
    for field in fields.values():
        s = statements[field.field_id]
        require(
            (s.unit_id, s.start, s.end, s.quote)
            == (field.field_id, 0, len(field.text), field.text),
            "intake_requires_whole_fields",
        )
    for declared_choice in plan.choices:
        if declared_choice.declaration is not None:
            require(
                declared_choice.declaration.statement == statements[declared_choice.field_id],
                "intake_whole_selection_mismatch",
            )
        if declared_choice.brief is not None:
            require(
                declared_choice.brief.unit_id == declared_choice.field_id,
                "intake_brief_unit_mismatch",
            )
    declarations, briefs = _sidecars(original, plan, plan.choices)
    # A local identity for checking sidecars only, explicitly not an inference request.
    local_identity = canonical_sha256({"operator_intake_plan": plan.model_dump(mode="json")})
    issues: dict[str, tuple[str, ...]] = {}
    for batch in original.batches:
        scope = scope_for_batch(original, batch.batch_id, local_identity)
        preview = preview_work_briefs(original, scope, declarations, briefs)
        issues.update({u.unit_id: u.issues for u in preview.units})
    findings = []
    for field in original.context.report_fields:
        choice = choices.get(field.field_id)
        if choice is None:
            findings.append(IntakeFinding(field=field, choice=None, status="not_selected"))
            continue
        reasons = list(issues[field.field_id])
        if choice.hold_reason:
            reasons.append("authored_hold")
        if choice.reading in ("editorial_effect", "mixed", "ambiguous"):
            reasons.append("nonfactual_or_ambiguous_reading")
        predicates = set(choice.declaration.claim_predicates) if choice.declaration else set()
        if choice.reading == "literal_procedure" and "observed_procedure" not in predicates:
            reasons.append("literal_procedure_requires_procedure_predicate")
        if choice.reading == "factual" and "observed_procedure" in predicates:
            reasons.append("procedure_requires_explicit_reading")
        findings.append(
            IntakeFinding(
                field=field,
                choice=choice,
                status="hold" if reasons else "pending_assessment",
                issues=tuple(reasons),
            )
        )
    admitted = {f.field.field_id for f in findings if f.status == "pending_assessment"}
    pending = None
    pending_declarations = None
    pending_briefs = None
    if admitted:
        pending = partition_work(
            original.context.model_copy(
                update={
                    "statements": tuple(
                        s for s in original.context.statements if s.unit_id in admitted
                    )
                }
            ),
            plan.maximum_units,
        )
        pending_declarations, pending_briefs = _sidecars(
            pending, plan, tuple(c for c in plan.choices if c.field_id in admitted)
        )
        for batch in pending.batches:
            preview = preview_work_briefs(
                pending,
                scope_for_batch(pending, batch.batch_id, local_identity),
                pending_declarations,
                pending_briefs,
            )
            require(
                all(u.status == "declared_consistent" for u in preview.units),
                "intake_pending_scope",
            )
    return IntakeResult(
        source=source,
        plan=plan,
        findings=tuple(findings),
        pending_work=pending,
        declarations=pending_declarations,
        briefs=pending_briefs,
    )


def render_intake(result: IntakeResult) -> str:
    """Recompute all dispositions; embedded Markdown/HTML remains literal data."""
    expected = compile_intake(result.source, result.plan)
    require(result == expected, "intake_result_mismatch")
    payload = json.dumps(
        expected.model_dump(mode="json"), ensure_ascii=False, indent=2, sort_keys=True
    )
    fence = "`" * max(3, 1 + max((len(m[0]) for m in re.finditer(r"`+", payload)), default=0))
    return (
        "# Read-only ordinary-review intake\n\n"
        "Explicit authored readings; whole fields and full context retained.\n"
        "Pending work is not a model request or completed assessment.\n"
        "Procedure, editorial effect and ambiguity remain distinct. Semantic support,\n"
        "evidence adequacy, edit necessity and craft are unassessed; no writer permission.\n\n"
        + fence
        + "json\n"
        + payload
        + "\n"
        + fence
        + "\n"
    )
