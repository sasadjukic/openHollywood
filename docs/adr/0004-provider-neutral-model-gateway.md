# ADR 0004: Provider-neutral model gateway

- Status: Accepted
- Date: 2026-07-13

## Context

Open Hollywood must compare local, cloud, and hybrid model assignments while
supporting Ollama Cloud, Google, and potentially OpenAI. Provider SDK types must
not leak into creative workflows.

## Decision

All model calls pass through an internal `ModelGateway` and capability model.
Implement Ollama first and one cloud provider second. Introduce LiteLLM behind
the internal interface only when its multi-provider value is needed.

Each invocation records provider, model identifier, profile, settings, input
artifact versions, token usage, latency, cost estimate, retry/fallback history,
and schema validation result.

## Consequences

- Workflows remain provider-neutral and testable with fakes.
- Provider-specific features require explicit capability adapters.
- No provider SDK may become the domain contract.
- Adding a dependency requires a concrete role in the vertical slice.
