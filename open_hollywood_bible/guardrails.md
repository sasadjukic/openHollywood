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

## Durable run-control boundary

Step 17 persists every pause, resume, stop, retry-from-node, and budget update
under a caller-supplied idempotency key. A repeated key must resolve to the same
command and cannot be reused with different data.

Pause is cooperative for active work and takes effect before the next
registered node. Stop durably cancels the workflow and any pending or running
model invocation, with the graph observing cancellation at its next safe
boundary. Resume is valid only for user- or budget-paused runs; the mandatory
Story Blueprint approval remains a separate typed interrupt.

The active budget carries a graph recursion ceiling, aggregate model-call,
input-token, output-token, cost, and wall-clock ceilings, plus conservative
per-call token and cost reservations. A model-backed node may start only when
the remaining aggregate budget can cover that reservation. Exhaustion records
the violated limits and consumed usage, pauses before the call, and leaves
already-created artifacts untouched.

Retry-from-node is limited to registered workflow nodes. It creates a linked
child run, seeds it with only compatible exact artifact-version references, and
never deletes or rewrites the source checkpoint history. Replaying a retry
command after a process interruption reuses its existing child and checkpoint.

## Mature fictional content

Open Hollywood can adopt an app-level policy that permits mature fictional crime, violence, sexuality, and language. It still cannot guarantee that every cloud provider will generate every allowed request; provider policies remain outside the application’s control.

The system should distinguish fictional depiction from operational wrongdoing, while applying hard exclusions required by law and provider agreements. Model settings can explain provider-specific content limitations before a long run begins.
