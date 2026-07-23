"""Model preset configuration and dynamic catalog routes."""

from typing import Annotated
from uuid import UUID

import anyio
from fastapi import APIRouter, Depends, HTTPException, status

from open_hollywood_api.dependencies import (
    get_model_catalog_service,
    get_model_profile_store,
)
from open_hollywood_api.model_profile_models import (
    ConfigureModelProfileRequest,
    ModelCatalog,
    ModelProfileList,
    ModelProfileSummary,
)
from open_hollywood_api.services.model_profiles import (
    IncompleteModelProfileError,
    ModelCatalogService,
    ModelProfileNotFoundError,
    ModelProfileStore,
)

router = APIRouter(tags=["model profiles"])
ModelProfileStoreDependency = Annotated[
    ModelProfileStore,
    Depends(get_model_profile_store),
]
ModelCatalogDependency = Annotated[
    ModelCatalogService,
    Depends(get_model_catalog_service),
]


@router.get(
    "/model-profiles",
    operation_id="listModelProfiles",
    response_model=ModelProfileList,
    summary="List durable Local, Cloud, and Hybrid presets",
)
async def list_model_profiles(
    store: ModelProfileStoreDependency,
) -> ModelProfileList:
    """Return the fixed v0.1 presets and their exact selected models."""
    records = await anyio.to_thread.run_sync(store.list_profiles)
    return ModelProfileList(
        profiles=[ModelProfileSummary.from_record(record) for record in records]
    )


@router.put(
    "/model-profiles/{profile_id}",
    operation_id="configureModelProfile",
    response_model=ModelProfileSummary,
    responses={404: {"description": "Model profile not found"}},
    summary="Configure exact models for one preset",
)
async def configure_model_profile(
    profile_id: UUID,
    request: ConfigureModelProfileRequest,
    store: ModelProfileStoreDependency,
) -> ModelProfileSummary:
    """Persist only provider, exact identifier, and inference placement."""
    try:
        record = await anyio.to_thread.run_sync(
            lambda: store.configure_profile(
                profile_id,
                local_model=(
                    request.local_model.to_domain() if request.local_model is not None else None
                ),
                cloud_model=(
                    request.cloud_model.to_domain() if request.cloud_model is not None else None
                ),
            )
        )
    except ModelProfileNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model profile not found",
        ) from error
    return ModelProfileSummary.from_record(record)


@router.post(
    "/model-profiles/{profile_id}/activate",
    operation_id="activateModelProfile",
    response_model=ModelProfileSummary,
    responses={
        404: {"description": "Model profile not found"},
        409: {"description": "Required models are not configured"},
    },
    summary="Select one complete preset as the default",
)
async def activate_model_profile(
    profile_id: UUID,
    store: ModelProfileStoreDependency,
) -> ModelProfileSummary:
    """Atomically activate one complete secret-free preset."""
    try:
        record = await anyio.to_thread.run_sync(
            store.activate_profile,
            profile_id,
        )
    except ModelProfileNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model profile not found",
        ) from error
    except IncompleteModelProfileError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error
    return ModelProfileSummary.from_record(record)


@router.get(
    "/models/catalog",
    operation_id="listModelCatalog",
    response_model=ModelCatalog,
    summary="Discover configured Ollama model catalogs",
)
async def list_model_catalog(
    catalog: ModelCatalogDependency,
) -> ModelCatalog:
    """Return dynamic models while reporting each source independently."""
    return ModelCatalog.from_record(await catalog.list_catalog())
