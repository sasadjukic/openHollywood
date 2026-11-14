"""Compact admission preserves exact source messages and native response binding."""

import json
from dataclasses import replace

import pytest
from open_hollywood_engine.evaluations.assessment_compact_presentation import render_compact
from open_hollywood_engine.evaluations.assessment_presentation import render_presentation
from open_hollywood_engine.evaluations.assessment_result import scope_for_batch
from open_hollywood_engine.models.assessment_openai_compact import prepare_compact_wire
from open_hollywood_engine.models.contracts import MessageRole, ModelMessage

from tests.authored_completion_fixtures import authored_context
from tests.models.test_assessment_openai import inputs, offline

__all__ = ["offline"]


def test_shared_wire_protocol_only_compact_messages_and_original_native_schema() -> None:
    context = authored_context()
    work = context.intake.pending_work
    assert work is not None
    _, _, request, spec, _ = inputs()
    scope = scope_for_batch(work, work.batches[0].batch_id, "a" * 64)
    bundle = render_compact(context, scope.batch_id)
    presentation = bundle.presentation
    request = replace(
        request,
        messages=tuple(ModelMessage(MessageRole(m.role), m.content) for m in presentation.messages),
    )
    wire = prepare_compact_wire(context, scope, request, spec)
    count, generation = [json.loads(e.body_utf8) for e in wire.endpoints]
    assert generation["input"] == [m.model_dump(mode="json") for m in presentation.messages]
    assert count == {k: generation[k] for k in count}
    assert generation["reasoning"] == {"effort": "high"}
    assert generation["truncation"] == "disabled"
    assert generation["max_output_tokens"] == 32000
    assert wire.work_sha256 == work.fingerprint
    assert wire.schema_canonical_sha256 == presentation.schema_canonical_sha256
    assert "hidden_start" not in wire.endpoints[1].body_utf8
    assert "hidden_start" in bundle.local_provenance.document.content_json
    assert not wire.live_authorized


@pytest.mark.parametrize("change", ["v1", "edited", "schema", "scope", "provider"])
def test_version_or_native_contract_drift_refused(change: str) -> None:
    context = authored_context()
    work = context.intake.pending_work
    assert work is not None
    _, _, request, spec, _ = inputs()
    scope = scope_for_batch(work, work.batches[0].batch_id, "a" * 64)
    presentation = render_compact(context, scope.batch_id).presentation
    if change == "v1":
        presentation = render_presentation(context, scope.batch_id)  # type: ignore[assignment]
    request = replace(
        request,
        messages=tuple(ModelMessage(MessageRole(m.role), m.content) for m in presentation.messages),
    )
    if change == "edited":
        request = replace(
            request,
            messages=(
                *request.messages[:-1],
                ModelMessage(MessageRole.USER, request.messages[-1].content + " "),
            ),
        )
    elif change == "schema":
        request = replace(request, response_schema={"type": "object"})
    elif change == "scope":
        scope = scope.model_copy(update={"active_unit_ids": ("U999",)})
    elif change == "provider":
        request = replace(request, provider="other")
    with pytest.raises(ValueError):
        prepare_compact_wire(context, scope, request, spec)
