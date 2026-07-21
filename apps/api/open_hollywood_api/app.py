"""FastAPI application factory."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from open_hollywood_api.app_metadata import API_VERSION
from open_hollywood_api.routes.health import router as health_router

LOCAL_WEB_ORIGINS = (
    "http://127.0.0.1:5173",
    "http://localhost:5173",
)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Own application startup and shutdown resources."""
    yield


def create_app() -> FastAPI:
    """Build the API application without starting process-level side effects."""
    application = FastAPI(
        title="Open Hollywood API",
        summary="Local API for the Open Hollywood creative-writing workspace.",
        version=API_VERSION,
        lifespan=lifespan,
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=list(LOCAL_WEB_ORIGINS),
        allow_credentials=False,
        allow_methods=["GET"],
        allow_headers=["Accept", "Content-Type"],
    )
    application.include_router(health_router, prefix="/api/v1")
    return application


app = create_app()
