"""Public model-gateway contracts and the first Ollama adapter."""

from open_hollywood_engine.models.contracts import (
    InvocationContext,
    MessageRole,
    ModelCallBudget,
    ModelCapabilities,
    ModelDeployment,
    ModelDescriptor,
    ModelMessage,
    ModelRequest,
    ModelResponse,
    ModelSettings,
    ModelTiming,
    ModelUsage,
)
from open_hollywood_engine.models.gateway import (
    ModelGateway,
    ModelGatewayError,
    ModelGatewayErrorCode,
)
from open_hollywood_engine.models.ollama import OllamaGateway, OllamaHost

__all__ = [
    "InvocationContext",
    "MessageRole",
    "ModelCallBudget",
    "ModelCapabilities",
    "ModelDeployment",
    "ModelDescriptor",
    "ModelGateway",
    "ModelGatewayError",
    "ModelGatewayErrorCode",
    "ModelMessage",
    "ModelRequest",
    "ModelResponse",
    "ModelSettings",
    "ModelTiming",
    "ModelUsage",
    "OllamaGateway",
    "OllamaHost",
]
