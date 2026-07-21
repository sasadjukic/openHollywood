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
