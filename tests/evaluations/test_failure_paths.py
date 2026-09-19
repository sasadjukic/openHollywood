"""Injected Cloud faults and durable recovery, without live provider calls."""

from __future__ import annotations

import errno
import json
from pathlib import Path
from uuid import UUID, uuid4

import httpx
import pytest
from open_hollywood_api.persistence.database import create_session_factory
from open_hollywood_api.persistence.models import (
    AgentInvocation,
    ArtifactVersion,
    InvocationStatus,
    RunStatus,
    WorkflowRun,
)
from open_hollywood_api.persistence.secret_policy import audit_database_export
from open_hollywood_api.services.agentic_benchmark import AgenticBenchmarkBlueprintService
from open_hollywood_api.services.blueprint_model_executor import ProfileRoutedBlueprintNodeExecutor
from open_hollywood_api.services.blueprint_workflow import (
    BlueprintWorkflowService,
    SqlAlchemyBlueprintWorkflowObserver,
)
from open_hollywood_api.services.evaluation_execution import DirectBaselineBenchmarkExecutor
from open_hollywood_api.services.model_profiles import BUILTIN_PROFILE_IDS, ModelProfileStore
from open_hollywood_api.services.production_model_executor import ProfileRoutedProductionExecutor
from open_hollywood_api.services.production_workflow import (
    SceneProductionService,
    SqlAlchemySceneProductionObserver,
)
from open_hollywood_engine.artifacts import ArtifactKind
from open_hollywood_engine.evaluations import (
    BenchmarkCaseExecutionError,
    BenchmarkRunReport,
    run_benchmark_plan,
)
from open_hollywood_engine.models import (
    ModelCostBasis,
    ModelDeployment,
    ModelGatewayError,
    ModelGatewayErrorCode,
    ModelProfileMode,
    ModelRequest,
    ModelResponse,
    ModelSelection,
    OllamaGateway,
    OllamaHost,
)
from open_hollywood_engine.secrets import SecretValue
from open_hollywood_engine.workflows import (
    ArtifactReference,
    BlueprintDecisionAction,
    BlueprintHumanDecision,
    BlueprintNode,
    BlueprintWorkflowError,
    ProductionNode,
    SceneProductionError,
)
from sqlalchemy import Engine, select

from scripts.evaluation_harness import ATOMIC_REPLACE_ATTEMPTS, AtomicJsonReportCheckpoint
from tests.evaluations.test_agentic_blueprint import BlueprintFixtureGateway
from tests.evaluations.test_agentic_production import ProductionFixtureGateway
from tests.evaluations.test_harness import FixtureGateway
from tests.evaluations.test_scoped_campaigns import cloud_plan


def _configure_cloud(engine: Engine) -> None:
    ModelProfileStore(create_session_factory(engine)).configure_profile(
        BUILTIN_PROFILE_IDS[ModelProfileMode.CLOUD],
        local_model=None,
        cloud_model=ModelSelection(
            provider="ollama", model_identifier="cloud-fixture", deployment=ModelDeployment.CLOUD
        ),
    )


@pytest.mark.anyio
@pytest.mark.parametrize("path", ["baseline", "blueprint"])
@pytest.mark.parametrize(
    "fault,code,attempts",
    [
        ("401", "authentication", 1),
        ("403", "authentication", 1),
        ("404", "model_not_found", 1),
        ("429", "rate_limited", 2),
        ("503", "provider_unavailable", 2),
        ("offline", "provider_unavailable", 2),
        ("timeout", "provider_timeout", 2),
        ("invalid_json", "invalid_response", 1),
    ],
)
async def test_cloud_faults_persist_terminal_attempts_without_unbounded_retry(
    path: str,
    fault: str,
    code: str,
    attempts: int,
    migrated_database_path: Path,
    database_engine: Engine,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    corpus, plan = cloud_plan()
    prompt = corpus.prompts[0]
    case = next(c for c in plan.cases if c.target_key == path.replace("blueprint", "cloud"))
    sessions = create_session_factory(database_engine)
    _configure_cloud(database_engine)
    secret = "failure-test-credential-never-export"
    monkeypatch.setenv("OLLAMA_API_KEY", secret)
    requests: list[httpx.Request] = []

    def fail(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/chat"
        requests.append(request)
        if fault == "offline":
            raise httpx.ConnectError(secret, request=request)
        if fault == "timeout":
            raise httpx.ReadTimeout(secret, request=request)
        if fault == "invalid_json":
            return httpx.Response(200, content="not JSON")
        return httpx.Response(int(fault), json={"error": f"private provider body {secret}"})

    async with OllamaGateway(
        host=OllamaHost.CLOUD,
        api_key=SecretValue(secret),
        transport=httpx.MockTransport(fail),
    ) as gateway:
        with pytest.raises((BenchmarkCaseExecutionError, BlueprintWorkflowError)):
            if path == "baseline":
                await DirectBaselineBenchmarkExecutor(
                    campaign_id=plan.campaign_id, session_factory=sessions, gateway=gateway
                ).execute(case, prompt)
            else:
                await AgenticBenchmarkBlueprintService(
                    campaign_id=plan.campaign_id,
                    database_path=migrated_database_path,
                    session_factory=sessions,
                    gateway=gateway,
                ).prepare(case, prompt)

    assert len(requests) == (1 if path == "baseline" else attempts)
    with sessions() as session:
        invocations = session.scalars(select(AgentInvocation)).all()
        assert len(invocations) == len(requests)
        assert all(i.status is InvocationStatus.FAILED for i in invocations)
        assert all(i.error_code == code and i.completed_at is not None for i in invocations)
        assert all(i.cost_basis is ModelCostBasis.UNKNOWN for i in invocations)
        assert all(not i.output_versions and i.input_versions for i in invocations)
        assert all(secret not in (i.error_message or "") for i in invocations)
        assert all("private provider body" not in (i.error_message or "") for i in invocations)
        run = session.scalar(select(WorkflowRun))
        assert run and run.status is RunStatus.FAILED
        assert secret not in (run.error_message or "")
    audit_database_export(database_engine)


class SimulatedProcessExit(BaseException):
    """Bypass ordinary exception/cancellation cleanup as process loss would."""


class InterruptedBlueprintGateway(BlueprintFixtureGateway):
    async def generate(self, request: ModelRequest) -> ModelResponse:
        if request.invocation.specialist_role == "premise_architect":
            raise SimulatedProcessExit
        return await super().generate(request)


@pytest.mark.anyio
@pytest.mark.parametrize("boundary", ["open_call", "committed_output"])
async def test_blueprint_restart_reconciles_open_call_and_preserves_completed_work(
    boundary: str,
    migrated_database_path: Path,
    database_engine: Engine,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    corpus, plan = cloud_plan()
    prompt = corpus.prompts[0]
    case = next(c for c in plan.cases if c.target_key == "cloud")
    sessions = create_session_factory(database_engine)
    _configure_cloud(database_engine)
    interrupted = AgenticBenchmarkBlueprintService(
        campaign_id=plan.campaign_id,
        database_path=migrated_database_path,
        session_factory=sessions,
        gateway=(
            InterruptedBlueprintGateway if boundary == "open_call" else BlueprintFixtureGateway
        )(prompt.prompt, prompt),
    )
    original_completed = SqlAlchemyBlueprintWorkflowObserver.node_completed

    async def interrupt_after_commit(
        observer: SqlAlchemyBlueprintWorkflowObserver,
        run_id: UUID,
        node: BlueprintNode,
        artifacts: tuple[ArtifactReference, ...],
    ) -> None:
        if node is BlueprintNode.PREMISE:
            raise SimulatedProcessExit
        await original_completed(observer, run_id, node, artifacts)

    with monkeypatch.context() as patch:
        if boundary == "committed_output":
            patch.setattr(
                SqlAlchemyBlueprintWorkflowObserver, "node_completed", interrupt_after_commit
            )
        with pytest.raises(SimulatedProcessExit):
            await interrupted.prepare(case, prompt)
    with sessions() as session:
        pending = session.scalar(
            select(AgentInvocation).where(AgentInvocation.specialist_role == "premise_architect")
        )
        assert pending is not None
        interrupted_id = pending.id
        prior_versions = {v.id: v.content_sha256 for v in session.scalars(select(ArtifactVersion))}

    gateway = BlueprintFixtureGateway(prompt.prompt, prompt)
    resumed = AgenticBenchmarkBlueprintService(
        campaign_id=plan.campaign_id,
        database_path=migrated_database_path,
        session_factory=sessions,
        gateway=gateway,
    )
    prepared = await resumed.prepare(case, prompt)
    assert await resumed.prepare(case, prompt) == prepared
    assert prepared.awaiting_approval
    assert len(gateway.requests) == (5 if boundary == "open_call" else 4)
    if boundary == "open_call":
        retried_premise = next(
            r for r in gateway.requests if r.invocation.specialist_role == "premise_architect"
        )
        assert "retry_context" not in json.loads(retried_premise.messages[-1].content)
    with sessions() as session:
        pending = session.get(AgentInvocation, interrupted_id)
        assert pending is not None
        if boundary == "open_call":
            assert pending.status is InvocationStatus.FAILED
            assert pending.error_code == "interrupted_execution"
            assert pending.request_settings["interruption"]["provider_outcome"] == "unknown"
        else:
            assert pending.status is InvocationStatus.SUCCEEDED
            assert pending.error_code is None
        assert pending.completed_at is not None
        assert pending.cost_basis is ModelCostBasis.UNKNOWN
        assert not session.scalar(
            select(AgentInvocation).where(AgentInvocation.status == InvocationStatus.RUNNING)
        )
        versions = {v.id: v.content_sha256 for v in session.scalars(select(ArtifactVersion))}
        assert prior_versions.items() <= versions.items()


class FaultedProductionGateway(ProductionFixtureGateway):
    fault = "open_call"
    failures = 0

    async def generate(self, request: ModelRequest) -> ModelResponse:
        assignment = json.loads(request.messages[-1].content).get("assignment", {})
        if assignment.get("unit_number") == 2 and assignment.get("operation") == "continuity":
            self.failures += 1
            if self.fault == "open_call":
                raise SimulatedProcessExit
            raise ModelGatewayError(
                ModelGatewayErrorCode.PROVIDER_TIMEOUT, "injected timeout", retryable=True
            )
        return await super().generate(request)


@pytest.mark.anyio
@pytest.mark.parametrize("boundary", ["open_call", "timeout_exhausted", "committed_output"])
async def test_production_recovery_keeps_accepted_scene_and_exact_artifact_lineage(
    boundary: str,
    migrated_database_path: Path,
    database_engine: Engine,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    corpus, plan = cloud_plan()
    prompt = corpus.prompts[0]
    case = next(c for c in plan.cases if c.target_key == "cloud")
    sessions = create_session_factory(database_engine)
    _configure_cloud(database_engine)
    gateway = ProductionFixtureGateway(prompt.prompt, prompt)
    prepared = await AgenticBenchmarkBlueprintService(
        campaign_id=plan.campaign_id,
        database_path=migrated_database_path,
        session_factory=sessions,
        gateway=gateway,
    ).prepare(case, prompt)
    assert prepared.interrupt_id
    async with BlueprintWorkflowService(
        migrated_database_path,
        sessions,
        ProfileRoutedBlueprintNodeExecutor(session_factory=sessions, gateway=gateway),
    ) as blueprint_service:
        approved = await blueprint_service.resume(
            prepared.workflow_run_id,
            BlueprintHumanDecision(
                id=uuid4(),
                interrupt_id=prepared.interrupt_id,
                action=BlueprintDecisionAction.APPROVE,
            ),
        )
    blueprint = next(a for a in approved.artifacts if a.kind is ArtifactKind.STORY_BLUEPRINT)
    broken_gateway = FaultedProductionGateway(prompt.prompt, prompt)
    broken_gateway.fault = boundary
    original_completed = SqlAlchemySceneProductionObserver.node_completed

    async def interrupt_after_commit(
        observer: SqlAlchemySceneProductionObserver,
        run_id: UUID,
        node: ProductionNode,
        artifacts: tuple[ArtifactReference, ...],
    ) -> None:
        if node is ProductionNode.CONTINUITY:
            with sessions() as session:
                if any(
                    (v := session.get(ArtifactVersion, a.version_id)) is not None
                    and v.content.get("scene_number") == 2
                    for a in artifacts
                ):
                    raise SimulatedProcessExit
        await original_completed(observer, run_id, node, artifacts)

    with monkeypatch.context() as patch:
        if boundary == "committed_output":
            patch.setattr(
                SqlAlchemySceneProductionObserver, "node_completed", interrupt_after_commit
            )
        async with SceneProductionService(
            database_path=migrated_database_path,
            session_factory=sessions,
            executor=ProfileRoutedProductionExecutor(
                session_factory=sessions,
                gateway=gateway if boundary == "committed_output" else broken_gateway,
            ),
        ) as production:
            with pytest.raises(
                SceneProductionError if boundary == "timeout_exhausted" else SimulatedProcessExit
            ):
                await production.execute(prepared.workflow_run_id, blueprint)
    assert broken_gateway.failures == (
        2 if boundary == "timeout_exhausted" else 1 if boundary == "open_call" else 0
    )
    with sessions() as session:
        run = session.scalar(
            select(WorkflowRun).where(
                WorkflowRun.parent_workflow_run_id == prepared.workflow_run_id
            )
        )
        assert run is not None
        run_id = run.id
        assert run.status is (
            RunStatus.FAILED if boundary == "timeout_exhausted" else RunStatus.RUNNING
        )
        prior_versions = {v.id: v.content_sha256 for v in session.scalars(select(ArtifactVersion))}
        approved_scenes = [
            v.id
            for v in session.scalars(select(ArtifactVersion))
            if v.artifact.artifact_type == "scene_draft" and v.artifact.status.value == "approved"
        ]
        assert len(approved_scenes) == 1
        failed_calls = session.scalars(
            select(AgentInvocation).where(
                AgentInvocation.workflow_run_id == run_id,
                AgentInvocation.status != InvocationStatus.SUCCEEDED,
            )
        ).all()
        failure_ids = {i.id for i in failed_calls}
        assert len(failure_ids) == broken_gateway.failures
        if boundary == "timeout_exhausted":
            assert all(i.error_code == "provider_timeout" for i in failed_calls)
            assert len({tuple(v.id for v in i.input_versions) for i in failed_calls}) == 1

    recovered_gateway = ProductionFixtureGateway(prompt.prompt, prompt)
    async with SceneProductionService(
        database_path=migrated_database_path,
        session_factory=sessions,
        executor=ProfileRoutedProductionExecutor(
            session_factory=sessions, gateway=recovered_gateway
        ),
    ) as production:
        recovered = await production.execute(prepared.workflow_run_id, blueprint)
        assert await production.execute(prepared.workflow_run_id, blueprint) == recovered
    assert recovered.result is not None
    assert len(recovered.result.accepted_units) == 3
    assert recovered.result.accepted_units[0].artifact.version_id == approved_scenes[0]
    assignments = [
        json.loads(r.messages[-1].content)["assignment"] for r in recovered_gateway.requests
    ]
    assert all(a["unit_number"] >= 2 for a in assignments)
    assert not any(
        a["unit_number"] == 2 and a["operation"] in {"write", "critique"} for a in assignments
    )
    if boundary == "committed_output":
        assert not any(
            a["unit_number"] == 2 and a["operation"] == "continuity" for a in assignments
        )
    with sessions() as session:
        assert (
            prior_versions.items()
            <= {v.id: v.content_sha256 for v in session.scalars(select(ArtifactVersion))}.items()
        )
        calls = session.scalars(select(AgentInvocation)).all()
        assert not any(i.status is InvocationStatus.RUNNING for i in calls)
        assert all(i.cost_basis is ModelCostBasis.UNKNOWN for i in calls if i.id in failure_ids)
        assert len([i for i in calls if i.id in failure_ids]) == len(failure_ids)
    audit_database_export(database_engine)


@pytest.mark.anyio
@pytest.mark.parametrize("fault", ["disk_full", "locked"])
async def test_report_write_failure_preserves_prior_bytes_and_replays_persisted_story(
    fault: str,
    tmp_path: Path,
    database_engine: Engine,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from tests.evaluations.test_cost_evidence import response

    corpus, plan = cloud_plan()
    baseline = tuple(c for c in plan.cases if c.target_key == "baseline")[:2]
    gateway = FixtureGateway(response())
    executor = DirectBaselineBenchmarkExecutor(
        campaign_id=plan.campaign_id,
        session_factory=create_session_factory(database_engine),
        gateway=gateway,
    )
    path = tmp_path / "report.json"
    checkpoint = AtomicJsonReportCheckpoint(path, plan)
    first = await run_benchmark_plan(
        plan=plan,
        corpus=corpus,
        executor=executor,
        case_ids=frozenset({baseline[0].case_id}),
        checkpoint=checkpoint,
    )
    saved = path.read_bytes()
    attempts = 0
    original_write = Path.write_bytes

    def reject_replace(source: Path, target: Path) -> Path:
        nonlocal attempts
        attempts += 1
        raise PermissionError("injected persistent file lock")

    def disk_full_write(target: Path, content: bytes) -> int:
        nonlocal attempts
        attempts += 1
        original_write(target, content[:10])
        raise OSError(errno.ENOSPC, "injected disk full")

    with monkeypatch.context() as patch:
        if fault == "locked":
            patch.setattr(Path, "replace", reject_replace)
        else:
            patch.setattr(Path, "write_bytes", disk_full_write)
        with pytest.raises(OSError):
            await run_benchmark_plan(
                plan=plan,
                corpus=corpus,
                executor=executor,
                prior_results=first.results,
                case_ids=frozenset(c.case_id for c in baseline),
                checkpoint=checkpoint,
            )
    assert attempts == (ATOMIC_REPLACE_ATTEMPTS if fault == "locked" else 1)
    assert path.read_bytes() == saved
    assert not tuple(tmp_path.glob(".*.tmp"))
    assert not tuple(tmp_path.glob(".*.lock"))
    assert len(gateway.requests) == 2
    recovered = await run_benchmark_plan(
        plan=plan,
        corpus=corpus,
        executor=executor,
        prior_results=first.results,
        case_ids=frozenset(c.case_id for c in baseline),
        checkpoint=checkpoint,
    )
    assert len(gateway.requests) == 2
    assert len(recovered.results) == 2
    assert recovered.results[0] == first.results[0]
    assert BenchmarkRunReport.model_validate(json.loads(path.read_bytes())) == recovered
