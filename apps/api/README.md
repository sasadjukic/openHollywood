# API application

FastAPI boundary for projects, conversations, artifacts, workflow commands, and
the resumable event stream.

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

## Persisted workspace reads

The browser workspace uses read-only, UI-safe views assembled directly from
SQLite:

```text
GET /api/v1/projects
GET /api/v1/projects/{project_id}/workspace
GET /api/v1/artifact-versions/{artifact_version_id}
```

The project workspace contains persisted conversations, messages, workflow run
status, the active human interrupt identifier, logical artifacts, and immutable
version metadata. Full artifact bodies and evaluation summaries are fetched for
one selected version at a time. These responses deliberately exclude workflow
checkpoint state, model prompts, credentials, and private reasoning.

## Model presets and discovery

Local, Cloud, and Hybrid are fixed, versioned role-routing policies persisted
through the existing `model_profiles` table:

```text
GET  /api/v1/model-profiles
PUT  /api/v1/model-profiles/{profile_id}
POST /api/v1/model-profiles/{profile_id}/activate
GET  /api/v1/models/catalog
```

The first read idempotently creates any missing built-in presets without
guessing model names. Configuration stores exact provider/model identifiers and
local-or-cloud placement only. Activation fails until all required slots are
configured and atomically clears the previous default. Catalog discovery
queries local Ollama and, when `OLLAMA_API_KEY` is available, direct Ollama
Cloud independently so one unavailable source does not hide another source's
models. Credentials never appear in these requests, responses, or persisted
profiles.

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

## Story Blueprint decisions

The mandatory blueprint review accepts one idempotent command:

```text
POST /api/v1/workflow-runs/{workflow_run_id}/decisions
```

The body supplies a client-generated decision UUID, the active interrupt ID,
an `approve`, `revise`, `reject`, or `fork` action, and a required instruction
for every action except approval. The response is emitted only after execution
reaches a durable next interrupt or completes approval. The same decision UUID
can be retried safely with identical command data.

The route delegates to the worker-owned `BlueprintWorkflowService`; it returns
`503` when that execution service has not been attached to the API process.
This keeps creative workflow execution out of the FastAPI route while exposing
the typed command boundary needed by the workspace UI.
