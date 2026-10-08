"""Inactive historical repair advice must not become a current review instruction."""

from __future__ import annotations

import json
from copy import deepcopy
from dataclasses import replace
from pathlib import Path
from typing import Any, cast

import pytest
from open_hollywood_api.persistence.database import create_session_factory
from open_hollywood_api.persistence.models import ArtifactVersion, RunStatus
from open_hollywood_api.services.production_model_executor import (
    _bounded_continuity_history_entry,
    _ContinuitySchemaVariant,
    _messages,
    _Operation,
    _output_schema,
)
from open_hollywood_engine.evaluations import load_benchmark_corpus
from open_hollywood_engine.models import ModelDeployment, ModelRequest, ModelResponse
from sqlalchemy import Engine, select

from tests.api.test_production_v26 import _run_gateway
from tests.api.test_production_v34 import ContinuityContractGateway
from tests.api.test_production_v35 import _recurrence
from tests.evaluations.test_agentic_blueprint import CORPUS_PATH
from tests.evaluations.test_agentic_production import _v17_catalog_test_execution


@pytest.mark.parametrize("latest_severity", [None, "warning", "error", "blocking"])
@pytest.mark.parametrize("basis", ["contradiction", "missing_requirement"])
def test_only_current_blockers_retain_historical_repair_direction(
    latest_severity: str | None, basis: str
) -> None:
    context, _ = _recurrence(active=latest_severity is not None)
    original, latest = context.continuity_history
    original["content"]["findings"][0].update(basis=basis, recheck_disposition="still_blocking")
    if latest_severity is not None:
        latest["content"]["findings"][0].update(severity=latest_severity, basis=basis)
    before = deepcopy(context)
    unfiltered = _bounded_continuity_history_entry(original)
    filtered = _bounded_continuity_history_entry(
        original, active_finding_ids=context.prior_blocking_finding_ids
    )
    if latest_severity in {"error", "blocking"}:
        assert filtered == unfiltered
    else:
        expected = deepcopy(unfiltered)
        entry = cast(list[dict[str, object]], expected["findings"])[0]
        entry.pop("recommended_resolution")
        entry.pop("recheck_disposition")
        entry["active_in_latest_report"] = False
        assert filtered == expected
    assert context == before
    # Adjudication still uses the unfiltered history projection.
    assert _bounded_continuity_history_entry(original) == unfiltered


@pytest.mark.parametrize("deployment", list(ModelDeployment))
def test_mixed_review_history_preserves_active_repairs_and_canonical_context(
    deployment: ModelDeployment,
) -> None:
    context, _ = _recurrence(active=True)
    original, latest = context.continuity_history
    inactive = deepcopy(original["content"]["findings"][0])
    inactive.update(id="cleared_conflict", recommended_resolution="Obsolete repair direction.")
    original["content"]["findings"].append(inactive)
    before = deepcopy(context)
    execution = _v17_catalog_test_execution()
    execution = replace(execution, selection=replace(execution.selection, deployment=deployment))
    schema = _output_schema(
        _Operation.CONTINUITY,
        continuity_schema_variant=_ContinuitySchemaVariant.RECHECK,
        continuity_model_context=context,
    )
    messages = _messages(
        _Operation.CONTINUITY,
        execution,
        schema,
        continuity_schema_variant=_ContinuitySchemaVariant.RECHECK,
        continuity_model_context=context,
    )
    payload = json.loads(messages[-1].content)
    active, historical = payload["continuity_history"][0]["findings"]
    assert active["recommended_resolution"] == "Preserve the established non-return."
    assert historical["active_in_latest_report"] is False
    assert "Obsolete repair direction." not in messages[-1].content
    assert payload["previous_continuity_report"] == latest
    assert payload["continuity_recheck"]["required_prior_finding_ids"] == ["original_key_conflict"]
    assert [item["finding_id"] for item in payload["original_allegation_ledger"]] == [
        "original_key_conflict"
    ]
    assert payload["original_allegation_ledger"][0]["original_requested_repair_not_canon"] == (
        "Preserve the established non-return."
    )
    assert payload["candidate_draft"] == context.candidate_draft
    assert payload["contradiction_claim_catalog"] == list(context.contradiction_claim_catalog)
    assert payload["world_rule_catalog"] == list(context.world_rule_catalog)
    assert payload["requirement_coverage_catalog"] == list(context.requirement_catalog)
    assert context == before


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


class HistoryProjectionGateway(ContinuityContractGateway):
    def __init__(self, *args: Any) -> None:
        super().__init__(*args, mode="history")
        self.original_repair = ""
        self.projected = False

    async def generate(self, request: ModelRequest) -> ModelResponse:
        response = await super().generate(request)
        payload = json.loads(request.messages[-1].content)
        assignment = payload.get("assignment", {})
        if assignment.get("operation") == "continuity" and assignment.get("unit_number") == 2:
            if assignment["revision_number"] == 0:
                self.original_repair = json.loads(response.content)["findings"][0][
                    "recommended_resolution"
                ]
            elif assignment["revision_number"] == 2:
                entry = payload["continuity_history"][0]["findings"][0]
                assert entry["active_in_latest_report"] is False
                assert "recommended_resolution" not in entry
                assert self.original_repair not in request.messages[-1].content
                self.projected = True
        return response


@pytest.mark.anyio
async def test_durable_history_keeps_original_advice_while_current_review_omits_it(
    migrated_database_path: Path, database_engine: Engine
) -> None:
    prompt = load_benchmark_corpus(CORPUS_PATH).prompts[0]
    gateway = HistoryProjectionGateway(prompt.prompt, prompt)
    result = await _run_gateway(gateway, migrated_database_path, database_engine)
    assert result.status is RunStatus.SUCCEEDED
    assert gateway.projected and gateway.target_calls == 1
    with create_session_factory(database_engine)() as session:
        artifacts = session.scalars(select(ArtifactVersion)).all()
        assert any(
            finding.get("recommended_resolution") == gateway.original_repair
            for artifact in artifacts
            for finding in artifact.content.get("findings", [])
        )
