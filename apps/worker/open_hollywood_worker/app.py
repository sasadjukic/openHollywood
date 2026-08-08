"""Runtime-composed FastAPI application with the durable local worker."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from open_hollywood_api.app import create_app
from open_hollywood_api.app import lifespan as api_lifespan
from open_hollywood_api.persistence.database import (
    create_session_factory,
    create_sqlite_engine,
    database_path_from_environment,
)
from open_hollywood_api.services.blueprint_model_executor import (
    ProfileRoutedBlueprintNodeExecutor,
)
from open_hollywood_api.services.blueprint_workflow import BlueprintWorkflowService
from open_hollywood_api.services.production_model_executor import (
    ProfileRoutedProductionExecutor,
)
from open_hollywood_api.services.production_workflow import SceneProductionService
from open_hollywood_api.services.workflow_commands import QueuedWorkflowCommandService
from open_hollywood_engine.models import ModelGateway, OllamaGateway

from open_hollywood_worker.runtime import WorkflowWorker


def create_worker_app(
    *,
    gateway: ModelGateway | None = None,
    poll_interval_seconds: float = 0.25,
) -> FastAPI:
    """Compose storage, API commands, provider gateway, and one durable worker."""
    application = create_app()

    @asynccontextmanager
    async def runtime_lifespan(app: FastAPI) -> AsyncIterator[None]:
        async with api_lifespan(app):
            database_path = database_path_from_environment()
            worker_engine = create_sqlite_engine(database_path)
            session_factory = create_session_factory(worker_engine)
            execution_gateway = gateway or OllamaGateway(timeout_seconds=900)
            owns_gateway = gateway is None
            blueprint_executor = ProfileRoutedBlueprintNodeExecutor(
                session_factory=session_factory,
                gateway=execution_gateway,
            )
            production_executor = ProfileRoutedProductionExecutor(
                session_factory=session_factory,
                gateway=execution_gateway,
            )
            try:
                async with (
                    BlueprintWorkflowService(
                        database_path,
                        session_factory,
                        blueprint_executor,
                    ) as blueprint_service,
                    SceneProductionService(
                        database_path=database_path,
                        session_factory=session_factory,
                        executor=production_executor,
                    ) as production_service,
                ):
                    worker = WorkflowWorker(
                        session_factory=session_factory,
                        blueprint_service=blueprint_service,
                        production_service=production_service,
                        poll_interval_seconds=poll_interval_seconds,
                    )
                    app.state.blueprint_workflow_service = blueprint_service
                    app.state.workflow_command_service = QueuedWorkflowCommandService(
                        session_factory,
                        blueprint_service,
                        cancel_active_run=worker.cancel_active_run,
                        wake_worker=worker.wake,
                    )
                    await worker.start()
                    try:
                        yield
                    finally:
                        await worker.stop()
                        app.state.workflow_command_service = None
                        app.state.blueprint_workflow_service = None
            finally:
                if owns_gateway:
                    await execution_gateway.close()
                worker_engine.dispose()

    application.router.lifespan_context = runtime_lifespan
    return application


app = create_worker_app()
