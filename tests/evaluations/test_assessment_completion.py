"""The authored envelope composes native bindings without claiming model or edit authority."""

from __future__ import annotations

import json
from dataclasses import replace
from typing import Any

import pytest
from open_hollywood_engine.evaluations.assessment_completion import (
    AuthoredSubmission,
    derive,
    encoded,
    fixture_input,
    parse_submission,
    render_completion,
)

from tests.authored_completion_fixtures import authored_context, submission_for


def test_full_context_multibatch_binding_is_unassessed_and_literal() -> None:
    context = authored_context()
    submission = submission_for(context)
    assert parse_submission(encoded(submission.model_dump(mode="json"))) == submission
    envelope = derive(context, submission)
    assert envelope["intake"] == context.intake.model_dump(mode="json")
    completion = envelope["completion"]
    assert isinstance(completion, dict)
    assert completion["complete_delivery"] and completion["binding"] == "complete"
    assert completion["completed_batches"] == completion["delivered_units"] == 2
    assert completion["unknown_usage_attempts"] == 2
    assert envelope["origin"] == "authored_fixture" and not envelope["model_evidence"]
    assert envelope["usage_applicability"] == "not_applicable_no_inference"
    for flag in ("writer_dispatch_authorized", "semantic_interpretation_verified"):
        assert envelope[flag] is False
    for label in (
        "factual_support",
        "evidence_adequacy",
        "edit_necessity",
        "editorial_effect",
        "craft",
    ):
        assert envelope[label] == "unassessed"
    assert sum(f.status == "hold" for f in context.intake.findings) == 2
    assert sum(f.status == "not_selected" for f in context.intake.findings) == 2
    assert context.intake.assessment_result is context.intake.completion_receipt is None
    view = render_completion(envelope)
    fence = "````"
    assert json.loads(view.split(fence + "json\n")[1].rsplit("\n" + fence, 1)[0]) == envelope
    assert context.intake.pending_work is not None
    for attempt in submission.attempts:
        local = json.loads(fixture_input(context, attempt.batch_id))
        assert local["provider_request"] is local["model_input"] is False
        assert local["work"] == context.intake.pending_work.model_dump(mode="json")


@pytest.mark.parametrize(
    "field",
    [
        "origin",
        "authenticated",
        "completion",
        "binding",
        "usage",
        "writer_dispatch_authorized",
    ],
)
def test_caller_cannot_supply_authority(field: str) -> None:
    obj = submission_for(authored_context()).model_dump(mode="json")
    obj[field] = "authenticated_model_delivery" if field == "origin" else True
    with pytest.raises(ValueError):
        parse_submission(encoded(obj))


@pytest.mark.parametrize("field", ["contract", "origin", "authored_by"])
def test_discriminators_and_author_must_be_explicit(field: str) -> None:
    obj = submission_for(authored_context()).model_dump(mode="json")
    obj.pop(field)
    with pytest.raises(ValueError):
        parse_submission(encoded(obj))


@pytest.mark.parametrize(
    "change",
    [
        "missing_batch",
        "duplicate_batch",
        "duplicate_fixture",
        "wrong_input",
        "wrong_raw",
        "missing_unit",
        "extra_unit",
        "bad_evidence",
        "intake_bytes",
        "manifest_bytes",
        "unchecked_origin",
        "source_pin",
        "declaration_pin",
        "brief_pin",
        "source_origin",
    ],
)
def test_stale_or_incomplete_work_never_becomes_a_publication(change: str) -> None:
    context = authored_context()
    submission = submission_for(context)
    obj: dict[str, Any] = submission.model_dump(mode="json")
    if change == "missing_batch":
        obj["attempts"].pop()
    elif change == "duplicate_batch":
        obj["attempts"].append(obj["attempts"][0])
    elif change == "duplicate_fixture":
        obj["attempts"][1]["fixture_id"] = obj["attempts"][0]["fixture_id"]
    elif change == "wrong_input":
        obj["attempts"][0]["local_input_bytes_sha256"] = "f" * 64
    elif change == "wrong_raw":
        obj["attempts"][0]["raw_final"] = "{"
    elif change in ("missing_unit", "extra_unit", "bad_evidence"):
        rows = json.loads(obj["attempts"][0]["raw_final"])["assessments"]
        unit = next(iter(rows))
        if change == "missing_unit":
            rows.pop(unit)
        elif change == "extra_unit":
            rows["Q999"] = rows[unit]
        else:
            rows[unit]["evidence"] = ["operator-provenance-not-visible-authority"]
        obj["attempts"][0]["raw_final"] = json.dumps({"assessments": rows})
    elif change == "intake_bytes":
        context = replace(context, exact_intake=context.exact_intake + b" ")
    elif change == "manifest_bytes":
        context = replace(context, exact_manifest=context.exact_manifest + b" ")
    elif change == "unchecked_origin":
        submission = submission.model_copy(update={"origin": "authenticated_model_delivery"})
    else:
        key = {
            "source_pin": "source_canonical_sha256",
            "declaration_pin": "declarations_canonical_sha256",
            "brief_pin": "briefs_canonical_sha256",
            "source_origin": "source_origin",
        }[change]
        obj["source"][key] = "saved_review" if change == "source_origin" else "f" * 64
    with pytest.raises(ValueError):
        candidate = submission if change == "unchecked_origin" else parse_submission(encoded(obj))
        derive(context, candidate)


@pytest.mark.parametrize(
    "kind",
    [
        "duplicate_top",
        "duplicate_nested",
        "invalid_utf8",
        "large_submission",
        "large_final",
        "receipt",
    ],
)
def test_strict_submission_parser(kind: str) -> None:
    obj = submission_for(authored_context()).model_dump(mode="json")
    data = encoded(obj)
    if kind == "duplicate_top":
        data = b'{"origin":"authored_fixture",' + data[1:]
    elif kind == "duplicate_nested":
        data = data.replace(b'"batch_id":', b'"batch_id":"other", "batch_id":', 1)
    elif kind == "invalid_utf8":
        data = b"\xff"
    elif kind == "large_submission":
        data = b" " * (4 * 1024 * 1024 + 1)
    else:
        change: dict[str, Any] = (
            {"raw_final": "a" * 64_001} if kind == "large_final" else {"receipt": {}}
        )
        obj["attempts"][0].update(change)
        data = encoded(obj)
    with pytest.raises(ValueError):
        parse_submission(data)


def test_declared_schema_matches_required_authored_boundary() -> None:
    schema = AuthoredSubmission.model_json_schema()
    assert schema["additionalProperties"] is False
    assert set(schema["required"]) == {"contract", "origin", "authored_by", "source", "attempts"}
    assert schema["properties"]["origin"]["const"] == "authored_fixture"
