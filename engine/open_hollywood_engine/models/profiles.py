"""Validated Local, Cloud, and Hybrid model-profile presets."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from types import MappingProxyType
from typing import Any

from open_hollywood_engine.models.contracts import ModelDeployment

MODEL_PROFILE_SCHEMA_VERSION = "3"
BLUEPRINT_SPECIALIST_ROLES = (
    "brief_architect",
    "premise_architect",
    "world_builder",
    "character_architect",
    "blueprint_integrator",
    "blueprint_critic",
)
DIALOGUE_SPECIALIST_ROLES = (
    "character_actor",
    "dialogue_director",
)
PRODUCTION_SPECIALIST_ROLES = (
    "scene_writer",
    "scene_critic",
)
REGISTERED_SPECIALIST_ROLES = (
    *BLUEPRINT_SPECIALIST_ROLES,
    *DIALOGUE_SPECIALIST_ROLES,
    *PRODUCTION_SPECIALIST_ROLES,
)


class ModelProfileMode(StrEnum):
    """User-facing inference allocation preset."""

    LOCAL = "local"
    CLOUD = "cloud"
    HYBRID = "hybrid"


@dataclass(frozen=True, slots=True)
class ModelSelection:
    """One exact, secret-free model assignment."""

    provider: str
    model_identifier: str
    deployment: ModelDeployment

    def __post_init__(self) -> None:
        if not self.provider.strip():
            raise ValueError("model provider must not be empty")
        if not self.model_identifier.strip():
            raise ValueError("model identifier must not be empty")

    def to_data(self) -> dict[str, str]:
        """Return a JSON-safe persistence representation."""
        return {
            "provider": self.provider,
            "model_identifier": self.model_identifier,
            "deployment": self.deployment.value,
        }

    @classmethod
    def from_data(cls, value: object) -> ModelSelection:
        """Validate one model selection at the persistence boundary."""
        data = _require_mapping(value, "model selection")
        provider = _require_string(data.get("provider"), "provider")
        model_identifier = _require_string(
            data.get("model_identifier"),
            "model_identifier",
        )
        deployment = ModelDeployment(_require_string(data.get("deployment"), "deployment"))
        return cls(
            provider=provider,
            model_identifier=model_identifier,
            deployment=deployment,
        )


@dataclass(frozen=True, slots=True)
class ModelPreset:
    """Stable preset metadata and its role-to-deployment policy."""

    mode: ModelProfileMode
    name: str
    description: str
    role_assignments: Mapping[str, ModelDeployment]

    def __post_init__(self) -> None:
        if not self.name.strip() or not self.description.strip():
            raise ValueError("preset name and description must not be empty")
        assignments = dict(self.role_assignments)
        if set(assignments) != set(REGISTERED_SPECIALIST_ROLES):
            raise ValueError("preset must assign every registered specialist role exactly once")
        deployments = set(assignments.values())
        if self.mode is ModelProfileMode.LOCAL and deployments != {ModelDeployment.LOCAL}:
            raise ValueError("Local preset must route every role locally")
        if self.mode is ModelProfileMode.CLOUD and deployments != {ModelDeployment.CLOUD}:
            raise ValueError("Cloud preset must route every role to cloud")
        if self.mode is ModelProfileMode.HYBRID and deployments != {
            ModelDeployment.LOCAL,
            ModelDeployment.CLOUD,
        }:
            raise ValueError("Hybrid preset must contain local and cloud roles")
        object.__setattr__(
            self,
            "role_assignments",
            MappingProxyType(assignments),
        )

    @property
    def required_deployments(self) -> tuple[ModelDeployment, ...]:
        """Return required model slots in stable local-then-cloud order."""
        deployments = set(self.role_assignments.values())
        return tuple(
            deployment
            for deployment in (ModelDeployment.LOCAL, ModelDeployment.CLOUD)
            if deployment in deployments
        )

    def configuration(
        self,
        *,
        local_model: ModelSelection | None = None,
        cloud_model: ModelSelection | None = None,
    ) -> ModelProfileConfiguration:
        """Bind optional exact models to this preset's fixed role policy."""
        return ModelProfileConfiguration(
            mode=self.mode,
            role_assignments=self.role_assignments,
            models={
                ModelDeployment.LOCAL: local_model,
                ModelDeployment.CLOUD: cloud_model,
            },
        )


@dataclass(frozen=True, slots=True)
class ModelProfileConfiguration:
    """Validated persisted configuration for one preset."""

    mode: ModelProfileMode
    role_assignments: Mapping[str, ModelDeployment]
    models: Mapping[ModelDeployment, ModelSelection | None]
    schema_version: str = MODEL_PROFILE_SCHEMA_VERSION

    def __post_init__(self) -> None:
        if self.schema_version != MODEL_PROFILE_SCHEMA_VERSION:
            raise ValueError(f"unsupported model profile schema version {self.schema_version!r}")
        preset = MODEL_PRESETS[self.mode]
        assignments = dict(self.role_assignments)
        if assignments != dict(preset.role_assignments):
            raise ValueError("role assignments do not match the selected preset")
        models = {
            deployment: self.models.get(deployment)
            for deployment in (ModelDeployment.LOCAL, ModelDeployment.CLOUD)
        }
        for deployment, selection in models.items():
            if selection is not None and selection.deployment is not deployment:
                raise ValueError(
                    f"{deployment.value} model slot requires {deployment.value} inference"
                )
        object.__setattr__(
            self,
            "role_assignments",
            MappingProxyType(assignments),
        )
        object.__setattr__(self, "models", MappingProxyType(models))

    @property
    def required_deployments(self) -> tuple[ModelDeployment, ...]:
        """Return the exact model slots required by this preset."""
        return MODEL_PRESETS[self.mode].required_deployments

    @property
    def is_complete(self) -> bool:
        """Return whether every required deployment has an exact model."""
        return all(self.models[deployment] is not None for deployment in self.required_deployments)

    def selection_for(self, specialist_role: str) -> ModelSelection:
        """Resolve one registered specialist to its selected exact model."""
        try:
            deployment = self.role_assignments[specialist_role]
        except KeyError as error:
            raise LookupError(f"unknown specialist role {specialist_role!r}") from error
        selection = self.models[deployment]
        if selection is None:
            raise LookupError(
                f"{deployment.value} model is not configured for {self.mode.value} preset"
            )
        return selection

    def to_data(self) -> dict[str, Any]:
        """Return the canonical secret-free JSON persistence shape."""
        return {
            "schema_version": self.schema_version,
            "preset": self.mode.value,
            "role_assignments": {
                role: deployment.value for role, deployment in self.role_assignments.items()
            },
            "models": {
                deployment.value: (selection.to_data() if selection is not None else None)
                for deployment, selection in self.models.items()
            },
        }

    @classmethod
    def from_data(cls, value: object) -> ModelProfileConfiguration:
        """Reject malformed or aspirational persisted profile data."""
        data = _require_mapping(value, "model profile configuration")
        schema_version = _require_string(
            data.get("schema_version"),
            "schema_version",
        )
        mode = ModelProfileMode(_require_string(data.get("preset"), "preset"))
        role_data = _require_mapping(data.get("role_assignments"), "role_assignments")
        role_assignments = {
            _require_string(role, "role"): ModelDeployment(
                _require_string(deployment, f"role_assignments.{role}")
            )
            for role, deployment in role_data.items()
        }
        model_data = _require_mapping(data.get("models"), "models")
        models: dict[ModelDeployment, ModelSelection | None] = {}
        for deployment in (ModelDeployment.LOCAL, ModelDeployment.CLOUD):
            selection_data = model_data.get(deployment.value)
            models[deployment] = (
                None if selection_data is None else ModelSelection.from_data(selection_data)
            )
        if schema_version in {"1", "2"}:
            legacy_roles = (
                BLUEPRINT_SPECIALIST_ROLES
                if schema_version == "1"
                else (*BLUEPRINT_SPECIALIST_ROLES, *DIALOGUE_SPECIALIST_ROLES)
            )
            expected_legacy = {
                role: MODEL_PRESETS[mode].role_assignments[role] for role in legacy_roles
            }
            if role_assignments != expected_legacy:
                raise ValueError("legacy role assignments do not match the selected preset")
            role_assignments.update(
                {
                    role: MODEL_PRESETS[mode].role_assignments[role]
                    for role in REGISTERED_SPECIALIST_ROLES
                    if role not in legacy_roles
                }
            )
            schema_version = MODEL_PROFILE_SCHEMA_VERSION
        return cls(
            mode=mode,
            role_assignments=role_assignments,
            models=models,
            schema_version=schema_version,
        )


MODEL_PRESETS: Mapping[ModelProfileMode, ModelPreset] = MappingProxyType(
    {
        ModelProfileMode.LOCAL: ModelPreset(
            mode=ModelProfileMode.LOCAL,
            name="Local",
            description="Keep every specialist on this device through Ollama.",
            role_assignments={role: ModelDeployment.LOCAL for role in REGISTERED_SPECIALIST_ROLES},
        ),
        ModelProfileMode.CLOUD: ModelPreset(
            mode=ModelProfileMode.CLOUD,
            name="Cloud",
            description="Use the selected cloud model for every specialist.",
            role_assignments={role: ModelDeployment.CLOUD for role in REGISTERED_SPECIALIST_ROLES},
        ),
        ModelProfileMode.HYBRID: ModelPreset(
            mode=ModelProfileMode.HYBRID,
            name="Hybrid",
            description=(
                "Keep structured preparation and evaluation local while cloud "
                "models handle high-impact creative reasoning."
            ),
            role_assignments={
                "brief_architect": ModelDeployment.LOCAL,
                "premise_architect": ModelDeployment.CLOUD,
                "world_builder": ModelDeployment.CLOUD,
                "character_architect": ModelDeployment.CLOUD,
                "blueprint_integrator": ModelDeployment.CLOUD,
                "blueprint_critic": ModelDeployment.LOCAL,
                "character_actor": ModelDeployment.CLOUD,
                "dialogue_director": ModelDeployment.CLOUD,
                "scene_writer": ModelDeployment.CLOUD,
                "scene_critic": ModelDeployment.LOCAL,
            },
        ),
    }
)


def _require_mapping(value: object, field_name: str) -> Mapping[object, object]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{field_name} must be an object")
    return value


def _require_string(value: object, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")
    return value
