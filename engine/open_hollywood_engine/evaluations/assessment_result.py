"""Read-only active results and literal evidence locations; no inference or writer route."""

from __future__ import annotations

import json
import re
from typing import Literal, Self

from pydantic import Field, JsonValue, model_validator

from open_hollywood_engine.evaluations.assessment_work import (
    AssessmentReceipt,
    AssessmentWork,
    Count,
    Name,
    SelectedStatement,
)
from open_hollywood_engine.evaluations.review_evidence import (
    Digest,
    JsonObject,
    Record,
    require,
    strict_object,
    text_hash,
)


class EvidenceLocation(Record):
    """Application-owned field or paragraph location, never a support judgment."""

    ref: Name
    document_id: Name
    document_version: Name
    document_sha256: Digest
    field_pointer: str = Field(pattern=r"^/")
    field_sha256: Digest
    start: Count
    end: Count
    quote: str = Field(min_length=1, max_length=100_000)
    # None means the complete field; integers identify nonempty paragraphs, one-based.
    paragraph: int | None = Field(default=None, ge=1)


class EvidenceRegistry(Record):
    contract: Literal["assessment-evidence-registry-1"] = "assessment-evidence-registry-1"
    entries: tuple[EvidenceLocation, ...] = Field(min_length=1, max_length=10_000)

    @model_validator(mode="after")
    def unique_refs(self) -> Self:
        require(len({e.ref for e in self.entries}) == len(self.entries), "duplicate_evidence_ref")
        return self


class AssessmentScope(Record):
    contract: Literal["assessment-active-scope-1"] = "assessment-active-scope-1"
    work_sha256: Digest
    batch_id: Name
    request_sha256: Digest
    active_unit_ids: tuple[Name, ...] = Field(min_length=1, max_length=12)


class ModelAssessment(Record):
    """Fallible model-authored values, explicitly separate from application authority."""

    support: Literal["supported", "unsupported", "uncertain"]
    evidence: tuple[Name, ...] = Field(max_length=8)
    reason: str = Field(min_length=1, max_length=1200)

    @model_validator(mode="after")
    def check_content(self) -> Self:
        require(bool(self.reason.strip()), "blank_assessment_reason")
        require(len(set(self.evidence)) == len(self.evidence), "duplicate_assessment_evidence")
        require(bool(self.evidence) or self.support == "uncertain", "definite_without_evidence")
        return self


class _Response(Record):
    assessments: dict[str, ModelAssessment]


class LocatedAssessment(Record):
    statement: SelectedStatement
    model_assessment: ModelAssessment
    evidence_locations: tuple[EvidenceLocation, ...]


class BoundAssessmentResult(Record):
    contract: Literal["assessment-bound-result-1"] = "assessment-bound-result-1"
    scope: AssessmentScope
    delivery_receipt: AssessmentReceipt
    receipt: AssessmentReceipt
    raw_final: str = Field(min_length=1, max_length=64_000)
    units: tuple[LocatedAssessment, ...]
    binding: Literal["complete"] = "complete"
    support: Literal["unassessed"] = "unassessed"
    evidence_adequacy: Literal["unassessed"] = "unassessed"
    edit_necessity: Literal["unassessed"] = "unassessed"
    craft: Literal["unassessed"] = "unassessed"
    whole_relation_credit: Literal[False] = False
    writer_dispatch_authorized: Literal[False] = False


def _field(content: JsonObject, pointer: str) -> str:
    require(re.search(r"~(?![01])", pointer) is None, "invalid_evidence_pointer")
    value: JsonValue = content
    for token in pointer[1:].split("/"):
        key = token.replace("~1", "/").replace("~0", "~")
        if isinstance(value, dict):
            require(key in value, "missing_evidence_field")
            value = value[key]
        elif isinstance(value, list):
            require(re.fullmatch(r"0|[1-9][0-9]*", key) is not None, "invalid_evidence_index")
            index = int(key)
            require(index < len(value), "missing_evidence_index")
            value = value[index]
        else:
            require(False, "invalid_evidence_pointer")
    require(isinstance(value, str), "nontext_evidence_field")
    assert isinstance(value, str)
    return value


def _paragraphs(text: str) -> tuple[tuple[int, int], ...]:
    """Pinned blank-line algorithm, preserving spaces and repeated occurrences exactly."""
    spans = []
    start = 0
    for separator in re.finditer(r"\r?\n[ \t]*\r?\n", text):
        if text[start : separator.start()].strip():
            spans.append((start, separator.start()))
        start = separator.end()
    if text[start:].strip():
        spans.append((start, len(text)))
    return tuple(spans)


def _registry(work: AssessmentWork) -> EvidenceRegistry:
    documents = [d for d in work.context.documents if d.kind == "registry"]
    require(len(documents) == 1, "expected_one_evidence_registry")
    # Reject duplicate JSON keys before Pydantic can collapse them.
    strict_object(documents[0].content_json)
    registry = EvidenceRegistry.model_validate_json(documents[0].content_json)
    sources = {d.identity: d for d in work.context.documents if d.kind == "source"}
    parsed_sources: dict[str, JsonObject] = {}
    fields: dict[tuple[str, str], str] = {}
    for entry in registry.entries:
        require(entry.document_id in sources, "unknown_evidence_document")
        document = sources[entry.document_id]
        require(document.version == entry.document_version, "evidence_version_mismatch")
        require(document.content_sha256 == entry.document_sha256, "evidence_document_mismatch")
        key = (document.identity, entry.field_pointer)
        if key not in fields:
            if document.identity not in parsed_sources:
                parsed_sources[document.identity] = strict_object(document.content_json)
            fields[key] = _field(parsed_sources[document.identity], entry.field_pointer)
        field = fields[key]
        require(text_hash(field) == entry.field_sha256, "evidence_field_mismatch")
        require(0 <= entry.start < entry.end <= len(field), "invalid_evidence_offsets")
        require(field[entry.start : entry.end] == entry.quote, "evidence_quote_mismatch")
        expected = (0, len(field))
        if entry.paragraph is not None:
            paragraphs = _paragraphs(field)
            require(entry.paragraph <= len(paragraphs), "unknown_evidence_paragraph")
            expected = paragraphs[entry.paragraph - 1]
        require((entry.start, entry.end) == expected, "evidence_section_mismatch")
    return registry


def scope_for_batch(work: AssessmentWork, batch_id: str, request_sha256: str) -> AssessmentScope:
    """Bind an adapter-authenticated exact request hash; does not create a request."""
    checked = AssessmentWork.model_validate_json(work.model_dump_json())
    batches = {b.batch_id: b for b in checked.batches}
    require(batch_id in batches, "unknown_batch")
    _registry(checked)
    return AssessmentScope(
        work_sha256=checked.fingerprint,
        batch_id=batch_id,
        request_sha256=request_sha256,
        active_unit_ids=batches[batch_id].unit_ids,
    )


def _check_scope(
    work: AssessmentWork, scope: AssessmentScope
) -> tuple[AssessmentWork, AssessmentScope]:
    checked = AssessmentWork.model_validate_json(work.model_dump_json())
    scope = AssessmentScope.model_validate_json(scope.model_dump_json())
    expected = scope_for_batch(checked, scope.batch_id, scope.request_sha256)
    require(scope == expected, "active_scope_mismatch")
    return checked, scope


def assessment_response_schema(work: AssessmentWork, scope: AssessmentScope) -> JsonObject:
    """Closed, exact active slots. Provider compatibility is not asserted by this schema."""
    checked, scope = _check_scope(work, scope)
    item = {
        "type": "object",
        "additionalProperties": False,
        "required": ["support", "evidence", "reason"],
        "properties": {
            "support": {"type": "string", "enum": ["supported", "unsupported", "uncertain"]},
            "evidence": {
                "type": "array",
                "minItems": 0,
                "maxItems": 8,
                "items": {"type": "string", "enum": [e.ref for e in _registry(checked).entries]},
            },
            "reason": {"type": "string", "minLength": 1, "maxLength": 1200},
        },
    }
    return strict_object(
        json.dumps(
            {
                "type": "object",
                "additionalProperties": False,
                "required": ["assessments"],
                "properties": {
                    "assessments": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": list(scope.active_unit_ids),
                        "properties": {unit: item for unit in scope.active_unit_ids},
                    }
                },
            }
        )
    )


def bind_assessment_result(
    work: AssessmentWork,
    scope: AssessmentScope,
    receipt: AssessmentReceipt,
    raw_final: str,
) -> BoundAssessmentResult:
    """Resolve successful raw delivery whole; reject extras, drift and failed-final salvage.

    For this versioned boundary receipt.result_sha256 hashes the exact raw final UTF-8
    text. The caller must authenticate transport status, actual wire and terminal usage.
    No historical receipt or provider request is converted implicitly.
    """
    checked, scope = _check_scope(work, scope)
    receipt = AssessmentReceipt.model_validate_json(receipt.model_dump_json())
    require(receipt.status == "valid", "unsuccessful_assessment_delivery")
    require(receipt.work_sha256 == scope.work_sha256, "mixed_work_scope")
    require(receipt.batch_id == scope.batch_id, "wrong_result_batch")
    require(receipt.request_sha256 == scope.request_sha256, "wrong_request_receipt")
    require(
        len(receipt.assessed_unit_ids) == len(scope.active_unit_ids)
        and set(receipt.assessed_unit_ids) == set(scope.active_unit_ids),
        "incomplete_batch_result",
    )
    require(0 < len(raw_final) <= 64_000, "assessment_final_bound")
    require(text_hash(raw_final) == receipt.result_sha256, "assessment_final_digest_mismatch")
    strict_object(raw_final)
    response = _Response.model_validate_json(raw_final)
    require(set(response.assessments) == set(scope.active_unit_ids), "active_result_coverage")
    require(sum(len(row.reason) for row in response.assessments.values()) <= 8000, "reason_total")
    registry = {e.ref: e for e in _registry(checked).entries}
    statements = {s.unit_id: s for s in checked.context.statements}
    units = []
    for unit_id in scope.active_unit_ids:
        row = response.assessments[unit_id]
        require(set(row.evidence) <= set(registry), "unknown_assessment_evidence")
        units.append(
            LocatedAssessment(
                statement=statements[unit_id],
                model_assessment=row,
                evidence_locations=tuple(registry[ref] for ref in row.evidence),
            )
        )
    return BoundAssessmentResult(
        scope=scope,
        delivery_receipt=receipt,
        receipt=receipt.model_copy(update={"binding": "complete"}),
        raw_final=raw_final,
        units=tuple(units),
    )


def render_assessment_result(
    work: AssessmentWork,
    scope: AssessmentScope,
    receipt: AssessmentReceipt,
    raw_final: str,
) -> str:
    """Recompute locations and render full context and raw/model/application values literally."""
    result = bind_assessment_result(work, scope, receipt, raw_final)
    payload = json.dumps(
        {"full_work": work.model_dump(mode="json"), "result": result.model_dump(mode="json")},
        ensure_ascii=False,
        indent=2,
    )
    fence = "`" * max(3, 1 + max((len(m[0]) for m in re.finditer(r"`+", payload)), default=0))
    return (
        "# Read-only assessment result\n\n"
        "Locations are application-verified; model judgments remain unassessed.\n"
        "Evidence adequacy, factual support, edit necessity and craft remain unassessed.\n"
        "No whole-relation credit or writer permission is granted.\n\n"
        + fence
        + "json\n"
        + payload
        + "\n"
        + fence
        + "\n"
    )
