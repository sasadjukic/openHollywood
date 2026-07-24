"""FastAPI application-service dependencies."""

from fastapi import HTTPException, Request, status

from open_hollywood_api.services.blueprint_workflow import BlueprintWorkflowService
from open_hollywood_api.services.exports import ProjectExportStore
from open_hollywood_api.services.model_profiles import (
    ModelCatalogService,
    ModelProfileStore,
)
from open_hollywood_api.services.workflow_events import WorkflowEventStore
from open_hollywood_api.services.workspace import WorkspaceStore


def get_workflow_event_store(request: Request) -> WorkflowEventStore:
    """Return the app-owned event store or report an unavailable database."""
    event_store = getattr(request.app.state, "workflow_event_store", None)
    if not isinstance(event_store, WorkflowEventStore):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Workflow event storage is unavailable",
        )
    return event_store


def get_blueprint_workflow_service(request: Request) -> BlueprintWorkflowService:
    """Return the app-owned workflow service when a worker has provided it."""
    service = getattr(request.app.state, "blueprint_workflow_service", None)
    if not isinstance(service, BlueprintWorkflowService):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Blueprint workflow execution is unavailable",
        )
    return service


def get_workspace_store(request: Request) -> WorkspaceStore:
    """Return the app-owned read boundary for persisted workspace data."""
    store = getattr(request.app.state, "workspace_store", None)
    if not isinstance(store, WorkspaceStore):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Workspace storage is unavailable",
        )
    return store


def get_project_export_store(request: Request) -> ProjectExportStore:
    """Return the app-owned deterministic export boundary."""
    store = getattr(request.app.state, "project_export_store", None)
    if not isinstance(store, ProjectExportStore):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Project export storage is unavailable",
        )
    return store


def get_model_profile_store(request: Request) -> ModelProfileStore:
    """Return the app-owned durable model-preset boundary."""
    store = getattr(request.app.state, "model_profile_store", None)
    if not isinstance(store, ModelProfileStore):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model profile storage is unavailable",
        )
    return store


def get_model_catalog_service(request: Request) -> ModelCatalogService:
    """Return the app-owned dynamic provider catalog."""
    catalog = getattr(request.app.state, "model_catalog_service", None)
    if not isinstance(catalog, ModelCatalogService):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model discovery is unavailable",
        )
    return catalog
