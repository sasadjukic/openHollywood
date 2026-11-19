"""Display records derived only after registered publication authentication.

These records attribute model judgments; they neither verify them nor attach them
to production artifacts. This module is not an admission path for caller receipts.
"""

from __future__ import annotations

import json
import re
from typing import Literal

from open_hollywood_engine.evaluations.assessment_authored_source import AuthoredSource
from open_hollywood_engine.evaluations.assessment_authority import AssessmentAuthority
from open_hollywood_engine.evaluations.assessment_claim_scope import ClaimScopeDeclaration
from open_hollywood_engine.evaluations.assessment_completion import encoded
from open_hollywood_engine.evaluations.assessment_intake import IntakeFinding, IntakeResult
from open_hollywood_engine.evaluations.assessment_result import (
    BoundAssessmentResult,
    EvidenceLocation,
    ModelAssessment,
    _field,
    bind_assessment_result,
)
from open_hollywood_engine.evaluations.assessment_work import ReportField, complete_work
from open_hollywood_engine.evaluations.assessment_work_brief import AuthoredWorkBrief
from open_hollywood_engine.evaluations.contracts import canonical_sha256
from open_hollywood_engine.evaluations.review_evidence import (
    Digest,
    JsonObject,
    Record,
    require,
    strict_object,
)
from pydantic import Field

HOLDS = ("semantic_support", "evidence_adequacy", "editorial_effect", "edit_necessity", "craft")
NOTICE = (
    "READ-ONLY DIAGNOSTIC CONSUMER. Model judgments are attributed reports, not verified "
    "facts or editing approval. No canonical production artifact association. Local journal "
    "binding is not provider-signed attestation. Writer permission is false."
)
SourceOrigin = Literal["authored_diagnostic", "registered_diagnostic_probe"]


class Holds(Record):
    semantic_support: Literal["unassessed"] = "unassessed"
    evidence_adequacy: Literal["unassessed"] = "unassessed"
    editorial_effect: Literal["unassessed"] = "unassessed"
    edit_necessity: Literal["unassessed"] = "unassessed"
    craft: Literal["unassessed"] = "unassessed"
    writer_dispatch_authorized: Literal[False] = False


class Identity(Record):
    registration: str
    publication_sha256: Digest
    work_sha256: Digest
    request_sha256: Digest
    field_pointer: str
    unit_id: str | None


class Citation(Record):
    location: EvidenceLocation
    field_extent: Literal["complete_field", "located_section"]
    material_coverage: Literal["unassessed"] = "unassessed"


class ConsumerField(Holds):
    identity: Identity
    identity_sha256: Digest
    original_field: ReportField
    original_selection_status: Literal["pending_assessment", "hold", "not_selected"]
    selection_detail: IntakeFinding | None
    display_status: Literal["model_judgment_available", "hold", "not_selected"]
    model_judgment: ModelAssessment | None
    citations: tuple[Citation, ...]
    claim_declaration: ClaimScopeDeclaration | None
    work_brief: AuthoredWorkBrief | None


class Usage(Record):
    input_tokens: int = Field(strict=True, ge=0)
    output_tokens: int = Field(strict=True, ge=0)
    reasoning_tokens: int = Field(strict=True, ge=0)
    cached_input_tokens: int = Field(strict=True, ge=0)


class ProductionBinding(Record):
    canonical_review_id: None = None
    artifact_version_id: None = None
    status: Literal["not_qualified"] = "not_qualified"


class ConsumerProjection(Holds):
    contract: Literal["assessment-consumer-projection-1"] = "assessment-consumer-projection-1"
    notice: str = NOTICE
    registration: str
    work: str
    publication_sha256: Digest
    work_sha256: Digest
    request_sha256: Digest
    source_origin: SourceOrigin
    delivery_origin: Literal["observed_openai_transport"] = "observed_openai_transport"
    observation_binding: JsonObject
    status: Literal["observed_bound_unassessed"] = "observed_bound_unassessed"
    production_binding: ProductionBinding = ProductionBinding()
    authority_record: AssessmentAuthority | None
    authority_record_status: Literal[
        "explicit_authored_record", "not_supplied_use_declared_scope_and_work_brief"
    ]
    usage: Usage
    accounting_clear: Literal[True] = True
    actual_billed_cost: None = None
    fields: tuple[ConsumerField, ...]
    whole_review_verdict: None = None
    live_calls: Literal[0] = 0


def _object(value: object) -> JsonObject:
    require(isinstance(value, dict), "consumer_object_required")
    return strict_object(encoded(value).decode("utf-8"))


def _project(
    envelope: JsonObject,
    *,
    registration: str,
    publication_sha256: str,
    work_name: str,
    source_origin: SourceOrigin,
    observation_binding: JsonObject,
) -> ConsumerProjection:
    """Internal projection: the exporter must authenticate the entire fixed publication first."""
    authored = source_origin == "authored_diagnostic"
    require(
        envelope.get("contract")
        == (
            "assessment-authored-observed-completion-1"
            if authored
            else "assessment-observed-completion-1"
        )
        and envelope.get("source_origin") == source_origin
        and envelope.get("delivery_origin" if authored else "origin") == "observed_openai_transport"
        and envelope.get("work") == work_name
        and envelope.get("observation_binding") == observation_binding,
        "consumer_source_binding",
    )
    require(
        all(envelope.get(k) == "unassessed" for k in HOLDS)
        and envelope.get("writer_dispatch_authorized") is False
        and envelope.get("actual_billed_cost") is None
        and envelope.get("live_calls") == 0,
        "consumer_credit_forbidden",
    )
    require(
        envelope.get("state") == "bound_unassessed"
        and envelope.get("journal_closed") is True
        and envelope.get("stop_reason") == "complete",
        "consumer_incomplete_delivery",
    )
    terminal = _object(envelope.get("terminal"))
    usage = Usage.model_validate_json(encoded(terminal.get("usage")))
    require(
        envelope.get("accounting_clear") is True
        and terminal.get("accounting_hold") is False
        and terminal.get("budget_violations") == []
        and terminal.get("unknown_elapsed_endpoints") == 0,
        "consumer_accounting_hold",
    )
    slots = envelope.get("endpoint_slots")
    require(isinstance(slots, list), "consumer_endpoint_slots")
    assert isinstance(slots, list)
    require(
        len(slots) == 2
        and [
            (_object(s).get("work"), _object(s).get("stage"), _object(s).get("state"))
            for s in slots
        ]
        == [(work_name, stage, "observed_terminal") for stage in ("input_count", "generation")],
        "consumer_endpoint_coverage",
    )
    findings: dict[str, IntakeFinding] = {}
    authority = None
    if authored:
        source = AuthoredSource.model_validate_json(encoded(envelope.get("source")))
        work, declarations, briefs = source.work, source.declarations, source.briefs
        authority = AssessmentAuthority.model_validate_json(
            encoded(envelope.get("request_bound_authority"))
        )
    else:
        intake = IntakeResult.model_validate_json(encoded(envelope.get("intake")))
        require(
            intake.pending_work is not None
            and intake.declarations is not None
            and intake.briefs is not None,
            "consumer_missing_work",
        )
        assert intake.pending_work is not None
        assert intake.declarations is not None and intake.briefs is not None
        work, declarations, briefs = intake.pending_work, intake.declarations, intake.briefs
        findings = {f.field.field_id: f for f in intake.findings}
        require(
            len(findings) == len(intake.findings) == len(work.context.report_fields)
            and tuple(f.field for f in intake.findings) == work.context.report_fields,
            "consumer_inventory_mismatch",
        )
    require(work.context.canonical_review_id is None, "consumer_production_binding_forbidden")
    require(terminal.get("state") == "bound_unassessed", "consumer_terminal_failed")
    bound = BoundAssessmentResult.model_validate_json(encoded(terminal.get("bound_result")))
    rebound = bind_assessment_result(work, bound.scope, bound.delivery_receipt, bound.raw_final)
    require(rebound == bound, "consumer_result_changed")
    require(
        terminal.get("native_receipt") == bound.receipt.model_dump(mode="json"),
        "consumer_receipt_changed",
    )
    request = bound.scope.request_sha256
    completion = complete_work(work, (bound.receipt,), {bound.scope.batch_id: request})
    require(
        completion.complete_delivery
        and completion.binding == "complete"
        and envelope.get("completion") == completion.model_dump(mode="json"),
        "consumer_whole_work_incomplete",
    )
    if authored:
        require(
            authority is not None
            and authority.model_dump(mode="json")
            == {**source.authority.model_dump(mode="json"), "request_sha256": request},
            "consumer_authority_changed",
        )
    units = {u.statement.unit_id: u for u in rebound.units}
    statements = {s.field_id: s for s in work.context.statements}
    decls = {d.statement.unit_id: d for d in declarations.declarations}
    brief_map = {b.unit_id: b for b in briefs.briefs}
    require(
        len(statements) == len(work.context.statements) == len(units)
        and set(units) == {s.unit_id for s in statements.values()}
        and set(units) == set(decls) == set(brief_map)
        and len(decls) == len(declarations.declarations)
        and len(brief_map) == len(briefs.briefs),
        "consumer_selected_scope_incomplete",
    )
    documents = {d.identity: d for d in work.context.documents}
    rows = []
    for field in work.context.report_fields:
        statement = statements.get(field.field_id)
        finding = findings.get(field.field_id)
        selection = (
            finding.status if finding else ("pending_assessment" if statement else "not_selected")
        )
        require(
            (selection == "pending_assessment") == (statement is not None),
            "consumer_selection_changed",
        )
        citations = []
        unit = None
        if statement:
            require(
                statement.start == 0
                and statement.end == len(field.text)
                and statement.quote == field.text,
                "consumer_whole_field_required",
            )
            unit = units[statement.unit_id]
            for location in unit.evidence_locations:
                text = _field(
                    strict_object(documents[location.document_id].content_json),
                    location.field_pointer,
                )
                citations.append(
                    Citation(
                        location=location,
                        field_extent="complete_field"
                        if location.start == 0 and location.end == len(text)
                        else "located_section",
                    )
                )
        identity = Identity(
            registration=registration,
            publication_sha256=publication_sha256,
            work_sha256=work.fingerprint,
            request_sha256=request,
            field_pointer=field.pointer,
            unit_id=statement.unit_id if statement else None,
        )
        rows.append(
            ConsumerField(
                identity=identity,
                identity_sha256=canonical_sha256(identity.model_dump(mode="json")),
                original_field=field,
                original_selection_status=selection,
                selection_detail=finding,
                display_status="model_judgment_available"
                if statement
                else ("hold" if selection == "hold" else "not_selected"),
                model_judgment=unit.model_assessment if unit else None,
                citations=tuple(citations),
                claim_declaration=decls[statement.unit_id] if statement else None,
                work_brief=brief_map[statement.unit_id] if statement else None,
            )
        )
    return ConsumerProjection(
        registration=registration,
        work=work_name,
        publication_sha256=publication_sha256,
        work_sha256=work.fingerprint,
        request_sha256=request,
        source_origin=source_origin,
        observation_binding=observation_binding,
        usage=usage,
        fields=tuple(rows),
        authority_record=authority,
        authority_record_status="explicit_authored_record"
        if authored
        else "not_supplied_use_declared_scope_and_work_brief",
    )


def _literal(value: object) -> str:
    text = json.dumps(value, ensure_ascii=False, indent=2)
    longest = max((len(m.group()) for m in re.finditer(r"`+", text)), default=0)
    fence = "`" * max(3, longest + 1)
    return f"{fence}json\n{text}\n{fence}\n"


def _render(view: ConsumerProjection) -> bytes:
    require(
        re.fullmatch(r"F0[123]|N(06|07|10|11)", view.work) is not None,
        "consumer_unregistered_work_name",
    )
    name = view.work
    count = sum(row.model_judgment is not None for row in view.fields)
    text = f"# {name}: read-only assessment\n\n{NOTICE}\n\n"
    text += (
        f"State: **observed_bound_unassessed**. {count} selected whole claims delivered; "
        f"{len(view.fields)} original fields retained. This is not a whole-review verdict.\n\n"
        f"[Original envelope]({name}.completion.json) · "
        f"[Original native view]({name}.view.md) · "
        f"[Consumer record](consumer.{name}.json)\n\n"
    )
    text += _literal(view.model_dump(mode="json", exclude={"fields", "authority_record"}))
    text += "\nSeparate request-bound authority record (absent for probe sources):\n\n"
    text += _literal(
        view.authority_record.model_dump(mode="json") if view.authority_record else None
    )
    for number, row in enumerate(view.fields, 1):
        text += f"\n## Field {number}: {row.display_status}\n\n"
        text += (
            "Original field, scope and attributed model result. Complete citation spans "
            "do not establish material sufficiency:\n\n"
        )
        text += _literal(row.model_dump(mode="json"))
    return text.encode("utf-8")
