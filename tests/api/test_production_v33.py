"""Temporal claim scope, later development and restart evidence remain separate."""

from __future__ import annotations

import json
from copy import deepcopy
from dataclasses import replace
from pathlib import Path
from typing import Any, cast
from uuid import uuid4

import pytest
from open_hollywood_api.persistence.database import create_session_factory
from open_hollywood_api.persistence.models import (
    AgentInvocation,
    ArtifactVersion,
    InvocationStatus,
    Project,
    RunStatus,
    WorkflowEvent,
    WorkflowRun,
)
from open_hollywood_api.services.production_model_executor import (
    _continuity_canonical_source_catalog,
    _retry_context,
)
from open_hollywood_api.services.production_workflow import SceneProductionService
from open_hollywood_api.services.run_controls import run_usage
from open_hollywood_engine.evaluations import load_benchmark_corpus
from open_hollywood_engine.models import ModelRequest, ModelResponse
from open_hollywood_engine.workflows import (
    SCENE_PRODUCTION_PROMPT_TEMPLATE_VERSION,
    RunBudget,
    SceneProductionError,
    SceneProductionExecutor,
)
from sqlalchemy import Engine, select

from tests.api.test_production_v26 import V26Gateway, _run_gateway
from tests.evaluations.test_agentic_blueprint import CORPUS_PATH


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


def _catalog() -> tuple[dict[str, Any], ...]:
    return _continuity_canonical_source_catalog(
        (
            {
                "artifact_kind": "story_bible",
                "artifact_key": "bible",
                "artifact_version_id": str(uuid4()),
                "content": {
                    "timeline": [
                        {
                            "id": "arrival",
                            "scene_id": "scene_1",
                            "sequence": 1,
                            "time_context": "Morning",
                            "summary": "Mara arrives at the station.",
                            "character_ids": ["mara"],
                            "location_id": "station",
                        }
                    ],
                    "established_facts": [
                        {
                            "id": "locked",
                            "statement": "The vault cannot open without the key.",
                            "established_scene_id": "scene_1",
                        }
                    ],
                    "character_states": [
                        {
                            "character_id": "mara",
                            "last_updated_scene_id": "scene_2",
                            "physical_state": "Broken wrist",
                            "emotional_state": "Afraid",
                            "current_goal": "Leave",
                            "current_location_id": "station",
                            "knowledge_fact_ids": ["locked"],
                        }
                    ],
                    "relationship_states": [
                        {
                            "relationship_id": "mara_ivo",
                            "state": "Distrust",
                            "last_updated_scene_id": "scene_2",
                        }
                    ],
                    "location_states": [
                        {
                            "location_id": "station",
                            "state": "Dark",
                            "last_updated_scene_id": "scene_1",
                        }
                    ],
                    "threads": [
                        {
                            "id": "question",
                            "kind": "mystery",
                            "statement": "Who has the key?",
                            "status": "open",
                            "introduced_scene_id": "scene_1",
                        },
                        {
                            "id": "answer",
                            "kind": "promise",
                            "statement": "Identify the sender.",
                            "status": "resolved",
                            "introduced_scene_id": "scene_1",
                            "resolved_scene_id": "scene_2",
                            "resolution": "Ivo sent the letter.",
                        },
                    ],
                    "prohibited_contradictions": ["The dead cannot return."],
                },
            },
        )
    )


def test_event_time_and_subject_are_an_indivisible_scoped_claim() -> None:
    events = [c for c in _catalog() if c["categories"] == ["timeline"]]
    assert len(events) == 1
    assert json.loads(events[0]["claim"]) == {
        "scene_id": "scene_1",
        "time_context": "Morning",
        "summary": "Mara arrives at the station.",
    }
    assert events[0]["scope"] == "past_event_only@scene_1"
    assert events[0]["canonical_id"] == "arrival"
    assert {"mara", "station", "scene_1"}.issubset(events[0]["related_ids"])


@pytest.mark.parametrize(
    "path,scene",
    [
        ("character_states", "scene_2"),
        ("relationship_states", "scene_2"),
        ("location_states", "scene_1"),
    ],
)
def test_current_states_are_bound_to_their_actual_update_scene(path: str, scene: str) -> None:
    states = [c for c in _catalog() if f".{path}" in c["source_path"]]
    assert states and all(
        c["scope"] == f"state_snapshot@{scene}; later change allowed" for c in states
    )
    assert all(c["claim"] not in {"Afraid", "Leave"} for c in states)


def test_administrative_labels_cannot_supply_contradictions_but_resolutions_and_facts_can() -> None:
    catalog = _catalog()
    assert not any(c["source_path"].endswith((".kind", ".status")) for c in catalog)
    assert not {"open", "resolved", "mystery", "promise"}.intersection(c["claim"] for c in catalog)
    resolution = next(c for c in catalog if c["source_path"].endswith(".resolution"))
    assert resolution["claim"] == "Ivo sent the letter."
    assert resolution["scope"] == "resolved_history@scene_2; resolution immutable"
    fact = next(c for c in catalog if ".established_facts" in c["source_path"])
    assert fact["claim"] == "The vault cannot open without the key."
    assert "scene_1" in fact["scope"]
    assert any(c["claim"] == "The dead cannot return." for c in catalog)


def test_initial_knowledge_does_not_become_a_ceiling_and_secret_content_remains_fact() -> None:
    artifact = {
        "artifact_kind": "character",
        "artifact_key": "mara",
        "artifact_version_id": str(uuid4()),
        "content": {
            "id": "mara",
            "initial_knowledge": ["Ivo has a key."],
            "secrets": ["Mara forged the letter."],
        },
    }
    before = deepcopy(artifact)
    catalog = _continuity_canonical_source_catalog((artifact,))
    knowledge = next(c for c in catalog if ".initial_knowledge" in c["source_path"])
    assert "non-exhaustive" in knowledge["scope"] and "later learning" in knowledge["scope"]
    assert any(c["claim"] == "Mara forged the letter." for c in catalog)
    assert artifact == before


class DevelopmentGateway(V26Gateway):
    async def generate(self, request: ModelRequest) -> ModelResponse:
        response = await super().generate(request)
        payload = json.loads(request.messages[-1].content)
        assignment = payload.get("assignment", {})
        if (
            assignment.get("operation") == "continuity"
            and assignment["unit_number"] == 2
            and payload["output_schema_variant"] == "initial_check"
        ):
            raw = json.loads(response.content)
            event = next(
                c for c in payload["contradiction_claim_catalog"] if c["category"] == "timeline"
            )
            finding = raw["findings"][0]
            finding["basis_details"]["canonical_claim_ids"] = [event["canonical_claim_id"]]
            finding["basis_details"]["conflict_disposition"] = (
                "compatible_development" if self.mode == "development" else "directly_incompatible"
            )
            finding["basis_details"]["conflict_explanation"] = (
                "Offline supplied disposition: compare the event at its stated time, "
                "not a later state."
            )
            return replace(response, content=json.dumps(raw))
        return response


@pytest.mark.anyio
@pytest.mark.parametrize("mode", ["development", "upheld"])
async def test_scoped_claims_cross_real_persistence_and_preserve_terminal_gates(
    mode: str, migrated_database_path: Path, database_engine: Engine
) -> None:
    prompt = load_benchmark_corpus(CORPUS_PATH).prompts[0]
    gateway = DevelopmentGateway(prompt.prompt, prompt, mode=mode)
    if mode == "upheld":
        with pytest.raises(SceneProductionError):
            await _run_gateway(gateway, migrated_database_path, database_engine)
        assert gateway.adjudication_calls == 1
    else:
        result = await _run_gateway(gateway, migrated_database_path, database_engine)
        assert len(result.result.accepted_units) == 3
        assert all(u.revision_cycles_used == 0 for u in result.result.accepted_units)
        assert gateway.adjudication_calls == 0
    sessions = create_session_factory(database_engine)
    with sessions() as session:
        invocations = session.scalars(select(AgentInvocation)).all()
        audited = [
            c
            for c in invocations
            if c.request_settings.get("operation") == "continuity"
            and c.request_settings.get("continuity_finding_audit", {}).get("findings")
        ]
        assert audited
        source = audited[0].request_settings["continuity_finding_audit"]["findings"][0][
            "source_claims"
        ][0]
        assert source["scope"].startswith("past_event_only@")
        assert "time_context" in json.loads(source["claim"])
        assert not any(c.error_code for c in invocations)


def test_recovery_closes_only_lost_calls_without_inventing_usage_or_review_retries(
    migrated_database_path: Path, database_engine: Engine
) -> None:
    sessions = create_session_factory(database_engine)
    run_id, other_id, lost_id, success_id, foreign_id = [uuid4() for _ in range(5)]
    settings = {
        "task_fingerprint": "same-candidate",
        "prompt_template_version": SCENE_PRODUCTION_PROMPT_TEMPLATE_VERSION,
    }
    with sessions.begin() as session:
        project = Project(id=uuid4(), name="Recovery evidence")
        session.add(project)
        session.flush()
        for ident in (run_id, other_id):
            session.add(
                WorkflowRun(
                    id=ident,
                    project_id=project.id,
                    workflow_name="scene_production",
                    graph_version="9",
                    status=RunStatus.RUNNING,
                    checkpoint_id="preserved",
                    current_node="continuity",
                    input_state={},
                    budget=RunBudget().to_data(),
                )
            )
        session.flush()
        for ident, target_run_id, status in (
            (lost_id, run_id, InvocationStatus.RUNNING),
            (success_id, run_id, InvocationStatus.SUCCEEDED),
            (foreign_id, other_id, InvocationStatus.RUNNING),
        ):
            session.add(
                AgentInvocation(
                    id=ident,
                    workflow_run_id=target_run_id,
                    specialist_role="continuity_supervisor",
                    provider="fixture",
                    model_identifier="fixture",
                    status=status,
                    prompt_sha256="a" * 64,
                    request_settings=settings,
                    input_tokens=0,
                    output_tokens=0,
                )
            )
    service = SceneProductionService(
        database_path=migrated_database_path,
        session_factory=sessions,
        executor=cast(SceneProductionExecutor, object()),
    )
    service._recover_interrupted_run(run_id)
    with sessions() as session:
        lost = session.get(AgentInvocation, lost_id)
        run = session.get(WorkflowRun, run_id)
        assert lost is not None and run is not None
        assert lost.status is InvocationStatus.FAILED and lost.error_code == "interrupted_execution"
        assert lost.request_settings["interruption"]["provider_outcome"] == "unknown"
        assert (
            lost.request_settings["interruption"]["completed_at_basis"]
            == "recovery_detection_not_provider_completion"
        )
        assert lost.input_tokens == lost.output_tokens == 0
        assert run.checkpoint_id == "preserved" and run_usage(run).model_calls == 2
        success = session.get(AgentInvocation, success_id)
        foreign = session.get(AgentInvocation, foreign_id)
        assert success is not None and success.status is InvocationStatus.SUCCEEDED
        assert foreign is not None and foreign.status is InvocationStatus.RUNNING
        attempt, failure = _retry_context(
            session,
            workflow_run_id=run_id,
            specialist_role="continuity_supervisor",
            task_fingerprint="same-candidate",
        )
        assert attempt == 1 and failure is None
        event = session.scalar(select(WorkflowEvent).where(WorkflowEvent.workflow_run_id == run_id))
        assert event and event.payload["interrupted_invocation_ids"] == [str(lost_id)]
        assert not session.scalars(select(ArtifactVersion)).all()
