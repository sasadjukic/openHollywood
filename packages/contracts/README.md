# Generated client contracts

Generated TypeScript API client and schemas derived from FastAPI's OpenAPI
document. Do not manually duplicate Python API request/response models here.

## Regenerate

From the repository root:

```powershell
pnpm contracts:generate
```

This exports `openapi.json` directly from the FastAPI application and runs the
exactly pinned Hey API generator. Files under `src/generated/` are generated
artifacts and must not be edited manually.
