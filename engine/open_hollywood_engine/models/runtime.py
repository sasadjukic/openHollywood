"""Shared runtime composition; no inference or selection changes on construction."""

from open_hollywood_engine.models.contracts import ModelDeployment
from open_hollywood_engine.models.ollama import OllamaGateway
from open_hollywood_engine.models.openai import OpenAIGateway
from open_hollywood_engine.models.routing import ProviderModelGateway


def runtime_gateway(*, timeout_seconds: float = 900) -> ProviderModelGateway:
    """Retain Ollama's signed-in local path alongside direct OpenAI inference."""
    ollama = OllamaGateway(timeout_seconds=timeout_seconds)
    return ProviderModelGateway(
        {
            ("ollama", ModelDeployment.LOCAL): ollama,
            ("ollama", ModelDeployment.CLOUD): ollama,
            ("openai", ModelDeployment.CLOUD): OpenAIGateway(timeout_seconds=timeout_seconds),
        }
    )
