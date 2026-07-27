"""Provider-neutral routing across exact model deployments."""

from __future__ import annotations

from collections.abc import Mapping

from open_hollywood_engine.models.contracts import (
    ModelCapabilities,
    ModelDeployment,
    ModelDescriptor,
    ModelRequest,
    ModelResponse,
)
from open_hollywood_engine.models.gateway import ModelGateway


class CampaignModelGateway:
    """Route one provider's exact campaign models to deployment-specific gateways."""

    def __init__(
        self,
        *,
        provider: str,
        deployments: Mapping[ModelDeployment, ModelGateway],
        model_deployments: Mapping[str, ModelDeployment],
    ) -> None:
        if not provider.strip():
            raise ValueError("campaign gateway provider must not be empty")
        if not deployments:
            raise ValueError("campaign gateway needs at least one deployment")
        if any(gateway.provider != provider for gateway in deployments.values()):
            raise ValueError("campaign gateway routes must use one provider")
        missing = set(model_deployments.values()).difference(deployments)
        if missing:
            formatted = ", ".join(sorted(deployment.value for deployment in missing))
            raise ValueError(f"campaign gateway is missing deployment routes: {formatted}")
        self._provider = provider
        self._deployments = dict(deployments)
        self._model_deployments = dict(model_deployments)

    @property
    def provider(self) -> str:
        """Return the stable provider identifier shared by every route."""
        return self._provider

    async def list_models(self) -> tuple[ModelDescriptor, ...]:
        """Combine configured deployment catalogs without duplicate descriptors."""
        discovered: dict[tuple[str, str, ModelDeployment], ModelDescriptor] = {}
        for gateway in dict.fromkeys(self._deployments.values()):
            for model in await gateway.list_models():
                discovered[(model.provider, model.model_identifier, model.deployment)] = model
        return tuple(
            discovered[key]
            for key in sorted(
                discovered,
                key=lambda value: (value[2].value, value[0], value[1]),
            )
        )

    async def capabilities(self, model_identifier: str) -> ModelCapabilities:
        """Inspect a model through the deployment frozen into the campaign plan."""
        return await self._gateway_for(model_identifier).capabilities(model_identifier)

    async def generate(self, request: ModelRequest) -> ModelResponse:
        """Generate through the endpoint assigned to the frozen model identifier."""
        return await self._gateway_for(request.model_identifier).generate(request)

    async def close(self) -> None:
        """Close each owned route exactly once."""
        for gateway in dict.fromkeys(self._deployments.values()):
            await gateway.close()

    def _gateway_for(self, model_identifier: str) -> ModelGateway:
        try:
            deployment = self._model_deployments[model_identifier]
        except KeyError as error:
            raise ValueError(
                f"model {model_identifier!r} is not frozen into this campaign"
            ) from error
        return self._deployments[deployment]
