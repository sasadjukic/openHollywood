"""Offline v2 presentation admission to the unchanged OpenAI wire protocol mapper."""

from __future__ import annotations

from open_hollywood_engine.evaluations.assessment_compact_presentation import render_compact
from open_hollywood_engine.evaluations.assessment_completion import CompletionContext
from open_hollywood_engine.evaluations.assessment_result import AssessmentScope
from open_hollywood_engine.evaluations.review_evidence import require
from open_hollywood_engine.models.assessment_openai import WireMapping, _prepare_wire
from open_hollywood_engine.models.contracts import ModelRequest
from open_hollywood_engine.models.openai_catalog import OpenAIModelSpec
from open_hollywood_engine.secrets import SecretLeakGuard


def prepare_compact_wire(
    context: CompletionContext,
    scope: AssessmentScope,
    request: ModelRequest,
    spec: OpenAIModelSpec,
    *,
    guard: SecretLeakGuard | None = None,
) -> WireMapping:
    """Regenerate v2 from original native context; arbitrary replacement messages are refused."""
    presentation = render_compact(context, scope.batch_id).presentation
    require(
        [{"role": m.role.value, "content": m.content} for m in request.messages]
        == [m.model_dump(mode="json") for m in presentation.messages],
        "compact_wire_messages",
    )
    work = context.intake.pending_work
    require(work is not None, "compact_wire_no_work")
    assert work is not None
    # Shared protocol record/serializer only. This does not call the v1 presentation entry point.
    return _prepare_wire(work, scope, request, spec, guard=guard)
