# Workflow worker

Long-running local process that claims durable workflow runs and executes the
creative engine. Start the browser runtime from the repository root with:

```powershell
uv run --extra api uvicorn open_hollywood_worker.app:app --reload
```

The worker-composed FastAPI application owns one sequential SQLite claimant. It
freezes the active complete Local, Cloud, or Hybrid profile onto an ordinary
queued Story Blueprint before its first call, runs or resumes the fixed durable
graph, and starts the child scene-production graph after Blueprint approval.
Runs carrying benchmark campaign lineage remain isolated under the formal
operator harness.

The worker supports cooperative pause, immediate stop with open-call
cancellation, checkpoint recovery, idempotent replay, and hard run budgets.
`BlueprintWorkflowService` owns Story Blueprint decisions; the worker attaches
it to the API decision boundary and exposes a workflow-agnostic command service
for Blueprint and production controls.

Workflow activity intended for the user-facing timeline is appended through the
shared `WorkflowEventStore`. Event payloads contain concise status and artifact
references, never secrets, raw prompts, or private chain-of-thought. The API
replays the same durable rows rather than maintaining a separate in-memory
notification history.

The profile-routed Blueprint and production executors are shared by the browser
runtime and Step 19 harness. Interactive runs snapshot the active profile;
benchmark runs retain their independently frozen campaign profile, prompt,
constraints, and lineage. Both paths persist every invocation and immutable
typed output through the same provider-neutral contracts.
