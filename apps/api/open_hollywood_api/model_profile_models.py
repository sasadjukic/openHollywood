"""Public API contracts for model presets and dynamic model discovery."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from open_hollywood_engine.models import (
    ModelDeployment,
    ModelDescriptor,
    ModelProfileMode,
    ModelSelection,
)
from pydantic import BaseModel, ConfigDict

from open_hollywood_api.services.model_profiles import (
    CatalogSourceRecord,
    ModelCatalogRecord,
    ModelProfileRecord,
)


class ModelProfileApiModel(BaseModel):
    """Shared immutable API model configuration."""

    model_config = ConfigDict(frozen=True)


class ModelSelectionInput(ModelProfileApiModel):
    """One exact model selected from a dynamically discovered catalog."""

    provider: str
    model_identifier: str
    deployment: ModelDeployment

    def to_domain(self) -> ModelSelection:
        """Return the provider-neutral validated domain selection."""
        return ModelSelection(
            provider=self.provider,
            model_identifier=self.model_identifier,
            deployment=self.deployment,
        )


class ConfigureModelProfileRequest(ModelProfileApiModel):
    """Exact model slots for one fixed preset policy."""

    local_model: ModelSelectionInput | None = None
    cloud_model: ModelSelectionInput | None = None


class ModelProfileSummary(ModelProfileApiModel):
    """One durable Local, Cloud, or Hybrid preset."""

    id: UUID
    name: str
    description: str
    mode: ModelProfileMode
    is_default: bool
    is_complete: bool
    required_deployments: list[ModelDeployment]
    role_assignments: dict[str, ModelDeployment]
    local_model: ModelSelectionInput | None
    cloud_model: ModelSelectionInput | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_record(cls, record: ModelProfileRecord) -> ModelProfileSummary:
        configuration = record.configuration
        local = configuration.models[ModelDeployment.LOCAL]
        cloud = configuration.models[ModelDeployment.CLOUD]
        return cls(
            id=record.id,
            name=record.name,
            description=record.description,
            mode=record.mode,
            is_default=record.is_default,
            is_complete=configuration.is_complete,
            required_deployments=list(configuration.required_deployments),
            role_assignments=dict(configuration.role_assignments),
            local_model=_selection_input(local),
            cloud_model=_selection_input(cloud),
            created_at=record.created_at,
            updated_at=record.updated_at,
        )


class ModelProfileList(ModelProfileApiModel):
    """The three built-in model presets."""

    profiles: list[ModelProfileSummary]


class CatalogModel(ModelProfileApiModel):
    """One dynamically discovered provider model."""

    provider: str
    model_identifier: str
    deployment: ModelDeployment
    digest: str | None
    parameter_size: str | None
    quantization_level: str | None
    size_bytes: int | None

    @classmethod
    def from_descriptor(cls, descriptor: ModelDescriptor) -> CatalogModel:
        return cls(
            provider=descriptor.provider,
            model_identifier=descriptor.model_identifier,
            deployment=descriptor.deployment,
            digest=descriptor.digest,
            parameter_size=descriptor.parameter_size,
            quantization_level=descriptor.quantization_level,
            size_bytes=descriptor.size_bytes,
        )


class CatalogSourceStatus(ModelProfileApiModel):
    """Availability of one credential-free catalog source."""

    key: str
    label: str
    provider: str
    status: str
    detail: str | None

    @classmethod
    def from_record(cls, record: CatalogSourceRecord) -> CatalogSourceStatus:
        return cls(
            key=record.key,
            label=record.label,
            provider=record.provider,
            status=record.status,
            detail=record.detail,
        )


class ModelCatalog(ModelProfileApiModel):
    """Combined discovered models and provider-source status."""

    models: list[CatalogModel]
    sources: list[CatalogSourceStatus]

    @classmethod
    def from_record(cls, record: ModelCatalogRecord) -> ModelCatalog:
        return cls(
            models=[CatalogModel.from_descriptor(model) for model in record.models],
            sources=[CatalogSourceStatus.from_record(source) for source in record.sources],
        )


def _selection_input(selection: ModelSelection | None) -> ModelSelectionInput | None:
    if selection is None:
        return None
    return ModelSelectionInput(
        provider=selection.provider,
        model_identifier=selection.model_identifier,
        deployment=selection.deployment,
    )
