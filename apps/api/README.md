# API application

FastAPI boundary for projects, conversations, artifacts, workflow commands, and
the resumable event stream. Implementation begins in step 3.

The API may call application services but must not contain creative workflow or
provider logic.

## Run locally

From the repository root:

```powershell
uv run --extra api uvicorn --app-dir apps/api open_hollywood_api.app:app --reload
```

The initial `/api/v1/health` boundary provides a typed vertical slice for the
generated web SDK. Interactive API documentation is available at `/docs` and
the canonical OpenAPI 3.1 document at `/openapi.json`.
