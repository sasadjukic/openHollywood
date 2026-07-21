# Workflow worker

Long-running process that claims durable workflow runs and executes the creative
engine. Implementation begins after the API/client foundation exists.

The worker must support cancellation, checkpoint recovery, idempotency, and
hard run budgets.

Workflow activity intended for the user-facing timeline is appended through the
shared `WorkflowEventStore`. Event payloads contain concise status and artifact
references, never secrets, raw prompts, or private chain-of-thought. The API
replays the same durable rows rather than maintaining a separate in-memory
notification history.
