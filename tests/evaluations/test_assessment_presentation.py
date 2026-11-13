"""Original native identity and batch-specific diagnostic presentation remain distinct."""

from __future__ import annotations

import json
from dataclasses import replace

import pytest
from open_hollywood_engine.evaluations.assessment_presentation import render_presentation
from open_hollywood_engine.models.assessment_openai_manifest import Settings, make_request_set
from open_hollywood_engine.models.openai_catalog import builtin_model_specs

from tests.authored_completion_fixtures import authored_context


def settings() -> Settings:
    return Settings(
        contract="assessment-openai-rehearsal-settings-1",
        model_spec=builtin_model_specs()["gpt-6.1-sol"],
        reasoning="high",
        max_input_tokens=24000,
        max_output_tokens=32000,
        max_cost_usd="0.60",
        max_transport_seconds=600,
        live_authorized=False,
    )


def test_full_original_work_and_holds_preserved_without_rebinding_native_identity() -> None:
    context = authored_context()
    before = context.intake.model_dump_json()
    work = context.intake.pending_work
    assert work is not None
    assert context.intake.declarations is not None and context.intake.briefs is not None
    plan = make_request_set(context, "test", settings(), "a" * 64)
    assert plan == make_request_set(context, "test", settings(), "a" * 64)
    assert plan.payload.count_attempt_limit == plan.payload.generation_attempt_limit == 2
    for manifest, batch in zip(plan.payload.requests, work.batches, strict=True):
        presentation = manifest.payload.presentation
        packet = json.loads(presentation.messages[1].content)
        assert packet["full_original_work"] == work.model_dump(mode="json")
        assert packet["original_scope_declarations"] == context.intake.declarations.model_dump(
            mode="json"
        )
        assert packet["original_work_briefs"] == context.intake.briefs.model_dump(mode="json")
        assert packet["whole_intake_dispositions"] == [
            f.model_dump(mode="json") for f in context.intake.findings
        ]
        assert presentation.active_unit_ids == batch.unit_ids
        assert presentation.messages != work.context.messages
        assert "six whole" not in presentation.messages[0].content
        count, gen = [json.loads(e.body_utf8) for e in manifest.payload.endpoints]
        assert (
            count["input"]
            == gen["input"]
            == [m.model_dump(mode="json") for m in presentation.messages]
        )
        assert set(
            gen["text"]["format"]["schema"]["properties"]["assessments"]["properties"]
        ) == set(batch.unit_ids)
    assert context.intake.model_dump_json() == before
    assert all(
        m.payload.source.work_canonical_sha256 == work.fingerprint for m in plan.payload.requests
    )


@pytest.mark.parametrize("changed", ["snapshot", "pin", "batch", "settings"])
def test_presentation_drift_or_live_promotion_refused(changed: str) -> None:
    context = authored_context()
    batch = "batch-001"
    if changed == "snapshot":
        context = replace(context, exact_intake=b"{}")
    elif changed == "pin":
        context = replace(
            context, pin=context.pin.model_copy(update={"work_canonical_sha256": "b" * 64})
        )
    elif changed == "batch":
        batch = "not-a-batch"
    else:
        with pytest.raises(ValueError):
            Settings.model_validate_json(
                settings().model_copy(update={"live_authorized": True}).model_dump_json()
            )
        return
    with pytest.raises(ValueError):
        render_presentation(context, batch)
