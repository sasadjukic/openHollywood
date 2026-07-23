# Step-by-step implementation sequence

This file is the authoritative implementation progress tracker. Mark a step
complete only when its deliverables exist and the relevant checks pass. Update the completion date and evidence in the same change.

## Status legend

- `[x]` COMPLETED
- `[~]` IN PROGRESS
- `[ ]` NOT STARTED

## Rewrite foundation — COMPLETED 2026-07-13

- [x] Preserve the legacy implementation on `openHollywood-legacy`.
- [x] Create and publish the immutable `legacy-v2-final` tag.
- [x] Move the Python environment to `.venv` and standardize on Python 3.13.
- [x] Standardize on Node.js 24 LTS, pnpm 11, and uv.
- [x] Track the product vision and project bible.
- [x] Adopt the MIT License for the public project.
- [x] Add toolchain pins, workspace manifests, text-format rules, environment
  template, repository guidance, and module responsibility documents.
- [x] Preserve useful legacy prompts, scene configuration, and director-flow
  behavior as regression fixtures.

## Implementation steps

1. [x] **COMPLETED 2026-07-13 — Write architecture decision records.**
   Accepted ADRs cover local-first deployment, an explicit durable graph,
   SQLite persistence, a provider-neutral model gateway, and versioned
   artifacts with bounded context. Evidence: `docs/adr/0001` through `0005`.

2. [x] **COMPLETED 2026-07-13 — Freeze and capture the legacy prototype.**
   The final implementation is preserved by branch and tag. Useful prompts,
   scene configuration, director state, call order, and termination invariants
   are captured under `tests/fixtures/legacy/`.

3. [x] **COMPLETED 2026-07-21 — Create the React/TypeScript client and FastAPI application with a shared generated OpenAPI client.** The branded React/Vite shell consumes a typed FastAPI health boundary through an exactly pinned Hey API SDK generated from OpenAPI 3.1. Evidence:
`apps/web/`, `apps/api/open_hollywood_api/`, `packages/contracts/`, and
`tests/api/`. Ruff, mypy, pytest, Prettier, ESLint, TypeScript, Vitest, the
production build, and desktop/mobile browser verification pass.

4. [x] **COMPLETED 2026-07-21 — Add SQLite, SQLAlchemy, and Alembic.** The
migration-managed SQLite layer implements `Project`, `Conversation`,`Message`, `Artifact`, immutable `ArtifactVersion` lineage, `WorkflowRun`,
observable `AgentInvocation` records with exact input-version links,
secret-free `ModelProfile` configuration, and `Evaluation`. Evidence:
`apps/api/open_hollywood_api/persistence/`, `alembic.ini`, `migrations/`, and `tests/persistence/`. Migration upgrade/downgrade and metadata parity, Ruff, mypy, pytest, Prettier, ESLint, TypeScript, Vitest, and the production build pass.

5. [x] **COMPLETED 2026-07-21 — Implement an append-only workflow event
stream.** Workflow events use globally ordered durable IDs and SQLite
mutation-rejection triggers. The API exposes typed paginated replay after an
exclusive event cursor plus an SSE feed that replays missed events before
following new rows; reconnects accept both `after` and `Last-Event-ID`.
Evidence: `migrations/versions/0002_append_only_workflow_events.py`, `apps/api/open_hollywood_api/services/workflow_events.py`, `apps/api/open_hollywood_api/routes/workflow_events.py`, generated contracts,
and persistence/API integration tests. Migration upgrade/downgrade and
metadata parity, Ruff, mypy, pytest, Prettier, ESLint, TypeScript, Vitest,
and the production build pass.

6. [x] **COMPLETED 2026-07-22 — Build `ModelGateway` and `ModelCapabilities`.** Provider-neutral, immutable call contracts require
explicit token/cost budgets and reproducibility identifiers. The first
adapter dynamically discovers local Ollama and Ollama Cloud models, inspects
per-model features and context windows, classifies cloud offload correctly,
supports runtime-injected cloud bearer authentication, normalizes usage,
timing, finish state, and retryable errors, and rejects unsupported cloud
structured-output calls before inference. No Google, OpenAI, or LiteLLM
dependency was added because Ollama Local plus Ollama Cloud is sufficient for the initial short-fiction slice. Evidence: `engine/open_hollywood_engine/models/`, `tests/models/`, `engine/models/README.md`, and `open_hollywood_bible/model_configuration.md`. Ruff, mypy, pytest (including 16 model-gateway tests), Prettier, ESLint, TypeScript, Vitest, and the production build pass. Live discovery against the development Ollama server also classified two installed local models and two cloud-offloaded models with their reported context windows.

7. [x] **COMPLETED 2026-07-22 — Add secure secret handling.** Provider-neutral runtime handles and opaque redacting values keep model credentials outside workflow and domain contracts. The current environment-backed store resolves credentials only when constructing the provider transport; fail-closed gateway guards reject credentials in prompts and provider responses, while SQLAlchemy flush guards protect every durable story, profile, event, and invocation record. Database exports receive an independent full-table audit, and committed fixtures are checked against credentials configured in the test process. Evidence:
`engine/open_hollywood_engine/secrets/`, `apps/api/open_hollywood_api/persistence/secret_policy.py`, ADR 0006, and secret-policy integration tests. Ruff, mypy, 51 pytest tests, Prettier, ESLint, TypeScript, Vitest, and the production build pass.

8. [x] **COMPLETED 2026-07-22 — Define Pydantic artifact schemas.** Immutable, extra-field-forbidding contracts cover Creative Brief, Character, Relationship, Location, World Rule, Beat, Scene Plan, Critique, Continuity Finding, and the integrated Story Blueprint. A canonical artifact registry exposes JSON Schema for structured model output, while local and blueprint-level validators enforce v0.1 scope, stable IDs, ordered beats and scenes, reference integrity, critique and continuity routing invariants, and agreement with the Creative Brief. Evidence: `engine/open_hollywood_engine/artifacts/`, `tests/artifacts/`, and
`engine/artifacts/README.md`. Ruff, mypy, 66 pytest tests, Prettier, ESLint,
TypeScript, Vitest, and the production build pass.

9. [x] **COMPLETED 2026-07-22 — Build the context-packet compiler.** Versioned per-specialist manifests declare artifact cardinalities, exact story-bible sections, nearby-summary bounds, and structured output types. The deterministic compiler rejects undeclared or ambiguous versions, renders canonical packets with assignments, constraints, dependencies, output JSON Schema, and rubrics, and carries exact input-version lineage into model invocations. Mandatory context fails closed when it exceeds the reserved input-token envelope; budget-optional context is included in stable priority order or omitted with an observable reason. Token counting is injectable and versioned, with a conservative provider-neutral UTF-8 byte fallback. Evidence: `engine/open_hollywood_engine/context/`, `tests/context/`, and `engine/context/README.md`. Ruff, mypy, 76 pytest tests, Prettier, ESLint, TypeScript, Vitest, and the production build pass.

10. [x] **COMPLETED 2026-07-22 — Create the first persisted LangGraph.** The
fixed, versioned Story Blueprint graph runs `intake → brief → premise → parallel world and character specialists → integration → evaluation → approval` with registered node contracts, bounded timeouts, and retries limited to explicit retryable specialist failures. SQLite checkpoints store only JSON-safe coordination state and exact immutable artifact-version references; the workflow run mirrors its latest checkpoint and lifecycle events. A failed parallel super-step resumes in a fresh service without repeating the successful sibling, and the approval boundary leaves the run paused for Step 11. Evidence: `engine/open_hollywood_engine/workflows/`,
`apps/api/open_hollywood_api/services/blueprint_workflow.py`,
`migrations/versions/0003_langgraph_checkpoints.py`, `tests/workflows/`, and
`engine/workflows/README.md`. Ruff, mypy, 80 pytest tests, Prettier, ESLint,
TypeScript, Vitest, and the production build pass.

11. [x] **COMPLETED 2026-07-23 — Implement human interrupts for approve,
revise, reject, and fork.** The Story Blueprint review is a real
SQLite-checkpointed LangGraph interrupt with typed, idempotent human decisions. Approval succeeds the run and marks the exact active blueprint version approved; revision reruns integration and evaluation; rejection regenerates from premise through the parallel specialists; and fork freezes the source lineage while creating an explicitly linked child checkpoint thread. Free-form instructions live once in secret-guarded application persistence while graph state and events carry only decision and artifact-version references. The FastAPI command endpoint and generated TypeScript SDK expose the same durable contract for Step 12. Evidence:
`engine/open_hollywood_engine/workflows/`,
`apps/api/open_hollywood_api/services/blueprint_workflow.py`,
`apps/api/open_hollywood_api/routes/blueprint_decisions.py`,
`migrations/versions/0004_human_interrupts.py`, generated contracts, and
workflow/API/persistence integration tests. Migration upgrade/downgrade and
metadata parity, Ruff, mypy, 86 pytest tests, Prettier, ESLint, TypeScript,
Vitest, and the production build pass.

12. [ ] **Build the workspace UI around persisted data:** projects, chat, event timeline, artifact viewer, versions, and run status.

13. [ ] **Add model presets:** Local, Cloud, and Hybrid.

14. [ ] **Port the legacy character-agent dialogue experiment** into an isolated subgraph with typed inputs, outputs, and regression tests.

15. [ ] **Implement the scene/chapter production loop** with bounded critique and revision.

16. [ ] **Add deterministic story-bible updates and continuity invariants**
after every accepted unit.

17. [ ] **Add run controls:** stop, pause, resume, retry-from-node, and budgets.

18. [ ] **Implement Fountain/Markdown renderers and PDF/DOCX export.**

19. [ ] **Build the evaluation harness** and run the benchmark corpus across
local, cloud, and hybrid profiles.

20. [ ] **Tune prompts and graph routing** based on blind human preference—not isolated attractive examples.

21. [ ] **Package the stable system with Tauri** and test crash/restart, offline, missing-model, invalid-key, provider-timeout, and low-disk-space behavior.

22. [ ] **Consider broader formats and hosted features only after the core is proven:** songs, poems, video scripts, collaboration, or hosted accounts.
