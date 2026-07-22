# Secret handling

`open_hollywood_engine.secrets` owns provider-neutral, runtime-only credential
contracts and leak detection. It keeps secret values outside creative domain
models while allowing provider transports to authenticate.

The current implementation provides:

- Stable `ModelSecret` handles that are safe to persist in model profiles
- Opaque `SecretValue` objects with redacted string, representation, and format
  behavior
- A `SecretStore` protocol for storage-neutral runtime resolution
- An environment-backed store for the local browser/API phase
- Recursive leak guards for prompts, provider responses, persistence, fixtures,
  diagnostics, and database exports

Application code should construct direct Ollama Cloud access with
`OllamaGateway.from_secret_store(...)`. Plaintext is revealed only while the
HTTP authorization header is created. Do not pass environment-variable values
through workflow state, model requests, profiles, events, artifacts, or API
responses.

Tauri packaging may add a Stronghold-backed `SecretStore`; it must preserve the
same handles and policy boundaries.
