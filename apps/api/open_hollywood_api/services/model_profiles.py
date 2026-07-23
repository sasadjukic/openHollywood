"""Durable model presets and dynamic provider catalog application services."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from open_hollywood_engine.models import (
    MODEL_PRESETS,
    ModelDeployment,
    ModelDescriptor,
    ModelGateway,
    ModelGatewayError,
    ModelProfileConfiguration,
    ModelProfileMode,
    ModelSelection,
)
from sqlalchemy import select, update
from sqlalchemy.orm import Session, sessionmaker

from open_hollywood_api.persistence.models import (
    ModelProfile,
)
from open_hollywood_api.persistence.models import (
    ModelProfileMode as PersistenceModelProfileMode,
)

BUILTIN_PROFILE_IDS = {
    ModelProfileMode.LOCAL: UUID("00000000-0000-4000-8000-000000000131"),
    ModelProfileMode.CLOUD: UUID("00000000-0000-4000-8000-000000000132"),
    ModelProfileMode.HYBRID: UUID("00000000-0000-4000-8000-000000000133"),
}


@dataclass(frozen=True, slots=True)
class ModelProfileRecord:
    """One validated persisted preset."""

    id: UUID
    name: str
    description: str
    mode: ModelProfileMode
    configuration: ModelProfileConfiguration
    is_default: bool
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True, slots=True)
class CatalogSource:
    """One configured discovery endpoint without credential material."""

    key: str
    label: str
    gateway: ModelGateway | None
    unavailable_detail: str | None = None

    def __post_init__(self) -> None:
        if not self.key.strip() or not self.label.strip():
            raise ValueError("catalog source key and label must not be empty")


@dataclass(frozen=True, slots=True)
class CatalogSourceRecord:
    """UI-safe status for one provider catalog source."""

    key: str
    label: str
    provider: str
    status: str
    detail: str | None


@dataclass(frozen=True, slots=True)
class ModelCatalogRecord:
    """Combined dynamically discovered catalog and per-source status."""

    models: tuple[ModelDescriptor, ...]
    sources: tuple[CatalogSourceRecord, ...]


class ModelProfileNotFoundError(LookupError):
    """Raised when a model preset identifier is unknown."""


class IncompleteModelProfileError(ValueError):
    """Raised when an incomplete preset is selected for execution."""


class ModelProfileStore:
    """Persist and resolve the three fixed v0.1 model presets."""

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def list_profiles(self) -> tuple[ModelProfileRecord, ...]:
        """Seed missing built-ins and return Local, Cloud, Hybrid in product order."""
        with self._session_factory.begin() as session:
            self._ensure_builtin_profiles(session)
            records = session.scalars(
                select(ModelProfile).where(ModelProfile.id.in_(tuple(BUILTIN_PROFILE_IDS.values())))
            ).all()
            by_id = {record.id: record for record in records}
            return tuple(
                _profile_record(by_id[BUILTIN_PROFILE_IDS[mode]])
                for mode in (
                    ModelProfileMode.LOCAL,
                    ModelProfileMode.CLOUD,
                    ModelProfileMode.HYBRID,
                )
            )

    def configure_profile(
        self,
        profile_id: UUID,
        *,
        local_model: ModelSelection | None,
        cloud_model: ModelSelection | None,
    ) -> ModelProfileRecord:
        """Replace exact model slots while preserving the preset's fixed policy."""
        with self._session_factory.begin() as session:
            self._ensure_builtin_profiles(session)
            profile = self._require_profile(session, profile_id)
            mode = ModelProfileMode(profile.mode.value)
            configuration = MODEL_PRESETS[mode].configuration(
                local_model=local_model,
                cloud_model=cloud_model,
            )
            profile.configuration = configuration.to_data()
            if profile.is_default and not configuration.is_complete:
                profile.is_default = False
            session.flush()
            session.refresh(profile)
            return _profile_record(profile)

    def activate_profile(self, profile_id: UUID) -> ModelProfileRecord:
        """Atomically select one complete preset as the application default."""
        with self._session_factory.begin() as session:
            self._ensure_builtin_profiles(session)
            profile = self._require_profile(session, profile_id)
            configuration = ModelProfileConfiguration.from_data(profile.configuration)
            if not configuration.is_complete:
                missing = ", ".join(
                    deployment.value
                    for deployment in configuration.required_deployments
                    if configuration.models[deployment] is None
                )
                raise IncompleteModelProfileError(
                    f"configure the required {missing} model before activating "
                    f"the {configuration.mode.value} preset"
                )
            session.execute(update(ModelProfile).values(is_default=False))
            profile.is_default = True
            session.flush()
            session.refresh(profile)
            return _profile_record(profile)

    def resolve_role(
        self,
        profile_id: UUID,
        specialist_role: str,
    ) -> ModelSelection:
        """Resolve an exact execution target for a future specialist invocation."""
        with self._session_factory() as session:
            profile = self._require_profile(session, profile_id)
            configuration = ModelProfileConfiguration.from_data(profile.configuration)
            return configuration.selection_for(specialist_role)

    def _ensure_builtin_profiles(self, session: Session) -> None:
        existing_ids = set(
            session.scalars(
                select(ModelProfile.id).where(
                    ModelProfile.id.in_(tuple(BUILTIN_PROFILE_IDS.values()))
                )
            )
        )
        for mode, profile_id in BUILTIN_PROFILE_IDS.items():
            if profile_id in existing_ids:
                continue
            preset = MODEL_PRESETS[mode]
            session.add(
                ModelProfile(
                    id=profile_id,
                    name=preset.name,
                    description=preset.description,
                    mode=PersistenceModelProfileMode(mode.value),
                    configuration=preset.configuration().to_data(),
                    is_default=False,
                )
            )
        session.flush()

    @staticmethod
    def _require_profile(session: Session, profile_id: UUID) -> ModelProfile:
        if profile_id not in BUILTIN_PROFILE_IDS.values():
            raise ModelProfileNotFoundError(str(profile_id))
        profile = session.get(ModelProfile, profile_id)
        if profile is None:
            raise ModelProfileNotFoundError(str(profile_id))
        return profile


class ModelCatalogService:
    """Combine one or more provider-neutral discovery gateways."""

    def __init__(self, sources: tuple[CatalogSource, ...]) -> None:
        if not sources:
            raise ValueError("at least one catalog source is required")
        if len({source.key for source in sources}) != len(sources):
            raise ValueError("catalog source keys must be unique")
        self._sources = sources

    async def list_catalog(self) -> ModelCatalogRecord:
        """Discover every source independently so one outage does not hide the rest."""
        results = await asyncio.gather(*(self._discover(source) for source in self._sources))
        models: dict[tuple[str, str, ModelDeployment], ModelDescriptor] = {}
        statuses: list[CatalogSourceRecord] = []
        for discovered, status in results:
            statuses.append(status)
            for model in discovered:
                models[(model.provider, model.model_identifier, model.deployment)] = model
        return ModelCatalogRecord(
            models=tuple(
                sorted(
                    models.values(),
                    key=lambda model: (
                        0 if model.deployment is ModelDeployment.LOCAL else 1,
                        model.provider,
                        model.model_identifier.casefold(),
                    ),
                )
            ),
            sources=tuple(statuses),
        )

    async def close(self) -> None:
        """Release each distinct configured gateway."""
        gateways = {
            id(source.gateway): source.gateway
            for source in self._sources
            if source.gateway is not None
        }
        await asyncio.gather(*(gateway.close() for gateway in gateways.values()))

    @staticmethod
    async def _discover(
        source: CatalogSource,
    ) -> tuple[tuple[ModelDescriptor, ...], CatalogSourceRecord]:
        gateway = source.gateway
        if gateway is None:
            return (), CatalogSourceRecord(
                key=source.key,
                label=source.label,
                provider="ollama",
                status="not_configured",
                detail=source.unavailable_detail,
            )
        try:
            models = await gateway.list_models()
        except ModelGatewayError as error:
            return (), CatalogSourceRecord(
                key=source.key,
                label=source.label,
                provider=gateway.provider,
                status="unavailable",
                detail=str(error),
            )
        return models, CatalogSourceRecord(
            key=source.key,
            label=source.label,
            provider=gateway.provider,
            status="available",
            detail=None,
        )


def _profile_record(profile: ModelProfile) -> ModelProfileRecord:
    configuration = ModelProfileConfiguration.from_data(profile.configuration)
    return ModelProfileRecord(
        id=profile.id,
        name=profile.name,
        description=profile.description or MODEL_PRESETS[configuration.mode].description,
        mode=configuration.mode,
        configuration=configuration,
        is_default=profile.is_default,
        created_at=profile.created_at,
        updated_at=profile.updated_at,
    )
