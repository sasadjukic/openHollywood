# Model gateway

`open_hollywood_engine.models` owns the provider-neutral boundary used by
creative workflows. Its initial adapter supports both a local Ollama server and
direct Ollama Cloud access without exposing HTTP or Ollama response types to the
rest of the engine.

The gateway currently provides:

- Dynamic model discovery through Ollama's model catalog
- Per-model capability and context-window discovery
- Explicit local versus cloud inference placement
- Required per-call token and cost envelopes
- Exact prompt-template, profile, role, and input-artifact version references
- Normalized token usage, timing, finish reason, and errors
- Runtime-only bearer authentication resolved through opaque secret handles
- Preflight rejection when a credential reaches a model prompt or response

The same package owns schema-versioned `Local`, `Cloud`, and `Hybrid` preset
contracts. Each preset assigns every registered Story Blueprint specialist to
local or cloud inference, then binds those deployment slots to exact discovered
model identifiers. Configurations fail closed on unknown roles, mismatched
deployment slots, unsupported schema versions, or missing required models.
They remain independent from SQLAlchemy, FastAPI, Ollama response types, and
provider credentials.

Profile schema version 2 adds the concrete `character_actor` and
`dialogue_director` roles introduced by the dialogue subgraph. Version 1
profiles from Step 13 are upgraded in memory using their preset's fixed routing
policy, so existing Local, Cloud, and Hybrid selections remain usable without a
destructive database rewrite.

Cloud model names are never hard-coded because availability and free-plan access
can change. Ollama models reached through a local host with a `-cloud` suffix are
still classified as cloud inference. Schema-enforced structured output is
rejected for cloud inference until Ollama documents support for it.

Direct Ollama Cloud access should be constructed with an application-owned
`SecretStore`. The current environment-backed store reads `OLLAMA_API_KEY` on
demand. It never places the value in a domain request or response; a future
Tauri adapter can use platform-backed storage without changing gateway or
workflow contracts.
