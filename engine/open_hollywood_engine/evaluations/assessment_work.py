"""Read-only assessment work and completion; no inference, persistence or repair route."""

from __future__ import annotations

import json
import re
from typing import Annotated, Literal, Self

from pydantic import Field, model_validator

from open_hollywood_engine.evaluations.contracts import canonical_sha256
from open_hollywood_engine.evaluations.review_evidence import (
    Digest,
    Record,
    SavedMessage,
    require,
    strict_object,
    text_hash,
)

Name = Annotated[str, Field(min_length=1, max_length=200)]
Count = Annotated[int, Field(ge=0)]


class ContextDocument(Record):
    """Complete immutable JSON document, not a selected excerpt or semantic proof."""

    identity: Name
    version: Name
    kind: Literal["source", "report", "registry", "scope"]
    content_json: str = Field(min_length=2, max_length=2_000_000)
    content_sha256: Digest

    @model_validator(mode="after")
    def check_content(self) -> Self:
        strict_object(self.content_json)
        require(text_hash(self.content_json) == self.content_sha256, "context_digest_mismatch")
        return self


class ReportField(Record):
    field_id: Name
    pointer: str = Field(pattern=r"^/")
    text: str = Field(min_length=1, max_length=100_000)


class SelectedStatement(Record):
    unit_id: Name
    field_id: Name
    start: Count
    end: Count
    quote: str = Field(min_length=1, max_length=100_000)


class DeclaredLink(Record):
    """Caller-declared inseparability, never inferred from component support labels."""

    link_id: Name
    unit_ids: tuple[Name, ...] = Field(min_length=2)
    origin: Literal["authored_diagnostic", "explicit_source_relation"]


class AssessmentContext(Record):
    contract: Literal["assessment-context-1"] = "assessment-context-1"
    provenance: Literal["synthetic_fixture", "diagnostic_capture"]
    origin_sha256: Digest
    documents: tuple[ContextDocument, ...] = Field(min_length=3)
    report_fields: tuple[ReportField, ...] = Field(min_length=1)
    statements: tuple[SelectedStatement, ...] = Field(min_length=1)
    declared_links: tuple[DeclaredLink, ...] = ()
    # The exact full source/report presentation. Does not contain answers/gold.
    messages: tuple[SavedMessage, ...] = Field(min_length=1)
    semantic_links_inferred: Literal[False] = False
    canonical_review_id: None = None
    writer_dispatch_authorized: Literal[False] = False

    @model_validator(mode="after")
    def check_bindings(self) -> Self:
        require(
            len({d.identity for d in self.documents}) == len(self.documents), "duplicate_document"
        )
        kinds = [d.kind for d in self.documents]
        require(kinds.count("report") == 1 and "source" in kinds, "incomplete_context")
        fields = {f.field_id: f for f in self.report_fields}
        require(len(fields) == len(self.report_fields), "duplicate_field")
        report = strict_object(next(d.content_json for d in self.documents if d.kind == "report"))
        require(len({f.pointer for f in self.report_fields}) == len(fields), "duplicate_pointer")
        for field in self.report_fields:
            value: object = report
            for token in field.pointer[1:].split("/"):
                key = token.replace("~1", "/").replace("~0", "~")
                if isinstance(value, dict):
                    require(key in value, "missing_report_pointer")
                    value = value[key]
                elif isinstance(value, list):
                    require(key.isdecimal() and int(key) < len(value), "invalid_report_index")
                    value = value[int(key)]
                else:
                    require(False, "invalid_report_pointer")
            require(value == field.text, "report_field_mismatch")
        units = {s.unit_id for s in self.statements}
        require(len(units) == len(self.statements), "duplicate_statement")
        spans = {(s.field_id, s.start, s.end) for s in self.statements}
        require(len(spans) == len(self.statements), "duplicate_selection")
        for statement in self.statements:
            require(statement.field_id in fields, "unknown_field")
            text = fields[statement.field_id].text
            require(0 <= statement.start < statement.end <= len(text), "invalid_offsets")
            require(text[statement.start : statement.end] == statement.quote, "quote_mismatch")
        require(
            len({g.link_id for g in self.declared_links}) == len(self.declared_links), "link_id"
        )
        for link in self.declared_links:
            require(len(set(link.unit_ids)) == len(link.unit_ids), "duplicate_link_member")
            require(set(link.unit_ids) <= units, "unknown_link_member")
        return self

    @property
    def fingerprint(self) -> str:
        return canonical_sha256(self.model_dump(mode="json"))


class AssessmentBatch(Record):
    batch_id: Name
    unit_ids: tuple[Name, ...] = Field(min_length=1)


class AssessmentWork(Record):
    contract: Literal["assessment-work-1"] = "assessment-work-1"
    context: AssessmentContext
    context_sha256: Digest
    maximum_units: int = Field(gt=0)
    batches: tuple[AssessmentBatch, ...] = Field(min_length=1)
    support: Literal["unassessed"] = "unassessed"
    edit_necessity: Literal["unassessed"] = "unassessed"
    craft: Literal["unassessed"] = "unassessed"
    writer_dispatch_authorized: Literal[False] = False

    @model_validator(mode="after")
    def check_partition(self) -> Self:
        require(self.context_sha256 == self.context.fingerprint, "context_scope_mismatch")
        require(len({b.batch_id for b in self.batches}) == len(self.batches), "duplicate_batch")
        actual = [unit for batch in self.batches for unit in batch.unit_ids]
        expected = {s.unit_id for s in self.context.statements}
        require(len(actual) == len(set(actual)) and set(actual) == expected, "selection_coverage")
        require(all(len(b.unit_ids) <= self.maximum_units for b in self.batches), "batch_overflow")
        for link in self.context.declared_links:
            require(
                any(set(link.unit_ids) <= set(b.unit_ids) for b in self.batches), "split_relation"
            )
        return self

    @property
    def fingerprint(self) -> str:
        return canonical_sha256(self.model_dump(mode="json"))


def partition_work(context: AssessmentContext, maximum_units: int) -> AssessmentWork:
    """Pack whole statements and transitive declared links without discovering semantics."""
    require(type(maximum_units) is int and maximum_units > 0, "invalid_batch_limit")
    context = AssessmentContext.model_validate_json(context.model_dump_json())
    order = [s.unit_id for s in context.statements]
    groups = [{unit} for unit in order]
    for link in context.declared_links:
        touching = [g for g in groups if g.intersection(link.unit_ids)]
        merged = set().union(*touching)
        groups = [g for g in groups if g not in touching] + [merged]
    groups.sort(key=lambda g: min(order.index(unit) for unit in g))
    chunks: list[list[str]] = []
    for group in groups:
        require(len(group) <= maximum_units, "linked_group_exceeds_limit")
        if not chunks or len(chunks[-1]) + len(group) > maximum_units:
            chunks.append([])
        chunks[-1].extend(unit for unit in order if unit in group)
    return AssessmentWork(
        context=context,
        context_sha256=context.fingerprint,
        maximum_units=maximum_units,
        batches=tuple(
            AssessmentBatch(batch_id=f"batch-{i:03d}", unit_ids=tuple(chunk))
            for i, chunk in enumerate(chunks, 1)
        ),
    )


class AssessmentReceipt(Record):
    """Delivery facts only. A structurally valid result is still semantically unassessed."""

    work_sha256: Digest
    batch_id: Name
    request_sha256: Digest
    attempt_id: Name
    status: Literal["valid", "invalid", "length", "refusal", "transport_error", "cancelled"]
    result_sha256: Digest | None = None
    assessed_unit_ids: tuple[Name, ...] = ()
    binding: Literal["unresolved", "complete"] = "unresolved"
    input_tokens: Count | None = None
    output_tokens: Count | None = None
    reasoning_tokens: Count | None = None
    active_seconds: float = Field(ge=0, allow_inf_nan=False)

    @model_validator(mode="after")
    def check_status(self) -> Self:
        if self.status == "valid":
            require(self.result_sha256 is not None and bool(self.assessed_unit_ids), "no_result")
        else:
            require(
                self.result_sha256 is None
                and not self.assessed_unit_ids
                and self.binding == "unresolved",
                "failed_delivery_has_credit",
            )
        if self.reasoning_tokens is not None:
            require(
                self.output_tokens is not None and self.reasoning_tokens <= self.output_tokens,
                "reasoning_exceeds_generation",
            )
        return self


class Completion(Record):
    work_sha256: Digest
    expected_batches: Count
    completed_batches: Count
    expected_units: Count
    delivered_units: Count
    complete_delivery: bool
    binding: Literal["unresolved", "complete"]
    known_input_tokens: Count
    known_output_tokens: Count
    unknown_usage_attempts: Count
    total_active_seconds: float
    support: Literal["unassessed"] = "unassessed"
    edit_necessity: Literal["unassessed"] = "unassessed"
    craft: Literal["unassessed"] = "unassessed"
    whole_relation_credit: Literal[False] = False
    writer_dispatch_authorized: Literal[False] = False


def complete_work(
    work: AssessmentWork,
    receipts: tuple[AssessmentReceipt, ...],
    expected_requests: dict[str, str],
) -> Completion:
    """Account for every batch; no retries, partial success or semantic aggregation."""
    # Revalidate even instances produced through model_copy/model_construct.
    work = AssessmentWork.model_validate_json(work.model_dump_json())
    checked = tuple(AssessmentReceipt.model_validate_json(r.model_dump_json()) for r in receipts)
    batches = {b.batch_id: b for b in work.batches}
    require(set(expected_requests) == set(batches), "request_manifest_coverage")
    require(len({r.batch_id for r in checked}) == len(checked), "duplicate_receipt")
    require(len({r.attempt_id for r in checked}) == len(checked), "duplicate_attempt")
    for receipt in checked:
        require(receipt.work_sha256 == work.fingerprint, "mixed_work_scope")
        require(receipt.batch_id in batches, "unknown_batch")
        require(
            receipt.request_sha256 == expected_requests[receipt.batch_id], "wrong_request_receipt"
        )
        if receipt.status == "valid":
            expected = batches[receipt.batch_id].unit_ids
            require(
                len(receipt.assessed_unit_ids) == len(expected)
                and set(receipt.assessed_unit_ids) == set(expected),
                "incomplete_batch_result",
            )
    valid = [r for r in checked if r.status == "valid"]
    complete = len(valid) == len(batches)
    return Completion(
        work_sha256=work.fingerprint,
        expected_batches=len(batches),
        completed_batches=len(valid),
        expected_units=len(work.context.statements),
        delivered_units=sum(len(r.assessed_unit_ids) for r in valid),
        complete_delivery=complete,
        binding="complete"
        if complete and all(r.binding == "complete" for r in valid)
        else "unresolved",
        known_input_tokens=sum(r.input_tokens or 0 for r in checked),
        known_output_tokens=sum(r.output_tokens or 0 for r in checked),
        unknown_usage_attempts=sum(
            r.input_tokens is None or r.output_tokens is None for r in checked
        ),
        total_active_seconds=sum(r.active_seconds for r in checked),
    )


def render_work(work: AssessmentWork) -> str:
    """Literal complete context and selections; never executes embedded Markdown/HTML."""
    checked = AssessmentWork.model_validate_json(work.model_dump_json())
    payload = json.dumps(checked.model_dump(mode="json"), ensure_ascii=False, indent=2)
    fence = "`" * max(3, 1 + max((len(m[0]) for m in re.finditer(r"`+", payload)), default=0))
    return (
        "# Read-only assessment work\n\nSupport, edit necessity and craft remain unassessed.\n\n"
        + fence
        + "json\n"
        + payload
        + "\n"
        + fence
        + "\n"
    )
