"""Mandatory-check routing tests use simulated judgments, not live semantic evidence."""

from __future__ import annotations

import json
from copy import deepcopy
from dataclasses import replace
from pathlib import Path
from typing import Any

import pytest
from open_hollywood_api.persistence.database import create_session_factory
from open_hollywood_api.persistence.models import AgentInvocation
from open_hollywood_api.services.production_failure_evidence import capture_review_failure
from open_hollywood_api.services.production_model_executor import (
    _Operation,
    _output_schema,
    _StructuredOutputContractError,
)
from open_hollywood_engine.evaluations import load_benchmark_corpus
from open_hollywood_engine.models import ModelDeployment, ModelRequest, ModelResponse
from sqlalchemy import Engine, select

from tests.api.test_production_v26 import V26Gateway, _run_gateway
from tests.api.test_production_v29 import _materialize, _raw, _refs
from tests.api.test_production_v31 import _review
from tests.api.test_production_v37 import _fixture, _payload
from tests.api.test_production_v41 import _revision
from tests.api.test_production_v46 import _retry_execution
from tests.evaluations.test_agentic_blueprint import CORPUS_PATH
from tests.evaluations.test_agentic_production import ProductionFixtureGateway
from tests.repair_condition_fixtures import condition_fixture_for_request
from tests.repair_condition_fixtures import (
    fixture_boundary_audit as _scene_boundary_audit,
)


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


def _unmet(raw: dict[str, Any], anchor: str) -> None:
    raw["assignment_checks"][anchor].update(
        status="unmet",
        assessment=f"Simulated independent failure of {anchor} in the cited current passage.",
        recommended_resolution=f"Restore only the assigned {anchor}.",
    )


@pytest.mark.parametrize("deployment", [ModelDeployment.LOCAL, ModelDeployment.CLOUD])
@pytest.mark.parametrize(
    "anchors", [(), ("turning_point",), ("outcome",), ("turning_point", "outcome")]
)
def test_only_populated_approved_obligations_are_required(
    deployment: ModelDeployment, anchors: tuple[str, ...]
) -> None:
    execution = _fixture()
    execution = replace(execution, selection=replace(execution.selection, deployment=deployment))
    for anchor in ("turning_point", "outcome"):
        if anchor not in anchors:
            execution.inputs[0]["content"][anchor] = None
    before = deepcopy(execution.inputs)
    schema = _output_schema(
        _Operation.CRITIQUE,
        continuity_schema_variant=None,
        critic_execution=execution,
        critic_evidence_refs=tuple(_refs(execution)),
    )
    assert "assignment_checks" in schema["required"]
    checks = schema["properties"]["assignment_checks"]
    assert checks["required"] == list(anchors)
    assert checks["additionalProperties"] is False
    for check in checks["properties"].values():
        met, unmet = check["anyOf"]
        assert met["properties"]["recommended_resolution"] == {"type": "null"}
        assert unmet["properties"]["recommended_resolution"] == {"type": "null"}
        assert set(met["required"]) == {
            "status",
            "assessment",
            "draft_evidence_refs",
            "recommended_resolution",
        }
        assert met["properties"]["draft_evidence_refs"]["items"] == {
            "$ref": "#/$defs/CriticDraftEvidenceReference"
        }
    remaining = schema["properties"]["assignment_violations"]
    assert not set(anchors) & set(remaining["items"]["properties"]["anchor"]["enum"])
    result = _materialize(_raw(execution), execution)
    assert result["verdict"] == "pass" and "assignment_checks" not in result
    assert execution.inputs == before


@pytest.mark.parametrize("unmet", [("turning_point",), ("outcome",), ("turning_point", "outcome")])
@pytest.mark.parametrize("old_status", ["met", "unmet"])
def test_each_unmet_obligation_blocks_independently_of_scores_boundary_and_old_repairs(
    unmet: tuple[str, ...], old_status: str
) -> None:
    execution = _revision()
    raw = _review(execution, old_status)
    for anchor in unmet:
        _unmet(raw, anchor)
    original = deepcopy(raw)
    result = _materialize(raw, execution)
    assert result["verdict"] == "revise" and result["overall_score"] == 5
    for anchor in unmet:
        assert any(
            issue["category"] == f"scene_assignment:{anchor}"
            and issue["severity"] == "blocking"
            and raw["assignment_checks"][anchor]["assessment"] in issue["description"]
            for issue in result["issues"]
        )
    if old_status == "met":
        assert len(result["issues"]) == len(unmet)
    assert raw == original


@pytest.mark.parametrize(
    "bad",
    [
        "omitted",
        "missing_turn",
        "unexpected",
        "blank",
        "long",
        "status",
        "extra",
        "missing_field",
        "met_repair",
        "unmet_no_repair",
        "unmet_blank_repair",
        "stale",
        "empty_evidence",
        "duplicate_evidence",
        "prose_evidence",
        "legacy_route",
    ],
)
def test_invalid_checks_never_become_manuscript_findings(bad: str) -> None:
    execution = _fixture()
    raw = _raw(execution)
    check = raw["assignment_checks"]["turning_point"]
    if bad == "omitted":
        del raw["assignment_checks"]
    elif bad == "missing_turn":
        del raw["assignment_checks"]["turning_point"]
    elif bad == "unexpected":
        raw["assignment_checks"]["exit_state"] = deepcopy(check)
    elif bad in ("blank", "long"):
        check["assessment"] = " " if bad == "blank" else "x" * 601
    elif bad == "status":
        check["status"] = "uncertain"
    elif bad == "extra":
        check["extra"] = "undeclared"
    elif bad == "missing_field":
        del check["recommended_resolution"]
    elif bad == "met_repair":
        check["recommended_resolution"] = "Not applicable"
    elif bad.startswith("unmet_"):
        check.update(
            status="unmet", recommended_resolution=None if bad.endswith("no_repair") else " "
        )
    elif bad == "stale":
        check["draft_evidence_refs"] = _refs(_fixture())[:1]
    elif bad == "empty_evidence":
        check["draft_evidence_refs"] = []
    elif bad == "duplicate_evidence":
        check["draft_evidence_refs"] *= 2
    elif bad == "prose_evidence":
        check["draft_evidence_refs"] = ["Elara decides to examine the letter."]
    elif bad == "legacy_route":
        raw["assignment_violations"] = [
            {
                "anchor": "turning_point",
                "explanation": "Do not accept a duplicate route.",
                "draft_evidence_refs": _refs(execution)[:1],
                "recommended_resolution": "Restore the turn.",
            }
        ]
    with pytest.raises(_StructuredOutputContractError):
        _materialize(raw, execution)


def test_retry_specifies_exact_applicable_fields_without_rejected_allegations() -> None:
    execution = _fixture()
    raw = _raw(execution)
    raw["assignment_checks"]["turning_point"] = "Rejected allegation must stay out of retry input."
    retry = _retry_execution(execution, raw)
    packet = _payload(_Operation.CRITIQUE, retry)
    repair = packet["schema_repair"]
    assert repair["policy_version"] == "20"
    directive = next(
        d for d in repair["directives"] if d["location"].startswith("assignment_checks")
    )
    assert directive["required_checks"] == ["turning_point", "outcome"]
    for field in ("status", "assessment", "draft_evidence_refs", "recommended_resolution"):
        assert field in directive["action"]
    assert "Rejected allegation" not in json.dumps(packet)
    assert _materialize(_raw(execution), retry)["verdict"] == "pass"


def test_audit_records_both_checks_with_exact_sources_and_redacts_failed_capture(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("OLLAMA_API_KEY", "v49-test-only-secret-value")
    execution = _fixture()
    raw = _raw(execution)
    raw["assignment_checks"]["turning_point"]["assessment"] = "v49-test-only-secret-value"
    _unmet(raw, "outcome")
    audit = _scene_boundary_audit(raw, execution)
    assert audit["schema_version"] == "7"
    assert audit["candidate_version_id"] == execution.inputs[1]["artifact_version_id"]
    assert audit["current_plan_version_id"] == execution.inputs[0]["artifact_version_id"]
    checks = audit["assignment_checks"]
    assert isinstance(checks, dict) and set(checks) == {"turning_point", "outcome"}
    assert "v49-test-only-secret-value" not in json.dumps(audit)
    captured = capture_review_failure(
        operation="critique",
        response_content=json.dumps(raw),
        request_content=json.dumps(_payload(_Operation.CRITIQUE, execution)),
        input_version_ids=tuple(str(v) for v in execution.input_version_ids),
        validation_issues=(),
    )
    assert captured is not None and not captured["manuscript_defect_established"]
    assert len(captured["attempted_review"]["assignment_checks"]) == 2
    assert "v49-test-only-secret-value" not in json.dumps(captured)


class MandatoryCheckGateway(V26Gateway):
    initial_reviews = 0

    async def generate(self, request: ModelRequest) -> ModelResponse:
        response = await ProductionFixtureGateway.generate(self, request)
        payload = json.loads(request.messages[-1].content)
        assignment = payload.get("assignment", {})
        if (
            assignment.get("operation") == "critique"
            and assignment["unit_number"] == 1
            and assignment["revision_number"] == 0
        ):
            self.initial_reviews += 1
            raw = json.loads(response.content)
            if self.mode == "unmet_turn":
                _unmet(raw, "turning_point")
            elif self.initial_reviews == 1:
                del raw["assignment_checks"]["turning_point"]
            else:
                assert payload["retry_context"]["manuscript_defect_established"] is False
                assert payload["schema_repair"]["policy_version"] == "20"
            response = replace(
                response, content=json.dumps(condition_fixture_for_request(raw, request))
            )
        return response


@pytest.mark.anyio
@pytest.mark.parametrize("mode", ["unmet_turn", "missing_check"])
async def test_persisted_unmet_turn_reaches_writer_but_missing_check_only_retries_review(
    mode: str, migrated_database_path: Path, database_engine: Engine
) -> None:
    prompt = load_benchmark_corpus(CORPUS_PATH).prompts[0]
    gateway = MandatoryCheckGateway(prompt.prompt, prompt, mode=mode)
    result = await _run_gateway(gateway, migrated_database_path, database_engine)
    assert len(result.result.accepted_units) == 3
    payloads = [json.loads(r.messages[-1].content) for r in gateway.requests]
    writes = [p for p in payloads if p.get("assignment", {}).get("operation") == "write"]
    assert len(writes) == (4 if mode == "unmet_turn" else 3)
    if mode == "unmet_turn":
        revised = next(p for p in writes if p["assignment"]["revision_number"] == 1)
        tests = revised["revision_contract"]["critic_acceptance_tests"]
        assert len(tests) == 1 and tests[0]["category"] == "scene_assignment:turning_point"
        critic = next(
            p
            for p in payloads
            if p.get("assignment", {}).get("operation") == "critique"
            and p["assignment"]["revision_number"] == 1
        )
        assert critic["repair_acceptance_tests"] == tests
    with create_session_factory(database_engine)() as session:
        critics = [
            i
            for i in session.scalars(select(AgentInvocation)).all()
            if i.specialist_role == "scene_critic"
        ]
        failed = [i for i in critics if not i.schema_validation_succeeded]
        assert len(failed) == (1 if mode == "missing_check" else 0)
        for invocation in critics:
            if invocation.schema_validation_succeeded:
                assert invocation.request_settings["scene_boundary_audit"]["schema_version"] == "7"
                assert "assignment_checks" not in invocation.output_versions[0].content
            else:
                assert not invocation.output_versions
