# API application

FastAPI boundary for projects, conversations, artifacts, workflow commands, and
the resumable event stream. Implementation begins in step 3.

The API may call application services but must not contain creative workflow or
provider logic.

`open_hollywood_api.persistence` owns the SQLAlchemy records, SQLite engine
configuration, and session factory used by the local application. Schema
creation belongs to the root Alembic migration chain; application startup must
not call `Base.metadata.create_all()`.

## Run locally

From the repository root:

```powershell
uv run --extra api uvicorn --app-dir apps/api open_hollywood_api.app:app --reload
```

The initial `/api/v1/health` boundary provides a typed vertical slice for the
generated web SDK. Interactive API documentation is available at `/docs` and
the canonical OpenAPI 3.1 document at `/openapi.json`.

## Workflow events

Workflow producers append UI-safe summaries through `WorkflowEventStore`.
Events receive a global, monotonically increasing integer ID and cannot be
updated or deleted; SQLite triggers enforce that invariant. Payloads must never
contain secrets or private chain-of-thought.

Clients catch up with a typed, exclusive cursor page:

```text
GET /api/v1/workflow-runs/{workflow_run_id}/events?after={last_event_id}
```

They can then open the resumable SSE feed. The feed first replays every missed
event and then follows new rows. It accepts both the `after` query parameter for
restoring a cursor after page reload and the standard `Last-Event-ID` header for
transport reconnects:

```text
GET /api/v1/workflow-runs/{workflow_run_id}/events/stream?after={last_event_id}
```

SSE frames use the durable database ID in the `id` field and a
`WorkflowEventEnvelope` JSON object in `data`. The generated TypeScript SDK
contains both the paginated replay and SSE operations.
