"""API boundary tests."""

import json
from collections.abc import AsyncIterator
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient
from open_hollywood_api.app import create_app
from open_hollywood_api.app_metadata import API_VERSION

pytestmark = pytest.mark.anyio
WORKSPACE_ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def anyio_backend() -> str:
    """Keep API tests on the asyncio backend used by FastAPI."""
    return "asyncio"


@pytest.fixture
async def client() -> AsyncIterator[AsyncClient]:
    """Create an isolated client around a fresh application instance."""
    transport = ASGITransport(app=create_app())
    async with AsyncClient(transport=transport, base_url="http://test") as test_client:
        yield test_client


async def test_health_reports_service_metadata(client: AsyncClient) -> None:
    response = await client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {
        "api_version": API_VERSION,
        "service": "open-hollywood-api",
        "state": "ok",
    }


async def test_openapi_exposes_stable_health_operation(client: AsyncClient) -> None:
    response = await client.get("/openapi.json")

    assert response.status_code == 200
    schema = response.json()
    operation = schema["paths"]["/api/v1/health"]["get"]
    assert schema["openapi"].startswith("3.1.")
    assert operation["operationId"] == "getHealth"
    assert operation["responses"]["200"]["content"]["application/json"]["schema"] == {
        "$ref": "#/components/schemas/ServiceStatus"
    }


async def test_exported_openapi_contract_is_current(client: AsyncClient) -> None:
    response = await client.get("/openapi.json")
    exported_schema = json.loads(
        (WORKSPACE_ROOT / "packages" / "contracts" / "openapi.json").read_text(encoding="utf-8")
    )

    assert exported_schema == response.json()


async def test_local_web_origin_is_allowed(client: AsyncClient) -> None:
    response = await client.options(
        "/api/v1/health",
        headers={
            "Access-Control-Request-Method": "GET",
            "Origin": "http://localhost:5173",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"


async def test_event_reconnect_header_is_allowed_by_cors(client: AsyncClient) -> None:
    response = await client.options(
        "/api/v1/workflow-runs/00000000-0000-0000-0000-000000000000/events/stream",
        headers={
            "Access-Control-Request-Headers": "Last-Event-ID",
            "Access-Control-Request-Method": "GET",
            "Origin": "http://localhost:5173",
        },
    )

    assert response.status_code == 200
    allowed_headers = response.headers["access-control-allow-headers"].lower()
    assert "last-event-id" in allowed_headers
