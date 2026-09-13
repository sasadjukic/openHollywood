"""One terminal adjudication allowance, exact allegations, and independent hard gates."""

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
from open_hollywood_api.services.production_critic_adjudication import (
    CRITIC_ADJUDICATION_INSTRUCTIONS,
    disputed_critic_issues,
    materialize_critic_adjudication,
)
from open_hollywood_api.services.production_model_executor import (
    _INSTRUCTIONS,
    _critic_adjudication_source,
    _critic_evidence_catalog,
    _Execution,
    _materialize_output_data,
    _messages,
    _Operation,
    _output_schema,
)
from open_hollywood_engine.artifacts import ContinuityCategory, ContinuityReport, Critique
from open_hollywood_engine.evaluations import load_benchmark_corpus
from open_hollywood_engine.models import ModelRequest, ModelResponse
from open_hollywood_engine.workflows import SceneProductionError
from sqlalchemy import Engine, select

from tests.api.test_production_v26 import V26Gateway, _run_gateway
from tests.api.test_production_v29 import _materialize
from tests.api.test_production_v31 import _review, _revision
from tests.evaluations.test_agentic_blueprint import CORPUS_PATH
from tests.evaluations.test_agentic_production import ProductionFixtureGateway


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


def _adjudication() -> _Execution:
    execution = _revision()
    draft = next(
        a
        for a in execution.inputs
        if a["artifact_kind"] == "scene_draft" and a["content"]["revision_number"] == 1
    )
    report = _materialize(_review(execution, "unmet"), execution)
    source = {
        "artifact_kind": "critique",
        "artifact_key": "critique_scene_2",
        "artifact_version_id": str(uuid4()),
        "content": report,
    }
    gate = ContinuityReport(
        story_bible_version_id=uuid4(),
        scene_version_id=draft["artifact_version_id"],
        scene_plan_version_id=uuid4(),
        scene_id="scene_2",
        scene_number=2,
        checked_categories=tuple(ContinuityCategory),
    )
    inputs = (
        *execution.inputs,
        source,
        {
            "artifact_kind": "continuity_report",
            "artifact_key": "continuity_scene_2",
            "artifact_version_id": str(uuid4()),
            "content": gate.model_dump(mode="json"),
        },
    )
    return replace(
        execution,
        inputs=inputs,
        input_version_ids=tuple(UUID(a["artifact_version_id"]) for a in inputs),
    )


def _decisions(execution: _Execution, disposition: str = "unsupported") -> dict[str, Any]:
    source = _critic_adjudication_source(execution)
    return {
        "decisions": {
            key: {
                "disposition": disposition,
                "assessment": (
                    "The passage attributes the inference to the focal character; "
                    "the prior claim is unsupported."
                ),
                "evidence_refs": [_critic_evidence_catalog(execution)[0]["evidence_ref"]],
            }
            for key in disputed_critic_issues(source["content"])
        }
    }


@pytest.mark.parametrize(
    "disposition,blocking",
    [("unsupported", False), ("already_repaired", False), ("upheld", True), ("uncertain", True)],
)
def test_only_supported_release_dispositions_remove_exact_blocker(
    disposition: str, blocking: bool
) -> None:
    execution = _adjudication()
    source = deepcopy(_critic_adjudication_source(execution))
    result = _materialize_output_data(
        _Operation.CRITIC_ADJUDICATION, object(), execution, _decisions(execution, disposition)
    )
    Critique.model_validate(result)
    assert any(i["severity"] == "blocking" for i in result["issues"]) == blocking
    for key in ("scores", "overall_score", "verdict", "target_artifact_version_id"):
        assert result[key] == source["content"][key]
    assert _critic_adjudication_source(execution) == source


@pytest.mark.parametrize(
    "bad", ["missing", "invented", "stale", "duplicate", "empty", "extra", "invalid_disposition"]
)
def test_malformed_decisions_fail_closed(bad: str) -> None:
    execution = _adjudication()
    raw = _decisions(execution)
    key = next(iter(raw["decisions"]))
    decision = raw["decisions"][key]
    if bad == "missing":
        raw["decisions"].pop(key)
    elif bad == "invented":
        raw["decisions"]["issue_999"] = raw["decisions"].pop(key)
    elif bad == "stale":
        decision["evidence_refs"] = ["old_version_evidence"]
    elif bad == "duplicate":
        decision["evidence_refs"] *= 2
    elif bad == "empty":
        decision["assessment"] = " "
    elif bad == "extra":
        raw["scores"] = []
    else:
        decision["disposition"] = "probably_fine"
    with pytest.raises(ValueError):
        _materialize_output_data(_Operation.CRITIC_ADJUDICATION, object(), execution, raw)


def test_unrelated_issues_cannot_be_changed_and_schema_cannot_address_them() -> None:
    execution = _adjudication()
    source = deepcopy(_critic_adjudication_source(execution)["content"])
    other = {**source["issues"][0], "category": "other_hard_gate"}
    source["issues"].append(other)
    evidence = {i["evidence_ref"]: i["exact_excerpt"] for i in _critic_evidence_catalog(execution)}
    result = materialize_critic_adjudication(_decisions(execution), source, evidence)
    assert result["issues"][1] == other
    _critic_adjudication_source(execution)["content"]["issues"].append(other)
    with pytest.raises(ValueError, match="unrelated hard"):
        _critic_adjudication_source(execution)


def test_packet_has_frozen_repair_history_current_context_and_shorter_instructions() -> None:
    execution = _adjudication()
    source = _critic_adjudication_source(execution)
    schema = _output_schema(
        _Operation.CRITIC_ADJUDICATION, continuity_schema_variant=None, critic_execution=execution
    )
    messages = _messages(
        _Operation.CRITIC_ADJUDICATION,
        execution,
        schema,
        continuity_schema_variant=None,
        continuity_model_context=None,
    )
    payload = json.loads(messages[-1].content)
    assert payload["source_critique_version_id"] == source["artifact_version_id"]
    assert payload["repair_acceptance_tests"][0]["original_evidence"] == [
        "Cora secretly knew the spare key was gone."
    ]
    assert "scores" not in json.dumps(payload["disputed_findings"])
    assert all(a["artifact_kind"] != "critique" for a in payload["input_artifacts"])
    assert len(CRITIC_ADJUDICATION_INSTRUCTIONS) < len(_INSTRUCTIONS[_Operation.CRITIQUE])
    assert set(schema["properties"]["decisions"]["required"]) == set(payload["disputed_findings"])


class AdjudicationGateway(V26Gateway):
    def __init__(self, *args: Any, decision_mode: str) -> None:
        super().__init__(*args, mode="release")
        self.decision_mode = decision_mode
        self.critic_adjudication_calls = 0

    async def generate(self, request: ModelRequest) -> ModelResponse:
        payload = json.loads(request.messages[-1].content)
        assignment = payload.get("assignment", {})
        operation = assignment.get("operation")
        if self.decision_mode == "competing" and operation == "continuity":
            return await super().generate(request)
        response = await ProductionFixtureGateway.generate(self, request)
        raw = json.loads(response.content)
        if operation == "critique" and assignment["unit_number"] == 2:
            draft = next(
                a
                for a in payload["input_artifacts"]
                if a["artifact_kind"] == "scene_draft"
                and a["content"]["scene_id"] == assignment["unit_id"]
                and a["content"]["revision_number"] == assignment["revision_number"]
            )
            raw["assignment_violations"] = [
                {
                    "anchor": "outcome",
                    "draft_evidence_refs": [
                        draft["content"]["evidence_catalog"][0]["evidence_ref"]
                    ],
                    "explanation": "Fixture dispute: the planned outcome is only implicit.",
                    "recommended_resolution": "State the planned outcome more explicitly.",
                }
            ]
            for check in raw.get("repair_checks", {}).values():
                check["status"] = "unmet"
        elif operation == "critic_adjudication":
            self.critic_adjudication_calls += 1
            draft = next(
                a
                for a in payload["input_artifacts"]
                if a["artifact_kind"] == "scene_draft"
                and a["content"]["scene_id"] == assignment["unit_id"]
                and a["content"]["revision_number"] == assignment["revision_number"]
            )
            raw = {
                "decisions": {
                    key: {
                        "disposition": self.decision_mode
                        if self.decision_mode in {"upheld", "uncertain"}
                        else "unsupported",
                        "assessment": (
                            "The outcome is realized indirectly. test-only-adjudication-secret"
                        ),
                        "evidence_refs": [draft["content"]["evidence_catalog"][0]["evidence_ref"]],
                    }
                    for key in payload["disputed_findings"]
                }
            }
            if self.decision_mode == "invalid_always" or (
                self.decision_mode == "invalid_once" and self.critic_adjudication_calls == 1
            ):
                raw["decisions"] = {}
        return replace(response, content=json.dumps(raw))


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mode", ["release", "upheld", "uncertain", "invalid_once", "invalid_always", "competing"]
)
async def test_persisted_terminal_adjudication_limits_provenance_and_replay(
    mode: str,
    migrated_database_path: Path,
    database_engine: Engine,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    secret = "test-only-adjudication-secret"
    monkeypatch.setenv("OLLAMA_API_KEY", secret)
    prompt = load_benchmark_corpus(CORPUS_PATH).prompts[0]
    gateway = AdjudicationGateway(prompt.prompt, prompt, decision_mode=mode)
    if mode in {"upheld", "uncertain", "invalid_always", "competing"}:
        with pytest.raises(SceneProductionError):
            await _run_gateway(gateway, migrated_database_path, database_engine)
    else:
        result = await _run_gateway(gateway, migrated_database_path, database_engine)
        assert len(result.result.accepted_units) == 3
        assert result.result.accepted_units[1].revision_cycles_used == 2
    assert gateway.critic_adjudication_calls == (
        0 if mode == "competing" else 2 if mode.startswith("invalid") else 1
    )
    sessions = create_session_factory(database_engine)
    with sessions() as session:
        invocations = session.scalars(select(AgentInvocation)).all()
        calls = [
            i for i in invocations if i.request_settings.get("operation") == "critic_adjudication"
        ]
        assert len(calls) == gateway.critic_adjudication_calls
        for call in calls:
            ids = {str(v.id) for v in call.input_versions}
            assert call.prompt_text is not None
            packet = json.loads(call.prompt_text.rsplit("\n\n", 1)[1])
            assert packet["source_critique_version_id"] in ids
            assert packet["assignment"]["revision_number"] == 2
            assert all(
                t["source_critique_version_id"] in ids and t["source_draft_version_id"] in ids
                for t in packet["repair_acceptance_tests"]
            )
            if call.error_code:
                assert (
                    call.request_settings["review_failure_evidence"]["capture_status"] == "captured"
                )
            else:
                audit = call.request_settings["critic_adjudication_audit"]
                assert audit["candidate_version_id"] in ids
                assert secret not in json.dumps(audit)
                source = session.get(ArtifactVersion, UUID(audit["source_critique_version_id"]))
                assert source and any(i["severity"] == "blocking" for i in source.content["issues"])
        assert not any(
            i.request_settings.get("operation") == "continuity_adjudication" for i in invocations
        )
    audit_database_export(database_engine)


@pytest.mark.parametrize(
    "revision,completed,eligible_count,expected",
    [
        (0, False, 1, "revision_budget_remaining"),
        (1, False, 1, "revision_budget_remaining"),
        (2, False, 1, "eligible"),
        (2, True, 1, "completed"),
        (2, False, 0, "skipped_hard_critic_blockers"),
    ],
)
def test_shared_terminal_allowance_cannot_run_early_or_twice(
    revision: int,
    completed: bool,
    eligible_count: int,
    expected: str,
) -> None:
    from open_hollywood_api.services.production_workflow import _maximum_production_model_calls
    from open_hollywood_engine.workflows.production_graph import (
        _adjudication_status,
        initial_production_state,
    )

    from tests.workflows.test_scene_production import _production_input, _units

    production = _production_input(maximum_revision_cycles=2, units=_units(dialogue=False))
    state = initial_production_state(production)
    state["adjudication_completed"] = completed
    state["critique_blocking_issue_count"] = 1
    state["critique_adjudicable_issue_count"] = eligible_count
    execution = _adjudication()
    gate = next(a for a in execution.inputs if a["artifact_kind"] == "continuity_report")
    assert (
        _adjudication_status(
            state, production, revision, ContinuityReport.model_validate(gate["content"])
        )
        == expected
    )
    assert _maximum_production_model_calls(production) == len(production.units) * 12
    assert production.max_graph_steps == len(production.units) * 12


def test_adjudication_request_is_smaller_than_the_corresponding_full_critic_request() -> None:
    execution = _adjudication()
    source = _critic_adjudication_source(execution)
    ordinary = replace(
        execution,
        inputs=tuple(
            a
            for a in execution.inputs
            if a is not source and a["artifact_kind"] != "continuity_report"
        ),
    )
    sizes = []
    for operation, context in (
        (_Operation.CRITIQUE, ordinary),
        (_Operation.CRITIC_ADJUDICATION, execution),
    ):
        schema = _output_schema(
            operation,
            continuity_schema_variant=None,
            critic_execution=context,
            critic_evidence_refs=tuple(
                i["evidence_ref"] for i in _critic_evidence_catalog(context)
            ),
        )
        messages = _messages(
            operation,
            context,
            schema,
            continuity_schema_variant=None,
            continuity_model_context=None,
        )
        sizes.append(sum(len(m.content) for m in messages))
    assert sizes[1] < sizes[0]


def test_rejected_adjudication_text_never_returns_as_story_evidence() -> None:
    execution = replace(
        _adjudication(),
        previous_failure={
            "error_code": "schema_validation_failed",
            "message": "rejected story allegation",
            "validation_issues": [
                {
                    "location": "decisions",
                    "type": "critic_adjudication_contract_invalid",
                    "message": "rejected story allegation",
                    "received_value": "rejected story allegation",
                }
            ],
        },
    )
    schema = _output_schema(
        _Operation.CRITIC_ADJUDICATION, continuity_schema_variant=None, critic_execution=execution
    )
    messages = _messages(
        _Operation.CRITIC_ADJUDICATION,
        execution,
        schema,
        continuity_schema_variant=None,
        continuity_model_context=None,
    )
    assert "rejected story allegation" not in messages[-1].content
    assert json.loads(messages[-1].content)["schema_repair"]["focus_locations"] == ["decisions"]
