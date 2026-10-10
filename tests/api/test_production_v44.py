"""Severity-bound restatements and precise review-only structural retries."""

from __future__ import annotations

import json
from copy import deepcopy
from dataclasses import replace
from pathlib import Path
from typing import Any

import pytest
from open_hollywood_api.persistence.database import create_session_factory
from open_hollywood_api.persistence.models import AgentInvocation
from open_hollywood_api.services.production_critic_retry import critic_link_directive
from open_hollywood_api.services.production_model_executor import (
    _critic_assignment_routes,
    _critic_candidate_version_id,
    _Execution,
    _Operation,
    _output_schema,
    _structured_failure_issues,
    _StructuredOutputContractError,
)
from open_hollywood_api.services.production_revision_acceptance import critic_repair_tests
from open_hollywood_engine.evaluations import load_benchmark_corpus
from open_hollywood_engine.models import ModelDeployment, ModelRequest, ModelResponse
from sqlalchemy import Engine, select

from tests.api.test_production_v26 import _run_gateway
from tests.api.test_production_v29 import _comparison, _materialize, _raw
from tests.api.test_production_v37 import _fixture, _payload
from tests.api.test_production_v41 import LinkedRepairGateway, _linked, _revision
from tests.evaluations.test_agentic_blueprint import CORPUS_PATH


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.mark.parametrize("deployment", [ModelDeployment.LOCAL, ModelDeployment.CLOUD])
def test_restatement_schema_uses_explicit_comparison_in_both_delivery_modes(
    deployment: ModelDeployment,
) -> None:
    execution = _fixture()
    execution = replace(execution, selection=replace(execution.selection, deployment=deployment))
    schema = _output_schema(
        _Operation.CRITIQUE, continuity_schema_variant=None, critic_execution=execution
    )
    issue = schema["$defs"]["CritiqueIssue"]
    assert "anyOf" not in issue
    assert "assignment_comparison" in issue["required"]
    assert None in issue["properties"]["assignment_finding_ref"]["enum"]
    assert "assignment:outcome" in issue["properties"]["assignment_finding_ref"]["enum"]
    assert {"severity", "assignment_finding_ref"} <= set(issue["required"])
    packet = _payload(_Operation.CRITIQUE, execution)
    assert ("output_schema" in packet) == (deployment is ModelDeployment.CLOUD)


def _retry(execution: _Execution, raw: dict[str, Any]) -> dict[str, Any]:
    with pytest.raises(_StructuredOutputContractError) as failure:
        _materialize(raw, execution)
    issues = _structured_failure_issues(failure.value)
    retry = replace(
        execution,
        attempt_number=2,
        previous_failure={
            "error_code": "schema_validation_failed",
            "validation_issues": list(issues),
        },
    )
    packet = _payload(_Operation.CRITIQUE, retry)
    assert packet["schema_repair"]["policy_version"] == "12"
    assert packet["retry_context"]["manuscript_defect_established"] is False
    return packet


@pytest.mark.parametrize("severity", ["note", "minor", "major"])
def test_invalid_nonblocking_link_gets_exact_reported_choices(severity: str) -> None:
    execution = _fixture()
    raw = _raw(execution, "assignment")
    raw["issues"] = _raw(execution, "craft")["issues"]
    raw["issues"][0].update(
        severity=severity,
        assignment_finding_ref="outcome",
        assignment_comparison=_comparison("assignment:outcome"),
    )
    before = deepcopy(raw)
    packet = _retry(execution, raw)
    directive = packet["schema_repair"]["directives"][0]
    assert directive["allowed_assignment_finding_refs"] == [None, "assignment:outcome"]
    assert directive["reported_severity"] == severity
    assert "Do not escalate severity" in directive["action"]
    assert raw == before
    raw["issues"][0]["assignment_finding_ref"] = None
    assert len(_materialize(raw, execution)["issues"]) == 2


@pytest.mark.parametrize("bad_ref", ["outcome", "boundary", None])
def test_blocking_restatement_retry_lists_only_reported_valid_assignment_routes(
    bad_ref: str | None,
) -> None:
    execution = _fixture()
    raw = _raw(execution, "assignment")
    raw["issues"] = _raw(execution, "blocking_craft")["issues"]
    if bad_ref is None:
        raw["issues"][0].pop("assignment_finding_ref")
    else:
        raw["issues"][0]["assignment_finding_ref"] = bad_ref
    directives = _retry(execution, raw)["schema_repair"]["directives"]
    directive = next(d for d in directives if "allowed_assignment_finding_refs" in d)
    assert directive["allowed_assignment_finding_refs"] == [None, "assignment:outcome"]


def _two_repairs() -> tuple[_Execution, dict[str, Any]]:
    execution = _revision()
    original = next(a for a in execution.inputs if a["artifact_kind"] == "critique")
    original["content"]["issues"].append(
        {
            "category": "dramatic_tension",
            "severity": "major",
            "description": "Original tension.",
            "evidence": ["Original evidence."],
            "recommendation": "Retain uncertainty.",
        }
    )
    raw = _linked(execution)
    raw["issues"] = _raw(execution, "craft")["issues"]
    raw["issues"][0].update(
        category="dramatic tension",
        severity="major",
        assignment_finding_ref="outcome",
        assignment_comparison=_comparison("assignment:outcome"),
        description="Rejected allegation must not enter retry guidance.",
    )
    tests = critic_repair_tests(execution.inputs, execution.unit_id)
    raw["repair_checks"][tests[0]["test_id"]]["current_finding_refs"] = ["assignment:outcome"]
    raw["repair_checks"][tests[1]["test_id"]]["current_finding_refs"] = ["issue:0"]
    return execution, raw


def test_one_rejection_reports_null_category_and_missing_route_without_rejected_prose() -> None:
    execution, raw = _two_repairs()
    before = deepcopy((execution.inputs, raw))
    packet = _retry(execution, raw)
    directives = packet["schema_repair"]["directives"]
    assert len(directives) == 3
    restatement, outcome, tension = directives
    assert set(restatement["allowed_assignment_finding_refs"]) == {
        None,
        "boundary",
        "assignment:outcome",
    }
    assert outcome["expected_category"] == "scene_assignment:outcome"
    assert outcome["expected_severity"] == "blocking"
    assert outcome["all_routes_for_selected_findings"] == ["boundary", "assignment:outcome"]
    assert outcome["missing_routes"] == ["boundary"]
    assert tension["expected_category"] == "dramatic_tension"
    assert tension["expected_severity"] == "major"
    assert "Rejected allegation" not in json.dumps(packet)
    assert (execution.inputs, raw) == before
    # Corrections are made by the simulated reviewer, never by validation.
    raw["issues"][0].update(category="dramatic_tension", assignment_finding_ref=None)
    test = critic_repair_tests(execution.inputs, execution.unit_id)[0]
    raw["repair_checks"][test["test_id"]]["current_finding_refs"] = [
        "boundary",
        "assignment:outcome",
    ]
    result = _materialize(raw, execution)
    assert len(result["issues"]) == 2 and result["verdict"] == "revise"


@pytest.mark.parametrize("bad", ["met", "unknown", "duplicate", "partial", "owner"])
def test_link_failures_receive_exact_original_and_ownership_constraints(bad: str) -> None:
    execution = _revision(two_originals=bad == "owner")
    raw = _linked(execution)
    check = next(iter(raw["repair_checks"].values()))
    if bad == "met":
        check["status"] = "met"
    elif bad == "unknown":
        check["current_finding_refs"] = ["issue:99"]
    elif bad == "duplicate":
        check["current_finding_refs"] = ["boundary", "boundary"]
    elif bad == "partial":
        check["current_finding_refs"] = ["assignment:outcome"]
    directives = _retry(execution, raw)["schema_repair"]["directives"]
    precise = [d for d in directives if "expected_category" in d]
    assert precise and all(d["expected_category"] == "scene_assignment:outcome" for d in precise)
    if bad == "met":
        assert precise[0]["eligible_refs_if_independent_craft_is_retained"] == []
    if bad == "partial":
        assert precise[0]["missing_routes"] == ["boundary"]
    if bad == "owner":
        assert all(d["competing_original_test_ids"] for d in precise)


@pytest.mark.parametrize(
    "bad", ["stale", "prose_ref", "bad_severity", "bad_shape", "truncated", "extra"]
)
def test_retry_hints_cannot_replay_arbitrary_or_stale_data(bad: str) -> None:
    execution = _fixture()
    hint: dict[str, Any] = {
        "candidate": _critic_candidate_version_id(execution),
        "kind": "restatement",
        "severity": "major",
        "allowed_refs": [None],
    }
    if bad == "stale":
        hint["candidate"] = "previous-candidate"
    elif bad == "prose_ref":
        hint["allowed_refs"] = ["Invent a manuscript defect."]
    elif bad == "bad_severity":
        hint["severity"] = []
    elif bad == "bad_shape":
        hint["allowed_refs"] = [{"nested": "prose"}]
    elif bad == "extra":
        hint["rejected_allegation"] = "Invent a manuscript defect."
    encoded = "x" * 501 if bad == "truncated" else json.dumps(hint)
    result = critic_link_directive(
        {"location": "issues.0.assignment_finding_ref", "repair_hint": encoded},
        candidate_version_id=_critic_candidate_version_id(execution),
        tests=[],
        assignment_routes=_critic_assignment_routes(execution),
    )
    if bad == "extra":
        assert result is not None and "Invent" not in json.dumps(result)
    else:
        assert result is None


def test_rejected_secret_and_large_metadata_stay_out_of_bounded_retry(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    secret = "v44-rejected-only-secret"
    monkeypatch.setenv("OLLAMA_API_KEY", secret)
    execution, raw = _two_repairs()
    raw["issues"][0].update(category=secret, description=secret, assignment_finding_ref=secret)
    raw["issues"] *= 100
    with pytest.raises(_StructuredOutputContractError) as failure:
        _materialize(raw, execution)
    diagnostics = _structured_failure_issues(failure.value)
    assert len(diagnostics) <= 12
    assert all(len(value) <= 500 for item in diagnostics for value in item.values())
    assert secret not in json.dumps(diagnostics)
    packet = _retry(execution, raw)
    assert secret not in json.dumps(packet)


class LinkRetryGateway(LinkedRepairGateway):
    def __init__(self, *args: Any) -> None:
        super().__init__(*args, invalid_once=False)
        self.revision_calls = 0

    async def generate(self, request: ModelRequest) -> ModelResponse:
        response = await super().generate(request)
        payload = json.loads(request.messages[-1].content)
        assignment = payload.get("assignment", {})
        if assignment.get("operation") != "critique" or assignment["revision_number"] != 1:
            return response
        self.revision_calls += 1
        raw = json.loads(response.content)
        if self.revision_calls == 1:
            raw["issues"] = [
                {
                    "category": "tension",
                    "severity": "major",
                    "assignment_finding_ref": "outcome",
                    "assignment_comparison": _comparison("assignment:outcome"),
                    "draft_evidence_refs": raw["scene_boundary_check"]["draft_evidence_refs"],
                    "description": "Rejected reviewer allegation.",
                    "recommendation": "Keep as craft.",
                }
            ]
            for check in raw["repair_checks"].values():
                check["current_finding_refs"] = ["assignment:outcome"]
        else:
            directives = payload["schema_repair"]["directives"]
            assert any(
                set(d.get("allowed_assignment_finding_refs", []))
                == {None, "boundary", "assignment:outcome"}
                for d in directives
            )
            assert any(d.get("missing_routes") == ["boundary"] for d in directives)
            assert "Rejected reviewer allegation" not in json.dumps(payload)
        return replace(response, content=json.dumps(raw))


@pytest.mark.anyio
async def test_persisted_retry_keeps_candidate_and_writer_count_unchanged(
    migrated_database_path: Path,
    database_engine: Engine,
) -> None:
    prompt = load_benchmark_corpus(CORPUS_PATH).prompts[0]
    gateway = LinkRetryGateway(prompt.prompt, prompt)
    result = await _run_gateway(gateway, migrated_database_path, database_engine)
    assert len(result.result.accepted_units) == 3 and gateway.revision_calls == 2
    packets = [json.loads(r.messages[-1].content) for r in gateway.requests]
    writes = [p for p in packets if p.get("assignment", {}).get("operation") == "write"]
    assert len(writes) == 5  # Same two real manuscript revisions as the v41 fixture.
    revisions = [
        p
        for p in packets
        if p.get("assignment", {}).get("operation") == "critique"
        and p["assignment"]["revision_number"] == 1
    ]
    assert revisions[0]["input_artifacts"] == revisions[1]["input_artifacts"]
    with create_session_factory(database_engine)() as session:
        failed = [i for i in session.scalars(select(AgentInvocation)) if i.error_code]
        assert len(failed) == 1 and not failed[0].output_versions
        issues = failed[0].request_settings["structured_failure"]["issues"]
        assert any("repair_hint" in i for i in issues)
