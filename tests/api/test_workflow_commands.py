"""Control writes must let the asynchronous checkpoint writer release SQLite."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

import aiosqlite
import pytest
from open_hollywood_api.persistence.database import create_session_factory
from open_hollywood_api.persistence.models import WorkflowRunControl
from open_hollywood_api.services.blueprint_workflow import BlueprintWorkflowService
from open_hollywood_api.services.production_model_executor import ProfileRoutedProductionExecutor
from open_hollywood_api.services.production_workflow import SceneProductionService
from open_hollywood_api.services.run_controls import RunControlStore
from open_hollywood_api.services.workflow_commands import QueuedWorkflowCommandService
from open_hollywood_engine.evaluations import load_benchmark_corpus
from open_hollywood_engine.workflows import RunControlAction, RunControlCommand, RunControlStatus
from sqlalchemy import Connection, Engine, event

from tests.evaluations.test_agentic_blueprint import CORPUS_PATH
from tests.evaluations.test_agentic_production import ProductionFixtureGateway
from tests.workflows.test_blueprint_workflow import PersistingExecutor, _persist_run


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.mark.anyio
@pytest.mark.parametrize(
    "action",
    [
        RunControlAction.PAUSE,
        RunControlAction.STOP,
        RunControlAction.UPDATE_BUDGET,
        RunControlAction.RESUME,
    ],
)
async def test_control_write_allows_async_checkpoint_commit_before_notifying_worker(
    action: RunControlAction,
    migrated_database_path: Path,
    database_engine: Engine,
) -> None:
    sessions = create_session_factory(database_engine)
    run_id = _persist_run(sessions)
    if action is RunControlAction.RESUME:
        RunControlStore(sessions).request_pause(
            run_id, RunControlCommand(id=uuid4(), action=RunControlAction.PAUSE)
        )
    command = RunControlCommand(
        id=uuid4(),
        action=action,
        budget_updates={"max_model_calls": 40}
        if action is RunControlAction.UPDATE_BUDGET
        else None,
    )
    loop = asyncio.get_running_loop()
    attempted = asyncio.Event()
    notifications: list[UUID] = []

    def notify_worker(notified_run: UUID = run_id) -> None:
        assert asyncio.get_running_loop() is loop
        with sessions() as session:
            record = session.get(WorkflowRunControl, command.id)
            assert record is not None and record.status.value == "applied"
        notifications.append(notified_run)

    def observe_write(
        connection: Connection,
        cursor: Any,
        statement: str,
        parameters: Any,
        context: Any,
        executemany: bool,
    ) -> None:
        if statement.startswith("INSERT INTO workflow_run_controls"):
            loop.call_soon_threadsafe(attempted.set)

    prompt = load_benchmark_corpus(CORPUS_PATH).prompts[0]
    gateway = ProductionFixtureGateway(prompt.prompt, prompt)
    commands = QueuedWorkflowCommandService(
        sessions,
        BlueprintWorkflowService(migrated_database_path, sessions, PersistingExecutor(sessions)),
        SceneProductionService(
            database_path=migrated_database_path,
            session_factory=sessions,
            executor=ProfileRoutedProductionExecutor(session_factory=sessions, gateway=gateway),
        ),
        cancel_active_run=notify_worker,
        wake_worker=notify_worker,
    )
    # Bound the unfixed failure; do not change the application's timeout.
    with database_engine.connect() as connection:
        connection.exec_driver_sql("PRAGMA busy_timeout=500")
    event.listen(database_engine, "before_cursor_execute", observe_write)
    try:
        async with aiosqlite.connect(migrated_database_path) as checkpoint:
            await checkpoint.execute("BEGIN IMMEDIATE")

            async def release_checkpoint() -> None:
                await asyncio.wait_for(attempted.wait(), timeout=2)
                await checkpoint.commit()

            release = asyncio.create_task(release_checkpoint())
            try:
                result = await commands.apply_control(run_id, command)
            finally:
                await asyncio.wait_for(release, timeout=2)
            assert result.command_status is RunControlStatus.APPLIED
            duplicate = await commands.apply_control(run_id, command)
            assert duplicate == result
    finally:
        event.remove(database_engine, "before_cursor_execute", observe_write)
    assert notifications == (
        [run_id, run_id] if action in {RunControlAction.STOP, RunControlAction.RESUME} else []
    )
