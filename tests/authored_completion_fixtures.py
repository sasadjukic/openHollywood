"""Explicitly authored completion inputs, never model observations or semantic gold."""

from __future__ import annotations

import hashlib

from open_hollywood_engine.evaluations.assessment_completion import (
    AuthoredAttempt,
    AuthoredSubmission,
    CompletionContext,
    encoded,
    expected_pin,
    fixture_input,
)
from open_hollywood_engine.evaluations.assessment_intake import IntakeResult, compile_intake

from tests.assessment_intake_fixtures import authored_source, choice_for, plan_for


def context_for(intake: IntakeResult) -> CompletionContext:
    data = encoded(intake.model_dump(mode="json"))
    manifest = b'{"authored_test_only":true}'
    return CompletionContext(
        intake,
        expected_pin(intake, manifest, data),
        data,
        manifest,
        {"origin": "authored_test_only_not_source_authentication"},
    )


def authored_context() -> CompletionContext:
    source = authored_source()
    plan = plan_for(
        source,
        choice_for(source, "Q001"),
        choice_for(source, "Q002", "literal_procedure"),
        choice_for(source, "Q003", "editorial_effect"),
        choice_for(source, "Q004", "ambiguous"),
    ).model_copy(update={"maximum_units": 1})
    return context_for(compile_intake(source, plan))


def submission_for(context: CompletionContext) -> AuthoredSubmission:
    work = context.intake.pending_work
    assert work is not None
    attempts = []
    for i, batch in enumerate(work.batches):
        raw = encoded(
            {
                "assessments": {
                    u: {
                        "support": "uncertain",
                        "evidence": [],
                        "reason": "Authored fixture 🔑 ``` </script>. No semantic conclusion.",
                    }
                    for u in batch.unit_ids
                }
            }
        ).decode("utf-8")
        attempts.append(
            AuthoredAttempt(
                fixture_id=f"authored-{i}",
                batch_id=batch.batch_id,
                local_input_bytes_sha256=hashlib.sha256(
                    fixture_input(context, batch.batch_id)
                ).hexdigest(),
                raw_final=raw,
            )
        )
    return AuthoredSubmission(
        contract="assessment-authored-submission-1",
        origin="authored_fixture",
        authored_by="Authored test operator",
        source=context.pin,
        attempts=tuple(attempts),
    )
