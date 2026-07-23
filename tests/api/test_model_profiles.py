"""Model preset persistence, routing, catalog, and API integration tests."""

from collections.abc import AsyncIterator
from uuid import UUID

import pytest
from httpx import ASGITransport, AsyncClient
from open_hollywood_api.app import create_app
from open_hollywood_api.persistence.database import create_session_factory
from open_hollywood_api.services.model_profiles import (
    BUILTIN_PROFILE_IDS,
    CatalogSource,
    ModelCatalogService,
    ModelProfileStore,
)
from open_hollywood_engine.models import (
    ModelCapabilities,
    ModelDeployment,
    ModelDescriptor,
    ModelGatewayError,
    ModelGatewayErrorCode,
    ModelProfileMode,
    ModelRequest,
    ModelResponse,
)
from sqlalchemy import Engine

pytestmark = pytest.mark.anyio


@pytest.fixture
def anyio_backend() -> str:
    """Keep API tests on the asyncio backend used by FastAPI."""
    return "asyncio"


class FakeCatalogGateway:
    """Minimal provider-neutral gateway used for deterministic discovery."""

    def __init__(
        self,
        models: tuple[ModelDescriptor, ...] = (),
        *,
        failure: ModelGatewayError | None = None,
    ) -> None:
        self._models = models
        self._failure = failure
        self.closed = False

    @property
    def provider(self) -> str:
        return "ollama"

    async def list_models(self) -> tuple[ModelDescriptor, ...]:
        if self._failure is not None:
            raise self._failure
        return self._models

    async def capabilities(self, model_identifier: str) -> ModelCapabilities:
        raise AssertionError(f"unexpected capability request for {model_identifier}")

    async def generate(self, request: ModelRequest) -> ModelResponse:
        raise AssertionError(f"unexpected generation request for {request.model_identifier}")

    async def close(self) -> None:
        self.closed = True


@pytest.fixture
async def model_profile_client(
    database_engine: Engine,
) -> AsyncIterator[tuple[AsyncClient, ModelProfileStore]]:
    """Expose presets and a mixed-availability model catalog."""
    local_gateway = FakeCatalogGateway(
        (
            ModelDescriptor(
                provider="ollama",
                model_identifier="qwen3:8b",
                deployment=ModelDeployment.LOCAL,
                parameter_size="8.2B",
                quantization_level="Q4_K_M",
            ),
            ModelDescriptor(
                provider="ollama",
                model_identifier="creative-cloud",
                deployment=ModelDeployment.CLOUD,
            ),
        )
    )
    unavailable_cloud = FakeCatalogGateway(
        failure=ModelGatewayError(
            ModelGatewayErrorCode.AUTHENTICATION,
            "Ollama Cloud authentication is unavailable",
            retryable=False,
        )
    )
    catalog = ModelCatalogService(
        (
            CatalogSource(
                key="ollama_local",
                label="Ollama on this device",
                gateway=local_gateway,
            ),
            CatalogSource(
                key="ollama_cloud",
                label="Ollama Cloud",
                gateway=unavailable_cloud,
            ),
        )
    )
    store = ModelProfileStore(create_session_factory(database_engine))
    application = create_app(
        model_profile_store=store,
        model_catalog_service=catalog,
    )
    transport = ASGITransport(app=application)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client, store
    await catalog.close()


async def test_presets_seed_in_product_order_without_model_guesses(
    model_profile_client: tuple[AsyncClient, ModelProfileStore],
) -> None:
    client, _ = model_profile_client

    response = await client.get("/api/v1/model-profiles")

    assert response.status_code == 200
    profiles = response.json()["profiles"]
    assert [profile["mode"] for profile in profiles] == ["local", "cloud", "hybrid"]
    assert all(profile["is_default"] is False for profile in profiles)
    assert all(profile["is_complete"] is False for profile in profiles)
    assert profiles[2]["role_assignments"]["brief_architect"] == "local"
    assert profiles[2]["role_assignments"]["blueprint_integrator"] == "cloud"
    assert profiles[2]["role_assignments"]["character_actor"] == "cloud"
    assert profiles[2]["role_assignments"]["dialogue_director"] == "cloud"
    assert profiles[2]["role_assignments"]["scene_writer"] == "cloud"
    assert profiles[2]["role_assignments"]["scene_critic"] == "local"


async def test_configure_and_activate_local_preset_routes_every_role(
    model_profile_client: tuple[AsyncClient, ModelProfileStore],
) -> None:
    client, store = model_profile_client
    profile_id = BUILTIN_PROFILE_IDS[ModelProfileMode.LOCAL]

    configured = await client.put(
        f"/api/v1/model-profiles/{profile_id}",
        json={
            "local_model": {
                "provider": "ollama",
                "model_identifier": "qwen3:8b",
                "deployment": "local",
            }
        },
    )
    activated = await client.post(f"/api/v1/model-profiles/{profile_id}/activate")

    assert configured.status_code == 200
    assert configured.json()["is_complete"] is True
    assert activated.status_code == 200
    assert activated.json()["is_default"] is True
    selection = store.resolve_role(profile_id, "character_architect")
    assert selection.model_identifier == "qwen3:8b"
    assert selection.deployment is ModelDeployment.LOCAL
    assert (
        store.resolve_role(
            profile_id,
            "character_actor",
        ).model_identifier
        == "qwen3:8b"
    )
    assert store.resolve_role(profile_id, "scene_writer").model_identifier == "qwen3:8b"


async def test_incomplete_hybrid_preset_cannot_be_activated(
    model_profile_client: tuple[AsyncClient, ModelProfileStore],
) -> None:
    client, _ = model_profile_client
    profile_id = BUILTIN_PROFILE_IDS[ModelProfileMode.HYBRID]

    response = await client.post(f"/api/v1/model-profiles/{profile_id}/activate")

    assert response.status_code == 409
    assert "local, cloud" in response.json()["detail"]


async def test_catalog_keeps_available_models_when_one_source_fails(
    model_profile_client: tuple[AsyncClient, ModelProfileStore],
) -> None:
    client, _ = model_profile_client

    response = await client.get("/api/v1/models/catalog")

    assert response.status_code == 200
    catalog = response.json()
    assert [model["model_identifier"] for model in catalog["models"]] == [
        "qwen3:8b",
        "creative-cloud",
    ]
    assert [source["status"] for source in catalog["sources"]] == [
        "available",
        "unavailable",
    ]
    assert "authorization" not in str(catalog).lower()


async def test_unknown_profile_returns_not_found(
    model_profile_client: tuple[AsyncClient, ModelProfileStore],
) -> None:
    client, _ = model_profile_client
    missing = UUID("00000000-0000-4000-8000-000000000000")

    response = await client.put(
        f"/api/v1/model-profiles/{missing}",
        json={},
    )

    assert response.status_code == 404
