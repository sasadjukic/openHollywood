# Open Hollywood repository guidance

## Product contract

- Open Hollywood is a local-first, fully agentic creative-writing workspace.
- v0.1 supports short prose fiction only.
- The normal v0.1 flow has one mandatory human checkpoint: Story Blueprint
  approval before autonomous drafting.
- The UI is chat- and artifact-centered. Do not introduce a general-purpose
  manuscript editor.
- Local, cloud, and hybrid model profiles are first-class capabilities.

## Architecture constraints

- Build a modular monolith with a React/TypeScript client, FastAPI API, Python
  workflow worker, and provider-neutral Python engine.
- Use an explicit durable graph with registered specialist roles. Do not create
  an unconstrained or recursively spawning agent swarm.
- Keep domain models independent from LangGraph and provider SDK types.
- Treat the canonical story bible and immutable artifact versions as the source
  of story truth. Do not use an ever-growing chat transcript as memory.
- Every model call must be budgeted, observable, reproducible, cancellable, and
  associated with exact input artifact versions.
- Store local state in SQLite for v0.1. Preserve a future migration path to
  PostgreSQL without implementing hosted infrastructure now.
- Never store API keys in source, prompts, traces, fixtures, story artifacts, or
  database exports.

## Sources of truth

Read these before architecture or workflow changes:

1. `open_hollywood_future.md`
2. `open_hollywood_bible/README.md`
3. `open_hollywood_bible/important_decisions.md`
4. `open_hollywood_bible/product_contract_and_benchmarks.md`
5. Relevant accepted records under `docs/adr/`

The complete legacy implementation is available only through the
`legacy-v2-final` tag and `openHollywood-legacy` branch. Do not restore legacy
modules into the rewrite except through a deliberate port backed by tests.

## Tooling

- Python: 3.13, managed with uv.
- JavaScript/TypeScript: Node.js 24 LTS, managed with pnpm.
- Python quality: Ruff, mypy strict mode, and pytest.
- TypeScript quality: strict TypeScript, ESLint, Prettier, Vitest, and Playwright.
- Prefer generated TypeScript API contracts from FastAPI OpenAPI schemas over
  manually duplicating Python request/response types.

## Progress tracking

`open_hollywood_bible/step_by_step_implementation.md` is authoritative.

- Mark a step complete only after its deliverables exist and relevant checks
  pass.
- Update the tracker in the same change that completes a step.
- Record partial work as `IN PROGRESS`; never mark an aspirational scaffold as
  complete.
- Do not start a later product phase merely because its directories exist.

## Change discipline

- Preserve user changes and keep unrelated edits out of a task.
- Add migrations for persisted schema changes once persistence exists.
- Prefer small vertical slices with tests over broad empty abstractions.
- Validate structured model output at system boundaries.
- Avoid adding dependencies until a concrete use requires them.
- Keep all text files UTF-8 and follow `.editorconfig` and `.gitattributes`.
- Before handing off code, run the applicable lint, type-check, unit, integration,
  and production-build commands documented in the root README.
