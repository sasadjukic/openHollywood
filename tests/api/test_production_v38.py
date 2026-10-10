"""Required scene-boundary evidence, hard gates and review-only repair behavior."""

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
    _Operation,
    _output_schema,
    _scene_boundary_audit,
    _StructuredOutputContractError,
)
from open_hollywood_engine.evaluations import load_benchmark_corpus
from open_hollywood_engine.models import ModelDeployment, ModelRequest, ModelResponse
from sqlalchemy import Engine, select

from tests.api.test_production_v26 import V26Gateway, _run_gateway
from tests.api.test_production_v29 import _materialize, _raw, _refs
from tests.api.test_production_v37 import _fixture, _payload
from tests.evaluations.test_agentic_blueprint import CORPUS_PATH
from tests.evaluations.test_agentic_production import ProductionFixtureGateway


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.mark.parametrize("deployment", [ModelDeployment.LOCAL, ModelDeployment.CLOUD])
@pytest.mark.parametrize("has_endpoint", [True, False])
def test_schema_requires_comparison_and_exact_evidence_even_for_no_overrun(
    deployment: ModelDeployment, has_endpoint: bool
) -> None:
    execution = _fixture()
    execution = replace(
        execution,
        selection=replace(execution.selection, deployment=deployment),
    )
    if not has_endpoint:
        execution.inputs[0]["content"].update(outcome=None, turning_point=None)
    schema = _output_schema(
        _Operation.CRITIQUE,
        continuity_schema_variant=None,
        critic_execution=execution,
        critic_evidence_refs=tuple(_refs(execution)),
    )
    assert "scene_boundary_check" in schema["required"]
    check = schema["properties"]["scene_boundary_check"]
    assert set(check["required"]) == set(_raw(execution)["scene_boundary_check"])
    assert check["properties"]["status"]["enum"] == (
        ["no_overrun", "overrun"] if has_endpoint else ["no_overrun"]
    )
    assert check["properties"]["draft_evidence_refs"]["items"] == {
        "$ref": "#/$defs/CriticDraftEvidenceReference"
    }
    assert schema["$defs"]["CriticDraftEvidenceReference"]["enum"] == _refs(execution)
    assert not {"target_artifact_kind", "target_artifact_key", "target_artifact_version_id"} & set(
        schema["properties"]
    )
    assert not {"target_artifact_kind", "target_artifact_key", "target_artifact_version_id"} & set(
        schema["required"]
    )


@pytest.mark.parametrize(
    "change",
    [
        {"status": "aligned"},
        {"achieved_state": " "},
        {"achieved_state": 5},
        {"current_endpoint_comparison": ""},
        {"next_scene_comparison": "x" * 601},
        {"unexpected": "field"},
        {"draft_evidence_refs": []},
        {"draft_evidence_refs": ["old-draft-handle"]},
        {"draft_evidence_refs": "prose"},
    ],
)
def test_invalid_comparisons_are_review_errors_not_manuscript_issues(
    change: dict[str, object],
) -> None:
    execution = _fixture()
    raw = _raw(execution)
    raw["scene_boundary_check"].update(change)
    original = deepcopy(raw)
    with pytest.raises(_StructuredOutputContractError) as failure:
        _materialize(raw, execution)
    assert failure.value.location.startswith("scene_boundary_check")
    assert raw == original and not raw["issues"]


@pytest.mark.parametrize("status", ["no_overrun", "overrun"])
def test_missing_duplicate_and_stale_evidence_cannot_pass(status: str) -> None:
    execution = _fixture()
    raw = _raw(execution)
    del raw["scene_boundary_check"]
    with pytest.raises(_StructuredOutputContractError, match="achieved_state"):
        _materialize(raw, execution)
    raw = _raw(execution)
    raw["scene_boundary_check"]["status"] = status
    raw["scene_boundary_check"]["draft_evidence_refs"] *= 2
    with pytest.raises(_StructuredOutputContractError, match="distinct"):
        _materialize(raw, execution)
    raw = _raw(execution)
    raw["scene_boundary_check"]["status"] = status
    execution.inputs[1]["artifact_version_id"] = str(uuid4())
    with pytest.raises(_StructuredOutputContractError, match="current-draft"):
        _materialize(raw, execution)


def test_overrun_alone_overrides_pass_and_perfect_scores_through_assignment_gate() -> None:
    execution = _fixture(
        "Elara decides to check. She compares the journal and establishes a match."
    )
    raw = _raw(execution)
    raw["scene_boundary_check"].update(
        achieved_state="She has verified the handwriting through a journal comparison.",
        current_endpoint_comparison="The plan ends at deciding to verify; the draft goes further.",
        next_scene_comparison="It completes the distinct verification assigned to scene 2.",
        draft_evidence_refs=[_refs(execution)[-1]],
        status="overrun",
    )
    assert raw["assignment_violations"] == []
    result = _materialize(raw, execution)
    assert result["overall_score"] == 5.0 and result["verdict"] == "revise"
    issue = result["issues"][0]
    assert issue["severity"] == "blocking" and issue["category"] == "scene_assignment:outcome"
    assert issue["evidence"] == ["She compares the journal and establishes a match."]
    assert "scene_2" in issue["recommendation"] and "approved overlap" in issue["recommendation"]
    assert "scene_boundary_check" not in result


def test_no_overrun_never_clears_other_hard_failures_or_implies_outcome_is_met() -> None:
    execution = _fixture("The plan was abandoned. Cora secretly knew the code.")
    for route in ("assignment", "pov", "blocking_craft"):
        result = _materialize(_raw(execution, route), execution)
        assert result["verdict"] == "revise"
        assert result["issues"][0]["severity"] == "blocking"


def test_inapplicable_overrun_rejected_even_if_provider_ignores_bound_schema() -> None:
    execution = _fixture()
    execution.inputs[0]["content"].update(outcome=None, turning_point=None)
    raw = _raw(execution)
    raw["scene_boundary_check"]["status"] = "overrun"
    with pytest.raises(_StructuredOutputContractError) as failure:
        _materialize(raw, execution)
    assert failure.value.issue_type == "inapplicable_scene_boundary_overrun"


def test_audit_and_failed_capture_bind_sources_redact_and_stay_outside_canon(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    secret = "test-only-boundary-secret-value"
    monkeypatch.setenv("OLLAMA_API_KEY", secret)
    execution = _fixture()
    raw = _raw(execution)
    raw["scene_boundary_check"]["achieved_state"] = f"Simulated state {secret}"
    audit = _scene_boundary_audit(raw, execution)
    assert secret not in json.dumps(audit)
    assert audit["candidate_version_id"] == execution.inputs[1]["artifact_version_id"]
    assert audit["current_plan_version_id"] == execution.inputs[0]["artifact_version_id"]
    reservation = audit["next_scene"]
    assert isinstance(reservation, dict)
    assert reservation["blueprint_version_id"] == execution.inputs[-1]["artifact_version_id"]
    raw["scene_boundary_check"]["extra"] = "do not retain this"
    captured = capture_review_failure(
        operation="critique",
        response_content=json.dumps(raw),
        request_content=json.dumps(_payload(_Operation.CRITIQUE, execution)),
        input_version_ids=tuple(str(v) for v in execution.input_version_ids),
        validation_issues=(
            {"type": "invalid_scene_boundary_check", "loc": "scene_boundary_check"},
        ),
    )
    assert captured is not None
    assert captured["manuscript_defect_established"] is False
    assert secret not in json.dumps(captured) and "do not retain this" not in json.dumps(captured)
    assert "achieved_state" in captured["attempted_review"]["scene_boundary_check"]


class ComparisonGateway(V26Gateway):
    def __init__(self, *args: Any, mode: str) -> None:
        super().__init__(*args, mode=mode)
        self.initial_reviews = 0

    async def generate(self, request: ModelRequest) -> ModelResponse:
        response = await ProductionFixtureGateway.generate(self, request)
        payload = json.loads(request.messages[-1].content)
        assignment = payload.get("assignment", {})
        if (
            assignment.get("operation") == "critique"
            and assignment.get("unit_number") == 1
            and assignment.get("revision_number") == 0
        ):
            self.initial_reviews += 1
            raw = json.loads(response.content)
            if self.mode == "overrun":
                raw["scene_boundary_check"]["status"] = "overrun"
            elif self.initial_reviews == 1:
                del raw["scene_boundary_check"]
            else:
                assert payload["retry_context"]["manuscript_defect_established"] is False
                assert payload["schema_repair"]["policy_version"] == "13"
            response = replace(response, content=json.dumps(raw))
        return response


@pytest.mark.anyio
@pytest.mark.parametrize("mode", ["overrun", "missing_once"])
async def test_persisted_comparison_audit_distinguishes_prose_revision_from_review_retry(
    mode: str, migrated_database_path: Path, database_engine: Engine
) -> None:
    prompt = load_benchmark_corpus(CORPUS_PATH).prompts[0]
    gateway = ComparisonGateway(prompt.prompt, prompt, mode=mode)
    result = await _run_gateway(gateway, migrated_database_path, database_engine)
    assert len(result.result.accepted_units) == 3
    payloads = [json.loads(r.messages[-1].content) for r in gateway.requests]
    writes = [p for p in payloads if p.get("assignment", {}).get("operation") == "write"]
    assert len(writes) == (4 if mode == "overrun" else 3)
    assert gateway.initial_reviews == (1 if mode == "overrun" else 2)
    with create_session_factory(database_engine)() as session:
        invocations = session.scalars(select(AgentInvocation)).all()
        critics = [i for i in invocations if i.specialist_role == "scene_critic"]
        successful = [i for i in critics if i.schema_validation_succeeded]
        assert len(successful) == (4 if mode == "overrun" else 3)
        for invocation in successful:
            audit = invocation.request_settings["scene_boundary_audit"]
            inputs = {str(v.id) for v in invocation.input_versions}
            assert audit["candidate_version_id"] in inputs
            assert audit["current_plan_version_id"] in inputs
            if audit["next_scene"]:
                assert audit["next_scene"]["blueprint_version_id"] in inputs
            assert "scene_boundary_check" not in invocation.output_versions[0].content
        failures = [i for i in critics if not i.schema_validation_succeeded]
        assert len(failures) == (1 if mode == "missing_once" else 0)
        if failures:
            assert not failures[0].output_versions
            assert "scene_boundary_audit" not in failures[0].request_settings
