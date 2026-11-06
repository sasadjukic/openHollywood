"""Authored work-brief previews bound to read-only scope; no inference or repair route."""

from __future__ import annotations

import json
import re
from typing import Annotated, Literal

from pydantic import Field

from open_hollywood_engine.evaluations.assessment_claim_scope import (
    ClaimScopeAudit,
    ClaimScopeDeclarations,
    audit_claim_scope,
)
from open_hollywood_engine.evaluations.assessment_result import (
    AssessmentScope,
    bind_assessment_result,
)
from open_hollywood_engine.evaluations.assessment_work import (
    AssessmentReceipt,
    AssessmentWork,
    Name,
)
from open_hollywood_engine.evaluations.contracts import canonical_sha256
from open_hollywood_engine.evaluations.review_evidence import Digest, Record, require

BriefText = Annotated[str, Field(min_length=1, max_length=1200, pattern=r"\S")]


class AuthoredWorkBrief(Record):
    """Author-supplied interpretation, not an inferred question or verified answer."""

    unit_id: Name
    question: BriefText
    temporal_scope: BriefText
    source_authority: BriefText
    evidence_obligation: BriefText


class AssessmentWorkBriefs(Record):
    contract: Literal["assessment-work-briefs-1"] = "assessment-work-briefs-1"
    work_sha256: Digest
    declarations_sha256: Digest
    authored_by: BriefText
    briefs: tuple[AuthoredWorkBrief, ...] = ()
    model_input: Literal[False] = False
    writer_dispatch_authorized: Literal[False] = False


class WorkBriefFinding(Record):
    unit_id: Name
    brief: AuthoredWorkBrief | None
    issues: tuple[str, ...]
    status: Literal["declared_consistent", "needs_scope_review"]


class WorkBriefPreview(Record):
    contract: Literal["assessment-work-brief-preview-1"] = "assessment-work-brief-preview-1"
    claim_scope_audit: ClaimScopeAudit
    authored_briefs: AssessmentWorkBriefs
    units: tuple[WorkBriefFinding, ...]
    # Identity and declaration checks cannot prove arbitrary prose is neutral or correct.
    semantic_interpretation_verified: Literal[False] = False
    brief_neutrality_verified: Literal[False] = False
    model_input: Literal[False] = False
    factual_support: Literal["unassessed"] = "unassessed"
    evidence_adequacy: Literal["unassessed"] = "unassessed"
    obligation_existence: Literal["unassessed"] = "unassessed"
    observed_fulfillment: Literal["unassessed"] = "unassessed"
    edit_necessity: Literal["unassessed"] = "unassessed"
    editorial_effect: Literal["unassessed"] = "unassessed"
    craft: Literal["unassessed"] = "unassessed"
    whole_relation_credit: Literal[False] = False
    writer_dispatch_authorized: Literal[False] = False


def preview_work_briefs(
    work: AssessmentWork,
    scope: AssessmentScope,
    declarations: ClaimScopeDeclarations,
    briefs: AssessmentWorkBriefs,
) -> WorkBriefPreview:
    """Recheck identities and propagate unresolved scope; never synthesize a missing brief."""
    work = AssessmentWork.model_validate_json(work.model_dump_json())
    audit = audit_claim_scope(work, scope, declarations)
    briefs = AssessmentWorkBriefs.model_validate_json(briefs.model_dump_json())
    require(briefs.work_sha256 == work.fingerprint, "work_brief_work_mismatch")
    require(
        briefs.declarations_sha256 == canonical_sha256(audit.declarations.model_dump(mode="json")),
        "work_brief_declarations_mismatch",
    )
    by_unit = {b.unit_id: b for b in briefs.briefs}
    require(len(by_unit) == len(briefs.briefs), "duplicate_work_brief")
    require(set(by_unit) <= {s.unit_id for s in work.context.statements}, "unknown_work_brief_unit")
    findings = []
    for finding in audit.units:
        brief = by_unit.get(finding.statement.unit_id)
        issues = finding.issues + (() if brief is not None else ("missing_work_brief",))
        findings.append(
            WorkBriefFinding(
                unit_id=finding.statement.unit_id,
                brief=brief,
                issues=issues,
                status="needs_scope_review" if issues else "declared_consistent",
            )
        )
    return WorkBriefPreview(claim_scope_audit=audit, authored_briefs=briefs, units=tuple(findings))


def render_work_briefs(
    work: AssessmentWork,
    scope: AssessmentScope,
    declarations: ClaimScopeDeclarations,
    briefs: AssessmentWorkBriefs,
    *,
    receipt: AssessmentReceipt | None = None,
    raw_final: str | None = None,
) -> str:
    """Literal full context, whole fields and declared questions; optional native result only."""
    work = AssessmentWork.model_validate_json(work.model_dump_json())
    preview = preview_work_briefs(work, scope, declarations, briefs)
    require((receipt is None) == (raw_final is None), "incomplete_result_arguments")
    result = (
        bind_assessment_result(work, preview.claim_scope_audit.scope, receipt, raw_final)
        if receipt is not None and raw_final is not None
        else None
    )
    payload = json.dumps(
        {
            "full_work": work.model_dump(mode="json"),
            "work_brief_preview": preview.model_dump(mode="json"),
            "bound_result": result.model_dump(mode="json") if result else None,
        },
        ensure_ascii=False,
        sort_keys=True,
        indent=2,
    )
    fence = "`" * max(3, 1 + max((len(m[0]) for m in re.finditer(r"`+", payload)), default=0))
    return (
        "# Read-only assessment work-brief preview\n\n"
        "Authored interpretation; identity and declaration consistency do not verify meaning\n"
        "or brief neutrality. Unresolved scope remains unresolved; no model input is created.\n"
        "Obligation existence, observed fulfillment and repair necessity are separate questions.\n"
        "Support, evidence adequacy, edit necessity and craft remain unassessed.\n"
        "No whole-relation credit or writer permission.\n\n"
        + fence
        + "json\n"
        + payload
        + "\n"
        + fence
        + "\n"
    )
