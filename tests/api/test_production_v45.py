"""Explicit claim comparisons; simulated judgments do not prove model accuracy."""

from __future__ import annotations

import json
from copy import deepcopy
from dataclasses import replace
from pathlib import Path
from typing import Any
from uuid import uuid4

import pytest
from open_hollywood_api.persistence.database import create_session_factory
from open_hollywood_api.persistence.models import AgentInvocation
from open_hollywood_api.services.production_failure_evidence import capture_review_failure
from open_hollywood_api.services.production_model_executor import (
    _Execution,
    _scene_boundary_audit,
    _StructuredOutputContractError,
)
from open_hollywood_api.services.production_revision_acceptance import critic_repair_tests
from open_hollywood_engine.evaluations import load_benchmark_corpus
from open_hollywood_engine.models import ModelRequest, ModelResponse
from sqlalchemy import Engine, select

from tests.api.test_production_v26 import _run_gateway
from tests.api.test_production_v29 import _materialize, _raw
from tests.api.test_production_v37 import _fixture
from tests.api.test_production_v41 import _linked, _revision
from tests.api.test_production_v43 import RepeatedAssignmentGateway
from tests.api.test_production_v44 import _retry
from tests.evaluations.test_agentic_blueprint import CORPUS_PATH


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


def _claim(
    execution: _Execution, *, repeated: bool = False, severity: str = "major"
) -> dict[str, Any]:
    raw: dict[str, Any] = _raw(execution, "craft")["issues"][0]
    raw.update(
        category="Plot Pacing",
        severity=severity,
        assignment_finding_ref="assignment:outcome" if repeated else None,
        assignment_comparison={
            "finding_refs": ["assignment:outcome"],
            "assessment": (
                "Both claims object to completing the comparison early; leaving it inconclusive "
                "repairs both. The pacing label describes a consequence of that same breach."
                if repeated
                else "Even if verification stays inconclusive, three repetitive explanations of "
                "the character's fear slow the passage. Condense them without changing the "
                "planned outcome. That prose defect survives the assignment correction."
            ),
        },
        description="The comparison finishes too early."
        if repeated
        else "Fear is explained repeatedly.",
        recommendation="Leave verification inconclusive."
        if repeated
        else "Condense the repeated explanation.",
    )
    return raw


@pytest.mark.parametrize("severity", ["note", "minor", "major", "blocking"])
def test_same_defect_at_any_severity_consolidates_without_promoting_the_craft_issue(
    severity: str,
) -> None:
    execution = _fixture()
    raw = _raw(execution, "assignment")
    raw["issues"] = [_claim(execution, repeated=True, severity=severity)]
    before = deepcopy(raw)
    result = _materialize(raw, execution)
    assert len(result["issues"]) == 1
    assert result["issues"][0]["severity"] == "blocking"  # Native assignment severity retained.
    assert raw["issues"][0]["description"] in result["issues"][0]["description"]
    audit = _scene_boundary_audit(raw, execution)
    assert audit["schema_version"] == "3"
    comparisons, repetitions = audit["assignment_comparisons"], audit["assignment_restatements"]
    assert isinstance(comparisons, list) and isinstance(repetitions, list)
    assert comparisons[0]["severity"] == repetitions[0]["severity"] == severity
    assert raw == before
    assert "assignment_comparison" not in json.dumps(result)


@pytest.mark.parametrize("same_category", [False, True])
def test_independent_claim_survives_with_same_evidence_and_severity(same_category: bool) -> None:
    execution = _fixture()
    raw = _raw(execution, "assignment")
    repeated, independent = _claim(execution, repeated=True), _claim(execution)
    if same_category:
        independent["category"] = repeated["category"]
    else:
        independent["category"] = "prose"
    raw["issues"] = [repeated, independent]
    result = _materialize(raw, execution)
    assert len(result["issues"]) == 2
    assert result["issues"][0]["description"] == independent["description"]
    assert result["issues"][0]["severity"] == "major"
    comparisons = _scene_boundary_audit(raw, execution)["assignment_comparisons"]
    assert isinstance(comparisons, list) and len(comparisons) == 2


@pytest.mark.parametrize("alias", ["assignment:outcome", "boundary"])
def test_independence_compares_consolidated_finding_once_but_does_not_skip_separate_turn(
    alias: str,
) -> None:
    execution = _revision()
    raw = _linked(execution)
    raw["issues"] = [_claim(execution)]
    raw["issues"][0]["draft_evidence_refs"] = raw["scene_boundary_check"]["draft_evidence_refs"]
    raw["issues"][0]["assignment_comparison"]["finding_refs"] = [alias]
    assert len(_materialize(raw, execution)["issues"]) == 2
    raw["assignment_violations"].append(
        {**raw["assignment_violations"][0], "anchor": "turning_point"}
    )
    with pytest.raises(_StructuredOutputContractError, match="every reported"):
        _materialize(raw, execution)
    packet = _retry(execution, raw)
    directive = next(
        d
        for d in packet["schema_repair"]["directives"]
        if "reported_assignment_finding_groups" in d
    )
    assert ["assignment:turning_point"] in directive["reported_assignment_finding_groups"]
    raw["issues"][0]["assignment_comparison"]["finding_refs"].append("assignment:turning_point")
    assert len(_materialize(raw, execution)["issues"]) == 3


@pytest.mark.parametrize(
    "bad",
    [
        "missing",
        "blank",
        "long",
        "extra",
        "unknown",
        "unreported",
        "duplicate",
        "omitted",
        "internal",
    ],
)
def test_comparison_errors_reject_without_mutating_or_silently_dropping_findings(bad: str) -> None:
    execution = _fixture()
    raw = _raw(execution, "assignment")
    raw["issues"] = [_claim(execution)]
    issue = raw["issues"][0]
    comparison = issue["assignment_comparison"]
    if bad == "missing":
        issue.pop("assignment_comparison")
    elif bad == "blank":
        comparison["assessment"] = " \n "
    elif bad == "long":
        comparison["assessment"] = "x" * 1001
    elif bad == "extra":
        comparison["invented"] = "do not drop"
    elif bad in {"unknown", "unreported"}:
        comparison["finding_refs"] = ["invented" if bad == "unknown" else "boundary"]
    elif bad == "duplicate":
        comparison["finding_refs"] *= 2
    elif bad == "omitted":
        comparison["finding_refs"] = []
    else:
        issue["_assignment_comparison"] = comparison
    before = deepcopy(raw)
    with pytest.raises(_StructuredOutputContractError):
        _materialize(raw, execution)
    assert raw == before


def test_no_assignment_findings_still_requires_an_explicit_empty_comparison() -> None:
    execution = _fixture()
    raw = _raw(execution, "craft")
    assert len(_materialize(raw, execution)["issues"]) == 1
    raw["issues"][0].pop("assignment_comparison")
    with pytest.raises(_StructuredOutputContractError):
        _materialize(raw, execution)


def test_repetition_comparison_must_include_its_selected_target() -> None:
    execution = _fixture()
    raw = _raw(execution, "assignment")
    raw["issues"] = [_claim(execution, repeated=True)]
    raw["issues"][0]["assignment_comparison"]["finding_refs"] = []
    with pytest.raises(_StructuredOutputContractError, match="selected restatement target"):
        _materialize(raw, execution)


def test_original_craft_and_assignment_identities_survive_even_if_current_report_is_combined() -> (
    None
):
    execution = _revision()
    original = next(a for a in execution.inputs if a["artifact_kind"] == "critique")
    original["content"]["issues"].append(
        {
            "category": "dramatic_tension",
            "severity": "major",
            "description": "Original skepticism.",
            "evidence": ["The letters matched."],
            "recommendation": "Preserve unsettled suspicion.",
        }
    )
    tests = critic_repair_tests(execution.inputs, execution.unit_id)
    raw = _linked(execution)
    raw["repair_checks"][tests[1]["test_id"]]["current_finding_refs"] = []
    repeated = _claim(execution, repeated=True)
    repeated["draft_evidence_refs"] = raw["scene_boundary_check"]["draft_evidence_refs"]
    raw["issues"] = [repeated]
    result = _materialize(raw, execution)
    assert len(result["issues"]) == 2
    review = {
        "artifact_kind": "critique",
        "artifact_key": "next",
        "artifact_version_id": str(uuid4()),
        "content": result,
    }
    assert critic_repair_tests((*execution.inputs, review), execution.unit_id) == tests
    # A combined assignment is not a back door for aliasing away a craft obligation.
    raw["repair_checks"][tests[1]["test_id"]]["current_finding_refs"] = ["issue:0"]
    with pytest.raises(_StructuredOutputContractError):
        _materialize(raw, execution)


def test_comparison_is_audited_redacted_and_never_replayed_as_retry_prose(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    secret = "v45-only-test-secret"
    monkeypatch.setenv("OLLAMA_API_KEY", secret)
    execution = _fixture()
    raw = _raw(execution, "assignment")
    raw["issues"] = [_claim(execution)]
    raw["issues"][0]["assignment_comparison"]["assessment"] = secret
    audit = _scene_boundary_audit(raw, execution)
    assert secret not in json.dumps(audit)
    raw["issues"][0]["assignment_comparison"]["finding_refs"] = []
    evidence = capture_review_failure(
        operation="critique",
        response_content=json.dumps(raw),
        request_content="{}",
        input_version_ids=(),
        validation_issues=(),
    )
    assert "assignment_comparison" in json.dumps(evidence) and secret not in json.dumps(evidence)
    retry = _retry(execution, raw)
    assert secret not in json.dumps(retry)
    assert "Fear is explained" not in json.dumps(retry["schema_repair"])


class ComparedClaimsGateway(RepeatedAssignmentGateway):
    async def generate(self, request: ModelRequest) -> ModelResponse:
        response = await super().generate(request)
        payload = json.loads(request.messages[-1].content)
        assignment = payload.get("assignment", {})
        if assignment.get("operation") != "critique" or assignment["revision_number"] != 1:
            return response
        raw = json.loads(response.content)
        raw["issues"][0]["severity"] = "major"
        raw["issues"][0]["assignment_comparison"]["assessment"] = (
            "Both reports concern the absent turn and require restoring that turn."
        )
        distinct = deepcopy(raw["issues"][0])
        refs = [f"assignment:{v['anchor']}" for v in raw["assignment_violations"]]
        distinct.update(
            category="prose",
            assignment_finding_ref=None,
            description="Separate repeated explanation.",
            recommendation="Condense repetition.",
            assignment_comparison={
                "finding_refs": refs,
                "assessment": "Restoring the turn leaves repeated explanations; condense them.",
            },
        )
        raw["issues"].append(distinct)
        return replace(response, content=json.dumps(raw))


@pytest.mark.anyio
@pytest.mark.parametrize("original_unmet", [False, True])
async def test_writer_receives_one_assignment_repair_and_one_distinct_craft_repair(
    original_unmet: bool, migrated_database_path: Path, database_engine: Engine
) -> None:
    prompt = load_benchmark_corpus(CORPUS_PATH).prompts[0]
    gateway = ComparedClaimsGateway(prompt.prompt, prompt, original_unmet=original_unmet)
    result = await _run_gateway(gateway, migrated_database_path, database_engine)
    assert len(result.result.accepted_units) == 3
    packets = [json.loads(r.messages[-1].content) for r in gateway.requests]
    writers = [
        p
        for p in packets
        if p.get("assignment", {}).get("operation") == "write"
        and p["assignment"]["revision_number"] > 0
    ]
    old = writers[0]["revision_contract"]["critic_acceptance_tests"]
    following = writers[1]["revision_contract"]["critic_acceptance_tests"]
    assert len(following) == 3 and following[0] == old[0]
    assert {t["category"] for t in following[1:]} == {"prose", "scene_assignment:turning_point"}
    critic = next(
        p
        for p in packets
        if p.get("assignment", {}).get("operation") == "critique"
        and p["assignment"]["revision_number"] == 2
    )
    assert critic["repair_acceptance_tests"] == following
    with create_session_factory(database_engine)() as session:
        audits = [
            i.request_settings["scene_boundary_audit"]
            for i in session.scalars(select(AgentInvocation))
            if i.request_settings.get("scene_boundary_audit", {}).get("assignment_comparisons")
        ]
        assert len(audits) == 1 and len(audits[0]["assignment_comparisons"]) == 2
