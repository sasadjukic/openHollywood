"""Prospective request identity and terminal semantics; all responses are authored."""

from __future__ import annotations

import json
from dataclasses import replace

import pytest
from open_hollywood_engine.evaluations.assessment_completion import encoded
from open_hollywood_engine.evaluations.assessment_delivery import (
    complete_terminals,
    derive_terminal,
    make_request_set,
    parse_manifest,
    parse_request_set,
    parse_terminal,
)
from open_hollywood_engine.evaluations.contracts import canonical_sha256

from tests.assessment_delivery_fixtures import evidence_for
from tests.authored_completion_fixtures import authored_context, submission_for


def test_full_work_set_is_deterministic_and_complete_without_authority_promotion() -> None:
    ctx = authored_context()
    prepared = make_request_set(ctx, "test-run", "a" * 64)
    assert prepared == make_request_set(ctx, "test-run", "a" * 64)
    assert parse_request_set(encoded(prepared.model_dump(mode="json"))) == prepared
    assert prepared.payload.generation_attempt_limit == prepared.payload.count_attempt_limit == 2
    assert ctx.intake.pending_work is not None and ctx.intake.declarations is not None
    evidence = []
    for m, authored in zip(prepared.payload.requests, submission_for(ctx).attempts, strict=True):
        packet = json.loads(m.payload.presentation_utf8)
        assert packet["work"] == ctx.intake.pending_work.model_dump(mode="json")
        assert packet["declarations"] == ctx.intake.declarations.model_dump(mode="json")
        evidence.append(evidence_for(m, authored.raw_final))
        result = derive_terminal(ctx, m, m, evidence[-1])
        assert result.state == "bound_unassessed" and result.bound_result is not None
        assert not result.model_evidence and not result.writer_dispatch_authorized
        assert result.actual_billed_cost is None and result.evidence_adequacy == "unassessed"
    completion = complete_terminals(ctx, prepared.payload.requests, tuple(evidence))
    assert completion.complete_delivery and completion.binding == "complete"
    assert completion.known_input_tokens == 200  # Count estimates of 777 are not generation usage.


@pytest.mark.parametrize(
    "failure",
    [
        "length",
        "refusal",
        "unrecognized",
        "non200",
        "empty",
        "malformed",
        "duplicate",
        "missing",
        "extra",
        "citation",
        "model",
    ],
)
def test_failed_and_malformed_results_never_salvage_valid_slots(failure: str) -> None:
    ctx = authored_context()
    m = make_request_set(ctx, "test", "a" * 64).payload.requests[0]
    raw = submission_for(ctx).attempts[0].raw_final
    changes: dict[str, object] = {}
    if failure in {"length", "refusal", "unrecognized"}:
        changes["state"] = failure
    elif failure == "non200":
        changes["http_status"] = (
            500  # A complete body and valid final do not override HTTP failure.
        )
    elif failure == "model":
        changes["returned_model"] = "unexpected"
    elif failure == "empty":
        raw = ""
    elif failure == "malformed":
        raw = "{"
    elif failure == "duplicate":
        raw = raw.replace('"assessments":', '"assessments": {}, "assessments":')
    else:
        obj = json.loads(raw)
        key = next(iter(obj["assessments"]))
        if failure == "missing":
            del obj["assessments"][key]
        elif failure == "extra":
            obj["assessments"]["extra"] = obj["assessments"][key]
        else:
            obj["assessments"][key]["evidence"] = ["wrong-namespace"]
        raw = json.dumps(obj)
    result = derive_terminal(ctx, m, m, evidence_for(m, raw, **changes))
    assert result.state == "failed" and result.bound_result is None
    assert result.native_receipt is not None and result.native_receipt.binding == "unresolved"
    assert result.generation_attempts_consumed == 1


@pytest.mark.parametrize(
    "usage,state",
    [
        (
            {
                "input_tokens": None,
                "output_tokens": None,
                "reasoning_tokens": None,
                "cached_input_tokens": None,
            },
            "unknown",
        ),
        (
            {
                "input_tokens": 1,
                "output_tokens": None,
                "reasoning_tokens": None,
                "cached_input_tokens": None,
            },
            "partial",
        ),
        (
            {
                "input_tokens": 0,
                "output_tokens": 0,
                "reasoning_tokens": None,
                "cached_input_tokens": None,
            },
            "known",
        ),
    ],
)
def test_known_zero_partial_and_unknown_usage_are_distinct(
    usage: dict[str, int | None], state: str
) -> None:
    ctx = authored_context()
    m = make_request_set(ctx, "test", "a" * 64).payload.requests[0]
    result = derive_terminal(
        ctx, m, m, evidence_for(m, submission_for(ctx).attempts[0].raw_final, usage=usage)
    )
    assert result.state == "bound_unassessed" and result.usage_state == state
    assert result.generation_usage.model_dump() == usage
    assert result.actual_billed_cost is None and not result.next_dispatch_allowed


@pytest.mark.parametrize("namespace", ["count", "generation", "presentation", "set"])
def test_same_shaped_digest_does_not_replace_request_identity(namespace: str) -> None:
    ctx = authored_context()
    prepared = make_request_set(ctx, "test", "a" * 64)
    m = prepared.payload.requests[0]
    evidence = evidence_for(m, submission_for(ctx).attempts[0].raw_final)
    digest = {
        "count": m.payload.endpoints[0].body_canonical_sha256,
        "generation": m.payload.endpoints[-1].body_canonical_sha256,
        "presentation": m.payload.presentation_bytes_sha256,
        "set": prepared.payload_canonical_sha256,
    }[namespace]
    with pytest.raises(ValueError, match="wrong_manifest_namespace"):
        derive_terminal(
            ctx, m, m, evidence.model_copy(update={"request_payload_canonical_sha256": digest})
        )


@pytest.mark.parametrize(
    "field", ["source", "presentation_utf8", "settings", "active_unit_ids", "budget_slot"]
)
def test_rehashed_manifest_cannot_change_prepared_source_or_request(field: str) -> None:
    ctx = authored_context()
    m = make_request_set(ctx, "test", "a" * 64).payload.requests[0]
    data = m.model_dump(mode="json")
    values = {
        "source": {**data["payload"]["source"], "review_id": "different"},
        "presentation_utf8": "shortened",
        "settings": {"output_token_limit": 1},
        "active_unit_ids": ["different"],
        "budget_slot": 12,
    }
    data["payload"][field] = values[field]
    data["payload_canonical_sha256"] = canonical_sha256(data["payload"])
    candidate = parse_manifest(encoded(data))
    with pytest.raises(ValueError, match="manifest_source_or_request_changed"):
        derive_terminal(
            ctx, candidate, m, evidence_for(m, submission_for(ctx).attempts[0].raw_final)
        )


def test_source_bytes_duplicate_keys_and_origin_promotion_rejected() -> None:
    ctx = authored_context()
    m = make_request_set(ctx, "test", "a" * 64).payload.requests[0]
    evidence = evidence_for(m, submission_for(ctx).attempts[0].raw_final)
    with pytest.raises(ValueError, match="source_pins_changed"):
        derive_terminal(replace(ctx, exact_intake=ctx.exact_intake + b" "), m, m, evidence)
    data = encoded(evidence.model_dump(mode="json"))
    with pytest.raises(ValueError):
        parse_terminal(
            data.replace(
                b'"origin": "authored_fixture"',
                b'"origin":"authored_fixture","origin":"authored_fixture"',
            )
        )
    with pytest.raises(ValueError):
        parse_terminal(data.replace(b'"authored_fixture"', b'"authenticated_model_delivery"'))
    with pytest.raises(ValueError):
        parse_manifest(
            encoded(m.model_dump(mode="json")).replace(
                b"assessment-fixture-request-manifest-1", b"assessment-request-manifest-design-1"
            )
        )


def test_missing_duplicate_and_failed_batch_leave_work_incomplete() -> None:
    ctx = authored_context()
    manifests = make_request_set(ctx, "test", "a" * 64).payload.requests
    authored = submission_for(ctx).attempts
    good = evidence_for(manifests[0], authored[0].raw_final)
    bad = evidence_for(manifests[1], authored[1].raw_final, state="length")
    completion = complete_terminals(ctx, manifests, (good, bad))
    assert completion.completed_batches == 1 and not completion.complete_delivery
    with pytest.raises(ValueError, match="terminal_coverage"):
        complete_terminals(ctx, manifests, (good,))
    with pytest.raises(ValueError, match="duplicate_terminal"):
        complete_terminals(ctx, manifests, (good, good))
