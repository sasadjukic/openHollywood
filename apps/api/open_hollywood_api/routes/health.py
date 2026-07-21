"""Service health route."""

from fastapi import APIRouter

from open_hollywood_api.app_metadata import API_VERSION
from open_hollywood_api.models import ServiceState, ServiceStatus

router = APIRouter(tags=["system"])


@router.get(
    "/health",
    operation_id="getHealth",
    response_model=ServiceStatus,
    summary="Report API availability",
)
async def get_health() -> ServiceStatus:
    """Return stable service metadata without touching external dependencies."""
    return ServiceStatus(
        service="open-hollywood-api",
        state=ServiceState.OK,
        api_version=API_VERSION,
    )
