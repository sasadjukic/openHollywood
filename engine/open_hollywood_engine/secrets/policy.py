"""Recursive policy checks that keep credentials out of durable and model data."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import fields, is_dataclass
from enum import Enum
from pathlib import Path

from open_hollywood_engine.secrets.contracts import SecretValue

_FORBIDDEN_FIELD_NAMES = frozenset(
    {
        "api_key",
        "apikey",
        "authorization",
        "bearer_token",
        "client_secret",
        "credential",
        "credentials",
        "access_token",
        "refresh_token",
        "password",
    }
)


class SecretLeakError(ValueError):
    """Raised without echoing a credential when material reaches a forbidden boundary."""

    def __init__(self, destination: str, path: str) -> None:
        super().__init__(f"secret material is forbidden in {destination} at {path}")
        self.destination = destination
        self.path = path


class SecretLeakGuard:
    """Reject opaque, known, or credential-labelled values recursively."""

    def __init__(self, secrets: Sequence[SecretValue] = ()) -> None:
        self.__known_values = tuple(secret.reveal() for secret in secrets)

    def ensure_safe(self, value: object, *, destination: str) -> None:
        """Raise before value crosses a prompt, persistence, trace, or export boundary."""
        self._check(value, destination=destination, path="$", seen=set())

    def redact_text(self, value: str) -> str:
        """Redact known values for exceptional diagnostic text that cannot be rejected."""
        redacted = value
        for secret in self.__known_values:
            redacted = redacted.replace(secret, "[REDACTED]")
        return redacted

    def ensure_file_safe(self, path: Path, *, destination: str) -> None:
        """Audit a fixture or export file without decoding or printing its contents."""
        self._check(path.read_bytes(), destination=destination, path=str(path), seen=set())

    def _check(
        self,
        value: object,
        *,
        destination: str,
        path: str,
        seen: set[int],
    ) -> None:
        if isinstance(value, SecretValue):
            raise SecretLeakError(destination, path)
        if isinstance(value, str):
            if any(secret in value for secret in self.__known_values):
                raise SecretLeakError(destination, path)
            return
        if isinstance(value, bytes):
            if any(secret.encode() in value for secret in self.__known_values):
                raise SecretLeakError(destination, path)
            return
        if value is None or isinstance(value, (bool, int, float, Enum)):
            return

        identity = id(value)
        if identity in seen:
            return
        seen.add(identity)

        if isinstance(value, Mapping):
            for index, (key, item) in enumerate(value.items()):
                key_text = str(key)
                normalized_key = _normalize_field_name(key_text)
                self._check(
                    key_text,
                    destination=destination,
                    path=f"{path}[key:{index}]",
                    seen=seen,
                )
                if normalized_key in _FORBIDDEN_FIELD_NAMES:
                    raise SecretLeakError(destination, f"{path}.{normalized_key}")
                self._check(
                    item,
                    destination=destination,
                    path=f"{path}[value:{index}]",
                    seen=seen,
                )
            return
        if isinstance(value, Sequence):
            for index, item in enumerate(value):
                self._check(
                    item,
                    destination=destination,
                    path=f"{path}[{index}]",
                    seen=seen,
                )
            return
        if is_dataclass(value) and not isinstance(value, type):
            for field in fields(value):
                self._check(
                    getattr(value, field.name),
                    destination=destination,
                    path=f"{path}.{field.name}",
                    seen=seen,
                )


def _normalize_field_name(value: str) -> str:
    return value.strip().lower().replace("-", "_").replace(" ", "_")
