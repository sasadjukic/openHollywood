"""Provider-neutral contracts for runtime-only model credentials."""

from __future__ import annotations

from enum import StrEnum
from typing import Protocol, final


class ModelSecret(StrEnum):
    """Stable secret handles that are safe to persist and display."""

    OLLAMA_API_KEY = "ollama_api_key"
    OPENAI_API_KEY = "openai_api_key"
    GOOGLE_API_KEY = "google_api_key"


@final
class SecretValue:
    """Opaque in-memory credential whose string representations are redacted."""

    __slots__ = ("__value",)

    def __init__(self, value: str) -> None:
        if not value or not value.strip():
            raise ValueError("secret value must not be empty")
        self.__value = value

    def reveal(self) -> str:
        """Reveal the credential only at the provider transport boundary."""
        return self.__value

    def __bool__(self) -> bool:
        return True

    def __repr__(self) -> str:
        return "SecretValue('[REDACTED]')"

    def __str__(self) -> str:
        return "[REDACTED]"

    def __format__(self, format_spec: str) -> str:
        return format(str(self), format_spec)


class SecretStore(Protocol):
    """Resolve a safe handle to a credential without persisting the value."""

    def get(self, reference: ModelSecret) -> SecretValue | None:
        """Return a runtime credential when configured."""
        ...

    def require(self, reference: ModelSecret) -> SecretValue:
        """Return a runtime credential or raise a reference-only error."""
        ...


class MissingSecretError(RuntimeError):
    """Raised without secret material when a required credential is absent."""

    def __init__(self, reference: ModelSecret) -> None:
        super().__init__(f"required model secret {reference.value!r} is not configured")
        self.reference = reference
