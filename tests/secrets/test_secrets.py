"""Runtime secret contracts and recursive policy tests."""

from pathlib import Path

import pytest
from open_hollywood_engine.secrets import (
    EnvironmentSecretStore,
    MissingSecretError,
    ModelSecret,
    SecretLeakError,
    SecretLeakGuard,
    SecretValue,
)


def test_secret_value_never_reveals_itself_through_display_protocols() -> None:
    secret = SecretValue("unit-test-runtime-credential")

    assert str(secret) == "[REDACTED]"
    assert repr(secret) == "SecretValue('[REDACTED]')"
    assert f"credential={secret}" == "credential=[REDACTED]"
    assert "unit-test-runtime-credential" not in str([secret])


def test_environment_store_resolves_safe_handle_without_mutating_source() -> None:
    environment = {"OLLAMA_API_KEY": "unit-test-runtime-credential"}
    store = EnvironmentSecretStore(environment)

    secret = store.require(ModelSecret.OLLAMA_API_KEY)

    assert secret.reveal() == "unit-test-runtime-credential"
    assert environment == {"OLLAMA_API_KEY": "unit-test-runtime-credential"}


def test_environment_store_missing_error_contains_only_safe_reference() -> None:
    store = EnvironmentSecretStore({})

    with pytest.raises(MissingSecretError) as error:
        store.require(ModelSecret.OLLAMA_API_KEY)

    assert error.value.reference is ModelSecret.OLLAMA_API_KEY
    assert str(error.value) == "required model secret 'ollama_api_key' is not configured"


def test_guard_rejects_known_values_opaque_values_and_credential_fields() -> None:
    secret = SecretValue("unit-test-runtime-credential")
    guard = SecretLeakGuard((secret,))

    for unsafe in (
        {"content": "prefix unit-test-runtime-credential suffix"},
        {"content": secret},
        {"configuration": {"api-key": "unknown-value"}},
        {"unit-test-runtime-credential": "value"},
    ):
        with pytest.raises(SecretLeakError) as error:
            guard.ensure_safe(unsafe, destination="test boundary")
        assert "unit-test-runtime-credential" not in str(error.value)


def test_guard_allows_secret_references_and_token_accounting() -> None:
    SecretLeakGuard().ensure_safe(
        {
            "secret_reference": ModelSecret.OLLAMA_API_KEY.value,
            "input_tokens": 100,
            "output_tokens": 200,
        },
        destination="model profile",
    )


def test_known_values_can_be_redacted_from_unavoidable_diagnostics() -> None:
    guard = SecretLeakGuard((SecretValue("unit-test-runtime-credential"),))

    assert guard.redact_text("bad unit-test-runtime-credential") == "bad [REDACTED]"


def test_committed_legacy_fixtures_are_free_of_configured_model_credentials() -> None:
    fixtures = Path(__file__).resolve().parents[1] / "fixtures"
    guard = SecretLeakGuard(EnvironmentSecretStore().configured_values())

    for fixture in fixtures.rglob("*"):
        if fixture.is_file():
            guard.ensure_file_safe(fixture, destination="committed test fixture")
