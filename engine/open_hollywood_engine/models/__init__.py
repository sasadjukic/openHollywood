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
from open_hollywood_engine.models.profiles import (
    BLUEPRINT_SPECIALIST_ROLES,
    DIALOGUE_SPECIALIST_ROLES,
    MODEL_PRESETS,
    MODEL_PROFILE_SCHEMA_VERSION,
    REGISTERED_SPECIALIST_ROLES,
    ModelPreset,
    ModelProfileConfiguration,
    ModelProfileMode,
    ModelSelection,
)
from open_hollywood_engine.secrets import EnvironmentSecretStore, ModelSecret, SecretValue

__all__ = [
    "EnvironmentSecretStore",
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
    "ModelProfileConfiguration",
    "ModelProfileMode",
    "ModelPreset",
    "ModelRequest",
    "ModelResponse",
    "ModelSecret",
    "ModelSettings",
    "ModelTiming",
    "ModelUsage",
    "ModelSelection",
    "MODEL_PRESETS",
    "MODEL_PROFILE_SCHEMA_VERSION",
    "OllamaGateway",
    "OllamaHost",
    "SecretValue",
    "BLUEPRINT_SPECIALIST_ROLES",
    "DIALOGUE_SPECIALIST_ROLES",
    "REGISTERED_SPECIALIST_ROLES",
]
