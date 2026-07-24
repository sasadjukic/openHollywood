"""FastAPI application factory."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from open_hollywood_engine.models import OllamaGateway, OllamaHost
from open_hollywood_engine.secrets import EnvironmentSecretStore, ModelSecret
from sqlalchemy import Engine

from open_hollywood_api.app_metadata import API_VERSION
from open_hollywood_api.persistence.database import (
    create_session_factory,
    create_sqlite_engine,
    database_path_from_environment,
)
from open_hollywood_api.routes.blueprint_decisions import router as blueprint_decisions_router
from open_hollywood_api.routes.exports import router as exports_router
from open_hollywood_api.routes.health import router as health_router
from open_hollywood_api.routes.model_profiles import router as model_profiles_router
from open_hollywood_api.routes.run_controls import router as run_controls_router
from open_hollywood_api.routes.workflow_events import router as workflow_events_router
from open_hollywood_api.routes.workspace import router as workspace_router
from open_hollywood_api.services.blueprint_workflow import BlueprintWorkflowService
from open_hollywood_api.services.exports import ProjectExportStore
from open_hollywood_api.services.model_profiles import (
    CatalogSource,
    ModelCatalogService,
    ModelProfileStore,
)
from open_hollywood_api.services.workflow_events import WorkflowEventStore
from open_hollywood_api.services.workspace import WorkspaceStore

LOCAL_WEB_ORIGINS = (
    "http://127.0.0.1:5173",
    "http://localhost:5173",
)


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncIterator[None]:
    """Own application startup and shutdown resources."""
    owned_engine: Engine | None = None
    owns_event_store = application.state.workflow_event_store is None
    owns_workspace_store = application.state.workspace_store is None
    owns_project_export_store = application.state.project_export_store is None
    owns_model_profile_store = application.state.model_profile_store is None
    owns_model_catalog_service = application.state.model_catalog_service is None
    if (
        owns_event_store
        or owns_workspace_store
        or owns_project_export_store
        or owns_model_profile_store
    ):
        owned_engine = create_sqlite_engine(database_path_from_environment())
        session_factory = create_session_factory(owned_engine)
        if owns_event_store:
            application.state.workflow_event_store = WorkflowEventStore(session_factory)
        if owns_workspace_store:
            application.state.workspace_store = WorkspaceStore(session_factory)
        if owns_project_export_store:
            application.state.project_export_store = ProjectExportStore(session_factory)
        if owns_model_profile_store:
            application.state.model_profile_store = ModelProfileStore(session_factory)
    if owns_model_catalog_service:
        secret_store = EnvironmentSecretStore()
        cloud_api_key = secret_store.get(ModelSecret.OLLAMA_API_KEY)
        application.state.model_catalog_service = ModelCatalogService(
            (
                CatalogSource(
                    key="ollama_local",
                    label="Ollama on this device",
                    gateway=OllamaGateway(timeout_seconds=10),
                ),
                CatalogSource(
                    key="ollama_cloud",
                    label="Ollama Cloud",
                    gateway=(
                        OllamaGateway(
                            host=OllamaHost.CLOUD,
                            api_key=cloud_api_key,
                            timeout_seconds=10,
                        )
                        if cloud_api_key is not None
                        else None
                    ),
                    unavailable_detail=(
                        "Set OLLAMA_API_KEY for direct cloud discovery, or use "
                        "cloud models advertised by a signed-in local Ollama."
                    ),
                ),
            )
        )
    try:
        yield
    finally:
        if owns_model_catalog_service:
            await application.state.model_catalog_service.close()
            application.state.model_catalog_service = None
        if owned_engine is not None:
            owned_engine.dispose()
            if owns_event_store:
                application.state.workflow_event_store = None
            if owns_workspace_store:
                application.state.workspace_store = None
            if owns_project_export_store:
                application.state.project_export_store = None
            if owns_model_profile_store:
                application.state.model_profile_store = None


def create_app(
    workflow_event_store: WorkflowEventStore | None = None,
    blueprint_workflow_service: BlueprintWorkflowService | None = None,
    workspace_store: WorkspaceStore | None = None,
    project_export_store: ProjectExportStore | None = None,
    model_profile_store: ModelProfileStore | None = None,
    model_catalog_service: ModelCatalogService | None = None,
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
    application.state.workspace_store = workspace_store
    application.state.project_export_store = project_export_store
    application.state.model_profile_store = model_profile_store
    application.state.model_catalog_service = model_catalog_service
    application.add_middleware(
        CORSMiddleware,
        allow_origins=list(LOCAL_WEB_ORIGINS),
        allow_credentials=False,
        allow_methods=["GET", "POST", "PUT"],
        allow_headers=["Accept", "Content-Type", "Last-Event-ID"],
    )
    application.include_router(health_router, prefix="/api/v1")
    application.include_router(workflow_events_router, prefix="/api/v1")
    application.include_router(blueprint_decisions_router, prefix="/api/v1")
    application.include_router(workspace_router, prefix="/api/v1")
    application.include_router(exports_router, prefix="/api/v1")
    application.include_router(model_profiles_router, prefix="/api/v1")
    application.include_router(run_controls_router, prefix="/api/v1")
    return application


app = create_app()
