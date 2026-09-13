"""Repair conditions are immutable review targets, not word-change heuristics."""

from __future__ import annotations

import json
from copy import deepcopy
from dataclasses import replace
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

import pytest
from open_hollywood_api.persistence.database import create_session_factory
from open_hollywood_api.persistence.models import AgentInvocation, ArtifactVersion
from open_hollywood_api.persistence.secret_policy import audit_database_export
from open_hollywood_api.services.production_model_executor import (
    _INSTRUCTIONS,
    _critic_evidence_catalog,
    _Execution,
    _messages,
    _Operation,
    _output_schema,
    _StructuredOutputContractError,
)
from open_hollywood_api.services.production_revision_acceptance import (
    compact_repair_inputs,
    critic_repair_tests,
)
from open_hollywood_engine.evaluations import load_benchmark_corpus
from open_hollywood_engine.models import ModelRequest, ModelResponse
from open_hollywood_engine.workflows import SceneProductionError
from sqlalchemy import Engine, select

from scripts.production_probe import load_probe, with_repair_history
from tests.api.test_production_v26 import V26Gateway, _run_gateway
from tests.api.test_production_v29 import _fixture, _materialize, _raw
from tests.evaluations.test_agentic_blueprint import CORPUS_PATH
from tests.evaluations.test_agentic_production import ProductionFixtureGateway


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


def _revision() -> _Execution:
    old = _fixture()
    draft = next(item for item in old.inputs if item["artifact_kind"] == "scene_draft")
    review = {
        "artifact_kind": "critique",
        "artifact_key": "critique_scene_2",
        "artifact_version_id": str(uuid4()),
        "content": _materialize(_raw(old, "pov"), old),
    }
    new = deepcopy(draft)
    new["artifact_version_id"] = str(uuid4())
    new["content"]["revision_number"] = 1
    new["content"]["prose"] = "Cora clenched her jaw; Elara read it as fear."
    inputs = tuple(new if item is draft else item for item in old.inputs) + (review, draft)
    return replace(
        old,
        inputs=inputs,
        revision_number=1,
        input_version_ids=tuple(UUID(item["artifact_version_id"]) for item in inputs),
    )


def _review(execution: _Execution, status: str = "met") -> dict[str, Any]:
    raw = _raw(execution)
    raw["repair_checks"] = {
        test["test_id"]: {
            "status": status,
            "assessment": "The current passage was compared with the original condition.",
            "draft_evidence_refs": [_critic_evidence_catalog(execution)[0]["evidence_ref"]],
        }
        for test in critic_repair_tests(execution.inputs, execution.unit_id)
    }
    return raw


def test_writer_and_critic_receive_identical_frozen_targets() -> None:
    execution = _revision()
    before = deepcopy(execution.inputs)
    packets = {}
    for operation in (_Operation.WRITE, _Operation.CRITIQUE):
        schema = _output_schema(
            operation,
            continuity_schema_variant=None,
            critic_execution=execution if operation is _Operation.CRITIQUE else None,
        )
        messages = _messages(
            operation,
            execution,
            schema,
            continuity_schema_variant=None,
            continuity_model_context=None,
        )
        packets[operation] = json.loads(messages[-1].content)
    tests = packets[_Operation.CRITIQUE]["repair_acceptance_tests"]
    assert tests == packets[_Operation.WRITE]["revision_contract"]["critic_acceptance_tests"]
    assert len(tests) == 1
    assert tests[0]["original_evidence"] == ["Cora secretly knew the spare key was gone."]
    assert tests[0]["source_draft_version_id"] != next(
        item["artifact_version_id"]
        for item in execution.inputs
        if item["artifact_kind"] == "scene_draft" and item["content"]["revision_number"] == 1
    )
    assert "qualifier" in tests[0]["accept_when"].lower()
    for packet in packets.values():
        review = next(a for a in packet["input_artifacts"] if a["artifact_kind"] == "critique")
        assert "scores" not in review["content"] and "issues" not in review["content"]
    assert execution.inputs == before


@pytest.mark.parametrize("status,verdict", [("met", "pass"), ("unmet", "revise")])
def test_recheck_controls_original_blocker_despite_perfect_craft(status: str, verdict: str) -> None:
    execution = _revision()
    result = _materialize(_review(execution, status), execution)
    assert result["verdict"] == verdict and result["overall_score"] == 5
    assert "repair_checks" not in result
    if status == "unmet":
        assert result["issues"][0]["severity"] == "blocking"
        assert result["issues"][0]["evidence"] == ["Cora clenched her jaw; Elara read it as fear."]


@pytest.mark.parametrize("bad", ["missing", "invented", "stale_evidence", "empty_assessment"])
def test_invalid_rechecks_cannot_resolve_or_create_story_findings(bad: str) -> None:
    execution = _revision()
    raw = _review(execution)
    key = next(iter(raw["repair_checks"]))
    if bad == "missing":
        raw.pop("repair_checks")
    elif bad == "invented":
        raw["repair_checks"]["invented"] = raw["repair_checks"].pop(key)
    elif bad == "stale_evidence":
        raw["repair_checks"][key]["draft_evidence_refs"] = ["old-draft-reference"]
    else:
        raw["repair_checks"][key]["assessment"] = " "
    with pytest.raises(_StructuredOutputContractError) as failure:
        _materialize(raw, execution)
    assert failure.value.issue_type.startswith("repair_test_")


def test_repeated_unmet_issue_keeps_first_target_and_evidence() -> None:
    execution = _revision()
    original_tests = critic_repair_tests(execution.inputs, execution.unit_id)
    repeated: dict[str, Any] = {
        "artifact_kind": "critique",
        "artifact_key": "critique_scene_2",
        "artifact_version_id": str(uuid4()),
        "content": _materialize(_review(execution, "unmet"), execution),
    }
    assert critic_repair_tests((*execution.inputs, repeated), execution.unit_id) == original_tests
    changed = deepcopy(repeated)
    changed["content"]["issues"][0]["description"] = "A genuinely different recorded allegation."
    tests = critic_repair_tests((*execution.inputs, changed), execution.unit_id)
    assert len(tests) == 2 and tests[0] == original_tests[0]
    promoted_inputs = deepcopy(execution.inputs)
    first = next(item for item in promoted_inputs if item["artifact_kind"] == "critique")
    first["content"]["issues"][0]["severity"] = "major"
    promoted = critic_repair_tests((*promoted_inputs, repeated), execution.unit_id)
    assert [test["severity"] for test in promoted] == ["major", "blocking"]


def test_met_test_never_overrides_an_independent_current_blocker() -> None:
    execution = _revision()
    raw = _review(execution)
    raw["issues"] = _raw(execution, "blocking_craft")["issues"]
    assert _materialize(raw, execution)["verdict"] == "revise"


class RepairGateway(V26Gateway):
    def __init__(self, *args: Any, repair_mode: str) -> None:
        super().__init__(*args, mode="repair-tests")
        self.repair_mode = repair_mode
        self.repair_calls = 0

    async def generate(self, request: ModelRequest) -> ModelResponse:
        response = await ProductionFixtureGateway.generate(self, request)
        payload = json.loads(request.messages[-1].content)
        assignment = payload.get("assignment", {})
        if assignment.get("operation") != "critique" or assignment.get("unit_number") != 1:
            return response
        raw = json.loads(response.content)
        draft = next(
            a
            for a in payload["input_artifacts"]
            if a["artifact_kind"] == "scene_draft"
            and a["content"]["scene_id"] == assignment["unit_id"]
            and a["content"]["revision_number"] == assignment["revision_number"]
        )
        if assignment["revision_number"] == 0:
            raw["issues"] = [
                {
                    "category": "pacing",
                    "severity": "blocking",
                    "description": "Offline fixture: the opening turn is obscured.",
                    "draft_evidence_refs": [
                        draft["content"]["evidence_catalog"][0]["evidence_ref"]
                    ],
                    "recommendation": "Make the opening decision and its consequence legible.",
                }
            ]
        else:
            self.repair_calls += 1
            if self.repair_mode == "invalid_once" and self.repair_calls == 1:
                raw.pop("repair_checks")
            else:
                for check in raw["repair_checks"].values():
                    check["status"] = "unmet" if self.repair_mode == "unmet" else "met"
                    check["assessment"] = "Repair audit test-only-repair-assessment-secret"
        return replace(response, content=json.dumps(raw))


@pytest.mark.anyio
@pytest.mark.parametrize("mode", ["met", "unmet", "invalid_once"])
async def test_real_revision_workflow_lineage_audit_and_existing_limits(
    mode: str,
    migrated_database_path: Path,
    database_engine: Engine,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    secret = "test-only-repair-assessment-secret"
    monkeypatch.setenv("OLLAMA_API_KEY", secret)
    prompt = load_benchmark_corpus(CORPUS_PATH).prompts[0]
    gateway = RepairGateway(prompt.prompt, prompt, repair_mode=mode)
    if mode == "unmet":
        with pytest.raises(SceneProductionError):
            await _run_gateway(gateway, migrated_database_path, database_engine)
        assert gateway.repair_calls == 2
    else:
        result = await _run_gateway(gateway, migrated_database_path, database_engine)
        assert len(result.result.accepted_units) == 3
        assert gateway.repair_calls == (2 if mode == "invalid_once" else 1)
    sessions = create_session_factory(database_engine)
    with sessions() as session:
        invocations = session.scalars(select(AgentInvocation)).all()
        audited = [i for i in invocations if "revision_acceptance_audit" in i.request_settings]
        assert audited
        first_audit = audited[0].request_settings["revision_acceptance_audit"]
        origin = session.get(
            ArtifactVersion, UUID(first_audit["tests"][0]["source_critique_version_id"])
        )
        assert origin is not None and origin.created_by_invocation_id is not None
        probe = load_probe(migrated_database_path, audited[0].id)
        restored = with_repair_history(probe, (origin.created_by_invocation_id,))
        assert restored.execution.input_version_ids == probe.execution.input_version_ids
        with pytest.raises(ValueError, match="preceding reviews"):
            with_repair_history(probe, (audited[0].id,))
        for invocation in audited:
            audit = invocation.request_settings["revision_acceptance_audit"]
            assert secret not in json.dumps(audit)
            assert len(audit["tests"]) == 1
            input_ids = {str(v.id) for v in invocation.input_versions}
            assert audit["tests"][0]["source_critique_version_id"] in input_ids
            assert audit["tests"][0]["source_draft_version_id"] in input_ids
            assert audit["candidate_version_id"] in input_ids
        failed = [i for i in invocations if i.error_code]
        assert len(failed) == (1 if mode == "invalid_once" else 0)
        if failed:
            assert (
                failed[0].request_settings["review_failure_evidence"]["capture_status"]
                == "captured"
            )
        for version in session.scalars(select(ArtifactVersion)).all():
            assert "repair_checks" not in version.content
    audit_database_export(database_engine)


def test_revision_instructions_do_not_grow_and_schema_shares_one_check_definition() -> None:
    assert len(_INSTRUCTIONS[_Operation.WRITE]) <= 638
    assert len(_INSTRUCTIONS[_Operation.CRITIQUE]) <= 3887
    execution = _revision()
    schema = _output_schema(
        _Operation.CRITIQUE,
        continuity_schema_variant=None,
        critic_execution=execution,
    )
    checks = schema["properties"]["repair_checks"]
    assert all(
        item == {"$ref": "#/$defs/RepairAcceptanceCheck"} for item in checks["properties"].values()
    )
    assert "RepairAcceptanceCheck" in schema["$defs"]
    assert "target_artifact_version_id" not in schema["properties"]


def test_nonblocking_advice_is_preserved_for_writer_without_becoming_a_repair_gate() -> None:
    execution = _revision()
    inputs = deepcopy(execution.inputs)
    review = next(item for item in inputs if item["artifact_kind"] == "critique")
    advice = {
        "category": "voice",
        "severity": "minor",
        "description": "Optional lighter phrasing.",
        "evidence": ["Cora clenched her jaw."],
        "recommendation": "Consider a lighter phrase.",
    }
    review["content"]["issues"].append(advice)
    assert len(critic_repair_tests(inputs, execution.unit_id)) == 1
    packet = compact_repair_inputs(inputs, scene_id=execution.unit_id, revision=1, critic=False)
    projected = next(item for item in packet if item["artifact_kind"] == "critique")
    assert projected["content"]["issues"] == [advice]
