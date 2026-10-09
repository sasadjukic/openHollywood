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
aggregate run budgets and typed idempotent commands. SQLite now persists each command, pause reason, source checkpoint, and resulting run. Pause requests made during execution take effect before the next registered node; stop cancels the run and open invocations; resume continues from the durable checkpoint while keeping the Story Blueprint approval interrupt distinct. Story Blueprint retry-from-node prunes obsolete outputs, preserves compatible exact artifact versions, and creates an immutable linked child lineage. Failed production specialists can retry only their exact current node from the same durable checkpoint, preserving completed-scene artifacts and invocation history. Crash replay reuses the resulting run and checkpoint rather than duplicating completed work. Before every model-backed node, the runtime reserves model-call, input-token, output-token, and cost capacity and checks elapsed wall-clock time; exhaustion pauses with useful usage and limit events while preserving partial artifacts. FastAPI, the generated TypeScript SDK, and the workspace expose the same controls, current limits, and aggregate usage. Evidence:
`engine/open_hollywood_engine/workflows/run_controls.py`, `apps/api/open_hollywood_api/services/run_controls.py`, `apps/api/open_hollywood_api/routes/run_controls.py`, `migrations/versions/0005_workflow_run_controls.py`, generated contracts, workspace UI controls, and workflow/API/migration/React tests. Migration upgrade/downgrade and metadata parity, Ruff, mypy, 129 pytest tests, Prettier, ESLint, TypeScript, 5 Vitest tests, and the production build pass.

18. [x] **COMPLETED 2026-07-24 — Implement Fountain/Markdown renderers and
PDF/DOCX export.** A provider-neutral, invariant-checked manuscript contract
assembles only complete latest versions of approved Scene Draft artifacts in
unique, contiguous three-to-eight-scene order. The canonical Markdown renderer normalizes line endings and escapes structural markup. A separate typed Fountain screenplay contract renders title pages, forced headings and action, dialogue structures, transitions, sections, synopses, centered text, and page breaks without guessing script structure from prose. Searchable US-Letter PDF and editable US-Letter DOCX exporters use fixed metadata and canonicalized containers so identical inputs produce identical bytes. FastAPI exposes an export manifest, exact immutable source-version lineage, SHA-256 ETags, sanitized downloads, and fail-closed `409` behavior; the generated TypeScript SDK and workspace enable Markdown, PDF, and DOCX controls only for exportable projects. Evidence: `engine/open_hollywood_engine/rendering/`, `apps/api/open_hollywood_api/services/exports.py`, `apps/api/open_hollywood_api/routes/exports.py`, generated contracts, workspace export controls, and rendering/API/React tests. All four representative PDF pages and all four representative DOCX pages passed visual inspection. Ruff, mypy, 140 pytest tests, Prettier, ESLint, TypeScript, 5 Vitest tests, and the production build pass.

19. [~] **IN PROGRESS 2026-07-26 — Build the evaluation harness** and execute phased benchmark evaluation (Cloud-first scope adopted 2026-09-11 below; Local/Hybrid qualification deferred). The provider-neutral harness core now strictly validates the frozen 12-prompt v0.1 corpus and pins its canonical digest, exact graph and prompt-contract versions, direct-model baseline, complete secret-free Local/Cloud/Hybrid profile snapshots, and prompt seeds into a deterministic 48-case campaign plan. Sequential case execution is failure-isolated and resumable from terminal results; successful outputs must carry exact workflow-run, model-invocation, and immutable artifact-version lineage. The accepted weighted rubric and hard gates are executable contracts. Deterministic A/B packaging separates provenance-free reviewer documents from the private answer key, and reporting maps blind human preferences back to systems while calculating the accepted completion, continuity, quality, preference, and cost thresholds. The operator command validates corpus integrity and creates plans from fully configured persisted presets. The application layer now executes the direct single-model baseline through a bounded provider-neutral call and persists its frozen prompt, invocation, workflow, and immutable story lineage idempotently. Campaign reports checkpoint atomically after each case, failed cases retry only when explicitly requested, and operator-configurable Ollama timeouts support long-form calls while distinguishing provider timeouts from outages. Retrying after an interrupted process closes stale running baseline attempts and preserves their immutable input lineage. Ollama Cloud response aliases are accepted only when they normalize to the frozen requested model; requested and provider-reported identifiers are both persisted. Operator commands create separated public/private review packets and summaries from schema-validated evidence. Failed structured calls retain provider usage, finish reason, response hash, and length, while a lone JSON fence is normalized without accepting surrounding
commentary. Agentic cases now enter the real durable Story Blueprint graph:
every registered specialist resolves its exact frozen profile selection,
receives deterministic immutable inputs and benchmark constraints, uses schema enforcement when the deployment supports it, records a budgeted invocation plus output lineage, validates cross-artifact invariants, and pauses at the mandatory human approval interrupt. Replaying a paused case performs no duplicate model calls. Creative Brief prompt contract v6 requests only creative choices and the application deterministically attaches the frozen premise, format, genres, maturity, required elements, and forbidden elements; this keeps optional model fields from weakening benchmark intent. Prompted non-schema invariants preserve exact benchmark constraints; parallel World specialists cannot invent unresolved character references; the integrator emits only new beats and scene plans, and the application deterministically assembles immutable specialist artifacts into the Story Blueprint. Prompt contract v9 binds integration to a compact world summary, the Creative Brief's exact scene count, and no more than two beats per scene. Prompt-only cloud structured-output retries
persist their attempt number and receive safe validation locations plus provider finish metadata without storing or echoing the failed story response. Word bounds remain application-validated instead of emitting grammar keywords unsupported by local Ollama structured output. Model-executing operator commands now reject a campaign plan when its baseline, Blueprint, production prompt, or graph versions differ from the running build, including the direct-story graph and nested dialogue subgraph. Blueprint graph v4, scene-production graph v2, and dialogue
subgraph v2 give model-backed nodes a 900-second formal long-form ceiling while retaining bounded execution; cancelled or timed-out calls now close their persisted invocation instead of remaining `RUNNING`. A 12-case Local
qualification reached the mandatory approval interrupt while prompt contracts v6 through v9 were being hardened. A subsequent frozen v9 staging campaign completed all 12 Baselines after one explicit provider-timeout retry, paused all 12 Local Blueprints, and paused 9 Cloud Blueprints before exposing the prior 120-second graph-node ceiling on Cloud OH-010. Both campaigns are diagnostic evidence only and must not be sealed as the final frozen campaign. Operators can prepare selected cases independently. Batch preparation now isolates terminal Blueprint failures and continues with sibling cases; production reporting pre-seeds those failed cases while still requiring explicit approval for every surviving Blueprint. The July 31 replacement campaign completed all 12 Baselines
without retry. After the operator-level failure-isolation repair was merged, Blueprint staging resumed and settled every agentic case with no open workflow or invocation: Local paused 11 of 12 at approval and retained OH-008 as a terminal integration failure after twice emitting the unknown literal location ID `null`; Cloud paused all 12 at approval; Hybrid paused 7 of 12 and retained terminal failures for OH-006, OH-008, and OH-010 at integration, OH-009 at the World specialist, and OH-012 at the Character specialist after bounded structured-output repair. No Blueprint has been approved on the operator's behalf. The current staging yield is therefore 30 of 36 agentic cases (83.3%), which cannot meet the accepted 95% technical-completion threshold unless failed cases are explicitly rerun successfully or superseded by a new frozen campaign.
An August 1 frozen replacement campaign changed only the Hybrid cloud model from Nemotron to `gemma4:31b-cloud` while retaining the same accepted graph and prompt-contract versions. Its Baseline completed 12 of 12 after one explicit retry recovered an OH-009 provider HTTP 500; Local paused 11 of 12 at approval and retained OH-006 as a terminal integration failure after invalid cross-specialist character references and missing scene-plan beats exhausted bounded repair; Cloud paused all 12; and Hybrid paused all 12, with one invalid Cloud integration response recovered by bounded repair. All 35 surviving Blueprints remain at the mandatory approval checkpoint and no campaign workflow or invocation remains active. The 35-of-36 Blueprint staging yield is 97.2%, above the accepted 95% technical-completion threshold; final technical completion remains contingent on approved production finishing those cases.
The approved handoff now materializes exact Scene Plan versions and an initial canonical Story Bible, creates a child production run, and invokes the real SQLite-checkpointed writer, critic, continuity, and bible-maintainer graph. Production nodes reserve durable graph/call/token/cost budgets, profile-routed structured calls persist exact input lineage, accepted scene deltas advance the Story Bible through the deterministic reducer, and successful task fingerprints replay without duplicate calls. A final deterministic assembly persists the complete benchmark story and returns its Blueprint, accepted-scene, final-bible, manuscript, invocation, usage, latency, cost, and hard-gate evidence as `BenchmarkOutput`. The mandatory Blueprint approval remains fail-closed, and production pauses before a call that would exceed its reserved budget. The resumable operator flow now stages all Local, Cloud, and Hybrid Blueprint cases, requires explicit per-case approval, then runs approved production into the same atomically checkpointed report. An offline operator command now packages every surviving paused Blueprint, frozen prompt, and exact automated critique into a deterministic JSON packet plus readable Markdown dossier and reviewer CSV. The completed form must affirm every surviving case and preserve its campaign, plan, packet, workflow, artifact-version, and content-digest fields; approval rejects incomplete or stale review evidence and records the reviewer, packet digest, and exact Blueprint lineage durably before resolving each interrupt without enabling model calls. Frozen Ollama deployment routing supports cloud models through a signed-in local daemon or a runtime-secret-backed direct cloud endpoint, including split local/cloud Hybrid execution. Reviewer-specific CSV forms and provenance-free Markdown guides now carry the canonical rubric, score anchors, and hard gates; strict import merges completed forms while rejecting incomplete, duplicate, foreign-campaign, or unknown-comparison evidence. Review schema v2 binds every submission to the exact public-packet digest, which reporting verifies against the separately stored private answer key. Complete evidence can now be sealed into a deterministic archive only when
every planned case has a terminal result, every blinded comparison has human review coverage, and the corpus, plan, report, packets, reviews, declared budget, and recomputed summary agree. Its manifest records fixed public/private paths, counts, and per-member SHA-256 digests; independent verification reproduces the canonical archive and rejects tampering or partial evidence.

**Current status — 2026-10-04:** the September formal Cloud-versus-baseline campaign has
completed generation and all eleven eligible human comparisons; its reviewed
evidence is sealed and verified. All 22 September manual story reviews are also
complete and stored in the repository. **Item 5 is COMPLETE as a repeatability
assessment and evidence-sealing task.** All three prospective campaigns and all
34 eligible human comparisons are reviewed, sealed and independently verified,
with a consolidated evidence register. Cloud completion was 12/12, 12/12 and
10/12; all 36 baselines completed. Weighted Cloud scores were 4.05, 4.1167 and
4.16, while preference was 54.17%, 37.5% and 45%, below the unchanged 60% threshold
in every repeat. Repeat 3 failed technical acceptance on OH-V01-002 and OH-V01-010.
Its reviewed ten-pair score is 4.16 Cloud versus 4.15 baseline. The October 2
reviewer calibration and authorized Ollama 0.35.1 exception in repeat 3 remain
explicit; the original 0.35.0 freeze and historical seals are preserved.
Step 19 remains **IN PROGRESS** for inconsistent technical acceptance, unmet
preference and unknown monetary cost. Repeated acceptance has not been demonstrated.
The reviewer's character-depth, recurring-prose and group-dynamics concerns are
recorded as qualitative evidence without changing scores, criteria or the endpoint.
Local/Hybrid qualification remains deferred under the adopted Cloud-first scope.
The two Repeat 3 continuity response-contract failures have a v34 implementation
with offline regression evidence and two first-attempt-valid Cloud probes,
documented in the October 4 entry below. Both probes retained a blocker; semantic
judgment and full-story recovery remain unqualified. Sealed v33 results are unchanged.
The dated entries below retain their original checkpoint context; the
[September 30 completion entry](#human-reviews-recorded-and-formal-evidence-sealed--2026-09-30)
supersedes earlier pending-review status for these manual and formal outputs.

Evidence so far:
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
The fresh v12 canary plan has canonical digest
`b6e25db3c372676bb2973db6305aa360ddc06ee8c4c95189f273f570842be396`.
Its first Local batch completed none of five production-runnable cases;
OH-V01-006 retained its terminal Blueprint artifact-contract failure. All five
Production failures stopped at continuity. Persisted invocation diagnostics
showed ten exact-evidence failures, three canonical-source-reference failures,
and two length-truncated JSON responses across 24 continuity attempts. Prompt
contract v13 retains production graph v3 while replacing free-form evidence
copying with deterministic candidate-draft evidence handles and replacing broad
raw-ID provenance with bounded canonical claims carrying exact immutable source
paths. The call-specific Local schema constrains evidence, canonical source,
due requirement, and World Rule selections to exact enums; advisory findings
cannot emit evidence, prior accepted drafts are explicitly context-only, and
application-owned report lineage is absent from model output. The application
resolves evidence handles into exact canonical artifact excerpts before existing
artifact and routing validation. The v12 canary remains immutable diagnostic
evidence; another batch requires a new plan pinned to graph v3 and prompt v13.
Evidence: `docs/benchmark_reports/step-19-local-v12-canary-2026-08-25.md`.
The fresh v13 canary plan has canonical digest
`323c3a91850be72a4c09ef6911e39ccb59c0f27abfc3abf1441270a164c01a98`.
Its first Local batch completed none of five production-runnable cases;
OH-V01-006 retained its terminal Blueprint artifact-contract failure. Prompt
v13 eliminated the v12 exact-evidence, canonical-source, requirement-ID, and
truncated-JSON failures. The 13 remaining failed continuity calls instead
exposed overlap in each blocking branch: six omitted a companion-rule
assessment, three omitted or invented World Rule IDs, two misrepresented
explicit authorization, one attached world-only fields to a non-world finding,
and one re-check repeated a stale blocker. Prompt contract v14 retains
production graph v3 and splits contradiction, missing-requirement, and
forbidden-shortcut blockers into explicit world-rule and non-world branches for
both initial checks and re-checks. World branches require enum-constrained rule
IDs, a non-empty companion-rule assessment, and
`condition_explicitly_authorized=false`; non-world branches omit all three
world-analysis fields. Benchmark failure reporting now reads the terminal
failed invocation's exact redacted diagnostic before falling back to the
workflow error, so `report.json` records the actionable field-level cause. The
v13 canary remains immutable diagnostic evidence; another batch requires a new
plan pinned to graph v3 and prompt v14. Evidence:
`docs/benchmark_reports/step-19-local-v13-canary-2026-08-25.md`.
The fresh v14 canary plan has canonical digest
`61a3c33ae850c1bb9b7f030b896d362ceb8d2411770acc3354cde0357461b2ac`.
Its first Local batch completed none of five production-runnable cases, while
OH-V01-006 retained its terminal Blueprint artifact-contract failure. Prompt
v14 eliminated all v13 missing/invalid World Rule ID, missing companion-rule
assessment, invalid authorization-state, and non-world/world-field crossover
failures. OH-V01-001 stopped after repeated continuity re-check stagnation;
OH-V01-002 recovered one such structured failure but ultimately retained a
blocker at the revision limit. OH-V01-003, OH-V01-004, and OH-V01-005 accepted
two, one, and one scenes respectively before later continuity inputs exceeded
the unchanged 20,000-token per-call ceiling. A representative v14 initial
schema is 70.2% larger than v13 and the corresponding re-check schema is 70.6%
larger, so compacting the cross-product contract is the leading response rather
than immediately widening the budget. Exact report diagnostics worked for
terminal failed invocations, but OH-V01-002 exposed a precedence defect: its
recovered failed invocation masked the later specific workflow terminal cause.
The database passed integrity checking and retained no running workflow or
invocation. Evidence:
`docs/benchmark_reports/step-19-local-v14-canary-2026-08-26.md`.
Prompt contract v15 retains graph v3 and implements the v14 evidence response.
It composes one shared blocking-finding object with independent nested
basis/category detail unions instead of six duplicated full objects. The
representative initial schema falls from 14,270 to 5,792 UTF-8 bytes (59.4%)
and the re-check schema from 15,733 to 6,543 bytes (58.4%), with no `allOf`
dependency because the Local model did not reliably enforce that keyword.
Local user messages no longer duplicate the schema already sent through
Ollama's enforced format channel; Cloud and Hybrid cloud calls retain the
inline schema contract. Invocation telemetry now separates content-free size,
digest, and estimated-token contributions for system instructions, artifacts,
control data, retry/repair context, inline schema, and gateway schema, and
persists provider usage on over-budget failures with exact observed-versus-limit
diagnostics. Re-check evidence carries an explicit changed/unchanged/newly
exposed state that is checked against prior exact evidence and stripped before
canonical artifact persistence. Finally, report cause selection gives a
specific terminal workflow error precedence over a recovered failed
invocation, using invocation detail only for absent or generic workflow
wrappers. A new canary must use a fresh plan pinned to graph v3 and prompt v15.
Ruff and formatting pass over 133 files, strict mypy passes over 133 source
files, all 224 pytest tests pass, frontend formatting/lint/type checking pass,
all 10 Vitest tests pass, and the production build succeeds.
The first Local v15 canary then completed no cases: OH-V01-006 retained its
Blueprint failure, while all five production-runnable cases stopped at
continuity after accepting four scenes in total. The compact schema and explicit
world-rule branches held, but eight continuity invocations were rejected by the
model-authored re-check-state contract, OH-V01-002 retained a blocker at the
revision limit, and OH-V01-004 used 20,163 input tokens against the unchanged
20,000-token ceiling. Four invalid model-authored critic overall scores recovered
on retry. Evidence:
`docs/benchmark_reports/step-19-local-v15-canary-2026-08-28.md`.
Prompt contract v16 retains graph v3 and separates all due Scene Plan obligations
into an exhaustive application-validated coverage audit with stable IDs. Missing
requirements no longer share the contradiction union; the application derives
their canonical identity, category, lineage, and routing state, while
contradictions require an affirmative current-draft conflict with bounded canon.
Re-check evidence change is application-owned, unchanged exact blockers remain
valid graph feedback, and changed evidence paired with copied assessment yields
a granular safe reason code. Canonical source claims are grouped, continuity sees
at most the immediately prior accepted scene ending, and critic overall score is
the deterministic arithmetic mean of bounded rubric scores. The per-call input
ceiling remains 20,000 tokens so the next fresh canary isolates these prompt and
context changes.
Ruff and formatting pass over 133 files, strict mypy passes over 133 source
files, all 226 pytest tests pass, frontend formatting/lint/type checking pass,
all 10 Vitest tests pass, and the production build succeeds. No v16 canary was
started as part of this implementation change.
The first Local v16 canary then completed no cases, while OH-V01-006 retained its
Blueprint failure. The five production-runnable cases nevertheless reached
their final scenes and accepted 18 scenes, with 91 of 103 production calls and
21 of 33 continuity calls succeeding. No critic or input-budget failure
occurred, and the largest continuity input was 12,558 tokens. Terminal causes
were limited to incomplete model-authored coverage partitions, invalid
model-authored re-check dispositions, one application validator that rejected a
valid missing Scene Plan scalar obligation, and one changed-evidence assessment
heuristic. Evidence:
`docs/benchmark_reports/step-19-local-v16-canary-2026-08-29.md`.
Prompt contract v17 retains graph v3 and the 20,000-token ceiling. The
application now supplies one deduplicated due requirement catalog plus a
separate forbidden-shortcut catalog. Every due required ID is a schema-required
property of `requirement_coverage`, eliminating structurally valid omissions;
missing entries materialize canonical findings for benchmark and Scene Plan IDs
alike. Contradiction categories are nested in their basis and exclude
`constraint`, while forbidden category is application-owned. Re-check blockers
may reference an exact prior ID, but canonical identity and disposition are
derived by the application. Copied assessment after changed evidence is
non-terminal content-free advisory telemetry while exact draft evidence remains
mandatory. Regression coverage exercises the five v16 terminal patterns. Ruff
and formatting pass over 133 files, strict mypy passes over 133 source files,
all 230 pytest tests pass, frontend formatting/lint/type checking pass, all 10
Vitest tests pass, and the production build succeeds. No v17 canary was started
as part of this implementation change.
The first Local v17 canary subsequently completed OH-V01-002 and OH-V01-004,
the first recent Local production completions. Across the five runnable cases,
81 of 87 production calls and 22 of 26 continuity calls succeeded; every v16
coverage-partition failure disappeared. OH-V01-001 exposed a deterministic
collision between application-generated positional new-finding IDs across
consecutive re-checks. OH-V01-003 and OH-V01-005 reached the revision limit
after critic-passing revisions were blocked by continuity: one promoted pacing
and an intended anomaly to World Rule violations, while the other treated a
character goal as a guaranteed outcome despite an explicitly unresolved Scene
Plan exit state. OH-V01-006 retained its Blueprint failure. Evidence:
`docs/benchmark_reports/step-19-local-v17-canary-2026-08-30.md`.
Prompt contract v18 retains production graph v3 and the bounded revision policy.
Re-check output now contains an exhaustive object keyed by every exact prior
non-requirement blocker plus a separate new-finding array; the application
derives prior disposition and revision-scoped new IDs, eliminating positional
collisions and duplicate prior references. Requirement catalog policy v2 adds
per-entry satisfaction modes and companion IDs, distinguishing meaningful goal
pursuit from outcome achievement. World Rule blockers require exact rule-source
provenance, an explicit prohibition/required-condition violation kind, and a
direct logical-conflict assessment; pacing and dramatic framing are routed away
from continuity. Exact duplicate missing-requirement summaries or repairs cannot
also block as contradictions. Regression coverage reproduces all three v17
production terminal mechanisms. Ruff and formatting pass over 133 files, strict
mypy passes over 133 source files, all 236 pytest tests pass, frontend formatting,
lint, and type checking pass, all 10 Vitest tests pass, and the production build
succeeds. No v18 canary was started as part of this implementation change.
The first Local v18 canary subsequently completed OH-V01-002, OH-V01-003, and
OH-V01-004, raising production-runnable completion from two of five to three of
five and accepted scenes from 13 to 18. It produced no revision-limit failure,
and OH-V01-003 specifically validated the v18 semantic direction by completing
after v17 had promoted intended pacing and World Rule behavior to blockers.
Continuity structured-output success fell from 22 of 26 calls to 18 of 25,
however. A text-overlap exclusivity validator fired six times across four cases;
OH-V01-001 and OH-V01-005 terminated after Local repair, and OH-V01-005 first
reported a separate World Rule ID/source mismatch. Its earlier attempt remained
visible in SQLite but not in the final report. Evidence:
`docs/benchmark_reports/step-19-local-v18-canary-2026-08-31.md`.
Prompt contract v19 retains production graph v3. World Rule source provenance is
now derived deterministically from model-selected canonical rule IDs. Exact
duplicate missing summary-and-repair pairs consolidate into the keyed missing
blocker, while one shared text field alone cannot invalidate an independently
evidenced contradiction. Local repair policy v2 provides issue-specific actions
and exact required key sets without retaining failed response content. Failed
benchmark cases now serialize every safe persisted invocation failure in ordered
`failure_history`, preserving earlier attempts alongside the concise terminal
cause. Regression coverage reproduces the v18 terminal mechanisms and verifies
the derived provenance, deterministic consolidation, compact Local grammar,
focused repair packet, and resumable report serialization. No v19 canary was
started as part of this implementation change. Ruff and formatting pass over
133 files, strict mypy passes over 133 source files, all 238 pytest tests pass,
frontend formatting, lint, and type checking pass, all 10 Vitest tests pass,
and the production build succeeds.
The first Local v19 canary subsequently completed OH-V01-002 and OH-V01-003,
for two of five production-runnable cases and 15 accepted scenes. This was a
completion regression from v18, although production-call reliability improved
to 95 of 98 and continuity-call reliability improved to 26 of 29. OH-V01-001
and OH-V01-004 reached the revision limit despite exact time-of-day evidence;
their contradiction sources could resolve to unrelated timeline or Scene Plan
title material. OH-V01-005 also showed that generic coverage statuses allowed a
`pursue` goal to be evaluated as if achievement were required. The v19 ordered
failure history correctly preserved failed-attempt diagnostics. Evidence:
`docs/benchmark_reports/step-19-local-v19-canary-2026-09-01.md`.
Prompt contract v20 retains production graph v3 and the existing revision
limit. Non-world contradictions now select typed canonical claims whose source,
category, entity/scene lineage, and optional requirement lineage are validated
and materialized by the application; Scene Plan titles are not selectable
claims. Requirement coverage uses satisfaction-mode-specific positive/negative
statuses and exact positive draft evidence, with application-owned severity.
Entry-state and time-context omissions are advisory unless an independent
affirmative contradiction exists. Exact requirement lineage deterministically
consolidates missing/contradiction duplicates regardless of paraphrase. Compact
rechecks carry only resolution state, assessment, and current evidence while
the application rehydrates persisted finding details. Local repair policy v3
provides typed claim/category/lineage guidance. Regressions reproduce the v19
time evidence, pursue semantics, irrelevant-title provenance, and revision
grammar failures. Ruff and formatting pass over 125 files, strict mypy passes
over 125 source files, all 246 pytest tests pass, frontend formatting, lint, and
type checking pass, all 10 Vitest tests pass, and the production build succeeds.
No v20 canary was started as part of this implementation change.
The first Local v20 canary subsequently completed none of the five
production-runnable cases and accepted only two scenes, regressing from v19's
two completions and v18's three. Production-call reliability fell to 48 of 53
and continuity-call reliability to 14 of 19. The v20 initial and recheck schema
sizes roughly doubled relative to v19, Scene Plan requirements could be
represented both as keyed coverage and selectable contradiction claims, and
model-authored deterministic metadata produced category and lineage failures.
Evidence: `docs/benchmark_reports/step-19-local-v20-canary-2026-09-02.md`.
Prompt contract v21 retains production graph v3 and the bounded revision policy.
Scene Plan obligations are now exclusive to an exhaustive keyed
`met`/`partial`/`absent` coverage partition; exact draft evidence supports met
and partial results, while absence records a negative search outcome without a
fabricated excerpt. Partial and qualitative Scene Plan coverage is advisory,
and only absent application-owned hard requirements block. Non-World-Rule
contradictions select one compact semantic claim and World Rule findings use a
separate compact rule catalog. The application derives category, provenance,
lineage, and stable semantic finding IDs, then consolidates semantically
repeated recheck findings regardless of wording. Local repair policy v4 sends
only path-specific allowed keys or enums and a focused action. Regression
coverage exercises exclusive requirement routing, application-owned metadata,
shared coverage statuses, partial evidence, qualitative advisory policy,
semantic duplicate suppression, and compact Local repair. No v21 canary was
started as part of this implementation change. Ruff and formatting pass over
133 files, strict mypy passes over 85 source files, all 252 pytest tests pass,
frontend formatting, lint, and type checking pass, all 10 Vitest tests pass,
and the production build succeeds.
The mixed v21 canary plan, digest
`0a85c406fe24a19683f30b644826b5bfe5df7fd4670ede5d6bd366bc62cfe5e3`,
then completed two of five Local production-runnable cases and one of four
Cloud cases. Local OH-V01-003 reached all 40 reserved calls and paused before
its Story Bible update; Local OH-V01-001 and OH-V01-002 retained different
continuity blockers at the revision limit. Cloud OH-V01-002 and OH-V01-003
failed exact requirement-coverage evidence selection after bounded repair, and
Cloud OH-V01-004 reported 21,161 provider input tokens against the 20,000-token
allowance. The known Local OH-V01-006 Blueprint failure remained outside
production. Manual Cloud runs then exposed two product-runtime defects: a
failed production node had no same-node retry control, and regenerating an
approved Blueprint with stable Scene Plan IDs but changed content collided with
the project-level deterministic version-one handoff artifact. Because the
handoff failed before a child production row existed, the worker repeatedly
selected the same approved Blueprint and starved a later approved story.
Prompt contract v21 and production graph v3 remain pinned while the runtime is
hardened. The aggregate budget now derives ten calls per scene from
`3 * (1 + maximum_revision_cycles) + 1`; Cloud-capable profiles receive a
bounded 24,000-token per-call input allowance. The inline continuity grammar
shares one draft-evidence enum, exact excerpt values normalize only when they
map unambiguously to a catalog handle, and invalid values appear in bounded,
secret-redacted field diagnostics. Deterministic handoff artifacts append
Blueprint-lineage versions, handoff errors persist a failed production child,
and the UI distinguishes Blueprint from Production while allowing failed
production to retry only its exact durable node. Regression coverage exercises
the regenerated-Blueprint collision, idempotent version replay, terminal
handoff state and worker de-duplication, production checkpoint retry, corrected
call budget, compact evidence references, exact-excerpt normalization, bounded
invalid-value diagnostics, and the React retry control. Evidence:
`docs/benchmark_reports/step-19-local-cloud-v21-canary-2026-09-03.md`,
`apps/api/open_hollywood_api/services/production_workflow.py`,
`apps/api/open_hollywood_api/services/production_model_executor.py`,
`apps/worker/open_hollywood_worker/runtime.py`, and
`tests/api/test_production_workflow_hardening.py`. Ruff and Python formatting
pass, strict mypy passes over 134 source files, all 257 pytest tests pass,
frontend formatting, lint, and type checking pass, all 11 Vitest tests pass,
and the production build succeeds.
Five subsequent manual Cloud stories on prompt v21 and production graph v3
confirmed that all terminal failures shared continuity evidence-handle
validation rather than writer or critic failure. The catalog emitted
four-digit handles such as `draft_evidence_0021`, while Gemma repeatedly
shortened them to forms such as `draft_evidence_021`; exact-node retry correctly
resumed the durable checkpoint but repeated the deterministic mismatch. The
runtime now zero-pads one-to-four-digit numeric aliases only when the resulting
canonical handle exists in the current catalog, retaining exact validation for
unknown values. Workspace read models expose the latest safe specialist
diagnostic, and project summaries include workflow phase and node. The React
client derives the selected sidebar entry from its polled workspace, polls
active project summaries, and labels statuses as Blueprint or Production so a
terminal center state cannot remain paired with a stale sidebar state. Prompt
v21 and graph v3 remain pinned. All 262 pytest tests pass, Ruff lint and format
checks pass across 134 files, strict mypy passes across 134 source files, all 11
Vitest tests pass, frontend formatting, lint, and type checking pass, and the
production build succeeds. No canary was started as part of this runtime and UI
hardening change.
Manual exact-node retry then completed all four previously failed Cloud stories,
validating the evidence-handle and durable-retry fixes against those persisted
checkpoints. Two fresh Local stories, `The Chronophage` and `The Unblinking
Bloom`, still reached the revision limit after structurally valid calls because
continuity promoted qualitative causal/dramatization feedback into canonical
contradictions and could treat planned or open-ended Blueprint material as
established canon. Prompt contract v22 retains production graph v3 and the
bounded revision policy while narrowing contradiction authority to stable
canonical claims. New non-world blockers require an exact draft assertion, a
category-specific conflict kind, the conflicting attribute, a direct logical
conflict assessment, and a corrective rather than additive repair action.
Qualitative/additive contradiction attempts are deterministically advisory;
keyed requirement coverage owns duplicate obligation feedback, including
partial coverage; and newly exposed re-check blockers must cite evidence added
or changed by the revision. The exact preceding draft is attached to persisted
invocation lineage for that application-side check without enlarging the model
prompt. Regression coverage reproduces both Local failure shapes and preserves
real direct-conflict blocking. Ruff lint and formatting pass across 134 files,
strict mypy passes across 134 source files, all 268 pytest tests pass, frontend
formatting, lint, and type checking pass, all 11 Vitest tests pass, and the
production build succeeds. No canary was started as part of this prompt-v22
hardening change. Evidence:
`docs/benchmark_reports/step-19-local-cloud-v21-canary-2026-09-03.md` and
`docs/benchmark_reports/manual-v21-story-diagnostics-2026-09-03.md`.

The prompt-v22 canary then completed zero of five production-runnable Local
cases and three of four Cloud cases. All six production-terminal failures were
initial continuity application-validation failures in the redundant non-world
direct-conflict certificate: five `conflict_kind` mismatches, four lexical
`logical_conflict_assessment` failures, and three exact-copy `draft_assertion`
failures across twelve attempts. No retry recovered a case. Compact continuity
inputs and schemas stayed substantially below the corrected Cloud allowance,
and genuine World Rule repairs still converged, so prompt v23 retains graph v3
while removing the failure-prone duplication. The model now selects one typed
canonical claim, exact draft evidence handles, a direct-conflict disposition,
and a corrective action; the application derives category, conflict kind,
provenance, lineage, and exact assertion. Optional explanation text is not
lexically gated. Focused schema repair is provider-neutral and includes safe
expected/received values. Writers and critics receive an application-derived
story-wide advisory length packet, and word-count-only critic findings cannot
become revision gates unless an explicit hard scene constraint exists.
Regression coverage preserves real World Rule and structural-critique
blocking. The prompt-v23 acceptance criteria and subsequent results are
recorded below. Evidence:
`docs/benchmark_reports/step-19-local-cloud-v22-canary-2026-09-04.md`.

The prompt-v23 canary completed six of nine production-runnable cases, versus
three of nine for v22. It removed every v22 redundant-certificate terminal
failure, raised structurally valid continuity attempts to 49/51 (26/26 Local),
and kept all six completed stories within the advisory word range. Local
OH-V01-001 still exhausted revisions through semantic repair ping-pong; Local
OH-V01-003 replaced an accepted scene assignment with future-scene material
after a near-total rewrite while its critic returned PASS. Local OH-V01-002's
pause coincided with Windows correcting a two-hour dual-boot host-clock error
and is recorded as environmental rather than an application defect. Production
graph v4 and prompt v24 now scope Blueprint prompt context to the current scene,
promote explicit viewpoint and scene-assignment drift to blocking critique,
enforce a 0.35 prior-draft similarity floor for continuity-only repair, retain
bounded cumulative per-scene continuity history, preserve stable IDs for
semantic recurrences, narrow Blueprint contradiction claims, and persist
cause-oriented revision-limit diagnostics. Blind human review remains required
for semantic requirements, target format, quality, and preference. Ruff
lint/format and strict mypy pass across 134 Python files, all 276 pytest tests
pass, all 11 frontend tests pass, frontend formatting/lint/type checking pass,
and the production build succeeds. These checks refer to the v24 implementation;
the completed canary is recorded below. Evidence:
`docs/benchmark_reports/step-19-local-cloud-v23-canary-2026-09-04.md`.

The completed v24 canary produced four of nine runnable stories: Cloud remained
four of four, but Local fell from two of five to zero of five. The known Local
OH-V01-006 Blueprint failure stayed outside the production denominator. Scoped
context reduced Cloud production input by 17.7%, all Cloud structured attempts
succeeded, and Local persisted revisions avoided the v24 0.35 similarity floor.
Two benign critic notes were falsely promoted by topic keywords. Local
continuity retained unsupported concerns and changed allegations under stable
IDs, while OH-V01-003 cleared scene checks but failed the resolved-thread Bible
invariant twice. The operator-confirmed v23 dual-boot clock correction remains
environmental and does not require runtime clock changes.

Production graph v5 and prompt v25 now use explicit assignment findings with
exact draft evidence, shared critic/continuity requirement timing, smaller
canonical assertions with scope, and recheck outcomes that can invalidate an
unsupported allegation or retain only advisory feedback. Recurrence identity
includes the original normalized allegation as well as its source; this is
conservative identity matching, not semantic equivalence detection. Resolved
Bible threads require an actual explanation and receive application-owned
resolution-scene lineage with precise bounded retry diagnostics. Advisory
Blueprint name observations preserve immutable approved content, and hard
critic blockers now fail at the revision cap even when continuity clears.
Scoped context, repair ledgers, and bounded revision restraint remain in place.
The checks improve structural and provenance guarantees; model interpretation
still requires canary evidence and blind human evaluation. Combined verification
passes: Ruff lint/format and strict mypy across 141 Python files, all 341 pytest
tests, frontend formatting/lint/type checks, all 11 Vitest tests, and the
production build. These checks refer to the v25 implementation; its completed
canary and the next implementation are recorded below. Step 19 remains
**IN PROGRESS** because the formal campaign and human review are not complete.
Evidence: `docs/benchmark_reports/step-19-local-cloud-v24-canary-2026-09-05.md`.

The completed v25 canary matched v23's six of nine runnable completions and
advanced accepted scenes to 38/44 (v23: 32/44; v24: 24/44). Local OH-V01-001
became a new success, OH-V01-004 recovered, and all four Cloud cases completed.
Local OH-V01-002 and OH-V01-003 reached later scenes but failed historical
resolved-thread delta validation; OH-V01-005 retained an unsupported continuity
blocker. Local OH-V01-006 remains the exact inherited Blueprint failure, not a
production failure. The operator-confirmed host clock issue is environmental.
v23 and v25 are pinned comparison baselines until stronger evidence replaces them.

Production graph v6 / prompt v26 implement the six follow-up changes: immutable
resolved-thread history with no-op delta omission; a registered, budgeted terminal
continuity adjudication node; an evidence/source guard against immediately
reintroducing released findings under new wording; regression and positive-control
tests including a separate hard viewpoint audit; failure-layer and selected-claim
diagnostics; and matched technical comparison / blind human review tooling.
The existing revision cap, World Rule and requirement gates, approval checkpoint,
profile routing, and secret guards remain intact. No v26 canary or human review
has been run. Live semantic performance and repeatability are pending; Step 19
stays **IN PROGRESS**, and Step 20 has not been started. Evidence and verification:
`docs/benchmark_reports/step-19-local-cloud-v25-canary-2026-09-07.md`.

The completed v26 canary reached 3/9 runnable completions, 0/5 Local and 3/4
Cloud, with 16/44 accepted scenes. All five Local initial drafts exactly matched
v25, isolating the main regression to downstream review. Five terminal failures
exhausted the new viewpoint evidence contract; Local 003 also retained an
unsupported continuity allegation and a likely false hard critic blocker.
The adjudication node was never eligible in that case. Local Bible fixes were
not reached, and human quality evidence remains pending.

Selective repairs on the existing v26 development branch use graph v7 / prompt
v27 for new executions. Aligned viewpoint reviews need no quotation; genuine
violations use exact evidence handles and a different character's narrative
breach. Reviewer-format failures no longer enter critic input as manuscript
evidence. Approved-style/focal-character distinctions, first-allegation continuity
ledgers, bounded viewpoint audits, and combined terminal diagnostics are added.
Existing Bible-history protection and bounded adjudication remain intact.
Offline regression and protected saved-input probe tooling are implemented;
verification passes Ruff, strict mypy (149 files), all 396 Python tests, frontend
format/lint/type checks, all 11 frontend tests, and the production build. All
eight planned probe selections compile read-only against their frozen inputs;
live probes, a new full canary, repeatability, and blind review are still pending.
Step 19 remains **IN PROGRESS**; no later phase is started. Evidence:
`docs/benchmark_reports/step-19-local-cloud-v26-canary-2026-09-08.md` and ADR 0008.

The completed v27 isolated suite validated all eight responses in eight calls,
with no response repairs. Local 002/003 recovered the intended allowance for
assigned-character interiority/deductions, and both Bible probes preserved exact
resolved-thread history. Local 005 nevertheless missed its intended positive
control: direct narration of Cora's private feelings with Elara explicitly
assigned and no specific style authorization for that shift. The full canary was
held; response validation was not treated as semantic success.

The targeted follow-up uses prompt v28 with unchanged graph v7 on
`codex/v28-production-contract`. Critic guidance now distinguishes attributable
inference from direct private access, generic internalized style from specific
narrative permission, and short intrusions from whole-scene replacement. It
preserves assigned-character interiority, dialogue, observable behavior, authorized
omniscient/shifting narration, and status-only aligned responses. Non-canonical
contrasting examples and offline regression controls are added without changing
the writer, output schemas, graph, budgets, or Bible reducer. Three exact-input
Local follow-up probes are prepared with explicit semantic expectations, not run.
Verification passes Ruff lint/format, strict mypy across 150 Python files, all
412 Python tests (including 16 new viewpoint controls), frontend format/lint/type
checks, all 11 frontend tests, and the production build. All three follow-up
selections compile read-only with verified input hashes and Local 005's exact
reference evidence. Thirteen protected historical/probe hashes remain unchanged.
No live probes or full canary are launched. Step 19 remains **IN PROGRESS**, with
live semantic verification, repeatability, and blind review pending. Evidence:
`docs/benchmark_reports/step-19-v27-isolated-probes-2026-09-08.md` and ADR 0009.

The subsequent 31b candidate stage made 33 Cloud calls: 24/24 new POV controls
matched provisional assistant labels, while the unchanged full critic made 9/9
correct raw POV decisions but validated only 6/9 complete responses. All three
Local-002 failures confused an evidence ID with a quotation. Local-005's Cora
0044 intrusion was caught in all three samples; two raw pass verdicts were
correctly normalized to revise. Other substantive judgments remain unadjudicated.

Prompt v29 retains graph v7 and implements one version-bound evidence-reference
interface for assignment, POV, and ordinary craft findings, plus application-owned
rubric identity and a fixed three-dimension scene-craft mean separate from hard
gates. Canonical evidence remains exact excerpts and old artifacts stay readable.
Generic guidance distinguishes missing outcomes from optional stronger
dramatization without declaring the disputed scenes right or wrong. No model
routing, writer, budget, retry, continuity, or Bible behavior changes.
Verification passes Ruff lint/format, strict mypy across 151 Python files, all
449 Python tests, frontend format/lint/type checks, all 11 frontend tests, and
the production build. Six read-only request compilations confirm Local/Cloud
schema parity for the three frozen scenes; 425 protected evidence files remain
unchanged. Pending promotion requirements are documented in
`docs/benchmark_reports/step-19-31b-transfer-v29-corrections-2026-09-09.md` and
ADR 0010. No live v29 evaluation or canary is launched. Step 19 remains
**IN PROGRESS**, with human adjudication, expanded live controls, bounded repair
loops, and blind story-quality review still pending.

### Testing direction update — 2026-09-11

The operator designates `gemma4:31b` through Ollama Cloud
(`gemma4:31b-cloud`) as the testing model. E4B-driven tuning and further narrow
proofreading experiments are deferred. Local, Hybrid and Cloud remain product
options; no runtime profile, production prompt v29, graph v7 or safety gate changes
in this documentation update. The next priority is complete Cloud production,
including recovered failures, revision behavior and human story quality.

The evidence register now consolidates 264 Cloud calls in the September 9–11
focused series, plus the earlier single Cloud v27 probe. It records strong POV
and assignment results, 3/3 exact-preservation c05 writer repairs, and the latest
17/21 versus 15/21 minimal word-repair recommendations. The human correction
that c05 requires duplicate removal is retained explicitly; Local-002/003's
disputed broader judgments remain unscored. No v27/v28/v29 full canary has been
completed. Latest full Cloud canary completions remain v25 4/4 and v26 3/4.

Step 19 stays **IN PROGRESS**. Its current phase is explicitly Cloud-first:
complete the intended workflows across the frozen 12-prompt corpus, compare
against the direct-model baseline, inspect clean versus recovered completions,
and collect the required blind human scores, hard-gate decisions, preference and
budget evidence. Establish repeatability before closing this phase. This dated
policy supersedes the earlier all-profile completion prerequisite for the current
phase; Local/Hybrid qualification is deferred, not recorded as passed. Declare a
new scope-bound plan and evidence record rather than marking the unfinished
48-case historical campaign complete or weakening its sealing invariants.
Hybrid evaluation is considered only after Cloud-first completion, with separate
authorization. Step 20 has not started and no new model run is launched here.

References:
[testing decision](../docs/benchmark_reports/model-testing-direction-2026-09-11.md),
[exact evaluation register](../docs/benchmark_reports/gemma4-31b-evaluation-register-2026-09-11.md),
[deferred issue draft](../docs/issue_drafts/gemma4-31b-critic-repair-follow-up.md).

### Manual v29 Cloud evidence — 2026-09-12

Ten fresh manual stories completed under production prompt v29 / graph v7 with
the Cloud 31B model, accepting 59/59 planned scenes. A read-only SQLite audit
reconciles 326 calls (61 Blueprint + 265 production), six automatically recovered
failed attempts, eight one-cycle scene revisions, 10 exact Blueprint approvals
and zero run-control records. Notes, screenshots, artifacts, invocation lineage
and accepted manuscripts are preserved under
data/diagnostics/manual-v29-cloud-2026-09-12/. Public results and hashes are in
the [manual evaluation report](../docs/benchmark_reports/manual-v29-cloud-production-2026-09-12.md).

This manual completion sample is separate from the frozen 12-prompt corpus and
had no human literary scores or matched direct-model baseline at this checkpoint.
Step 19 remained **IN PROGRESS**; the canary batches, blind review, budget
assessment and repeatability were outstanding. All ten manual literary reviews
are now complete; see the September 30 entry below. No model call, canary staging,
production-contract change or later phase began while documenting this evidence.

### v29 Cloud canary batch 1 completed — 2026-09-12

Cloud OH-V01-001 through OH-V01-004 completed under prompt v29 / graph v7:
**4/4 stories, 21/21 accepted scenes, 99/99 succeeded production invocations**.
Five continuity-driven prose revisions completed without failed calls or manual
controls. The isolated approved-seed copy, explicit four-case scope, exact prior
approvals, source hashes, logs and completed snapshot are preserved under
data/benchmarks/v0.1/v29-cloud-batch-1-2026-09-12/. The
[batch report](../docs/benchmark_reports/step-19-cloud-v29-batch-1-2026-09-12.md)
records usage, matched historical Cloud comparisons and two semantic questions
requiring human review.

At batch 1 close, Step 19 remained **IN PROGRESS**. Batches 2 and 3 had not started; human quality,
direct-model baseline/preference, budget acceptance and repeatability remain
outstanding. No runtime tuning, later phase or Hybrid execution was introduced.

### v29 Cloud canary batch 2 completed — 2026-09-12

Cloud OH-V01-005 through OH-V01-008 reached terminal outcomes under the same
prompt v29 / graph v7, Cloud model, approved Blueprints, seeds and budgets:
**2/4 stories completed, 16/21 scenes accepted, 88 production calls (84 succeeded,
4 failed), five prose revisions**, in 453.888 seconds. Cases 006 and 008
completed. Case 005 exhausted its continuity structured-repair attempt on scene
2; case 007 reached the hard-critic revision limit on scene 5. The latter's
repeated POV allegation despite inference wording remains a semantic review
question, not a human-adjudicated defect. Case 008 recovered a critic validation
failure automatically.

Local receipts, failure details, exact revision diffs, two completed manuscripts,
failed-case partial drafts and an audited final snapshot are preserved under
data/benchmarks/v0.1/v29-cloud-batch-2-2026-09-12/. The archive's 17 evidence files
and 179 artifact content hashes were validated; original seed, batch 1 evidence
and runtime hashes remain unchanged. No new Blueprint calls, approvals, manual
run controls or production tuning occurred.

At batch 2 close, eight of twelve Cloud cases had been attempted: **6 completed, 2 failed,
37/42 planned scenes accepted** across batches 1 and 2. Batch 3 had not started.
The final consolidated diagnostic document was deferred until all three batches
finished, as requested. Step 19 remains **IN PROGRESS**; human quality, direct-model
preference, budget acceptance and repeatability remain outstanding.

### v29 Cloud canary cycle completed; diagnostics consolidated — 2026-09-12

Batch 3 ran Cloud OH-V01-009–012: **3/4 stories completed, 17/22 accepted
scenes, 81 calls (78 succeeded, 3 failed), three prose revisions**, in 452.385
seconds. Cases 010–012 completed; 009 exhausted the critic's structured repair
on the assigned-character interiority validation rule. Its failure and all
partial artifacts are retained. Case 010 recovered a writer JSON error.

All three batches now cover **12/12 frozen Cloud cases: 9 completed, 3 failed,
54/64 planned scenes accepted, 268 calls (261 succeeded, 7 failed), 13 prose
revisions across 12 scenes**. Recorded usage was 2,767,113 input + 224,110 output
tokens; summed runner time was 1,398.995 seconds. No new Blueprint calls,
approvals, manual run controls or runtime tuning occurred.

The [consolidated diagnostic report](../docs/benchmark_reports/step-19-cloud-v29-consolidated-2026-09-12.md)
records outcomes, exact failure classes, recovery, critic/continuity questions,
revision preservation, usage, matched historical context and source receipts.
Nine completed manuscripts and failed-case drafts are indexed in local
data/diagnostics/v29-cloud-cycle-2026-09-12/. All three archives passed source,
approval and integrity checks (52 archived files, 561 artifact hashes).

The canary execution and requested consolidation are complete. **Step 19
remains IN PROGRESS**: repeated POV boundary failures, case 007's inference
loop and questionable continuity rechecks need adjudication; blind human
quality/preference, real cost acceptance and repeatability remain open.
No later phase or additional model experiment has started.

### Failed-review evidence implemented — 2026-09-12

The first production-improvement step is complete: rejected critic, continuity
and continuity-adjudication responses now retain bounded, redacted, allowlisted
findings on the failed invocation, with exact input/candidate versions, scene/POV
assignment, selected request-catalog evidence and explicit capture availability.
The diagnostic record distinguishes an unassigned viewpoint from an allegation
about the assigned character without changing the existing validator or error.
Rejected findings remain unvalidated allegations, never manuscript facts.

Prompt v29, graph v7, response schemas, provider requests, retries, revision
limits and acceptance behavior are unchanged. Failure evidence is excluded from
retry context and model messages. Historical canary archives remain unchanged;
missing historical response bodies cannot be recovered. No live calls were run.
See [ADR 0011](../docs/adr/0011-bounded-failed-review-evidence.md).

Validation: 461 Python tests passed, including 12 new failure-evidence cases
covering both POV causes, source resolution, malformed output, capture bounds,
redaction, migrated SQLite persistence, recovery/terminal failure at the existing
limit, artifact and prompt isolation, unchanged retry context, export and replay.
Ruff lint/format and strict mypy passed. Frontend formatting, lint, type checking,
all 11 tests and the production build also passed.

**Step 19 remains IN PROGRESS.** Assignment-aware schemas, repair acceptance
criteria, critic adjudication and continuity policy are separate future work.
This completes observability work, not a claim of improved model judgment or
production success rate; no later product phase has started.

### Assignment-bound critic schema completed — 2026-09-13

Production-improvement step 2 is complete under prompt v30 / graph v7.
The application specializes each critic response schema from the exact approved
scene assignment: no assigned POV means only aligned status is available;
assignment findings can select only populated supported anchors. Explicit POV
and the existing single-character fallback retain the current narrative audit.
Same-character and other semantic/structural guards remain unchanged; no closed
character roster or keyword-derived narrative permission was introduced.

Production and isolated-probe requests use the same specialization. Prompt prose,
input artifacts, budgets, retry/revision limits and all manuscript acceptance
rules remain unchanged; schema size is equal or smaller for matched inputs.
See [ADR 0012](../docs/adr/0012-assignment-bound-critic-schema.md).

Validation: 472 Python tests passed (11 new cases), Ruff lint/format and strict
mypy passed, and the production build passed. Offline controls cover Local/Cloud
schema delivery, explicit/unassigned/fallback POV, populated anchors, unchanged
hard gates, source immutability, and SQLite workflow completion/replay.

The authorized focused Cloud probe of OH-V01-009 scene 2 used source invocation
c79d2999-842a-4710-a101-fc57ade60b7e and exact frozen v29 input artifacts,
gemma4:31b-cloud, seed 19209 and unchanged per-call budgets. It returned a valid
pass with no issues on its first call: 13,323 input / 467 output tokens, 1,945 ms
provider latency. Evidence is in data/diagnostics/v30-step2-cloud-009-2026-09-13/.
This is one isolated critic result, not a full-story completion, a new canary
score or repeatability evidence. The original source snapshot hash was verified.

Manual-test policy agreed on 2026-09-13: the user will run one or more stories
after each improvement step and keep a date/story log. Do not create individual
manual-story reports. Preserve normal app diagnostics and, when the user asks
after at least ten manually tested stories, compile an aggregate diagnostic
review that distinguishes the contract/runtime versions tested. Focused
benchmark retests may accompany individual steps.

**Step 19 remains IN PROGRESS.** Repair criteria, critic adjudication and
continuity policy remain subsequent work; no later product phase has started.


### Revision acceptance tests completed — 2026-09-13

Production-improvement step 3 is complete under prompt v31 / graph v8.
Writer and critic now share a bounded, version-bound repair target derived from
the current scene's earlier canonical critiques and exact rejected drafts.
Revision reviews must assess each target as met/unmet with current-draft
evidence. Unmet issues retain their original severity; perfect craft scores
cannot clear an unmet hard repair. Independent new blockers still apply.

The original claim, evidence and acceptance condition stay available across the
existing revision allowance. Exact repeated category/severity/claim/repair text
keeps its first target; no fuzzy semantic matching is introduced. Advisory
feedback remains available to the writer without becoming a hard gate. Actual
word changes neither guarantee nor automatically become necessary for approval.
Continuity rechecks/adjudication and all retry, call and revision limits remain
unchanged. Canonical artifact schemas and SQL storage remain compatible.
See [ADR 0013](../docs/adr/0013-revision-acceptance-tests.md).

Context projections replace duplicated historical review and scene prose while
preserving exact input-version lineage, the full current draft and canonical
Bible. Writer/critic instruction text is shorter than v30. All three matched
probe requests were smaller than their v30 equivalents. Successful repair
assessments and failed review checks are retained in redacted diagnostic records.

Validation: 486 Python tests passed, including 14 step-3 cases; the final focused
repair suite also passed after the severity-preservation check. Ruff lint/format,
strict mypy and the production build passed. Tests cover shared targets, stable
original evidence, current-reference validation, missing/invented checks,
unresolved hard gates, nonblocking advice, severity escalation, exact SQLite
lineage, secret-safe audit/export, bounded recovery and replay.

Four authorized isolated Cloud critic probes covered three frozen v29 scenes:
007 scene 5 revision 1 (twice), 006 scene 5 revision 1 and 009 scene 2. All four
validated on their first attempt and returned pass. Both 007 probes and 009
retained nonblocking notes; 006 had no issues. The repeated 007 probe verified the success-audit export.
Its saved assessment overcredits a qualifier already present in the original, so
the pass does not establish sound critic reasoning. Original snapshots were
hash-verified and remain unchanged. Exact requests, restored review lineage,
results, measured sizes and runtime receipts are under
data/diagnostics/v31-step3-cloud-2026-09-13/.

These were critic probes, not fresh writer runs, complete stories or a new canary
completion score. The aggregate manual-test review remains deferred until the
user requests it after at least ten stories. **Step 19 remains IN PROGRESS**;
critic adjudication and continuity-policy changes are steps 4 and 5 and have
not been implemented. No later product phase has started.


### Bounded critic adjudication — 2026-09-13

Production-improvement step 4 is COMPLETE under prompt v32 / graph v9.
The registered critic_adjudication node reuses the existing
one-visit/two-attempt terminal adjudication allowance. It addresses typed POV and
scene-assignment allegations against the approved plan, complete current scene
and original repair tests. Upheld or uncertain findings remain blocking. Unrelated
critic issues and all continuity blockers prevent this path; competing review
blockers are identified explicitly. Continuity-only adjudication is unchanged.

A new immutable critique preserves original evidence, scores and rubric verdict;
only specifically released allegations become notes. Diagnostics bind exact
source critique/candidate IDs and issue decisions. No ordinary prompt growth,
new prose retries, increased budgets, migrations or new human checkpoints.
See [ADR 0014](../docs/adr/0014-bounded-critic-adjudication.md).

Validation: the full 511-test Python regression suite passed. A final 35-test
focused run passed after adding rejection-text isolation, covering all 26 step-4
cases plus the production graph controls. Ruff lint/format, strict mypy (158 files)
and the production build passed. Ordinary writer/critic instructions remain
586/3,848 characters; the separate adjudication instruction is 1,298 characters.
A matched fixture request is shorter than its full critic counterpart. No live
v32 Cloud probe or canary was run; offline outcomes establish control-flow and
contract behavior, not semantic accuracy or a new completion score.

The three post-step-3 manual stories completed under v31 with 74 production calls
and no failed calls. Keep these separate from v32 validation. No individual manual
report or comparative quality judgment is inferred from the SammyAI premise reuse.
The aggregate manual review remains deferred until the user requests it after at
least ten stories. **Step 19 remains IN PROGRESS** and step 5 remains pending.


### Contradiction versus ordinary development — 2026-09-13

Production-improvement step 5 is COMPLETE under prompt v33 / graph v9.
Continuity claims now bind timeline events to their time and scene, identify
state snapshots by their actual update scene, and distinguish initial knowledge,
scoped facts and open/resolved history. Administrative kind/status labels cannot
supply contradiction evidence. Later change and missing explanatory bridges do
not alone establish incompatibility; real contradictions and explicit constraints
remain blocking. Existing dispositions, revision limits, budgets and adjudication
allowances are unchanged. See [ADR 0015](../docs/adr/0015-scoped-continuity-development.md).

The three latest v32 manual stories completed. The Root Ritual resumed at
19:51:02 local after the reported reboot, using the interrupted scene's exact
input lineage. App records do not establish the OS crash's cause. Future recovery
now closes stranded calls as interrupted_execution with unknown provider outcome,
without treating process loss as a malformed-response retry or removing it from
the aggregate call budget. Original completed-run records remain unchanged.
SQLite integrity and foreign-key checks passed, as did all 146 artifact hashes.
No adjudication was exercised by these three manual runs.

Validation: all 521 Python tests passed, Ruff lint/format and strict mypy (159
files) passed, and the production build passed. Nine new cases cover scoped
claims, retained constraints, real SQLite advisory/hard routing and recovery
bookkeeping. Three reconstructed v32 requests exactly matched their recorded
hashes; each matched v33 request was shorter. Continuity system text decreased
from 7,328 to 7,184 characters. Evidence is retained locally under
data/diagnostics/v33-step5-offline-2026-09-13/.

No live v33 probe or canary was run, and offline outcomes do not establish a
semantic improvement or completion rate. All five production-improvement
implementations are complete. The user's manual-test cadence continues; aggregate
review remains deferred until requested after at least ten stories. **Step 19
remains IN PROGRESS** pending evaluation/human review. No later product phase has
started.


### Aggregate manual v29–v33 evidence — tested 2026-09-13, reviewed 2026-09-14

The requested [twelve-story manual diagnostic review](../docs/benchmark_reports/manual-v29-v33-cloud-production-2026-09-13.md)
is COMPLETE. All 12 workflows completed with 70/70 accepted scenes: one story
under v29, two under v30, and three each under v31, v32 and v33. The sample records
381 calls (308 production / 73 Blueprint), seven recovered failed responses,
one interrupted v32 execution and seven one-cycle prose revisions. The interrupted
call remains a historical RUNNING row; its provider outcome is unknown. One
recovery at 19:51:02 local is supported by matching task/input lineage.

The review preserves 613 verified artifact hashes, 2,322 input links, 12 rendered
manuscripts, exact premises, version/seed identities, review audits and revision
diffs under data/diagnostics/manual-v29-v33-cloud-2026-09-13/. All 12 applied
Blueprint approvals are recorded; no in-app run controls or human quality scores
exist. SQLite integrity, completion-event lineage, bundle hashes and report links
were checked. No model calls, application-code changes or historical-data edits
were made for the review.

The sample includes one v31 critic acceptance test and three failed continuity
response captures, but no live adjudication. v33 completed all three stories while
still needing four structural response repairs and two prose revisions. Repeated
time-coverage evidence failures and questionable semantic allegations remain
visible. Different stories tested each contract, so neither a causal improvement
percentage nor a new combined canary score is inferred. At this checkpoint,
**Step 19 remained IN PROGRESS** pending controlled evaluation and human review.
All twelve manual literary reviews are now complete; see the September 30 entry
below. No later phase started.


### v33 Cloud canary batch 1 completed — 2026-09-14

Cloud OH-V01-001–004 completed under prompt v33 / graph v9: **4/4 stories,
21/21 scenes, 88 production calls (87 succeeded, one recovered response failure)**.
One scene received one prose revision. No new Blueprint calls or human approvals,
manual retries, terminal adjudication or revision-limit exhaustion occurred.
The run lasted 682.266 seconds, including one successful 202.158-second critic
request. The next two batches have not been staged or launched.

The isolated batch used the original human-approved seed, migrated only in its
new directory. Exact Blueprint IDs/hashes, seeds, Cloud profile and limits match
v29 batch 1. Ollama remains 0.34.0 and its model alias digest matches. Source,
runtime and v29 evidence hashes were preserved. All 192 selected-project artifact
hashes, final manuscript references, retry input lineage, database integrity and
secret-export checks passed. The report is schema-valid with exactly four results.

Evidence, completed snapshot and manuscripts are under
`data/benchmarks/v0.1/v33-cloud-batch-1-2026-09-14/`; the
[batch report](../docs/benchmark_reports/step-19-cloud-v33-batch-1-2026-09-14.md)
records the matched comparison. Calls decreased from 99 to 88 and revisions from
five to one, with 13.8% fewer total tokens. Failed calls rose from zero to one,
and elapsed time increased. All 21 initial drafts differ from v29, so this is
not an identical-prose test of reviewer accuracy. The time-coverage evidence
failure persists; the isolation-rule repair and its qualification are retained.

The separate cycle scope preserves the original 48-case plan's approval lineage
while selecting only this Cloud subset. Batch 2 is 005–008 and batch 3 is 009–012;
consolidation awaits both. **Step 19 remains IN PROGRESS**; no human quality scores
or later product phase are claimed.


### v33 Cloud canary batch 2 completed — 2026-09-14

Cloud OH-V01-005–008 completed under the unchanged prompt v33 / graph v9:
**4/4 stories, 21/21 scenes, 99/99 successful production calls**. Five revisions
occurred across four scenes; no failed responses, new human approvals, manual
retries, adjudication or revision-limit exhaustion occurred. Cases 005 and 007,
which failed under v29, now complete. Runtime, seeds, exact approved Blueprints,
Cloud profile and limits match the frozen cycle. Batch 1 evidence is preserved.

The [batch-2 report](../docs/benchmark_reports/step-19-cloud-v33-batch-2-2026-09-14.md)
and local archive `data/benchmarks/v0.1/v33-cloud-batch-2-2026-09-14/` preserve the
final snapshot, manuscripts, review audits, five diffs, comparison hashes and
semantic inspection notes. All 201 selected-project artifact hashes passed;
canonical output lineage, inherited seed counts, database integrity, secret export,
source hashes, bundle receipts and documentation links were checked.

Calls increased from v29's 88 to 99 while accepted scenes rose from 16 to 21.
The batch took 881.186 seconds; completion gains do not establish efficiency or
literary superiority. All 18 comparable initial drafts differ. 005's redundant
identification-evidence recap and 007's grief-inference handling remain review
concerns, despite successful production and explicit repair tests.

The first two batches total 8/8 completed cases, 42/42 scenes, 187 calls (186
succeeded, one recovered failure), and six revisions. Batch 3 (009–012) has not
been staged or launched. Full diagnostic consolidation waits for that batch.
**Step 19 remains IN PROGRESS**; no human quality scores or later phase are claimed.


### v33 Cloud canary cycle completed; diagnostics consolidated — 2026-09-14

The final batch, Cloud OH-V01-009–012, completed **4/4 stories and 22/22 scenes**
in 568.998 seconds: 101 calls (100 succeeded, one recovered continuity validation
failure), with four POV revisions in 011. The user-authorized three-batch cycle
is now complete under unchanged prompt v33 / graph v9, with **12/12 completions,
64/64 scenes, 288 calls (286 succeeded, two recovered failures), and ten prose
revisions across nine scenes**. All three v29 failures now complete; no prior
success regresses in this run. No terminal retry, limit increase or tuning occurred.

The [single consolidated report](../docs/benchmark_reports/step-19-cloud-v33-consolidated-2026-09-14.md)
incorporates all three batches, the matched v29 comparison, review/revision
analysis, timing, usage and twelve manuscript links. Final batch evidence lives
in `data/benchmarks/v0.1/v33-cloud-batch-3-2026-09-14/`; consolidated analysis,
lineage, exact recovery checks and semantic notes are in
`data/diagnostics/v33-cloud-cycle-2026-09-14/`. Checks verified 59 source archive
files, 599 artifact hashes, exact selected outcomes/approved inputs, consistent
snapshots, all manuscript hashes, unchanged source/seed/prior receipts, database
integrity/foreign keys, existing secret-export guards, and documentation links.

Both failed responses lacked current-draft time-coverage evidence. The 012
capture additionally preserves an unsupported closed-versus-unlocked allegation
that disappeared on same-draft structured retry. 005/4 requirement scope, 007/5
and 011/2 POV inference, and assessments crediting retained text remain review
concerns. Nine critic repair assessments record eight met and one unmet result;
no live adjudication occurred. All 57 paired initial drafts differ from v29.

The cycle used 3,171,102 tokens and 2,132.449 seconds of summed runner time while
completing ten more scenes than v29. No equal-work speed/cost or literary-quality
claim is inferred. Application source did not change; validation covered canary
evidence and documentation rather than rerunning the application build/test suite.
**Product Step 19 remains IN PROGRESS** pending semantic review, human quality/
preference, cost acceptance and repeatability; no later product phase is started.

### Cloud-first harness configuration completed - 2026-09-19

Item 1 of the remaining Step 19 engineering work is **COMPLETE**. New campaign
plans explicitly declare `cloud-first` (12 Cloud + 12 direct baseline cases) or
`all-profiles` (the existing 48-case default). Cloud-first planning needs only a
complete Cloud preset and freezes the baseline from its scene-writer selection.
Execution and approval defaults follow the plan; out-of-scope targets fail.

Plan schema 2 binds the complete declared matrix and seeds to the frozen corpus.
Summaries omit excluded profiles while retaining missing/failed planned cases in
the denominator. Sealing requires every terminal result, every eligible successful
comparison, exact output content, human reviews and a matching summary. Legacy
schema-1 hashes, summaries and sealing requirements remain intact; old Cloud
canaries do not become completed formal campaigns. Operator commands and design
are documented in the [benchmark guide](../benchmarks/README.md) and
[ADR 0016](../docs/adr/0016-scoped-benchmark-campaigns.md).

Validation passed: 537 Python tests, Ruff lint/format, strict mypy on 160 files,
frontend format/lint/type checks, 11 Vitest tests and production build. Sixteen new
cases cover scoped execution/evidence and historical compatibility. All six actual
v29/v33 campaign plan hashes and report bindings also passed read-only verification.
Two older operator fixtures now use complete matrices over smaller test corpora.
An existing parallel Blueprint recovery test failed once in the initial full run,
then passed isolated and in the final full run without test or workflow changes;
this intermittent result is retained for item 3, with no asserted root cause.

The user's next-model direction is recorded: after v0.1-alpha, limited evaluation
of additional models, tentatively GPT and Gemini; exact choices remain undecided.
Plans remain provider/model-neutral. The CLI still executes through Ollama
transports; this work adds no native GPT/Gemini adapters or live model runs.
Production prompt v33, graph v9, runtime limits and approval rules are unchanged.

Remaining engineering/evaluation sequence:

- [x] 1. Make Cloud-first evaluation a supported harness configuration.
- [x] 2. Distinguish unknown cost from an actual zero cost (completed 2026-09-19 below).
- [x] 3. Complete remaining failure-path verification (completed 2026-09-19 below).
- [x] 4. Execute full premise-to-story Cloud evaluation against the direct baseline (execution and human review complete 2026-09-30; acceptance shortfalls recorded below).
- [ ] 5. Establish repeatability and seal the formal evidence after human review (September campaign sealed; prospective three-repeat series started 2026-10-02, as recorded below).

**Product Step 19 remains IN PROGRESS.** No later product phase has started.

### Evidence-based cost acceptance completed - 2026-09-19

Item 2 of the remaining Step 19 engineering work is **COMPLETE**. Model responses,
persisted invocations and portable benchmark outputs now distinguish unknown,
provider-reported and local-inference cost evidence. An explicit reported zero is
eligible; Ollama Cloud's numeric placeholder is not. Migration 0008 preserves
historical amounts and assigns unknown provenance without inference or repricing.

Complete story costs require evidence for every invocation, including Blueprint
preparation and recovered production attempts. Baseline reporting now also retains
failed attempts and their known response cost/usage when a later attempt succeeds.
Interrupted calls with unknown outcomes prevent the story total being treated as
known. Exact invocation IDs bind the evidence across completion and replay.

Summary schema 2 reports known/unknown case coverage and leaves cost acceptance
`null` until every planned Cloud/Hybrid case has a complete cost total. With full
coverage, the unchanged median-budget criterion can pass or fail. New seals use
schema 2 and cannot reuse an old numeric-cost pass. Historical schema-1 archives
retain exact verification semantics, explicitly identified by the CLI. Sealing
unknown evidence does not establish cost qualification.

Validation passed: **560 Python tests**, Ruff lint/format, strict mypy on 163
files, frontend format/lint/type checks, **11 Vitest tests** and production build.
Twenty-two new cost tests and one populated migration test cover reported zero,
unknown and over-budget amounts, missing coverage, non-finite values, recovered
attempts, exact cost lineage, deterministic seals and legacy compatibility.
Existing production tests also verify that a missing Blueprint or recovered-call
cost makes the entire story total unknown, without additional model calls.

Read-only reanalysis of all six actual v29/v33 canary reports yields unknown Cloud
cost acceptance and preserves the source bytes and plan hashes. A fixed synthetic
archive generated before this change verifies byte for byte. No historical report
or user database was rewritten or migrated, and no live model call was made.

Before starting the updated application or database-backed harness, apply the
normal Alembic upgrade to the active database. The [operator guide](../benchmarks/README.md#cost-evidence-and-acceptance)
and [ADR 0017](../docs/adr/0017-evidence-based-cost-acceptance.md) explain the new
fields and migration. Prompt v33, graph v9, model routing, retry allowances and
runtime ceilings remain unchanged. Unknown provider charges still cannot prove
an actual billed-spend ceiling; no pricing or subscription allocation is invented.

**Product Step 19 remains IN PROGRESS.** Items 3-5, human review and actual cost
qualification remain outstanding. No later product phase has started.

### Failure-path verification completed - 2026-09-19

Item 3 of the remaining Step 19 engineering work is **COMPLETE** for the
application/harness paths documented in the
[failure-path verification matrix](../docs/verification/step-19-failure-paths-2026-09-19.md).
Twenty-five new parametrized cases exercise Cloud transport faults through
persisted baseline/Blueprint execution, process loss and committed-output recovery,
production timeout exhaustion, active-call shutdown/user stop, and failed report
writes. Existing budget, bounded adjudication and case-isolation tests remain part
of the verification evidence.

The checks reproduced and fixed two defects. Blueprint recovery could complete
while leaving a lost provider invocation RUNNING; it now reconciles orphaned calls
using production's shared recovery routine and preserves unknown outcome/cost.
Process loss remains in budget/cost accounting but supplies no false response-repair
instruction. Worker shutdown could cancel the same execution twice and interrupt
terminal-call cleanup; it now waits for cancellation cleanup before closing the
claimant, and repeated stop commands avoid a second cancellation.

The intermittent parallel Blueprint recovery test now waits for the successful
sibling's durable SQLite pending writes, replacing the previous 10 ms timing
assumption. Its original assertion remains intact. Separate tests verify that
outputs committed before graph completion are reused without another provider
call or artifact version. Accepted scenes and prior artifact hashes survive
production recovery. Failed report writes preserve prior bytes and recover from
persisted output without another model call.

Validation passed: **585 Python tests**, plus **30 affected tests** after the final
repair-context adjustment; Ruff lint/format, strict mypy on **165 files**, frontend
format/lint/type checks, **11 Vitest tests** and production build. No live model
request, user-database write or historical-evidence rewrite was performed. No
migration is required. Prompt v33, graph v9, routing, retry/revision allowances and
budgets remain unchanged.

This is deterministic engineering evidence, not live adjudicator-quality or
physical OS/disk-failure certification. Packaged desktop failure testing remains
Step 21 work. **Product Step 19 remains IN PROGRESS**, with items 4-5, real human
review and actual cost qualification still outstanding. No later product phase
has started.

### Formal Cloud-versus-baseline evaluation staged - 2026-09-29

At setup, item 4 was **IN PROGRESS: prepared, not launched**. A fresh plan-schema-2
`cloud-first` campaign covers all twelve frozen premises with twelve agentic Cloud
cases and twelve direct-model baseline cases. It uses `gemma4:31b-cloud`, prompt
v33 / graph v9, current Blueprint prompt v9 / graph v4, and the merged failure-path
fixes at commit `a60f7037367c16b1cdab0bdc55c360caaa22ecde`.

Campaign `042918c2-8a50-49fd-831b-c1a93553d4f6` is staged in
`data/benchmarks/v0.1/formal-cloud-v33-2026-09-29/`, with an isolated schema-0008
database, frozen inputs, zero-result report, source/environment/budget receipt,
read-only verifier and phased PowerShell runner. There are no inherited approvals,
Blueprints, production outputs or checkpoints. All 123 frozen runtime/configuration
hashes and SQLite integrity/foreign-key checks passed; all story-state counts are
zero at setup. Metadata confirmed Ollama 0.34.4 and the existing Cloud model alias.
No model generation had started at setup, and the source application database
was read-only. Subsequent execution is recorded below.

The [setup report and runbook](../docs/benchmark_reports/step-19-formal-cloud-v33-setup-2026-09-29.md)
define fresh Blueprint preparation, mandatory human approval, direct baselines,
three four-case production batches, blind review and later evidence sealing.
Retry/revision allowances, budgets and prompt content are unchanged. No migration
is required for the user's already-updated application database.

At setup, the user reported completing reviews for all **22 manually tested
stories**; their discussion was deferred as requested. Those reviews remain
separate from the formal comparisons. Formal human scoring and independent
repeatability were still outstanding at that checkpoint. Subsequent human review
and sealing are recorded in the September 30 entry below. Cost acceptance remains
unknown under Ollama Cloud's current cost evidence. **Product Step 19 remains
IN PROGRESS.**

### Formal Cloud Blueprint generation - 2026-09-29

At the preparation checkpoint, item 4 was **IN PROGRESS: 12/12 fresh Blueprints awaiting human approval** in
campaign `042918c2-8a50-49fd-831b-c1a93553d4f6`. Sequential preparation took about
6 minutes 48 seconds, using 74 model calls: 72 succeeded and two integrator
responses failed schema validation, then recovered within the existing retry
allowance. There were no terminal case failures. Token totals, including failed
attempts, are 197,928 input and 77,883 output.

The [Blueprint generation report](../docs/benchmark_reports/step-19-formal-cloud-v33-blueprints-2026-09-29.md)
records exact packet lineage, failed-call details and checks. All 123 frozen
runtime/configuration hashes passed verification; no prompts, limits or
application source changed. All twelve Blueprint/critique pairs were packaged and
matched persisted content hashes. No human decision, production run or direct
baseline run had been recorded at that checkpoint.

The user stated an intention to approve the generated set without editorial review or edits.
A technical approval manifest identifies exact versions without revealing story
content. Approval was still pending at that checkpoint; this choice is not a quality
assessment and does not establish that the user read the Blueprints. The existing
mandatory checkpoint was preserved. **Product Step 19 remained IN PROGRESS**;
production, baselines, formal human reviews, cost qualification and independent
repeatability evidence were outstanding at that checkpoint.

### Formal Cloud approval and execution - 2026-09-29

The user explicitly approved all twelve generated Blueprints without editorial
review or edits. Their exact packet-bound decisions were imported with zero model
calls. The twelve direct-model baselines then completed successfully using twelve
calls. All three production batches have finished under the unchanged v33
configuration: **11/12 Cloud stories completed, 64/65 scenes accepted**. Batch
outcomes were 4/4, 4/4 and 3/4. See the
[execution report](../docs/benchmark_reports/step-19-formal-cloud-v33-execution-2026-09-29.md).

OH-V01-012 failed on the final scene's critic request: the provider reported
27,542 input tokens against the unchanged 24,000-token per-call cap. Five scenes
were accepted, and the sixth draft is preserved as partial evidence. The failed
request's usage is retained. No terminal case was rerun and no limit changed.
Cloud completion is **91.7%, so the formal 95% technical criterion is not met**.

The full campaign used 382 calls, including two recovered Blueprint validation
failures, five recovered production validation failures and one terminal budget
failure. Production used 296 calls and made 11 prose revisions across 10 scenes;
there were no adjudication calls. All 622 artifact-version hashes passed audit,
as did exact approval/manuscript lineage, SQLite integrity/foreign keys, budget
and runtime checks, and the database secret-export audit.

At generation close, eleven eligible randomized A/B pairs and a blank canonical
review form were ready; the answer key, detailed diagnostics and database snapshot
remained private. Formal human review, cost qualification and item 5's independent
repeatability evidence were outstanding. Item 4 and **Product Step 19 remained
IN PROGRESS** at that checkpoint. The request-size failure still needs investigation
with the frozen result preserved. Subsequent review and sealing follow below.

### Human reviews recorded and formal evidence sealed — 2026-09-30

- [x] Record literary reviews for all **22 manual stories**: ten from September 12
  and twelve from September 13.
- [x] Import all **11 eligible formal A/B comparisons** from the user's completed
  review CSV, bound to the canonical public packet.
- [x] Recompute formal acceptance from actual human scores.
- [x] Seal and verify the reviewed formal campaign evidence.

The [manual review collection](../docs/september_2026_manual_test_reviews/)
contains 22 individual reviews, the
[review summary](../docs/september_2026_manual_test_reviews/review-summary.md) and
[AI-pattern observations](../docs/september_2026_manual_test_reviews/AI-patterns.md).
All 24 copied documents match the proofread originals. These qualitative manual
reviews remain separate from formal paired scores.

The [formal execution and review report](../docs/benchmark_reports/step-19-formal-cloud-v33-execution-2026-09-29.md#human-review-completed--2026-09-30)
records all outcomes. Cloud technical completion is **11/12 (91.7%)**; mean
weighted human score is **3.4818**; agentic preference is **4/11 (36.4%)**, with
seven baseline wins and no ties. Those three criteria are **not met**. All reviewed
candidates pass the hard gates, the Cloud severe-continuity-free rate is **11/11**,
and the lowest Cloud dimension mean is **3.0**. Cost acceptance remains **unknown**.
The failed OH-V01-012 stays in the technical denominator. No failed output was
replaced and no acceptance threshold changed.

The canonical import, reviewed summary, evidence seal and independent archive
verification passed offline with **zero model calls**. All 123 frozen runtime
files and database row counts were unchanged. The verified archive is retained
at `data/benchmarks/v0.1/formal-cloud-v33-2026-09-29/private/evidence.zip`.

**Item 4 is complete as an executed and reviewed evaluation.** Item 5 remains
open for independent repeatability, although this campaign's seal is complete.
**Product Step 19 remains IN PROGRESS** for repeatability, cost qualification and
the unmet acceptance criteria. No later product phase has started.

### Formal v33 Cloud repeatability started — 2026-10-02

**Item 5 is IN PROGRESS.** The user authorized the repeatability assessment.
The [prospective protocol and evidence register](../docs/benchmark_reports/step-19-v33-cloud-repeatability-2026-10-02.md)
declares three fresh Cloud-first campaigns, each with all twelve frozen premises,
twelve independent direct baselines, new Blueprints and exact-version human
approval before production. The September 29 reviewed campaign is a historical
reference and does not count as one of the three prospective repeats.

All three campaigns have unique identities and case IDs, isolated schema-0008
databases and matching corpus/profile/seed/limit snapshots. Setup verified zero
story-state rows and no inherited approvals or outputs. All **123 runtime files**
match the reference at merged source commit
`acf97b8087370acb713857e568e59a1722039bbc`. Prompt v33 / graph v9 is unchanged.
Ollama is now **0.35.0**, compared with 0.34.4 in the reference; all three new
campaigns use 0.35.0, with the same Cloud model alias digest. Historical comparisons
retain that environment difference. Remote provider weights are not pinned.

The series register and pre-generation protocol snapshot are under
`data/benchmarks/v0.1/v33-cloud-repeatability-2026-10-02/`. Repeat 1's Blueprint
preparation completed: **12/12 awaiting approval, zero terminal failures**,
74 calls (72 successful and two recovered HTTP 502 service errors), 189,277
recorded input tokens and 71,889 recorded output tokens in about 7m 18s. Both
service errors occurred on OH-V01-003 and returned no usage; zero placeholders
do not prove no provider work. The approval packet and database snapshot are
preserved, all 155 artifact hashes passed verification, and the secret-export
audit passed. No approval, baseline or production run has been recorded.

Repeats 2 and 3 remain staged with zero story-state rows and model calls.
New exact-version approvals, production, baseline generation, actual human
reviews and the three new evidence seals remain outstanding. All terminal failures
will be retained. The sequence ends after three campaigns and review, regardless
of whether the acceptance criteria pass; no extra attempt is added to improve a
headline result. Cost qualification remains unknown.

The user subsequently approved all twelve repeat-1 Blueprints as generated.
Verification at 07:05:01 UTC confirmed twelve durable decisions and zero model
calls added by import. The direct baseline phase began at 07:05:08 UTC, followed
by the three declared production batches. The blank approval form and
authorization/import receipts are preserved.

Repeat 1 generation finished at 07:29:01 UTC: **12/12 baselines, 12/12 Cloud
stories and 64/64 scenes completed**. The full campaign used 376 calls, including
two recovered Blueprint HTTP 502 failures and one recovered production continuity
evidence-reference failure. Production used 290 calls, with eleven revisions
across eleven scenes and no adjudication. All 620 artifact hashes and exact
manuscript lineages passed verification; the database secret-export audit passed.
The final OH-V01-012 critic call used 23,515 input tokens, only 485 below the
unchanged 24,000 cap. The earlier terminal error did not recur; request-size
reliability remains a concern.

All twelve randomized A/B pairs and a blank canonical review form are packaged.
The technical criterion passes for this campaign; the five human-quality,
preference and cost criteria remain unresolved. The generation receipt binds
81 evidence files, but a reviewed formal seal awaits actual human scoring.
Reference evidence and all frozen runtime files are unchanged. Repeats 2 and
3 remain unlaunched; one completed generation does not establish repeatability.

**Product Step 19 remains IN PROGRESS.** No writing-tic changes or later product
phase has started.

### Repeat 1 reviewed and sealed — 2026-10-02

- [x] Validate all twelve submitted A/B reviews with the canonical parser;
  preserve every score and preference unchanged.
- [x] Record the reviewer's originality/dialogue calibration as dated metadata,
  without changing the frozen protocol, rubric, weights or thresholds.
- [x] Import reviews, recompute acceptance, seal and independently verify repeat 1.

The [repeatability report](../docs/benchmark_reports/step-19-v33-cloud-repeatability-2026-10-02.md#repeat-1-human-review-and-seal--2026-10-02)
records **4.05/5 Cloud versus 4.15/5 baseline**, with **5 Cloud wins, 4 baseline
wins and 3 ties**. Canonical half-credit for ties gives **54.1667% Cloud preference**,
below 60%. Technical completion, severe-continuity-free assessments, weighted
quality and the dimension floor pass; cost acceptance remains unknown. All
24 candidates pass all human hard gates. Character depth and voice/prose remain
the lowest Cloud dimensions at 3.0.

Originality now assesses generated execution given the supplied premise, and
occasional dialogue overlength can qualify as a minor editing issue when the
other canonical qualities meet the score anchor. Carry this interpretation into
repeats 2 and 3. It differs from September's review calibration, so scores from
the two periods must not be pooled as identically calibrated quality evidence
or used to claim an engineering improvement.

The reviewed archive SHA-256 is
`0d5611771cd993023338039ebb76becea719900f5e9519ae89e8fb63d15ed43d`;
its manifest SHA-256 is
`f4391c6ff2778beaa5b5ab53fbe04b07dc4acccf9c9fd2ece2572c6d9ae7abe7`.
Input digests, the original blank CSV, generation summary and snapshot remain
preserved, and the dated calibration addendum is bound to the seal by the external
review-verification receipt. Import and sealing added zero model calls.

Repeat 2 passed empty-database, frozen-input and provider checks, then prepared
**12/12 fresh Blueprints** in about 8m 01s. All twelve await human approval;
zero baseline or production runs have started. Preparation used 73 calls
(72 succeeded, one recovered structured-output failure), 195,649 input tokens
and 75,262 output tokens. OH-V01-012's first Blueprint integration response
omitted five required scene numbers and recovered within the existing allowance.
All 161 artifact hashes, exact packet references, SQLite checks and secret-export
audit passed. The exact packet SHA-256 is
`86888a4837922cd88eac4c537c9f30cd3b784048367f214929940306d6a5be87`.
Its identifier-only approval manifest and source snapshot are preserved. The
September reference and repeat-1 review/seal remain unchanged. The new generated
versions require new human approval before production. Repeat 3 remains staged
with zero model calls.

The user subsequently approved all twelve repeat-2 Blueprints. Verification at
15:17:36 UTC confirmed twelve durable decisions and zero inference calls added
by approval import. Baseline generation began at 15:17:36 UTC, followed by the
three declared sequential production batches. All original forms and approval
receipts are preserved. **Item 5 and Product Step 19 remain IN PROGRESS.**

### Repeat 2 generation complete — 2026-10-02

The [repeatability report](../docs/benchmark_reports/step-19-v33-cloud-repeatability-2026-10-02.md#repeat-2-generation-results--2026-10-02)
records **12/12 Cloud stories, 12/12 baselines and 64/64 accepted scenes**.
The campaign used 368 calls, with four failed structured responses recovered on
the same task: one Blueprint integration failure and three production failures
covering critic repair-test coverage, a missing continuity finding summary and
invalid continuity evidence references. No terminal case was rerun or replaced.
Production made eight prose revisions across seven scenes and no adjudication
calls. The whole agentic arm used 356 calls, 3,029,350 input tokens and 309,142
output tokens. Dollar cost remains unknown.

Production finished at 15:43:08 UTC / 17:43:08 Europe/Belgrade after about 22m 46s;
baseline generation took about 2m 38s. OH-V01-012 completed without a production
call failure; its largest input was 20,104 tokens. The largest production input
overall was 21,042 on OH-V01-009, below the unchanged 24,000 cap. This does not
establish that request-size reliability is solved.

Verification checked 617 artifact hashes, exact approved/manuscript lineage,
recorded usage, frozen limits, SQLite integrity/foreign keys and secret-export
safety. Blind-packet reconstruction and canonical blank-form checks passed.
The generation receipt binds 84 evidence files; original reference and repeat-1
review/seal hashes remain unchanged. All completed outputs differ by content hash
from Repeat 1, and Repeat 3 remains empty.

The **twelve eligible blind pairs await actual human review** using the recorded
originality/dialogue calibration. The technical criterion passes; four human
quality/preference criteria and cost remain unresolved. The reviewed summary
and formal seal must wait for those scores. **Item 5 and Product Step 19 remain
IN PROGRESS.**

### Repeat 2 reviewed and sealed; repeat 3 preflight stopped — 2026-10-03

- [x] Validate all twelve repeat-2 human comparisons and preserve the submitted
  CSV unchanged; no corrections were needed.
- [x] Import the canonical review, recompute acceptance, seal and independently
  verify repeat 2's evidence.
- [x] Check repeat 3's frozen inputs, empty database and provider metadata.
- [x] Resolve Ollama version drift before any repeat-3 model call; the user
  subsequently authorized 0.35.1 as documented below.

The [repeatability report](../docs/benchmark_reports/step-19-v33-cloud-repeatability-2026-10-02.md#repeat-2-human-review-and-seal--2026-10-03)
records **4.1167/5 Cloud versus 4.1583/5 baseline**, with **1 Cloud win, 4 baseline
wins and 7 ties**. Half-credit for ties gives **37.5% Cloud preference**, below
the unchanged 60% threshold. Technical completion, severe-continuity-free review,
weighted quality and the dimension floor pass. All 24 candidates pass all gates;
character depth and voice/prose remain at 3.0 in both arms. Cost remains unknown.
The October 2 reviewer calibration is retained without a further reported change.

The reviewed archive SHA-256 is
`669eb4271dede30804419db802a58762ae91bd2f92d03b07e65090a85008bad2`;
its manifest SHA-256 is
`4854c81df5265eeac1eb760f8e132eb1ab8a1fb885e27cb22c84ec8e3205bc6c`.
Import and sealing added zero model calls. Original scores, generation evidence,
the September reference and repeat 1's reviewed seal remain preserved.

Repeat 3's provider check found **Ollama 0.35.1**, while the frozen series requires
**0.35.0**. All 123 application runtime hashes, frozen inputs/operator helpers,
model alias, alias digest and remote-model name still match. Its story-state
tables are empty; zero inference calls were made. The local
`preflight-environment-drift-2026-10-03.json` receipt preserves the discrepancy.
The next decision is restoring the declared environment or explicitly authorizing
a documented deviation before generation. No frozen check has been bypassed.

Both completed repeats retain their unmet preference criterion and unknown cost.
The third campaign and consolidated assessment remain outstanding. **Item 5 and
Product Step 19 remain IN PROGRESS.** No later product phase has begun.

### Repeat 3 environment exception authorized — 2026-10-03

The user explicitly authorized proceeding with **Ollama 0.35.1**. The
[dated environment addendum](../docs/benchmark_reports/step-19-v33-cloud-repeatability-2026-10-02.md#repeat-3-authorized-environment-addendum--2026-10-03)
was recorded at 13:07:38 UTC before any repeat-3 generation. The original 0.35.0
freeze, failed-preflight evidence, all original operators and earlier reviewed
seals remain intact. Only the expected daemon version changes for this repeat;
the model/profile/corpus/runtime/prompts/graphs, budgets, retries, checkpoints,
rubric and fixed three-campaign endpoint are unchanged.

The additional `run-campaign-approved-environment.ps1` and
`verify_approved_environment.py` preserve the original checks and require exactly
0.35.1 plus the unchanged alias digest/remote-model name. Their hashes are bound
by `environment-amendment-2026-10-03.json`, SHA-256
`4bd2e765ee1089e85c1d3c7b8a7022ef03ed8370ef40dbc9658db3ca72ee8eaa`.
The approved-environment empty-state/provider verification passed. Blueprint
preparation has started; exact generated-version approval is still required
before drafting. The daemon difference must remain explicit in the consolidated
analysis. **Item 5 and Product Step 19 remain IN PROGRESS.**

### Repeat 3 Blueprints prepared; human approval pending — 2026-10-03

- [x] Prepare all twelve fresh Blueprints under the authorized Ollama 0.35.1
  environment addendum and unchanged model, runtime, prompts and budgets.
- [x] Package the exact-version approval manifest, preserve the source database
  and verify the checkpoint, artifact hashes and earlier reviewed evidence.
- [x] Obtain human approval for these twelve generated versions; the subsequent
  authorization and import are recorded below.
- [x] Run the direct baselines and three production batches; outcomes are
  recorded in the generation-complete entry below.
- [ ] Collect fresh human A/B reviews, seal repeat 3 and consolidate the fixed
  three-repeat assessment.

The [repeat-3 checkpoint](../docs/benchmark_reports/step-19-v33-cloud-repeatability-2026-10-02.md#repeat-3-blueprint-checkpoint--2026-10-03)
records **12/12 awaiting approval**, **zero terminal failures**, **73 calls**,
**195,239 input / 75,152 output tokens**, and about **6 minutes 20 seconds**.
OH-V01-012's Blueprint integration omitted five required scene numbers and
recovered within the existing retry allowance; no limit or prompt changed.
All 158 artifact hashes, SQLite integrity/foreign keys, secret-export audit and
the preserved earlier seals passed verification. The approval packet SHA-256 is
`c32e2a59867a536d9c6926f7565f5713b515d1f41c8252eda5fb2cb2b5d86c96`.
Zero human approvals, baseline runs or production runs are recorded for repeat 3.
The environment exception does not authorize the new Blueprints. **Item 5 and
Product Step 19 remain IN PROGRESS.**

### Repeat 3 approved; generation underway — 2026-10-03

The user approved all twelve presented Blueprints without editorial changes.
Canonical import persisted twelve exact-version decisions and completed all
twelve Blueprint workflows with zero additional model calls, verified at
13:18:19 UTC. The original blank form, checkpoint and database snapshot remain
preserved. The [approval record](../docs/benchmark_reports/step-19-v33-cloud-repeatability-2026-10-02.md#repeat-3-approval-and-generation--2026-10-03)
binds the authorization to the previously presented packet. Baseline generation
has started after another successful approved-environment check; the three
production batches and fresh human review follow. **Item 5 and Product Step 19
remain IN PROGRESS.**

### Repeat 3 generation complete; ten human comparisons pending — 2026-10-03

- [x] Complete all 24 planned attempts: **10/12 Cloud successes**, **12/12 baseline
  successes**, **56/64 accepted scenes**, with both failed cases retained.
- [x] Preserve full diagnostics, verify 585 artifact hashes and the completed
  database snapshot, and retain the original freeze and both prior reviewed seals.
- [x] Package and independently verify ten eligible blind A/B pairs, the blank
  canonical review form and unchanged reviewer calibration.
- [x] Receive and import the ten actual human reviews, seal repeat 3, and finish
  the consolidated assessment at the predeclared three-campaign endpoint, as
  recorded in the October 4 completion entry below.

The [generation report](../docs/benchmark_reports/step-19-v33-cloud-repeatability-2026-10-02.md#repeat-3-generation-complete-human-review-pending--2026-10-03)
records **352 calls**, **2,879,354 input / 330,292 output tokens**, and about
**18 minutes 37 seconds** for production. Seven calls failed: three recovered
within existing retries, while four attempts account for the two failed stories.
OH-V01-002 reintroduced an older, cleared finding into the current continuity
recheck partition; OH-V01-010 first omitted a finding summary and then supplied
invalid evidence references. All four terminal responses retain untruncated
unvalidated review evidence. No manuscript defect is established by those
invalid responses alone. No retry allowance, prompt or budget changed.

The preserved 82-file generation manifest has SHA-256
`5304f86eae2321c9b74a0751ef5cd034e719beb9b310a11f58f8750c13f18d44`.
The public packet SHA-256 is
`decaaa85f9b65ac389da63697e6b6af74138adae0fb882d2093b9aafa40e6eea`.
Technical completion is **83.33%**, below the unchanged 95% criterion. Human
quality/preference results remain pending; cost remains unknown. The technical
series is **12/12, 12/12, 10/12 Cloud**, with **36/36 baselines**; repeat 3 retains
its authorized Ollama 0.35.1 qualification. Generation completion does not close
the reviewed evidence or the full assessment. **Item 5 and Product Step 19
remain IN PROGRESS.** Step 20 has not started.

### Item 5 complete: reviewed three-repeat assessment sealed — 2026-10-04

- [x] Validate and import Repeat 3's ten comparisons without modifying the CSV:
  160 scores, 140 true hard-gate answers and ten valid preferences.
- [x] Recompute results, seal Repeat 3 and independently verify its archive.
- [x] Reverify all three individual seals, submitted reviews, original generation
  evidence, database counts, runtime hashes and declared addenda.
- [x] Consolidate every prompt's three outcomes, technical diagnostics and human
  results, retaining both failed cases and all cost/environment qualifications.
- [x] Preserve the reviewer's new qualitative observations and the unchanged
  manual-review summary separately from the canonical scores.

The [completed assessment](../docs/benchmark_reports/step-19-v33-cloud-repeatability-2026-10-02.md#consolidated-three-repeat-assessment--2026-10-04)
records **34/36 Cloud completions**, **36/36 baselines**, **184/192 accepted scenes**
and **34 reviewed pairs**. Reviewed means are **4.1059 Cloud / 4.1529 baseline**;
preferences are **7 Cloud wins, 10 baseline wins and 17 ties**, or **45.59% Cloud
preference** with half credit. The report preserves the separate campaign results
and cohort differences; pooled numbers are descriptive, not new pass criteria.

Repeat 3 scored **4.16 Cloud / 4.15 baseline**, with 1 Cloud win, 2 baseline wins
and 7 ties. Its reviewed archive SHA-256 is
`f0f74505f17bd08b0480aa9f675a4a604c0b9f1e27c7208b5ac2e7ff37d907af`;
canonical manifest SHA-256 is
`418b578711afc75268d81e1b4936317765323b4b90cd3ca6c5b8948acd23c5c8`.
The local `consolidated-register-2026-10-04.json` under the series directory binds
the three seals and all case-level evidence, SHA-256
`1a15ce8db3619122776c943778c9b0586899c798f970eb44e7c3952293f1876a`.
Review import and consolidation added **zero model calls**; campaign invocation
counts remain 376, 368 and 352. No production code, prompt, limit or retry changed.

All eligible human review and formal evidence work is complete. **Item 5 is
COMPLETE as an assessment; Product Step 19 remains IN PROGRESS.** Technical
acceptance failed in repeat 3, preference failed in all three repeats, and cost
is still unknown. The qualitative feedback identifies character depth, prose
repetition, limited character variety and group dynamics as corrective priorities.
The proposed work is not implemented, and Step 20 has not started. No fourth
campaign or terminal-case replacement was added.

### Repeat 3 continuity response-contract corrections — 2026-10-04

**v34 / graph v9 implementation and targeted format probes complete; full-story
qualification pending.**
[ADR 0018](../docs/adr/0018-current-continuity-rechecks-and-compact-coverage.md)
records the exact OH-V01-002 and OH-V01-010 failure inputs and the corrections.

- [x] Distinguish the latest report's active finding keys from historical
  recurrence context; omit an empty model-facing recheck partition while still
  rejecting stale keys, malformed values and missing active decisions.
- [x] Derive coverage-gap summaries from the assessment; remove the redundant
  evidence-search selector and preserve mandatory exact evidence lists, targeted
  repair suggestions and the existing advisory/blocking rules.
- [x] Locate coverage text failures at the model's keyed response field and make
  the existing bounded repair explicit about missing versus empty evidence.
- [x] Add regression coverage for persisted history, validation, recovery,
  terminal failure, successful audit and replay without duplicate calls.
- [x] Reconstruct both original requests read-only, match their recorded v33
  hashes and verify shorter v34 messages: 41,436 to 39,997 characters for 002;
  40,738 to 40,495 for 010. System instructions also shrink.
- [x] Run the two isolated Cloud continuity probes after explicit user approval
  to send the frozen inputs. Both validated on their first attempts: exactly two
  calls, 19,665 input tokens and 2,069 output tokens, under unchanged limits.
- [ ] Resolve the remaining judgment/recurrence concerns and qualify production
  completion separately. Each valid review still retained one blocking finding.

Offline replay of 010's captured fields reproduces the old missing-summary error
and validates with v34 while retaining its independent contradiction blocker.
It does not establish the model's semantic correctness. Local reproduction files
are in `data/diagnostics/v34-continuity-validation-2026-10-04/`; the source snapshot
hash is unchanged. Writer/critic instructions, graph, budgets, retries, revision
limits, canonical schemas and the v33 campaign evidence remain unchanged. No
migration is required. The literary-quality work has not started.

Verification: **629 Python tests** pass, including **44 new regression cases**;
Ruff lint/format, strict mypy on 166 files, frontend formatting/lint/type checks,
all 11 frontend tests, production build and `git diff --check` pass.

The live probes ran at 14:09:53–14:10:04 Europe/Belgrade on October 4 using Ollama
0.35.1 and the same `gemma4:31b-cloud` alias digest and seeds as the frozen inputs.
Provider latencies were 4.596 s for 002 and 4.398 s for 010. Monetary cost remains
unknown. The actual request hashes matched the offline v34 packets and the source
snapshot hash remained unchanged. Results are stored in the diagnostic directory's
`live/` subdirectory; no canonical artifacts or campaign results were written.

002's stale-key format error did not recur, but the same handwriting-verification
allegation returned through the new-findings route and inherited its historical
ID and `still_blocking` disposition. This exposes a remaining recurrence concern:
that historical match bypasses the guard restricted to `newly_exposed` findings.
010's absent time cue became advisory as intended; its separate back-door blocker
requested a deletion explanation already present in the following sentence.
These observations warrant semantic and recurrence analysis. Neither scene nor
story was declared recovered, and no extra writer or adjudicator calls were made.

**Product Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.** Item 5 remains
complete as an assessment and sealing task, not as demonstrated repeatability.

### Technical stabilization v35 begun 2026-10-08

**IN PROGRESS — offline checks pass; live probes assessed; semantic recovery unqualified.**
Temporary branch: `codex/continuity-stabilization-v35`. The user authorized the
short technical stabilization before the creative-quality changes.
[ADR 0019](../docs/adr/0019-inactive-continuity-recurrence-and-counterevidence.md)
records the implementation and prepared evaluation.

- [x] Apply the revision evidence guard using the latest report's active finding
  IDs, so historical identity cannot bypass it. Preserve historical IDs, real
  blockers, independent hard gates, and the existing repair/revision limits.
- [x] Replace continuity guidance to consider nearby explanations and the strongest
  counterevidence before blocking or requesting a repair already present.
- [x] Add 14 regression cases, including persisted recovery within two review
  attempts and terminal failure without an extra writer call.
- [x] Pass repository checks: 643 Python tests, 11 frontend tests, Python and
  frontend lint/format/type checks, and the production build.
- [x] Reconstruct the exact v34 inputs read-only and verify shorter v35 requests:
  39,997 to 39,958 characters for 002; 40,495 to 40,479 for 010.
- [x] Run and assess four live probes, including two genuine contradiction
  controls, after explicit cloud-payload approval. All validate in one attempt;
  both controls catch the injected contradiction, but both original cases block.
- [ ] Resolve the remaining continuity judgment concern before expanding tests.
- [ ] Perform a bounded full-story check if probe results support proceeding.

The captured 002 finding cites five rewritten excerpts, so the guard change
alone does not reject it; its semantic judgment still needs evaluation.
The four probes used four of the maximum eight calls: 39,384 input / 4,467 output
tokens, with a published-rate estimate of USD 0.00730056 assuming uncached input
(the allocation estimate was USD 0.05248). Actual charges remain unknown.
Historical costs and formal cost-acceptance rules are unchanged. Automatic
approval review initially rejected the cloud launch; it ran only after the user
explicitly approved these private inputs, controls, and destination. The frozen
database and canonical artifacts are unchanged; no formal campaign rerun occurred.

002 still treats repeated verification as a contradiction despite the current
scene assignment requiring verification. Historical advice to remove it remains
in context and is the next focused investigation target. 010 now raises the
current-system flag rather than demanding the deletion explanation already
present; its timing still needs assessment. The 010 positive control catches the
injected denial but mixes physical and code back-doors in its repair explanation.
These results do not support expansion to a full-story run yet.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Inactive review advice investigation v36 begun 2026-10-08

**IN PROGRESS — implementation verified; live assessment does not establish semantic recovery.**
Temporary branch: `codex/continuity-history-v36`.
[ADR 0020](../docs/adr/0020-inactive-review-advice-projection.md) records the narrow
context change and comparison against v35.

- [x] Trace old repair instructions reaching the current continuity review after
  their finding leaves the active set.
- [x] Omit inactive repair advice and stale dispositions from the supervisor's
  history projection; preserve allegation identity, authority references,
  active repairs, full persisted history and all validation gates.
- [x] Add 11 regression cases, including a complete persisted workflow, and
  reconstruct all four saved v35 requests with exact matching hashes.
- [x] Verify that v36 changes only the contract version and inactive history
  projection: 002 requests shrink by 275 characters; 010 sizes are unchanged.
- [x] Pass repository checks: 654 Python tests, 11 frontend tests, lint,
  formatting, strict type checks, production build and clean whitespace checks.
- [x] Run and assess four explicitly approved live probes, all valid on their
  first attempt. 002 still blocks; both injected contradictions are caught.
- [ ] Establish sufficient semantic evidence before a bounded full-story check.

The automatic approval review rejected the v36 cloud launch as a new private
payload requiring explicit authorization. No call ran in that launch; the user
then explicitly approved the v36 probes. The experiment used four calls,
39,300 input / 3,838 output tokens, estimated at USD 0.00703720 with uncached
input, within the eight-call / USD 0.05248 allocation estimate. Actual charges
remain unknown. Request/response hashes and the unchanged snapshot were checked.

The model still treats repeated verification as incompatible with its earlier
occurrence and generates similar repair advice after the original instruction
is removed. The old allegation summary remains visible; its influence versus
independent model judgment is the next focused question. 010 clears on one call,
but it had no historical context affected by this change, so the result cannot
be credited to the fix. Its contradiction control still uses a confused
physical/code back-door explanation. No full-story run or formal rerun follows
from this limited evidence; semantic recovery and repeatability remain open.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Controlled inactive-summary experiment begun 2026-10-08

**Diagnostic COMPLETE — no semantic improvement from history removal; stabilization IN PROGRESS.**
Production remains v36 / graph v9. The
[experiment record](../docs/benchmark_reports/continuity-summary-experiment-2026-10-08.md)
fixes three conditions: current history, inactive summaries omitted, and inactive
findings omitted entirely from model context. Application validation retains the
complete immutable history in all three.

- [x] Prepare exact matched packets and verify that only the designated history
  fields change; preserve active repairs, canon, scene assignment, schema and
  the version label. Check source immutability and saved v36 request hashes.
- [x] Prespecify three paired original-draft seeds plus one positive control per
  condition: 12 probes, up to 24 calls, no outcome-dependent rerolls.
- [x] Obtain explicit permission for this modified private payload set and run it.
- [x] Assess repeated-verification blockers, other findings and control detection
  by seed before making any further production-context change.

The maximum published-rate allocation estimate is USD 0.15744 assuming uncached
input at the dated October 8 rates. The user explicitly approved the set. All
12 probes validated on their first attempts, using 114,632 input / 12,758 output
tokens, estimated at USD 0.02115168. Actual charges remain unknown. Prepared and
live request hashes, response hashes, plan hash and source immutability were
verified; all projection preflight checks passed. No application code changed.

Each condition reproduced the repetition blocker at all three seeds (3/3 each).
All three positive controls correctly identified the injected denial; no other
findings appeared. Historical allegation text is not necessary for this judgment
in the frozen case. No additional history removal is adopted in production.

Read-only inspection also found that the approved scene 1 ends with a decision
to verify, but its accepted draft already performs the verification assigned to
scene 2. The next draft repeats that sequence and two sentences verbatim. The
next focused target is the acceptance of this premature completion of a later
scene's work, together with distinguishing dramatic repetition from contradictory
facts. This experiment does not qualify full-story recovery or repeatability.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Scene-1 acceptance trace completed 2026-10-08

**Diagnostic COMPLETE — scene-endpoint detection gap identified; stabilization IN PROGRESS.**
The [acceptance trace](../docs/benchmark_reports/scene-one-acceptance-trace-2026-10-08.md)
follows OH-V01-002's original v33 writer, critic, continuity and Bible-update
invocations through the recorded scene-1 accept event.

- [x] Verify exact artifact provenance and the unchanged read-only snapshot.
- [x] Establish normal first-draft acceptance: critic PASS, no issues, three 5/5
  scores; continuity has one informational observation and no blocker.
- [x] Confirm that writer and critic saw the current "decides to verify" outcome,
  while future scene assignments were hidden and the overall story arc's later
  verification action remained visible.
- [x] Locate explicit critic praise for the overrun and the missing dedicated
  endpoint/next-scene-reservation assessment.
- [x] Reconstruct an identical critic message hash under current v36 and verify
  that a synthetic reported outcome violation forces revise despite 5/5 scores.

The Bible update accurately recorded the verification already performed in the
accepted prose. The failure was detection of the scene-boundary overrun before
acceptance, not a reported blocker being discarded, a cost/retry limit, or lost
canonical memory. Contextual influence on the model remains an interpretation;
the records cannot reveal unretained internal reasoning.

The next proposed implementation is a compact, version-bound scene endpoint and
immediately subsequent reserved turn/outcome for the existing writer and critic,
with controls for proper stopping, permitted foreshadowing, the original overrun
and correctly assigned verification. It is not implemented by this investigation.
No model calls, new inference costs, production changes or formal reruns occurred.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Shared scene boundary implemented and probed 2026-10-08

**Implementation COMPLETE — semantic detection unqualified; stabilization IN PROGRESS.**
Prompt v37 / graph v9 adds the same compact current endpoint and immediately next
scene's reserved turn/outcome to the existing writer and critic. The exact
current plan and approved Blueprint versions provide provenance. Their scoped
requests replace global plot prose; all 19 measured historical requests are
shorter. See [ADR 0021](../docs/adr/0021-shared-scene-boundary.md) and the
[implementation/probe report](../docs/benchmark_reports/scene-boundary-v37-2026-10-08.md).

- [x] Preserve approved artifacts, current canon and input lineage while sharing
  the boundary on initial and revision calls, without a new role or model call.
- [x] Distinguish premature completion from permitted setup, foreshadowing,
  incidental follow-through and approved overlap; retain existing hard gates.
- [x] Verify 11 focused offline cases, persisted revision/replay, and final
  Python/frontend checks (665 Python tests, 11 frontend tests, production build).
- [x] Prepare five isolated critic probes, obtain explicit permission, and run
  the frozen original, stopping/foreshadowing controls, assigned scene-2
  verification and a missing-turn control.
- [x] Verify prepared/live hashes, source immutability and usage separately from
  actual billing; retain the unsuccessful overrun result without rerolling.
- [ ] Demonstrate reliable overrun detection and fresh writer behavior.

All five probes validated on their first attempts. Proper stopping,
foreshadowing and correctly assigned verification passed; the missing-turn
control produced a blocking assignment issue. **The original scene-1 overrun
still passed with three 5/5 scores.** The model praised journal comparison while
describing the ending as a decision to verify. The context is now available, but
the requested comparison is not reliably applied.

Usage was 53,809 input / 2,497 output tokens: USD 0.00853206 at dated published
rates, against an approved maximum estimate of USD 0.06560. Actual charges remain
unknown. No new writer generation, canonical change or full-story rerun occurred.
The next proposed target is a small evidence-backed boundary assessment within
the existing critic response; this further change is not implemented.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Required critic boundary comparison implemented and probed 2026-10-08

**Implementation COMPLETE — overrun detection still unqualified; stabilization IN PROGRESS.**
Prompt v38 / graph v9 requires an achieved state, separate current/next comparisons,
current evidence handles and an overrun status inside the existing critic call.
Successful comparisons are retained with exact input lineage; malformed responses
use bounded review repair. A valid reported overrun becomes a blocking assignment
issue regardless of craft scores. See
[ADR 0022](../docs/adr/0022-required-critic-boundary-comparison.md) and the
[implementation/probe report](../docs/benchmark_reports/critic-boundary-v38-2026-10-08.md).

- [x] Require bounded comparisons and exact current evidence in Local/Cloud
  schemas and application validation; specialize away inapplicable overruns.
- [x] Preserve independent hard gates, canonical schemas, writer messages,
  profiles, call/revision budgets and graph routing.
- [x] Export bounded, redacted successful audits and failed-review diagnostics.
- [x] Pass 23 new focused cases and complete checks: 688 Python tests, 11 frontend
  tests, lint/format/type checks and production build.
- [x] Obtain explicit permission and run the same five v37 frozen inputs under
  v38; verify exact request/response/source hashes and retain all results.
- [ ] Demonstrate improved overrun detection and qualify fresh writer behavior.

All five probes validated on their first calls and retained their v37 verdicts.
The original still passes with three 5/5 scores, but its required comparison now
explicitly acknowledges verification beyond the decision to verify. It permits
this as a general match, reserving a particular secret flourish for scene 2.
The stopping, foreshadowing and assigned-verification controls pass. The
missing-turn control correctly blocks on assignment but also emits a questionable
extra plot allegation. The comparison is observable; correctness remains fallible.

Usage was 53,894 input / 3,484 output tokens, estimated at USD 0.00893876 against
the approved maximum estimate of USD 0.06560. Actual charges are unknown. The five
initial requests grow by 134 characters each; sampled revision requests grow by
134–912 characters without increased budgets. No writer call, canonical edit or
formal rerun occurred.

The next policy question is whether retaining a more specific later detail
authorizes material advancement beyond the current endpoint. Further changes
and additional probes are not included in this implementation.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Current scene endpoint made independently binding and probed 2026-10-08

**Implementation COMPLETE — original overrun still missed; stabilization IN PROGRESS.**
Prompt v39 / graph v9 tells writer and critic that retaining a more specific later
detail does not authorize an earlier result beyond the current endpoint.
Inconclusive tests, setup and incidental follow-through remain allowed within
that endpoint; explicit current-plan instructions can authorize overlap. See
[ADR 0023](../docs/adr/0023-binding-current-scene-endpoint.md) and the
[implementation/probe report](../docs/benchmark_reports/binding-endpoint-v39-2026-10-08.md).

- [x] Share the revised policy and request the authorizing current-plan field
  and instruction within the existing five-field critic comparison.
- [x] Permit an overrun with a current outcome/turning-point anchor independently
  of a next reservation, including final scenes; preserve other hard gates.
- [x] Route reported overruns through existing blocking issues and revision,
  with repair guidance that removes the unassigned result rather than one detail.
- [x] Preserve schemas, profiles, budgets, repair guidance v10 and graph routing.
- [x] Pass 11 new cases and full checks: 697 Python tests, 11 frontend tests,
  lint/format/type checks and production build.
- [x] Run seven explicitly approved, hash-frozen Cloud critic probes: the same
  five v38 inputs plus an inconclusive test and synthetic authorized overlap.
- [ ] Demonstrate semantic overrun detection, fresh writer compliance and
  full-story recovery.

All seven probes validated on their first calls and returned `no_overrun`.
The original still passes with perfect scores: the critic acknowledges an
identical handwriting match but labels the comparison preliminary, treats the
current outcome as satisfied and relies on the later stronger revelation.
The five legitimate-progress controls pass without boundary false positives,
but this does not establish discrimination when the positive case is missed.
The missing-turn control correctly blocks on assignment and retains an extra
overbroad plot allegation. No semantic rerolls or writer calls occurred.

Usage was 74,937 input / 4,778 output tokens, estimated at USD 0.01240238 against
the approved maximum estimate of USD 0.09184. Actual charges are unknown. The
seven critic requests grow by 251 characters; corresponding writer requests grow
by 254, with unchanged budgets. Source/request/response hashes verified and
canonical stories, sealed benchmarks and historical results remain unchanged.

The next diagnostic question is whether next-scene context still anchors this
judgment or the current outcome is independently treated as a minimum achievement.
No additional ablation or response-contract change is included here.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Controlled next scene reservation comparison completed 2026-10-09

**Diagnostic comparison COMPLETE — overrun detection unresolved; stabilization IN PROGRESS.**
Production remains prompt v39 / graph v9. Twelve approved isolated probes compare
the same request with its explicit next-scene reservation present or projected
as absent. Three paired seeds test the original OH-V01-002 overrun; one pair each
tests an inconclusive attempt, explicitly authorized verification and a missing
required turn. See the
[comparison report](../docs/benchmark_reports/reservation-context-comparison-2026-10-09.md).

- [x] Freeze exact inputs, unchanged system/schema/settings and a single-field
  projection; balance pair order and predeclare the stopping rule.
- [x] Verify that both conditions retain the overrun route and that request,
  materialized guidance and diagnostic audit use the same projected boundary.
- [x] Run the approved twelve probes, preserving all fourteen calls including
  two bounded structural repairs for invalid evidence-handle ordinals.
- [x] Reconstruct every request, replay validated materialization and verify
  source/request/response hashes; pass 36 focused probe/endpoint tests.
- [ ] Establish correct overrun detection and full-story recovery.

The original passes with `no_overrun` under every tested seed in both conditions.
All three no-reservation reviews explicitly recognize completed verification,
then treat the assigned decision to verify as achieved. Two reservation-present
reviews require structural repairs, so only one original pair consists of two
validated first calls. The rejected responses also propose no-overrun, but are
not counted as accepted critiques. The legitimate controls pass and the missing
turn blocks independently in both conditions.

The explicit reservation is not necessary for this failure. Broader creative-brief,
location and premise guidance still describes verification in both conditions;
its influence versus interpreting the endpoint as a minimum remains unresolved.
The next diagnostic target is this distinction between story-wide goals and
current-scene obligations, before further production changes.

Usage was 146,702 input / 9,643 output tokens, estimated at USD 0.02439548 using
the recorded October 8 rates, within the approved USD 0.15744 allocation estimate.
Actual charges remain unknown. Production source, canonical stories, sealed
benchmarks and historical results are unchanged; no writer or full-story run
occurred. Full application gates were not repeated for this diagnostic/docs change.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Broader context and current scene obligation comparison completed 2026-10-09

**Diagnostic comparison COMPLETE — overrun detection unresolved; stabilization IN PROGRESS.**
Production remains prompt v39 / graph v9. Twelve approved isolated probes compare
the full no-reservation request with a projection that retains only the current
plan and style guide in the Blueprint view. The exact draft, current obligations,
identity/viewpoint context, empty initial Bible, review policy and model settings
remain unchanged. See the
[comparison report](../docs/benchmark_reports/broader-context-comparison-2026-10-09.md).

- [x] Freeze three paired seeds for the original overrun and one pair each for
  inconclusive investigation, authorized verification and a missing turn.
- [x] Verify the Blueprint-only reduction, exact source inputs and unchanged
  schema/current obligations/evidence; retain the overrun route in both conditions.
- [x] Run the twelve approved probes once; all validate on their first calls.
- [x] Verify request/response/source hashes and exact materialization replay;
  pass 36 focused probe/endpoint tests.
- [ ] Demonstrate faithful endpoint enforcement and full-story recovery.

The original passes with `no_overrun` for all three seeds in both conditions.
Every reduced-context original review recognizes completed verification; one
restates the assigned decision-to-verify outcome as verification itself. The
inconclusive and authorized controls pass, while the missing turn correctly
blocks independently. All boundary statuses are no-overrun, so the legitimate
controls do not establish discrimination. Broad plot allegations also persist.

The omitted guidance is not necessary for the observed failure under the
no-reservation condition. This does not establish that context never influences
judgment. The next target is explicit terminal-state interpretation: a synthetic
plan control stating that no handwriting match is established by scene end,
compared with the existing wording and authorized verification. That stronger
instruction has not been tested or adopted in production.

Each reduced request removes 7,521 characters and 1,520 reported input tokens.
Total usage was 114,884 input / 8,325 output tokens, estimated at USD 0.01941376
using recorded October 8 rates against the approved USD 0.15744 allocation.
Actual charges remain unknown. Production code, canonical stories, sealed
benchmarks and historical results are unchanged; no writer or full-story calls
occurred. Full application gates were not repeated for this diagnostic/docs change.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Explicit unresolved endpoint comparison completed 2026-10-09

**Diagnostic comparison COMPLETE — explicit endpoint detected; stabilization IN PROGRESS.**
Production remains prompt v39 / graph v9. Twelve approved isolated probes retain
standard story context and the later-scene reservation. The same original draft
is reviewed under three outcome wordings at three seeds: original decision,
explicitly unverified at scene end, and authorized verification. Three further
probes cover inconclusive investigation under the first two wordings and a
missing required turn under the explicit endpoint. See the
[comparison report](../docs/benchmark_reports/explicit-endpoint-comparison-2026-10-09.md).

- [x] Freeze the twelve requests and rotated condition order before inference;
  validate synthetic plan/Blueprint/Bible lineage and all outcome copies.
- [x] Verify only outcome wording and associated version references differ;
  preserve exact drafts, evidence, broader context, schema and settings.
- [x] Run all twelve approved probes once; all validate on their first calls.
- [x] Verify request/response/source hashes and exact materialization replay;
  pass 36 focused probe/endpoint tests.
- [ ] Consolidate duplicate overrun findings without losing independent issues.
- [ ] Demonstrate actual writer repair, broader endpoint reliability and
  full-story recovery before technical acceptance.

The explicit no-match endpoint produces REVISE / overrun for all three original
draft seeds, using the same exact conclusive-match evidence. Original decision
wording and explicit permission to verify both produce PASS / no-overrun, 3/3.
Inconclusive investigation passes under both tested wordings; the missing turn
correctly blocks independently. These are normalized critic verdicts, not
executed writer revisions. Enforcement of the original implicit boundary remains
unresolved; the positive result applies to a stronger synthetic instruction.

Each positive response reports the same overrun through both boundary and
assignment routes, producing two blocking outcome issues. This needs a focused
normalization fix before testing the full repair loop. Repair advice about a
suspected forgery also needs scrutiny: uncertainty about authorship does not
erase an already established match. The proposed planning owner is the existing
Blueprint integrator, with coherence checked by the Blueprint critic and exact
approved endpoints shared by writer and critic; that planning change is not
implemented here. Useful story context remains intact.

Usage was 126,270 input / 8,853 output tokens, estimated at USD 0.021219 using
recorded October 8 rates, within the approved USD 0.15744 allocation estimate.
Actual charges remain unknown. Production source, canonical stories, sealed
benchmarks and historical results are unchanged. No writer or full-story calls
occurred; full application gates were not repeated for this diagnostic/docs change.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

20. [ ] **Tune prompts and graph routing** based on blind human preference—not isolated attractive examples.

21. [ ] **Package the stable system with Tauri** and test crash/restart, offline, missing-model, invalid-key, provider-timeout, and low-disk-space behavior.

22. [ ] **Consider broader formats and hosted features only after the core is proven:** songs, poems, video scripts, collaboration, or hosted accounts.
