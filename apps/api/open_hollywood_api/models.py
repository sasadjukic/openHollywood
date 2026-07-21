"""Public API models for application-level service metadata."""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict


class ServiceState(StrEnum):
    """Availability state exposed by the API boundary."""

    OK = "ok"


class ServiceStatus(BaseModel):
    """Typed response proving the client-to-API contract is available."""

    model_config = ConfigDict(frozen=True)

    service: str
    state: ServiceState
    api_version: str
