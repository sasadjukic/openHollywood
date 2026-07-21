# Web application

React and TypeScript workspace for chat, workflow activity, approval, artifact
inspection, version comparison, and settings. The browser-based vertical slice
is the first user interface.

## Run locally

Start the FastAPI service first, then run from the repository root:

```powershell
pnpm --filter @open-hollywood/web dev
```

The client defaults to `http://127.0.0.1:8000` for its API. Override
`VITE_API_URL` for another local origin. API calls must use the generated
`@open-hollywood/contracts` SDK rather than duplicate request or response types.
