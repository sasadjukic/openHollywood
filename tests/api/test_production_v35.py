"""Inactive historical allegations cannot bypass the revision evidence boundary."""

from __future__ import annotations

import json
from copy import deepcopy
from dataclasses import replace
from pathlib import Path
from typing import Any, cast
from uuid import uuid4

import pytest
from open_hollywood_api.persistence.database import create_session_factory
from open_hollywood_api.persistence.models import AgentInvocation, RunStatus
from open_hollywood_api.services.production_model_executor import (
    _ContinuityModelContext,
    _materialize_continuity_finding,
    _materialize_continuity_identity,
    _StructuredOutputContractError,
    _validate_new_recheck_contradiction_evidence,
)
from open_hollywood_engine.evaluations import load_benchmark_corpus
from open_hollywood_engine.models import ModelRequest, ModelResponse
from open_hollywood_engine.workflows import SceneProductionError
from sqlalchemy import Engine, select

from tests.api.test_production_v26 import _run_gateway
from tests.api.test_production_v34 import ContinuityContractGateway
from tests.evaluations.test_agentic_blueprint import CORPUS_PATH
from tests.evaluations.test_agentic_production import _schema_test_continuity_context


def _recurrence(*, active: bool = False) -> tuple[_ContinuityModelContext, dict[str, Any]]:
    base = _schema_test_continuity_context(recheck=True)
    claim_id = base.canonical_claim_ids[0]
    finding: dict[str, Any] = {
        "category": "fact",
        "severity": "blocking",
        "summary": "Mara returns the brass key despite its established non-return.",
        "basis": "contradiction",
        "canonical_claim_ids": [claim_id],
        "revised_evidence": ["Mara returns the brass key."],
        "repair_assessment": "The incompatible assertion remains.",
        "recommended_resolution": "Preserve the established non-return.",
    }
    original = {
        **finding,
        "id": "original_key_conflict",
        "canonical_source_refs": [base.canonical_claim_source_refs[claim_id]],
    }
    original.pop("canonical_claim_ids")
    history = {"artifact_version_id": str(uuid4()), "content": {"findings": [original]}}
    latest = {
        "artifact_version_id": str(uuid4()),
        "content": {"findings": [deepcopy(original)] if active else []},
    }
    context = replace(
        base,
        previous_continuity_report=latest,
        continuity_history=(history, latest),
        previous_candidate_draft={"content": {"prose": "Mara returns the brass key."}},
    )
    return context, finding


@pytest.mark.parametrize("allegation", ["same", "differently_worded"])
@pytest.mark.parametrize("severity", ["error", "blocking"])
def test_inactive_recurrence_with_unchanged_evidence_cannot_block(
    allegation: str, severity: str
) -> None:
    context, raw = _recurrence()
    raw["severity"] = severity
    if allegation == "differently_worded":
        raw["summary"] = "The key comes back despite its established absence."
    before = deepcopy((context, raw))
    finding = cast(dict[str, Any], _materialize_continuity_identity(raw, context, index=0))
    if allegation == "same":
        # The historical ID/disposition survive; neither may grant active status.
        assert finding["id"] == "original_key_conflict"
        assert finding["recheck_disposition"] == "still_blocking"
    else:
        assert finding["recheck_disposition"] == "newly_exposed"
    with pytest.raises(_StructuredOutputContractError) as error:
        _validate_new_recheck_contradiction_evidence([finding], context)
    assert error.value.issue_type == "new_contradiction_not_new_to_revision"
    assert (context, raw) == before


def test_active_original_blocker_retains_unchanged_evidence() -> None:
    context, raw = _recurrence(active=True)
    raw["prior_finding_id"] = "original_key_conflict"
    finding = cast(dict[str, Any], _materialize_continuity_identity(raw, context, index=0))
    _validate_new_recheck_contradiction_evidence([finding], context)
    persisted = cast(dict[str, Any], _materialize_continuity_finding(finding, "scene_1"))
    assert persisted["blocks_approval"] is True
    assert persisted["recheck_disposition"] == "still_blocking"


@pytest.mark.parametrize("keep_unchanged_excerpt", [False, True])
def test_reintroduced_changed_assertion_keeps_its_blocking_identity(
    keep_unchanged_excerpt: bool,
) -> None:
    context, raw = _recurrence()
    context = replace(
        context,
        previous_candidate_draft={"content": {"prose": "Mara waits beside the door."}},
    )
    if keep_unchanged_excerpt:
        raw["revised_evidence"].insert(0, "Mara waits beside the door.")
    finding = cast(dict[str, Any], _materialize_continuity_identity(raw, context, index=0))
    _validate_new_recheck_contradiction_evidence([finding], context)
    persisted = cast(dict[str, Any], _materialize_continuity_finding(finding, "scene_1"))
    assert persisted["id"] == "original_key_conflict"
    assert persisted["blocks_approval"] is True


def test_old_identity_cannot_be_presented_as_an_active_recheck() -> None:
    context, raw = _recurrence()
    raw["prior_finding_id"] = "original_key_conflict"
    with pytest.raises(_StructuredOutputContractError, match="exact prior blocking finding"):
        _materialize_continuity_identity(raw, context, index=0)


@pytest.mark.parametrize("case", ["initial", "world_rule", "forbidden_shortcut", "advisory"])
def test_revision_guard_does_not_change_independent_finding_routes(case: str) -> None:
    context, raw = _recurrence()
    if case == "initial":
        context = replace(context, previous_candidate_draft=None)
    elif case == "world_rule":
        raw["category"] = "world_rule"
    elif case == "forbidden_shortcut":
        raw["basis"] = "forbidden_shortcut_violation"
    else:
        raw.update(severity="warning", basis=None)
    before = deepcopy(raw)
    _validate_new_recheck_contradiction_evidence([raw], context)
    assert raw == before


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


class RecurrenceGateway(ContinuityContractGateway):
    """A simulated cleared blocker returns after a different critic revision."""

    def __init__(self, *args: Any, always_invalid: bool) -> None:
        super().__init__(*args, mode="history")
        self.always_invalid = always_invalid
        self.original: dict[str, Any] = {}

    async def generate(self, request: ModelRequest) -> ModelResponse:
        response = await super().generate(request)
        payload = json.loads(request.messages[-1].content)
        assignment = payload.get("assignment", {})
        if assignment.get("operation") != "continuity" or assignment.get("unit_number") != 2:
            return response
        raw = json.loads(response.content)
        if assignment["revision_number"] == 0:
            self.original = deepcopy(raw["findings"][0])
        elif assignment["revision_number"] == 2:
            assert payload["continuity_recheck"]["required_prior_finding_ids"] == []
            if self.target_calls == 2:
                assert payload["schema_repair"]["focus_locations"] == [
                    "findings.0.revised_evidence"
                ]
            if self.target_calls == 1 or self.always_invalid:
                finding = deepcopy(self.original)
                finding.pop("draft_evidence_refs")
                finding["basis_details"]["revised_draft_evidence_refs"] = [
                    payload["candidate_draft"]["content"]["evidence_catalog"][0]["evidence_ref"]
                ]
                finding["repair_assessment"] = "The original allegation returns unchanged."
                raw["new_findings"] = [finding]
        return replace(response, content=json.dumps(raw))


@pytest.mark.anyio
@pytest.mark.parametrize("always_invalid", [False, True])
async def test_inactive_recurrence_uses_existing_review_repair_not_another_writer(
    always_invalid: bool, migrated_database_path: Path, database_engine: Engine
) -> None:
    prompt = load_benchmark_corpus(CORPUS_PATH).prompts[0]
    gateway = RecurrenceGateway(prompt.prompt, prompt, always_invalid=always_invalid)
    if always_invalid:
        with pytest.raises(SceneProductionError):
            await _run_gateway(gateway, migrated_database_path, database_engine)
    else:
        result = await _run_gateway(gateway, migrated_database_path, database_engine)
        assert result.status is RunStatus.SUCCEEDED
        assert result.result.accepted_units[1].revision_cycles_used == 2
    assert gateway.target_calls == 2
    with create_session_factory(database_engine)() as session:
        calls = session.scalars(select(AgentInvocation)).all()
        failures = [call for call in calls if call.error_code]
        assert len(failures) == (2 if always_invalid else 1)
        for call in failures:
            capture = call.request_settings["review_failure_evidence"]
            assert capture["manuscript_defect_established"] is False
        writers = [
            call
            for call in calls
            if call.request_settings.get("operation") == "write"
            and call.prompt_text is not None
            and json.loads(call.prompt_text.rsplit("\n\n", 1)[1])["assignment"]["revision_number"]
            == 2
        ]
        assert len(writers) == 1
