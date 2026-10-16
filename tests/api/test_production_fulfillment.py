"""Local handoff qualification with exact artifacts, real SQLite and a fake gateway."""

from __future__ import annotations

import asyncio
import json
from copy import deepcopy
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

import pytest
from open_hollywood_api.persistence.database import create_session_factory
from open_hollywood_api.persistence.models import (
    AgentInvocation,
    ArtifactVersion,
    InvocationStatus,
    WorkflowRun,
    agent_invocation_inputs,
)
from open_hollywood_api.services.production_fulfillment import (
    FULFILLMENT_POLICY,
    MAX_PACKET_BYTES,
    packet_bytes,
    project_fulfillment,
)
from open_hollywood_api.services.production_fulfillment_store import FulfillmentIntegrityError
from open_hollywood_api.services.production_model_executor import (
    ProfileRoutedProductionExecutor,
    _critic_evidence_catalog,
    _draft_evidence_catalog,
    _messages,
    _messages_sha256,
    _Operation,
    _output_schema,
    _reference,
    _scene_assignment_contract,
    _scene_boundary_audit,
    _writing_inputs,
)
from open_hollywood_api.services.workflow_recovery import reconcile_interrupted_invocations
from open_hollywood_engine.evaluations import canonical_sha256, load_benchmark_corpus
from open_hollywood_engine.models import ModelRequest, ModelResponse
from open_hollywood_engine.secrets import SecretLeakError
from open_hollywood_engine.workflows import (
    ArtifactReference,
    RetryableSceneProductionError,
    SceneDraftResult,
    SceneProductionError,
    SceneWritingTask,
)
from sqlalchemy import Engine, delete, func, insert, select
from sqlalchemy.orm import Session, sessionmaker

from tests.api.test_production_v26 import V26Gateway, _run_gateway
from tests.api.test_production_v31 import RepairGateway
from tests.api.test_production_v34 import ContinuityContractGateway
from tests.api.test_production_v37 import _fixture
from tests.api.test_production_v58 import _wire
from tests.evaluations.test_agentic_blueprint import CORPUS_PATH


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


def _projection_inputs() -> dict[str, Any]:
    execution = _fixture("She chose to investigate; she also established the forbidden match.")
    raw = _wire(execution, unmet=False)
    audit = _scene_boundary_audit(raw, execution)
    return {
        "audit": audit,
        "assignment": _scene_assignment_contract(execution),
        "catalog": _critic_evidence_catalog(execution),
        "critique_version_id": str(uuid4()),
        "draft_version_id": audit["candidate_version_id"],
        "plan_version_id": audit["current_plan_version_id"],
        "response_sha256": "a" * 64,
    }


def test_projection_preserves_complete_defective_excerpt_and_exact_policy() -> None:
    kwargs = _projection_inputs()
    before = deepcopy(kwargs)
    result = project_fulfillment(**kwargs)
    assert result.packet is not None and result.reason == "included"
    assert result.packet["policy"] == FULFILLMENT_POLICY
    assert len(result.packet["requirements"]) == 2
    for record in result.packet["requirements"]:
        assert record["evidence"] == list(kwargs["catalog"])
        assert "forbidden match" in record["evidence"][0]["exact_excerpt"]
        assert record["assigned_requirement"] == kwargs["assignment"][record["requirement"]]
    assert kwargs == before


@pytest.mark.parametrize(
    "bad",
    [
        "missing",
        "unsupported",
        "wrong_draft",
        "wrong_plan",
        "absent_anchor",
        "extra_anchor",
        "duplicate",
        "invented",
        "stale",
        "blank",
        "long",
        "partial",
        "met_advice",
        "unmet_no_advice",
        "diagnostic_field",
        "wrong_origin",
    ],
)
def test_malformed_second_check_omits_whole_packet(bad: str) -> None:
    kwargs = _projection_inputs()
    audit = kwargs["audit"]
    check = audit["assignment_checks"]["outcome"]
    if bad == "missing":
        kwargs["audit"] = None
    elif bad == "unsupported":
        audit["schema_version"] = "6"
    elif bad in {"wrong_draft", "wrong_plan"}:
        audit["candidate_version_id" if bad == "wrong_draft" else "current_plan_version_id"] = str(
            uuid4()
        )
    elif bad == "absent_anchor":
        del audit["assignment_checks"]["outcome"]
    elif bad == "extra_anchor":
        audit["assignment_checks"]["voice"] = deepcopy(check)
    elif bad in {"duplicate", "invented", "stale"}:
        refs = check["draft_evidence_refs"]
        check["draft_evidence_refs"] = (
            refs * 2
            if bad == "duplicate"
            else ["draft_evidence_0001" + ("_" + uuid4().hex if bad == "stale" else "_invented")]
        )
    elif bad in {"blank", "long"}:
        check["assessment"] = " " if bad == "blank" else "a" * 601
    elif bad == "partial":
        check["status"] = "partial"
    elif bad == "met_advice":
        check["recommended_resolution"] = "Do something."
    elif bad == "unmet_no_advice":
        check["status"] = "unmet"
    elif bad == "diagnostic_field":
        check["failed_clause"] = "Imported diagnostic"
    else:
        audit["repair_advice_origin"] = "unknown"
    assert project_fulfillment(**kwargs).packet is None


def test_unmet_compound_requirement_is_never_partially_certified() -> None:
    kwargs = _projection_inputs()
    kwargs["assignment"]["outcome"] = "Decide to verify, and remain without proof."
    check = kwargs["audit"]["assignment_checks"]["outcome"]
    check.update(
        status="unmet",
        assessment="Decision met; endpoint unmet.",
        recommended_resolution="Remove proof.",
    )
    result = project_fulfillment(**kwargs)
    assert result.packet is not None
    assert [r["requirement"] for r in result.packet["requirements"]] == ["turning_point"]
    kwargs["audit"]["assignment_checks"]["turning_point"].update(
        status="unmet", recommended_resolution="Restore realization."
    )
    assert project_fulfillment(**kwargs).reason == "no_met_requirements"
    kwargs["assignment"]["turning_point"] = None
    kwargs["assignment"]["outcome"] = None
    kwargs["audit"]["assignment_checks"] = {}
    assert project_fulfillment(**kwargs).reason == "no_met_requirements"


class HandoffGateway(RepairGateway):
    sessions: sessionmaker[Session]
    mode_revision = "valid"
    revision_calls = 0
    invalid_initial_critic = False
    initial_critic_calls = 0

    async def generate(self, request: ModelRequest) -> ModelResponse:
        payload = json.loads(request.messages[-1].content)
        assignment = payload.get("assignment", {})
        revision = assignment.get("operation") == "write" and assignment["revision_number"] > 0
        if revision:
            self.revision_calls += 1
            with self.sessions() as session:
                running = list(
                    session.scalars(
                        select(AgentInvocation).where(
                            AgentInvocation.status == InvocationStatus.RUNNING
                        )
                    )
                )
                assert len(running) == 1
                invocation = running[0]
                assert invocation.prompt_sha256 == _messages_sha256(request.messages)
                assert invocation.prompt_text == "\n\n".join(m.content for m in request.messages)
                handoff = invocation.request_settings.get("writer_fulfillment_handoff")
                if request.invocation.prompt_template_version == "61":
                    assert handoff is not None
                    assert handoff["packet"] == payload["revision_contract"].get(
                        "latest_fulfilled_requirements"
                    )
                    assert canonical_sha256(handoff["packet"]) == handoff["packet_sha256"]
                else:
                    assert handoff is None
            if self.mode_revision == "cancel":
                raise asyncio.CancelledError
        response = await super().generate(request)
        if (
            assignment.get("operation") == "critique"
            and assignment["unit_number"] == 1
            and assignment["revision_number"] == 0
        ):
            self.initial_critic_calls += 1
            if self.invalid_initial_critic and self.initial_critic_calls == 1:
                return replace(response, content="{}")
        if revision and (
            self.mode_revision == "invalid"
            or (self.mode_revision == "invalid_once" and self.revision_calls == 1)
        ):
            return replace(response, content="{}")
        return response


@dataclass
class Prepared:
    task: SceneWritingTask
    executor: ProfileRoutedProductionExecutor
    gateway: HandoffGateway
    sessions: sessionmaker[Session]

    def execution(self) -> Any:
        return self.executor._load_execution(
            _Operation.WRITE, self.task, _writing_inputs(self.task)
        )

    def source(self, session: Session) -> AgentInvocation:
        assert self.task.previous_critique is not None
        critique = session.get(ArtifactVersion, self.task.previous_critique.version_id)
        assert critique is not None and critique.created_by_invocation_id is not None
        source = session.get(AgentInvocation, critique.created_by_invocation_id)
        assert source is not None
        return source


@pytest.fixture
async def prepared(
    migrated_database_path: Path,
    database_engine: Engine,
    monkeypatch: pytest.MonkeyPatch,
    request: pytest.FixtureRequest,
) -> Prepared:
    sessions = create_session_factory(database_engine)
    prompt = load_benchmark_corpus(CORPUS_PATH).prompts[0]
    gateway = HandoffGateway(prompt.prompt, prompt, repair_mode="met")
    gateway.sessions = sessions
    gateway.invalid_initial_critic = bool(getattr(request, "param", False))
    captured: list[SceneWritingTask] = []
    original = ProfileRoutedProductionExecutor.write

    async def capture(
        self: ProfileRoutedProductionExecutor, task: SceneWritingTask
    ) -> SceneDraftResult:
        if task.revision_number == 1:
            captured.append(task)
            raise SceneProductionError("fixture prepared")
        return await original(self, task)

    with monkeypatch.context() as patch:
        patch.setattr(ProfileRoutedProductionExecutor, "write", capture)
        with pytest.raises(SceneProductionError, match="fixture prepared"):
            await _run_gateway(gateway, migrated_database_path, database_engine)
    assert len(captured) == 1
    return Prepared(
        captured[0],
        ProfileRoutedProductionExecutor(session_factory=sessions, gateway=gateway),
        gateway,
        sessions,
    )


@pytest.mark.anyio
async def test_real_writer_persists_packet_before_gateway_and_replays_without_call(
    prepared: Prepared,
) -> None:
    before = prepared.execution()
    handoff = before.writer_fulfillment_handoff
    assert handoff["status"] == "included"
    assert len(handoff["packet"]["requirements"]) == 2
    result = await prepared.executor.write(prepared.task)
    assert await prepared.executor.write(prepared.task) == result
    assert prepared.gateway.revision_calls == 1
    payload = json.loads(prepared.gateway.requests[-1].messages[-1].content)
    contract = payload["revision_contract"]
    assert contract["critic_acceptance_tests"]
    assert "repair_ledger" in contract
    assert contract["latest_fulfilled_requirements"] == handoff["packet"]
    with prepared.sessions() as session:
        for invocation in session.scalars(select(AgentInvocation)):
            if invocation.request_settings.get("writer_fulfillment_handoff") is not None:
                assert invocation.specialist_role == "scene_writer"
            elif invocation.prompt_text:
                assert "latest_fulfilled_requirements" not in invocation.prompt_text
        version = session.get(ArtifactVersion, result.artifact.version_id)
        assert version is not None and "latest_fulfilled_requirements" not in version.content


@pytest.mark.anyio
@pytest.mark.parametrize("failure", ["invalid_once", "cancel"])
async def test_retry_or_cancellation_resume_reuses_pinned_snapshot(
    prepared: Prepared, failure: str
) -> None:
    prepared.gateway.mode_revision = failure
    with pytest.raises(
        asyncio.CancelledError if failure == "cancel" else RetryableSceneProductionError
    ):
        await prepared.executor.write(prepared.task)
    before = prepared.execution()
    prepared.gateway.mode_revision = "valid"
    restarted = ProfileRoutedProductionExecutor(
        session_factory=prepared.sessions, gateway=prepared.gateway
    )
    result = await restarted.write(prepared.task)
    assert await restarted.write(prepared.task) == result
    with prepared.sessions() as session:
        writers = [
            i
            for i in session.scalars(select(AgentInvocation))
            if "writer_fulfillment_handoff" in i.request_settings
        ]
        assert len(writers) == 2
        assert {i.request_settings["attempt_number"] for i in writers} == {1, 2}
        assert all(
            i.request_settings["writer_fulfillment_handoff"] == before.writer_fulfillment_handoff
            for i in writers
        )
        assert {i.request_settings["task_fingerprint"] for i in writers} == {
            before.task_fingerprint
        }


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mutation",
    ["audit", "response_hash", "snapshot", "remove_snapshot", "source_status", "source_inputs"],
)
async def test_mutation_after_failed_attempt_stops_before_another_call(
    prepared: Prepared, mutation: str
) -> None:
    prepared.gateway.mode_revision = "invalid"
    with pytest.raises(RetryableSceneProductionError):
        await prepared.executor.write(prepared.task)
    with prepared.sessions.begin() as session:
        source = prepared.source(session)
        if mutation in {"audit", "response_hash"}:
            settings = deepcopy(source.request_settings)
            if mutation == "audit":
                settings["scene_boundary_audit"]["assignment_checks"]["outcome"]["assessment"] = (
                    "Changed assessment."
                )
            else:
                settings["provider_response_content_sha256"] = "b" * 64
            source.request_settings = settings
        elif mutation == "source_status":
            source.status = InvocationStatus.FAILED
        elif mutation == "source_inputs":
            session.execute(
                delete(agent_invocation_inputs).where(
                    agent_invocation_inputs.c.agent_invocation_id == source.id,
                    agent_invocation_inputs.c.artifact_version_id == source.input_versions[-1].id,
                )
            )
        else:
            writer = next(
                i
                for i in session.scalars(select(AgentInvocation))
                if "writer_fulfillment_handoff" in i.request_settings
            )
            settings = deepcopy(writer.request_settings)
            if mutation == "snapshot":
                settings["writer_fulfillment_handoff"]["packet"]["policy"] = "Changed policy."
            else:
                settings.pop("writer_fulfillment_handoff")
            writer.request_settings = settings
    with pytest.raises(FulfillmentIntegrityError):
        await prepared.executor.write(prepared.task)
    assert prepared.gateway.revision_calls == 1


@pytest.mark.anyio
@pytest.mark.parametrize(
    "change,reason",
    [
        ("missing_audit", "missing_audit"),
        ("unsupported_audit", "unsupported_audit"),
        ("unsupported_critic", "unsupported_critic"),
        ("adjudication", "ineligible_creator"),
        ("failed", "ineligible_creator"),
        ("unvalidated", "ineligible_creator"),
        ("wrong_run", "ineligible_creator"),
        ("wrong_role", "ineligible_creator"),
        ("invalid_hash", "invalid_response_hash"),
        ("malformed_version", "unsupported_critic"),
        ("zero_met", "no_met_requirements"),
        ("malformed", "malformed_check"),
        ("wrong_draft", "stale_audit"),
        ("wrong_plan", "stale_audit"),
    ],
)
async def test_optional_source_failures_are_persisted_omissions(
    prepared: Prepared, change: str, reason: str
) -> None:
    with prepared.sessions.begin() as session:
        source = prepared.source(session)
        settings = deepcopy(source.request_settings)
        if change == "missing_audit":
            settings.pop("scene_boundary_audit")
        elif change == "unsupported_audit":
            settings["scene_boundary_audit"]["schema_version"] = "6"
        elif change == "unsupported_critic":
            settings["prompt_template_version"] = "58"
        elif change == "adjudication":
            settings["operation"] = "critic_adjudication"
        elif change == "failed":
            source.status = InvocationStatus.FAILED
        elif change == "unvalidated":
            source.schema_validation_succeeded = False
        elif change == "wrong_run":
            parent = source.workflow_run.parent_workflow_run_id
            assert parent is not None
            source.workflow_run_id = parent
        elif change == "wrong_role":
            source.specialist_role = "continuity_supervisor"
        elif change == "invalid_hash":
            settings["provider_response_content_sha256"] = "not a response hash"
        elif change == "malformed_version":
            settings["prompt_template_version"] = ["59"]
        elif change == "zero_met":
            for check in settings["scene_boundary_audit"]["assignment_checks"].values():
                check.update(status="unmet", recommended_resolution="Repair assigned fact.")
        elif change in {"wrong_draft", "wrong_plan"}:
            settings["scene_boundary_audit"][
                "candidate_version_id" if change == "wrong_draft" else "current_plan_version_id"
            ] = str(uuid4())
        else:
            settings["scene_boundary_audit"]["assignment_checks"]["outcome"]["assessment"] = ""
        source.request_settings = settings
    execution = prepared.execution()
    handoff = execution.writer_fulfillment_handoff
    assert (
        handoff["status"] == "omitted" and handoff["reason"] == reason and handoff["packet"] is None
    )
    await prepared.executor.write(prepared.task)
    assert prepared.execution().writer_fulfillment_handoff == handoff


@pytest.mark.anyio
async def test_source_changed_between_load_and_persist_rolls_back_before_gateway(
    prepared: Prepared,
) -> None:
    execution = prepared.execution()
    with prepared.sessions.begin() as session:
        source = prepared.source(session)
        source.request_settings = {**source.request_settings, "scene_boundary_audit": None}
    schema = _output_schema(_Operation.WRITE, continuity_schema_variant=None)
    messages = _messages(
        _Operation.WRITE,
        execution,
        schema,
        continuity_schema_variant=None,
        continuity_model_context=None,
    )
    with pytest.raises(FulfillmentIntegrityError, match="before submission"):
        prepared.executor._start_invocation(_Operation.WRITE, execution, messages, None, schema)
    assert prepared.gateway.revision_calls == 0
    with prepared.sessions() as session:
        assert not any(
            i.status is InvocationStatus.RUNNING for i in session.scalars(select(AgentInvocation))
        )


@pytest.mark.anyio
async def test_v59_run_retains_legacy_request_and_successful_replay(prepared: Prepared) -> None:
    with prepared.sessions.begin() as session:
        run = session.get(WorkflowRun, prepared.task.production.workflow_run_id)
        assert run is not None
        state = dict(run.input_state)
        state.pop("production_prompt_template_version")
        run.input_state = state
    prepared.task = replace(
        prepared.task, production=replace(prepared.task.production, prompt_template_version="59")
    )
    execution = prepared.execution()
    assert (
        execution.prompt_template_version == "59" and execution.writer_fulfillment_handoff is None
    )
    prepared.gateway.mode_revision = "invalid_once"
    with pytest.raises(RetryableSceneProductionError):
        await prepared.executor.write(prepared.task)
    assert prepared.execution().attempt_number == 2
    result = await prepared.executor.write(prepared.task)
    assert await prepared.executor.write(prepared.task) == result
    assert prepared.gateway.revision_calls == 2


@pytest.mark.anyio
@pytest.mark.parametrize("prepared", [True], indirect=True)
async def test_only_validated_creator_retry_supplies_evidence(prepared: Prepared) -> None:
    assert prepared.gateway.initial_critic_calls == 2
    with prepared.sessions() as session:
        creator = prepared.source(session)
        assert creator.status is InvocationStatus.SUCCEEDED
        failures = [
            i
            for i in session.scalars(select(AgentInvocation))
            if i.specialist_role == "scene_critic" and i.status is InvocationStatus.FAILED
        ]
        assert len(failures) == 1 and not failures[0].output_versions
        source_id = str(creator.id)
    handoff = prepared.execution().writer_fulfillment_handoff
    assert handoff["status"] == "included"
    assert handoff["provenance"]["source_state"]["source_invocation_id"] == source_id


@pytest.mark.anyio
async def test_interrupted_invocation_recovery_keeps_pinned_evidence(prepared: Prepared) -> None:
    execution = prepared.execution()
    schema = _output_schema(_Operation.WRITE, continuity_schema_variant=None)
    messages = _messages(
        _Operation.WRITE,
        execution,
        schema,
        continuity_schema_variant=None,
        continuity_model_context=None,
    )
    invocation_id = prepared.executor._start_invocation(
        _Operation.WRITE, execution, messages, None, schema
    )
    with prepared.sessions.begin() as session:
        assert reconcile_interrupted_invocations(
            session, prepared.task.production.workflow_run_id
        ) == (invocation_id,)
    resumed = prepared.execution()
    assert resumed.attempt_number == 1  # Existing lost-process policy is preserved.
    assert resumed.writer_fulfillment_handoff == execution.writer_fulfillment_handoff
    result = await prepared.executor.write(prepared.task)
    assert await prepared.executor.write(prepared.task) == result
    assert prepared.gateway.revision_calls == 1


@pytest.mark.anyio
async def test_graph_keeps_existing_two_attempt_limit(
    migrated_database_path: Path, database_engine: Engine
) -> None:
    prompt = load_benchmark_corpus(CORPUS_PATH).prompts[0]
    gateway = HandoffGateway(prompt.prompt, prompt, repair_mode="met")
    gateway.sessions = create_session_factory(database_engine)
    gateway.mode_revision = "invalid"
    with pytest.raises(RetryableSceneProductionError):
        await _run_gateway(gateway, migrated_database_path, database_engine)
    assert gateway.revision_calls == 2
    with gateway.sessions() as session:
        snapshots = [
            i.request_settings["writer_fulfillment_handoff"]
            for i in session.scalars(select(AgentInvocation))
            if "writer_fulfillment_handoff" in i.request_settings
        ]
        assert len(snapshots) == 2 and snapshots[0] == snapshots[1]


@pytest.mark.anyio
async def test_continuity_only_repair_receives_packet_and_keeps_ledger(
    migrated_database_path: Path, database_engine: Engine
) -> None:
    prompt = load_benchmark_corpus(CORPUS_PATH).prompts[0]
    gateway = V26Gateway(prompt.prompt, prompt, mode="release")
    await _run_gateway(gateway, migrated_database_path, database_engine)
    contracts = [
        json.loads(r.messages[-1].content).get("revision_contract") for r in gateway.requests
    ]
    contracts = [
        c for c in contracts if c is not None and c["mode"] == "targeted_continuity_repair"
    ]
    assert contracts
    assert all(
        c["repair_ledger"] and c["latest_fulfilled_requirements"]["requirements"] for c in contracts
    )


@pytest.mark.anyio
@pytest.mark.parametrize("version", ["59", "61"])
async def test_only_deliberately_supported_critic_contracts_are_eligible(
    prepared: Prepared, version: str
) -> None:
    with prepared.sessions.begin() as session:
        source = prepared.source(session)
        source.request_settings = {**source.request_settings, "prompt_template_version": version}
    assert prepared.execution().writer_fulfillment_handoff["status"] == "included"


@pytest.mark.anyio
async def test_changed_accepted_prior_scene_version_omits_packet(
    migrated_database_path: Path,
    database_engine: Engine,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sessions = create_session_factory(database_engine)
    prompt = load_benchmark_corpus(CORPUS_PATH).prompts[0]
    gateway = ContinuityContractGateway(prompt.prompt, prompt, mode="history")
    original = ProfileRoutedProductionExecutor.write
    captured: list[SceneWritingTask] = []

    async def capture(
        self: ProfileRoutedProductionExecutor, task: SceneWritingTask
    ) -> SceneDraftResult:
        if task.revision_number == 0:
            return await original(self, task)
        assert task.unit.unit_number == 2 and len(task.accepted_units) == 1
        captured.append(task)
        raise SceneProductionError("prior scene prepared")

    monkeypatch.setattr(ProfileRoutedProductionExecutor, "write", capture)
    with pytest.raises(SceneProductionError, match="prior scene prepared"):
        await _run_gateway(gateway, migrated_database_path, database_engine)
    task = captured[0]
    executor = ProfileRoutedProductionExecutor(session_factory=sessions, gateway=gateway)
    before = executor._load_execution(_Operation.WRITE, task, _writing_inputs(task))
    assert before.writer_fulfillment_handoff is not None
    assert before.writer_fulfillment_handoff["status"] == "included"
    assert task.previous_critique is not None
    with sessions.begin() as session:
        review = session.get(ArtifactVersion, task.previous_critique.version_id)
        assert review is not None
        source = session.get(AgentInvocation, review.created_by_invocation_id)
        assert source is not None
        prior = task.accepted_units[0]
        alternate = _copy_version(session, prior)
        _replace_source_input(session, source, prior.version_id, alternate.version_id)
    after = executor._load_execution(_Operation.WRITE, task, _writing_inputs(task))
    assert after.writer_fulfillment_handoff is not None
    assert after.writer_fulfillment_handoff["reason"] == "shared_authority_mismatch"


@pytest.mark.parametrize("operation", [_Operation.WRITE, _Operation.CRITIQUE])
def test_first_drafts_and_critic_messages_are_unchanged_by_new_request_version(
    operation: _Operation,
) -> None:
    execution = _fixture()
    schema = _output_schema(operation, continuity_schema_variant=None)

    def messages(version: str) -> tuple[Any, ...]:
        return _messages(
            operation,
            replace(execution, prompt_template_version=version),
            schema,
            continuity_schema_variant=None,
            continuity_model_context=None,
        )

    assert messages("59") == messages("61")


def _copy_version(
    session: Session,
    reference: ArtifactReference,
    *,
    changes: dict[str, Any] | None = None,
    creator_id: UUID | None = None,
    bad_hash: bool = False,
) -> ArtifactReference:
    old = session.get(ArtifactVersion, reference.version_id)
    assert old is not None
    content = {**old.content, **(changes or {})}
    number = session.scalar(
        select(func.max(ArtifactVersion.version_number)).where(
            ArtifactVersion.artifact_id == old.artifact_id
        )
    )
    assert number is not None
    new = ArtifactVersion(
        id=uuid4(),
        artifact_id=old.artifact_id,
        parent_version_id=old.id,
        version_number=number + 1,
        schema_version=old.schema_version,
        content=content,
        content_sha256="a" * 64 if bad_hash else canonical_sha256(content),
        created_by_invocation_id=creator_id,
    )
    session.add(new)
    session.flush()
    return _reference(new)


def _replace_source_input(session: Session, source: AgentInvocation, old: UUID, new: UUID) -> None:
    session.execute(
        delete(agent_invocation_inputs).where(
            agent_invocation_inputs.c.agent_invocation_id == source.id,
            agent_invocation_inputs.c.artifact_version_id == old,
        )
    )
    session.execute(
        insert(agent_invocation_inputs),
        [{"agent_invocation_id": source.id, "artifact_version_id": new}],
    )


@pytest.mark.anyio
@pytest.mark.parametrize("kind", ["draft", "plan", "exit_state", "blueprint", "bible", "hash"])
async def test_source_requires_exact_versions_even_with_identical_content(
    prepared: Prepared, kind: str
) -> None:
    task = prepared.task
    assert task.previous_draft is not None
    reference = {
        "draft": task.previous_draft,
        "plan": task.unit.plan,
        "exit_state": task.unit.plan,
        "blueprint": task.production.approved_blueprint,
        "bible": task.story_bible,
        "hash": task.unit.plan,
    }[kind]
    with prepared.sessions.begin() as session:
        source = prepared.source(session)
        new = _copy_version(
            session,
            reference,
            changes={"exit_state": "Changed ending."} if kind == "exit_state" else None,
            bad_hash=kind == "hash",
        )
        _replace_source_input(session, source, reference.version_id, new.version_id)
    handoff = prepared.execution().writer_fulfillment_handoff
    assert handoff["packet"] is None
    assert handoff["reason"] == (
        "source_lineage_mismatch" if kind in {"draft", "hash"} else "shared_authority_mismatch"
    )


@pytest.mark.anyio
@pytest.mark.parametrize("kind", ["revision", "scene", "hash", "review_target"])
async def test_invalid_writer_task_is_an_error_not_optional_omission(
    prepared: Prepared, kind: str
) -> None:
    if kind == "revision":
        prepared.task = replace(prepared.task, revision_number=2)
    elif kind == "scene":
        prepared.task = replace(
            prepared.task, unit=replace(prepared.task.unit, unit_id="another_scene")
        )
    elif kind == "hash":
        with prepared.sessions.begin() as session:
            plan = _copy_version(session, prepared.task.unit.plan, bad_hash=True)
        prepared.task = replace(prepared.task, unit=replace(prepared.task.unit, plan=plan))
    else:
        assert prepared.task.previous_critique is not None
        with prepared.sessions.begin() as session:
            review = _copy_version(
                session,
                prepared.task.previous_critique,
                changes={"target_artifact_version_id": str(uuid4())},
            )
        prepared.task = replace(prepared.task, previous_critique=review, critique_history=(review,))
    with pytest.raises(SceneProductionError):
        prepared.execution()
    assert prepared.gateway.revision_calls == 0


@pytest.mark.anyio
async def test_latest_review_without_creator_does_not_reuse_older_positive_review(
    prepared: Prepared,
) -> None:
    old = prepared.task.previous_critique
    assert old is not None
    with prepared.sessions.begin() as session:
        new = _copy_version(session, old)
    prepared.task = replace(prepared.task, previous_critique=new, critique_history=(old, new))
    assert prepared.execution().writer_fulfillment_handoff["reason"] == "missing_creator"


@pytest.mark.anyio
async def test_omission_is_pinned_and_cannot_be_upgraded_on_retry(prepared: Prepared) -> None:
    with prepared.sessions.begin() as session:
        source = prepared.source(session)
        original = deepcopy(source.request_settings)
        settings = deepcopy(original)
        settings.pop("scene_boundary_audit")
        source.request_settings = settings
    prepared.gateway.mode_revision = "invalid"
    with pytest.raises(RetryableSceneProductionError):
        await prepared.executor.write(prepared.task)
    assert prepared.execution().writer_fulfillment_handoff["packet"] is None
    with prepared.sessions.begin() as session:
        prepared.source(session).request_settings = original
    with pytest.raises(FulfillmentIntegrityError):
        await prepared.executor.write(prepared.task)
    assert prepared.gateway.revision_calls == 1


@pytest.mark.anyio
@pytest.mark.parametrize("offset", [-1, 0, 1])
async def test_actual_utf8_packet_cap_omits_whole_packet_without_truncating(
    prepared: Prepared, offset: int
) -> None:
    with prepared.sessions.begin() as session:
        source = prepared.source(session)
        settings = deepcopy(source.request_settings)
        settings["scene_boundary_audit"]["assignment_checks"]["outcome"].update(
            status="unmet", recommended_resolution="Repair outcome."
        )
        source.request_settings = settings
    template = deepcopy(prepared.execution().writer_fulfillment_handoff["packet"])
    template["requirements"][0]["evidence"] = [
        {**template["requirements"][0]["evidence"][0], "exact_excerpt": "é"}
    ]
    prose = "é" + "x" * (MAX_PACKET_BYTES + offset - len(packet_bytes(template)))
    assert prepared.task.previous_draft is not None and prepared.task.previous_critique is not None
    with prepared.sessions.begin() as session:
        source = prepared.source(session)
        draft = _copy_version(session, prepared.task.previous_draft, changes={"prose": prose})
        _replace_source_input(
            session, source, prepared.task.previous_draft.version_id, draft.version_id
        )
        review = _copy_version(
            session,
            prepared.task.previous_critique,
            changes={"target_artifact_version_id": str(draft.version_id)},
            creator_id=source.id,
        )
        settings = deepcopy(source.request_settings)
        settings["scene_boundary_audit"]["candidate_version_id"] = str(draft.version_id)
        refs = [
            f"{r['evidence_ref']}_{draft.version_id.hex}" for r in _draft_evidence_catalog(prose)
        ]
        for check in settings["scene_boundary_audit"]["assignment_checks"].values():
            check["draft_evidence_refs"] = refs
        source.request_settings = settings
    prepared.task = replace(
        prepared.task, previous_draft=draft, previous_critique=review, critique_history=(review,)
    )
    handoff = prepared.execution().writer_fulfillment_handoff
    if offset > 0:
        assert handoff["packet"] is None and handoff["reason"] == "packet_too_large"
    else:
        packet = handoff["packet"]
        assert len(packet_bytes(packet)) == MAX_PACKET_BYTES + offset
        assert packet["requirements"][0]["evidence"][0]["exact_excerpt"] == prose


@pytest.mark.anyio
async def test_credential_in_exact_quote_is_security_error_not_redacted_evidence(
    prepared: Prepared, monkeypatch: pytest.MonkeyPatch
) -> None:
    packet = prepared.execution().writer_fulfillment_handoff["packet"]
    excerpt = packet["requirements"][0]["evidence"][0]["exact_excerpt"]
    monkeypatch.setenv("OLLAMA_API_KEY", excerpt)
    with pytest.raises(SecretLeakError):
        prepared.execution()
    assert prepared.gateway.revision_calls == 0


@pytest.mark.anyio
@pytest.mark.parametrize("status", [InvocationStatus.RUNNING, InvocationStatus.SUCCEEDED])
async def test_concurrent_start_cannot_duplicate_an_existing_task(
    prepared: Prepared, status: InvocationStatus
) -> None:
    execution = prepared.execution()
    schema = _output_schema(_Operation.WRITE, continuity_schema_variant=None)
    messages = _messages(
        _Operation.WRITE,
        execution,
        schema,
        continuity_schema_variant=None,
        continuity_model_context=None,
    )
    first = prepared.executor._start_invocation(_Operation.WRITE, execution, messages, None, schema)
    with prepared.sessions.begin() as session:
        invocation = session.get(AgentInvocation, first)
        assert invocation is not None
        invocation.status = status
    with pytest.raises(FulfillmentIntegrityError, match="already running or succeeded"):
        prepared.executor._start_invocation(_Operation.WRITE, execution, messages, None, schema)
    with prepared.sessions() as session:
        assert (
            len(
                [
                    i
                    for i in session.scalars(select(AgentInvocation))
                    if "writer_fulfillment_handoff" in i.request_settings
                ]
            )
            == 1
        )


@pytest.mark.anyio
async def test_stale_prepared_request_cannot_bypass_a_newly_recorded_failure(
    prepared: Prepared,
) -> None:
    stale = prepared.execution()
    prepared.gateway.mode_revision = "invalid"
    with pytest.raises(RetryableSceneProductionError):
        await prepared.executor.write(prepared.task)
    schema = _output_schema(_Operation.WRITE, continuity_schema_variant=None)
    messages = _messages(
        _Operation.WRITE,
        stale,
        schema,
        continuity_schema_variant=None,
        continuity_model_context=None,
    )
    with pytest.raises(FulfillmentIntegrityError, match="retry context changed"):
        prepared.executor._start_invocation(_Operation.WRITE, stale, messages, None, schema)
    assert prepared.gateway.revision_calls == 1
    assert prepared.execution().attempt_number == 2
