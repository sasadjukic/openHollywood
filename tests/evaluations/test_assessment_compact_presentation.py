"""Source-bound version-two presentation, exact reconstruction and no semantic credit."""

from __future__ import annotations

import json
from dataclasses import replace
from typing import Any

import pytest
from open_hollywood_engine.evaluations.assessment_compact_presentation import (
    CompactBundle,
    compact,
    parse_bundle,
    reconstruct,
    render_compact,
    validate_compact,
)
from open_hollywood_engine.evaluations.assessment_completion import encoded
from open_hollywood_engine.evaluations.assessment_presentation import render_presentation
from open_hollywood_engine.evaluations.assessment_result import (
    bind_assessment_result,
    scope_for_batch,
)
from open_hollywood_engine.evaluations.assessment_work import AssessmentReceipt, complete_work
from open_hollywood_engine.evaluations.contracts import canonical_sha256
from open_hollywood_engine.evaluations.review_evidence import text_hash

from tests.authored_completion_fixtures import authored_context


def test_complete_native_binding_preserves_whole_work_and_unchanged_schema() -> None:
    context = authored_context()
    before = context.intake.model_dump_json()
    work = context.intake.pending_work
    assert work is not None
    receipts, expected = [], {}
    for batch in work.batches:
        original = render_presentation(context, batch.batch_id)
        bundle = render_compact(context, batch.batch_id)
        assert validate_compact(context, bundle) == bundle
        assert reconstruct(bundle) == original
        assert bundle.presentation.response_schema == original.response_schema
        packet = json.loads(bundle.presentation.messages[1].content)
        assert packet["native_work_view"]["context"]["messages"] == [
            m.model_dump(mode="json") for m in work.context.messages
        ]
        assert "hidden_start" not in bundle.presentation.messages[1].content
        assert "hidden_start" in bundle.local_provenance.document.content_json
        assert len(packet["whole_intake_dispositions"]) == len(context.intake.findings)
        request_hash = canonical_sha256(bundle.presentation.model_dump(mode="json"))
        assert request_hash != canonical_sha256(original.model_dump(mode="json"))
        expected[batch.batch_id] = request_hash
        scope = scope_for_batch(work, batch.batch_id, request_hash)
        raw = encoded(
            {
                "assessments": {
                    u: {
                        "support": "uncertain",
                        "evidence": ["E0001"],
                        "reason": "Authored binding fixture only.",
                    }
                    for u in batch.unit_ids
                }
            }
        ).decode()
        receipt = AssessmentReceipt(
            attempt_id="fixture-" + batch.batch_id,
            work_sha256=work.fingerprint,
            batch_id=batch.batch_id,
            request_sha256=request_hash,
            status="valid",
            assessed_unit_ids=batch.unit_ids,
            result_sha256=text_hash(raw),
            active_seconds=0,
            input_tokens=None,
            output_tokens=None,
            binding="unresolved",
        )
        bound = bind_assessment_result(work, scope, receipt, raw)
        assert bound.support == bound.evidence_adequacy == bound.craft == "unassessed"
        assert not bound.writer_dispatch_authorized
        receipts.append(bound.receipt)
    done = complete_work(work, tuple(receipts), expected)
    assert done.complete_delivery and done.binding == "complete"
    assert done.support == "unassessed" and not done.writer_dispatch_authorized
    assert context.intake.model_dump_json() == before


@pytest.mark.parametrize(
    "mutation",
    [
        "quote",
        "version",
        "hash",
        "pointer",
        "source",
        "duplicate",
        "missing",
        "row_shape",
        "columns",
        "local_ref",
        "local_body",
        "scope",
        "brief",
        "claim",
        "disposition",
        "message",
        "schema",
        "system",
        "roles",
        "origin",
        "extra",
        "packet_digest",
    ],
)
def test_drift_rejected_even_with_rehashed_messages(mutation: str) -> None:
    context = authored_context()
    candidate: dict[str, Any] = render_compact(context, "batch-001").model_dump(mode="json")
    p = candidate["presentation"]
    packet = json.loads(p["messages"][1]["content"])
    documents = packet["native_work_view"]["context"]["documents"]
    rows = documents[3]["whole_field_locations"]
    if mutation == "quote":
        documents[1]["structured_content"]["prose"] += "changed"
    elif mutation == "version":
        documents[0]["version"] = "other"
    elif mutation == "hash":
        documents[0]["content_sha256"] = "0" * 64
    elif mutation == "pointer":
        rows[0][2] = rows[1][2]
    elif mutation == "source":
        rows[0][1] = documents[4]["identity"]
    elif mutation == "duplicate":
        rows[1][0] = rows[0][0]
    elif mutation == "missing":
        rows.pop()
    elif mutation == "row_shape":
        rows[0].append("extra")
    elif mutation == "columns":
        documents[3]["columns"].reverse()
    elif mutation == "local_ref":
        documents[4]["content_sha256"] = "0" * 64
    elif mutation == "local_body":
        candidate["local_provenance"]["document"]["content_json"] += " "
    elif mutation == "scope":
        packet["original_scope_declarations"]["declarations"].clear()
    elif mutation == "brief":
        packet["original_work_briefs"]["briefs"].clear()
    elif mutation == "claim":
        packet["active_unit_ids"] = ["Q999"]
    elif mutation == "disposition":
        packet["whole_intake_dispositions"].pop()
    elif mutation == "message":
        packet["native_work_view"]["context"]["messages"][0]["content"] = "x"
    elif mutation == "schema":
        p["response_schema"] = {"type": "object"}
        p["schema_canonical_sha256"] = canonical_sha256(p["response_schema"])
    elif mutation == "system":
        p["messages"][0]["content"] += "new task"
    elif mutation == "roles":
        p["messages"][0]["role"] = "user"
    elif mutation == "origin":
        p["live_authorized"] = True
    elif mutation == "extra":
        candidate["model_evidence"] = True
    else:
        p["original_packet_bytes_sha256"] = "0" * 64
    p["messages"][1]["content"] = compact(packet)
    p["messages_canonical_sha256"] = canonical_sha256(p["messages"])
    with pytest.raises((ValueError, KeyError)):
        validate_compact(context, parse_bundle(encoded(candidate)))


@pytest.mark.parametrize("mutation", ["pin", "snapshot", "batch", "duplicate_json", "oversize"])
def test_trusted_context_and_parser_boundary(mutation: str) -> None:
    context = authored_context()
    if mutation == "duplicate_json":
        with pytest.raises(ValueError):
            parse_bundle(b'{"contract":1,"contract":2}')
        return
    if mutation == "oversize":
        with pytest.raises(ValueError):
            parse_bundle(b" " * (16 * 1024 * 1024 + 1))
        return
    if mutation == "pin":
        context = replace(
            context, pin=context.pin.model_copy(update={"work_canonical_sha256": "0" * 64})
        )
    elif mutation == "snapshot":
        context = replace(context, exact_intake=b"{}")
    with pytest.raises(ValueError):
        render_compact(context, "other" if mutation == "batch" else "batch-001")


def test_self_consistent_changed_schema_still_requires_context_validation() -> None:
    context = authored_context()
    original = render_compact(context, "batch-001")
    candidate = original.model_dump(mode="json")
    candidate["presentation"]["response_schema"] = {"type": "object"}
    candidate["presentation"]["schema_canonical_sha256"] = canonical_sha256({"type": "object"})
    changed = CompactBundle.model_validate_json(encoded(candidate))
    reconstruct(changed)  # A self-consistent local bundle is not external authentication.
    with pytest.raises(ValueError, match="authenticated_context"):
        validate_compact(context, changed)


@pytest.mark.parametrize("kind", ["paragraph", "partial", "serialization", "scope_kind"])
def test_unqualified_document_layout_refused_before_presentation(
    kind: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    from open_hollywood_engine.evaluations import assessment_compact_presentation as domain

    context = authored_context()
    original = render_presentation(context, "batch-001")
    packet = json.loads(original.messages[1].content)
    documents = packet["full_original_work"]["context"]["documents"]
    if kind in ("paragraph", "partial"):
        registry = json.loads(documents[3]["content_json"])
        registry["entries"][0]["paragraph" if kind == "paragraph" else "start"] = 1
        documents[3]["content_json"] = json.dumps(registry, ensure_ascii=False, sort_keys=True)
        documents[3]["content_sha256"] = text_hash(documents[3]["content_json"])
    elif kind == "serialization":
        documents[0]["content_json"] += " "
        documents[0]["content_sha256"] = text_hash(documents[0]["content_json"])
    else:
        documents[4]["identity"] = "additional-story-authority"
    messages = (
        original.messages[0],
        original.messages[1].model_copy(update={"content": encoded(packet).decode()}),
    )
    # Fault injection at the already-verified v1 renderer boundary, never an archive trust override.
    monkeypatch.setattr(
        domain, "render_presentation", lambda *_: original.model_copy(update={"messages": messages})
    )
    with pytest.raises(ValueError):
        domain.render_compact(context, "batch-001")


def test_schema_artifacts_match_runtime() -> None:
    from pathlib import Path

    from open_hollywood_engine.evaluations.assessment_compact_presentation import (
        CompactPresentation,
    )

    root = Path(__file__).resolve().parents[2]
    for name, model in (
        ("assessment-compact-bundle-2", CompactBundle),
        ("assessment-intake-presentation-2", CompactPresentation),
    ):
        assert (
            json.loads((root / "docs/contracts" / (name + ".schema.json")).read_bytes())
            == model.model_json_schema()
        )
