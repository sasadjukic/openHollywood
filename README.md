# Open Hollywood

Open Hollywood is a local-first agentic story studio that turns a user premise
into an approved story blueprint and then autonomously produces a versioned,
evaluated, properly formatted work through a durable specialist-agent workflow.

## Project status

The legacy scene-execution prototype is preserved on the
`openHollywood-legacy` branch and at the immutable `legacy-v2-final` tag. The
active rewrite now includes a browser-based React client, a local FastAPI
service, a generated TypeScript SDK shared through the contracts package, and a
migration-managed SQLite persistence layer for projects, conversations,
artifacts, workflow runs, model invocations, profiles, and evaluations. Workflow
activity is exposed through a durable append-only event log with paginated
cursor replay and resumable Server-Sent Events. Creative workflow implementation
begins in subsequent steps.

The v0.1 target is deliberately narrow: short prose fiction, local-first
storage, optional local/cloud/hybrid inference, and one mandatory story
blueprint approval before autonomous drafting.

## Source of truth

- [`open_hollywood_future.md`](open_hollywood_future.md) describes the product
  vision and the distinction between Open Hollywood and SammyAI.
- [`open_hollywood_bible/`](open_hollywood_bible/) contains the accepted product,
  architecture, workflow, evaluation, and UI guidance.
- [`open_hollywood_bible/step_by_step_implementation.md`](open_hollywood_bible/step_by_step_implementation.md)
  is the authoritative implementation progress tracker.
- [`docs/adr/`](docs/adr/) records accepted architecture decisions.

## Toolchain

- Python 3.13
- uv 0.11.28+
- Node.js 24 LTS
- pnpm 11.12.0+

Versions are pinned in `.python-version`, `.node-version`, `pyproject.toml`,
and `package.json` where appropriate.

## Repository layout

```text
apps/          Deployable API, worker, web, and desktop applications
engine/        Provider-neutral creative workflow and domain engine
packages/      Shared TypeScript contracts and UI components
migrations/    Database migrations
tests/         Cross-package, integration, evaluation, and legacy fixtures
docs/          Architecture decisions and technical documentation
images/        Open Hollywood brand assets
```

## Development

Install the pinned Python and JavaScript dependencies from the repository root:

```powershell
uv sync --extra api
pnpm install
```

Start the API and web client in separate terminals:

```powershell
uv run --extra api uvicorn --app-dir apps/api open_hollywood_api.app:app --reload
```

```powershell
pnpm --filter @open-hollywood/web dev
```

The client runs at `http://127.0.0.1:5173` and the API documentation is at
`http://127.0.0.1:8000/docs`. Set `VITE_API_URL` when the API uses another
origin.

When a FastAPI route or response model changes, regenerate the shared SDK:

```powershell
pnpm contracts:generate
```

Create or upgrade the local SQLite database using the path in
`OPEN_HOLLYWOOD_DB_PATH` (default: `./data/open_hollywood.db`):

```powershell
uv run alembic upgrade head
```

Inspect the active revision or roll back one migration during development:

```powershell
uv run alembic current
uv run alembic downgrade -1
```

Run the applicable quality checks before handing off a change:

```powershell
uv run --extra api ruff check apps/api scripts tests migrations
uv run --extra api ruff format --check apps/api scripts tests migrations
uv run --extra api mypy apps/api scripts tests migrations
uv run --extra api pytest
pnpm format:check
pnpm lint
pnpm typecheck
pnpm test
pnpm build
```

## License

Open Hollywood is available under the [MIT License](LICENSE). Contributions,
forks, experimentation, and derivative projects are welcome under its terms.
