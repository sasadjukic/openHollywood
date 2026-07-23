# Web application

React and TypeScript workspace for chat, workflow activity, approval, artifact
inspection, immutable version history, and run status. The responsive
three-panel layout is backed by persisted SQLite data exposed through FastAPI;
it is an artifact-centered workflow surface, not a general manuscript editor.

## Run locally

Start the FastAPI service first, then run from the repository root:

```powershell
pnpm --filter @open-hollywood/web dev
```

The client defaults to `http://127.0.0.1:8000` for its API. Override
`VITE_API_URL` for another local origin. API calls must use the generated
`@open-hollywood/contracts` SDK rather than duplicate request or response types.

The left panel switches between persisted story projects and their artifacts.
The center combines durable conversation messages with workflow events and
shows the Story Blueprint decision composer while a run is paused. The right
inspector renders the selected immutable artifact version, provenance, and
evaluation summary. On narrow screens, navigation and inspection become
dismissible drawers.
