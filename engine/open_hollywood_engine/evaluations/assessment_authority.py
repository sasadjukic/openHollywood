"""Read-only historical bindings and authored per-component evidence obligations."""

from __future__ import annotations

import json
import re
from typing import Literal

from pydantic import Field

from open_hollywood_engine.evaluations.assessment_claim_scope import (
    ClaimScopeDeclaration,
    ClaimScopeDeclarations,
    Predicate,
    SourceRole,
    Text,
    required_source_roles,
)
from open_hollywood_engine.evaluations.assessment_result import (
    AssessmentScope,
    EvidenceLocation,
    EvidenceRegistry,
    bind_assessment_result,
)
from open_hollywood_engine.evaluations.assessment_work import (
    AssessmentReceipt,
    AssessmentWork,
    ContextDocument,
    Count,
    Name,
)
from open_hollywood_engine.evaluations.assessment_work_brief import (
    AssessmentWorkBriefs,
    WorkBriefPreview,
    preview_work_briefs,
)
from open_hollywood_engine.evaluations.contracts import canonical_sha256
from open_hollywood_engine.evaluations.review_evidence import (
    Digest,
    Record,
    require,
    strict_object,
    text_hash,
)

Visibility = Literal["shown", "not_shown", "unknown"]


class HistoricalSpan(Record):
    """Exact occurrence in a supplied historical body; not a semantic evidence section."""

    document_id: Name
    document_version: Name
    document_sha256: Digest
    field_pointer: str = Field(pattern=r"^/")
    field_sha256: Digest
    start: Count
    end: Count
    quote: Text


class HistoricalBinding(Record):
    evidence_ref: Name
    historical_span: HistoricalSpan
    # Visibility is an adapter declaration tied to this exact request, not a
    # substring heuristic or a conclusion from finding the old body locally.
    excerpt_visibility: Visibility
    historical_body_visibility: Visibility
    visibility_basis: Text


class ComponentEvidenceObligation(Record):
    """One existing material component, not an application-inferred new claim."""

    component_index: Count
    requirement: Text
    predicates: tuple[Predicate, ...] = Field(min_length=1)
    source_roles: tuple[SourceRole, ...] = Field(min_length=1)
    # Illustrative located evidence, never a whitelist for a model's citations.
    example_refs: tuple[Name, ...] = ()


class ClaimEvidenceObligations(Record):
    unit_id: Name
    obligations: tuple[ComponentEvidenceObligation, ...] = ()


class AssessmentAuthority(Record):
    contract: Literal["assessment-authority-1"] = "assessment-authority-1"
    work_sha256: Digest
    request_sha256: Digest
    declarations_sha256: Digest
    authored_by: Text
    # The adapter must authenticate this external archive provenance. Internal
    # hashes can detect inconsistency but cannot authenticate an invented archive.
    origin_sha256: Digest
    historical_sources: tuple[ContextDocument, ...] = ()
    bindings: tuple[HistoricalBinding, ...] = ()
    claims: tuple[ClaimEvidenceObligations, ...] = ()
    model_input: Literal[False] = False
    writer_dispatch_authorized: Literal[False] = False


class HistoricalBindingFinding(Record):
    binding: HistoricalBinding
    visible_location: EvidenceLocation
    status: Literal["exact_copy", "unverified_missing_source"]
    verified_against_supplied_body: bool
    external_provenance_authenticated: Literal[False] = False
    model_visibility_verified: Literal[False] = False
    event_truth: Literal["unassessed"] = "unassessed"
    historical_violation: Literal["unassessed"] = "unassessed"
    edit_necessity: Literal["unassessed"] = "unassessed"


class ClaimObligationFinding(Record):
    unit_id: Name
    authored: ClaimEvidenceObligations | None
    issues: tuple[str, ...]
    status: Literal["declared_consistent", "needs_scope_review"]


class AssessmentAuthorityPreview(Record):
    contract: Literal["assessment-authority-preview-1"] = "assessment-authority-preview-1"
    work_brief_preview: WorkBriefPreview
    authored_authority: AssessmentAuthority
    historical_bindings: tuple[HistoricalBindingFinding, ...]
    units: tuple[ClaimObligationFinding, ...]
    evidence_examples_are_whitelist: Literal[False] = False
    external_provenance_authenticated: Literal[False] = False
    model_visibility_verified: Literal[False] = False
    semantic_interpretation_verified: Literal[False] = False
    evidence_adequacy: Literal["unassessed"] = "unassessed"
    factual_support: Literal["unassessed"] = "unassessed"
    obligation_existence: Literal["unassessed"] = "unassessed"
    observed_fulfillment: Literal["unassessed"] = "unassessed"
    edit_necessity: Literal["unassessed"] = "unassessed"
    craft: Literal["unassessed"] = "unassessed"
    model_input: Literal[False] = False
    whole_relation_credit: Literal[False] = False
    writer_dispatch_authorized: Literal[False] = False


def _historical_field(document: ContextDocument, span: HistoricalSpan) -> str:
    require(document.kind == "source", "historical_body_not_source")
    require(document.version == span.document_version, "historical_version_mismatch")
    require(document.content_sha256 == span.document_sha256, "historical_body_mismatch")
    require(re.search(r"~(?![01])", span.field_pointer) is None, "historical_pointer_invalid")
    value: object = strict_object(document.content_json)
    for token in span.field_pointer[1:].split("/"):
        key = token.replace("~1", "/").replace("~0", "~")
        if isinstance(value, dict):
            require(key in value, "historical_field_missing")
            value = value[key]
        elif isinstance(value, list):
            require(re.fullmatch(r"0|[1-9][0-9]*", key) is not None, "historical_index_invalid")
            index = int(key)
            require(index < len(value), "historical_field_missing")
            value = value[index]
        else:
            require(False, "historical_pointer_invalid")
    require(isinstance(value, str), "historical_field_not_text")
    assert isinstance(value, str)
    require(text_hash(value) == span.field_sha256, "historical_field_mismatch")
    return value


def _bindings(
    work: AssessmentWork, authority: AssessmentAuthority, entries: dict[str, EvidenceLocation]
) -> tuple[HistoricalBindingFinding, ...]:
    sources = {s.identity: s for s in authority.historical_sources}
    require(len(sources) == len(authority.historical_sources), "duplicate_historical_source")
    require(all(s.kind == "source" for s in sources.values()), "historical_body_not_source")
    # A proof must not replace any existing work document under the same identity.
    context = {d.identity: d for d in work.context.documents}
    for identity, supplied_document in sources.items():
        require(
            identity not in context or context[identity] == supplied_document,
            "historical_identity_conflict",
        )
    refs = [b.evidence_ref for b in authority.bindings]
    require(len(refs) == len(set(refs)), "duplicate_historical_binding")
    require(set(refs) <= set(entries), "unknown_historical_evidence")
    findings = []
    for binding in authority.bindings:
        span = binding.historical_span
        location = entries[binding.evidence_ref]
        require(span.quote == location.quote, "historical_copy_mismatch")
        require(
            0 <= span.start < span.end and span.end - span.start == len(span.quote),
            "historical_offsets_invalid",
        )
        document = sources.get(span.document_id)
        if document is not None:
            field = _historical_field(document, span)
            require(
                span.end <= len(field) and field[span.start : span.end] == span.quote,
                "historical_quote_mismatch",
            )
        findings.append(
            HistoricalBindingFinding(
                binding=binding,
                visible_location=location,
                status="exact_copy" if document is not None else "unverified_missing_source",
                verified_against_supplied_body=document is not None,
            )
        )
    return tuple(findings)


def _obligation_issues(
    declaration: ClaimScopeDeclaration | None,
    authored: ClaimEvidenceObligations | None,
    bindings: dict[str, HistoricalBindingFinding],
) -> list[str]:
    if authored is None:
        return ["missing_claim_evidence_obligations"]
    if declaration is None:
        return ["missing_claim_declaration"]
    issues = []
    covered = {o.component_index for o in authored.obligations}
    for index in range(len(declaration.material_components)):
        if index not in covered:
            issues.append(f"missing_component_obligation:{index}")
    roles = {s.role: set(s.evidence_refs) for s in declaration.source_scopes}
    obligation_predicates = {p for o in authored.obligations for p in o.predicates}
    if obligation_predicates != set(declaration.claim_predicates):
        issues.append("obligation_claim_predicate_mismatch")
    for obligation in authored.obligations:
        for role in sorted(
            required_source_roles(set(obligation.predicates)) - set(obligation.source_roles)
        ):
            issues.append(f"obligation_missing_required_role:{obligation.component_index}:{role}")
        for role in obligation.source_roles:
            if not set(obligation.example_refs) & roles.get(role, set()):
                issues.append(f"obligation_missing_source_role:{obligation.component_index}:{role}")
    # Check all declared historical excerpts, not only the chosen obligation examples.
    for ref in sorted(roles.get("historical_excerpt", set())):
        finding = bindings.get(ref)
        if finding is None or finding.status != "exact_copy":
            issues.append("unverified_historical_excerpt:" + ref)
        if finding is None or finding.binding.excerpt_visibility != "shown":
            issues.append("historical_excerpt_visibility_unresolved:" + ref)
    return issues


def preview_assessment_authority(
    work: AssessmentWork,
    scope: AssessmentScope,
    declarations: ClaimScopeDeclarations,
    briefs: AssessmentWorkBriefs,
    authority: AssessmentAuthority,
) -> AssessmentAuthorityPreview:
    """Recompute copying and declaration checks; do not grade claims or authorize edits."""
    work = AssessmentWork.model_validate_json(work.model_dump_json())
    brief_preview = preview_work_briefs(work, scope, declarations, briefs)
    declarations = brief_preview.claim_scope_audit.declarations
    authority = AssessmentAuthority.model_validate_json(authority.model_dump_json())
    require(authority.work_sha256 == work.fingerprint, "authority_work_mismatch")
    require(
        authority.request_sha256 == brief_preview.claim_scope_audit.scope.request_sha256,
        "authority_request_mismatch",
    )
    require(
        authority.declarations_sha256 == canonical_sha256(declarations.model_dump(mode="json")),
        "authority_declarations_mismatch",
    )
    registry = EvidenceRegistry.model_validate_json(
        next(d.content_json for d in work.context.documents if d.kind == "registry")
    )
    entries = {e.ref: e for e in registry.entries}
    findings = _bindings(work, authority, entries)
    by_ref = {f.binding.evidence_ref: f for f in findings}
    declared = {d.statement.unit_id: d for d in declarations.declarations}
    claims = {c.unit_id: c for c in authority.claims}
    require(len(claims) == len(authority.claims), "duplicate_authority_claim")
    require(set(claims) <= {s.unit_id for s in work.context.statements}, "unknown_authority_claim")
    # Validate every supplied obligation, even when its unit is inactive.
    for unit, claim in claims.items():
        indices = [o.component_index for o in claim.obligations]
        require(len(indices) == len(set(indices)), "duplicate_component_obligation")
        if unit in declared:
            require(
                all(i < len(declared[unit].material_components) for i in indices),
                "unknown_material_component",
            )
        else:
            require(not indices, "obligation_without_declaration")
        for obligation in claim.obligations:
            require(
                len(set(obligation.predicates)) == len(obligation.predicates),
                "duplicate_obligation_predicate",
            )
            require(
                len(set(obligation.source_roles)) == len(obligation.source_roles),
                "duplicate_obligation_role",
            )
            require(
                len(set(obligation.example_refs)) == len(obligation.example_refs),
                "duplicate_obligation_ref",
            )
            require(set(obligation.example_refs) <= set(entries), "unknown_obligation_ref")
    units = []
    for brief_finding in brief_preview.units:
        authored = claims.get(brief_finding.unit_id)
        issues = tuple(
            dict.fromkeys(
                (
                    *brief_finding.issues,
                    *_obligation_issues(declared.get(brief_finding.unit_id), authored, by_ref),
                )
            )
        )
        units.append(
            ClaimObligationFinding(
                unit_id=brief_finding.unit_id,
                authored=authored,
                issues=issues,
                status="needs_scope_review" if issues else "declared_consistent",
            )
        )
    return AssessmentAuthorityPreview(
        work_brief_preview=brief_preview,
        authored_authority=authority,
        historical_bindings=findings,
        units=tuple(units),
    )


def render_assessment_authority(
    work: AssessmentWork,
    scope: AssessmentScope,
    declarations: ClaimScopeDeclarations,
    briefs: AssessmentWorkBriefs,
    authority: AssessmentAuthority,
    *,
    receipt: AssessmentReceipt | None = None,
    raw_final: str | None = None,
) -> str:
    """Full literal work plus separate local historical proof and recomputed findings."""
    work = AssessmentWork.model_validate_json(work.model_dump_json())
    preview = preview_assessment_authority(work, scope, declarations, briefs, authority)
    require((receipt is None) == (raw_final is None), "incomplete_result_arguments")
    result = (
        bind_assessment_result(work, scope, receipt, raw_final)
        if receipt is not None and raw_final is not None
        else None
    )
    payload = json.dumps(
        {
            "full_work": work.model_dump(mode="json"),
            "authority_preview": preview.model_dump(mode="json"),
            "bound_result": result.model_dump(mode="json") if result else None,
        },
        ensure_ascii=False,
        sort_keys=True,
        indent=2,
    )
    fence = "`" * max(3, 1 + max((len(m[0]) for m in re.finditer(r"`+", payload)), default=0))
    return (
        "# Read-only assessment authority preview\n\n"
        "Exact copying against supplied bodies is not event truth or justified criticism.\n"
        "Historical proof is separate from the unchanged work and its recorded model context.\n"
        "Roles, material obligations and visibility are authored; archive authentication is\n"
        "the adapter's responsibility. Semantic interpretation remains unverified.\n"
        "Evidence adequacy, support, obligation, fulfillment, edit necessity and craft remain\n"
        "unassessed. No model input, whole-relation credit or writer permission.\n\n"
        + fence
        + "json\n"
        + payload
        + "\n"
        + fence
        + "\n"
    )
