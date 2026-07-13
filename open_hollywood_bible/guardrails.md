# Guardrails and completion controls

Every workflow run needs hard limits independent of model judgment:

- Maximum graph steps
- Maximum agents invoked
- Maximum revision cycles per artifact
- Maximum model calls
- Maximum input and output tokens
- Maximum monetary cost
- Maximum wall-clock runtime
- Per-call timeout
- Provider retry limit
- Consecutive schema-failure limit
- Cancellation signal
- Pause and resume
- Idempotency keys
- Circuit breaker for provider failures

Every agent returns one of:

- `completed`
- `needs_revision`
- `blocked`
- `failed`

Completion is based on deterministic conditions plus evaluator results—not on an orchestrator repeatedly asking itself whether it is finished.

A workflow that reaches its budget should pause with a useful status and partial artifacts, not silently generate a rushed ending.

## Mature fictional content

Open Hollywood can adopt an app-level policy that permits mature fictional crime, violence, sexuality, and language. It still cannot guarantee that every cloud provider will generate every allowed request; provider policies remain outside the application’s control.

The system should distinguish fictional depiction from operational wrongdoing, while applying hard exclusions required by law and provider agreements. Model settings can explain provider-specific content limitations before a long run begins.