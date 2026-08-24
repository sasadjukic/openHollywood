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

12. [x] **COMPLETED 2026-07-23; INTAKE CORRECTED 2026-07-25; UX CORRECTED
2026-08-02; RUNTIME CORRECTED 2026-08-04 — Build the
workspace UI around persisted data.** The responsive three-panel React workspace
now lists durable projects and story artifacts, merges persisted chat with
workflow activity, presents current run and checkpoint status, and renders
immutable artifact bodies, version history, provenance, and evaluations without
introducing a manuscript editor. The empty library opens in the same workspace
shell with an actionable first-premise composer instead of a dead-end welcome
screen; its idempotent API command atomically persists the project, conversation,
user message, queued Story Blueprint run, and safe workflow event. The Story
Blueprint checkpoint supports approve, revise, reject, and fork through the
generated SDK. FastAPI boundaries assemble UI-safe project workspaces and
artifact details directly from SQLite while excluding checkpoints, prompts, and
secrets. Each desktop panel now exposes bounded independent scrolling, the
premise composer grows with its content, and stopped stories can be permanently
removed with their complete local workflow and artifact aggregate. Loading,
empty, disconnected, and mobile panel states are covered.
Evidence:
`apps/api/open_hollywood_api/services/workspace.py`,
`apps/api/open_hollywood_api/routes/workspace.py`, `apps/web/src/`, generated
contracts, and API/React tests. Ruff, mypy, 178 pytest tests, Prettier, ESLint,
TypeScript, 7 Vitest tests, and the production build pass.

The browser-runtime correction now composes FastAPI with one sequential local
workflow worker instead of launching the storage-only API. The worker claims
only ordinary queued stories, freezes the active complete Local, Cloud, or
Hybrid profile before the first invocation, resumes SQLite checkpoints, and
hands an approved Story Blueprint to the durable scene-production graph.
Pause, resume, stop, retry, and budget commands share a worker-owned command
boundary; stopping cancels the active execution task. Frozen benchmark runs are
excluded from interactive claiming and remain operator-owned. The API-only app
continues to fail closed with an actionable `503`. Evidence:
`apps/worker/open_hollywood_worker/`, the reusable profile-routed executors,
`apps/api/open_hollywood_api/services/workflow_commands.py`, runtime/API/React
regression tests, and updated launch documentation. Ruff, formatting, mypy,
181 pytest tests, Prettier, ESLint, TypeScript, 8 Vitest tests, and the
production build pass.

13. [x] **COMPLETED 2026-07-23 — Add Local, Cloud, and Hybrid model
presets.** Provider-neutral, schema-versioned preset contracts now route every registered Story Blueprint specialist to an exact local or cloud model. Local keeps all roles on-device, Cloud assigns all roles to cloud inference, and Hybrid keeps structured preparation and evaluation local while sending high-impact creative reasoning to cloud. The three presets are seeded idempotently into SQLite without guessed model names, cannot activate until every required model slot is configured, and resolve exact role assignments for future invocations. FastAPI exposes durable configuration, atomic activation, and failure-isolated dynamic Ollama catalog discovery; the responsive workspace settings surface uses the generated SDK and persists no credentials. Evidence: `engine/open_hollywood_engine/models/profiles.py`, `apps/api/open_hollywood_api/services/model_profiles.py`, `apps/api/open_hollywood_api/routes/model_profiles.py`, `apps/web/src/components/ModelSettings.tsx`, generated contracts, and engine/API/React tests. Ruff, mypy, 99 pytest tests, Prettier, ESLint, TypeScript, 4 Vitest tests, and the production build pass.

14. [x] **COMPLETED 2026-07-23 — Port the legacy character-agent dialogue
experiment into an isolated subgraph.** The preserved two-actor/director concept now runs as a fixed LangGraph topology: one director briefing, character one, character two, and one director evaluation per bounded round. Typed scene, actor, briefing, dialogue-turn, evaluation, and completion contracts replace legacy mutable state and provider-specific calls. Checkpoints contain only JSON-safe budgets, counters, profile identifiers, and exact immutable artifact references; model output bodies remain validated artifact versions. Minimum rounds, climax-or-resolution closure, declared endings, maximum rounds, timeouts, and retryable failures are enforced deterministically. Step 13 profiles upgrade in memory from schema v1 and route the registered `character_actor` and `dialogue_director` roles without breaking existing profiles. Regression tests use the preserved `legacy-v2-final` director-flow fixture to retain its one-briefing, two-actors-per-round, one-evaluation, and seven-call/two-round behavior. Evidence: `engine/open_hollywood_engine/workflows/dialogue_contracts.py`, `engine/open_hollywood_engine/workflows/dialogue_graph.py`, typed dialogue artifact schemas, and `tests/workflows/test_dialogue_subgraph.py`. Ruff, mypy, 106 pytest tests, Prettier, ESLint, TypeScript, 4 Vitest tests, and the production build pass.

15. [x] **COMPLETED 2026-07-23 — Implement the scene/chapter production
loop with bounded critique and revision.** The fixed `scene_production`
LangGraph consumes an approved Story Blueprint plus three-to-eight ordered
Scene Plan assignments, writes immutable prose versions, optionally embeds the Step 14 two-character dialogue subgraph and integrates its outputs, and sends each exact draft version to an independent critic. Non-passing drafts return to the writer only while the configured revision allowance remains; each canonical scene records whether it passed the rubric or reached the hard limit. Incomplete drafts, mismatched critique targets, reused versions, invalid artifact kinds, and malformed state fail closed. Checkpoints retain only budgets, counters, deterministic dispositions, and immutable artifact references—not prose, dialogue, critique bodies, prompts, or provider objects. Model-profile schema v3 adds `scene_writer` and `scene_critic` while upgrading Step 13 and Step 14 profiles in memory. The unit abstraction is ready for a later chapter format, while v0.1 remains intentionally limited to prose scenes. Evidence:
`engine/open_hollywood_engine/workflows/production_contracts.py`,
`engine/open_hollywood_engine/workflows/production_graph.py`, the typed
`SceneDraft` artifact, and `tests/workflows/test_scene_production.py`. Ruff,
mypy, 112 pytest tests, Prettier, ESLint, TypeScript, 4 Vitest tests, and the production build pass.

16. [x] **COMPLETED 2026-07-24 — Add deterministic story-bible updates and
continuity invariants after every accepted unit.** The fixed production graph now gates every candidate scene against the exact current Story Bible, Scene Plan, and Scene Draft versions before canonical acceptance. Error or blocking findings consume the shared bounded revision allowance and fail closed if they survive its hard limit; rubric-limit acceptance cannot bypass continuity. Each cleared scene produces a typed delta and a full immutable Story Bible successor that must equal the pure deterministic reducer exactly. Accepted-scene and timeline histories append monotonically, fact and event identifiers cannot be reused, entity references remain within the approved blueprint catalog, and resolved mysteries or setup/payoff promises cannot reopen. Later writers, dialogue passes, critics, and continuity checks receive the exact resulting bible version, while checkpoints retain only artifact references and deterministic routing state. Model-profile schema v4 registers local-friendly `continuity_supervisor` and `story_bible_maintainer` roles and upgrades versions 1–3 in memory. Evidence: `engine/open_hollywood_engine/artifacts/story_bible.py`, `engine open_hollywood_engine/workflows/production_graph.py`, `tests/artifacts/test_story_bible.py`, and `tests/workflows/test_scene_production.py`. Ruff, mypy, 120 pytest tests, Prettier, ESLint, TypeScript, 4 Vitest tests, and the production build pass.

17. [x] **COMPLETED 2026-07-24 — Add run controls: stop, pause, resume,
retry-from-node, and budgets.** Provider-neutral contracts define strict
aggregate run budgets and typed idempotent commands. SQLite now persists each command, pause reason, source checkpoint, and resulting child run. Pause requests made during execution take effect before the next registered node; stop cancels the run and open invocations; resume continues from the durable checkpoint while keeping the Story Blueprint approval interrupt distinct. Retry-from-node is restricted to registered Story Blueprint specialist nodes, prunes obsolete outputs, preserves compatible exact artifact versions, and creates an immutable linked child lineage. Crash replay reuses that child and its checkpoint rather than duplicating work. Before every model-backed node, the runtime reserves model-call, input-token, output-token, and cost capacity and checks elapsed wall-clock time; exhaustion pauses with useful usage and limit events while preserving partial artifacts. FastAPI, the generated TypeScript SDK, and the workspace expose the same controls, current limits, and aggregate usage. Evidence:
`engine/open_hollywood_engine/workflows/run_controls.py`, `apps/api/open_hollywood_api/services/run_controls.py`, `apps/api/open_hollywood_api/routes/run_controls.py`, `migrations/versions/0005_workflow_run_controls.py`, generated contracts, workspace UI controls, and workflow/API/migration/React tests. Migration upgrade/downgrade and metadata parity, Ruff, mypy, 129 pytest tests, Prettier, ESLint, TypeScript, 5 Vitest tests, and the production build pass.

18. [x] **COMPLETED 2026-07-24 — Implement Fountain/Markdown renderers and
PDF/DOCX export.** A provider-neutral, invariant-checked manuscript contract
assembles only complete latest versions of approved Scene Draft artifacts in
unique, contiguous three-to-eight-scene order. The canonical Markdown renderer normalizes line endings and escapes structural markup. A separate typed Fountain screenplay contract renders title pages, forced headings and action, dialogue structures, transitions, sections, synopses, centered text, and page breaks without guessing script structure from prose. Searchable US-Letter PDF and editable US-Letter DOCX exporters use fixed metadata and canonicalized containers so identical inputs produce identical bytes. FastAPI exposes an export manifest, exact immutable source-version lineage, SHA-256 ETags, sanitized downloads, and fail-closed `409` behavior; the generated TypeScript SDK and workspace enable Markdown, PDF, and DOCX controls only for exportable projects. Evidence: `engine/open_hollywood_engine/rendering/`, `apps/api/open_hollywood_api/services/exports.py`, `apps/api/open_hollywood_api/routes/exports.py`, generated contracts, workspace export controls, and rendering/API/React tests. All four representative PDF pages and all four representative DOCX pages passed visual inspection. Ruff, mypy, 140 pytest tests, Prettier, ESLint, TypeScript, 5 Vitest tests, and the production build pass.

19. [~] **IN PROGRESS 2026-07-26 — Build the evaluation harness** and run the benchmark corpus across local, cloud, and hybrid profiles. The provider-neutral harness core now strictly validates the frozen 12-prompt v0.1 corpus and pins its canonical digest, exact graph and prompt-contract versions, direct-model baseline, complete secret-free Local/Cloud/Hybrid profile snapshots, and prompt seeds into a deterministic 48-case campaign plan. Sequential case execution is failure-isolated and resumable from terminal results; successful outputs must carry exact workflow-run, model-invocation, and immutable artifact-version lineage. The accepted weighted rubric and hard gates are executable contracts. Deterministic A/B packaging separates provenance-free reviewer documents from the private answer key, and reporting maps blind human preferences back to systems while calculating the accepted completion, continuity, quality, preference, and cost thresholds. The operator command validates corpus integrity and creates plans from fully configured persisted presets. The application layer now executes the direct single-model baseline through a bounded provider-neutral call and persists its frozen prompt, invocation, workflow, and immutable story lineage idempotently. Campaign reports checkpoint atomically after each case, failed cases retry only when explicitly requested, and operator-configurable Ollama timeouts support long-form calls while distinguishing provider timeouts from outages. Retrying after an interrupted process closes stale running baseline attempts and preserves their immutable input lineage. Ollama Cloud response aliases are accepted only when they normalize to the frozen requested model; requested and provider-reported identifiers are both persisted. Operator commands create separated public/private review packets and summaries from schema-validated evidence. Failed structured calls retain provider usage, finish reason, response hash, and length, while a lone JSON fence is normalized without accepting surrounding
commentary. Agentic cases now enter the real durable Story Blueprint graph:
every registered specialist resolves its exact frozen profile selection,
receives deterministic immutable inputs and benchmark constraints, uses schema enforcement when the deployment supports it, records a budgeted invocation plus output lineage, validates cross-artifact invariants, and pauses at the mandatory human approval interrupt. Replaying a paused case performs no duplicate model calls. Creative Brief prompt contract v6 requests only creative choices and the application deterministically attaches the frozen premise, format, genres, maturity, required elements, and forbidden elements; this keeps optional model fields from weakening benchmark intent. Prompted non-schema invariants preserve exact benchmark constraints; parallel World specialists cannot invent unresolved character references; the integrator emits only new beats and scene plans, and the application deterministically assembles immutable specialist artifacts into the Story Blueprint. Prompt contract v9 binds integration to a compact world summary, the Creative Brief's exact scene count, and no more than two beats per scene. Prompt-only cloud structured-output retries
persist their attempt number and receive safe validation locations plus provider finish metadata without storing or echoing the failed story response. Word bounds remain application-validated instead of emitting grammar keywords unsupported by local Ollama structured output. Model-executing operator commands now reject a campaign plan when its baseline, Blueprint, production prompt, or graph versions differ from the running build, including the direct-story graph and nested dialogue subgraph. Blueprint graph v4, scene-production graph v2, and dialogue
subgraph v2 give model-backed nodes a 900-second formal long-form ceiling while retaining bounded execution; cancelled or timed-out calls now close their persisted invocation instead of remaining `RUNNING`. A 12-case Local
qualification reached the mandatory approval interrupt while prompt contracts v6 through v9 were being hardened. A subsequent frozen v9 staging campaign completed all 12 Baselines after one explicit provider-timeout retry, paused all 12 Local Blueprints, and paused 9 Cloud Blueprints before exposing the prior 120-second graph-node ceiling on Cloud OH-010. Both campaigns are diagnostic evidence only and must not be sealed as the final frozen campaign. Operators can prepare selected cases independently. Batch preparation now isolates terminal Blueprint failures and continues with sibling cases; production reporting pre-seeds those failed cases while still requiring explicit approval for every surviving Blueprint. The July 31 replacement campaign completed all 12 Baselines
without retry. After the operator-level failure-isolation repair was merged, Blueprint staging resumed and settled every agentic case with no open workflow or invocation: Local paused 11 of 12 at approval and retained OH-008 as a terminal integration failure after twice emitting the unknown literal location ID `null`; Cloud paused all 12 at approval; Hybrid paused 7 of 12 and retained terminal failures for OH-006, OH-008, and OH-010 at integration, OH-009 at the World specialist, and OH-012 at the Character specialist after bounded structured-output repair. No Blueprint has been approved on the operator's behalf. The current staging yield is therefore 30 of 36 agentic cases (83.3%), which cannot meet the accepted 95% technical-completion threshold unless failed cases are explicitly rerun successfully or superseded by a new frozen campaign.
An August 1 frozen replacement campaign changed only the Hybrid cloud model from Nemotron to `gemma4:31b-cloud` while retaining the same accepted graph and prompt-contract versions. Its Baseline completed 12 of 12 after one explicit retry recovered an OH-009 provider HTTP 500; Local paused 11 of 12 at approval and retained OH-006 as a terminal integration failure after invalid cross-specialist character references and missing scene-plan beats exhausted bounded repair; Cloud paused all 12; and Hybrid paused all 12, with one invalid Cloud integration response recovered by bounded repair. All 35 surviving Blueprints remain at the mandatory approval checkpoint and no campaign workflow or invocation remains active. The 35-of-36 Blueprint staging yield is 97.2%, above the accepted 95% technical-completion threshold; final technical completion remains contingent on approved production finishing those cases.
The approved handoff now materializes exact Scene Plan versions and an initial canonical Story Bible, creates a child production run, and invokes the real SQLite-checkpointed writer, critic, continuity, and bible-maintainer graph. Production nodes reserve durable graph/call/token/cost budgets, profile-routed structured calls persist exact input lineage, accepted scene deltas advance the Story Bible through the deterministic reducer, and successful task fingerprints replay without duplicate calls. A final deterministic assembly persists the complete benchmark story and returns its Blueprint, accepted-scene, final-bible, manuscript, invocation, usage, latency, cost, and hard-gate evidence as `BenchmarkOutput`. The mandatory Blueprint approval remains fail-closed, and production pauses before a call that would exceed its reserved budget. The resumable operator flow now stages all Local, Cloud, and Hybrid Blueprint cases, requires explicit per-case approval, then runs approved production into the same atomically checkpointed report. An offline operator command now packages every surviving paused Blueprint, frozen prompt, and exact automated critique into a deterministic JSON packet plus readable Markdown dossier and reviewer CSV. The completed form must affirm every surviving case and preserve its campaign, plan, packet, workflow, artifact-version, and content-digest fields; approval rejects incomplete or stale review evidence and records the reviewer, packet digest, and exact Blueprint lineage durably before resolving each interrupt without enabling model calls. Frozen Ollama deployment routing supports cloud models through a signed-in local daemon or a runtime-secret-backed direct cloud endpoint, including split local/cloud Hybrid execution. Reviewer-specific CSV forms and provenance-free Markdown guides now carry the canonical rubric, score anchors, and hard gates; strict import merges completed forms while rejecting incomplete, duplicate, foreign-campaign, or unknown-comparison evidence. Review schema v2 binds every submission to the exact public-packet digest, which reporting verifies against the separately stored private answer key. Complete evidence can now be sealed into a deterministic archive only when
every planned case has a terminal result, every blinded comparison has human review coverage, and the corpus, plan, report, packets, reviews, declared budget, and recomputed summary agree. Its manifest records fixed public/private paths, counts, and per-member SHA-256 digests; independent verification reproduces the canonical archive and rejects tampering or partial evidence. Remaining before completion: run the formal corpus across all three profiles and the single-model baseline within an authorized budget, collect the actual blind human reviews, and seal the resulting evidence. Evidence so far:
`benchmarks/v0.1/corpus.json`,
`engine/open_hollywood_engine/evaluations/`,
`engine/open_hollywood_engine/evaluations/evidence.py`,
`engine/open_hollywood_engine/evaluations/reviews.py`,
`apps/api/open_hollywood_api/services/agentic_benchmark.py`,
`apps/api/open_hollywood_api/services/blueprint_model_executor.py`,
`apps/api/open_hollywood_api/services/evaluation_campaign.py`,
`apps/api/open_hollywood_api/services/evaluation_execution.py`,
`apps/api/open_hollywood_api/services/production_model_executor.py`,
`apps/api/open_hollywood_api/services/production_workflow.py`,
`engine/open_hollywood_engine/models/routing.py`,
`scripts/evaluation_harness.py`, and `tests/evaluations/`.

The benchmark now treats its 2,500–5,000-word range as advisory creative
guidance rather than a proxy for completion or short-prose format. Every new
output records a validated non-gating adherence measurement, automatic
completion checks only whether the document is present and ends normally, and
human reviewers decide the short-prose format gate. Older resumable reports and
immutable story artifacts remain readable; advisory deviation alone cannot turn
a technically completed story into a failed case.

An August 19 Local v7 regression diagnostic reused the approved August 1
pre-production lineage and ran the first six-case Local batch. The five
runnable production cases fell from four prior v1 successes to one v7 success;
three regressions began when non-final continuity calls treated story-wide
requirements as current-scene blockers, and their re-checks then failed the
text-signature stagnation guard. The preserved diagnostic is not final
benchmark evidence. Scene-production prompt contract v8 now gives continuity a
deterministic applicability packet: non-final scenes receive opaque IDs but not
the text of requirements deferred until the ending, while the final scene
receives the exact frozen required elements and forbidden shortcuts as due-now
gates. Exact Scene Plan requirements remain immediate. Typed continuity
re-check disposition, repair assessment, and revised-draft evidence replace
lexical-difference inference, while Local remains fail-closed and the persisted
Hybrid-only stagnation escalation remains bounded. Regression coverage asserts
non-final/final constraint visibility, permits the same exact quotation when a
repair assessment says the passage was unchanged, and preserves Local, Cloud,
and Hybrid routing behavior. Evidence:
`docs/benchmark_reports/step-19-local-v7-regression-2026-08-19.md`,
`engine/open_hollywood_engine/artifacts/schemas.py`,
`engine/open_hollywood_engine/workflows/production_contracts.py`,
`apps/api/open_hollywood_api/services/production_model_executor.py`, and
`tests/evaluations/test_agentic_production.py`. The isolated v8 canary database
was copied byte-for-byte from the approved pre-production snapshot, migrated to
schema 0007, and frozen into a 48-case plan with canonical digest
`2e1a76a7fec7cec9b408e08c5e65632d0aabf62f7f93a4c1734734bb5298c788`.
Its first six-case Local batch completed two of five production-runnable cases;
OH-V01-006 retained its terminal Blueprint failure. The two successes passed all
automated hard gates at 3,579 and 3,621 words. Two failures exhausted continuity
structured-output repair after ordinary application diagnostics collapsed to
`$:ValueError`; a third recovered continuity but exhausted Story Bible repair on
unknown canonical fact and location IDs. Prompt contract v9 now persists a
redacted, bounded diagnostic envelope with exact output-field locations,
validation types, and messages without retaining provider response bodies. The
one bounded Local retry receives those focus locations plus operation-specific
continuity and Story Bible schema-repair rules. Cloud retries remain unchanged,
and an audited Hybrid continuity-stagnation retry drops Local guidance when it
escalates to Cloud. The v8 canary remains immutable diagnostic evidence; another
batch requires a new plan pinned to prompt v9. Evidence:
`docs/benchmark_reports/step-19-local-v8-canary-2026-08-20.md`.
The fresh v9 canary plan has canonical digest
`83ffb10a8a1ca02f115ac0e4077e7a514cd8362fed9894790cc353a8293521b1`.
Its first Local batch completed one of five production-runnable cases; OH-V01-004
produced 3,365 words within target and passed every automated hard gate, while
OH-V01-006 retained its terminal Blueprint failure. All four terminal Production
failures were initial continuity calls that populated fields intended only for
re-checks. Prompt contract v10 now derives an explicit `initial_check` or
`recheck` schema from immutable input lineage, removes all three re-check-only
fields and their enum definition from the initial schema, and withholds re-check
instructions until a prior Continuity Report is present. The same selected
schema is used in the prompt and Local provider grammar, and its variant is
persisted for replay diagnostics. Canonical artifacts, bounded repair, Cloud
routing, and Hybrid-only escalation are unchanged. The v9 canary remains
immutable diagnostic evidence; another batch requires a new plan pinned to
prompt v10. Evidence:
`docs/benchmark_reports/step-19-local-v9-canary-2026-08-20.md`.
The fresh v10 canary plan has canonical digest
`f985ae1b5976836952451a3011126c796e6e65773339f3b5b933bbfe5c24ee53`.
Its first Local batch completed one of five production-runnable cases;
OH-V01-004 produced 3,455 words within target and passed every automated hard
gate, while OH-V01-006 retained its terminal Blueprint failure. The v9
initial-check regression did not recur. OH-V01-002 and OH-V01-005 instead
exhausted repair after blocking findings omitted `recommended_resolution`;
OH-V01-001 and OH-V01-003 reached the revision limit after continuity re-checks
used non-exact evidence or copied stale assessments despite materially changed
drafts. Prompt contract v11 now uses severity-discriminated finding branches:
error/blocking branches require a non-empty resolution and the model cannot emit
the application-owned `blocks_approval` field, while advisory branches may omit
the resolution. Re-check blocker branches additionally require disposition,
assessment, and revised evidence together. Boundary validation proves every
revised-evidence item is an exact current-draft excerpt, rejects a copied prior
assessment when evidence changes, and requires an explicit explanation for
unchanged evidence. Exact story-wide benchmark requirements duplicated into a
non-final Scene Plan are deferred and removed from the continuity prompt view;
other Scene Plan requirements remain immediate. Canonical persisted artifacts,
bounded repair, Cloud routing, and Hybrid-only escalation are unchanged. The
v10 canary remains immutable diagnostic evidence; another batch requires a new
plan pinned to prompt v11. Evidence:
`docs/benchmark_reports/step-19-local-v10-canary-2026-08-23.md`.
The fresh v11 canary plan has canonical digest
`a71a83a87092f7d095b96918b5dc8503f90508e45d524c5220ab7ccdc6400489`.
Its first Local batch completed two of five production-runnable cases;
OH-V01-003 produced 4,061 words and OH-V01-004 produced 2,992 words, with both
passing every automated hard gate. OH-V01-006 retained its terminal Blueprint
failure. The v11 schema split and resolution guarantee held, but the remaining
Production failures exposed three contract/routing gaps: missing requirements
and absent forbidden shortcuts could fabricate draft evidence; world-rule
findings could ignore explicit companion-rule authorization; and critic-only
revisions could consume the revision allowance before continuity ran. Prompt
contract v12 separates the three blocking bases, validates exact evidence on
initial calls and re-checks, binds requirement and canonical rule IDs, and
prevents an explicitly authorized world condition from blocking. Production
graph v3 runs critic and continuity on every candidate and schedules at most one
revision after consolidating both results. Benchmark failures now surface the
redacted persisted Production cause. The v11 canary remains immutable evidence;
the next canary requires a new plan pinned to graph v3 and prompt v12. Evidence:
`docs/benchmark_reports/step-19-local-v11-canary-2026-08-24.md`.
Ruff and formatting pass over 133 files, strict mypy passes over 133 source
files, all 219 pytest tests pass, frontend formatting/lint/type checking pass,
all 10 Vitest tests pass, and the production build succeeds.

20. [ ] **Tune prompts and graph routing** based on blind human preference—not isolated attractive examples.

21. [ ] **Package the stable system with Tauri** and test crash/restart, offline, missing-model, invalid-key, provider-timeout, and low-disk-space behavior.

22. [ ] **Consider broader formats and hosted features only after the core is proven:** songs, poems, video scripts, collaboration, or hosted accounts.
