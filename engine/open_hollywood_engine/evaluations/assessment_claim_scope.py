"""Authored claim-scope declarations and literal audits; no inference or edit authority."""

from __future__ import annotations

import json
import re
from typing import Annotated, Literal

from pydantic import Field, JsonValue

from open_hollywood_engine.evaluations.assessment_result import (
    AssessmentScope,
    EvidenceLocation,
    EvidenceRegistry,
    bind_assessment_result,
    scope_for_batch,
)
from open_hollywood_engine.evaluations.assessment_work import (
    AssessmentReceipt,
    AssessmentWork,
    Name,
    SelectedStatement,
)
from open_hollywood_engine.evaluations.review_evidence import (
    Digest,
    Record,
    require,
    strict_object,
)

Text = Annotated[str, Field(min_length=1, max_length=100_000, pattern=r"\S")]
Predicate = Literal[
    "assignment_obligation",
    "observed_choice",
    "observed_procedure",
    "observed_event",
    "observed_means_relation",
    "endpoint_compliance",
    "speaker_attribution",
    "plan_content",
    "unavailable_document_content",
    "editorial_effect",
]
SourceRole = Literal["assignment", "draft", "definition", "plan", "availability"]


class MaterialComponent(Record):
    description: Text
    addressed_by_evidence_contract: bool


class DeclaredSourceScope(Record):
    """The role is authored, not inferred from a document name or citation location."""

    role: SourceRole
    evidence_refs: tuple[Name, ...] = ()
    coverage: Literal["located_sections", "complete_fields"] = "located_sections"


class ClaimScopeDeclaration(Record):
    statement: SelectedStatement
    field_pointer: str = Field(pattern=r"^/")
    claim_predicates: tuple[Predicate, ...] = ()
    evidence_predicates: tuple[Predicate, ...] = ()
    material_components: tuple[MaterialComponent, ...] = ()
    unresolved_qualifiers: tuple[Text, ...] = ()
    source_scopes: tuple[DeclaredSourceScope, ...] = ()
    evidence_requirement: Text
    whole_claim_reviewed: bool
    observation_basis: Literal[
        "positive_depiction",
        "explicit_nonperformance",
        "absence_in_complete_scope",
        "unavailable_scope",
        "not_applicable",
    ]


class ClaimScopeDeclarations(Record):
    contract: Literal["assessment-claim-declarations-1"] = "assessment-claim-declarations-1"
    work_sha256: Digest
    authored_by: Text
    # Missing declarations are retained as audit findings, not silently filled in.
    declarations: tuple[ClaimScopeDeclaration, ...] = ()
    model_input: Literal[False] = False
    semantic_interpretation_verified: Literal[False] = False
    writer_dispatch_authorized: Literal[False] = False


class ClaimScopeFinding(Record):
    statement: SelectedStatement
    full_report_field: Text
    field_pointer: str
    declaration: ClaimScopeDeclaration | None
    source_locations: tuple[EvidenceLocation, ...]
    issues: tuple[str, ...]
    status: Literal["declared_consistent", "needs_scope_review"]


class ClaimScopeAudit(Record):
    contract: Literal["assessment-claim-audit-1"] = "assessment-claim-audit-1"
    scope: AssessmentScope
    declarations: ClaimScopeDeclarations
    units: tuple[ClaimScopeFinding, ...]
    source_roles_are_authored: Literal[True] = True
    semantic_interpretation_verified: Literal[False] = False
    evidence_adequacy: Literal["unassessed"] = "unassessed"
    factual_support: Literal["unassessed"] = "unassessed"
    editorial_effect: Literal["unassessed"] = "unassessed"
    edit_necessity: Literal["unassessed"] = "unassessed"
    craft: Literal["unassessed"] = "unassessed"
    whole_relation_credit: Literal[False] = False
    writer_dispatch_authorized: Literal[False] = False


def _complete_fields(work: AssessmentWork, entries: list[EvidenceLocation]) -> bool:
    """Check literal coverage of declared fields, not whether the fields are relevant."""
    documents = {d.identity: strict_object(d.content_json) for d in work.context.documents}
    keys = {(e.document_id, e.field_pointer) for e in entries}
    if not keys:
        return False
    for document_id, pointer in keys:
        # Every pointer was already validated by scope_for_batch's registry check.
        value: JsonValue = documents[document_id]
        for token in pointer[1:].split("/"):
            key = token.replace("~1", "/").replace("~0", "~")
            if isinstance(value, list):
                value = value[int(key)]
            else:
                assert isinstance(value, dict)
                value = value[key]
        assert isinstance(value, str)
        spans = sorted(
            (e.start, e.end)
            for e in entries
            if (e.document_id, e.field_pointer) == (document_id, pointer)
        )
        cursor = 0
        for start, end in spans:
            if value[cursor:start].strip():
                return False
            cursor = max(cursor, end)
        if value[cursor:].strip():
            return False
    return True


def _issues(
    work: AssessmentWork, d: ClaimScopeDeclaration, registry: EvidenceRegistry
) -> list[str]:
    issues = []
    if not d.claim_predicates or not d.evidence_predicates:
        issues.append("missing_predicate_declaration")
    if set(d.claim_predicates) != set(d.evidence_predicates):
        issues.append("claim_evidence_predicate_mismatch")
    if not d.whole_claim_reviewed or not d.material_components:
        issues.append("whole_claim_not_reviewed")
    if d.unresolved_qualifiers or any(
        not c.addressed_by_evidence_contract for c in d.material_components
    ):
        issues.append("unresolved_material_qualifier")
    predicates = set(d.claim_predicates + d.evidence_predicates)
    if "editorial_effect" in predicates:
        issues.append("editorial_effect_requires_separate_assessment")
    required: set[str] = set()
    if predicates & {"assignment_obligation", "endpoint_compliance"}:
        required.add("assignment")
    if predicates & {
        "observed_event",
        "observed_choice",
        "observed_procedure",
        "observed_means_relation",
        "endpoint_compliance",
        "speaker_attribution",
    }:
        required.add("draft")
    if "observed_procedure" in predicates:
        required.add("definition")
    if "plan_content" in predicates:
        required.add("plan")
    roles = {s.role for s in d.source_scopes if s.evidence_refs}
    issues.extend("missing_source_role:" + role for role in sorted(required - roles))
    by_ref = {e.ref: e for e in registry.entries}
    for source in d.source_scopes:
        if source.coverage == "complete_fields" and not _complete_fields(
            work, [by_ref[r] for r in source.evidence_refs]
        ):
            issues.append("incomplete_declared_field_coverage:" + source.role)
    if d.observation_basis == "absence_in_complete_scope" and not any(
        s.role == "draft" and s.evidence_refs and s.coverage == "complete_fields"
        for s in d.source_scopes
    ):
        issues.append("absence_requires_complete_draft_scope")
    if ("unavailable_document_content" in predicates) != (
        d.observation_basis == "unavailable_scope"
    ):
        issues.append("unavailable_scope_mismatch")
    return issues


def audit_claim_scope(
    work: AssessmentWork, scope: AssessmentScope, declarations: ClaimScopeDeclarations
) -> ClaimScopeAudit:
    """Validate identities; expose authored scope conflicts without grading the claim."""
    work = AssessmentWork.model_validate_json(work.model_dump_json())
    scope = AssessmentScope.model_validate_json(scope.model_dump_json())
    declarations = ClaimScopeDeclarations.model_validate_json(declarations.model_dump_json())
    expected = scope_for_batch(work, scope.batch_id, scope.request_sha256)
    require(scope == expected, "active_scope_mismatch")
    require(declarations.work_sha256 == work.fingerprint, "claim_scope_work_mismatch")
    registry = EvidenceRegistry.model_validate_json(
        next(d.content_json for d in work.context.documents if d.kind == "registry")
    )
    entries = {e.ref: e for e in registry.entries}
    statements = {s.unit_id: s for s in work.context.statements}
    fields = {f.field_id: f for f in work.context.report_fields}
    declared = {d.statement.unit_id: d for d in declarations.declarations}
    require(len(declared) == len(declarations.declarations), "duplicate_claim_declaration")
    require(set(declared) <= set(statements), "unknown_claim_declaration")
    # Validate all supplied declarations, including context-only units outside this batch.
    for unit, d in declared.items():
        require(d.statement == statements[unit], "claim_scope_selection_mismatch")
        require(
            d.field_pointer == fields[d.statement.field_id].pointer, "claim_scope_field_mismatch"
        )
        for values in (d.claim_predicates, d.evidence_predicates):
            require(len(values) == len(set(values)), "duplicate_scope_predicate")
        require(
            len({s.role for s in d.source_scopes}) == len(d.source_scopes), "duplicate_source_role"
        )
        for source in d.source_scopes:
            require(
                len(source.evidence_refs) == len(set(source.evidence_refs)), "duplicate_scope_ref"
            )
            require(set(source.evidence_refs) <= set(entries), "unknown_scope_evidence")
    findings = []
    for unit in scope.active_unit_ids:
        statement = statements[unit]
        active_declaration = declared.get(unit)
        issues = (
            _issues(work, active_declaration, registry)
            if active_declaration
            else ["missing_claim_declaration"]
        )
        refs = (
            tuple(
                dict.fromkeys(r for s in active_declaration.source_scopes for r in s.evidence_refs)
            )
            if active_declaration
            else ()
        )
        findings.append(
            ClaimScopeFinding(
                statement=statement,
                full_report_field=fields[statement.field_id].text,
                field_pointer=fields[statement.field_id].pointer,
                declaration=active_declaration,
                source_locations=tuple(entries[r] for r in refs),
                issues=tuple(issues),
                status="needs_scope_review" if issues else "declared_consistent",
            )
        )
    return ClaimScopeAudit(scope=scope, declarations=declarations, units=tuple(findings))


def render_claim_scope(
    work: AssessmentWork,
    scope: AssessmentScope,
    declarations: ClaimScopeDeclarations,
    *,
    receipt: AssessmentReceipt | None = None,
    raw_final: str | None = None,
) -> str:
    """Render full context and recomputed scope, optionally alongside a native bound result."""
    work = AssessmentWork.model_validate_json(work.model_dump_json())
    audit = audit_claim_scope(work, scope, declarations)
    require((receipt is None) == (raw_final is None), "incomplete_result_arguments")
    result = (
        bind_assessment_result(work, audit.scope, receipt, raw_final)
        if receipt is not None and raw_final is not None
        else None
    )
    payload = json.dumps(
        {
            "full_work": work.model_dump(mode="json"),
            "claim_scope_audit": audit.model_dump(mode="json"),
            "bound_result": result.model_dump(mode="json") if result else None,
        },
        ensure_ascii=False,
        sort_keys=True,
        indent=2,
    )
    fence = "`" * max(3, 1 + max((len(m[0]) for m in re.finditer(r"`+", payload)), default=0))
    return (
        "# Read-only claim-scope audit\n\n"
        "Declarations describe intended scope; consistency does not prove semantic correctness.\n"
        "Source roles are authored. Support, evidence adequacy, editorial effect, edit necessity\n"
        "and craft remain unassessed. No whole-relation credit or writer permission.\n\n"
        + fence
        + "json\n"
        + payload
        + "\n"
        + fence
        + "\n"
    )
