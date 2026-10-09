"""Regressions for Repeat 3's stale recheck and incomplete coverage responses."""

from __future__ import annotations

import json
from copy import deepcopy
from dataclasses import replace
from pathlib import Path
from typing import Any
from uuid import uuid4

import pytest
from open_hollywood_api.persistence.database import create_session_factory
from open_hollywood_api.persistence.models import AgentInvocation, ArtifactVersion, RunStatus
from open_hollywood_api.services.production_model_executor import (
    _continuity_model_findings,
    _continuity_recheck_decision_audit,
    _ContinuityModelContext,
    _ContinuitySchemaVariant,
    _materialize_continuity_finding,
    _materialize_requirement_coverage,
    _messages,
    _Operation,
    _output_schema,
    _StructuredOutputContractError,
)
from open_hollywood_engine.artifacts import ContinuityFinding
from open_hollywood_engine.evaluations import load_benchmark_corpus
from open_hollywood_engine.models import ModelDeployment, ModelRequest, ModelResponse
from open_hollywood_engine.workflows import SceneProductionError
from sqlalchemy import Engine, select

from tests.api.test_production_v26 import V26Gateway, _run_gateway
from tests.evaluations.test_agentic_blueprint import CORPUS_PATH
from tests.evaluations.test_agentic_production import (
    ProductionFixtureGateway,
    _schema_test_continuity_context,
    _v17_catalog_test_execution,
)


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


def _history_context(*, active: bool = False) -> _ContinuityModelContext:
    context = _schema_test_continuity_context(recheck=True)
    original: dict[str, Any] = {
        "artifact_version_id": str(uuid4()),
        "content": {
            "findings": [{"id": "old_conflict", "severity": "blocking", "basis": "contradiction"}]
        },
    }
    latest = {
        "artifact_version_id": str(uuid4()),
        "content": {"findings": deepcopy(original["content"]["findings"]) if active else []},
    }
    return replace(
        context, previous_continuity_report=latest, continuity_history=(original, latest)
    )


@pytest.mark.parametrize("deployment", list(ModelDeployment))
@pytest.mark.parametrize("active", [False, True])
def test_latest_report_alone_defines_recheck_keys(
    deployment: ModelDeployment, active: bool
) -> None:
    context = _history_context(active=active)
    before = deepcopy(context.continuity_history)
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
    assert payload["continuity_recheck"]["required_prior_finding_ids"] == (
        ["old_conflict"] if active else []
    )
    assert payload["continuity_history"][0]["findings"][0]["id"] == "old_conflict"
    if active:
        assert schema["properties"]["prior_finding_rechecks"]["required"] == ["old_conflict"]
    else:
        assert "prior_finding_rechecks" not in schema["properties"]
        assert "prior_finding_rechecks" not in schema["required"]
        assert "PriorFindingRecheckEntry" not in schema["$defs"]
        assert payload["original_allegation_ledger"] == []
    if deployment is ModelDeployment.CLOUD:
        assert payload["output_schema"] == schema
    else:
        assert payload["output_schema_delivery"] == "enforced_by_local_gateway"
    assert context.continuity_history == before


@pytest.mark.parametrize("empty", [{}, {"prior_finding_rechecks": {}}])
def test_empty_current_partition_is_application_owned_and_auditable(empty: dict[str, Any]) -> None:
    context = _history_context()
    raw = {**empty, "new_findings": []}
    assert _continuity_model_findings(raw, context) == []
    assert (
        _continuity_recheck_decision_audit(
            raw, context, materialized_blocking_finding_ids=frozenset()
        )
        == ()
    )


@pytest.mark.parametrize("prior", [None, [], {"old_conflict": {"status": "still_blocking"}}])
def test_stale_or_malformed_partition_is_never_silently_discarded(prior: object) -> None:
    context = _history_context()
    raw: dict[str, Any] = {"prior_finding_rechecks": prior, "new_findings": []}
    with pytest.raises(_StructuredOutputContractError, match="prior finding audit"):
        _continuity_model_findings(raw, context)
    with pytest.raises(_StructuredOutputContractError):
        _continuity_recheck_decision_audit(
            raw, context, materialized_blocking_finding_ids=frozenset()
        )


def test_active_finding_cannot_be_omitted_or_released_without_current_evidence() -> None:
    context = _history_context(active=True)
    incomplete: tuple[dict[str, Any], ...] = (
        {"new_findings": []},
        {"new_findings": [], "prior_finding_rechecks": {}},
    )
    for raw in incomplete:
        with pytest.raises(_StructuredOutputContractError, match="prior finding audit"):
            _continuity_model_findings(raw, context)
    decision = {
        "status": "resolved",
        "resolution_assessment": "The prior claim is repaired.",
        "revised_draft_evidence_refs": [],
    }
    raw = {"new_findings": [], "prior_finding_rechecks": {"old_conflict": decision}}
    with pytest.raises(_StructuredOutputContractError):
        _continuity_model_findings(raw, context)
    decision["revised_draft_evidence_refs"] = ["draft_evidence_0001"]
    assert _continuity_model_findings(raw, context) == []


def _coverage(*, status: str = "absent", refs: object = ()) -> dict[str, Any]:
    # OH-V01-010's original gap had an assessment and explicit [], but no summary.
    return {
        "status": status,
        "coverage_assessment": "The draft does not explicitly mention the time of day.",
        "recommended_resolution": "Add a brief atmospheric reference to the night setting.",
        "evidence_refs": list(refs) if isinstance(refs, tuple) else refs,
    }


@pytest.mark.parametrize("recheck", [False, True])
@pytest.mark.parametrize(
    "status,enforcement,blocking",
    [("absent", "advisory", False), ("absent", "blocking", True), ("partial", "blocking", False)],
)
def test_gap_summary_comes_from_assessment_without_changing_gate(
    recheck: bool, status: str, enforcement: str, blocking: bool
) -> None:
    context = replace(
        _schema_test_continuity_context(recheck=recheck),
        requirement_enforcement={"required_element_1": enforcement},
    )
    entry = _coverage(status=status, refs=("draft_evidence_0001",) if status == "partial" else ())
    before = deepcopy(entry)
    findings = _materialize_requirement_coverage(
        {"requirement_coverage": {"required_element_1": entry}}, context
    )
    result = ContinuityFinding.model_validate(
        _materialize_continuity_finding(findings[0], "scene_1")
    )
    assert result.summary == entry["coverage_assessment"]
    assert result.blocks_approval is blocking
    assert result.coverage_evidence == (
        ("Mara pockets the brass key.",) if status == "partial" else ()
    )
    assert entry == before


@pytest.mark.parametrize("status", ["met", "partial", "absent"])
@pytest.mark.parametrize(
    "bad", ["omitted", None, "draft_evidence_0001", ["draft_evidence_9999"], [None]]
)
def test_coverage_never_invents_or_defaults_evidence(status: str, bad: object) -> None:
    entry = _coverage(status=status, refs=bad)
    if bad == "omitted":
        entry.pop("evidence_refs")
    with pytest.raises(_StructuredOutputContractError) as error:
        _materialize_requirement_coverage(
            {"requirement_coverage": {"required_element_1": entry}},
            _schema_test_continuity_context(),
        )
    assert error.value.location == "requirement_coverage.required_element_1.evidence_refs"
    assert error.value.issue_type == "requirement_coverage_evidence_invalid"


@pytest.mark.parametrize("field", ["coverage_assessment", "recommended_resolution"])
@pytest.mark.parametrize("bad", [None, "", "  ", 7])
def test_missing_coverage_text_points_to_model_response_field(field: str, bad: object) -> None:
    entry = _coverage()
    entry[field] = bad
    with pytest.raises(_StructuredOutputContractError) as error:
        _materialize_requirement_coverage(
            {"requirement_coverage": {"required_element_1": entry}},
            _schema_test_continuity_context(),
        )
    assert error.value.location == f"requirement_coverage.required_element_1.{field}"


def test_coverage_schema_removes_duplicate_summary_and_search_decision() -> None:
    schema = _output_schema(
        _Operation.CONTINUITY,
        continuity_schema_variant=_ContinuitySchemaVariant.INITIAL_CHECK,
        continuity_model_context=_schema_test_continuity_context(),
    )
    for branch in schema["$defs"]["RequirementCoverageEntry"]["anyOf"]:
        assert "evidence_refs" in branch["required"]
        assert not {"summary", "evidence_search_result"} & set(branch["properties"])


class ContinuityContractGateway(V26Gateway):
    """Exercise real durable history, repair and audit paths with simulated judgments."""

    def __init__(self, *args: Any, mode: str) -> None:
        super().__init__(*args, mode=mode)
        self.target_calls = 0

    async def generate(self, request: ModelRequest) -> ModelResponse:
        payload = json.loads(request.messages[-1].content)
        assignment = payload.get("assignment", {})
        operation = assignment.get("operation")
        scene_two = assignment.get("unit_number") == 2
        revision = assignment.get("revision_number")
        if self.mode == "history" and operation == "continuity" and scene_two and revision == 0:
            return await super().generate(request)
        response = await ProductionFixtureGateway.generate(self, request)
        raw = json.loads(response.content)
        if self.mode == "history" and scene_two:
            if operation == "critique" and revision == 1:
                raw["verdict"] = "revise"
                raw["issues"] = [
                    {
                        "category": "pacing",
                        "severity": "major",
                        "description": "The conflict needs one more consequential exchange.",
                        "recommendation": "Make the exchange change the decision.",
                        "draft_evidence_refs": [
                            next(
                                item
                                for item in payload["input_artifacts"]
                                if item["artifact_kind"] == "scene_draft"
                            )["content"]["evidence_catalog"][0]["evidence_ref"]
                        ],
                    }
                ]
            if operation == "continuity" and revision == 2:
                assert payload["continuity_history"][0]["findings"]
                assert payload["continuity_recheck"]["required_prior_finding_ids"] == []
                raw.pop("prior_finding_rechecks")
                self.target_calls += 1
        elif operation == "continuity" and scene_two:
            self.target_calls += 1
            raw["requirement_coverage"]["scene_plan_time_context"] = _coverage()
            if self.mode == "invalid_always" or (
                self.mode == "invalid_once" and self.target_calls == 1
            ):
                raw["requirement_coverage"]["scene_plan_time_context"].pop("evidence_refs")
            if self.target_calls == 2:
                assert payload["schema_repair"]["focus_locations"] == [
                    "requirement_coverage.scene_plan_time_context.evidence_refs"
                ]
                assert "never omit it" in payload["schema_repair"]["directives"][0]["action"]
        return replace(response, content=json.dumps(raw))


@pytest.mark.anyio
@pytest.mark.parametrize("mode", ["history", "coverage", "invalid_once", "invalid_always"])
async def test_durable_continuity_contract_replay_and_bounded_repair(
    mode: str, migrated_database_path: Path, database_engine: Engine
) -> None:
    prompt = load_benchmark_corpus(CORPUS_PATH).prompts[0]
    gateway = ContinuityContractGateway(prompt.prompt, prompt, mode=mode)
    if mode == "invalid_always":
        with pytest.raises(SceneProductionError):
            await _run_gateway(gateway, migrated_database_path, database_engine)
    else:
        result = await _run_gateway(gateway, migrated_database_path, database_engine)
        assert result.status is RunStatus.SUCCEEDED
        assert len(result.result.accepted_units) == 3
        assert result.result.accepted_units[1].revision_cycles_used == (
            2 if mode == "history" else 0
        )
    assert gateway.target_calls == (2 if mode.startswith("invalid") else 1)
    sessions = create_session_factory(database_engine)
    with sessions() as session:
        calls = session.scalars(select(AgentInvocation)).all()
        failures = [call for call in calls if call.error_code]
        assert len(failures) == {"invalid_once": 1, "invalid_always": 2}.get(mode, 0)
        for call in failures:
            capture = call.request_settings["review_failure_evidence"]
            assert capture["manuscript_defect_established"] is False
            assert capture["status"] == "unvalidated_review_response"
        if mode == "history":
            final_call = next(
                call
                for call in calls
                if call.request_settings.get("operation") == "continuity"
                and call.prompt_text is not None
                and json.loads(call.prompt_text.rsplit("\n\n", 1)[1])["assignment"][
                    "revision_number"
                ]
                == 2
            )
            assert final_call.request_settings["prompt_template_version"] == "42"
        elif mode != "invalid_always":
            reports = session.scalars(select(ArtifactVersion)).all()
            gap = next(
                finding
                for report in reports
                for finding in report.content.get("findings", [])
                if finding.get("requirement_id") == "scene_plan_time_context"
            )
            assert gap["summary"] == _coverage()["coverage_assessment"]
            assert gap["severity"] == "warning" and not gap["blocks_approval"]
