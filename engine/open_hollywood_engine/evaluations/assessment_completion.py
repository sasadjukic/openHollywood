"""Pure authored completion over native assessment contracts; no I/O or provider types."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from typing import Literal

from pydantic import Field, model_validator

from open_hollywood_engine.evaluations.assessment_intake import IntakeResult, compile_intake
from open_hollywood_engine.evaluations.assessment_result import (
    assessment_response_schema,
    bind_assessment_result,
    scope_for_batch,
)
from open_hollywood_engine.evaluations.assessment_work import AssessmentReceipt, complete_work
from open_hollywood_engine.evaluations.assessment_work_brief import preview_work_briefs
from open_hollywood_engine.evaluations.contracts import canonical_sha256
from open_hollywood_engine.evaluations.review_evidence import (
    Digest,
    JsonObject,
    Record,
    require,
    strict_object,
    text_hash,
)

NOTICE = (
    "AUTHORED FIXTURE — NO MODEL DELIVERY. No model request or delivery occurred. "
    "Native model_assessment and receipt values are test data. Complete binding "
    "does not qualify support, evidence adequacy, editorial effect, craft or editing. "
    "Source authentication belongs to the registered application adapter."
)


class SourcePin(Record):
    source_origin: Literal["diagnostic_probe"]
    review_id: str = Field(min_length=1, max_length=200)
    intake_manifest_bytes_sha256: Digest
    intake_result_bytes_sha256: Digest
    source_canonical_sha256: Digest
    work_canonical_sha256: Digest
    declarations_canonical_sha256: Digest
    briefs_canonical_sha256: Digest


class AuthoredAttempt(Record):
    fixture_id: str = Field(min_length=1, max_length=200, pattern=r"\S")
    batch_id: str = Field(min_length=1, max_length=200, pattern=r"\S")
    local_input_bytes_sha256: Digest
    raw_final: str = Field(min_length=1, max_length=64_000)

    @model_validator(mode="after")
    def bound_bytes(self) -> AuthoredAttempt:
        require(len(self.raw_final.encode("utf-8")) <= 256_000, "raw_final_byte_bound")
        return self


class AuthoredSubmission(Record):
    contract: Literal["assessment-authored-submission-1"]
    origin: Literal["authored_fixture"]
    authored_by: str = Field(min_length=1, max_length=1200, pattern=r"\S")
    source: SourcePin
    attempts: tuple[AuthoredAttempt, ...] = Field(min_length=1, max_length=12)


def parse_submission(data: bytes) -> AuthoredSubmission:
    require(len(data) <= 4 * 1024 * 1024, "submission_byte_bound")
    parsed = strict_object(data.decode("utf-8"))
    return AuthoredSubmission.model_validate_json(encoded(parsed))


@dataclass(frozen=True)
class CompletionContext:
    """Pure derivation inputs. This type does not authenticate an archive or a delivery."""

    intake: IntakeResult
    pin: SourcePin
    exact_intake: bytes
    exact_manifest: bytes
    adapter_receipt: JsonObject


def encoded(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False) + "\n"
    ).encode("utf-8")


def expected_pin(intake: IntakeResult, manifest: bytes, original: bytes) -> SourcePin:
    work, declarations, briefs = intake.pending_work, intake.declarations, intake.briefs
    require(work is not None and declarations is not None and briefs is not None, "no_pending_work")
    assert work is not None and declarations is not None and briefs is not None
    require(intake.source.origin == "diagnostic_probe", "source_origin_not_qualified")
    return SourcePin(
        source_origin="diagnostic_probe",
        review_id=intake.source.review_id,
        intake_manifest_bytes_sha256=hashlib.sha256(manifest).hexdigest(),
        intake_result_bytes_sha256=hashlib.sha256(original).hexdigest(),
        source_canonical_sha256=intake.source.source_sha256,
        work_canonical_sha256=work.fingerprint,
        declarations_canonical_sha256=canonical_sha256(declarations.model_dump(mode="json")),
        briefs_canonical_sha256=canonical_sha256(briefs.model_dump(mode="json")),
    )


def fixture_input(source: CompletionContext, batch_id: str) -> bytes:
    intake = source.intake
    work, declarations, briefs = intake.pending_work, intake.declarations, intake.briefs
    assert work is not None and declarations is not None and briefs is not None
    scope = scope_for_batch(work, batch_id, "0" * 64)
    preview = preview_work_briefs(work, scope, declarations, briefs)
    require(all(u.status == "declared_consistent" for u in preview.units), "pending_scope_changed")
    return encoded(
        {
            "contract": "assessment-authored-input-1",
            "origin": "authored_fixture",
            "notice": NOTICE,
            "provider_request": False,
            "model_input": False,
            "source": source.pin.model_dump(mode="json"),
            "work": work.model_dump(mode="json"),
            "declarations": declarations.model_dump(mode="json"),
            "briefs": briefs.model_dump(mode="json"),
            "batch_id": batch_id,
            "active_unit_ids": list(scope.active_unit_ids),
            "response_schema": assessment_response_schema(work, scope),
        }
    )


def derive(source: CompletionContext, submission: AuthoredSubmission) -> JsonObject:
    """Mechanical derivation only; source authentication is an application precondition."""
    intake = IntakeResult.model_validate_json(source.intake.model_dump_json())
    require(intake == compile_intake(intake.source, intake.plan), "intake_changed")
    require(
        hashlib.sha256(source.exact_intake).hexdigest() == source.pin.intake_result_bytes_sha256,
        "intake_bytes_changed",
    )
    require(
        IntakeResult.model_validate_json(source.exact_intake) == intake, "intake_snapshot_changed"
    )
    require(
        expected_pin(intake, source.exact_manifest, source.exact_intake) == source.pin,
        "source_pin_inconsistent",
    )
    submission = AuthoredSubmission.model_validate_json(submission.model_dump_json())
    require(submission.source == source.pin, "submission_source_changed")
    work = intake.pending_work
    assert work is not None
    require(
        1 <= len(work.context.statements) <= 12 and len(work.batches) <= 12, "publisher_work_bound"
    )
    attempts = {a.batch_id: a for a in submission.attempts}
    require(len(attempts) == len(submission.attempts), "duplicate_batch")
    require(len({a.fixture_id for a in submission.attempts}) == len(attempts), "duplicate_fixture")
    require(set(attempts) == {b.batch_id for b in work.batches}, "batch_coverage")
    receipts = []
    results = []
    expected_requests: dict[str, str] = {}
    for batch in work.batches:
        attempt = attempts[batch.batch_id]
        local = fixture_input(source, batch.batch_id)
        require(len(local) <= 16 * 1024 * 1024, "fixture_input_byte_bound")
        digest = hashlib.sha256(local).hexdigest()
        require(digest == attempt.local_input_bytes_sha256, "fixture_input_changed")
        scope = scope_for_batch(work, batch.batch_id, digest)
        # Synthetic fixture receipt, never asserted to be a provider delivery.
        receipt = AssessmentReceipt(
            work_sha256=work.fingerprint,
            batch_id=batch.batch_id,
            request_sha256=digest,
            attempt_id=attempt.fixture_id,
            status="valid",
            result_sha256=text_hash(attempt.raw_final),
            assessed_unit_ids=scope.active_unit_ids,
            active_seconds=0,
        )
        result = bind_assessment_result(work, scope, receipt, attempt.raw_final)
        receipts.append(result.receipt)
        results.append(result.model_dump(mode="json"))
        expected_requests[batch.batch_id] = digest
    completion = complete_work(work, tuple(receipts), expected_requests)
    require(
        completion.complete_delivery and completion.binding == "complete", "incomplete_publication"
    )
    return strict_object(
        encoded(
            {
                "contract": "assessment-authored-completion-1",
                "origin": "authored_fixture",
                "notice": NOTICE,
                "source_binding": source.pin.model_dump(mode="json"),
                "source_adapter_receipt": source.adapter_receipt,
                "intake": intake.model_dump(mode="json"),
                "authored_submission": submission.model_dump(mode="json"),
                "results": results,
                "completion": completion.model_dump(mode="json"),
                "publication_state": "bound_unassessed",
                "model_evidence": False,
                "usage_applicability": "not_applicable_no_inference",
                "live_calls": 0,
                "writer_dispatch_authorized": False,
                "semantic_interpretation_verified": False,
                "evidence_adequacy": "unassessed",
                "factual_support": "unassessed",
                "editorial_effect": "unassessed",
                "edit_necessity": "unassessed",
                "craft": "unassessed",
            }
        ).decode()
    )


def render_completion(envelope: JsonObject) -> str:
    """Render a derived envelope literally, including all source and disposition context."""
    text = encoded(envelope).decode("utf-8")
    fence = "`" * max(3, 1 + max((len(m[0]) for m in re.finditer(r"`+", text)), default=0))
    return (
        "# Authored assessment completion\n\n"
        + NOTICE
        + "\n\n"
        + fence
        + "json\n"
        + text
        + fence
        + "\n"
    )
