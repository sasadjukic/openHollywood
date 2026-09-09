"""v25 replay shapes plus positive controls through v26's real production boundary."""

from __future__ import annotations

import json
from dataclasses import replace
from decimal import Decimal
from pathlib import Path
from typing import Any
from uuid import uuid4

import pytest
from open_hollywood_api.persistence.database import create_session_factory
from open_hollywood_api.persistence.models import AgentInvocation, ArtifactVersion, RunStatus
from open_hollywood_api.services.agentic_benchmark import AgenticBenchmarkBlueprintService
from open_hollywood_api.services.blueprint_model_executor import BenchmarkBlueprintNodeExecutor
from open_hollywood_api.services.blueprint_workflow import BlueprintWorkflowService
from open_hollywood_api.services.model_profiles import BUILTIN_PROFILE_IDS, ModelProfileStore
from open_hollywood_api.services.production_adjudication import (
    ADJUDICATION_INSTRUCTIONS,
    adjudication_schema,
    materialize_adjudication,
)
from open_hollywood_api.services.production_model_executor import (
    BenchmarkProductionExecutor,
    _continuity_model_findings,
    _critic_evidence_catalog,
    _materialize_thread_changes,
    _normalize_point_of_view_check,
    _normalize_scene_assignment_critique,
    _StructuredOutputContractError,
)
from open_hollywood_api.services.production_workflow import BenchmarkSceneProductionService
from open_hollywood_engine.artifacts import (
    ArtifactKind,
    ContinuityCategory,
    ContinuityFinding,
    ContinuityReport,
    StoryBibleInvariantError,
    StoryBibleThread,
    StoryBibleUpdate,
    apply_story_bible_update,
)
from open_hollywood_engine.evaluations import (
    BenchmarkCase,
    BenchmarkProfileSnapshot,
    BenchmarkSystem,
    load_benchmark_corpus,
)
from open_hollywood_engine.models import (
    ModelDeployment,
    ModelProfileMode,
    ModelRequest,
    ModelResponse,
    ModelSelection,
)
from open_hollywood_engine.workflows import (
    BlueprintDecisionAction,
    BlueprintHumanDecision,
    SceneProductionError,
)
from sqlalchemy import Engine, select

from tests.artifacts.test_story_bible import _initial_bible, _scene_one_update, _scene_two_update
from tests.evaluations.test_agentic_blueprint import CAMPAIGN_ID, CORPUS_PATH
from tests.evaluations.test_agentic_production import (
    ProductionFixtureGateway,
    _schema_test_continuity_context,
    _v17_catalog_test_execution,
)

FIXTURES = json.loads(
    (Path(__file__).parents[1] / "fixtures" / "production_v25_regressions.json").read_text(
        encoding="utf-8"
    )
)


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


def test_resolved_echo_survives_enclosing_delta_and_reducer() -> None:
    first = apply_story_bible_update(_initial_bible(), _scene_one_update())
    current = apply_story_bible_update(first, _scene_two_update())
    thread = current.threads[0]
    raw = _scene_two_update().model_dump(mode="json")
    raw.update(
        established_facts=[],
        thread_changes=_materialize_thread_changes(
            [thread.model_dump(mode="json")], "scene_3", {thread.id: thread}
        ),
    )
    raw["accepted_scene"].update(
        scene_id="scene_3", scene_number=3, artifact_version_id=str(uuid4())
    )
    raw["timeline_events"][0].update(id="event_3", sequence=3, scene_id="scene_3")
    delta = StoryBibleUpdate.model_validate(raw)
    successor = apply_story_bible_update(current, delta)
    assert delta.thread_changes == ()
    assert successor.threads == current.threads
    assert successor.threads[0].resolved_scene_id == "scene_2"
    assert len(successor.accepted_scenes) == 3


@pytest.mark.parametrize(
    "change",
    [
        {"status": "open", "resolution": None},
        {"resolution": "A completely new payoff."},
    ],
)
def test_resolved_history_cannot_be_reopened_or_rewritten(change: dict[str, Any]) -> None:
    thread = _scene_two_update().thread_changes[0]
    with pytest.raises(_StructuredOutputContractError) as error:
        _materialize_thread_changes(
            [{**thread.model_dump(mode="json"), **change}], "scene_3", {thread.id: thread}
        )
    assert "thread_changes.0" in error.value.location
    assert "A completely new payoff" not in str(error.value)


def test_reducer_independently_rejects_rewritten_resolution_history() -> None:
    current = apply_story_bible_update(
        apply_story_bible_update(_initial_bible(), _scene_one_update()), _scene_two_update()
    )
    raw = _scene_two_update().model_dump(mode="json")
    raw["accepted_scene"].update(
        scene_id="scene_3", scene_number=3, artifact_version_id=str(uuid4())
    )
    raw["timeline_events"][0].update(id="event_3", sequence=3, scene_id="scene_3")
    raw["established_facts"] = []
    raw["thread_changes"][0]["resolved_scene_id"] = "scene_3"
    with pytest.raises(StoryBibleInvariantError, match="cannot change resolution history"):
        apply_story_bible_update(current, StoryBibleUpdate.model_validate(raw))


@pytest.mark.parametrize("record", FIXTURES["resolved_threads"])
def test_exact_canary_resolution_origins_are_preserved(record: dict[str, str]) -> None:
    thread = StoryBibleThread.model_validate(
        {
            "id": record["thread_id"],
            "kind": "promise",
            "statement": "An established thread.",
            "introduced_scene_id": record["resolved_scene"],
            "status": "resolved",
            "resolution": "The accepted scene establishes the payoff.",
            "resolved_scene_id": record["resolved_scene"],
        }
    )
    assert (
        _materialize_thread_changes(
            [thread.model_dump(mode="json")], record["update_scene"], {thread.id: thread}
        )
        == []
    )


def _report(*, category: str = "timeline") -> dict[str, Any]:
    finding = ContinuityFinding.model_validate(
        {
            "id": "disputed",
            "severity": "blocking",
            "category": category,
            "basis": "contradiction",
            "canonical_source_refs": ["source_1"],
            "related_scene_ids": ["scene_2"],
            "summary": FIXTURES["unresolved_goal"]["allegation"],
            "evidence": [FIXTURES["unresolved_goal"]["evidence"]],
            "recommended_resolution": "Settle the argument conclusively.",
            "blocks_approval": True,
        }
    )
    return ContinuityReport(
        story_bible_version_id=uuid4(),
        scene_version_id=uuid4(),
        scene_plan_version_id=uuid4(),
        scene_id="scene_2",
        scene_number=2,
        checked_categories=tuple(ContinuityCategory),
        findings=(finding,),
    ).model_dump(mode="json")


@pytest.mark.parametrize(
    "disposition,blocking",
    [
        ("upheld", True),
        ("uncertain", True),
        ("unsupported", False),
        ("requirement_only", False),
        ("compatible_development", False),
        ("already_repaired", False),
    ],
)
def test_adjudication_dispositions_are_bounded_and_fail_closed(
    disposition: str,
    blocking: bool,
) -> None:
    report = _report()
    response = {
        "decisions": {
            "disputed": {
                "disposition": disposition,
                "assessment": "The source and approved outcome were compared.",
                "evidence_refs": ["draft_evidence_0001"],
            }
        }
    }
    result = materialize_adjudication(
        response, report, {"draft_evidence_0001": FIXTURES["unresolved_goal"]["evidence"]}
    )
    assert result["findings"][0]["blocks_approval"] is blocking
    assert result["scene_version_id"] == report["scene_version_id"]
    assert result["findings"][0]["id"] == "disputed"


def test_adjudication_cannot_release_world_rules_or_add_new_findings() -> None:
    report = _report()
    world = {**report["findings"][0], "id": "world", "category": "world_rule"}
    report["findings"].append(world)
    response = {
        "decisions": {
            "disputed": {
                "disposition": "unsupported",
                "assessment": "Unrelated timeline source.",
                "evidence_refs": ["draft_evidence_0001"],
            }
        }
    }
    result = materialize_adjudication(response, report, {"draft_evidence_0001": "Exact prose."})
    assert result["findings"][1] == world
    response["decisions"]["world"] = response["decisions"]["disputed"]
    with pytest.raises(ValueError, match="every exact disputed finding"):
        materialize_adjudication(response, report, {"draft_evidence_0001": "Exact prose."})


def test_adjudication_schema_is_small_and_uses_one_exact_evidence_enum() -> None:
    schema = adjudication_schema(_report(), ["draft_evidence_0001"])
    assert schema["properties"]["decisions"]["required"] == ["disputed"]
    assert len(json.dumps(schema)) < 2000
    assert "not freeze later time" in ADJUDICATION_INSTRUCTIONS
    assert "review reports and requested repairs" in ADJUDICATION_INSTRUCTIONS


def test_same_repaired_evidence_cannot_return_as_a_reworded_new_blocker() -> None:
    base = _schema_test_continuity_context(recheck=True)
    base.candidate_draft["content"]["evidence_catalog"][0]["exact_excerpt"] = FIXTURES[
        "reintroduced_repair"
    ]["evidence"]
    claim_id = base.canonical_claim_ids[0]
    source_ref = base.canonical_claim_source_refs[claim_id]
    evidence_ref = base.evidence_refs[0]
    context = replace(
        base,
        previous_continuity_report={
            "content": {
                "findings": [
                    {
                        "id": "old",
                        "severity": "blocking",
                        "basis": "contradiction",
                        "category": "timeline",
                        "summary": "Link the mechanism to the memory.",
                        "canonical_source_refs": [source_ref],
                    }
                ]
            }
        },
    )
    response: dict[str, Any] = {
        "prior_finding_rechecks": {
            "old": {
                "status": "resolved",
                "resolution_assessment": "The repair explicitly links them.",
                "revised_draft_evidence_refs": [evidence_ref],
            }
        },
        "new_findings": [
            {
                "severity": "blocking",
                "summary": FIXTURES["reintroduced_repair"]["allegation"],
                "basis": "contradiction",
                "canonical_claim_ids": [claim_id],
                "revised_draft_evidence_refs": [evidence_ref],
            }
        ],
    }
    with pytest.raises(_StructuredOutputContractError) as failure:
        _continuity_model_findings(response, context)
    assert failure.value.issue_type == "released_finding_reintroduced"
    # Different canonical authority does not count as the same repaired claim.
    context = replace(
        context,
        canonical_source_catalog=(
            *context.canonical_source_catalog,
            {"claim_id": "different", "reference_id": "different_source", "categories": ["fact"]},
        ),
    )
    response["new_findings"][0]["canonical_claim_ids"] = ["different"]
    assert _continuity_model_findings(response, context)


@pytest.mark.parametrize("status", ["aligned", "violation"])
def test_viewpoint_audit_cannot_be_overruled_by_a_high_overall_score(status: str) -> None:
    prose = (
        "Cora privately knew what Elara could not know."
        if status == "violation"
        else "Elara watched Cora open the door."
    )
    execution = _v17_catalog_test_execution(
        scene_plan={"point_of_view_character_id": "elara"}, draft_prose=prose
    )
    check: dict[str, Any] = {"status": status}
    if status == "violation":
        check.update(
            violation_kind="unauthorized_private_state",
            subject_character_id="cora",
            draft_evidence_refs=[_critic_evidence_catalog(execution)[0]["evidence_ref"]],
            assessment="Cora's private knowledge is narrated as fact.",
            recommended_resolution="Frame observable actions through Elara's viewpoint.",
        )
    result = _normalize_scene_assignment_critique(
        _normalize_point_of_view_check(
            {
                "verdict": "pass",
                "overall_score": 5.0,
                "issues": [],
                "assignment_violations": [],
                "point_of_view_check": check,
            },
            execution,
        ),
        execution,
    )
    assert result["verdict"] == ("revise" if status == "violation" else "pass")


@pytest.mark.parametrize("status", [[], {}, "not_assigned", "unrecognized"])
def test_invalid_viewpoint_audit_requests_bounded_repair(status: object) -> None:
    execution = _v17_catalog_test_execution(
        scene_plan={"point_of_view_character_id": "elara"}, draft_prose="Elara opens the door."
    )
    with pytest.raises(_StructuredOutputContractError):
        _normalize_point_of_view_check(
            {
                "assignment_violations": [],
                "point_of_view_check": {
                    "status": status,
                    "assessment": "Checked.",
                    "draft_evidence": "Elara opens the door.",
                },
            },
            execution,
        )


class V26Gateway(ProductionFixtureGateway):
    def __init__(self, *args: Any, mode: str) -> None:
        super().__init__(*args)
        self.mode = mode
        self.adjudication_calls = 0

    async def generate(self, request: ModelRequest) -> ModelResponse:
        response = await super().generate(request)
        payload = json.loads(request.messages[-1].content)
        assignment = payload.get("assignment", {})
        operation = assignment.get("operation")
        raw = json.loads(response.content)
        if self.mode == "thread_echo" and operation == "story_bible_update":
            bible = next(
                item["content"]
                for item in payload["input_artifacts"]
                if item["artifact_kind"] == "story_bible"
            )
            raw["thread_changes"] = bible["threads"] or [
                {
                    "id": "resolved_once",
                    "kind": "mystery",
                    "statement": "Who left the key?",
                    "status": "resolved",
                    "resolution": "Mara left it.",
                }
            ]
        elif (
            operation == "continuity"
            and self.mode != "thread_echo"
            and (assignment["unit_number"] == 2)
        ):
            if payload["output_schema_variant"] == "initial_check":
                raw["findings"] = [
                    {
                        "severity": "blocking",
                        "summary": "The goal must be conclusively achieved.",
                        "recommended_resolution": "Resolve all ambiguity now.",
                        "draft_evidence_refs": [
                            payload["candidate_draft"]["content"]["evidence_catalog"][0][
                                "evidence_ref"
                            ]
                        ],
                        "basis_details": {
                            "basis": "contradiction",
                            "canonical_claim_ids": [
                                payload["contradiction_claim_catalog"][0]["canonical_claim_id"]
                            ],
                            "conflict_disposition": "directly_incompatible",
                            "repair_action": "replace",
                            "conflict_explanation": "Prior history is misused as an obligation.",
                        },
                    }
                ]
            else:
                for decision in raw["prior_finding_rechecks"].values():
                    decision["status"] = "still_blocking"
                    decision["repair_assessment"] = "The same disputed goal remains unachieved."
                    decision.pop("resolution_assessment", None)
        elif operation == "continuity_adjudication":
            self.adjudication_calls += 1
            raw = {
                "decisions": {
                    finding["id"]: {
                        "disposition": (
                            self.mode
                            if self.mode in {"upheld", "uncertain"}
                            else "requirement_only"
                        ),
                        "assessment": "Past history does not require achieving a pursued goal.",
                        "evidence_refs": [
                            payload["candidate_draft"]["content"]["evidence_catalog"][0][
                                "evidence_ref"
                            ]
                        ],
                    }
                    for finding in payload["disputed_findings"]
                }
            }
            if self.mode == "invalid_always" or (
                self.mode == "invalid_once" and self.adjudication_calls == 1
            ):
                raw["decisions"] = {}
        return replace(response, content=json.dumps(raw))


async def _run_gateway(gateway: V26Gateway, database: Path, engine: Engine) -> Any:
    prompt = load_benchmark_corpus(CORPUS_PATH).prompts[0]
    sessions = create_session_factory(engine)
    profile = ModelProfileStore(sessions).configure_profile(
        BUILTIN_PROFILE_IDS[ModelProfileMode.LOCAL],
        local_model=ModelSelection(
            provider="ollama", model_identifier="local-fixture", deployment=ModelDeployment.LOCAL
        ),
        cloud_model=None,
    )
    case = BenchmarkCase(
        case_id=uuid4(),
        prompt_id=prompt.prompt_id,
        prompt_version=prompt.version,
        system=BenchmarkSystem.AGENTIC,
        run_seed=prompt.random_seed,
        profile=BenchmarkProfileSnapshot.from_configuration(
            profile_id=profile.id, configuration=profile.configuration
        ),
    )
    prepared = await AgenticBenchmarkBlueprintService(
        campaign_id=CAMPAIGN_ID, database_path=database, session_factory=sessions, gateway=gateway
    ).prepare(case, prompt)
    assert prepared.interrupt_id
    async with BlueprintWorkflowService(
        database,
        sessions,
        BenchmarkBlueprintNodeExecutor(session_factory=sessions, gateway=gateway),
    ) as blueprint_service:
        approved = await blueprint_service.resume(
            prepared.workflow_run_id,
            BlueprintHumanDecision(
                id=uuid4(),
                interrupt_id=prepared.interrupt_id,
                action=BlueprintDecisionAction.APPROVE,
            ),
        )
    blueprint = next(
        item for item in approved.artifacts if item.kind is ArtifactKind.STORY_BLUEPRINT
    )
    async with BenchmarkSceneProductionService(
        database_path=database,
        session_factory=sessions,
        executor=BenchmarkProductionExecutor(session_factory=sessions, gateway=gateway),
        cost_ceiling_usd=Decimal("5"),
    ) as service:
        result = await service.execute(prepared.workflow_run_id, blueprint)
        count = len(gateway.requests)
        replay = await service.execute(prepared.workflow_run_id, blueprint)
        assert replay == result
        assert len(gateway.requests) == count
        return result


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mode", ["thread_echo", "release", "upheld", "uncertain", "invalid_once", "invalid_always"]
)
async def test_real_persisted_workflow_runs_v26_guards_and_replays(
    mode: str,
    migrated_database_path: Path,
    database_engine: Engine,
) -> None:
    prompt = load_benchmark_corpus(CORPUS_PATH).prompts[0]
    gateway = V26Gateway(prompt.prompt, prompt, mode=mode)
    if mode in {"upheld", "uncertain", "invalid_always"}:
        with pytest.raises(SceneProductionError):
            await _run_gateway(gateway, migrated_database_path, database_engine)
    else:
        result = await _run_gateway(gateway, migrated_database_path, database_engine)
        assert result.status is RunStatus.SUCCEEDED
        assert len(result.result.accepted_units) == 3
    sessions = create_session_factory(database_engine)
    with sessions() as session:
        invocations = session.scalars(select(AgentInvocation)).all()
        adjudications = [
            item
            for item in invocations
            if item.request_settings.get("operation") == "continuity_adjudication"
        ]
        expected_calls = 0 if mode == "thread_echo" else (2 if mode.startswith("invalid") else 1)
        assert len(adjudications) == expected_calls
        assert sorted(item.request_settings["attempt_number"] for item in adjudications) == list(
            range(1, expected_calls + 1)
        )
        for item in adjudications:
            if item.error_code:
                assert item.request_settings["failure_layer"] == "application_materialization"
                assert item.request_settings["structured_failure"]["failure_layer"] == (
                    "application_materialization"
                )
        successful = [item for item in adjudications if not item.error_code]
        if successful:
            audit = successful[0].request_settings["continuity_finding_audit"]
            assert audit["stage"] == "adjudication"
            assert audit["findings"][0]["source_claims"]
        if mode == "thread_echo":
            bible = session.get(ArtifactVersion, result.result.final_story_bible.version_id)
            assert bible is not None
            assert bible.content["threads"][0]["resolved_scene_id"] == "scene_1"
