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
cursor replay and resumable Server-Sent Events. The provider-neutral model
gateway supports dynamically discovered local Ollama models and optional Ollama
Cloud inference with explicit per-model capabilities and budgeted calls. Runtime
secret handles and fail-closed gateway, persistence, fixture, and database-export
guards keep model credentials outside story data and observability records.
The provider-neutral engine now exposes immutable Pydantic schemas for every
v0.1 planning artifact, including an integrated Story Blueprint with validated
character, location, beat, and scene references. A deterministic context-packet
compiler assembles only manifest-declared artifact versions, story-bible
sections, and nearby summaries under explicit input-token budgets. Creative
workflow execution now begins with a fixed, SQLite-checkpointed Story Blueprint
LangGraph. It runs the brief and premise stages, parallel world and character
specialists, integration, and evaluation before pausing at the mandatory
blueprint review boundary. Checkpoints retain only orchestration state and exact
immutable artifact-version references, and failed parallel work resumes without
repeating a successful sibling branch. The review is now a real durable human
interrupt with typed, idempotent approve, revise, reject, and fork commands.
Approval marks the exact blueprint version accepted; revision and rejection
create immutable descendant versions through bounded graph routes; forks create
linked child workflow threads without discarding the source lineage. The
FastAPI command boundary and generated TypeScript SDK expose the same durable
transition contract to the persisted workspace UI. The responsive three-panel
client now reads projects, conversations, workflow activity, run state,
artifact versions, provenance, and evaluations from SQLite-backed API views.
It keeps the Story Blueprint decision beside its source artifact and activity
timeline while preserving the product boundary against a general-purpose
manuscript editor.

Model configuration is now a first-class persisted workflow surface. The
workspace offers Local, Cloud, and Hybrid presets backed by fixed,
provider-neutral role-routing policies and dynamically discovered Ollama model
catalogs. A preset cannot become active until all of its required exact model
slots are configured. Stored profiles contain model identifiers and inference
placement only; cloud credentials continue to resolve from runtime secret
handles and never enter SQLite or the generated API contract.

The useful legacy character-agent dialogue experiment has also been ported as
an isolated, bounded subgraph rather than restored as an application module.
Two registered character actors speak in sequence under a dialogue director
that briefs once and evaluates after each round. Dialogue bodies and director
assessments use typed immutable artifacts, while checkpoint state retains only
budgets, counters, model-profile IDs, and exact version references. This
subgraph is now an optional specialist pass inside the bounded scene-production
loop; it does not add a second human checkpoint or a standalone scene editor.

After blueprint approval, the provider-neutral production graph processes the
three-to-eight planned prose scenes in stable order. Each scene receives an
initial writer pass, an optional embedded dialogue pass and prose integration,
and an independent critique against the exact draft version. Non-passing scenes
return to the writer only while the configured revision allowance remains.
Every accepted scene records whether it passed the rubric or reached that hard
limit, and later scenes receive only immutable references to earlier accepted
work. Checkpoints contain plans, counters, dispositions, and artifact-version
references—not prose, critiques, prompts, or conversation history. The same
unit contract can support chapters when a later product version adds a
long-form format; v0.1 deliberately produces scenes only.

Before any scene becomes canonical, a continuity supervisor checks its exact
draft and plan versions against the exact current Story Bible. Severe findings
enter the shared bounded revision loop and fail closed at the hard limit.
Continuity-cleared scenes produce typed deltas that a deterministic reducer
applies to immutable full-snapshot Story Bible versions. Accepted-scene and
timeline history only append, established identifiers cannot be reused,
resolved mysteries and setup/payoff promises cannot reopen, and the next scene
receives the exact resulting canonical version.

Workflow runs now expose durable, idempotent pause, resume, stop,
retry-from-node, and budget-update commands. Active pause requests take effect
at the next safe node boundary; stop cancels the run and any open invocation;
resume continues from the SQLite checkpoint without repeating completed work.
Retry-from-node creates a linked child run from compatible immutable artifact
versions instead of rewriting source history. Aggregate model-call, token,
cost, and wall-clock usage is visible in the workspace and checked before each
model-backed node so an unaffordable next call pauses with partial artifacts
preserved. Human approval remains a distinct pause reason and still requires
the Story Blueprint decision flow.

Completed short-prose projects now have a deterministic publication boundary.
The provider-neutral engine assembles only complete, latest approved Scene
Draft versions in contiguous story order, renders canonical Markdown, and
exports searchable PDF and editable DOCX files with stable metadata and bytes.
A separate typed Fountain renderer supports future screenplay-family formats
without guessing screenplay structure from prose. The API exposes export
readiness, exact source-version lineage, content hashes, and downloads; the
workspace shows Markdown, PDF, and DOCX controls only when the manuscript
invariants pass.

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

Run every command in this section from the repository root. Install the pinned
Python and JavaScript dependencies:

```powershell
uv sync --extra api
pnpm install
```

The uv workspace installs `open_hollywood_engine` and `open_hollywood_api` as
editable local packages. No `PYTHONPATH` configuration or Uvicorn `--app-dir`
option is required.

Create or upgrade the local SQLite database before starting the API. The
default database is `./data/open_hollywood.db`:

```powershell
uv run alembic upgrade head
```

Then start the API and web client in separate terminals.

Terminal 1 — API:

```powershell
uv run --extra api uvicorn open_hollywood_api.app:app --reload
```

Terminal 2 — web client:

```powershell
pnpm --filter @open-hollywood/web dev
```

Open `http://127.0.0.1:5173`. The API health endpoint is
`http://127.0.0.1:8000/api/v1/health`, and its interactive documentation is at
`http://127.0.0.1:8000/docs`.

The defaults require no environment variables. To use another database, set
its path in the API terminal before running Alembic and Uvicorn:

```powershell
$env:OPEN_HOLLYWOOD_DB_PATH = "C:\path\to\open_hollywood.db"
uv run alembic upgrade head
uv run --extra api uvicorn open_hollywood_api.app:app --reload
```

To use an API origin other than `http://127.0.0.1:8000`, set the client
variable before starting Vite:

```powershell
$env:VITE_API_URL = "http://127.0.0.1:8000"
pnpm --filter @open-hollywood/web dev
```

Local Ollama must be running only when using local models. Direct Ollama Cloud
catalog discovery additionally reads `OLLAMA_API_KEY` from the API process
environment; credentials must never be written to project files.

When a project has three to eight complete, approved Scene Draft artifacts, its
workspace header enables Markdown, PDF, and DOCX downloads. The same downloads
are available from:

```text
GET /api/v1/projects/{project_id}/exports
GET /api/v1/projects/{project_id}/exports/{markdown|pdf|docx}
```

The manifest reports the exact immutable scene-version IDs used. A project
that does not yet form a complete, contiguous manuscript reports no available
formats, and a direct download attempt returns `409 Conflict`.

When a FastAPI route or response model changes, regenerate the shared SDK:

```powershell
pnpm contracts:generate
```

Inspect the active revision or roll back one migration during development:

```powershell
uv run alembic current
uv run alembic downgrade -1
```

Run the applicable quality checks before handing off a change:

```powershell
uv run --extra api ruff check apps/api engine scripts tests migrations
uv run --extra api ruff format --check apps/api engine scripts tests migrations
uv run --extra api mypy apps/api engine scripts tests migrations
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
