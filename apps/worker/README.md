# Workflow worker

Long-running process that claims durable workflow runs and executes the creative
engine. The shared Step 10 execution service now runs or resumes the fixed Story
Blueprint LangGraph with SQLite checkpoints; a standalone claiming loop remains
future worker work.

The worker must support cancellation, checkpoint recovery, idempotency, and
hard run budgets.

`BlueprintWorkflowService` now also owns the durable Story Blueprint interrupt
commands. It validates the active interrupt ID, persists a human decision
before resuming, and can recover the resulting checkpoint through the same
SQLite thread. Fork creates an explicitly linked child `WorkflowRun`; a future
standalone claiming loop should attach this service to the API command
boundary rather than reimplementing the transitions.

Workflow activity intended for the user-facing timeline is appended through the
shared `WorkflowEventStore`. Event payloads contain concise status and artifact
references, never secrets, raw prompts, or private chain-of-thought. The API
replays the same durable rows rather than maintaining a separate in-memory
notification history.
