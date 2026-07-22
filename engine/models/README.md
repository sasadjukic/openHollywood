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
- Runtime-only bearer authentication for direct Ollama Cloud calls

Cloud model names are never hard-coded because availability and free-plan access
can change. Ollama models reached through a local host with a `-cloud` suffix are
still classified as cloud inference. Schema-enforced structured output is
rejected for cloud inference until Ollama documents support for it.

Secure retrieval and storage of `OLLAMA_API_KEY` belongs to implementation Step
7. The Step 6 adapter only accepts a key injected at runtime and never places it
in a domain request or response.
