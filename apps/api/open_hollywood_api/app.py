"""FastAPI application factory."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import Engine

from open_hollywood_api.app_metadata import API_VERSION
from open_hollywood_api.persistence.database import (
    create_session_factory,
    create_sqlite_engine,
    database_path_from_environment,
)
from open_hollywood_api.routes.blueprint_decisions import router as blueprint_decisions_router
from open_hollywood_api.routes.health import router as health_router
from open_hollywood_api.routes.workflow_events import router as workflow_events_router
from open_hollywood_api.services.blueprint_workflow import BlueprintWorkflowService
from open_hollywood_api.services.workflow_events import WorkflowEventStore

LOCAL_WEB_ORIGINS = (
    "http://127.0.0.1:5173",
    "http://localhost:5173",
)


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncIterator[None]:
    """Own application startup and shutdown resources."""
    owned_engine: Engine | None = None
    if application.state.workflow_event_store is None:
        owned_engine = create_sqlite_engine(database_path_from_environment())
        application.state.workflow_event_store = WorkflowEventStore(
            create_session_factory(owned_engine)
        )
    try:
        yield
    finally:
        if owned_engine is not None:
            owned_engine.dispose()
            application.state.workflow_event_store = None


def create_app(
    workflow_event_store: WorkflowEventStore | None = None,
    blueprint_workflow_service: BlueprintWorkflowService | None = None,
) -> FastAPI:
    """Build the API application without starting process-level side effects."""
    application = FastAPI(
        title="Open Hollywood API",
        summary="Local API for the Open Hollywood creative-writing workspace.",
        version=API_VERSION,
        lifespan=lifespan,
    )
    application.state.workflow_event_store = workflow_event_store
    application.state.blueprint_workflow_service = blueprint_workflow_service
    application.add_middleware(
        CORSMiddleware,
        allow_origins=list(LOCAL_WEB_ORIGINS),
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["Accept", "Content-Type", "Last-Event-ID"],
    )
    application.include_router(health_router, prefix="/api/v1")
    application.include_router(workflow_events_router, prefix="/api/v1")
    application.include_router(blueprint_decisions_router, prefix="/api/v1")
    return application


app = create_app()
