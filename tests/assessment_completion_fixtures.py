"""Authored local response fixtures. Never provider requests, deliveries or semantic gold."""

from __future__ import annotations

import json
from typing import Literal

from open_hollywood_engine.evaluations.assessment_intake import IntakeResult, compile_intake
from open_hollywood_engine.evaluations.assessment_result import (
    AssessmentScope,
    assessment_response_schema,
    scope_for_batch,
)
from open_hollywood_engine.evaluations.assessment_work import AssessmentReceipt, AssessmentWork
from open_hollywood_engine.evaluations.review_evidence import require, text_hash

AUTHORED_NOTICE = (
    "AUTHORED LOCAL RESPONSE FIXTURE. No model call or provider delivery occurred. "
    "Native model_assessment and receipt fields below contain synthetic test data. "
    "Binding/completion is structural only; no semantic evidence or writer permission."
)
DeliveryStatus = Literal["valid", "invalid", "length", "refusal", "transport_error", "cancelled"]


def local_input(result: IntakeResult) -> tuple[str, AssessmentScope]:
    """Bind an exact offline input document, without pretending it is a provider wire."""
    require(result == compile_intake(result.source, result.plan), "rehearsal_intake_mismatch")
    work = result.pending_work
    require(work is not None and len(work.batches) == 1, "rehearsal_requires_one_pending_batch")
    assert work is not None
    batch = work.batches[0]
    placeholder = scope_for_batch(work, batch.batch_id, "0" * 64)
    document = {
        "contract": "authored-local-assessment-input-1",
        "notice": AUTHORED_NOTICE,
        "provider_request": False,
        "model_input": False,
        "live_calls": 0,
        "work": work.model_dump(mode="json"),
        "declarations": result.declarations.model_dump(mode="json")
        if result.declarations
        else None,
        "briefs": result.briefs.model_dump(mode="json") if result.briefs else None,
        "batch": batch.model_dump(mode="json"),
        "response_schema": assessment_response_schema(work, placeholder),
    }
    text = json.dumps(document, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    return text, scope_for_batch(work, batch.batch_id, text_hash(text))


def authored_receipt(
    work: AssessmentWork,
    scope: AssessmentScope,
    raw: str,
    *,
    status: DeliveryStatus = "valid",
) -> AssessmentReceipt:
    """Only a test input to native validation; no asserted real tokens, time or transport."""
    return AssessmentReceipt(
        work_sha256=work.fingerprint,
        batch_id=scope.batch_id,
        request_sha256=scope.request_sha256,
        attempt_id="authored-local-fixture",
        status=status,
        result_sha256=text_hash(raw) if status == "valid" else None,
        assessed_unit_ids=scope.active_unit_ids if status == "valid" else (),
        input_tokens=None,
        output_tokens=None,
        reasoning_tokens=None,
        active_seconds=0,
    )
