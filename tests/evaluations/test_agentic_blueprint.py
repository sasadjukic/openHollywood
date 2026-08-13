"""Real graph-backed benchmark Blueprint preparation and persistence tests."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any
from uuid import UUID

import pytest
from open_hollywood_api.persistence.database import create_session_factory
from open_hollywood_api.persistence.models import (
    AgentInvocation,
    Artifact,
    InvocationStatus,
    RunStatus,
    WorkflowRun,
)
from open_hollywood_api.services.agentic_benchmark import (
    AgenticBenchmarkBlueprintService,
)
from open_hollywood_api.services.model_profiles import (
    BUILTIN_PROFILE_IDS,
    ModelProfileStore,
)
from open_hollywood_engine.artifacts import (
    ArtifactKind,
    Critique,
    CritiqueVerdict,
    MaturityMode,
    Premise,
    RubricScore,
)
from open_hollywood_engine.evaluations import (
    BenchmarkCase,
    BenchmarkProfileSnapshot,
    BenchmarkSystem,
    load_benchmark_corpus,
)
from open_hollywood_engine.models import (
    ModelCapabilities,
    ModelDeployment,
    ModelDescriptor,
    ModelProfileMode,
    ModelRequest,
    ModelResponse,
    ModelSelection,
    ModelTiming,
    ModelUsage,
)
from open_hollywood_engine.workflows import RetryableSpecialistError, RunPauseReason
from sqlalchemy import Engine, func, select

from tests.artifacts.test_schemas import _blueprint

WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
CORPUS_PATH = WORKSPACE_ROOT / "benchmarks" / "v0.1" / "corpus.json"
CAMPAIGN_ID = UUID("bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb")


class BlueprintFixtureGateway:
    """Return coherent structured outputs for every registered Blueprint role."""

    provider = "ollama"

    def __init__(self, prompt_text: str, prompt: Any) -> None:
        source = _blueprint()
        self.brief = source.creative_brief.model_copy(
            update={
                "original_premise": prompt_text,
                "genres": tuple(prompt.genres),
                "maturity": MaturityMode(prompt.intended_maturity.value),
                "target_word_count": 3_000,
                "required_elements": tuple(prompt.required_elements),
                "forbidden_elements": tuple(prompt.forbidden_shortcuts),
            }
        )
        self.premise = Premise(
            logline=source.logline,
            thematic_thesis=source.thematic_thesis,
            central_conflict=source.central_conflict,
            story_arc=source.story_arc,
            proposed_ending=source.proposed_ending,
            voice_and_style_guide=source.voice_and_style_guide,
            potential_risks=source.potential_risks,
            unresolved_decisions=source.unresolved_decisions,
        )
        self.blueprint = source.model_copy(update={"creative_brief": self.brief})
        self.brief_response_overrides: dict[str, Any] = {}
        self.requests: list[ModelRequest] = []

    async def generate(self, request: ModelRequest) -> ModelResponse:
        self.requests.append(request)
        role = request.invocation.specialist_role
        value: Any
        if role == "brief_architect":
            value = self.brief.model_dump(
                mode="json",
                exclude={
                    "original_premise",
                    "story_format",
                    "genres",
                    "maturity",
                    "required_elements",
                    "forbidden_elements",
                },
            )
            value.update(self.brief_response_overrides)
        elif role == "premise_architect":
            value = self.premise
        elif role == "world_builder":
            value = {
                "locations": [
                    item.model_copy(update={"associated_character_ids": ()}).model_dump(mode="json")
                    for item in self.blueprint.locations
                ],
                "world_rules": [
                    item.model_copy(update={"relevant_character_ids": ()}).model_dump(mode="json")
                    for item in self.blueprint.world_rules
                ],
            }
        elif role == "character_architect":
            value = {
                "characters": [item.model_dump(mode="json") for item in self.blueprint.characters],
                "relationships": [
                    item.model_dump(mode="json") for item in self.blueprint.relationships
                ],
            }
        elif role == "blueprint_integrator":
            value = {
                "world_summary": self.blueprint.world_summary,
                "beats": [item.model_dump(mode="json") for item in self.blueprint.beats],
                "scene_plans": [
                    item.model_dump(mode="json") for item in self.blueprint.scene_plans
                ],
            }
        elif role == "blueprint_critic":
            payload = json.loads(request.messages[-1].content)
            blueprint_input = next(
                item
                for item in payload["input_artifacts"]
                if item["artifact_kind"] == ArtifactKind.STORY_BLUEPRINT.value
            )
            value = Critique(
                target_artifact_kind=ArtifactKind.STORY_BLUEPRINT,
                target_artifact_key=blueprint_input["artifact_key"],
                target_artifact_version_id=blueprint_input["artifact_version_id"],
                rubric_name="story-blueprint",
                rubric_version="1",
                summary="The blueprint is complete and causally specific.",
                strengths=("The ending pays off the opening image.",),
                scores=(
                    RubricScore(
                        dimension="causal_coherence",
                        score=4,
                        rationale="Every scene advances the declared arc.",
                    ),
                ),
                overall_score=4.0,
                verdict=CritiqueVerdict.PASS,
            )
        else:
            raise AssertionError(f"unexpected specialist role {role}")
        content = (
            value.model_dump_json() if hasattr(value, "model_dump_json") else json.dumps(value)
        )
        return ModelResponse(
            provider=self.provider,
            model_identifier=request.model_identifier,
            deployment=(
                ModelDeployment.CLOUD
                if request.model_identifier == "cloud-fixture"
                else ModelDeployment.LOCAL
            ),
            content=content,
            thinking=None,
            finish_reason="stop",
            created_at=datetime.now(UTC),
            usage=ModelUsage(input_tokens=300, output_tokens=500),
            timing=ModelTiming(total_ms=100),
            estimated_cost_usd=Decimal("0"),
        )

    async def list_models(self) -> tuple[ModelDescriptor, ...]:
        return ()

    async def capabilities(self, _model_identifier: str) -> ModelCapabilities:
        raise NotImplementedError

    async def close(self) -> None:
        return None


@pytest.mark.anyio
async def test_agentic_case_runs_real_blueprint_graph_to_durable_approval(
    migrated_database_path: Path,
    database_engine: Engine,
) -> None:
    corpus = load_benchmark_corpus(CORPUS_PATH)
    prompt = corpus.prompts[0]
    selection = ModelSelection(
        provider="ollama",
        model_identifier="local-fixture",
        deployment=ModelDeployment.LOCAL,
    )
    profile_id = BUILTIN_PROFILE_IDS[ModelProfileMode.LOCAL]
    profile = ModelProfileStore(create_session_factory(database_engine)).configure_profile(
        profile_id,
        local_model=selection,
        cloud_model=None,
    )
    case = BenchmarkCase(
        case_id=UUID("cccccccc-cccc-4ccc-8ccc-cccccccccccc"),
        prompt_id=prompt.prompt_id,
        prompt_version=prompt.version,
        system=BenchmarkSystem.AGENTIC,
        run_seed=prompt.random_seed,
        profile=BenchmarkProfileSnapshot.from_configuration(
            profile_id=profile.id,
            configuration=profile.configuration,
        ),
    )
    gateway = BlueprintFixtureGateway(prompt.prompt, prompt)
    service = AgenticBenchmarkBlueprintService(
        campaign_id=CAMPAIGN_ID,
        database_path=migrated_database_path,
        session_factory=create_session_factory(database_engine),
        gateway=gateway,
    )

    prepared = await service.prepare(case, prompt)
    replayed = await service.prepare(case, prompt)

    assert prepared == replayed
    assert prepared.awaiting_approval is True
    assert prepared.interrupt_id is not None
    assert len(gateway.requests) == 6
    assert all(request.response_schema is not None for request in gateway.requests)
    assert all(request.invocation.prompt_template_version == "9" for request in gateway.requests)
    brief_payload = json.loads(gateway.requests[0].messages[-1].content)
    assert brief_payload["output_invariants"] == {
        "application_assembles_authoritative_fields": [
            "original_premise",
            "story_format",
            "genres",
            "maturity",
            "required_elements",
            "forbidden_elements",
        ],
        "generate_only": [
            "interpretation",
            "assumptions",
            "tone",
            "intended_effect",
            "target_audience",
            "target_word_count",
            "target_scene_count",
            "target_significant_character_count",
            "central_dramatic_question",
            "themes",
            "style_constraints",
            "authorized_ambiguities",
        ],
        "target_word_count_range": prompt.target_word_count.model_dump(mode="json"),
    }
    brief_schema = gateway.requests[0].response_schema
    assert brief_schema is not None
    brief_properties = brief_schema.get("properties")
    assert isinstance(brief_properties, dict)
    assert set(brief_properties).isdisjoint(
        {
            "original_premise",
            "story_format",
            "genres",
            "maturity",
            "required_elements",
            "forbidden_elements",
        }
    )
    integration_request = next(
        request
        for request in gateway.requests
        if request.invocation.specialist_role == "blueprint_integrator"
    )
    integration_schema = integration_request.response_schema
    assert integration_schema is not None
    integration_properties = integration_schema.get("properties")
    assert isinstance(integration_properties, dict)
    world_summary_schema = integration_properties["world_summary"]
    beats_schema = integration_properties["beats"]
    scene_plans_schema = integration_properties["scene_plans"]
    assert isinstance(world_summary_schema, dict)
    assert isinstance(beats_schema, dict)
    assert isinstance(scene_plans_schema, dict)
    assert "maxLength" not in world_summary_schema
    assert world_summary_schema["description"] == (
        "A compact world synthesis of at most 250 words."
    )
    assert beats_schema["maxItems"] == gateway.brief.target_scene_count * 2
    assert scene_plans_schema["minItems"] == gateway.brief.target_scene_count
    assert scene_plans_schema["maxItems"] == gateway.brief.target_scene_count
    integration_payload = json.loads(integration_request.messages[-1].content)
    assert integration_payload["output_invariants"] == {
        "application_assembles_authoritative_input_artifacts": True,
        "generate_only": ["world_summary", "beats", "scene_plans"],
        "allowed_character_ids": sorted(character.id for character in gateway.blueprint.characters),
        "allowed_location_ids": sorted(location.id for location in gateway.blueprint.locations),
        "required_scene_count": gateway.brief.target_scene_count,
        "maximum_beat_count": gateway.brief.target_scene_count * 2,
        "maximum_world_summary_words": 250,
        "every_beat_id_must_appear_in_a_scene_plan": True,
    }
    world_request = next(
        request
        for request in gateway.requests
        if request.invocation.specialist_role == "world_builder"
    )
    world_payload = json.loads(world_request.messages[-1].content)
    assert world_payload["output_invariants"] == {
        "location_associated_character_ids_must_be_empty": True,
        "world_rule_relevant_character_ids_must_be_empty": True,
    }
    with create_session_factory(database_engine)() as session:
        run = session.get(WorkflowRun, prepared.workflow_run_id)
        assert run is not None
        assert run.status is RunStatus.PAUSED
        assert run.pause_reason is RunPauseReason.HUMAN_APPROVAL
        assert run.budget["per_call_output_tokens"] == 8_000
        assert session.scalar(select(func.count()).select_from(AgentInvocation)) == 6
        assert session.scalar(select(func.count()).select_from(Artifact)) == 10
        invocations = session.scalars(
            select(AgentInvocation).order_by(AgentInvocation.started_at)
        ).all()
        assert all(invocation.status is InvocationStatus.SUCCEEDED for invocation in invocations)
        assert all(invocation.input_versions for invocation in invocations)
        brief = session.scalar(
            select(Artifact).where(Artifact.artifact_type == ArtifactKind.CREATIVE_BRIEF.value)
        )
        assert brief is not None
        content = brief.versions[-1].content
        assert content["original_premise"] == prompt.prompt
        assert content["story_format"] == "short_prose"
        assert content["genres"] == list(prompt.genres)
        assert content["maturity"] == prompt.intended_maturity.value
        assert content["required_elements"] == list(prompt.required_elements)
        assert content["forbidden_elements"] == list(prompt.forbidden_shortcuts)


@pytest.mark.anyio
async def test_brief_rejects_model_attempt_to_rewrite_authoritative_fields(
    migrated_database_path: Path,
    database_engine: Engine,
) -> None:
    corpus = load_benchmark_corpus(CORPUS_PATH)
    prompt = corpus.prompts[0]
    selection = ModelSelection(
        provider="ollama",
        model_identifier="local-fixture",
        deployment=ModelDeployment.LOCAL,
    )
    profile_id = BUILTIN_PROFILE_IDS[ModelProfileMode.LOCAL]
    profile = ModelProfileStore(create_session_factory(database_engine)).configure_profile(
        profile_id,
        local_model=selection,
        cloud_model=None,
    )
    case = BenchmarkCase(
        case_id=UUID("dddddddd-dddd-4ddd-8ddd-dddddddddddd"),
        prompt_id=prompt.prompt_id,
        prompt_version=prompt.version,
        system=BenchmarkSystem.AGENTIC,
        run_seed=prompt.random_seed,
        profile=BenchmarkProfileSnapshot.from_configuration(
            profile_id=profile.id,
            configuration=profile.configuration,
        ),
    )
    gateway = BlueprintFixtureGateway(prompt.prompt, prompt)
    gateway.brief_response_overrides["required_elements"] = ["A paraphrased requirement."]
    service = AgenticBenchmarkBlueprintService(
        campaign_id=CAMPAIGN_ID,
        database_path=migrated_database_path,
        session_factory=create_session_factory(database_engine),
        gateway=gateway,
    )

    with pytest.raises(RetryableSpecialistError):
        await service.prepare(case, prompt)

    with create_session_factory(database_engine)() as session:
        invocations = session.scalars(
            select(AgentInvocation).order_by(AgentInvocation.started_at)
        ).all()
        assert len(invocations) == 2
        assert all(
            invocation.error_code == "schema_validation_failed" for invocation in invocations
        )
        assert all(invocation.schema_validation_succeeded is False for invocation in invocations)
        assert [invocation.retry_count for invocation in invocations] == [0, 1]
        assert all(invocation.output_tokens == 500 for invocation in invocations)
        assert all(
            invocation.request_settings["provider_finish_reason"] == "stop"
            for invocation in invocations
        )
        assert all(
            len(invocation.request_settings["provider_response_content_sha256"]) == 64
            for invocation in invocations
        )
    retry_payload = json.loads(gateway.requests[1].messages[-1].content)
    assert retry_payload["retry_context"]["attempt_number"] == 2
    assert (
        retry_payload["retry_context"]["previous_failure"]["error_code"]
        == "schema_validation_failed"
    )
    assert (
        "required_elements:extra_forbidden"
        in (retry_payload["retry_context"]["previous_failure"]["message"])
    )
