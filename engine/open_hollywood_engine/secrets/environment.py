"""Environment-backed secret resolution for the local browser/API phase."""

from __future__ import annotations

import os
from collections.abc import Mapping

from open_hollywood_engine.secrets.contracts import MissingSecretError, ModelSecret, SecretValue

DEFAULT_SECRET_VARIABLES: Mapping[ModelSecret, str] = {
    ModelSecret.OLLAMA_API_KEY: "OLLAMA_API_KEY",
    ModelSecret.OPENAI_API_KEY: "OPENAI_API_KEY",
    ModelSecret.GOOGLE_API_KEY: "GOOGLE_API_KEY",
}


class EnvironmentSecretStore:
    """Read model credentials on demand without loading or writing dotenv files."""

    def __init__(
        self,
        environment: Mapping[str, str] | None = None,
        *,
        variable_names: Mapping[ModelSecret, str] = DEFAULT_SECRET_VARIABLES,
    ) -> None:
        self._environment = os.environ if environment is None else environment
        self._variable_names = dict(variable_names)

    def get(self, reference: ModelSecret) -> SecretValue | None:
        """Resolve a configured value while retaining only the environment mapping."""
        variable_name = self._variable_names.get(reference)
        if variable_name is None:
            return None
        value = self._environment.get(variable_name)
        if value is None or not value.strip():
            return None
        return SecretValue(value)

    def require(self, reference: ModelSecret) -> SecretValue:
        """Resolve a required value or fail using only its safe handle."""
        value = self.get(reference)
        if value is None:
            raise MissingSecretError(reference)
        return value

    def configured_values(self) -> tuple[SecretValue, ...]:
        """Return configured model credentials for boundary leak guards."""
        return tuple(
            value
            for reference in self._variable_names
            if (value := self.get(reference)) is not None
        )
