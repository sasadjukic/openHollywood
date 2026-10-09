"""Cancellation cleanup must outlive graph wrappers and stay scoped to one call."""

from __future__ import annotations

import asyncio
from pathlib import Path
from threading import Event
from typing import Any

import pytest
from open_hollywood_api.persistence.database import create_session_factory
from open_hollywood_api.persistence.models import AgentInvocation, InvocationStatus
from open_hollywood_api.services.production_model_executor import ProfileRoutedProductionExecutor
from open_hollywood_api.services.workflow_cancellation import (
    finish_cleanup,
    run_with_invocation_cleanup,
    tracked_invocation,
)
from open_hollywood_engine.evaluations import load_benchmark_corpus
from open_hollywood_engine.models import ModelRequest, ModelResponse
from sqlalchemy import Engine, select

from tests.api.test_production_v26 import V26Gateway, _run_gateway
from tests.evaluations.test_agentic_blueprint import CORPUS_PATH

pytestmark = pytest.mark.anyio


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.mark.parametrize("cleanup_fails", [False, True])
@pytest.mark.parametrize("graph_cancels_leaf", [False, True])
async def test_graph_waits_for_cleanup_and_preserves_failure(
    cleanup_fails: bool, graph_cancels_leaf: bool
) -> None:
    started = asyncio.Event()
    cleaning = asyncio.Event()
    release = asyncio.Event()
    leaves: list[asyncio.Task[None]] = []

    async def persist() -> None:
        cleaning.set()
        await release.wait()
        if cleanup_fails:
            raise OSError("synthetic persistence failure")

    @tracked_invocation
    async def specialist() -> None:
        started.set()
        try:
            await asyncio.Event().wait()
        except asyncio.CancelledError:
            await finish_cleanup(persist())
            raise

    async def early_returning_graph() -> None:
        leaf = asyncio.create_task(specialist())
        leaves.append(leaf)
        await started.wait()
        if graph_cancels_leaf:
            leaf.cancel()
        raise asyncio.CancelledError("graph stopped before its leaf")

    graph = asyncio.create_task(run_with_invocation_cleanup(early_returning_graph()))
    try:
        await asyncio.wait_for(cleaning.wait(), timeout=2)
        leaves[0].cancel()
        graph.cancel()  # A second shutdown must still wait for durable cleanup.
        with pytest.raises(TimeoutError):
            await asyncio.wait_for(asyncio.shield(graph), timeout=0.03)
    finally:
        release.set()
    with pytest.raises(OSError if cleanup_fails else asyncio.CancelledError):
        await asyncio.wait_for(graph, timeout=2)
    assert all(task.done() for task in leaves)


async def test_cleanup_scopes_do_not_wait_for_another_workflow() -> None:
    other_started = asyncio.Event()
    other_release = asyncio.Event()

    @tracked_invocation
    async def other_specialist() -> str:
        other_started.set()
        await other_release.wait()
        return "other"

    async def other_graph() -> str:
        return await asyncio.create_task(other_specialist())

    @tracked_invocation
    async def failing_specialist() -> None:
        raise ValueError("this workflow failed")

    async def failing_graph() -> None:
        await asyncio.create_task(failing_specialist())

    other = asyncio.create_task(run_with_invocation_cleanup(other_graph()))
    try:
        await asyncio.wait_for(other_started.wait(), timeout=2)
        with pytest.raises(ValueError, match="this workflow failed"):
            await asyncio.wait_for(run_with_invocation_cleanup(failing_graph()), timeout=2)
        assert not other.done()
    finally:
        other_release.set()
        assert await asyncio.wait_for(other, timeout=2) == "other"


async def test_production_service_persists_cancellation_before_closing_its_database(
    monkeypatch: pytest.MonkeyPatch,
    migrated_database_path: Path,
    database_engine: Engine,
) -> None:
    started = asyncio.Event()
    cleaning = asyncio.Event()
    release = Event()
    loop = asyncio.get_running_loop()
    fail = ProfileRoutedProductionExecutor._fail_invocation

    def delayed_failure(self: ProfileRoutedProductionExecutor, *args: Any, **kwargs: Any) -> None:
        loop.call_soon_threadsafe(cleaning.set)
        if not release.wait(timeout=5):
            raise TimeoutError("test did not release production cleanup")
        fail(self, *args, **kwargs)

    class BlockingGateway(V26Gateway):
        async def generate(self, request: ModelRequest) -> ModelResponse:
            if request.invocation.specialist_role == "scene_writer":
                started.set()
                await asyncio.Event().wait()
            return await super().generate(request)

    monkeypatch.setattr(ProfileRoutedProductionExecutor, "_fail_invocation", delayed_failure)
    prompt = load_benchmark_corpus(CORPUS_PATH).prompts[0]
    gateway = BlockingGateway(prompt.prompt, prompt, mode="thread_echo")
    running = asyncio.create_task(_run_gateway(gateway, migrated_database_path, database_engine))
    try:
        await asyncio.wait_for(started.wait(), timeout=5)
        running.cancel()
        await asyncio.wait_for(cleaning.wait(), timeout=5)
        running.cancel()
        with pytest.raises(TimeoutError):
            await asyncio.wait_for(asyncio.shield(running), timeout=0.03)
    finally:
        release.set()
    with pytest.raises(asyncio.CancelledError):
        await asyncio.wait_for(running, timeout=5)
    with create_session_factory(database_engine)() as session:
        invocation = session.scalar(
            select(AgentInvocation).where(AgentInvocation.specialist_role == "scene_writer")
        )
        assert invocation is not None
        assert invocation.status is InvocationStatus.FAILED
        assert invocation.error_code == "cancelled_execution"
        assert invocation.completed_at is not None and not invocation.output_versions
