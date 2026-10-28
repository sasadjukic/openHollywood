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

### Consolidated overrun reporting and writer repair completed 2026-10-09

**Current-review consolidation and bounded experiment COMPLETE — stabilization IN PROGRESS.**
New executions use production contract v40 / graph v9. Boundary and assignment
reports with the same anchor and exact evidence-handle set become one blocking
issue, preserving both explanations and repairs. Independent anchors/evidence,
craft/POV blockers and malformed-response validation remain intact. No new model
call, instruction, schema, migration or revision allowance is added. See
[ADR 0024](../docs/adr/0024-consolidated-scene-overrun-reporting.md) and the
[implementation/live report](../docs/benchmark_reports/consolidated-overrun-writer-repair-2026-10-09.md).

- [x] Consolidate the observed current boundary/assignment duplicate route without
  losing either assessment or bypassing validation.
- [x] Replay all twelve saved reviews: three duplicate pairs consolidate;
  nine other results remain exactly equal.
- [x] Add 13 regression cases including persisted shared writer/critic repair
  tests and replay; pass full Python/frontend quality gates.
- [x] Run three explicitly approved isolated writer/critic pairs and an
  unchanged-draft control; audit exact requests, responses and artifact lineage.
- [x] Inspect full revised prose and preserve exact diffs, distinguishing model
  verdicts from observed changes.
- [ ] Address overlap between current findings and unmet historical repair tests
  without erasing independent obligations or source-test identity.
- [ ] Establish broader endpoint reliability, full-story recovery, technical
  repeatability, preference and cost acceptance before closing Step 19.

Two revisions clearly leave the match unresolved and pass; the third keeps
apparent identity and forgery doubts entangled and requires revision. The control
correctly rejects unchanged prose. All three writers validate on their first
calls; two critics need one structural retry for mistyped evidence handles.
Seven probes use nine calls. Each writer changes four relevant paragraphs and
preserves nine exactly, including the warning and ten-year-future realization.
No second writer revision, continuity or full-story run occurs. The explicit
endpoint remains a synthetic plan, not an automatic Blueprint-generation change.

The two blocked live reviews confirm current-route consolidation but expose
another duplicate path: an unmet historical repair is appended beside a current
finding, with different evidence sets. This is recorded for follow-up; duplicate
reporting is not claimed solved throughout the revision loop. The remaining
semantic target is a clear distinction between an unestablished handwriting
match and uncertain authorship of a likeness already recognized as matching.

Verification: Ruff, strict mypy (172 files), all 710 Python tests, frontend
format/lint/types, 11 frontend tests and production build. The initial full Python
run had one SQLite-lock worker failure; the five worker tests and a second full
suite passed unchanged. The live estimate is USD 0.01559182 for 85,693 input /
8,987 output tokens, within the approved 14-call / USD 0.09184 allocation.
Actual charges remain unknown. Canonical stories, sealed benchmarks and prior
evidence are unchanged.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Linked historical repair findings evaluated 2026-10-09

**Fixed diagnostic COMPLETE — candidate verification and stabilization IN PROGRESS.**
Production contract v41 / graph v9 adds explicit current-finding links to existing
repair checks. Valid links retain the original claim, repair and test identity
with current evidence. Independent findings and distinct original IDs remain;
invalid or partial links cannot bypass response validation. Current wording is
preserved in the audit. No new role, call, canonical schema or migration is added.
See [ADR 0025](../docs/adr/0025-linked-historical-repair-findings.md) and the
[v41 report](../docs/benchmark_reports/linked-repair-findings-v41-2026-10-09.md).

- [x] Implement explicit provenance links, guarded consolidation and shared audit
  evidence without fuzzy matching or category-only suppression.
- [x] Add and pass 28 regression cases, including two persisted revisions and
  replay; pass lint/types and frontend quality gates.
- [x] Replay four prior responses with explicitly labeled manual link annotations;
  preserve verdicts and original targets. These are offline wiring tests.
- [x] Run the approved five critic probes once; replay every valid/failed response
  and verify frozen requests, evidence and original repair lineage.
- [ ] Resolve invalid links on satisfied repairs, then qualify the revised protocol.
- [ ] Resolve the recurring worker shutdown test failure and pass the full Python
  gate before merging the candidate or running further cloud probes.
- [ ] Establish reliable independent reporting of the missing-turn control and
  resolve unstable match-versus-authorship interpretation.
- [ ] Establish broader technical repeatability, full-story recovery, preference
  and cost acceptance before closing Step 19.

The unchanged draft now reports its two original obligations once each. Four
probes validate on their first calls. Revision 19102 instead fails both attempts
because met checks link nonexistent current findings; its proposed PASS is not
accepted. Revision 19103 passes. The ambiguous 19104 revision changes from v40's
REVISE to PASS without prose changes. The missing-turn control requires revision
but notices the omitted turn only in assessment text, reopens the old outcome
repair and creates no independent turn target. That control fails its intended
expectation; no emitted turn finding was removed by consolidation.

The six calls consume 71,252 input / 6,353 output tokens, estimated at USD
0.01251648 using recorded October 8 rates, within the approved ten-call /
USD 0.06560 allocation. Actual charges remain unknown. No writer, canonical
change or full-story run occurs. The source snapshot and prior evidence retain
their frozen hashes. The initial 732-test suite, Ruff, strict mypy (173 files),
frontend format/lint/types, 11 frontend tests and production build pass. Deterministic
checks do not establish the critic's semantic reliability. Final code review also
adds complete issue-field validation before linked craft findings can be removed;
six new cases reproduce then verify that correction. The tested executor is
archived, the final hash is recorded separately, and all saved responses replay
identically under the correction without additional cloud calls.

Final validation also exposes an intermittent worker shutdown failure, with an
invocation remaining marked running. The worker group reproduces it once, then
passes unchanged; a limited in-memory HEAD-source comparison also passes. Its
cause remains unestablished, and no worker change is included in this slice.
Both final full 738-test runs report 737 passed / 1 failed on that same shutdown
assertion. The full gate remains failed; this candidate is not marked ready to
merge. Worker cleanup is the immediate offline stabilization target.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Worker cleanup and critic v42 implemented 2026-10-09

**Local implementation, verification and fixed diagnostic COMPLETE — reviewer qualification IN PROGRESS.**
Production contract v42 / graph v9 gives satisfied repair checks an empty-link
schema alternative and requires independent assignment defects to be reported
separately. Original repair identity and guarded consolidation remain intact.
The recurring worker failure is reproduced by delaying cancellation persistence:
the graph wrapper previously returned before its specialist's cleanup finished.
Workflow-scoped task tracking and protected persistence now join that work before
closure. See [ADR 0026](../docs/adr/0026-durable-worker-cancellation-cleanup.md),
[ADR 0027](../docs/adr/0027-satisfied-repair-schema-and-independent-findings.md),
and the [v42 report](../docs/benchmark_reports/worker-cleanup-critic-v42-2026-10-09.md).

- [x] Reproduce the cleanup ordering locally and verify that repeated cancellation
  cannot end stop before the gated persistence operation finishes.
- [x] Cover Blueprint worker stop/restart, real production-service cleanup,
  graph/leaf cancellation, failure propagation and concurrent-workflow isolation.
- [x] Reproduce the separate SQLite stop-command lock failure; move generic
  control-store writes off the event loop and test real checkpoint contention,
  post-commit worker notification and idempotency for all four mutations.
- [x] Encode met checks with empty links while retaining invalid-response rejection.
- [x] Verify an independent turn reaches the next writer and critic with its own
  source-bound test, whether the original outcome repair is met or unmet.
- [x] Replay all six saved v41 raw responses unchanged: four identical valid
  critiques and the same two rejected attempts.
- [x] Freeze the same five diagnostic cases with exact source/request/code hashes,
  unchanged inputs/settings and a ten-call / USD 0.06560 maximum rate estimate.
- [x] Pass all 758 Python tests, Ruff lint/format, strict mypy (177 files),
  frontend format/lint/types, 11 frontend tests and production build.
- [x] Run the approved five probes in six calls; reconstruct every request and
  replay every valid/failed response and its audit exactly.
- [x] Observe valid satisfied checks and independent missing-turn reporting on
  their frozen controls, keeping the original outcome repair met.
- [ ] Resolve incompatible links from original repairs and duplicate reporting
  of the new turn as a generic plot blocker; qualify the same controls again.
- [ ] Resolve the ambiguous match-versus-authorship judgment and broader reviewer
  reliability; the unchanged negative control remains a failed review.
- [ ] Establish broader technical repeatability, full-story recovery, preference
  and cost acceptance before closing Step 19.

Four live probes validate on their first calls. The unchanged draft fails both
attempts because its major tension repair links a blocking outcome finding also
claimed by the original outcome repair. The missing-turn control now preserves
the repaired outcome and reports the new turn separately, but adds a second
generic plot blocker for the same defect; offline reconstruction yields two new
repair tests. Saved repair 19102 passes with empty met links, where v41 failed
twice. Repairs 19103 and 19104 also pass; the latter's semantic ambiguity remains.

The six calls use 72,298 input / 6,296 output tokens, estimated at USD 0.01264012
against the approved USD 0.06560 allocation at recorded October 8 rates. Actual
charges remain unknown. No writer call or full-story run occurs. Diagnostics
retain the synthetic explicit endpoint; canonical stories, sealed benchmarks and
prior evidence remain unchanged. No role, inference allowance, canonical field
or migration is added. Worker verification is complete for the tested local
paths; narrative reviewer qualification remains open.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Eligible repair links and assignment restatements v43: 2026-10-10

Implementation, local verification and the approved diagnostic are **COMPLETE**;
live reviewer qualification remains **IN PROGRESS**. Production contract v43 / graph v9 constrains
eligible original-repair links before inference and adds an explicit reference
for generic issues that repeat current assignment findings. See
[ADR 0028](../docs/adr/0028-eligible-repair-links-and-assignment-restatements.md) and
the [v43 report](../docs/benchmark_reports/eligible-repair-links-v43-2026-10-10.md).

- [x] Bind eligible links by original category/severity and populated current
  assignment, including boundary fallback and satisfied empty-link checks.
- [x] Keep runtime existence, category/severity, ownership and complete-route
  validation; preserve original repair IDs and independent defects.
- [x] Validate explicit generic assignment repetitions before combining them;
  preserve their descriptions, evidence and advice in one assignment finding.
- [x] Retain bounded, redacted repetition audits and rejection evidence.
- [x] Add 26 local cases, including persisted writer/critic repair propagation.
- [x] Replay all six unmodified v42 responses; label protocol annotations
  separately and verify one new turn target from an explicit restatement.
- [x] Freeze five requests with identical source inputs/settings, unchanged
  system instructions, and a ten-call / USD 0.06560 maximum rate estimate.
- [x] Pass all 784 Python tests, Ruff lint/format, strict mypy (178 files),
  frontend format/lint/types, 11 frontend tests and production build.
- [x] Run the five revised probes with explicit approval; inspect raw responses,
  validation, canonical findings and resulting repair identities.
- [x] Observe one independent turn repair on the missing-turn control, while
  retaining its satisfied original outcome repair and empty links.
- [ ] Resolve invalid restatement metadata, incomplete consolidated-route links
  and exact-category drift on the unchanged control; qualify it again.
- [ ] Resolve remaining semantic ambiguity and establish broader repeatability,
  full-story recovery, preference and cost acceptance.

Six approved calls yield four valid reviews and one failed probe. The missing
turn is now reported only through its dedicated route and creates one new repair
target; this live case avoids duplication rather than exercising non-null
consolidation. Three saved revisions pass with empty met links; the ambiguous
match/authorship interpretation remains unresolved. The unchanged draft fails
both attempts on an invalid generic assignment reference. Manual counterfactuals
also expose a severity mismatch, omitted boundary link and category spelling
drift. These annotations do not convert the live failure into a pass.

Every request, response, validation result and audit reconstructs exactly. The
six calls use 73,892 input / 6,363 output tokens, estimated at USD 0.01289008 within
the approved USD 0.06560 allocation at recorded October 8 rates. Actual charges
remain unknown. There are no writer calls or full-story runs. Source database,
canonical stories and sealed benchmarks are unchanged. No role, inference
allowance, canonical schema field or migration is added.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Severity-bound restatements and precise critic retries v44: 2026-10-10

Implementation, local verification and the approved five-probe campaign are
**COMPLETE**; reviewer qualification remains open. Production contract v44 /
graph v9 adds severity
branches for generic restatement references and precise structural metadata for
the existing critic retry. See
[ADR 0029](../docs/adr/0029-severity-bound-restatements-and-precise-retries.md) and
the [v44 report](../docs/benchmark_reports/restatement-retries-v44-2026-10-10.md).

- [x] Require null restatement references for nonblocking issues in schema and
  materialization; retain explicit valid blocking repetitions.
- [x] Provide candidate-bound allowed references, original category/severity,
  complete/missing routes and competing owners without rejected allegations.
- [x] Collect independent link errors after rejection without repairing or
  accepting the rejected response; keep existing limits and fallback guidance.
- [x] Add 22 regressions, including persisted retry with unchanged candidate,
  input artifacts and writer count.
- [x] Replay six unmodified v43 responses: four identical valid critiques and
  two rejected responses producing precise offline retry packets.
- [x] Freeze five requests with identical inputs/settings and a ten-call /
  USD 0.06560 maximum recorded-rate estimate; initial schema growth is 162 chars.
- [x] Pass all 806 Python tests, Ruff lint/format, strict mypy (180 files),
  frontend format/lint/types, 11 frontend tests and production build. Record the
  initial Vitest worker startup timeout and unchanged isolated passing rerun.
- [x] Run all five explicitly approved probes: eight calls, four valid reviews,
  one failed unchanged control; 100,171 input / 8,463 output tokens,
  USD 0.01740914 at recorded rates; actual charges unknown.
- [x] Reconstruct every request and response, verify original repair lineage and
  unchanged frozen hashes, and retain failures plus labeled offline diagnostics.
- [x] Record that both missing boundary links were corrected, but the unchanged
  retry introduced an invalid reference and the ambiguous revision retained a
  generic pacing duplicate despite structural recovery.
- [ ] Distinguish repeated assignment allegations from independent craft claims
  without treating null or category/severity differences as proof of independence.
- [ ] Establish reviewer reliability, resolve semantic ambiguity and demonstrate
  full-story recovery, preference and cost acceptance before closing Step 19.

No writer call, canonical edit, migration, new specialist or inference allowance
is introduced. Story context and system instructions remain unchanged. Structural
hints are not manuscript evidence and do not establish narrative equivalence.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Explicit assignment versus craft comparison v45: 2026-10-10

Implementation, local verification and the approved diagnostic campaign are
**COMPLETE**; semantic qualification remains outstanding. Production contract v45 / graph v9 requires
an explicit comparison for generic critic issues and permits declared repetitions
at any severity. See [ADR 0030](../docs/adr/0030-explicit-assignment-and-craft-comparison.md)
and the [v45 report](../docs/benchmark_reports/claim-comparison-v45-2026-10-10.md).

- [x] Require current finding references and an explanation of the same defect
  or the distinct craft problem remaining after a minimal assignment correction.
- [x] Validate comparison coverage and preserve original repair identities;
  retain declared repetitions without promoting independent craft severity.
- [x] Persist bounded/redacted comparisons in invocation audits, with precise
  structural retry guidance that excludes rejected review prose.
- [x] Add 23 regressions, including two persisted workflows with one new
  assignment repair and one independent craft repair passed to writer and critic.
- [x] Replay eight saved v44 responses and two labeled offline annotations;
  three valid reviews are unchanged, and the duplicate-bearing response now
  requires the comparison. Edited responses are not live model successes.
- [x] Freeze the same five private requests/settings at ten calls maximum and
  USD 0.06560 recorded-rate estimate; initial schema growth is 1,242 characters.
- [x] Pass all 829 Python tests, Ruff lint/format, strict mypy (182 files), frontend
  formatting/lint/types, 11 frontend tests and production build. The first full
  run's old v40 fixture was corrected to supply required comparison coverage;
  no production validation was weakened.
- [x] Run the five explicitly approved probes: six calls, four valid reviews,
  one failed unchanged control; 75,950 input / 6,581 output tokens and
  USD 0.0132654 recorded-rate estimate; actual charges unknown.
- [x] Reconstruct all requests and responses, verify frozen hashes and original
  repair lineage, and retain the first-response/retry classification change.
- [x] Compare the missing-turn control with accepted repair 19103: identical
  verification text and noncandidate inputs/settings, but an extra outcome
  complaint. Preserve this contextual variation without claiming its cause.
- [ ] Stabilize claim classification through structural repair; no successfully
  validated generic comparison occurred in this campaign.
- [ ] Investigate the additional decision-to-verify complaint separately from
  generic craft deduplication.
- [ ] Qualify model accuracy, broader recovery, human preference and cost
  acceptance before closing Step 19.

No new role, writer change, extra call allowance, canonical field or migration
is introduced. Comparison text is a model judgment, not verified story truth.
**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Preserve critic classification during structural repair v46: 2026-10-10

Implementation, all local verification and the approved diagnostic campaign are
**COMPLETE**; reviewer qualification remains open. Production contract v46 / graph v9,
critic retry policy 13. See [ADR 0031](../docs/adr/0031-preserve-critic-classification-during-structural-repair.md)
and the [v46 report](../docs/benchmark_reports/retry-classification-v46-2026-10-10.md).

- [x] Retain valid classification choices with candidate/task binding and bounded
  category, severity and exact current evidence metadata; exclude rejected prose.
- [x] Reject changed classifications, missing complaints and duplicate counts
  while allowing reordered issues and evidence. Preserve counts for complaints
  sharing metadata without claiming semantic identity.
- [x] Cover materialization and later domain-validation failures; preserve
  original repair IDs and current-finding validation without an extra model call.
- [x] Add 33 regressions, including a persisted structural retry on the same draft
  with the same original repair tests and writer count.
- [x] Replay six saved v45 outputs: four valid results unchanged, both failures
  retained. Reject the manually coverage-corrected retry's classification drift;
  accept the manually format-corrected first response with no new repair target.
- [x] Verify all five initial messages/settings unchanged and freeze three
  retry-only requests at three calls maximum / USD 0.01968 recorded-rate estimate.
- [x] Pass all 862 Python tests, Ruff lint/format, strict mypy (184 files), frontend
  formatting/lint/types, all 11 frontend tests, production build and diff checks.
- [x] Run the three explicitly approved private retries: 3/3 preserve classification,
  repair comparison structure and complete the boundary/outcome links. All three
  still fail after newly linking the original tension repair to a generic issue
  that has been consolidated. No valid live review is claimed.
- [x] Inspect each raw claim/comparison, verify all frozen hashes and isolate the
  remaining error in three labeled offline copies. Changing only the ineligible
  link to [] preserves both original repair IDs and introduces zero new targets.
- [x] Record three calls, 41,832 input / 4,225 output tokens and USD 0.00754648
  recorded-rate estimate; actual charges remain unknown. No writer or canonical edits.
- [ ] Distinguish retained raw complaints from separately linkable current findings
  before emission; exclude consolidated repetitions from original craft links.
- [ ] Qualify semantic accuracy and investigate the separate decision-to-verify
  complaint before claiming wider critic reliability.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Independent craft owns original repair links v47: 2026-10-10

**IN PROGRESS**: implementation and required local quality checks complete.
All three live retries exclude the invalid link; two fully validate, and one
retains a comparison-format failure. Production contract v47 / graph v9,
critic retry policy 14. See [ADR 0032](../docs/adr/0032-independent-craft-owns-original-repair-links.md)
and the [v47 report](../docs/benchmark_reports/independent-repair-links-v47-2026-10-10.md).

- [x] Permit original craft IDs only on independent issues with exact original
  category/severity; require empty craft-check link arrays and reject legacy indexes.
- [x] Validate explicit ownership and translate it to internal routes without
  merging original IDs, dropping obligations or weakening evidence validation.
- [x] Preserve classification during retries; provide eligible ID hints and
  separate wire/effective links in audits, without replaying rejected prose.
- [x] Add 22 regressions, including durable writer/critic propagation of the same
  two originals with independent craft and a consolidated assignment repetition.
- [x] Replay three v46 failures unchanged and reproduce their three labeled
  one-field counterfactuals without changing canonical outcomes.
- [x] Prepare three matching controlled retries: same saved failure, inputs,
  settings and seeds; maximum three calls / USD 0.01968 recorded-rate estimate.
- [x] Pass required quality gates: 884 Python tests, 11 frontend tests, Ruff,
  strict mypy, frontend formatting/lint/types and production build.
- [x] Obtain explicit approval, run exactly three private retries and inspect
  both structure and claims: classification and link exclusion hold in 3/3;
  2/3 validate with the same two originals and zero new targets. Recorded-rate
  estimate USD 0.00770396; actual charges unknown.
- [x] Isolate the remaining comparison-format failure locally: wrapping only its
  existing comparison text and reference validates with the same original tests.
  The actual response stays failed; no additional model attempt is granted.
- [x] Strengthen exact comparison-object instructions in v48 and qualify the
  remaining failure on the same three controlled retries: all validate without
  relaxing validation or classification (see the v48 record below).
- [ ] Qualify broader reviewer accuracy and investigate the separate
  decision-to-verify complaint before closing Step 19.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Explicit comparison retry shape v48: 2026-10-10

**Focused change COMPLETE**: implementation, required local quality checks and
three approved controlled retries complete. All three validate; broader Step 19
qualification remains IN PROGRESS. Production contract v48 / graph v9, critic
retry policy 15. See the [v48 report](../docs/benchmark_reports/comparison-shape-v48-2026-10-10.md).

- [x] State both required comparison fields, object shape and bounds in the
  targeted retry directive, deriving structure from the existing schema.
- [x] Preserve comparison semantics, classification, original repair links and
  existing call allowances without replaying rejected prose or changing schemas.
- [x] Add eight regressions, including two persisted retries retaining independent
  craft and consolidated assignment complaints without extra writer work.
- [x] Replay all three v47 responses with unchanged outcomes and verify the prior
  labeled offline correction produces the same canonical result.
- [x] Prepare the same three saved-first-failure retries: only comparison guidance
  and policy version change, maximum three calls / USD 0.01968 estimated.
- [x] Pass required quality gates: 892 Python tests, 11 frontend tests, Ruff,
  strict mypy, frontend formatting/lint/types and production build.
- [x] Obtain explicit approval and run exactly three retries: all return valid
  comparison objects, retain classification, exclude invalid craft links and
  preserve exactly two original repairs with no new target. Inspect the claims
  and replay all responses without edits; verify frozen evidence and database.
- [x] Record 43,581 input / 4,244 output tokens, USD 0.00779894 estimated at the
  recorded October 8 rates; actual charges remain unknown.
- [ ] Qualify broader reliability and the separate decision-to-verify complaint
  before closing Step 19.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Decision versus inconclusive attempt investigation: 2026-10-10

**Focused investigation COMPLETE**: historical inspection and twelve approved
probes complete; production follow-up remains. Production v48 / graph v9 unchanged.
See the [investigation report](../docs/benchmark_reports/decision-vs-attempt-v48-2026-10-10.md).

- [x] Verify identical handwriting verification passages and shared noncandidate
  context/settings in the v45 repaired draft and missing-turn control.
- [x] Inspect ten saved v41–v45 responses: the repaired draft passes throughout;
  extra outcome allegations on the control vary and concern different defects.
- [x] Separate the actual outcome requirement from the critic's additional demand
  for a future decision to verify; retain uncertainty about its cause.
- [x] Prepare date-present/absent crossed with implicit, explicit prior decision
  and explicit future decision, at two paired seeds: twelve probes, maximum
  24 calls / USD 0.15744 recorded-rate estimate.
- [x] Verify exact synthetic edits, unchanged verification prose, shared context,
  original repair identity and four unchanged historical response replays.
- [x] Execute the approved fixed comparison: twelve first-call valid responses,
  six correct future-date passes; two unmodified missing-turn revisions (one with
  an extra outcome complaint); four incorrect missing-turn passes after explicit
  decision sentences. Original no-match repair remains met in all cases.
- [x] Inspect claim text and exact source evidence; record partial recurrence of
  the extra-demand pattern with a changed rationale, not a stable future-decision
  requirement. Verify all receipts, canonical replays, audits and frozen inputs.
- [x] Record 148,812 input / 11,062 output tokens, USD 0.02525848 estimated at
  recorded October 8 rates; actual charges unknown, no writer or production changes.
- [x] Select the next focused candidate: separate evidence-backed turning-point
  and outcome checks within the existing critic, with consistent blocker routing.
- [x] Implement that candidate without requiring explicit decision prose; see v49
  below. Live semantic qualification remains open.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Independent mandatory scene checks v49: 2026-10-11

**Focused implementation and controlled probes COMPLETE; semantic qualification
remains IN PROGRESS.** Production prompt v49 / graph v9, critic retry policy 16. See
[ADR 0033](../docs/adr/0033-independent-mandatory-scene-checks.md) and the
[v49 report](../docs/benchmark_reports/mandatory-assignment-checks-v49-2026-10-11.md).

- [x] Require independent evidence-backed met/unmet checks for each populated
  current turning point and outcome; preserve action-based evidence of intent.
- [x] Route unmet checks into existing blocking assignment findings regardless
  of other satisfied checks, scores or historical repairs.
- [x] Preserve boundary consolidation, generic craft comparisons and original
  repair identity. Reject duplicate legacy reporting of the two mandatory anchors.
- [x] Reject malformed checks as review errors; retain the existing call limits,
  precise structural retries and bounded/redacted diagnostic evidence.
- [x] Pass 34 new local regressions including durable writer-versus-review retry
  behavior; explicitly port existing synthetic fixtures to the new wire contract.
- [x] Pass all required checks: 926 Python tests, 11 frontend tests, Ruff,
  strict mypy (189 files), frontend formatting/lint/types and production build.
- [x] Prepare the exact twelve v48 date/decision cases with unchanged artifacts,
  context, settings and budgets. Pin all requests, sources and candidate code.
  Twelve saved raw reviews correctly fail the new wire contract; four labeled
  human-authored annotations test deterministic blocker routing only.
- [x] Execute the twelve approved probes in 15 calls: 9/12 first-attempt valid,
  all twelve valid after three bounded structural retries. Verify exact request
  replays, output materialization, audits, original repair lineage and source hashes.
- [x] Record six correct future-date passes, two turn-only control revisions and
  four unchanged false passes now explicitly marking the turn met. The prior extra
  outcome complaint does not recur; all original no-match repairs remain met.
- [x] Record 199,327 input / 19,501 output tokens, USD 0.03570618 estimated at
  recorded October 8 rates, within the USD 0.15744 approval; actual charges unknown.
  No writer calls, full-story runs or canonical changes.
- [x] Implement a stricter full-proposition meaning of met while preserving
  indirect/action-based realization; v50 below completes the controlled test.
- [ ] Qualify independent semantic judgments before making broader reliability
  claims. Full-story repeatability, preference and cost acceptance remain open.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Complete assigned fact means met v50: 2026-10-11

**Focused implementation and frozen comparison COMPLETE; broader qualification
IN PROGRESS.** Production prompt v50 / graph v9, critic retry policy 17. See the
[v50 report](../docs/benchmark_reports/complete-assigned-fact-v50-2026-10-11.md).

- [x] Define met as the complete assigned fact/state, including every explicit
  condition. A similar dramatic function or broad premise cannot replace a
  missing or contradictory required fact.
- [x] Preserve action-based evidence, embodied reactions and indirect narration;
  do not demand literal plan wording, explicit decision sentences or new conditions.
- [x] Deliver the rule through the existing critic assessment and structural
  retry paths. Keep schema, runtime validation, writer instructions and budgets.
- [x] Pass eight focused prompt-delivery/retry regressions; replay all fifteen
  saved v49 responses with twelve identical accepted results and three identical
  rejections. The four semantic false passes remain unchanged in this offline replay.
- [x] Pass all required checks: 934 Python tests, 11 frontend tests, Ruff,
  strict mypy (190 files), frontend formatting/lint/types and production build.
- [x] Prepare twelve matching v49 cases with identical input artifacts, settings,
  budgets and first user messages/output schemas. Pin code, source and request hashes.
- [x] Obtain explicit approval and complete twelve probes in 16 calls; all final
  results valid, eight on the first attempt. Correct all four v49 false passes:
  six missing-date controls each produce one turning-point blocker; six positive
  drafts remain accepted. All twelve outcomes and original no-match repairs stay
  met, including action-based decisions in the four implicit cases.
- [x] Inspect all final evidence and four rejected first responses; replay all
  sixteen responses and verify frozen requests, sources, code and database.
  Two first responses still select met despite acknowledging the wrong fact;
  structural retries recover them. Two other retries repair comparison objects
  while preserving valid classification and consolidating duplicate complaints.
  First-response validity is 8/12 versus v49's 9/12: no structural reliability claim.
- [x] Record 216,532 input / 21,654 output tokens and USD 0.03897608 at recorded
  October 8 rates, below the USD 0.15744 cap. Actual charges remain unknown.
  No writer calls, full-story runs or canonical changes.
- [ ] Qualify transfer to a separate scene with complete indirect/action-based
  fulfillment, a similar dramatic effect with a wrong/missing fact, and a genuinely
  missing decision. The comparison below qualifies these distinctions on one new
  scene with v50 unchanged; broader semantic and Step 19 acceptance remain open.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Assignment transfer with unchanged v50: 2026-10-11

**Bounded comparison COMPLETE; broader qualification IN PROGRESS.** See the
[transfer report](../docs/benchmark_reports/assignment-transfer-v50-2026-10-11.md).

- [x] Select OH-V01-001 scene 1's existing approved touch-plus-psychic-pull turning
  point and decision-to-enter outcome. Preserve all source context and production
  prompt v50 / graph v9 / critic retry policy 17.
- [x] Prepare four diagnostic variants: touch present/absent crossed with an entry
  decision shown through action or an explicitly unresolved choice. Preserve the
  same indirect psychic pull and other prose between paired conditions. Include
  the both-missing case to test independent reporting.
- [x] Freeze twelve requests at three paired seeds with opaque draft identifiers,
  exact source lineage, no condition/expectation labels in model messages and no
  synthetic plan or repair history. Verify reconstruction and hashes locally;
  all eight existing v50 delivery/retry regressions pass.
- [x] Obtain explicit approval and complete twelve probes in 21 calls. All first
  mandatory check pairs match the inspected facts; all twelve final reviews are
  valid and correct on those checks. Six valid indirect turns and six action-based
  decisions are accepted; six missing touches and six missing decisions are found.
  Both-missing cases retain two independent blockers; no extra repair targets.
- [x] Inspect all passages and nine failed first responses. All negative reviews
  repeat a complaint with a comparison string instead of the required object;
  only 3/12 complete first responses validate. All retries preserve the native
  checks and valid classification and consolidate repeated complaints. The first
  schema already supplies the object; this is not missing schema delivery.
- [x] Replay all 21 responses and reconstruct requests; verify exact source/code
  and database hashes. Record 275,139 input / 24,356 output tokens and
  USD 0.04826186 at recorded October 8 rates, below the USD 0.15744 cap. Actual
  charges unknown. No production changes, writer/full-story calls or canonical changes.
- [x] Test a compact first-review comparison-object clarification while retaining
  v50 met semantics and existing schema/consolidation. Implementation and matched
  results follow below: v51 validates all twelve first responses. Separately retain
  the concern about repair advice demanding immediate causality or completed entry
  beyond the literal assigned minimum.
- [ ] Establish broader reliability; this one-scene transfer does not qualify
  other models, writer repairs, full-story repeatability, preference or cost acceptance.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### First-review comparison-object clarification v51: 2026-10-11

**Local implementation and bounded comparison COMPLETE; broader qualification
IN PROGRESS.** See the
[implementation and comparison report](../docs/benchmark_reports/first-review-comparison-v51-2026-10-11.md).

- [x] Add the successful comparison-object shape clarification to normal critic
  instructions for local/cloud original and revision reviews. Share the wording
  with the existing retry directive without changing that directive's output.
  Prompt v51 / graph v9 / critic retry policy 17.
- [x] Preserve the exact v50 obligation module, schemas, validation, classification
  retention, duplicate consolidation, repair links and writer contract.
- [x] Replay all 21 sealed v50 responses: twelve identical canonical results and
  nine identical structural rejections, including matching evidence/classification
  audits and retry packets. Verify all 116 sealed evidence-file hashes.
- [x] Freeze the same twelve transfer cases, source artifact versions, seeds,
  order, settings and budgets. Only the 291-character system clarification differs
  in model-facing requests; all first user messages and schemas remain identical.
- [x] Complete local checks: 937 tests pass in the full Python run and the sole
  obsolete prompt-size guard passes after its explicit allowance update. All 938
  collected tests are covered. The 54 focused regressions, Ruff, strict mypy,
  frontend formatting/lint/type checks, 11 frontend tests and production build pass.
- [x] Obtain explicit approval and complete twelve probes in twelve calls, with
  all first responses valid versus v50's 3/12. All nine generic repetitions now
  contain the correct object immediately; none requires a retry.
- [x] Inspect all checks, evidence, generic comparisons and repairs. Native check
  pairs and repair-target counts remain unchanged in all twelve cases: indirect
  fulfillment remains valid and missing touch/decision facts remain separate
  blockers. No extra craft/boundary finding or repair target. Record changed
  generic labels/links in three both-missing fresh reviews without claiming all
  review text or reasoning is identical.
- [x] Replay every new response and reconstruct its request; verify frozen code,
  source, prior evidence and database hashes. Record 150,528 input / 13,881 output
  tokens and USD 0.02662632 at recorded October 8 rates, below the USD 0.15744 cap.
  Actual charges unknown. No writer/full-story calls or canonical changes.
- [ ] Address stronger-than-assigned repair advice separately: immediate causal
  touch triggers and completed entry are prescribed beyond the explicit minimum.
  The focused v52 comparison follows below; its instruction does not resolve
  the repair-scope defect.
  Broader models, writer repair, full-story, preference and cost acceptance remain open.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Minimum assignment repairs v52: 2026-10-11

**Local implementation and bounded comparison COMPLETE; repair-scope remedy
NOT QUALIFIED.** See the
[implementation and diagnostic report](../docs/benchmark_reports/minimum-assignment-repairs-v52-2026-10-11.md).

- [x] Add an instruction constraining current assignment assessments, native repairs
  and repeated generic complaints to the missing assigned fact. Preserve fulfilled
  facts and the current endpoint; do not invent causal order, immediacy or completed action. Retain
  explicit applicable assignment/canonical requirements. Keep optional suggestions
  outside mandatory repair text and acceptance conditions.
- [x] Preserve the v50/v51 definition of met and v51 comparison-object clarification.
  Prompt v52 / graph v9 / critic retry policy 17. No schema, validator, consolidation,
  historical repair-test, writer-contract or call-allowance change.
- [x] Preserve the uncommitted v51 baseline and replay its twelve responses to
  identical canonical results and audits. Verify prior sealed evidence and source
  database hashes; past stronger-than-assigned advice is not rewritten.
- [x] Freeze twelve probes: six cases at two seeds. Match four requests to v51's
  complete/both-missing baselines. Add pull-before-touch and settled-decision-outside
  positives, plus same-draft controls with one explicit causality or completed-entry
  requirement. Keep synthetic plans outside canon and preserve coherent lineage.
- [x] Complete full local checks: 946 Python tests, 29 focused regressions, Ruff,
  strict mypy across 192 files, frontend formatting/lint/type checks, 11 frontend
  tests and production build pass.
- [x] Obtain explicit approval and complete twelve probes in twelve calls, all
  first responses valid, with no retries. All eight generic complaints supply valid
  comparison objects and consolidate; no independent craft or boundary blocker.
- [x] Inspect all checks, cited passages, plans, generic complaints and complete
  repairs. Native check pairs match the inspected assignments in 10/12 reviews;
  both pull-before-touch positives gain unsupported causal blockers. Decision-only
  and explicit completed-entry controls are distinguished correctly at both seeds.
- [x] Record the unresolved primary target: neither matched both-missing review
  keeps complete advice within scope. Both touch repairs still prescribe causality;
  one generic complaint still prescribes crossing the threshold. Native baseline
  pairs remain unchanged from v51. Ten repair targets are reported where eight are
  supported; the two extra targets are native false findings, not duplicates.
- [x] Replay all twelve raw responses and reconstruct requests. Verify and seal
  frozen code, sources, prior evidence and database hashes. Record 153,616 input /
  13,206 output tokens and USD 0.02678864 at recorded October 8 rates, below the
  USD 0.15744 cap. Actual charges unknown. No writer/full-story calls or canonical
  changes. New controls have no historical v51 live arm; their failures do not
  establish a regression caused by v52.
- [ ] Test support in the assignment or applicable canon for claimed temporal,
  causal and completion requirements before treating them as mandatory. Retain
  action/indirect fulfillment. This next focused remedy is not implemented or
  qualified; broader reliability, preference and cost acceptance remain open.
- [x] Record the user's observation that v50/v51 charges appear below estimates as
  qualitative billing evidence awaiting more monitoring. Keep estimates, actual
  charges and broader cost acceptance separate; retain current reference ceilings.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Source-backed assignment requirements v53: 2026-10-11

**Local implementation and bounded comparison COMPLETE; remedy NOT QUALIFIED.**
See the [implementation and diagnostic report](../docs/benchmark_reports/requirement-basis-v53-2026-10-11.md).

- [x] Add a critic instruction requiring the assignment field or canonical artifact
  version/field, exact source words and applicability before treating causal,
  temporal or completion relations as mandatory. Carry only supported requirements
  into judgments and native/repeated repair advice. Retain action and indirect
  narration as valid fulfillment evidence; source quotation is not a prose test.
- [x] Preserve the exact met/minimum-repair rules, comparison-object clarification,
  schemas, validators, consolidation, writer contract and retry policy 17. Prompt
  v53 / graph v9. Support is a model instruction, not a semantic guarantee enforced
  by the application; false or inapplicable quotations still require inspection.
- [x] Pass 42 focused regressions, Ruff formatting/lint and strict mypy across 193
  files. Replay all twelve v52 responses to identical canonical results/audits;
  retain all 97 sealed v52 evidence files, its report and source database hashes.
- [x] Freeze sixteen probes at two seeds: twelve matched v52 requests and four
  new controls isolating explicit noncausal order or a synthetic applicable Bible
  rule. Verify exact paired drafts, single-clause context changes, schemas,
  coherent artifact lineage and canon-rule delivery. No canonical writes.
- [x] Complete the full Python suite: 954 tests pass. Required frontend
  formatting/lint/type checks, 11 frontend tests, production build and
  `git diff --check` also pass.
- [x] Obtain explicit approval and complete sixteen probes in sixteen calls, all
  first responses valid. All thirteen generic comparisons validate and consolidate;
  no independent craft, viewpoint or boundary blocker and no structural retries.
- [x] Inspect all 32 native checks, source claims, draft evidence and complete
  repairs. All twelve matched v52 status pairs are unchanged. Both unsupported
  causal blockers persist despite quoting the correct conjunction; neither
  both-missing repair set stays within the assigned minimum. Native decision
  repairs remain appropriate, and the unconditional completed-entry demand does
  not recur; avoid treating that wording difference as broad qualification.
- [x] Inspect new controls separately: both order-only repairs avoid demanding
  causation. Both canon-control verdicts are correct, but neither quotes/identifies
  the exact supporting Bible version/rule. One mentions its field only in generic
  advice and permits an insufficient intensification alternative in the native
  repair. Correct verdicts do not prove correct grounding or sufficient advice.
- [x] Replay all sixteen responses and reconstruct requests; verify and seal
  frozen code, source database, prior evidence and inputs. Record 206,870 input /
  18,707 output tokens and USD 0.03644460 at recorded October 8 rates, below the
  USD 0.20992 cap. Actual charges unknown. No writer/full-story calls or canonical
  changes. Four new controls have no historical v52 live arm.
- [x] Hold v53 stable and isolate assignment wording: original conjunction versus
  separately expressed facts and explicitly unassigned relationships, retaining
  explicit-relation and indirect-fulfillment controls. The subsequent approved
  diagnostic is completed in the section below. Source quotation alone does not
  prove entailment; broader reliability remains unqualified.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Assignment wording comparison under stable v53: 2026-10-11

**Preparation, local verification and bounded comparison COMPLETE; remedy NOT QUALIFIED.**
See the [diagnostic results and frozen design](../docs/benchmark_reports/assignment-wording-v53-2026-10-11.md).

- [x] Keep production prompt v53, graph v9, critic retry policy 17 and all runtime
  code unchanged. Verify the sealed v53 code hashes at current merge `f5a665b`.
- [x] Freeze a three-wording comparison: original conjunction, separate fact
  statements and an explicit clarification that the turning point imposes no
  order/causal relation while applicable canon still binds. Change only the
  synthetic turning-point fields and coherent artifact lineage, outside canon.
- [x] Prepare 24 probes at two paired seeds: three wordings crossed with the
  pull-before-touch, both-missing and valid action-decision drafts (18), plus
  explicit cause, order-only and applicable-canon controls (6). Ten requests match
  prior v53 requests exactly; fourteen are new. Preserve system messages, schemas,
  drafts, settings, budgets and all unrelated model context.
- [x] Replay all sixteen saved v53 responses with identical requests, results and
  audits. Verify all 108 sealed evidence files, prior report and source database.
  Pass 20 relevant offline regressions and `git diff --check`. The prior full v53
  build checks remain recorded evidence; no new full-suite run is claimed.
- [x] Obtain explicit approval bound to the frozen plan and complete 24 probes in
  25 calls, below the 48-call ceiling. Record 324,585 input / 30,306 output tokens
  and USD 0.05756430 at recorded October 8 rates, below the USD 0.31488 cap. Actual
  charges unknown. No writer/full-story calls or canonical changes.
- [x] Inspect all final native checks, generic complaints and complete repairs,
  plus the one rejected first response. All ten historical matched status pairs
  remain unchanged. Original and separate wordings both falsely block the valid
  pull-before-touch draft at both seeds; clarification produces one correct
  assignment judgment out of two. That review still returns revise for a minor
  craft issue; no pull-before-touch review cleanly passes. Overall 19/24 native
  pairs match the inspected obligations, with five false assignment blockers.
- [x] Retain correct two-blocker detection in all six both-missing cases, but record
  that all six consolidated repair sets add an unsupported temporal/causal demand.
  One clarified native touch repair is minimal while its generic restatement
  reintroduces a trigger. Decision repairs remain within scope; no unconditional
  completed-entry requirement recurs. All six action-decision baselines pass.
- [x] Inspect all six explicit cause/order/canon controls: correct statuses and
  appropriate relation-specific repairs. Both canon controls now cite and quote
  the real Bible clause and require first-onset causation, but neither supplies
  its artifact-version ID. Better source grounding does not qualify the remedy.
- [x] Record 23 first-valid and 24 final-valid reviews. The single retry fixes a
  reference to a nonexistent assignment finding, preserving met/met and minor
  independent classification. Its advice loses the Optional label; revise was
  already present. All 23 final comparison objects validate: 22 consolidate,
  one remains minor craft. The 23 mandatory repair targets include five false
  native blockers; none is an extra duplicate. Verify response replay, source
  hashes and local evidence closure. No new full-suite run is claimed.
- [x] Test the symmetric compliance/craft boundary inside the existing critic:
  established assigned facts and supported relationships suffice for met; a
  preferred dramatic mechanism must not turn them into unmet. Keep optional
  craft advice out of mandatory repairs and inspect verdict/routing as well as
  classification. Preserve genuine omissions, explicit relations, applicable
  canon and indirect fulfillment. The implementation and bounded comparison are
  completed below, with partial improvement and two order-control regressions;
  the remedy and broader acceptance remain unqualified.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Fulfilled assignments, optional craft and verdicts v54: 2026-10-11

**Implementation, local verification and bounded comparison COMPLETE; remedy NOT QUALIFIED.**
See the [implementation and diagnostic results](../docs/benchmark_reports/compliance-craft-v54-2026-10-11.md).

- [x] Add a focused rule to the existing critic: complete assigned facts and
  supported conditions require met; a preferred dramatic mechanism cannot create
  a missing obligation. Optional craft preferences stay out of mandatory native
  and repeated repairs, retain explicit optional scope through retries, and
  alone do not justify revise/reject. Genuine craft defects remain eligible.
- [x] Preserve exact v50-v53 rules, schemas, validators, consolidation, writer
  contract and graph routing. Prompt v54 / graph v9 / critic retry policy 17.
  This is model guidance, not a semantic validator or automatic verdict rewrite.
- [x] Pass 32 focused regressions, including twelve new delivery/retry/durable
  routing cases. Optional pass avoids revision; genuine craft and unmet assignment
  defects retain repair targets. Optional revise still reaches the writer despite
  zero mandatory targets, so diagnostics must inspect the verdict too.
- [x] Pass Python lint/format, strict mypy across 194 files, frontend format/lint/
  type checks, eleven frontend tests and the production build. Update the existing
  instruction-size test to separately cap the new rule at 1,400 characters while
  preserving the old limit; its focused rerun passes.
- [x] Complete the full Python run: 965 pass and one instruction-size test fails
  before its addition-aware update. That corrected test passes separately (1/1),
  covering all 966 cases across the two runs with no unresolved failure. No second
  clean full-suite execution is claimed. No production code changed after the
  full run started. Final `git diff --check` passes.
- [x] Replay all 25 previous responses to identical canonical results/audits or
  validation failures. Preserve 159 sealed prior evidence files, the previous
  report and source database. Freeze 24 matched wording probes at the same two
  seeds; only the 1,393-character system addition and invocation metadata change.
- [x] Obtain approval bound to the frozen plan and complete 24 probes in 25 calls,
  below the 48-call ceiling. Record 329,887 input / 30,351 output tokens and
  USD 0.05832458 at recorded October 8 rates, below the USD 0.31488 cap. Actual
  charges unknown. No writer/full-story calls or canonical changes.
- [x] Inspect all native checks, full generic/consolidated advice, summaries,
  scores and verdicts, including the rejected first response. Five false blockers
  persist. One clarified met/met review now retains Optional minor advice and
  passes, but its summary still calls the turn partially met. All six complete
  baselines pass and all six missing-fact cases retain their two blockers; all six
  native touch repairs and complete repair sets exceed the assigned minimum.
  Decision repairs do not demand unconditional completed entry.
- [x] Record the explicit-order regression: both controls acknowledge the draft's
  reversed chronology yet mark met/met and pass. Correct native pairs decline
  from 19/24 to 17/24; 22 matched pairs remain unchanged. Explicit causation and
  applicable canon still block correctly at both seeds. Canon reviews quote the
  actual Bible clause but omit its artifact-version ID; consolidated advice
  restores causal onset more clearly than the native after-touch wording alone.
- [x] Verify 23 first-valid and 24 final-valid reviews. The one canon retry repairs
  incomplete evidence IDs, retaining native statuses and raw reject; existing
  mandatory-check materialization produces revise. Optional-label retry behavior
  is not exercised live. All 21 generic comparisons validate: twenty consolidate
  and one remains minor craft. The 21 mandatory targets include five false
  blockers. Two fewer targets than v53 reflect missed real order violations,
  not fewer false complaints. Replay saved responses and seal source/evidence
  hashes. Local simulated craft routing is not live craft or story qualification.
- [x] Hold implementation fixed and isolate temporal order from causal permission:
  compare order alone, order plus a no-causation clause, and separately stated
  relationship conditions, with valid/reversed order and unconstrained-facts
  controls. The approved diagnostic is completed in the next section. A paired
  wording effect is observed, with repair-scope and repeatability limits.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Temporal order and causal permission under stable v54: 2026-10-12

**Preparation, approved comparison and evidence review COMPLETE; remedy NOT QUALIFIED.**
See the [comparison results and frozen design](../docs/benchmark_reports/order-causation-v54-2026-10-12.md).

- [x] Keep production v54 / graph v9 / critic retry policy 17 and runtime sources
  unchanged at merge `f891bb7`. This is a controlled diagnostic, not a new prompt
  rule or semantic validator.
- [x] Prepare sixteen paired cases: four wordings (order alone, order plus the
  original causal waiver, separately stated relationship conditions, unconstrained
  facts) crossed with reversed order or touch before delayed pull, at two seeds.
  The new ordered draft changes only two paragraphs; the entry decision remains
  action-based. A full minute without pull rules out immediate onset, not every
  possible delayed causal link.
- [x] Add four controls: the delayed draft under an explicit immediate-cause plan
  and the saved both-missing draft under unconstrained facts, each at both seeds.
  Twenty total probes, six exact historical v54 requests and fourteen new requests.
  Reverse execution order at the second seed; do not rerun valid judgments.
- [x] Verify all 161 sealed prior evidence files, prior report and source database.
  Replay 25 v54 responses to identical requests, results/audits or validation
  failure. Verify paired payload isolation, coherent synthetic artifact lineage,
  unchanged system/settings/budgets and exclusion of expected labels from requests.
- [x] Pass sixteen existing critic/probe regressions, `git diff --check` and
  UTF-8/LF checks. Preserve the prior full v54 quality-gate record; no new full-suite
  or frontend build run is claimed for this diagnostic-only change.
- [x] Obtain explicit approval bound to the plan and complete all twenty probes
  in twenty calls with no retries. Record 265,530 input / 22,791 output tokens and
  USD 0.04629060 at recorded October 8 rates, below the USD 0.26240 ceiling. Actual
  charges unknown. No writer/full-story, production or canonical changes.
- [x] Inspect all forty native checks, twelve generic complaints, full repairs,
  summaries, scores and verdicts. At both seeds, order alone blocks reversed
  chronology, the original causal waiver causes a false pass, and separately
  stating order/causation restores the correct blocker. All eight ordered core
  cases pass. Both immediate-cause controls and both missing-fact controls block
  correctly. Overall 16/20 native pairs and all twenty outcome checks are correct;
  this differs from the previous matrix and is not an accuracy-improvement claim.
- [x] Record remaining scope failures: both order-only full repairs invent
  causation; both unconstrained reversed-draft reviews falsely require dramatic
  linkage; both missing-touch repairs add timing/trigger demands. One immediate-
  cause repair offers onset upon release, weakening its timing guarantee. Both
  separated-relationship repairs permit noncausal order. Twelve generic reports
  consolidate into twelve native targets (ten real obligations, two false
  blockers) without duplicates. Correct detection does not qualify all advice.
- [x] Compare all six exact historical requests: five native pairs/verdicts repeat,
  but the previous seed-19103 optional pass becomes a false blocker under unchanged
  requests/settings and recorded model digest. No retry explains this variation.
  Replay all twenty responses and verify/seal production, source and evidence
  hashes. The result supports a wording-associated scoping failure in this case,
  not a general internal-mechanism or reliability claim.
- [x] Test a compact replacement for the critic relationship guidance: distinguish
  required facts, temporal and causal relations; apply each permission only to
  its named relation and carry those limits into repairs. Preserve complete-fact
  met, applicable canon and indirect evidence. Reuse the frozen matrix before
  claiming improvement. The implementation and approved comparison are completed
  below, with partial improvement but remaining judgment and repair failures.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Separate facts, order and causation in critic guidance v55: 2026-10-12

**Implementation, local verification and approved comparison COMPLETE; remedy NOT QUALIFIED.**
See the [implementation and comparison results](../docs/benchmark_reports/relationship-scope-v55-2026-10-12.md).

- [x] Replace the existing source-basis and minimum-repair rules: assess facts,
  temporal order/immediacy and causation separately; scope each permission to
  its named relationship. Optional causation preserves required order; order
  alone does not require causation. Carry these distinctions into native and
  repeated repair advice without adding timing, triggers or completed action.
- [x] Preserve complete-fact met, applicable canon, actions/indirect narration
  and optional-versus-independent-craft guidance. The two rules shrink from
  1,446 to 1,345 characters including their separator. Prompt v55 / graph v9 /
  critic retry policy 17; no new output fields, validators or workflow changes.
- [x] Pass 41 focused regressions and all 966 Python tests; pass Ruff, strict
  mypy, frontend formatting/lint/type checks, all 11 frontend tests and build.
  Existing tests exercise instruction delivery, retries and durable routing;
  these local checks do not establish live semantic improvement.
- [x] Verify all 133 sealed prior evidence files, source report and source
  database. Replay twenty saved v54 responses to identical canonical results
  and audits. Verify that only the two rule constants and prompt version change
  in runtime code; all twenty frozen inputs, payloads, schemas, settings, budgets
  and seeds match the prior matrix apart from the system-guidance replacement.
- [x] Freeze twenty matched probes: sixteen core wording/draft cases and four
  immediate-cause/missing-fact controls, at seeds 19101/19103. Preserve the case
  order and existing one-retry bound. Maximum forty calls / USD 0.26240 at recorded
  October 8 rates; actual charges unknown. Zero model calls during preparation.
- [x] Obtain explicit approval and complete all twenty probes in twenty-one calls.
  Nineteen first reviews and all twenty final reviews validate. Record 279,680
  input / 26,322 output tokens and USD 0.049684 at recorded October 8 rates, below
  the USD 0.26240 ceiling; actual charges unknown. No writer/full-story calls or
  canonical writes. Production and frozen inputs stay fixed throughout execution.
- [x] Inspect all responses and replay all twenty-one results/failures and audits.
  Both causal-waiver false passes become correct blockers on first review.
  Native pairs improve from 16/20 to 18/20 first and 19/20 final; all twenty outcome
  checks remain correct. The extra gain follows a 631-character assessment's
  structural retry, which changes unmet/revise to met/pass. The other unconstrained
  case retains its false blocker. All eight ordered core cases and four controls
  preserve correct native checks; no general reliability claim follows.
- [x] Record repair failures separately: both order-only reviews invent a trigger;
  one separated-relationship repair adds immediacy; both missing-touch repairs
  add order. A minor tentative craft suggestion enters a blocking repair without
  explicit Optional scope. The remaining false blocker also creates an unnecessary
  repair. Both immediate-cause repairs now preserve onset at contact. Eleven
  generic reports consolidate into thirteen native targets (twelve real, one
  false), without duplicates; full advice and summaries remain unqualified.
- [x] Verify and seal frozen code, source database, prior evidence and current
  requests/results. Keep local full-suite/build evidence distinct from limited
  live semantic findings. Step 19 acceptance remains incomplete.
- [x] Keep v55 fact checks stable and compare each mandatory repair and
  linked restatement against the exact supported requirement it repairs. Preserve
  optional craft suggestions outside blockers; test saved-response/local cases
  before a bounded live comparison. Track the remaining false blocker and retry
  drift separately. The v56 instruction-only experiment completed but regressed
  to 17/20 correct native pairs versus v55's 19/20 final. Its candidate was rejected;
  the operator retained v55 on main. This completes the experiment, not the remedy.
  No writer, full-story or cross-provider qualification yet.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Inspectable assignment repair conditions v57: 2026-10-12

**Implementation, local verification and approved comparison COMPLETE; candidate NOT QUALIFIED.**
See [ADR 0034](../docs/adr/0034-traceable-assignment-repair-conditions.md) and the
[implementation and comparison results](../docs/benchmark_reports/repair-condition-sources-v57-2026-10-12.md).

- [x] Start from retained v55 at `d6834f0`, keeping its complete-fact, relationship,
  minimum-repair and optional-craft rules unchanged. Require condition records
  for every model-written native assignment repair and linked generic addition,
  including minor restatements. Preserve independent craft's existing route.
- [x] Validate exact repair-text coverage, current source membership, exact quotes
  and bounded structure. Resolve source references to immutable artifact versions
  and original paths despite context filtering. Retain redacted records in audit
  schema 5 and bounded failure evidence. Prompt v57 / graph v9 / critic retry
  policy 18; no new inference pass, retry allowance, writer behavior or migration.
- [x] Pass 32 new tests, all 998 Python tests, Ruff, strict mypy across 197 files,
  frontend formatting/lint/type checks, all 11 frontend tests and build. Explicitly
  port historical simulated fixtures; no production auto-annotation fallback.
  Demonstrate that a source-valid but unsupported repair remains structurally
  valid: traceability does not establish entailment or atomic decomposition.
- [x] Verify all 136 v55 and 133 v56 sealed evidence files and the source database.
  Replay all 41 saved responses locally. Explicit test-only annotations preserve
  forty prior canonical results, including semantic errors, and the known prior
  structural failure. Do not count simulated citations as model evidence.
- [x] Freeze twenty matched v55 cases at seeds 19101/19103. Inputs, settings,
  budgets and order match exactly; new requests differ only by condition guidance,
  source catalog and output schema. Maximum forty calls / USD 0.26240 at recorded
  October 8 rates, actual charges unknown. Zero model calls during preparation.
- [x] Obtain explicit permission and complete twenty probes in thirty calls:
  589,000 input / 37,691 output tokens, USD 0.0975364 at recorded October 8 rates,
  actual charges unknown. No valid-response reruns, writer/full-story calls or
  canonical writes. Replay all thirty unmodified responses and verify frozen
  code, database and source evidence.
- [x] Inspect every condition, cited source and separate advice. All forty first
  and last native check pairs match inspected facts, including rejected responses.
  Only ten no-repair reviews validate; all ten repair-bearing reviews exhaust
  retry because condition text differs from the separate recommendation. All 41
  citations resolve, but 24 native texts mismatch and two generic additions lack
  records. Four final raw reviews retain unsupported causal/order demands; one
  also gains completed-entry advice on retry. No nonempty condition review was
  accepted, so neither usable repair delivery nor semantic improvement is qualified.
- [x] Record structural failure separately from correct raw detection, inspect
  summaries/scores and stable check/verdict labels, and seal evidence. Keep main
  at v55. Canon and independent-craft source behavior remain local-test evidence.
- [ ] Next, test one authored source of mandatory assignment repair advice:
  render canonical recommendations from the structured conditions, covering native
  and linked generic routes and rejecting conflicting extra advice. Preserve v55
  obligation semantics and independent craft. Prove deterministic coverage locally
  before a bounded live comparison; source support still needs semantic testing.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Rendered assignment repair advice v58: 2026-10-13

**Implementation, local verification and approved comparison COMPLETE;
candidate NOT QUALIFIED.** See
[ADR 0035](../docs/adr/0035-rendered-assignment-repair-advice.md) and the
[implementation and test report](../docs/benchmark_reports/rendered-repair-advice-v58-2026-10-13.md).

- [x] Start from retained v55 production plus documentation at `1cd2d53` on
  `codex/critic-rendered-repair-advice`; leave main at v55. Preserve the meaning
  of met, relationship scope, optional craft and actions/indirect evidence.
- [x] Make conditions the sole model-authored assignment repair advice. Validate
  coverage and citations, require null native/linked advice fields, render exact
  joined conditions and reject competing text. Keep existing consolidation,
  writer targets and historical advice. Record rendered origin in audit schema 6.
  Prompt v58 / graph v9 / critic retry policy 19; no added inference or migration.
- [x] Pass 44 new tests, 101 affected regressions and all 1,010 Python tests.
  Ruff, strict mypy across 197 files, frontend format/lint/type checks, all eleven
  frontend tests and production build pass. Preserve the deliberate source-valid
  but semantically unsupported counterexample; tests do not establish entailment.
- [x] Verify 300 sealed v55/v57 files and both reports/database. Replay all thirty
  saved v57 responses: ten unchanged no-repair passes, twenty extra-advice
  rejections. Explicit null-only counterfactual copies yield 28 passes and two
  missing-record failures; these are not new model evidence or semantic approval.
- [x] Freeze twenty exactly matched cases, seeds, settings, budgets and order;
  maximum forty calls / USD 0.26240 at recorded October 8 rates. Zero model calls.
- [x] Record explicit operator approval bound to the final plan hash. Two launch
  attempts fail before execution due to automatic review timeout/capacity; after
  operator retry guidance, the third launch passes review. No check is bypassed.
- [x] Complete twenty probes in twenty-two calls: 428,184 input / 27,168 output
  tokens, USD 0.07081296 at recorded rates; actual charges unknown. Eighteen first
  reviews validate, including eight native repairs. All first/final native pairs
  match the twenty controls; both missing-facts controls exhaust their retry.
- [x] Inspect all 25 conditions/citations and accepted advice. All sources resolve;
  no extra mandatory causal/order/entry demands appear in the conditions. Rationale
  still uses unsupported causal language in four order-only cases. No linked
  generic repair is accepted live; that route remains unqualified.
- [x] Isolate the two first failures locally: copying native records into missing
  linked-issue records makes both explicit counterfactuals validate, while
  duplicating rendered advice. Originals remain unchanged and are not counted as
  successes. Replay all twenty-two raw responses, verify frozen evidence and seal
  the report. Keep main at v55; full-story/preference/cost acceptance stays open.
- [ ] Next, test one condition set per consolidated finding, with declared
  restatements reusing that authority. Keep additional conditions inspectable in
  the authoritative set and preserve independent craft; no silent repair fallback.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Shared assignment repair conditions v59: 2026-10-13

**Implementation, local verification, offline replay and approved comparison COMPLETE;
focused shared-condition contract PASSES this matrix; writer/broader qualification OPEN.** See
[ADR 0036](../docs/adr/0036-shared-consolidated-repair-conditions.md) and the
[implementation report](../docs/benchmark_reports/shared-repair-conditions-v59-2026-10-13.md).

- [x] Start from `8939848` on `codex/critic-shared-repair-conditions`, retaining
  main's v55 production. Recover the previous candidate's rendering and test
  infrastructure, then make each native finding own one condition set. Keep
  complete-fact fulfillment, actions/indirect evidence and independent craft.
- [x] Require linked generic advice to stay null and reuse the exact validated
  finding recommendation. Reject separate issue records/advice, absent owners
  and missing native coverage. Preserve repeated descriptions/evidence; append
  no repeated repair text. Extra conditions belong in the native source-cited set.
- [x] Resolve boundary/native aliases with the existing exact consolidation
  validators. Boundary-only restatements reuse application policy. Preserve
  historical repairs and retry classification. Audit schema 7 records owner refs
  and boundary policy; prompt 59 / graph 9 / critic retry 20. No new calls or migration.
- [x] Pass Ruff and strict mypy across 198 files, frontend checks, eleven tests
  and production build. Full Python run: 1,025 passed, one outdated boundary
  advice assertion failed. Correct that test-only expectation; all 86 affected
  v43/v58/v59 tests pass afterward. Sixteen new v59 cases and the adapted durable
  mock workflow cover shared repairs. No full-suite rerun after the test-only fix.
- [x] Verify 443 sealed prior files and the source database. Replay 22 unmodified
  v58 responses: eighteen first reviews keep identical results; both failed first
  reviews now produce two exact single-copy repairs; the two saved retries remain
  invalid for separate advice or incomplete independent-craft comparison.
- [x] Freeze twenty matched cases. Drafts, context, settings, budgets and seeds
  are identical; the only first-request difference from v58 is condition guidance.
  Maximum forty calls / USD 0.26240 at recorded October 8 rates; actual charges
  unknown. Preparation and offline replay make zero model calls.
- [x] Obtain explicit permission and complete twenty probes in 21 calls: nineteen
  first reviews and all twenty final reviews validate; all first/final native
  check pairs match the controls. One 601-character assessment passes after the
  existing bounded retry. Four generic repetitions share native sets; both
  missing-facts controls produce two blockers each. No duplicate repair text.
- [x] Inspect all 25 citations and conditions, twelve final native sets, computed
  writer targets and explanatory prose. Source identity resolves and no unassigned
  mandatory condition appears in rendered repairs. Causal language still occurs
  in explanations; atomic cause/timing and downstream writer behavior remain open.
- [x] Reconstruct and replay all requests/responses unchanged, verify frozen code
  and source database, and seal evidence. Usage: 407,609 input / 25,902 output
  tokens; USD 0.06742606 at recorded rates, actual charges unknown. No writer,
  full-story or canonical changes; main remains v55.
- [x] Complete the fixed-v59 writer repair test below with approved private
  payloads, order-only and missing-fact feedback, and required-causation controls.
  Existing facts and indirect decisions are preserved in the inspected cases;
  the test also identifies unresolved endpoint expansion in two repairs.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Fixed-v59 writer repairs: 2026-10-14

**APPROVED EXPERIMENT COMPLETE; REPAIR DELIVERY WORKS ON THESE CASES;
ENDPOINT PRESERVATION OPEN.** See the
[experiment results](../docs/benchmark_reports/writer-repairs-v59-2026-10-14.md).

- [x] Start from merged v59 at `72bed6f` on `codex/writer-repair-v59`. Keep all
  production code and the meaning of met fixed; no new schema, instruction,
  routing, retry allowance or canonical story change.
- [x] Verify 142 sealed v59 files, its report and the frozen source database;
  replay all 21 original responses unchanged. Build standard writer/critic
  requests with identical original repair tests and version-bound evidence.
- [x] Pass 34 relevant probe, repair-acceptance and v59 tests. Exercise all six
  writer requests plus retry recovery/exhaustion with nine fake responses and
  zero model calls. Check diagnostic formatting and syntax. No application changes
  require another full suite or frontend build.
- [x] Freeze six writer/critic pairs: order-only, missing-touch/decision and
  explicit immediate causation, each at two seeds. Add two unchanged-defect
  controls and one valid indirect-decision control with both feet outside.
  Maximum 30 calls / USD 0.19680 at recorded October 8 rates; actual charges unknown.
- [x] Obtain explicit permission and complete all fifteen probes in fifteen calls,
  without retries or extra requests. All six revisions validate and receive critic
  passes; eight original repairs are satisfied. All three control pairs match:
  unchanged defects remain, and a valid indirect decision outside passes.
- [x] Inspect all whole revisions, diffs and reviews. All first eight paragraphs
  and approach-to-threshold passages remain exact; four existing action endings
  and four existing pull paragraphs remain exact. No new mandatory causal or
  entry demand appears, but causal readings remain in explanatory prose.
- [x] Record the unresolved scope concern: both missing-decision writers complete
  entry, and both critics accept it despite the threshold exit state. One calls
  this the decision's logical completion. Distinguish optional writer expansion
  and permissive boundary interpretation from a mandatory entry requirement.
- [x] Reconstruct/replay all fifteen requests/responses unchanged; verify frozen
  code, database and historical evidence; seal results. Usage: 214,224 input /
  18,607 output tokens; USD 0.03743416 at recorded rates, actual charges unknown.
  No second prose revision, full-story calls, canonical or production changes.
- [x] Keep v59 fixed and compare a valid indirect decision outside with
  completed entry under the original threshold wording, explicit outside-at-end
  wording and authorized entry. Keep decision fulfillment separate from endpoint
  compliance before changing code. The completed comparison below supports a
  permissive interpretation of the original wording in these tested cases.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Fixed-v59 endpoint wording comparison: 2026-10-14

**COMPLETED; EXPLICIT ENDPOINT WORDING CHANGES THE BOUNDARY JUDGMENT.** See the
[comparison report](../docs/benchmark_reports/endpoint-wording-v59-2026-10-14.md).

- [x] Start from `c6739976` on `codex/endpoint-wording-v59`; keep production v59,
  the meaning of met, retry policy and all canonical story artifacts unchanged.
- [x] Freeze both previous missing-decision writer revisions and variants changing
  only their final entry sentence to the previously accepted outside-action ending.
  Cross all four drafts with original threshold, explicit outside-at-end and
  optional-entry wording at two paired critic seeds: twenty-four probes.
- [x] Keep the Scene Plan and embedded Blueprint plan consistent, updating only
  exit state and derived lineage. Verify wording-normalized requests are otherwise
  identical, including compaction, original repair tests and next-scene reservation.
  Reproduce two historical live requests exactly at their original seeds.
- [x] Verify 299 sealed files, both reports and the database; reconstruct/replay
  fifteen previous requests/responses unchanged. Confirm locally that a boundary
  blocker can coexist with met decision and original repair checks. Pass 45
  relevant tests and diagnostic formatting/syntax checks before cloud generation.
- [x] Declare twenty boundary controls and leave four original-wording entry
  cells descriptive. Require met decision/turning-point and original repairs
  independently of any new endpoint defect. Maximum 48 calls / USD 0.31488 at
  recorded October 8 rates; actual charges unknown.
- [x] Obtain explicit approval and run all 24 critic probes in 24 calls, with no
  structural retries. All twenty declared boundary controls match. Both entered
  drafts pass under original wording and optional entry, but require revision
  under explicit outside-at-end wording at both critic seeds. Treat the four
  original-wording entry cells as descriptive, not graded successes.
- [x] Inspect all judgments and advice: decisions, turning points and both original
  repairs remain met in 24/24; all twelve outside endings pass. Each explicit
  boundary violation produces one blocker, with no generic duplicates, reopened
  repairs or new causal/completion requirements. Raw/final verdicts agree 24/24.
  No authored condition sets were exercised in these responses.
- [x] Reconstruct/replay all requests and raw responses; verify frozen sources and
  seal evidence. Usage: 508,700 input / 34,452 output tokens; USD 0.08499880 at
  recorded rates, actual charges unknown. No writer, full-story or canonical changes.
- [x] Keep v59 fixed and test one writer/critic repair per explicit-boundary
  finding, checking outside position while preserving fulfilled facts and an
  indirect decision. Inspect prose and verdicts, with saved outside variants as
  controls. The completed experiment below supports localized boundary repair;
  preservation of an independently valid indirect expression remains open.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Fixed-v59 outside-boundary writer repairs: 2026-10-14

**COMPLETED; FOUR LOCALIZED BOUNDARY REPAIRS; INDIRECT STYLE PRESERVATION OPEN.**
See the [repair report](../docs/benchmark_reports/outside-boundary-repairs-v59-2026-10-14.md).

- [x] Start from `7adb3907` on `codex/outside-boundary-repairs-v59`; keep production
  v59, the meaning of met and canonical artifacts unchanged.
- [x] Prepare four writer/critic pairs from the four saved explicit-boundary
  findings, retaining exact canonical feedback and all three original repair
  tests. Add four controls using the saved accepted outside-decision prose under
  the same repair history. Freeze dependent critic construction from valid writer
  output only; allow one prose revision per case.
- [x] Verify 456 sealed files, source reports, database and code hashes. Reconstruct
  and replay all 24 endpoint requests/responses unchanged. Verify pair contracts,
  standard compaction and separate missing-decision versus boundary repair IDs.
- [x] Pass seven mock writer calls covering retry recovery/exhaustion and eight
  local critic fixtures separating the new boundary repair from met decisions
  and earlier repairs. No model calls or semantic success claimed.
- [x] Pass 45 relevant regression tests outside the sandbox after interrupting
  a stalled first sandboxed run; no application changes. Pass diagnostic Ruff
  checks and freeze the plan, eight initial requests and dependent critic builder.
- [x] Obtain explicit cloud approval for twelve probes, maximum 24 calls /
  USD 0.15744 at recorded October 8 rates.
  Actual charges remain unknown.
- [x] Run twelve probes in thirteen calls: four writer revisions, four follow-up
  critics and four controls. All writers preserve every word before the original
  final sentence and repair the boundary; all eight final critics pass with both
  native checks and all three repairs met. Two control reviews accept indirect
  decisions; the other two retain an explicit decision sentence.
- [x] Retain the one failed critic response: a mistyped boundary repair ID is
  rejected, then corrected by the existing structural retry. First attempts:
  11/12 valid. Native statuses, boundary and verdict do not change on retry.
- [x] Inspect prose and record the limitation: all four new endings use explicit
  decision narration. The original action partly conveyed the decision and was
  itself the overrun, so this does not isolate preservation of an independently
  valid indirect expression. No new mandatory advice or duplicate findings.
- [x] Reconstruct/replay all thirteen requests/responses, verify source/code and
  database hashes and seal evidence. Usage: 223,055 input / 18,028 output tokens;
  USD 0.03843890 at recorded rates, actual charges unknown. Production stays v59.
- [x] Keep v59 fixed and test an already accepted indirect outside decision with
  a separate forbidden-entry sentence appended. Check whether the writer removes
  only the overrun while preserving the independent decision expression. Prepare
  and approve that new matrix; the subsequent experiment below completes it.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Fixed-v59 indirect-decision preservation: 2026-10-14

**COMPLETED — BOUNDARY REPAIRED; DELETION-ONLY PRESERVATION 0/2.**
See the [preservation report](../docs/benchmark_reports/indirect-decision-preservation-v59-2026-10-14.md).

- [x] Start from `50fabff6` on `codex/indirect-decision-preservation-v59`, keeping
  production v59, the meaning of met and canonical artifacts unchanged.
- [x] Retain one previously accepted indirect outside decision verbatim and append
  a separate forbidden-entry paragraph. Freeze two seeds, each with an initial
  critic, deletion-only control, writer and post-repair critic. Keep all fresh
  canonical feedback unedited; skip dependents if the overrun is not detected.
- [x] Freeze the deletion-only primary measure and separate checks for indirect
  expression, fulfilled facts, unrelated prose, actual advice and critic verdicts.
  One prose revision per seed; no replacement cases or valid-response rerolls.
- [x] Verify 591 prior sealed files, reports, code and database; reconstruct and
  replay thirteen previous responses. Pass thirteen no-network mock calls and
  45 regression tests; diagnostic Ruff checks pass.
- [x] Freeze the plan, baseline, two initial requests and dependent construction.
  Maximum eight probes / sixteen calls / USD 0.10496 at recorded October 8 rates;
  actual charges remain unknown.
- [x] Obtain explicit approval for the new private payload set.
- [x] Run eight probes in eight calls, all valid on the first attempt; no skips.
  Both initial critics identify one boundary blocker while keeping both native
  checks and earlier repairs met. Neither asks for explicit decision narration.
- [x] Inspect both revisions: forbidden entry removed, first 4,021 characters
  preserved, including preparatory action, motivation and fulfilled facts. Both
  replace the accepted final sentence with more explicit entering intention.
  Exact deletion-only preservation succeeds 0/2; semantic repair succeeds 2/2.
- [x] Both deletion-only controls and both post-repair critics pass, with native
  checks and all three repairs met. No duplicate findings or additional mandatory
  conditions. The original indirect ending was acceptable under the same history.
- [x] Reconstruct/replay all eight requests/responses, inspect actual writer
  contracts, reverify hashes and seal evidence. Usage: 143,523 input / 11,215 output
  tokens; USD 0.02457922 at recorded rates, actual charges unknown.
- [x] Test a compact writer-only clarification to preserve already fulfilled
  expression when deletion alone fixes a separate defect. Include a genuinely
  missing-decision control; keep the critic and meaning of met unchanged. The
  current result demonstrates extra rewriting, not its isolated cause. The v60
  comparison below found no preservation improvement.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Writer preservation during minimal repair, v60: 2026-10-14

**EXPERIMENT COMPLETE — NO PRESERVATION IMPROVEMENT; NOT PROMOTED.**
See the [implementation report](../docs/benchmark_reports/writer-minimal-repair-v60-2026-10-14.md).

- [x] Start from `a01c3327` on `codex/writer-minimal-repair-v60`; main stays v59.
  Add only a 292-character writer clarification: when deletion suffices, preserve
  already fulfilled wording, including indirect expression; permit necessary repairs.
- [x] Advance shared prompt metadata to v60; keep graph v9, critic instructions,
  meaning of met, schemas, validation, compaction, budgets and retry policy unchanged.
- [x] Update three current-version test expectations and the bounded writer-length
  cap. Full suite initially passes 1,022 with four stale-expectation failures;
  all four affected modules subsequently pass 85 tests. Ruff and strict mypy pass.
- [x] Pass frontend formatting, lint, types, all 11 tests and the production build.
- [x] Verify 725 sealed files and source hashes; replay all eight previous responses.
  Confirm identical critic messages/schema/results and only the writer paragraph
  difference for the exact saved inputs, feedback and seeds.
- [x] Pass seventeen no-network mock calls for the twelve-stage matrix and bounded
  failures. Freeze two preservation pairs plus two missing-decision chains and
  unchanged controls. Maximum 24 calls / USD 0.15744 at recorded October 8 rates;
  actual charges unknown. No model calls made during preparation.
- [x] Obtain explicit approval for the frozen twelve-probe matrix.
- [x] Run all twelve probes in twelve calls: four writer and eight critic calls,
  all first-attempt valid, with no retries, skips or second prose revisions.
- [x] Inspect full prose and diffs. Deletion-only repairs remain **0/2**, matching
  v59: both remove forbidden entry but replace the accepted last sentence with an
  explicit decision. Both preserve the preceding 4,021 characters, including the
  preparatory actions, motivation and fulfilled touch/pull facts.
- [x] Both missing-decision repairs succeed outside; both initial reviews and both
  unchanged controls correctly reject indecision. All four post-reviews pass with
  native requirements and historical repairs met. Inspect four supported condition
  records and three generic restatements; consolidation retains one outcome blocker
  per negative review without adding a duplicate repair identity.
- [x] Reconstruct/replay every request/response, reverify the frozen sources and
  seal evidence. Usage: 194,332 input / 15,807 output tokens; USD 0.03352928 at the
  recorded rates. Actual charges remain unknown. Main stays v59; do not promote
  this candidate on these results. Step 19 remains IN PROGRESS.
- [x] Isolate whether the already satisfied historical missing-decision complaint
  in writer context causes the unnecessary restatement. Retain the current boundary
  and genuinely unmet obligations, and keep the critic and its review history fixed.
  This is a proposed diagnostic, not a production-history removal policy; the current
  experiment does not establish the cause. The fixed-v59 comparison below found
  no preservation improvement when this one complaint was omitted.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Satisfied decision history in writer context, fixed v59: 2026-10-14

**EXPERIMENT COMPLETE — NO PRESERVATION IMPROVEMENT; PRODUCTION V59 UNCHANGED.**
See the [diagnostic plan](../docs/benchmark_reports/writer-satisfied-history-v59-2026-10-14.md).

- [x] Start from `20280f0b` on `codex/writer-history-diagnostic-v59`. Keep all v59
  production code and both roles unchanged; do not restore the v60 writer paragraph.
- [x] Prepare paired full-history and one-item omission requests at seeds 19101/19103.
  Omit only the satisfied historical missing-decision test from the writer projection.
  Keep immutable artifacts, current boundary, other tests and assignment/canon intact.
- [x] Add two missing-decision writer controls using exact saved drafts/feedback.
  Their latest status is unmet, so the same omission procedure retains the test.
  Keep all history and tests in every post-revision critic request.
- [x] Verify 902 sealed files and unchanged v59 implementation hashes; replay eight
  saved responses. Check exact projection differences and identical paired critic
  requests for an identical candidate. Counterbalance writer condition order.
- [x] Pass nineteen no-network fixture calls including retry recovery, permanent
  failures and missing-decision rejection. Pass 45 focused regression tests, Ruff
  and strict mypy. Freeze the matrix at twelve probes / at most 24 calls and
  USD 0.15744 at recorded October 8 rates. Actual charges remain unknown.
- [x] Obtain explicit approval for this new private payload set. No model calls
  made during preparation.
- [x] Finish all twelve probes in twelve first-attempt-valid calls: six writer and
  six critic calls, with no retries, failures, skips or second prose revisions.
- [x] Compare fresh paired prose: deletion-only preservation is **0/2 with full
  history and 0/2 with omission**. All four remove entry but add or rewrite explicit
  commitment. One full-history output retains the entire accepted passage and adds
  a decision sentence; neither omitted-history output retains the whole ending.
- [x] Both missing-decision writers repair the outcome while remaining outside and
  preserving preceding paragraphs. All six full-history critics pass, with both
  native checks and all original repairs met, no overrun, new issues or conditions.
- [x] Inspect complete prose/diffs and advice, reconstruct/replay all requests and
  responses, reverify sources and seal evidence. Usage: 166,130 input / 14,648 output
  tokens; USD 0.02911740 at recorded rates, actual charges unknown. Keep v59 unchanged;
  this result does not justify filtering production history.
- [x] Test the current boundary recommendation's request to restore both outcome
  and exit state when only the outside endpoint is unmet. Compare advice confined
  to the boundary while preserving the met outcome; keep other history and critic
  fixed, and include a genuinely unmet outcome control. The comparison below finds
  no deletion-only improvement; it establishes no cause or production change.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Writer boundary-advice comparison, fixed v59: 2026-10-15

**DIAGNOSTIC COMPLETE — NO PRESERVATION IMPROVEMENT; V59 UNCHANGED.**
See the [diagnostic report](../docs/benchmark_reports/writer-boundary-advice-v59-2026-10-15.md).

- [x] Start from `e2fe1bb0` on `codex/writer-boundary-advice-v59`; keep both roles and
  all v59 production code fixed. Change only the current boundary advice prefix
  in the diagnostic writer projection; retain all claims, evidence and other advice.
- [x] Pair current and endpoint-only advice at seeds 19101/19103 using exact saved
  drafts and full feedback. Keep all original tests in every post-critic request.
- [x] Add two fresh revision-zero controls combining explicit indecision with
  involuntary crossing. Require the critic to detect both defects and expose boundary
  advice before dependent writer/post calls; preserve any native outcome repair.
- [x] Pass 23 no-network fixture calls, including separate/consolidated advice,
  retry recovery, detection/exposure gates and permanent failures. Pass 45 focused
  regressions, Ruff and strict mypy. Retain earlier fixture-assertion failures.
- [x] Freeze the fourteen-probe matrix and exact requests; verify 1,095 sealed files,
  prior reports, the source database and v59 hashes, and replay eight saved responses.
  Maximum 28 calls / USD 0.18368 at recorded October 8 rates; actual charges unknown.
- [x] Obtain explicit approval and complete all fourteen probes in fourteen calls:
  six writers and eight critics, all first-attempt valid. No retries, failures, skips
  or second prose revisions.
- [x] Compare paired prose: deletion-only preservation is **0/2 with current advice
  and 0/2 with endpoint-only advice**. All four remove entry and add explicit decision
  wording. One current-advice result retains the whole accepted passage but adds a
  decision paragraph; neither endpoint-advice result retains the complete ending.
- [x] Both mixed controls detect and repair the missing decision and forbidden entry.
  Native advice survives separately from boundary advice; generic Plot/Agency
  criticism consolidates into the native finding. All six post-critics pass with
  both native checks and every original repair met, no overrun or new conditions.
- [x] Inspect prose and advice, reconstruct/replay every request and response, reverify
  sources and seal evidence. Usage: 205,142 input / 17,933 output tokens;
  USD 0.03589308 at recorded October 8 rates, actual charges unknown. Keep v59 fixed.
- [x] Test whether a compact, draft-version-bound record of the latest review's met
  requirements and cited current passages helps the writer preserve valid expression.
  Keep genuinely unmet outcomes repairable, retain the unchanged critic, and use the
  mixed missing-decision/entry control. The comparison below improves preservation
  in both paired cases; broader transfer and production integration remain unqualified.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Writer fulfilled-evidence comparison, fixed v59: 2026-10-15

**DIAGNOSTIC COMPLETE — POSITIVE PAIRED RESULT; V59 UNCHANGED.**
See the [diagnostic report](../docs/benchmark_reports/writer-fulfilled-evidence-v59-2026-10-15.md).

- [x] Start from `54410412` on `codex/writer-fulfilled-evidence-v59`; leave production,
  critic and main at v59. Add only one diagnostic writer field; keep ordinary boundary
  advice, all original tests, claims, immutable inputs and role instructions intact.
- [x] Pair current/evidence writer context on the saved overrun at seeds 19101/19103.
  Reuse actual latest reviews and bind met checks/excerpts to exact draft and assignment
  versions. Keep post-critic requests identical for an identical candidate.
- [x] Reuse two mixed missing-decision/involuntary-entry drafts and saved initial
  reviews. Certify only their turning point; leave the missing decision and boundary
  repair obligations intact. No fresh initial critic calls are needed.
- [x] Pass 19 no-network mock calls and reject 13 invalid-provenance cases. Cover
  retries, failure skips, unchanged negative controls, necessary repairs and hook
  restoration. Retain two corrected preparation failures; no production fixes.
- [x] Pass 45 focused regressions, Ruff and strict mypy. The sandboxed test attempt
  stalled during Windows asyncio setup; the same tests pass outside the sandbox.
- [x] Verify 1,374 prior sealed files, source reports/database and v59 hashes; replay
  four saved initial reviews and freeze all six writer requests. Twelve probes,
  at most 24 calls / USD 0.15744 at recorded October 8 rates, actual charges unknown.
- [x] Obtain explicit approval for the frozen matrix and record its plan hash.
- [x] Complete all twelve probes in twelve first-attempt-valid calls: six writers and
  six critics, with no retries, failures, skipped stages or second prose revisions.
- [x] Both evidence-condition writers restore the exact accepted 720-word prose by
  deleting only the forbidden entry. Current context achieves 0/2 and rewrites the
  decision in both cases. All preceding paragraphs and other draft fields survive.
- [x] Both mixed controls repair the genuinely missing decision and remove entry.
  All six post-critics pass with native/historical checks met and no overrun or new
  conditions. Evidence-condition critics independently accept the retained indirect
  decision without receiving the added writer packet.
- [x] Inspect prose/advice, reconstruct/replay every request and response, reverify
  sources and seal evidence. Usage: 168,044 input / 14,870 output tokens;
  USD 0.02947416 at recorded rates, actual charges unknown. Keep v59 unchanged.
- [ ] Test transfer to another scene with valid indirect fulfillment and an independent
  defect, plus a genuinely unmet-requirement control. Keep this diagnostic projection
  and critic fixed. Later qualification must cover met evidence that overlaps another
  defect before production integration; no further cloud run is authorized here.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Writer fulfilled-evidence transfer, fixed v59: 2026-10-15

**DIAGNOSTIC COMPLETE — WRITER TRANSFER NOT MEASURED; INITIAL GATES FAILED.**
See the [diagnostic report](../docs/benchmark_reports/writer-evidence-transfer-v59-2026-10-15.md).

- [x] Start from `cdcc5488` on `codex/writer-evidence-transfer-v59`; keep production,
  critic and main at v59. Reuse the exact previous evidence projection and policy.
- [x] Prepare OH-V01-002's saved indirect verification passage with a separate
  forbidden match sentence. Preserve the decision outcome and move the existing
  no-match requirement to the exit state in both synthetic plan views.
- [x] Include the earlier missing-date draft with identical verification actions and
  the same overrun. Certify only its met outcome; its missing turning point must repair.
- [x] Freeze six initial requests and an 18-probe dependent protocol at two seeds:
  baseline critics, primary current/evidence pairs and unmet-requirement controls.
  Require suitable current reviews; skip failed/misclassified chains without rerolls.
- [x] Pass 24 no-network mock calls, ten invalid-provenance checks and four scheduler
  failure checks. Preserve all original advice and keep critic packets unmodified.
- [x] Pass 45 focused regressions, repository Ruff/formatting and strict mypy for
  198 source files. Verify 1,569 prior sealed files, source reports/database and v59.
- [x] Freeze the plan with maximum 36 calls / USD 0.23616 at recorded October 8 rates;
  actual charges unknown.
- [x] Obtain explicit approval and execute the bounded protocol. Six critic calls
  validate on first attempts; no retries or failures. Both baselines pass, all four
  overrun cases detect the match, and both negative controls detect the missing date.
- [x] Record that all four overrun reviews mark the already fulfilled decision unmet
  because the endpoint was exceeded. This exists in raw responses; it is not a
  validator-induced status change. All twelve writer/post-critic stages are skipped.
- [x] Replay every sent request and response; inspect actual actions, date evidence,
  advice and raw/canonical verdicts. Preserve the secondary duplicate-outcome finding
  in one review. Reverify sources and seal evidence. Usage: 115,472 input / 8,364 output
  tokens; USD 0.01951168 at recorded rates, actual charges unknown.
- [ ] Test scoped native fulfillment versus boundary compliance, retaining the valid
  decision as met while the separate exit violation remains blocking. Preserve
  genuinely unmet-fact/decision detection. Keep production v59 and the evidence
  projection fixed; writer transfer and necessary-repair success remain unmeasured.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Critic fulfillment versus endpoint compliance, fixed v59: 2026-10-15

**DIAGNOSTIC COMPLETE — NO IMPROVEMENT; PRODUCTION V59 UNCHANGED.**
See the [diagnostic report](../docs/benchmark_reports/critic-fulfillment-scope-v59-2026-10-15.md).

- [x] Start from `8f097792` on `codex/critic-fulfillment-scope-v59`. Keep production
  prompts, schemas, validators, writer and main at v59.
- [x] Prepare one diagnostic critic system-span replacement that distinguishes each
  requirement's own complete fact from a separate exit violation. Preserve indirect
  evidence, mandatory conditions within the requirement itself, and all blockers.
- [x] Pair current/scoped guidance for the six exact prior baseline, overrun and
  missing-date cases, plus a genuinely missing-decision control at both seeds.
  Sixteen independent critics; no writer or canonical changes.
- [x] Pass 19 no-network mock calls and verify all eight pairs, including structural
  retries. Replay six historical responses unchanged; do not impose desired semantics
  in validation. Verify 1,732 sealed files, reports, source database and v59 hashes.
- [x] Pass 45 focused regressions, Ruff/formatting and strict mypy for 198 source files.
- [x] Freeze sixteen requests and the protocol. Maximum 32 calls / USD 0.20992 at
  recorded October 8 rates; actual charges unknown.
- [x] Obtain explicit approval and complete sixteen probes in sixteen first-attempt-valid
  calls. No retries, failures, skipped probes, writer calls or canonical changes.
- [x] Record no primary improvement: 0/4 fulfilled decisions remain met with overrun
  in either arm. Both arms block all overruns, accept 2/2 baselines, and detect 2/2
  missing dates and 2/2 missing decisions. Current-arm disputed classifications reproduce.
- [x] Replay and inspect all requests, responses, evidence, conditions and raw/canonical
  verdicts. Record duplicate outcome/boundary complaints in four current and three
  scoped cases. Reverify sources and seal evidence. Usage: 303,296 input / 21,590 output
  tokens; USD 0.05109744 at recorded rates, actual charges unknown.
- [x] Keep production v59; do not promote the unsuccessful guidance clarification.
- [ ] Test exact-requirement binding in the diagnostic check: each unmet assessment
  must identify the failed clause of its own requirement with current-draft evidence.
  Keep endpoint blockers and both negative controls. Source validation establishes
  traceability only; semantic support and writer transfer remain unqualified.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Critic own-requirement failed clauses, fixed v59: 2026-10-15

**DIAGNOSTIC COMPLETE — PARTIAL IMPROVEMENT; PRODUCTION V59 UNCHANGED.**
See the [diagnostic report](../docs/benchmark_reports/critic-failed-clause-v59-2026-10-15.md).

- [x] Start from `d44605aa` on `codex/critic-failed-clause-v59`. Keep production
  prompts, schemas, validators, writer and main at v59.
- [x] Prepare a diagnostic-only response extension: each native check carries its
  exact assignment binding; unmet identifies its own failed clause and current-draft
  evidence. Keep the existing complete-fact meaning of met and separate endpoint blockers.
- [x] Validate source/text identity, quote membership and evidence references in an
  isolated adapter; strip only added fields before unchanged v59 materialization.
  Preserve classifications and advice even when source-valid claims lack support.
- [x] Freeze the same four drafts, both negative controls and two paired seeds under
  ordinary and diagnostic guidance. Sixteen critics, at most 32 calls / USD 0.20992
  at recorded October 8 rates; actual charges unknown.
- [x] Pass 20 no-network mock calls, 13 malformed-field rejection checks and sixteen
  historical replays. Verify all eight pairs and 1,932 prior sealed files.
- [x] Pass 45 focused regressions, Ruff/formatting and strict mypy for 198 source files.
- [x] Obtain explicit approval and complete sixteen probes in seventeen calls,
  including one structural link retry. No rerolls, writer calls or canonical changes.
- [x] Replay all seventeen responses and inspect clauses, evidence, advice and
  verdicts. Record 3/4 fulfilled decisions preserved with separate blocking overrun
  versus 0/4 current; both arms detect both negative controls and accept baselines.
- [x] Record the remaining unsupported own-clause claim: the later match is treated
  as contradicting a prior decision, importing an ending restriction. Traceability
  succeeds but does not establish semantic support. Do not promote the candidate.
- [x] Record the retry's valid links and unchanged classifications, plus its shortened
  date advice omitting explicit realization. Full writer repair remains untested.
- [x] Record 332,418 input / 24,794 output tokens, USD 0.05645612 at recorded rates,
  actual charges unknown. Reverify sources and seal results; production stays v59.
- [ ] Hold the diagnostic fixed and compare an explicit event requirement with an
  explicit terminal condition, retaining both negative controls. No further cloud
  test is authorized by this completed run.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Required event versus terminal condition, fixed v59 diagnostic: 2026-10-15

**DIAGNOSTIC COMPLETE — CLASSIFICATION CONTRAST REPRODUCED; REPAIR QUALIFICATION OPEN.**
See the [diagnostic report](../docs/benchmark_reports/critic-event-terminal-v59-2026-10-15.md).

- [x] Start from `15aedd38` on `codex/critic-event-terminal-v59`. Keep production,
  writer and main at v59. Reuse the sealed failed-clause diagnostic implementation.
- [x] Change only synthetic outcome wording and derived provenance: decision during
  the scene versus decided-but-unverified state at its end. Keep the separate
  no-match exit state, every draft and both negative controls unchanged.
- [x] Prepare four drafts × two wordings × two paired seeds. Freeze sixteen requests
  and the protocol. Maximum 32 calls / USD 0.20992 at recorded October 8 rates;
  actual charges unknown. No writer, full-story or canonical changes.
- [x] Pass 20 no-network mock calls and verify all eight pairs. Replay seventeen
  prior response attempts; verify 2,155 sealed files and unchanged critic hashes.
  Confirm source-valid semantic errors still validate rather than forcing statuses.
- [x] Pass 45 focused regressions, Ruff/formatting and strict mypy for 198 source files.
- [x] Obtain explicit approval and complete sixteen probes in eighteen calls,
  including two structural link retries. No rerolls, writer calls or canonical changes.
- [x] Replay all eighteen responses. Record the correct classification contrast in
  all four paired overruns, retained blockers, both negative controls and baselines.
  All twelve final failed-clause claims have supported sources and draft evidence.
- [x] Inspect advice and record limitations: terminal reviews do not positively
  certify the fulfilled decision; three of four final date recommendations omit
  explicit realization. One retry drops that instruction while repairing links.
  Complete prose repair remains untested; do not promote the diagnostic.
- [x] Record 363,194 input / 28,208 output tokens, USD 0.06213036 at recorded rates,
  actual charges unknown. Reverify fixed implementations and sources; seal results.
- [ ] Keep production v59 and the diagnostic fixed; resume a gated writer-evidence
  transfer test with explicit event scope and both negative controls. Check actual
  decision preservation, overrun removal and complete date-plus-realization repair.
  No additional cloud run is authorized by this completed experiment.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Gated writer evidence with explicit event scope, fixed v59: 2026-10-15

**DIAGNOSTIC COMPLETE — DELETION-ONLY PRESERVATION AND BOTH REPAIRS SUCCEEDED.**
See the [diagnostic report](../docs/benchmark_reports/writer-event-evidence-v59-2026-10-15.md).

- [x] Start from `47966236` on `codex/writer-event-evidence-v59`. Keep production
  v59, the sealed failed-clause critic diagnostic and writer evidence projection fixed.
- [x] Replay eight saved event reviews, ten historical response attempts, as gates;
  retain both missing-date and missing-decision controls and all actual advice.
- [x] Freeze eight writer requests: current/evidence preservation pairs and
  evidence-only negative controls at two seeds. Prepare dependent post-critic
  generation with complete repair history and no writer evidence packet.
- [x] Set a sixteen-probe / 32-call limit, USD 0.20992 at recorded October 8 rates;
  actual charges unknown. One prose revision per case; no full-story/canonical changes.
- [x] Pass twenty-four no-network mock calls, provenance and dependency checks;
  verify 2,398 sealed source files and unchanged implementation hashes.
- [x] Pass 45 focused regressions, Ruff/formatting and strict mypy for 198 files.
- [x] Obtain explicit approval and complete sixteen probes in sixteen calls, with
  no retries or skipped stages. Freeze every dependent critic request before sending.
- [x] Replay all sixteen responses and inspect all eight revisions/diffs. Record
  deletion-only preservation in 2/2 evidence cases versus 0/2 current cases; both
  arms retain the original decision. All six input overruns are removed and all six
  existing indirect verification passages stay verbatim.
- [x] Confirm complete date-plus-realization repair in 2/2 and genuine missing-decision
  repair in 2/2. Record the narrower saved date advice without claiming it is safe.
- [x] Confirm eight post passes, sixteen native met checks and ten historical met
  repair checks, with supported prose evidence. Record the distinction between edit
  restraint and assignment fulfillment; no blind story-quality result.
- [x] Record 212,392 input / 19,190 output tokens, USD 0.03741088 at recorded rates,
  actual charges unknown. Reverify fixed implementations and seal evidence.
- [ ] Keep production and diagnostic fixed; test the existing preservation exception
  when a cited fulfilled passage itself contains a defect requiring an edit. Retain
  a genuinely unmet control. No additional cloud run is authorized by this completion.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Writer preservation exception, fixed v59 diagnostic: 2026-10-15

**DIAGNOSTIC COMPLETE — PRESERVATION EXCEPTION SUCCEEDED; MINIMAL EDITING NOT ESTABLISHED.**
See the [diagnostic report](../docs/benchmark_reports/writer-preservation-exception-v59-2026-10-15.md).

- [x] Start from `12f8663d` on `codex/writer-preservation-exception-v59`. Keep
  production v59, the failed-clause critic diagnostic and writer evidence projection fixed.
- [x] Put the action-based decision and forbidden match in one evidence excerpt.
  Prepare a matched clean baseline and unchanged genuinely unresolved-decision control.
- [x] Freeze six initial critics at two seeds. Gate main current/evidence writer
  pairs on accepted baseline, expected classifications and an actual shared citation.
  Retain all feedback; never sanitize or fabricate the cited passage.
- [x] Bound the matrix to eighteen probes / 36 calls, USD 0.23616 at recorded
  October 8 rates; actual charges unknown. One prose revision per case; no full-story
  or canonical changes. Freeze dependent requests before sending.
- [x] Pass twenty-seven no-network mock calls, provenance and dependency checks;
  replay sixteen historical responses and verify 2,651 sealed source files.
- [x] Pass 45 focused regressions, Ruff/formatting and strict mypy for 198 files.
- [x] Obtain explicit approval and complete eighteen probes in nineteen calls,
  including one structural retry for duplicate recommendation text. All gates pass;
  no writer retry, skipped pair or semantic reroll.
- [x] Replay all nineteen responses and inspect all six full revisions/diffs. Both
  writer arms repair the shared passage and retain the decision; neither is clause-only.
  Both evidence arms preserve the original ending; current arms add verification language.
- [x] Confirm both genuinely missing decisions are repaired, all six date realizations
  remain fulfilled and all six post reviews pass. Record twelve native met checks and
  six historical met checks with supported resulting prose.
- [x] Record the initial critics' overstatement equating a match with accepting the
  warning; the explicit exit prohibition independently supports the blocker. Do not
  generalize the successful exception to all critic reasoning or minimal editing.
- [x] Record 284,316 input / 21,980 output tokens, USD 0.04859624 at recorded rates,
  actual charges unknown. Reverify fixed implementations and seal evidence.
- [x] Examine the smallest production handoff for the tested fulfillment-evidence
  packet, including current draft/assignment provenance and available validated audit
  storage. Retain mandatory repairs and the necessary-edit exception; keep the critic
  diagnostic separate. See the examination below. No integration or additional cloud
  run is authorized by completion.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Fulfillment evidence production handoff examination: 2026-10-15

**EXAMINATION COMPLETE; IMPLEMENTATION NOT STARTED.** See the
[proposed integration](../docs/handoffs/fulfillment-evidence-production-design-2026-10-15.md).

- [x] Trace the existing writer task, successful critic audit, creator/input lineage,
  request fingerprint, retry/replay and persistence paths at `fbd726c4`.
- [x] Identify an optional native-met packet requiring exact draft/plan/shared-canon
  validation, with every mandatory repair and the tested necessary-edit exception retained.
- [x] Specify persisted snapshot/digest binding before calls, including stable retries,
  source eligibility, whole-packet omission and an explicit integrity-error path.
- [x] Inspect twelve validated critic receipts (22 met and two unmet native checks),
  excluding one failed attempt. Reconstruct all six records in four saved writer
  packets exactly from their audits, assignment text and evidence catalogs.
- [x] Verify all 288 sealed experiment files and its report hash unchanged. Keep
  production v59, graph v9 and both diagnostic components fixed; make no model calls.
- [x] Define local provenance, isolation and durable SQLite tests, followed by a
  gated comparison using ordinary production critic semantics. Separate traceability
  from semantic qualification; do not promote the failed-clause diagnostic.
- [x] Implement and locally verify the small handoff slice, version its request
  identity and document the accepted implementation. Completed 2026-10-16 below.
- [ ] Qualify writer behavior with eligible ordinary critic reviews and genuinely
  unmet controls before promotion or any broader story-quality claim.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Durable writer fulfillment handoff implementation: 2026-10-16

**LOCAL IMPLEMENTATION AND VERIFICATION COMPLETE; MODEL QUALIFICATION PENDING.**
See [ADR 0037](../docs/adr/0037-durable-writer-fulfillment-handoff.md). This executes
the approved local implementation slice following the October 15 examination.

- [x] Define prompt v61 / graph v9 and policy 1, explicitly supporting ordinary
  prompt-59/61 schema-7 critics. Freeze the new version in run input and checkpoint
  state; keep existing v59 requests, retry identity and replay on their prior path.
- [x] Add a typed pure projection and exact SQLite creator/input reader. Validate
  current review/draft/plan/shared authority, both native checks and exact evidence;
  preserve the tested policy, necessary-edit exception and all mandatory feedback.
- [x] Persist included or omitted snapshots and digests before submission. Reuse
  pinned snapshots across retries/recovery; reject changed sources, corruption and
  duplicate concurrent starts without issuing another model call.
- [x] Test whole-packet omission at the inclusive 16,384-byte UTF-8 boundary and
  retain security errors instead of redacting exact quotes. Budgets are unchanged.
- [x] Pass the full Python unit/integration/workflow suite: **1,096 tests**. After
  adding the final stale-prepared-attempt guard, pass **five focused retry,
  cancellation, interruption and graph-limit checks** (66 deselected).
- [x] Pass repository Ruff lint/format and strict mypy on **201 source files**;
  compare the public OpenAPI schema unchanged and pass `pnpm build`. The handoff
  module contains 71 test cases, including exact dependency identities, failed
  critic retry selection, omission pinning, concurrent-start rejection, accepted
  prior-scene identity, UTF-8 cap boundaries and the v59 legacy request path.
- [x] Record the accepted decision in ADR 0037 and preserve the original design,
  historical experiment reports, canonical artifacts and budgets. No dependency,
  persisted table or public API schema change was needed.
- [ ] Qualify actual writer behavior using ordinary critics in a separately frozen,
  authorized comparison. Local fake-gateway checks establish no live quality result.

The failed-clause diagnostic, canonical stories and sealed experiments remain
unchanged. Independent craft findings can still require edits to fulfilled passages.
Later story-quality work requires blind human review and the accepted rubric;
preservation rate and smaller diffs are not quality scores. No live model calls.

Verification used the installed uv environment (`--no-sync --extra api`) and
workspace-local cache/test directories. Windows sandbox restrictions blocked
asyncio's loopback socket; the successful integration tests ran outside that
sandbox with fake gateways. The production build used the pinned pnpm toolchain.
Frontend source and generated API contracts are unchanged.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Ordinary-critic fulfillment comparison preparation: 2026-10-16

**PREPARATION COMPLETE; LIVE COMPARISON COMPLETED BELOW.** See the
[frozen comparison plan](../docs/benchmark_reports/production-fulfillment-v61-plan-2026-10-16.md).
This prepares step 5 following the locally verified durable handoff; it is not
a model qualification result.

- [x] Freeze prompt 61 / graph 9 / handoff policy 1 at `c1bacab638e91dadfd69016ac9226b4885e0f10f`.
  Keep ordinary critic semantics and the production fulfillment projection fixed;
  do not import the failed-clause diagnostic or change production code.
- [x] Freeze six cases across OH-V01-001/002 at seeds 19101/19103: two clean
  baselines, separate and embedded defects, missing decision, and missing future
  date plus realization. Preserve full corpus constraints and declare the fresh
  revision-zero context, corrected inherited case metadata and synthetic identities.
- [x] Freeze twelve complete initial requests, dependent request builders/gates,
  source hashes and implementation hashes. Paired writers differ only by the
  fulfillment field; retain every actual craft finding and mandatory repair.
- [x] Bound the matrix to 36 probes / 72 attempts, one structural retry per probe
  and one prose revision per arm. Reserve 1,728,000 input / 576,000 output tokens;
  USD 0.47232 is the estimate at recorded October 8 rates, not known billed cost.
  Require explicit plan-bound approval before any live calls.
- [x] Verify 483 sealed source files and their reports; pass 36 offline stage
  fixtures, four paired comparisons, twelve retry-request checks, failure gates
  and two craft-feedback checks. Verify all twelve saved requests reconstruct.
- [x] Pass 91 focused regressions, repository Ruff lint/format, strict mypy for
  201 files, and private-script formatting/syntax checks. Document decisions,
  isolated-probe limitations and later blind story-quality evaluation.
- [x] Obtain approval for plan SHA-256
  `03da1a013fc86a4a1a142d561d11fc001ab219ee252c55b64c72b4c0ed60bf18`;
  verify the recorded model digest and execute only its eligible bounded stages.
- [x] Inspect and replay every response, report eligibility coverage and writer
  outcomes separately, account for all attempts, and seal the resulting evidence.

Preparation made no live calls, canonical database writes or historical evidence edits.
The comparison measures isolated production request behavior; full durable workflow
qualification remains the separately proposed step 6. Preserving wording is not a
literary-quality acceptance gate. **Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Ordinary-critic fulfillment comparison results: 2026-10-16

**BOUNDED EXPERIMENT COMPLETE; FULL BEHAVIORAL QUALIFICATION NOT ACHIEVED.** See
the [results and inspection](../docs/benchmark_reports/production-fulfillment-v61-results-2026-10-16.md).

- [x] Record explicit approval for the frozen plan and verify the expected model
  digest. Keep prompt 61 / graph 9 / policy 1, cases, settings, ordinary critic
  semantics and production request builders unchanged.
- [x] Validate the execution ledger with 39 fake calls, including retry and permanent
  failure, replay without extra calls, call-73 rejection and unknown-outcome rejection.
  Save full requests and reserve each live attempt before dispatch.
- [x] Finish twelve initial probes in fifteen calls: eleven validated reviews, one
  terminal structural failure. Only one of four paired cases qualifies; both Elena
  embedded reviews mark the existing decision unmet, and seed-19103 Elara never
  validates. Skip all twelve dependent stages for those three pairs.
- [x] Execute the one eligible current/evidence pair and all four independently
  eligible unmet controls: six writers and six post-critics, all valid first attempt.
  Total: **24 finished probes / 27 calls**, within the 72-call ceiling.
- [x] Inspect all six full revisions. Current context restores the clean Elara prose
  exactly (1/1); evidence adds unnecessary explicit decision language (0/1 exact
  restoration), despite retaining all cited excerpts. All four unmet controls repair
  their missing fact, preserve fulfilled facts and avoid a handwriting match.
- [x] Record six post-passes, twelve native-met and six historical-met post checks.
  No independent craft finding or embedded-passage repair was exercised live.
  Do not treat critic pass, quote retention or smaller word count as prose quality.
- [x] Replay all 27 raw responses and validators, reconstruct every actual request,
  reconcile all ledger slots and skips, and reverify frozen implementation and
  483 sealed source files. Document and seal results without changing production.
- [x] Record **428,797 input / 30,845 output tokens**, USD **0.07236958** at recorded
  October 8 rates; actual charges remain unknown. No extra or replacement calls.
- [ ] Resolve the incomplete ordinary-critic eligibility and unsupported preservation
  benefit through separately scoped follow-up before claiming broader qualification.
- [ ] Full workflow canary: **NOT STARTED**, explicitly excluded by the user.

The experiment is complete even though its qualification criterion was not met.
There is no positive promotion or story-quality recommendation from one evaluable
pair. Keep the result fixed for later investigation and blind quality comparisons.
No new prompt tuning, canonical changes or story-quality campaign was started.
**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Fulfillment failure diagnosis and next experiment proposal: 2026-10-16

**DIAGNOSIS COMPLETE; FOLLOW-UP SINCE PREPARED AND RUN (2026-10-17).** See the
[diagnosis and bounded plan](../docs/handoffs/fulfillment-failure-diagnosis-next-experiment-2026-10-16.md).

- [x] Separate invalid critic output routes and assessment length from the valid but
  incorrect attribution of a separate endpoint defect to an already fulfilled event.
  Trace the repeated invalid anchor and the earlier repair-condition validation error.
- [x] Inspect exact writer requests and full prose. Positive policy arrived intact;
  every cited excerpt survived, but the uncited ending gained explicit restatement.
  Identify overlapping outcome/boundary framing as a hypothesis, not a proven cause.
- [x] Compare the earlier successful trial's revision history, repair ledger and
  evidence selection. Record why it is not an identical replication, and retain the
  unsuccessful scope-clarification and endpoint-advice diagnostics as counterevidence.
- [x] Propose a fixed-contract follow-up: ten critic cases at two seeds, plus three
  current/evidence writer pairs and their post-critics using one fixed validated
  saved review. Total: **32 probes / proposed 64-call ceiling**. Keep writer coverage
  independent of new critic eligibility; include complete-outcome negative controls.
- [x] Prepare and verify the new cases, full requests, scoring sheet and budget locally;
  present the [frozen manifest and plan](../docs/benchmark_reports/fulfillment-contrasts-v61-plan-2026-10-17.md)
  before live execution. No unused allowance from the completed experiment is carried forward.
- [x] Run and inspect the separately approved follow-up; see the October 17 results
  below. The diagnosis itself made no live calls or prompt/schema/runtime changes.
  Preserve independent craft and necessary edits; full-prose assistant inspection
  remains separate from pending blind human quality review.
- [ ] Full workflow canary: **NOT STARTED**, still excluded by the user.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Fulfillment contrasts and writer replication preparation: 2026-10-17

**PREPARED AND VERIFIED; SUBSEQUENT APPROVED EXECUTION COMPLETE.** See the
[frozen plan](../docs/benchmark_reports/fulfillment-contrasts-v61-plan-2026-10-17.md).

- [x] Freeze ten complete critic cases at seeds 19201/19203: clean, separate result,
  embedded result, missing decision and complete-outcome controls for both stories.
  Preserve full constraints and consistent immutable diagnostic artifact references.
- [x] Freeze six writer requests at seeds 19201/19203/19205 using the exact saved
  successful ordinary review. Each current/evidence pair differs only by the packet.
  New critic classifications cannot gate these writer trials.
- [x] Save **26 full static requests**, the six conditional post-review builders,
  structural retry rules, 32-probe order, scoring/prelabels and **64-call ceiling**.
  Hash the plan, cases, requests, scoring and 115 code/dependency files. Plan SHA-256:
  `9d01888c27a0aa45eaa126cf47824540591ce3867aa5324c44dbc48fb8371b9e`.
- [x] Validate 32 stage fixtures and 26 static retry requests. Complete the final
  **71-fake-call harness**, covering all three retry roles, permanent failures,
  writer independence, post skip, zero-call replay, call-65/third-attempt rejection,
  unknown/incomplete work, transport/overage/cancellation stops and approval guards.
  Retain 691 hashed fixture files and unscored anonymous full-prose pair exports.
- [x] Replay all 27 prior attempts; reverify sealed sources. Pass **91 relevant
  regressions**, repository Ruff/format and strict mypy for 201 source files;
  private harness lint/format checks pass. Production remains unchanged.
- [x] Publish the frozen plan and seal preparation evidence. **Zero live model calls
  or provider discovery calls**; human review remains pending. Preserve independent
  craft and necessary edits; no quality claim from quote retention or smaller diffs.
- [x] Obtain explicit approval bound to the frozen plan before live execution;
  retain the additional explicit prose/context transfer approval for Ollama Cloud.
- [x] Execute, inspect and report the bounded comparison without tuning mid-run;
  see the results below. The frozen preparation report remains unchanged.
- [ ] Full workflow canary: **ON HOLD; NOT STARTED**.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Fulfillment contrasts and writer replication results: 2026-10-17

**BOUNDED EXPERIMENT COMPLETE; BROADER QUALIFICATION INCOMPLETE.** See the
[results and full-text inspection](../docs/benchmark_reports/fulfillment-contrasts-v61-results-2026-10-17.md).

- [x] Execute the exact approved plan with the recorded cloud model digest and
  unchanged prompt 61 / graph 9 / policy 1. Retain all requests and durable
  reservations; no semantic rerolls, extra revisions or replacement probes.
- [x] Finish all **32 probes in 35/64 calls**, with no skips: 23 initial critic
  attempts, six writers and six post-critics. Thirty probes validate; two embedded
  Elena reviews fail after their allowed structural retry. All writer/post probes
  validate first attempt, independent of the new initial critic results.
- [x] Inspect all raw failures and native/normalized findings. Initial validity is
  17/20 first attempt and 18/20 final; classification matches are **16/20**. All
  ten Elara cases match. Both separate Elena results misclassify the fulfilled
  decision; both embedded cases fail routing. The recovered separate review changes
  from raw met to valid-but-wrong unmet. Compound outcomes remain unmet in 4/4.
- [x] Record supported advice separately from statuses: **15/20 sound reviews** on
  conservative assistant inspection, with one additional over-specific comparison
  condition documented transparently. No independent craft finding appeared.
- [x] Inspect all complete revisions and diffs: all six repair entry and retain
  fulfilled facts. Current context adds explicit decision restatement in **3/3**;
  evidence in **0/3**. Record three narrow preservation wins, no ties/losses/mixed
  tradeoffs. The prior evidence-only regression does not recur under these seeds.
- [x] Retain the shared limitation: **6/6 rewrite an adequate ending**, 0/6 exactly
  restore the clean text. Six post-passes, twelve native-met and six historical-met
  checks establish factual repair, not literary quality or durable workflow success.
- [x] Export three anonymous full-prose pairs and originals, with a separate private
  key. Complete assistant inspection separately; **blind human review stays pending**.
- [x] Reconstruct all 35 dispatched requests and replay all 32 receipts, including
  failed attempts; reconcile ledger, schedule, usage, approved hashes and model
  identities. Reverify preparation and historical seals; seal live evidence and
  report. Private inspection scripts pass lint/format; no production code changes.
- [x] Record **586,904 input / 41,345 output tokens**, 176.48 active dispatch seconds
  and USD **0.09870456** at recorded October 8 rates; actual charges unknown.
- [ ] Resolve ordinary-critic routing and attribution through a separately scoped
  proposal before broader qualification; do not tune from these results implicitly.
- [ ] Complete blind quality review and live craft-in-met-passage qualification
  separately. Preserve necessary edits and independent craft; never lock fulfilled prose.
- [ ] Full workflow canary: **ON HOLD; NOT STARTED**, as explicitly requested.

The comparison is complete even though broader qualification is not. No prompt,
schema, validator, runtime, canonical artifact or historical evidence was changed.
**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Remaining critic routes and shared ending rewrites: diagnosis 2026-10-17

**DIAGNOSIS COMPLETE; SUBSEQUENT LOCAL PREPARATION RECORDED BELOW.** See the
[diagnosis and bounded proposal](../docs/handoffs/fulfillment-routing-ending-next-experiment-2026-10-17.md).

- [x] Reverify 337 sealed live files, 44 preparation/operator files, frozen code and
  predecessor seals. Replay all 32 receipts / 35 attempts offline with network and
  gateway construction blocked. Preserve completed results and scoring unchanged.
- [x] Trace wrong outcome attribution separately from invalid conditions, anchors
  and links. Confirm all three retry requests omit rejected response bodies and
  retained classifications; one retry gains structural validity while losing the
  correct met judgment. Do not salvage failed reviews or relax validation.
- [x] Inspect the writer's actual negative-feedback channel: boundary category,
  outcome-framed claim and advice coexist with met evidence. Record adjacency and
  prospective-step wording as alternative hypotheses, not proven causes. Retain
  previous unsuccessful reminder, history-omission and advice-prefix experiments.
- [x] Propose independent critic and writer comparisons: 24 critic probes with an
  explicit route index; eight writers and eight ordinary post-critics comparing
  original versus boundary-only feedback framing, with evidence held constant.
  Include a fixed ordinary-review source whose cited passage contains the defect.
  Total **40 primary probes / proposed 80-call ceiling**; no prior unused allowance.
- [x] Keep first/final semantic correctness and advice support separate from output
  validity. Preserve full-prose judgment, required edits, independent craft and
  pending blind human review; no quality or promotion claim from smaller diffs.
- [x] User authorized local preparation of both comparisons; freeze full cases,
  projections, requests, scoring, schedule and budget, verify the harness and
  present the frozen plan below. Plan-bound live approval remains separate.
- [ ] Execute only after that approval; no candidate prompt, request projection or
  live call was made by this diagnosis. Full workflow canary: **ON HOLD; NOT STARTED**.

Production remains prompt 61 / graph 9 / policy 1. Live craft-in-met-passage and
complete-story quality qualification remain separate unfinished work.
**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Critic routes and writer boundary framing: local freeze 2026-10-17

**PREPARATION COMPLETE; APPROVED EXECUTION RECORDED BELOW.** See the
[frozen plan](../docs/benchmark_reports/fulfillment-routing-framing-v61-plan-2026-10-17.md).

- [x] Freeze six complete critic cases, both fixed ordinary writer sources, exact
  artifact versions, raw source reviews/audits and positive packets. Replay all
  32 prior receipts / 35 attempts and both writer sources; verify predecessor seals.
- [x] Freeze 24 critic probes comparing ordinary C0 with the sole added route-index
  field C1; eight writers comparing ordinary W0 with three boundary-framing fields
  W1, evidence held constant; eight conditional ordinary post-critics. Seeds 19301
  and 19303, counterbalanced arm order, no gating of writers by new critic results.
- [x] Freeze 32 exact static requests, all dependent/retry builders, request-difference
  records, schedule and scoring. Plan SHA-256:
  `cf143f6a1ee077a9c8c24b426b90009805b1d9897a517cb2782afdcf7cc4eb37`.
  Private bundle: `data/diagnostics/fulfillment-routing-framing-v61-2026-10-17/`.
- [x] Freeze **40 primary probes / 80 maximum attempts**, one structural retry per
  probe, nontransferable **48 critic / 32 writer-plus-post** block ceilings and
  16-attempt writer/post stage ceilings. Reserve at most 1,920,000 input / 640,000
  output tokens and 72,000 active seconds; historical-only estimate USD 0.52480.
- [x] Verify 40 stage fixtures, 32 static retry requests, 32 paired differences,
  four identical-output post pairs, 26 rejected source/view variants and four
  craft transmission checks. Required edits inside cited prose remain permitted;
  mixed/native/craft repairs cannot be hidden by the boundary projector.
- [x] Pass the final 87-fake-dispatch harness across independent ledgers: structural
  recovery, failed critic and wrong judgment independence, failed writer/sole post
  skip, zero-call replay, ceilings, ordering, source/request/model/approval guards,
  unknown/incomplete outcomes, transport/overage/cancellation stops. Bind 1,002
  fixture files and 121 code files. These calls are mocks, not live allowance use.
- [x] Pass 91 focused regressions, repository Ruff lint/format and strict mypy
  (201 files), private-script Ruff lint/format and documentation checks. Record the
  Windows sandbox temp/socket limitation and successful offline verification.
- [x] Preserve distinct scoring for routing validity, semantic correctness, advice
  support, factual repair, avoidable edits and genuine craft tradeoffs. Full anonymous
  pair exports remain human-review inputs; exact deletion is not a quality gate.
- [x] Record new approval bound to this plan hash and **full unpublished fictional
  prose/context sent to Ollama Cloud through the local daemon**, the 80-call ceiling
  and canary exclusion before gateway construction, discovery or inference.
- [x] Execute once after approval, inspect every attempt and full revision, report
  failures and limitations, update tracking and seal live evidence as recorded below.
- [ ] Blind human preference, live independent craft in a met passage and full-story
  quality qualification remain pending. Full workflow canary: **ON HOLD; NOT STARTED**.

Preparation made **zero live model, discovery or external network calls**. No
production prompt/schema/validator/runtime or canonical artifact changed.
**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Critic routes and writer boundary framing: completed comparison 2026-10-17

**COMPARISON COMPLETE; NEITHER CANDIDATE MEETS THE FROZEN SIGNAL.** See the
[results and inspection decisions](../docs/benchmark_reports/fulfillment-routing-framing-v61-results-2026-10-17.md).

- [x] Complete all 40 planned probes with **42/80 calls**: 26 initial critic calls,
  eight writers and eight ordinary post-critics. Respect the nontransferable
  48/32 block limits and one structural retry; no skips, replacements, semantic
  rerolls, transport retries or additional revisions. All three model checks match.
- [x] Record C0 **12/12 first-valid**, C1 **10/12 first-valid** and **12/12 final-valid
  in both arms**. Final classifications match **8/12 per arm**. Both falsely mark
  Elena's separate/embedded decision unmet at both seeds; retain correct clean,
  genuinely missing, complete compound and Elara controls.
- [x] Inspect both C1 embedded failures: illegal duplicate outcome route at 19301,
  conditions owned by a met outcome at 19303. Both retries change correct raw met
  to valid-but-wrong unmet. Preserve failed outputs; no salvaged writer evidence.
- [x] Audit advice separately: compound repair conditions are supported, with two
  control next-scene overclaims and one candidate support-rationale caution retained.
  No independent craft issue was reported. Structural validity is not semantic success.
- [x] Inspect all eight complete revisions and diffs. All repair entry and retain
  fulfilled facts; all eight ordinary posts pass, with sixteen native-met and eight
  original-repair-met checks. All four embedded revisions edit the cited defective
  sentence successfully. Exact excerpts remain descriptive, not protected spans.
- [x] Record W1 **0 preservation wins / 3 losses / 1 tie / 0 mixed**. W0 makes exact
  deletion-only repairs for both separate cases; W1 also rewrites their adequate
  endings. Embedded 19301 adds a new resolve/waiting beat and broader edits in W1;
  embedded 19303 is a tie. Preserve the alternative mixed interpretation for 19301
  if humans prefer its suspense; it still gives zero wins. No literary-quality claim.
- [x] Record six ending edits beyond the minimum, zero clear new explicit decision
  assertions and one ambiguous resolve beat. Separate factual retention, avoidable
  changes, benign wording and potential craft tradeoffs; do not count words as quality.
- [x] Export four full anonymous pairs/originals and a private order key. Complete
  assistant inspection separately; blind human review remains pending.
- [x] Reconstruct all 42 requests and replay all 40 probes / 42 attempts offline;
  reconcile reservations, outcomes, hashes, schedule and usage. Reverify 121 frozen
  code files and source/preparation seals. Seal live evidence, report and tracker
  snapshot. Private inspection scripts and documentation checks pass.
- [x] Record **686,223 input / 51,178 output tokens**, **292.13 active seconds** and
  USD **0.11654242** at historical October 8 rates only; actual billed charges unknown.
- [ ] Resolve critic attribution and retry stability through a separately scoped
  next proposal before further tuning or live calls. Do not promote either candidate.
- [ ] Complete blind human preference and live independent craft-in-met-passage
  qualification separately. Full-story quality qualification remains unfinished.
- [ ] Full workflow canary: **ON HOLD; NOT STARTED**.

Production prompt 61 / graph 9 / policy 1, validators, canonical artifacts and
historical evidence remain unchanged. No new application test/build claim is made
for this live execution; the full replay verifies the unchanged frozen path.
**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Route-index and boundary-framing diagnosis: next proposal 2026-10-17

**DIAGNOSIS COMPLETE; EXPERIMENT PROPOSED, NOT PREPARED OR RUN.** See the
[diagnosis and proposed comparisons](../docs/handoffs/fulfillment-routing-framing-diagnosis-next-experiment-2026-10-17.md).

- [x] Reverify 407 sealed live files, 52 preparation/operator files, 121 frozen code
  files and predecessor seals. Replay all 40 probes / 42 attempts to the sealed
  audit with network/gateway access blocked; inspect complete raw failures and prose.
- [x] Separate persistent outcome attribution errors from incompatible routes and
  retry drift. Both C1 retries legalize wrong unmet outcomes. Two explicitly manual
  routing fixtures validate with the original met/boundary judgments untouched;
  preserve them as counterfactuals, never model successes or writer sources.
- [x] Explain the narrower writer result: factual repair succeeds throughout;
  boundary framing adds static-ending rewrites and one ambiguous resolve/waiting
  beat. Record salience and edit granularity as hypotheses, retain the mixed-reading
  sensitivity, and avoid attributing a paired difference to the unchanged packet.
- [x] Propose ordinary critic versus adjudication-only diagnostic output, retaining
  complete obligation semantics and context. Do not credit a smaller schema as
  routing success, generate a production Critique, or omit craft from production.
- [x] Propose ordinary full-scene writer versus exact model-selected text edits,
  with original feedback and evidence fixed. Permit broad and whole-scene edits;
  reject stale, ambiguous or overlapping patches instead of silently fixing them.
- [x] Include a synthetic repetition control inside fulfilled evidence, with two
  ordinary source critics and conditional paired writers/posts. Freeze eligibility;
  source failure skips its dependent pair without fabricated reviews or rerolls.
- [x] Specify **50 primary probes / proposed 100-call ceiling**, with nontransferable
  48 critic / 32 fixed-source writer-post / 20 craft-control limits, one structural
  retry, new seeds 19401/19403 and no transferred allowance. No new calls authorized.
- [x] Keep preservation, factual repair, craft editing and human quality separate.
  Record the full-story rubric/baseline requirements and pending blind human review.
- [x] Verify the offline evidence helper with Ruff and documentation/link/whitespace
  checks; seal the diagnosis and tracker snapshot. No application test/build claim.
- [x] User authorized local preparation. Freeze and verify all contracts, complete
  cases, conditional builders, requests, scoring and budget; present the frozen plan
  recorded below. Plan-bound live approval remains separate.
- [ ] Execute only after that approval; broader qualification remains unfinished.
- [ ] Full workflow canary: **ON HOLD; NOT STARTED**.

Production prompt 61 / graph 9 / policy 1, canonical artifacts, validators and
historical evidence are unchanged. This diagnosis made **zero new inference,
discovery or external network calls**. **Step 19 IN PROGRESS; Step 20 NOT STARTED.**

### Adjudication, exact edits and craft control: local freeze 2026-10-17

**PREPARATION COMPLETE; approved execution is now complete below.** See the
[frozen plan](../docs/benchmark_reports/fulfillment-adjudication-edits-v61-plan-2026-10-17.md).

- [x] Preserve the six complete critic cases and both fixed ordinary writer sources,
  full drafts, source receipts, original feedback and fulfillment packets. Add one
  explicitly synthetic craft draft by duplicating the bracing sentence beside itself,
  with a new exact version and recorded parent lineage. Canonical stories are unchanged.
- [x] Freeze J0 ordinary review versus J1 native/boundary adjudication only; J1 remains
  ineligible as a production Critique or writer source. Preserve complete obligation
  semantics, full context and current evidence identities; do not compare the smaller
  schema's validity as if it qualified full critic routing or craft assessment.
- [x] Freeze E0 ordinary full-scene writing versus E1 exact, model-selected edits.
  Verify base version/hash, occurrence selectors, Unicode and atomic application;
  reject stale/ambiguous/overlapping/out-of-order edits. Permit changes anywhere and
  whole-scene replacement; no protected passages, diff quota or automatic prose fix.
- [x] Freeze two ordinary craft-source critics and conditional paired writers/posts.
  Require supported native/boundary judgments, one independent actionable repetition
  finding, two ordinary tests and positive evidence covering both repeated ranges.
  Require source/plan-bound operator semantic inspection before dependent dispatch;
  ineligibility skips its pair without replacement, reroll or manufactured evidence.
- [x] Freeze **50 scheduled primary probes / 100 maximum attempts**, seeds 19401/19403,
  counterbalanced arms, one structural retry and nontransferable **48/32/20** block
  limits. Reserve at most 2,400,000 input / 800,000 output tokens and 90,000 active
  seconds; historical-only estimate USD 0.65600, actual billed charges unknown.
- [x] Freeze **34 exact initial requests**, conditional builders, 36 paired-difference
  records, scoring and schedule. Bind 128 code/dependency hashes and 1,287 fixture
  files. Plan SHA-256:
  `765fd0499eb2ddb87f97e32cdfcb65b338b544c9be2e452f34bc16e4da0368a2`.
  Private bundle: `data/diagnostics/fulfillment-adjudication-edits-v61-2026-10-17/`.
- [x] Pass 50 stage fixtures, 50 retry builders, six post-equivalence checks and 37
  negative contract/source checks. Verify both-copy evidence coverage so deleting an
  uncited duplicate cannot falsely qualify the craft-in-met-passage control.
- [x] Pass the actual operator harness with 100 fake dispatches across independent
  ledgers: 52 valid-matrix, 44 fault-matrix and four terminal-failure calls. Verify
  budget/order/source/request/model/approval guards, pending and failed craft gates,
  skips, unknown outcomes, cancellation, failed transport/usage and zero-call replay.
- [x] Replay all 40 predecessor probes / 42 attempts, both fixed sources and all 96
  completed fixture attempts under final validators. Reconcile complete exports:
  six valid-matrix and three fault-matrix anonymous pairs; human review stays pending.
- [x] Pass **75 focused regressions**, repository Ruff lint/format and strict mypy
  (201 files), seven private-script Ruff lint/format checks and documentation checks.
  Record Windows sandbox fixture/event-loop limitations and successful mocked checks.
- [x] Keep factual repair, preservation, craft editing and human literary preference
  separate. Preserve the accepted rubric, hard gates and future full-story/baseline
  qualification; no production promotion or added mandatory human story checkpoint.
- [x] Receive explicit approval on 2026-10-17 bound to this exact plan, 100-call
  ceiling, full unpublished prose/context sent to Ollama Cloud through the local
  daemon, and canary exclusion before gateway construction or model discovery.
- [x] Execute once after approval; inspect all attempts/full prose, reconcile usage,
  export blind pairs and document failures without tuning mid-run. Results below.
- [ ] Full workflow canary: **ON HOLD; NOT STARTED**.

Preparation made **zero live model, discovery or external network calls**. Production
prompt 61 / graph 9 / policy 1, validators, runtime, canonical artifacts and historical
evidence remain unchanged. **Step 19 IN PROGRESS; Step 20 NOT STARTED.**

### Adjudication, exact edits and craft control: live results 2026-10-17

**BOUNDED RUN COMPLETE: 45/100 calls.** See the
[results and decisions](../docs/benchmark_reports/fulfillment-adjudication-edits-v61-results-2026-10-17.md).

- [x] Run all 24 critic probes in 27 attempts, eight fixed writers and eight ordinary
  post-reviews in 16 attempts, and both ordinary craft-source critics in two attempts.
  Account for all 50 slots: 42 completed probes plus eight dependent craft skips.
  No semantic rerolls, replacement cases, extra revisions or transport retries.
- [x] Confirm the frozen model digest at preflight and every phase. Match all 34
  static requests; save every actual request and reservation before dispatch. Replay
  all 45 attempts, including five invalid responses and two terminally invalid probes;
  reconcile all requests, response hashes, usage, outcomes, gates and skips offline.
- [x] Record J1's **12/12 valid supported shared judgments**, versus J0's **8/12**.
  J0 first/final validity is 9/12 and 10/12; both separate-match outcomes are falsely
  unmet and both embedded reviews remain invalid. J1 preserves clean, missing and
  compound controls. It meets the narrow diagnostic criterion, remains ineligible as
  a production Critique/writer source, and does not qualify craft, advice or routing.
- [x] Inspect all three ordinary structural retries: one compound review recovers;
  both embedded reviews fail terminally. Correct raw embedded judgments are not
  salvaged. This batch does not reproduce the earlier met-to-unmet retry drift.
  Record the separate-case advice overrestriction and next-scene acceptance overclaims.
- [x] Confirm **8/8 first-attempt factual writer repairs and 8/8 ordinary passing
  posts**, with four atomic E1 patches. Preserve complete prose/diffs. All revisions
  leave prose before the final main paragraph unchanged, but seven rewrite the ending
  beyond removing entry. E0 restores the clean scene once; E1 never does.
- [x] Score E1 preservation as **0 wins, 2 losses, 2 mixed**. Treating the smaller
  embedded loss as benign gives 0 wins, 1 loss, 1 tie, 2 mixed; the criterion still
  fails. Distinguish bodily embellishment, repeated bracing, new wait/commitment,
  benign wording and craft tradeoffs. These are operator judgments, not human scores.
- [x] Record **0/2 qualified craft sources**: both critics miss the adjacent duplicate,
  report only the boundary issue and score prose quality 5/5. Both also cite only one
  of the two repeated ranges as positive evidence. Skip four craft writers and four
  posts without replacements. Craft editing inside fulfilled evidence is **UNTESTED**.
- [x] Reconcile **696,412 input / 45,716 output tokens / 224.15 active seconds**;
  historical October 8 rate estimate **USD 0.11578408**, actual billed charges unknown.
  Respect the nontransferable block ceilings (27/48, 16/32, 2/20). Unused allowance
  does not authorize additional calls.
- [x] Save the sealed live bundle at
  `data/diagnostics/fulfillment-adjudication-edits-v61-2026-10-17-live/`, including
  all raw attempts, replay audit, operator assessment, complete prose/diffs and four
  anonymous primary pairs from six scheduled slots. Bind the unchanged preparation,
  new approval, dependency hashes, report and tracker snapshot in the final closure.
  New inspection scripts pass Ruff lint/format; documentation links/whitespace and
  evidence checks pass. The preparation's 75 regressions remain evidence against
  unchanged code, not a new test run. No production/client code changed.
- [ ] Human preference review remains **PENDING**; the exported review sheet is empty.
- [ ] Neither intervention is promoted. Future work requires a new bounded plan;
  full-story qualification still requires the accepted weighted rubric/hard gates,
  full intended Cloud corpus and comparable single-model baseline.
- [ ] Full workflow canary: **ON HOLD; NOT STARTED**.

Production prompt 61 / graph 9 / fulfillment policy 1, validators, runtime, canonical
artifacts and historical evidence remain unchanged. **Step 19 IN PROGRESS; Step 20
NOT STARTED.**

### Exact-edit selection and missed craft: diagnosis 2026-10-17

**DIAGNOSIS COMPLETE; NEXT EXPERIMENT PROPOSED, NOT PREPARED OR RUN.** See the
[diagnosis and proposed 80-call comparison](../docs/handoffs/fulfillment-edit-selection-craft-diagnosis-next-experiment-2026-10-17.md).

- [x] Record the user's retention decisions: J1 remains promising diagnostic evidence;
  E1 remains mechanically successful but unqualified for preservation. Neither is
  promoted or given production authority.
- [x] Reverify 443 sealed live files, 58 preparation/operator files, 128 dependency
  hashes and predecessor seals; replay all 42 probes / 45 attempts offline. Preserve
  the prior reports, scoring and empty human-review sheet. Network connections and
  gateway construction are blocked during diagnosis.
- [x] Locate E1's failure in the model's edit choices: both separate-entry cases
  contain an unnecessary edit wholly before the defect. All four minimal-patch
  counterfactuals validate and restore clean prose. These operator-authored fixtures
  are not model results, writer sources, canonical edits or literary preferences.
- [x] Verify that both critics received all scene wording, including two distinct
  duplicate handles, in a 52-entry sentence catalog. The continuous prose field and
  paragraph layout are absent from actual messages. No text loss or output truncation
  explains the miss; the raw reviews already omit independent craft and score prose 5/5.
- [x] Verify that the ordinary schema retains an independent duplication issue on
  response copies without changing native checks. Distinguish model omission from
  application filtering, presentation effects and unproven assignment/reporting load.
  Critics receive no writer fulfillment packet.
- [x] Identify additional craft-control limitations: both-copy positive coverage is
  an instrumentation requirement, and ordinary projection creates a second mandatory
  test for major craft on revise but not minor craft. Both severities remain normalized
  issues. Do not raise severity or manufacture sources to force control eligibility.
- [x] Propose comparison A: six complete cases (base, accidental duplicate, functional
  recurrence, each with/without entry overrun), two seeds, ordinary catalog-only versus
  exact continuous prose plus the unchanged catalog. Keep system instructions, output
  schema and critic settings fixed: 24 primary probes / maximum 48 attempts.
- [x] Propose comparison B: unchanged E1 requests and the two fixed ordinary writer
  sources at temperatures 0.85 versus 0.2, two seeds, with ordinary unchanged posts:
  eight writers plus eight posts / maximum 32 attempts. This is a sampling diagnosis,
  not a low-temperature drafting policy or craft-editing qualification.
- [x] Keep the proposed ceiling at **80 calls / 40 primary probes**, nontransferable
  48/32 blocks and one structural retry; no semantic rerolls or replacements. Preserve
  full-prose scoring, functional-repetition specificity and blind human review. No
  craft writer control is claimed this round; useful edits inside fulfilled passages
  remain an explicit later qualification requirement with a separately frozen design.
- [x] Save local diagnosis and labeled counterfactual evidence under
  `data/diagnostics/fulfillment-edit-selection-craft-diagnosis-2026-10-17/`; verify
  helper lint/format, documentation links, whitespace and source seals.
- [x] Prepare and freeze the proposed cases, requests, scoring and budget after
  authorization; see the preparation record below for the sealed plan. Approved
  bounded execution is recorded below.
- [ ] Human preference, full-story quality and production qualification remain open.
- [ ] Full workflow canary: **ON HOLD; NOT STARTED**.

This diagnosis made **zero live model, discovery or external network calls** and
created no next-experiment prompt, request bundle or live plan. Production prompt 61 /
graph 9 / policy 1, validators, runtime, canon and historical evidence remain unchanged.
**Step 19 IN PROGRESS; Step 20 NOT STARTED.**

### Critic presentation and E1 temperature: frozen preparation 2026-10-17

**PREPARATION COMPLETE; approved execution is now complete below.** See the
[frozen 80-call plan](../docs/benchmark_reports/fulfillment-presentation-temperature-v61-plan-2026-10-17.md).

- [x] Freeze six full-scene cases with distinct immutable draft versions: base,
  accidental adjacent duplication and functional recurrence, each with/without the
  entry overrun. Freeze construction rationales separately from model messages;
  legitimate criticism of the functional recurrence remains possible.
- [x] Freeze comparison A: ordinary P0 catalog versus P1 exact continuous prose
  alongside the unchanged catalog. Same ordinary instructions, schemas, evidence
  handles and settings; 24 primary probes / maximum 48 calls.
- [x] Freeze comparison B: unchanged E1 exact-edit instructions, two historical
  ordinary sources, full context, fulfillment packets and repair tests, at writer
  temperatures 0.85 versus 0.2. Eight writers plus eight ordinary P0 posts / maximum
  32 calls. No A result selects or gates the fixed B sources.
- [x] Freeze seeds 19501/19503, reverse arm order at the second seed, top-p 0.95,
  thinking disabled, critic temperature 0.2, and the nontransferable **80-call**
  ceiling. Reserve 24,000 input / 8,000 output tokens / 900 seconds per attempt;
  one structural retry, no semantic/transport rerolls or replacement cases.
- [x] Save 32 exact static requests and frozen dependent builders for eight posts
  and structural retries. Verify 32 paired attempt differences, all input lineage,
  exact prose inclusion, unchanged E1 instructions and identical ordinary posts for
  identical materialized prose. No context trimming. Largest static diagnostic
  token estimate 17,282; exact provider tokenization remains unknown until execution.
- [x] Freeze separate detection, native/boundary, advice-support, preservation and
  craft-tradeoff scoring; keep invalid results in scheduled denominators. Both minor
  and major independent craft findings can count as detection. Freeze pending
  assessment templates and four anonymous full-prose human-review pairs/export rules.
- [x] Verify all 40 scheduled slots through fake providers: 43 attempts with selected
  retries, 41 in the fault matrix and three terminal-error fixtures. Global, block,
  stage, token and time limits reject over-budget dispatch. A failed writer skips
  only its own post; critic failures do not block B. Completed replay adds zero calls.
- [x] Replay all 84 completed fixture attempts; reject request/response corruption,
  source mutation and six approval mismatches; verify 16 minor/major issue fixtures
  and complete/fault anonymous exports. Reverify predecessor seals and current source
  dependencies. Real gateway construction and external connections are blocked in
  offline checks.
- [x] Pass all 75 focused fulfillment/probe tests, repository Ruff/format and strict
  mypy checks across 201 files, and lint/format for six private helpers. No client or
  production changes require frontend tests/build. Save the plan, evidence hashes,
  verification, public report and tracker snapshot in the preparation closure.
- [x] Receive explicit approval for the frozen full-prose/context payload,
  Cloud-via-local-daemon destination and 80-call budget before model discovery or
  inference. Execute the frozen comparisons once; results are recorded below.
- [ ] Human preference, useful craft edits inside fulfilled passages, broader
  story-quality evaluation and production qualification remain open. No craft writer
  control is claimed in this round.
- [ ] Full workflow canary: **ON HOLD; NOT STARTED**.

Private evidence: `data/diagnostics/fulfillment-presentation-temperature-v61-2026-10-17/`.
Preparation made **zero live model or discovery calls**. J1 remains promising diagnostic
evidence; E1 remains mechanically successful but unqualified for preservation.
Production prompt 61 / graph 9 / policy 1, canon and historical evidence are unchanged.
**Step 19 IN PROGRESS; Step 20 NOT STARTED.**

### Critic presentation and E1 temperature: live results 2026-10-17

**BOUNDED RUN COMPLETE: 43/80 calls; neither frozen success criterion met.** See the
[results and decisions](../docs/benchmark_reports/fulfillment-presentation-temperature-v61-results-2026-10-17.md).

- [x] Complete all 40 scheduled probes: 24 initial critics in 27 calls, eight writers
  and eight ordinary posts in 16 calls. Final validity is 38/40. Three structural
  retries yield one recovery and two terminal failures; five attempts are invalid.
  No skips, semantic rerolls, transport retries, replacement sources or extra revisions.
- [x] Match the frozen model digest at preflight and both phases, verify all 32 static
  requests and dependent builders, and reconcile every reservation, response, receipt,
  outcome and probe through offline replay. Preserve invalid results in denominators.
- [x] Record P1's improved raw duplication detection **4/4 versus P0 0/4**, but only
  **2/4 valid supported findings**. Both P1 duplicate-plus-overrun reviews remain
  invalid after retry. Native/boundary judgments are supported in every raw review;
  valid qualified tuples are P0 12/12 and P1 10/12. Neither arm makes an unsupported
  repetition-removal demand on its eight base/functional-recurrence controls.
- [x] Inspect every failed attempt: model-written boundary repair references and
  recommendation reuse cause the observed failures. Record empty craft-comparison
  references as an additional visible omission, without inventing a later validation
  result. Keep correct raw observations separate from usable production reviews.
- [x] Confirm all eight E1 patches validate immediately, repair the boundary and
  retain fulfilled facts; all eight ordinary posts pass immediately. Inspect complete
  prose, selected edits and diffs: all four separate-entry writers edit before the
  defect, and all four embedded writers add the same threshold image.
- [x] Score T1 temperature 0.2 relative to T0 0.85 as **0 wins, 1 loss, 2 ties, 1
  mixed**. Sensitivity with debatable additions neutral gives 0 wins, 1 loss, 3 ties.
  No embedded pair wins; one pair has byte-identical prose. The clear loss deletes
  compatible first-step preparation. These are operator judgments; human preference
  remains pending. Maximum post-review craft scores do not qualify literary quality.
- [x] Reconcile **765,309 input / 44,131 output tokens / 219.15 active seconds**;
  historical October 8 rate estimate **USD 0.12479566**, actual billed charges unknown.
  Respect nontransferable block ceilings (27/48 and 16/32) and every stage/per-attempt
  limit. The 37 unused calls authorize no additional calls.
- [x] Seal the live evidence at
  `data/diagnostics/fulfillment-presentation-temperature-v61-2026-10-17-live/`,
  including replay audit, per-axis assessment, full prose/diffs, four anonymous human
  pairs, final verification and tracker snapshot. Bind the unchanged preparation,
  approval, 134 dependencies and public report. Pass private helper Ruff lint/format,
  documentation links, UTF-8/LF, whitespace and evidence checks. Preparation's 75
  regressions and mypy checks are prior evidence against unchanged production code.
- [x] Retain J1 as promising diagnostic evidence and E1 as mechanically successful
  but unqualified for preservation. Retain P1's noticing improvement as diagnostic
  evidence only; neither comparison qualifies promotion. No production prompt change.
- [ ] Human preference review: **PENDING**; four anonymous pairs exported, sheet empty.
- [ ] Useful craft edits inside fulfilled passages, full-story quality and production
  qualification remain open. Keep the accepted rubric/hard gates, full intended Cloud
  corpus and comparable single-model baseline; no craft writer control is claimed here.
- [ ] Further experiments require a new bounded design; none prepared in this results task.
- [ ] Full workflow canary: **ON HOLD; NOT STARTED**.

Production prompt 61 / graph 9 / policy 1, validators, runtime, canonical artifacts
and historical evidence remain unchanged. **Step 19 IN PROGRESS; Step 20 NOT STARTED.**

### P1 reporting and edit selection: diagnosis 2026-10-17

**DIAGNOSIS COMPLETE; NEXT EXPERIMENT PROPOSED, NOT PREPARED OR RUN.** See the
[diagnosis and proposed 96-call experiment](../docs/handoffs/fulfillment-reporting-edit-purpose-diagnosis-next-experiment-2026-10-17.md).

- [x] Retain P1's improved noticing as diagnostic evidence, per the user's decision.
  Preserve J1's diagnostic status and E1's mechanical success without preservation
  qualification. No production promotion.
- [x] Reverify 415 sealed live files, 57 preparation/operator files, 134 dependencies,
  source report and predecessor seals; replay all 40 probes / 43 attempts offline.
  Preserve historical evidence and empty human-review sheets. Block gateway creation
  and external connections; make zero model, discovery or external network calls.
- [x] Isolate P1's reporting failures on four response copies. Correcting advice
  ownership alone exposes missing independent-craft comparison coverage in all four.
  Correcting both validates all four without changing native/boundary judgments,
  craft description, severity or evidence. These are operator fixtures, not model
  successes, canonical artifacts or eligible writer sources.
- [x] Verify that invalid advice causes the existing diagnostic-enrichment helper
  to return before collecting comparison/retention metadata. Actual retries focus
  on the first condition-reference error. Record the distinction between a finding
  reference, model-authored condition owner and independent comparison coverage.
  Do not claim complete feedback is guaranteed to fix the exposed errors.
- [x] Reconfirm accurate application of all eight writer patches and eight valid
  minimal-patch counterfactuals. Existing preservation instructions and lower
  temperature do not prevent selected ending recomposition. Retain mixed/tie/loss
  judgments and their sensitivity analysis; do not equate minimal edits with quality.
- [x] Verify all eight actual post messages omit the full original prose and diff;
  only the revised sentence catalog is present alongside old metadata and selected
  repair evidence. Maximum post scores are not direct preservation comparisons.
- [x] Propose A: eight full cases, two seeds, 16 shared P1 initials, then one R0/R1
  correction per branch only after structural failure. Compare existing feedback
  with independently checkable concrete error coverage; maximum 48 calls. Include
  real missing/compound native obligations, retain the full ordinary validator and
  craft findings, and mark insufficient first failures inconclusive without rerolls.
- [x] Propose B: unchanged E1 versus checkable per-edit purposes at fixed temperature
  0.85. Two historical boundary sources plus one existing valid minor P1 duplication
  source, two seeds, 12 writers and 12 ordinary posts; maximum 48 calls. Both arms
  explicitly receive the optional craft task. Preserve its pass verdict/minor
  severity; no manufactured mandatory test or automatic production revision trigger.
- [x] Record the craft control's limitation: only one duplicate copy is positively
  cited, so successful deletion need not touch positive evidence. Score actual
  overlap; do not claim necessary craft editing inside fulfilled prose is qualified.
- [x] Propose nontransferable **96-call** ceiling, seeds 19601/19603, bounded structural
  retries, no semantic/transport rerolls, full-prose paired scoring and human review.
  Reserve 2,304,000 input / 768,000 output tokens and 86,400 active seconds; historical
  ceiling estimate USD 0.62976, actual charges unknown. No new plan or requests frozen.
- [x] Save private diagnosis evidence under
  `data/diagnostics/fulfillment-reporting-edit-purpose-diagnosis-2026-10-17/`;
  verify helper lint/format, source seals, documentation links and whitespace.
- [x] Receive subsequent authorization and prepare cases, candidate builders, scoring
  and harness; the completed preparation is recorded below. The diagnosis itself
  created no candidate prompt/schema or live request/operator bundle.
- [ ] Human preference, useful craft edits necessarily inside fulfilled evidence,
  full-story/baseline evaluation and production qualification remain open.
- [ ] Full workflow canary: **ON HOLD; NOT STARTED**.

Production prompt 61 / graph 9 / policy 1, validators, runtime and canonical artifacts
remain unchanged. **Step 19 IN PROGRESS; Step 20 NOT STARTED.**

### Reporting retry and edit purpose: frozen preparation 2026-10-17

**PREPARATION COMPLETE; subsequent approved execution is complete below.** See the
[frozen 96-call plan](../docs/benchmark_reports/fulfillment-reporting-edit-purpose-v61-plan-2026-10-17.md).

- [x] Freeze eight existing full-scene cases and input versions: six Elara
  base/duplication/functional-recurrence cases with and without overrun, plus Elena
  missing-decision and compound-outcome controls. Preserve exact prose and context.
- [x] Freeze A: 16 shared ordinary P1 initial reviews, followed only after structural
  failure by one R0 and one R1 correction. R0 uses existing retry feedback; R1 adds
  bounded, independently checkable condition-owner and comparison metadata. Both
  branches bind the same rejected response. Maximum **48 calls**; valid initials
  are shared, not two independent successes. No semantic rerolls or third attempts.
- [x] Keep the ordinary final validator and native conditions intact. Diagnostic
  projections can inspect metadata but cannot produce accepted reviews or writer
  sources. Missing/stale native evidence is not promoted; feedback is limited to
  16 diagnostics / 10,000 serialized diagnostic bytes, with partial coverage marked.
- [x] Freeze B: unchanged E1 (W0) versus per-edit target/purpose claims (W1), both at
  temperature 0.85. Three fixed historical sources, two seeds, 12 writers and 12
  conditional ordinary P0 posts; one structural retry each, maximum **48 calls**.
  A results cannot select, replace or gate the B sources.
- [x] Include the actual valid P1 pass/minor duplication source as an explicitly
  requested optional craft task in both arms. Manufacture no mandatory craft test
  and introduce no production revision trigger. Keep purpose records outside prose
  and post messages. Measure positive-evidence overlap without claiming it necessary.
- [x] Freeze seeds 19601/19603, reverse arm order at the second seed, critic
  temperature 0.2, top-p 0.95 and thinking disabled. Enforce the nontransferable
  **96-call** ceiling with stage limits 16/32/24/24. Reserve 24,000 input tokens,
  8,000 output tokens and 900 seconds per attempt; aggregate 2,304,000 input /
  768,000 output tokens / 86,400 active seconds. No transfer of prior unused calls.
- [x] Save **28 exact static requests**, 72 scheduled slots, dependent correction,
  post and retry builders, complete source identities, scoring and pending assessment
  templates. Freeze six anonymous full-prose review pairs/export rules. Reject source
  substitution or request drift; persist and reserve exact requests before dispatch.
- [x] Freeze separate structural, finding-support, preservation and craft assessments.
  R1 needs at least two paired qualified rescues including a combined failure, no
  losses and complete control coverage; fewer than two failed initials is inconclusive.
  W1 needs all four boundary and both craft repairs, at least two clear boundary-pair
  wins including an embedded case, no losses and substantively supported edit purposes.
  Missing/invalid outputs never win. Minor craft remains optional; no-op craft fails.
- [x] Pass 96 valid response fixtures, 28 paired request-difference checks, 24 invalid
  purpose checks, four historical failed-attempt feedback checks and six identical-
  post comparisons. Pass **181 fake dispatches** across ceiling/shared/fault/terminal
  matrices. Replay all 178 completed attempts and 63 skips with final code; completed
  reruns add zero calls. Verify caps, branch isolation, approval mismatches, corruption,
  cancellation, unknown outcomes, source mutation and unavailable stale evidence.
- [x] Export six complete and five available fault pairs, correctly recording two
  scheduled craft pairs. Save all qualitative and human assessments as pending.
  Largest static token estimate 17,282; largest tested dependent estimate 19,747.
  Exact provider counts remain unknown; no context trimming or token-cap expansion.
- [x] Pass all 75 focused fulfillment/probe regressions, repository Ruff/format and
  strict mypy across 201 files, and lint/format for eight private helpers. Reverify
  predecessor and diagnosis seals. Record final code, request, fixture, report and
  tracker hashes in the preparation closure. No client changes require frontend checks.
- [x] Obtain separate approval for this exact frozen plan, full unpublished prose,
  critique and story context, **Ollama Cloud via the local daemon**, and the **96-call**
  ceiling before discovery or inference. Bind the user's approval to the sealed plan.
- [x] Execute and inspect the approved comparison, keeping shared observations,
  raw diagnostic findings and qualified successes separate; document full prose,
  all changes, supported purposes and neutral-addition sensitivity before promotion.
- [ ] Human preference, craft repairs necessarily inside fulfilled evidence, full
  intended Cloud corpus, comparable single-model baseline and story-quality
  qualification remain open. Smaller diffs and high critic ratings are not quality.
- [ ] Full workflow canary: **ON HOLD; NOT STARTED**.

Private evidence: `data/diagnostics/fulfillment-reporting-edit-purpose-v61-2026-10-17/`.
Frozen plan SHA-256: `ee346c83e38643f9f1438279cde5863067e51896d8da2519fd9788651cc22844`.
Preparation made **zero live model or discovery calls**. Retain J1/P1 as diagnostic
evidence and E1 as mechanically successful but preservation-unqualified. Production
prompt 61 / graph 9 / policy 1, validators, runtime, canon and historical evidence
remain unchanged. **Step 19 IN PROGRESS; Step 20 NOT STARTED.**

### Reporting retry and edit purpose: live results 2026-10-17

**BOUNDED RUN COMPLETE: 46/96 calls; neither frozen success criterion met.** See the
[results and decisions](../docs/benchmark_reports/fulfillment-reporting-edit-purpose-v61-results-2026-10-17.md).

- [x] Execute all 72 scheduled slots: 46 calls and 26 justified correction skips.
  Thirteen of 16 shared initials validate; three branch into six correction calls,
  four of which validate. All 12 writers and 12 ordinary posts validate immediately.
  Preserve the five rejected responses, including three initials and two terminal
  correction branches. No semantic rerolls, transport retries or replacement sources.
- [x] Match the frozen model digest and Cloud deployment at preflight and both phases.
  Verify all 28 static requests and dependent builders, exact parent binding, unchanged
  preparation and 142 dependencies. Reconcile all requests, reservations, responses,
  receipts, outcomes and skips through offline replay.
- [x] Record A's **22/48 calls**: R0 and R1 each recover **2/3** failed initials,
  with **zero additional paired R1 rescues** and zero paired losses. Both policies
  finish with **15/16** valid supported native/boundary tuples and **3/4** valid
  supported duplication findings. Raw duplication noticing remains 4/4; eight base/
  recurrence controls receive no unsupported repetition-removal demand.
- [x] Inspect the remaining combined-case failures: R0 retains an empty independent
  craft comparison; R1 fixes comparison coverage but adds forbidden model-written
  boundary conditions. Both retain the correct minor duplication finding. No initial
  reproduced the earlier ownership error that masked comparison coverage; record
  that limit rather than claiming the masked-error hypothesis was fully tested.
- [x] Confirm all four Elena control conditions remain supported and narrow. Record
  overclaims in compound-case next-scene explanations separately: a confirmed match
  does not alone establish warning acceptance or verification of a particular flourish.
  The explicit current no-match rule still supports the boundary judgments.
- [x] Record B's **24/48 calls**, with no structural retry. Both arms repair all four
  boundary cases and both requested optional craft cases, retaining fulfilled facts.
  Every ordinary post passes, but all 36 maximum craft scores fail to distinguish
  the observed preservation differences and unsupported editing purposes.
- [x] Inspect complete prose, patches and diffs. W1 versus W0 primary judgments:
  **2 wins, 0 losses, 3 ties, 1 mixed**, including an embedded win. Additions-neutral
  sensitivity: **1 win, 1 loss, 4 ties**. Preserve the mixed tradeoff and human-review
  uncertainty; do not substitute the sensitivity labels for the frozen primary labels.
- [x] Assess all eight W1 purpose claims: **4 supported, 2 partly supported,
  2 unsupported**. Separate-case adjacent rewrites miscast preparation or tonal
  preference as necessity; embedded purposes justify entry removal but not all added
  imagery/action. W1 fails the all-supported-purpose criterion despite two primary wins.
- [x] Verify the craft control succeeds in all four revisions: one bracing action
  remains, all surrounding words retained; one output leaves a double space. Three
  selected ranges overlap positive evidence, but deleting the uncited copy remains
  possible. Do not claim qualification of necessary craft changes inside fulfilled prose.
- [x] Reconcile **778,005 input / 45,432 output tokens / 253.56 active seconds**;
  historical October 8 rate estimate **USD 0.12709350**, actual billed charges unknown.
  Respect every stage, block, per-call and aggregate cap. The 50 unused calls authorize
  no further experiments, revisions or canary work.
- [x] Save and seal all live evidence, response-bound assessments, full prose/diffs,
  six anonymous review pairs, final verification and tracker snapshot under
  `data/diagnostics/fulfillment-reporting-edit-purpose-v61-2026-10-17-live/`.
  Pass offline replay, helper Ruff/format, documentation links, UTF-8/LF and whitespace
  checks. Preparation's 75 regressions and strict mypy remain prior checks of unchanged
  production code; no new regression run is claimed.
- [x] Retain J1/P1 as diagnostic evidence and E1 as mechanically successful but
  preservation-unqualified. Record W1's limited gains and successful optional repair
  alongside its failed justification gate. No production prompt or policy promotion.
- [ ] Human preference: **PENDING**; all six complete anonymous pairs exported,
  review sheet empty. Necessary craft edits within fulfilled passages, broader
  story-quality evaluation, full intended Cloud corpus and comparable baseline remain open.
- [ ] Further experiments require a new bounded design; none prepared or run here.
- [ ] Full workflow canary: **ON HOLD; NOT STARTED**.

Production prompt 61 / graph 9 / policy 1, validators, runtime, canonical artifacts
and historical evidence remain unchanged. **Step 19 IN PROGRESS; Step 20 NOT STARTED.**

### Review repair and independent revision assessment: diagnosis 2026-10-18

**DIAGNOSIS COMPLETE; NEXT EXPERIMENT PROPOSED, NOT PREPARED OR RUN.** See the
[diagnosis and bounded proposal](../docs/handoffs/fulfillment-repair-surface-review-diagnosis-next-experiment-2026-10-18.md).

- [x] Trace the unchanged R0/R1 requests and all failed responses. Ordinary feedback
  already exposed the combined cases' missing comparison group; R1 corrected that
  field at seed 19603 but introduced unauthorized model-written boundary conditions.
  Both arms regenerate a complete report without the full rejected JSON. Bounded
  classification retention does not preserve every judgment, allegation or condition.
  Record error migration and the untested earlier masked-error case without claiming
  access to the model's internal reasoning or that expanded feedback is universally useless.
- [x] Verify five operator-authored review copies can pass with only their applicable
  reporting fields corrected, preserving judgments, scores, descriptions, severity,
  evidence and comparison prose. Keep these distinct from actual model recoveries.
- [x] Inspect all six W1 edit lists and their purposes. A true defect in an old span
  does not justify every added phrase; preparation is not entry, and a desired tonal
  change is not an established grammatical dependency. Four minimal boundary patch
  copies validate. Retain W1's limited preservation gains and successful craft repair.
- [x] Confirm ordinary posts lack the complete original/revision comparison and do
  not see purposes. Their maximum ratings do not qualify preservation or show whether
  writer explanations would bias a comparative reviewer.
- [x] Propose A: six fixed parent reports, two arms and two seeds, **24 calls** with
  no additional retry. Both arms receive exact rejected JSON as untrusted diagnostic
  data and the same diagnostics; compare full replacement against restricted atomic
  correction. Include valid native-condition controls and the earlier masked failure.
  This is an isolated departure from production rejected-prose replay policy, not an
  adopted runtime change. It isolates output scope, not parent visibility by itself.
- [x] Propose B: nine fixed full-prose candidate comparisons, purposes hidden versus
  visible, two seeds; **36 primary reviews / 72 calls maximum** with one structural
  correction each. No new writer calls. Include actual unnecessary/mixed edits,
  successful craft, clean boundary repairs, unrepaired no-ops with mismatching claims,
  and a synthetic craft repair necessarily changing a positively cited sentence.
  Predeclare the purpose-hidden reviewer as the candidate; visible purposes test
  explanation influence. Keep necessity, preservation and literary merit separate.
- [x] Propose a **96-call total ceiling**, nontransferable blocks, exact provenance,
  zero semantic/transport rerolls, identity checks, anonymous full-prose review and
  fail-closed handling of stale evidence, unexpected outcomes or invalid patches.
- [x] Verify unchanged source seals, 488 live files, 56 preparation/operator files,
  142 dependencies, all 46 attempts and 26 skips offline. Save nine labelled local
  counterfactuals and diagnosis verification; no model, discovery or network calls.
- [x] Preparation was subsequently authorized and completed; see the frozen plan below.
- [x] The subsequent frozen plan was explicitly approved and executed to its terminal
  stop; see the partial live results below. No further calls are authorized by that run.
- [ ] Independent human preference remains pending. Full Cloud corpus, comparable
  baseline and accepted weighted rubric remain required for broader qualification.
- [ ] Full workflow canary: **ON HOLD; NOT STARTED**.

Production prompt 61 / graph 9 / policy 1 and historical evidence remain unchanged.
J1/P1 remain diagnostic; E1 remains preservation-unqualified. **Step 19 IN PROGRESS;
Step 20 NOT STARTED.** No new production role, graph node or human checkpoint.

### Review correction and comparative assessment: frozen preparation 2026-10-18

**PREPARATION COMPLETE.** The historical preparation state is preserved in the
[frozen 96-call plan](../docs/benchmark_reports/fulfillment-repair-surface-review-v61-plan-2026-10-18.md).
Subsequent approval and the terminal live stop are recorded below.

- [x] Freeze A's six exact attempt-1 parent reports, two seeds and two arms: full
  report versus restricted atomic correction with the same parent JSON and R1
  diagnostics. Include masked-error and valid native-condition controls. Preserve
  the compound source's known explanation caveat without certifying it as truth.
- [x] Freeze B's nine original/revision comparisons: four actual W1 outputs, two
  minimal boundary repairs, two no-op claim challenges and the within-sentence
  craft control. Preserve full context, exact versions, provenance and optional
  task status. The new control necessarily edits inside one positively cited
  sentence while retaining its fulfilled fact; it has no invented critic source.
- [x] Freeze **60 primary requests**, exact source/schedule/scoring files and the
  builder for up to **36 B structural corrections**. V0 is the predeclared primary
  reviewer; V1 adds only unverified editorial claims. Expected labels and source
  arm/seed provenance stay outside messages. No new writer calls.
- [x] Freeze seeds **19701/19703**, temperature **0.2**, top-p **0.95**, thinking
  disabled and the existing gemma4 Cloud digest. Reverse case and arm order at
  the second seed. A has **24 calls**, B at most **72**, nontransferable, total **96**.
- [x] Enforce scope, parent hash, atomic operations and unchanged full validation
  for A. Preserve valid B judgments and assessments by unique identity on a
  structural retry, including reordered records. Reject drift; stop on ambiguous
  duplicate identity or oversized retention. No silent metadata or prose repair.
- [x] Verify **60 valid fixtures, 389 rejection checks, 30 paired deltas**, and
  additional reordered-retention checks. Fake matrices use 60/96/62 calls; all
  **278 completed attempts** replay with final code. **284 total fake dispatches**
  include transport, identity, cancellation and restart fixtures. Replay uses zero
  additional calls. Verify approval, locks, ceilings, interrupted/unknown outcomes,
  source integrity, capture/receipt/usage/summary binding and full-prose exports.
- [x] Pass **75 focused regressions**, repository Ruff/format and strict mypy
  across **201 files**, and Ruff/format on **9 private helpers**. No production or
  client changes; no provider discovery, external network or live inference calls.
- [x] Verify maximum static input estimate **19,184 tokens** and maximum retained
  retry-payload estimate **20,487** under the 24,000/8,000/900-second per-call limits.
  Estimates are not exact provider counts. Preserve aggregate reservations of
  2,304,000 input / 768,000 output / 86,400 active seconds. Historical-rate ceiling
  estimate USD 0.62976; actual charges unknown. No silent context trimming.
- [x] Save preparation, anonymous full-prose pairs and pending review sheet under
  `data/diagnostics/fulfillment-repair-surface-review-v61-2026-10-18/` and bind
  **151 code dependencies**, source/diagnosis seals, the public plan and tracker snapshot.
  Plan SHA-256:
  `9793f119f39c64ba2cd92f869f1d356240dfc8da7c8cf7b2a4184e79c12d9c86`.
- [x] Record explicit live approval bound to this frozen plan, the full
  prose/rejected-review/context payload and Ollama Cloud through the local daemon.
  Execute only the frozen schedule and stop rules; see the partial results below.
- [ ] Human preference and broader story-quality qualification remain pending.
- [ ] Full workflow canary: **ON HOLD; NOT STARTED**.

Production prompt 61 / graph 9 / policy 1, historical evidence and canonical
artifacts remain unchanged. **Step 19 IN PROGRESS; Step 20 NOT STARTED.**

### Review correction and comparative assessment: live stop 2026-10-18

**STOPPED AT 41/96 CALLS; A COMPLETE, B PARTIAL.** See the
[results and decisions](../docs/benchmark_reports/fulfillment-repair-surface-review-v61-results-2026-10-18.md).

- [x] Verify the frozen plan, approval, sources and pinned gemma4 Cloud identity
  before execution. Preserve temperature 0.2, top-p 0.95, thinking disabled,
  seeds 19701/19703 and the nontransferable 24/72-call blocks.
- [x] Complete all **24 A calls**. F0 validates 7/12 reports, with 4/8 qualified
  failed-parent recoveries and 3/4 preserved controls. F1 validates 10/12, with
  **6/8 qualified recoveries and 2/4 preserved controls**. Two F1 comparisons
  only restate the boundary; both compound controls emit undeclared report fields.
  Across all pairs F1 has 3 qualified wins, 2 losses and 7 ties. **A criterion fails.**
- [x] Execute eight B review slots at seed 19701, b01-b04 in both arms, including
  their single structural corrections: **16 calls, zero valid assessments or
  recoveries**. Inspect all attempts, including duplicate keys, missing output
  fields, citation mismatches and unsupported necessity claims. Preserve the
  distinction between useful raw observations and qualified model outputs.
- [x] Stop all dispatch at call **41**, b05/V0's first attempt, after the provider
  reports `length` at **8,000 output tokens** while copying input material.
  Preserve the raw capture and incomplete probe; do not retry, invent a receipt,
  mark the review phase complete or use the **55 remaining calls**.
- [x] Reconcile **41 reservations/outcomes/captures**, replay all **40 completed
  attempts**, and label all **27 unstarted primary slots** explicitly. A uses
  24/24 calls; B uses 17/72. Recover the terminal call's 15,183/8,000 token usage
  from its persisted capture without changing the outcome's null usage fields.
  Total: **780,033 input / 64,892 output tokens / 235.33 active seconds**;
  historical-rate estimate **USD 0.13516142**, actual charges unknown.
- [x] Inspect four reached raw pairs without claiming the planned 18-pair result.
  Visible purposes upgrade an optional preparation deletion into a required edit
  in b01; both arms miss b02's concrete preservation tradeoff and conflate b03's
  optional imagery with direct repair. b04's duplicate repair is correctly noticed
  in invalid reports. Retain these limited observations; **B is not qualified**.
- [x] Verify 95 retained semantic leaves without drift in four parseable retries.
  Record that duplicate-key responses retain none and wrongly named change records
  lie outside the frozen retention map. No invalid report is silently repaired.
- [x] Save partial reconciliation, A/B operator judgments, nine anonymous full-prose
  pairs, verification and closure under
  `data/diagnostics/fulfillment-repair-surface-review-v61-2026-10-18-live/`.
  Recheck 151 frozen code dependencies and preparation/source seals offline.
- [ ] B's remaining comparisons are **NOT RUN**: no-op defects, synthetic craft
  control, embedded minimal repair and the second seed remain untested. The
  minimal separate control was truncated. Any further execution requires a new
  reviewed plan; the stopped run cannot be automatically continued.
- [ ] Independent human preference and broader story-quality qualification remain
  pending. Neither partial raw findings nor structural recovery qualify production.
- [ ] Full workflow canary: **ON HOLD; NOT STARTED**.

Retain J1/P1 as diagnostic evidence, E1 as preservation-unqualified, and W1's earlier
limited gains. Production prompt 61 / graph 9 / policy 1 and canonical artifacts
remain unchanged. **Step 19 IN PROGRESS; Step 20 NOT STARTED.**

### Output-contract failure diagnosis and proposed experiment 2026-10-18

**DIAGNOSIS COMPLETE; FOLLOW-UP LOCAL PREPARATION RECORDED BELOW.** See the
[diagnosis and 74-call proposal](../docs/handoffs/fulfillment-output-contract-diagnosis-next-experiment-2026-10-18.md).

- [x] Diagnose F1's a01 semantic failure separately from a06's hybrid output.
  Correct patch locations/references do not establish a supported craft comparison.
  Both a06 responses contain the correct empty patch followed by an exact parent
  copy. Two labelled local projections validate without changing that parent.
  Competing whole-review/patch output cues are a hypothesis, not a proven cause.
- [x] Confirm all 41 saved requests use prompt-text schemas with
  `response_schema=null`; the checked-in Cloud adapter does not send a schema
  `format` for them. No provider discovery or capability change is inferred.
- [x] Distinguish B's field/duplicate errors, masked required-text/evidence errors,
  and input copying from literary judgment. Of 136 raw citation mismatches, 134
  are exact fragments of the correct full catalog entry; two span entries.
  Fifteen unambiguous format-only copies remain invalid; do not normalize the
  conflicting duplicate-key response or count any copy as model recovery.
- [x] Verify the truncated call echoes input and the complete original prose,
  reaching 8,000 output tokens before an assessment. Completed B responses use
  1,292–3,102 output tokens. Increasing the output cap is not supported as the
  first remedy. Preserve the old run's terminal stop and unused 55-call allowance.
- [x] Propose A: F1/F2 on four fixed parents at two new seeds, plus F3 local-focus
  challenges on the two comparison parents: **20 calls**. F2 isolates one active
  patch contract from ordinary reference rules; F3 adds a diagnosed-issue focus.
  Share F2's no-comparison controls explicitly instead of duplicate F3 calls.
- [x] Propose B: all nine frozen prose pairs, V0/V2/V3 at two seeds: **54 calls**.
  V2 clarifies/separates the existing output contract; V3 adds application-bound
  version metadata and reference-to-quote expansion while retaining model-chosen
  evidence and every editorial judgment. Purposes remain hidden. Preserve no-op,
  minimal-repair, mixed-ending and within-cited-sentence craft controls.
- [x] Propose **74 total calls, zero retries, no writers**, seeds 19801/19803,
  temperature 0.2, top-p 0.95, thinking disabled, and the same pinned Cloud model.
  Retain 24,000 input / 8,000 output / 900 active-second per-call caps; total maximum
  reservations 1,776,000 input / 592,000 output / 66,600 active seconds. Historical
  rate ceiling estimate USD 0.48544; actual charges unknown.
- [x] Explicitly propose a future diagnostic stop-policy distinction: a fully
  captured, correctly identified `length` response with known in-budget usage
  fails its cell without retry, then permits the next frozen cell. Unknown outcomes,
  identity/integrity drift, cancellation, transport failure and exceeded budgets
  still stop the run. The diagnosis did not implement this rule or retroactively
  authorize continuation; subsequent local preparation is recorded below.
- [x] Verify 378 sealed live files, 108 preparation/operator files, 151 dependencies,
  40 completed attempts and the terminal capture offline. Save findings, 17 labelled
  counterfactuals and verification under
  `data/diagnostics/fulfillment-output-contract-diagnosis-2026-10-18/`.
- [x] Local preparation subsequently authorized; see the output-contract comparison
  preparation below. The diagnosis itself made no prompt changes or model calls.
- [ ] Live execution requires subsequent approval of the frozen plan and payload.
- [ ] Independent human preference and broader story-quality qualification remain
  pending. Structural reliability does not establish preservation or literary merit.
- [ ] Full workflow canary: **ON HOLD; NOT STARTED**.

Production prompt 61 / graph 9 / policy 1, source evidence and canonical artifacts
remain unchanged. **Step 19 IN PROGRESS; Step 20 NOT STARTED.**

### Output-contract comparisons: local preparation 2026-10-18

**PREPARED, VERIFIED AND FROZEN 2026-10-18; approved attempt recorded below.** See the
[frozen 74-call plan](../docs/benchmark_reports/fulfillment-output-contract-v61-plan-2026-10-18.md).

- [x] Prepare A from the exact a01/a03/a05/a06 parents: unchanged F1 versus F2's
  single active patch contract, plus F3's issue-local focus on a01/a03 only.
  Retain ordinary rules/schema and resulting-review validation. F3 shares four
  F2 native-control observations explicitly, with no independent success count.
- [x] Prepare B from all nine exact original/revision packets: unchanged hidden-
  purpose V0, V2 delivery, and predeclared V3 handle-based metadata expansion.
  Retain full prose/context, task/fact/change judgments, mixed ending, no-op,
  minimal repair and within-cited-sentence craft controls. No writer calls.
- [x] Bind V3 handles to trial, side, frozen version and complete catalog record;
  expand only model-selected evidence and the bound version envelope. Reject
  unknown/stale handles and duplicate/missing records. Canonical validation and
  semantic support remain separate; application metadata is not model judgment.
- [x] Fix 74 primary slots: A 20 / B 54, seeds 19801/19803, no retries or transfers.
  Reverse each case's arm order and each block's case order between seeds;
  place negative/craft controls early. Retain the pinned model, temperature 0.2,
  top-p 0.95, thinking false and 24,000 / 8,000 / 900 per-call caps.
- [x] Implement the proposed future diagnostic stop rule: captured, identified,
  in-budget `length` fails its cell without parsing/retry; fixed scheduling can
  continue. Unknown outcomes, missing captures/usage, cancellation, transport,
  identity/integrity drift and exceeded caps stop the run. Old terminal evidence
  and its unused calls remain closed.
- [x] Pass 74 positive fixtures, 916 rejection checks, 56 paired request-delta checks
  and 18 canonical V3 equivalence checks. All requests retain complete packets and
  fit the existing input estimate (13,970–19,592; actual provider usage still capped).
- [x] Pass four complete 74-cell fake matrices: valid, invalid, captured length and
  partial restart. Use 306 fake dispatches including ten terminal fault modes;
  replay 296 completed attempts with final code, including 74 length responses
  with parsing disabled. Completed replay makes zero extra calls; restart after
  three completed slots makes 71. Approval, tamper, budget and lock checks pass.
- [x] Pass 75 focused regressions, repository Ruff/format, strict mypy on 201 files
  and lint/format for eight private helpers. Sandbox async stalls occurred before
  the harness in Windows socket-pair initialization; stopped those processes and
  reran offline with external-network/real-gateway guards. Correct a local fixture
  alias and invalid-response replay serialization before final verification.
- [x] Freeze all 74 requests, exact cases, scoring, stop rules, adapter mappings,
  schedule, code/source dependencies and verification under
  `data/diagnostics/fulfillment-output-contract-v61-2026-10-18/`.
  Plan SHA-256:
  `c8fb871abe6a9e9f4d432dd7a7a47a696dce0547cf671ccd372318a369c426c9`.
  Total reservation ceilings: 1,776,000 input / 592,000 output / 66,600 active
  seconds; historical-rate estimate USD 0.48544, actual charges unknown.
  Seal the plan/report and tracker snapshot with zero live/discovery calls.
- [x] Receive approval on 2026-10-19 for the frozen plan, full unpublished
  prose/context payload and Ollama Cloud destination through the local daemon.
- [x] Complete both live comparisons after an explicitly authorized preflight retry:
  74/74 cumulative inference calls. The original zero-call discovery stop remains
  sealed; see the separate execution records below.
- [ ] Human preference and broader story-quality qualification remain pending.
- [ ] Full workflow canary: **ON HOLD; NOT STARTED**.

Production prompts, graph, policy, canonical artifacts and previous evidence
remain unchanged. **Step 19 IN PROGRESS; Step 20 NOT STARTED.**

### Output-contract comparison execution attempt 2026-10-19

**STOPPED BEFORE INFERENCE — 0/74 CALLS; COMPARISONS NOT RUN.** See the
[attempt report](../docs/benchmark_reports/fulfillment-output-contract-v61-results-2026-10-19.md).

- [x] Record the user's approval against frozen plan
  `c8fb871abe6a9e9f4d432dd7a7a47a696dce0547cf671ccd372318a369c426c9`,
  maximum 74 calls, full prose/context, the specified destination and canary false.
  Verify the preparation seal, exact requests and source dependencies unchanged.
- [x] Attempt the unchanged operator's `all` phase. Model discovery at the local
  Ollama endpoint fails with `ConnectError` / `PROVIDER_UNAVAILABLE` before a
  catalog response or model-identity verification. The operator exits and cleans
  up its lock before dispatching any inference request.
- [x] Honor the frozen whole-run transport stop: no retry, fallback, direct Cloud
  route, prompt change or canary. The adapter's generic retryable flag does not
  override the frozen experiment policy.
- [x] Inspect and preserve the failure log and empty inference ledgers. Record
  A 0/20 and B 0/54 dispatched, zero responses/tokens/active inference time, all
  74 cells unobserved, and qualification not evaluated. No prose/context was sent.
  Seal the offline audit, approval, report and tracker snapshot.
- [x] Receive explicit authorization for a fresh preflight and complete both
  comparisons in the separate retry recorded below. This zero-call attempt stays
  closed; no automatic retry was made.
- [ ] Independent human preference and broader story-quality qualification remain
  pending; no experimental candidate is promoted or downgraded by this stop.
- [ ] Full workflow canary: **ON HOLD; NOT STARTED**.

Production prompt 61 / graph 9 / policy 1, canonical artifacts and previous
evidence remain unchanged. **Step 19 IN PROGRESS; Step 20 NOT STARTED.**

### Output-contract comparison authorized retry 2026-10-19

**COMPLETED — 74/74 CUMULATIVE CALLS; NEITHER PRIMARY CANDIDATE QUALIFIES.** See the
[completed retry report](../docs/benchmark_reports/fulfillment-output-contract-v61-retry-results-2026-10-19.md).

- [x] Record the user's explicit authorization to retry preflight and run both
  frozen comparisons. Retain the original payload/destination approval, all
  74 exact requests, scoring, budgets and stop rules. Production prompts unchanged;
  full workflow canary **ON HOLD; NOT STARTED**.
- [x] Verify the original plan and sealed zero-call attempt. Preserve that attempt
  unchanged; write new evidence under
  `data/diagnostics/fulfillment-output-contract-v61-2026-10-18-live-retry-2026-10-19/`.
  The retry wrapper changes only the evidence destination and adds approval/prior
  closure checks before the unchanged operator. Cumulative inference ceiling: 74.
- [x] Pass pinned Cloud model preflight and complete A 20/20 plus B 54/54 calls in
  the frozen order, one attempt each. No inference retries, writers, replacement
  cases, budget transfers or canary. Preserve six identified, in-budget length
  responses as failed cells without parsing/retry; no cells remain unobserved.
- [x] Inspect all A responses: F1 6/8 structurally valid, 4/8 qualified; F2 0/8
  valid; F3 0/4 valid. All twelve F2/F3 parent hashes fail. F3's four raw comparison
  explanations correctly identify duplication surviving minimal boundary repair,
  but yield zero qualified recoveries. Four native controls delegate to F2;
  they are not independent F3 successes. Preserve a06's inherited rationale caveat.
- [x] Inspect all B responses: V0 0/18 valid (twelve invalid stop, six length),
  V2 15/18 valid, V3 1/18 valid. Paired V2–V0: fifteen validity gains, zero losses;
  V3–V2: zero gains, fourteen losses. V2 omits required neutral-effect evidence in
  three cells; seventeen V3 outputs use bare refs instead of bound handles.
- [x] Separate delivery from substantive support. All 48 nontruncated raw B outputs
  identify expected task/fact/mandatory statuses; invalid outputs remain failures.
  Mixed b02 assessments miss losses/uncertainty; b03 promotes some added imagery
  to necessary repair. Second-seed V2/V3 b07 reports naturalness loss despite
  byte-identical prose. V2 accepts the within-cited-sentence craft control at both
  seeds. No primary candidate qualifies; no post-hoc replacement winner selected.
- [x] Reconcile 74 requests/reservations/captures/outcomes and replay all attempts
  offline, including six length replays with the parser disabled. Verify frozen
  source/code evidence unchanged. Record 1,294,398 input / 127,264 output tokens
  and 550.032 active seconds, all within caps. Actual billing remains unknown.
  Pass helper lint/format, documentation checks and seal the retry evidence,
  inspection, full-prose review export, report and tracker snapshot.
- [ ] Independent human preference and broader story-quality qualification remain
  pending. Retain earlier diagnostic/preservation candidates in their existing
  status; no new story-quality gain or production adoption is established.
- [ ] Full workflow canary: **ON HOLD; NOT STARTED**.

Production prompt 61 / graph 9 / policy 1, canonical artifacts and previous
evidence remain unchanged. **Step 19 IN PROGRESS; Step 20 NOT STARTED.**

### Critic and writer retrospective and human review packet 2026-10-19

**RETROSPECTIVE SAVED; REVIEW MATERIALS PREPARED; USER REVIEW RECEIVED 2026-10-20 BELOW.** See the
[analysis and recommendations](../docs/handoffs/critic-writer-retrospective-and-next-tests-2026-10-19.md).

- [x] Preserve the experiment history, bounded gains, failure diagnosis, unresolved
  hypotheses, and proposed 48-call reviewer / 24-call writer diagnostics. These are
  provisional proposals, not frozen plans or authorization for live calls.
- [x] Prepare all nine existing original/revision pairs as complete unlabeled A/B
  scenes with shuffled order and balanced randomized placement. Save a
  [blind reading packet](../data/human_reviews/critic-writer-2026-10-19/reviewer/01-blind-reading-packet.md),
  [assignment checklist](../data/human_reviews/critic-writer-2026-10-19/reviewer/02-assignment-checks.md),
  and [blank response form](../data/human_reviews/critic-writer-2026-10-19/reviewer/03-response-form.md).
- [x] Keep source identities, construction labels and original/revision placement
  in a separate coordinator key. Verify all 18 prose versions against the frozen
  candidates and sealed exports; preserve all source files. Full prose and review
  materials remain in Git-ignored local storage, outside sealed historical bundles.
- [x] Separate initial literary preference from subsequent assignment compliance
  and task-aware preference. Record the single scene family, shared originals,
  constructed controls, and prior-familiarity limitations in the review guidance.
- [ ] Independent human responses and broader story-quality qualification remain
  pending. Do not fill the review from model judgments or assistant inspections.
- [ ] Further experiments require their own frozen cases, requests, scoring,
  budgets, stop rules, verification and approval. Full workflow canary **ON HOLD**.

Documentation and local packaging only: zero model or discovery calls, no external
transfer, and no production changes. **Step 19 IN PROGRESS; Step 20 NOT STARTED.**

### User review received and mechanical evidence completed 2026-10-20

**COMPLETED USER REVIEW RECORDED; INFORMED READER FEEDBACK, NOT INDEPENDENT BLIND
QUALIFICATION.** See the
[findings and revised review process](../docs/handoffs/critic-writer-human-review-results-2026-10-20.md).

- [x] Preserve the exact submitted form and the user's clarifications in a new
  dated receipt. Record nine overall ties, 45 dimension ties, prior familiarity,
  and the user's assessment of the variants as one promising story foundation.
- [x] Interpret empty substantive fields as no major concerns. Do not invent
  confidence values, numerical scores or timestamps. Record the user's broad
  call-to-investigate interpretation separately from the frozen decision-to-enter
  requirement; do not retroactively alter the original assignment.
- [x] Fill all eighteen editing-request evidence fields from the exact saved
  prose, frozen tasks, writer/post-review records and comparative-review results.
  Attribute these additions to the assistant; preserve every human answer.
  Distinguish four actual writer revisions from five constructed controls, and
  retain invalid model outputs as invalid.
- [x] Reconcile the A/B key and verify the original packet, historical sources,
  exact prose and submitted-review snapshot. Keep the initial manifest unchanged
  and record the intentional response-form update in a separate annotation receipt.
- [x] Record the future human-review division of work in the product contract and
  provide a [short review template](../docs/handoffs/human-story-review-template-2026-10-20.md):
  human feel, emotion, flow, character and story-breaking concerns; prefilled
  mechanical checks and recorded outcomes; grounded semantic evidence and
  uncertainty; meaningful sample selection with less repeated reading.
- [x] Update the retrospective with the new human evidence. Small preservation
  differences are not demonstrated reader harm. Revisit editorial scoring before
  preparing the provisional reviewer/writer experiments; neither is frozen.
- [ ] Independent whole-story comparison, formal human scores, broader quality
  qualification and the full intended corpus remain outstanding.
- [ ] Full workflow canary **ON HOLD**; no new inference or production changes.

Documentation, local evidence completion and review guidance only. Existing
whole-story rubric weights, hard gates, formal coverage and qualification thresholds
remain unchanged. **Step 19 IN PROGRESS; Step 20 NOT STARTED.**

### Gemma and DeepSeek reviewer diagnostic preparation 2026-10-20

**FROZEN AND LOCALLY VERIFIED; SUBSEQUENT LIVE EXECUTION RECORDED BELOW.** See the
[frozen plan](../docs/handoffs/reviewer-gemma-deepseek-frozen-plan-2026-10-20.md).

- [x] Record the user's selection of `gemma4:31b-cloud` and
  `deepseek-v4.1-flash:cloud`. Freeze their full local manifest digests and advertised
  thinking controls; use explicit `think: false`, temperature 0.2, top-p 0.95, and
  seed 20261020. Three metadata-only requests; **zero inference calls**.
- [x] Freeze 12 original/revision pairs across Elara, Elena and the safehouse:
  four existing controls, four constructed assignment/endpoint failures, and four
  permissible variation/craft controls. Preserve exact source versions, full prose,
  catalogs, diffs, construction provenance and prefilled mechanical evidence.
- [x] Freeze **48 complete requests**: 12 cases × V2/C1 × Gemma/DeepSeek, one attempt
  per cell, no retries or fallback. V2 retains its existing judgment and delivery
  instructions; C1 changes diagnostic response delivery to short catalog references
  with application-owned version/quote binding. Paired source/system messages are
  identical; the historical b05/V2 messages reproduce byte-for-byte in r03/V2.
- [x] Freeze scoring that distinguishes delivery, task/fact correctness, mandatory
  failures, necessity, supported comparative claims, no-op invariance, and literary
  preference. Preserve supported ties and uncertainty; do not equate exact
  preservation with reader benefit or treat assistant taste as a gold answer key.
- [x] Freeze 24 calls per model and 12 per model/interface; 24,000 input and 8,000
  output tokens per call; 300 seconds per call; aggregate reservations 1,152,000
  input / 384,000 output tokens and 14,400 active seconds. Peak-rate planning
  estimate $0.56064 within a $0.60 allowance; actual provider billing remains unknown.
- [x] Freeze fail-closed stop rules, plan-bound future approval, pre-dispatch model
  checks, persisted reservations/raw captures, exact request validation and replay.
  Captured in-budget invalid/truncated cells consume their slots; no salvage or
  reroll. Unknown outcomes, transport errors, drift, tampering, excess usage/time
  and unexpected thinking stop further dispatch.
- [x] Verify **70 tests**: 48 diagnostic harness checks and 22 existing gateway/model
  contract checks. Exercise the complete 48-cell matrix through in-memory HTTP
  transport, restart without repeated calls, schema/citation failures, truncation,
  usage/model failures, cancellation, tampering and approval/lock boundaries.
  Reproduce archived V2 validation at **15/18**. Ruff lint/format and strict mypy
  pass on all five private diagnostic scripts.
- [x] Seal private preparation under
  `data/diagnostics/reviewer-crossover-v61-2026-10-20/`, including cases, requests,
  scoring, stop rules, code, verification and source hashes. Full prose remains
  under ignored `data/`; the repository handoff records the reviewable plan.
- [x] User subsequently approved this exact frozen plan, the 48-call ceiling and
  full-prose/context transmission to Ollama Cloud through the local daemon.
  See the completed execution below; prior budgets were not reused.
- [ ] Full workflow canary **ON HOLD**. Whole-story quality qualification, broader
  corpus coverage and independent human comparison remain outstanding.

Preparation only. Production prompt **61**, graph **9**, fulfillment policy **1**,
runtime routing, schemas, historical evidence and human checkpoints remain unchanged.
**Step 19 IN PROGRESS; Step 20 NOT STARTED.**

### Gemma and DeepSeek reviewer diagnostic execution 2026-10-20

**COMPLETED AND INSPECTED: 48/48 CALLS, NO RETRIES.** See the
[results and diagnosis](../docs/benchmark_reports/reviewer-gemma-deepseek-v61-results-2026-10-20.md).
The linked frozen plan remains an immutable preparation-time record.

- [x] Record plan-bound user approval for both exact deployments, full prose/context
  and the Ollama Cloud destination through the local daemon. Reverify the frozen
  preparation, requests, source/runtime hashes and model metadata before dispatch.
- [x] Execute all 48 scheduled cells once: **34 valid, 14 invalid, zero truncated**,
  no terminal stop, no fallback and no repair calls. Capture and replay every cell.
  Usage: 715,222 input / 61,683 output tokens and 323.40 active generation seconds.
  Recorded-rate estimate **$0.20505836**; actual provider charges remain unknown.
- [x] Inspect all shuffled normalized assessments before consulting model/interface
  identities, and inspect invalid raw answers separately. Preserve frozen scores,
  per-cell notes, exact evidence, scoring sensitivities and unresolved support.
  Coordinator inspection does not constitute independent human quality validation.
- [x] Record valid / usable supported assessments, each out of twelve:
  Gemma V2 **5 / 4**, Gemma C1 **12 / 7**, DeepSeek V2 **10 / 6**,
  DeepSeek C1 **7 / 5**. Total usable: **22/48**.
- [x] Retain **Gemma/C1 as promising diagnostic evidence** under the frozen rule:
  usable gains without paired mandatory/fact loss or new mandatory false alarms.
  DeepSeek/C1 does not meet the improvement criterion; all five of its invalid
  reports exceeded the six-reference evidence-array maximum.
- [x] Document remaining failures: no-op comparative loss; departure mistaken for
  erased truce; invented prior comparison; misleading token-fragment explanations;
  and necessary/optional label confusion. Distinguish genuine false claims from
  answer-key ambiguities and conditional grammar dependencies. Do not rescore
  failures as successes or equate local wording preferences with reader benefit.
- [x] Verify the original seal and all 48 completed cells without inference; verify
  inspection/aggregation coverage and local links. Ruff lint/format and strict mypy
  pass on the two new private analysis scripts. Preserve local closure and evidence.
- [ ] Any revised diagnostic interface or further experiment requires its own
  frozen plan and approval. No next budget or prompt change has been prepared.
- [ ] Full workflow canary **ON HOLD**. Whole-story quality qualification, broader
  corpus coverage and independent human comparison remain outstanding.

Production prompt **61**, graph **9**, fulfillment policy **1**, routing, schemas
and human checkpoints remain unchanged. **Step 19 IN PROGRESS; Step 20 NOT STARTED.**

### Unresolved critic and writer issue inventory 2026-10-21

**DOCUMENTATION COMPLETE; UNDERLYING ISSUES REMAIN OPEN.** See the
[issue index](../issues/README.md) for fourteen focused, GitHub-ready local drafts.

- [x] Review the critic/writer retrospective, completed human review, latest
  Gemma/DeepSeek results and supporting experiments. Separate resolved work,
  partial mitigations, deferred word-level concerns and scoring ambiguities.
- [x] Create one file per focused issue, with current status, recorded evidence,
  attempted remedies, expected behavior and independently checkable closure criteria.
  Use fixed committed source links suitable for copying into GitHub.
- [x] Preserve the human review's nine ties and distinguish unsupported edit scope
  from demonstrated literary harm. Retain the completed formal evaluations as
  history; do not represent them as missing reviews or qualification of v61.
- [x] Map the older combined 31B draft into focused detection/repair follow-ups
  without altering the historical file. Identify the three proposed preparation
  workstreams in the index; do not implement or freeze them in this task.
- [x] Verify issue inventory coverage, Markdown links, source targets, UTF-8/LF
  encoding and Git whitespace. No production code or sealed evidence changed.
- [ ] GitHub publication is left to the user. Local CW identifiers are not GitHub
  issue numbers; no external issues were created.
- [ ] Further implementation, experiment preparation and live calls remain separate
  work. The full workflow canary stays **ON HOLD**.

Production prompt **61**, graph **9**, fulfillment policy **1**, schemas and human
checkpoints remain unchanged. **Step 19 IN PROGRESS; Step 20 NOT STARTED.**

### Reviewer interface audit and C2 repeat preparation 2026-10-21

**LOCAL PREPARATION COMPLETE; SUBSEQUENT LIVE EXECUTION RECORDED BELOW.** See the
[interface audit](../docs/handoffs/reviewer-interface-audit-2026-10-21.md) and
[64-call frozen plan](../docs/handoffs/reviewer-interface-repeat-frozen-plan-2026-10-21.md).

- [x] Record the user's publication of the fourteen issues and preserve all supplied
  GitHub links. Link local preparation progress without closing or modifying any
  external issue. Relevant design work: CW-007–011; diagnostic targets also include
  CW-001, CW-012 and CW-013. Writer selection and whole-story qualification stay separate.
- [x] Implement isolated diagnostic C2: application-owned version/quote binding,
  separate request relation, edit support and conditional dependency, whole-paragraph
  explanation groups with exact token appendix, and an explicit endpoint judgment.
  Optional requested cleanup remains optional; conditional cleanup cannot authorize
  an unsupported root edit. No-op craft evidence rules are explicit.
- [x] Replay the five saved DeepSeek/C1 cardinality failures against bounds 6/8/12.
  All five fail at six and validate at eight; twelve adds no captured recovery.
  Adopt eight distinct references per field for C2, with no silent trimming. Preserve
  these as offline altered-contract findings, not new live or semantic successes.
- [x] Freeze eight pairs: four unchanged historical packets and four synthetic
  controls across three new settings. Both deployments cross two seeds and both
  labeled presentation orders: **64 calls**, one attempt per cell, no retries,
  writers, fallback models or transferred allowance. Six scene families in total.
- [x] Freeze exact requests, withheld scoring, independent seed/order contrasts,
  diagnostic screening criteria, per-call and aggregate limits, stop/resume rules,
  inherited model identities and the requirement for future plan-bound approval.
  The combined candidate has no concurrent C1 arm; no individual-change causal
  improvement claim is available from this repeat.
- [x] Pass **80 tests**: 58 offline harness tests plus 22 gateway/contract checks.
  Verify all 64 actual adapter wire requests through a mock provider, restart and
  replay, terminal failures, evidence limits, source binding and preserved controls.
  Ruff lint/format and strict mypy pass across six private scripts. Preserve local
  verification, the preparation seal and historical evidence without modification.
- [x] User subsequently approved the frozen plan, **64-call ceiling**, both model
  deployments, full unpublished prose/context and Ollama Cloud through the local
  daemon. Preparation itself made **zero inference and zero discovery calls**;
  the approved execution is recorded below.
- [ ] The full workflow canary remains **ON HOLD**; no candidate is production-qualified.

Private bundle: `data/diagnostics/reviewer-interface-repeat-v61-2026-10-21/`.
Preparation seal SHA-256:
`9246680ddc52832107f5e814a5cddb07c8b436932ab7f368ffb6a523b1a83142`.
Production prompt **61**, graph **9**, fulfillment policy **1**, schemas, routing and
human checkpoints are unchanged. **Step 19 IN PROGRESS; Step 20 NOT STARTED.**

### Gemma and DeepSeek C2 reviewer repeat execution 2026-10-21

**COMPLETED AND INSPECTED: 64/64 CALLS, NO RETRIES; NEITHER MODEL CLEARS THE SCREEN.**
See the [results and diagnosis](../docs/benchmark_reports/reviewer-interface-repeat-v61-results-2026-10-21.md).
The frozen audit, plan, requests, scoring and stop rules remain unchanged.

- [x] Record the user's exact plan-bound approval and verify both archived model
  manifests/capabilities at preflight and before every dispatch. Send the authorized
  full prose/context through the local daemon to Ollama Cloud, one attempt per cell.
- [x] Complete all 64 cells within the original ceiling: **32 valid, 32 invalid,
  zero truncated**, no terminal stop, repair, fallback, writer or canary calls.
  Replay every request, provider capture, receipt and cell seal without inference.
- [x] Inspect all 32 normalized assessments under shuffled identities, persist and
  hash per-review notes before unmasking, then inspect all 32 invalid raw answers
  separately. Retain uncertainty and counterevidence without changing frozen scores.
- [x] Record Gemma **0/32 valid, 0/32 usable**: every response duplicates the root
  endpoint key. Twenty-nine repeated values are identical; three differ in wording
  without differing endpoint status. Six cells have additional structural defects.
  Audit all 64 supplied schemas: no duplicate property/required names. Raw noticing
  remains diagnostic evidence; malformed answers are not promoted to successes.
- [x] Record DeepSeek **32/32 valid, 24/32 all-label-correct, 22/32 usable**.
  Eight valid no-ops remain invariant and sixteen permissible controls avoid mandatory
  false alarms. All h03 cells misattribute missing turning-point content to endpoint
  failure; seven h03/n03 group labels confuse task fulfillment with textual relevance.
  Two h04 reports with correct labels invent an internal contradiction from a later
  departure. Preserve one additional unresolved craft premise in an already-failed cell.
- [x] Record independent seed/order contrasts: DeepSeek usability **6/8 OR and 5/8 RO
  for each seed**; the h04 explanation failures occur in both RO cells. No paired seed
  contrast changes usability. Small correlated samples do not establish general order
  effects, a model winner, causal improvement over C1 or whole-story quality.
- [x] Record usage **605,648 input / 57,250 output tokens**, **252.79 active seconds**,
  historical-rate estimate **$0.17838736**; actual billed cost unknown. All exact call,
  token and time limits hold. No excessive evidence arrays occur under the eight-ref
  policy; this limited result does not close general delivery or evidence issues.
- [x] Verify sealed sources and live replay, inspection coverage, aggregate reproducibility,
  schema uniqueness, local links and UTF-8/LF. Ruff lint/format and strict mypy pass on
  five private analysis/preflight helpers. Preserve closure and evidence locally;
  update the local issue index without changing user-posted GitHub issues.
- [x] Complete the subsequent local delivery-layout investigation and semantic
  contrast design on 2026-10-22, recorded below. Neither model is retrospectively
  qualified; all frozen results remain unchanged.
- [ ] Any further live comparison requires a separate freeze and approval. No
  production adoption or new inference budget is authorized by the local audit.
- [ ] Full workflow canary **ON HOLD**. Writer selection, broader corpus coverage,
  independent whole-story preference and quality qualification remain outstanding.

Private execution bundle: `data/diagnostics/reviewer-interface-repeat-v61-2026-10-21-live/`.
Production prompt **61**, graph **9**, fulfillment policy **1**, schemas, routing and
human checkpoints remain unchanged. **Step 19 IN PROGRESS; Step 20 NOT STARTED.**

### C2 delivery and semantic investigation 2026-10-22

**LOCAL AUDIT AND EVALUATION DESIGN COMPLETE; NEXT COMPARISONS PROPOSED ONLY.**
See the [delivery findings](../docs/handoffs/reviewer-delivery-semantics-audit-2026-10-22.md),
[explicit semantic contrasts](../docs/handoffs/reviewer-semantic-contrast-design-2026-10-22.md)
and [isolated comparison proposal](../docs/handoffs/reviewer-isolated-comparisons-proposal-2026-10-22.md).

- [x] Verify 104 sealed preparation files, two preparation documents and all 465
  execution evidence files. Preserve the original packets, captures and scores.
- [x] Inspect all 32 Gemma raw duplicate-key answers without selecting an occurrence.
  Every answer uses the same root-field sequence; 29 duplicate values are identical,
  and all 32 pairs agree on endpoint status/evidence. Independently reproduce six
  additional task-ID/evidence defect cells. No failed answer is rescued.
- [x] Exercise a single canonical schema layout locally. All 640 property/required
  order mismatches disappear without changing constraints or other message content.
  All 32 valid DeepSeek captures remain valid; all 32 Gemma captures remain invalid.
  Treat schema order as a generation hypothesis, not a demonstrated cause or fix.
- [x] Check constrained-output feasibility separately. Both exact cloud tags reject
  schema enforcement before mocked transport; current official Ollama documentation
  also reports cloud structured outputs unsupported. No provider guard is bypassed.
- [x] Make event versus continuing/final state, fulfillment versus relevance, and
  forbidden transition versus true contradiction explicit. Retain historical controls
  and author fresh counterexamples, permissible changes and a no-op. Keep ambiguity,
  causal scope, evidence support and human literary judgment separate.
- [x] Pass **96 local tests**, Ruff lint/format and strict mypy on two private scripts.
  Record verification and source bindings; update the issue index while preserving
  all user-posted GitHub links and leaving external issues untouched.
- [x] Propose three isolated 16-call pilots (**48 provisional calls**): Gemma layout,
  DeepSeek temporal scope and DeepSeek fulfillment vocabulary. Include unchanged
  controls, fresh families, both display orders and an eight-call sentinel stop for
  systemic delivery failure. No budget is transferred between pilots.
- [x] Prepare and freeze the user-requested three-pilot follow-up on 2026-10-22,
  recorded below. The preceding proposal and offline prototypes remain historical
  artifacts; the new seal binds the exact live-ready diagnostic preparation.
- [x] Obtain subsequent plan-bound approval before inference; the approved
  execution and terminal stop are recorded below. No production change authorized.
- [ ] Full workflow canary remains **ON HOLD**. Writer selection and whole-story
  quality qualification remain separate work; preserve the completed human review.

Private local bundle:
`data/diagnostics/reviewer-delivery-semantics-audit-v61-2026-10-22/`.
**Zero inference and zero daemon discovery calls.** Production prompt **61**, graph
**9**, fulfillment policy **1**, production schemas, routing and human checkpoints
remain unchanged. **Step 19 IN PROGRESS; Step 20 NOT STARTED.**

### Isolated reviewer pilot preparation 2026-10-22

**FROZEN LOCALLY: 48 CALLS MAXIMUM.** Preparation itself made no live calls;
subsequent approved execution and its terminal stop are recorded below.
See the [frozen plan](../docs/handoffs/reviewer-isolated-pilots-frozen-plan-2026-10-22.md).

- [x] Preserve four historical C2 packets and their control messages exactly; assemble
  five fresh complete micro-scene packets with immutable version identities and
  exact catalogs. Freeze nine packets total, including permissible changes, a no-op,
  a true contradiction and independently grouped root/repair/callback decisions.
- [x] Resolve F02's scope explicitly: its contradiction must be identified without
  inventing an assignment/endpoint failure. Resolve F06's compound request into
  required retention and separate optional duplicate removal, with three complete
  sentence edit groups and every token operation owned exactly once.
- [x] Freeze three isolated 16-call pilots: Gemma C2/D1 schema presentation; DeepSeek
  C2/T1 temporal instruction; DeepSeek C2/R1 fulfillment vocabulary. Preserve all
  other factors within each pilot. Cross both presentation orders at seed 20261022;
  counterbalance arm and order dispatch. The 48 cells contain 46 distinct wire
  payloads because the shared h03 C2 control repeats in T and R intentionally.
- [x] Freeze strict delivery and alias validation, label keys, source-bound inspection
  anchors, masked support inspection and the advancement rule. No invalid report is
  repaired into a pass; partial pilots cannot qualify on reduced denominators.
- [x] Freeze independent 16-call allowances, 24,000 input/8,000 output tokens per call,
  300 seconds per call, no retries/repair/writer/fallback calls and no budget transfer.
  Public reference rates checked October 22 give a $0.64256 reservation estimate
  within the $0.80 planning allowance; actual billing remains unknown and uncapped
  by that estimate.
- [x] Implement and verify eight-call sentinel decisions, including stops when the
  unchanged control systematically fails. Bind decisions to all eight receipts;
  test interruption after the final sentinel receipt, tampering, illegal later
  dispatch, unknown outcomes, source integrity and operator locking. Both deployments
  must match archived metadata before any approved invocation dispatches.
- [x] Pass **152 tests**: 130 private diagnostic tests plus 22 gateway/contract checks.
  Exercise all 48 actual adapter wire requests through in-memory HTTP mocks and
  retain all 32 historical duplicate-key captures as negative fixtures. Ruff
  lint/format and strict mypy pass across ten private scripts. Verify the final
  preparation seal, local links and UTF-8/LF; update the local issue index.
- [x] Record the user's subsequent approval against the exact seal, 48-call ceiling,
  both deployments, full unpublished prose/context and Ollama Cloud through the
  local daemon. Preserve the approval in the private preparation bundle.
- [x] Execute within that approval and inspect all returned evidence, respecting
  sentinel and global terminal stops. The run is incomplete at **10/48 attempts**,
  as recorded below; no candidate is qualified on a reduced denominator.

Private bundle: `data/diagnostics/reviewer-isolated-pilots-v61-2026-10-22/`.
Preparation seal SHA-256:
`7256b677fab8fa4f226a0a3e0595339809c6f2af35147e751055df8fe6595cbe`.
**Preparation: zero inference and zero daemon discovery calls.** Production prompt **61**, graph
**9**, fulfillment policy **1**, production schemas, routing and human checkpoints
are unchanged. Historical results and all user-posted GitHub issue links are
preserved. **Step 19 IN PROGRESS; Step 20 NOT STARTED.**

### Isolated reviewer pilot execution 2026-10-22

**INCOMPLETE / TERMINAL STOP: 10/48 ATTEMPTS; RESULTS INSPECTED AND DOCUMENTED.**
See the [results and terminal audit](../docs/benchmark_reports/reviewer-isolated-pilots-v61-results-2026-10-22.md).

- [x] Verify the unchanged preparation seal and both model deployments; dispatch
  ten exact frozen payloads through the local daemon. Nine complete responses and
  one HTTP-500 error are captured. No retry, repair, fallback or budget transfer.
- [x] Enforce D's eight-cell sentinel: Gemma C2 **0/4 valid**, all with duplicated
  root `endpoint_check`; D1 **4/4 valid, label-correct and supported** across h02/F01
  and both orders. Stop D despite candidate success. Its h03 and no-op F04 cells
  remain unobserved; retain limited delivery evidence without qualification.
- [x] Preserve T's terminal HTTP-500 attempt after one valid T1 h04/RO response.
  That answer has correct labels but unsupported contradiction premises in its
  group and naturalness explanations, hence **0/1 usable**. No completed paired
  control exists. R was never started. **38 cells remain unstarted**, not scored
  as failures: eight D sentinel stops, fourteen T and sixteen R terminal stops.
- [x] Read all five valid reports and all four invalid raw replies. Seal source-bound
  notes before consulting the export key; disclose that T's identity was already
  exposed during terminal diagnosis and that delivery status limits other masking.
  Preserve human ties and separate supported premises from literary preference.
- [x] Audit the nine completed cells and failed dispatch offline without resolving
  the reservation or changing the frozen runner. Record the generic terminal-error
  classification and normal replay/export limitation. **10 offline tests**, Ruff
  lint/format and strict mypy pass on three new private post-run scripts.
- [x] Record known usage: **87,201 input / 7,737 output tokens**, 35.099 active seconds
  for nine complete responses; failed-request usage and actual billing unknown.
  Count the failed request among the ten attempts and retain its full reservation.
- [x] Apply the frozen decision: **all three pilots incomplete, no advancement**.
  Update the local issue index, preserve all fourteen GitHub links and issue bodies,
  and make no external issue changes. All issues remain open.
- [x] Address terminal HTTP evidence and offline audit/export locally in the
  separate support bundle recorded below. Preserve the original sealed runner,
  terminal marker, reservation and captures.
- [x] Specify and locally verify the continuation policy and executable seal below,
  carrying forward all ten attempts and retaining D's sentinel stop. The user
  selected one exact recovery; live continuation still requires new approval.
- [ ] Full workflow canary remains **ON HOLD**. No production adoption, writer
  selection or whole-story quality qualification follows from this partial run.

Private live bundle:
`data/diagnostics/reviewer-isolated-pilots-v61-2026-10-22-live/`.
The terminal marker, failed reservation, raw captures and preparation seal remain
intact. Production prompt **61**, graph **9**, fulfillment policy **1**, production
schemas, routing and human checkpoints are unchanged. **Step 19 IN PROGRESS;
Step 20 NOT STARTED.**

### Reviewer terminal evidence support 2026-10-22

**COMPLETE LOCALLY: ZERO LIVE INFERENCE AND ZERO DAEMON DISCOVERY CALLS.**
See the [support decisions and commands](../docs/handoffs/reviewer-terminal-evidence-support-2026-10-22.md).

- [x] Add sixteen explicit non-200 response fixtures, including HTTP 500, other
  provider/auth/rate-limit statuses, HTML/empty bodies, redirects and misleading
  length/usage fields. Keep non-200 captures out of answer/length evaluation.
- [x] Preserve the original gateway exception, code, retryability and cause/context
  chain in sealed terminal evidence. Retain failed reservations and distinguish
  dispatched attempts from preflight failure. Unreported tokens/cost stay null.
- [x] Add supported offline audit/export commands for the isolated pilot format,
  with compatibility pinned to the actual historical bundle. Replay completed
  receipts and verify terminal attempts separately; do not rescue or rescore them.
- [x] Export the actual interrupted run into a new local directory: **10 attempts,
  9 complete responses, 1 unknown-usage HTTP failure**, D stopped, 38 unstarted.
  Verify source immutability and preserve the original preparation/execution seals.
- [x] Pass **58 tests** (36 local diagnostic + 22 gateway/contract checks), Ruff
  lint/format and strict mypy on three private scripts. Exercise all 48 cells using
  mocks, completed-cell restart, sentinel retention, no terminal retry, tampering,
  overwrite prevention and the real historical capture without network calls.
- [x] Document the implementation and update the local issue index, retaining all
  fourteen GitHub links and original issue bodies. No external issue is changed.

Private support bundle:
`data/diagnostics/reviewer-terminal-evidence-v61-2026-10-22/`.
Its successor runner accepts only an in-memory transport and has no live command.
This completes the requested local support work; it does not authorize continuation
or alter the interrupted pilot's conclusions. Production prompt **61**, graph **9**
and fulfillment policy **1** remain unchanged. Canary **ON HOLD**; **Step 19 IN
PROGRESS; Step 20 NOT STARTED**.

### T/R reviewer continuation preparation 2026-10-22

**COMPLETE LOCALLY; AWAITING LIVE APPROVAL. ZERO INFERENCE OR DAEMON DISCOVERY CALLS.**
See the [frozen continuation plan](../docs/handoffs/reviewer-tr-continuation-frozen-plan-2026-10-22.md).

- [x] Freeze the user's chosen one-time exact recovery of **T-h04-C2-RO** as attempt
  two, followed by the fourteen untouched T cells and sixteen R cells. Carry the
  completed T1 h04/RO response and its unsupported interpretation unchanged.
- [x] Count **10 prior + at most 31 new = 41 combined attempts**, within the original
  **48-call ceiling**. Explicitly amend T's allowance from 16 to 17 and DeepSeek's
  from 32 to 33 for this named exception only. D stays at eight and stopped;
  seven original slots are unallocated and unavailable. No further retries.
- [x] Preserve the original source packets, all 31 request files byte-for-byte,
  both display orders, settings, scoring, inspection anchors and eight-logical-cell
  sentinels. Keep delivery-attempt accounting separate from comparison cells.
- [x] Bind a separate continuation ledger to the immutable prior evidence. Add
  daemon-version checks at approved preflight, before/after each call and across
  clean restarts; verify the original DeepSeek digest/capabilities before dispatch.
  Any new terminal failure stops all calls, retaining gateway chain and unknown usage.
- [x] Verify terminal-aware audit/export, unchanged logical-cell scoring, carryover
  of the unmasked T1 notes, source-safe exports and rejection of the old approval.
- [x] Pass **93 tests** (71 continuation + 22 gateway/contract), Ruff lint/format
  and strict mypy on four private scripts. Exercise all 31 wire requests through
  mocks, both sentinel stops, version drift, all sixteen non-200 fixtures, restart,
  authorization bindings and tamper guards. Preserve the initial test-fixture
  failure record and corrected final verification; no live request was made.
- [x] Seal the plan and document decisions; update the local issue index while
  preserving all fourteen GitHub links and issue bodies. No external issue changes.
- [x] Obtain new approval of this continuation before live preflight or inference,
  explicitly covering full prose/context, destination and 31 new / 41 total calls.
- [x] Execute, inspect and document the bounded continuation after that approval;
  results and the unchanged frozen advancement decisions are recorded below.
- [ ] Full workflow canary remains **ON HOLD**; no production adoption or story-quality
  qualification follows from local harness verification.

Private preparation:
`data/diagnostics/reviewer-tr-continuation-v61-2026-10-22/`.
Frozen plan SHA-256:
`1372bb40e4ccb75fb746ca4e888d007b68bdc8d4d49095a3fd138ba2fe9ac201`.
The prior HTTP-500 reservation remains charged with unknown usage; the old terminal
run stays closed. No approval record or live continuation directory existed at
preparation closure; the subsequently approved execution is recorded below.
Production **prompt 61 / graph 9 / fulfillment policy 1** and human judgments remain
unchanged. **Step 19 IN PROGRESS; Step 20 NOT STARTED.**

### T/R reviewer continuation execution 2026-10-22

**COMPLETE: 31 NEW CALLS, 41 COMBINED ATTEMPTS; NO ADVANCEMENT FOR T OR R.**
See the [continuation results](../docs/benchmark_reports/reviewer-tr-continuation-v61-results-2026-10-22.md).

- [x] Verify the frozen seal and record approval before inference. Match daemon
  **0.40.8**, the archived DeepSeek digest and capabilities; preserve exact request
  bytes, original settings, source versions, cases, scoring and stop rules.
- [x] Execute the one authorized exact recovery of **T-h04-C2-RO** and all remaining
  scheduled T/R cells. Count all ten prior attempts, retain the HTTP-500 reservation
  and unknown usage, and carry the unsupported T1 response/inspection unchanged.
  D remains stopped at eight calls; seven unallocated original slots stay unavailable.
- [x] Record **30 valid + 1 invalid** new reports, all HTTP 200 with normal stop
  finishes; no new HTTP/terminal/length failure or further retry. Both T/R sentinels
  pass with 4/4 valid per arm. The later T-F01-C2-OR response is invalid JSON with
  an unclosed root and six misplaced fields inside craft, not a length finish;
  retain its invalid receipt without inference repair or semantic rescue.
- [x] Read all 31 exported reports and audit all 30 valid assessments against source
  text/context. Seal source-bound judgments before opening the new arm/order key;
  disclose condition-revealing wording and the already-unmasked carried T1.
- [x] Record T C2 **7/8 valid, 3/8 label-correct, 3/8 usable** versus T1 **8/8 valid,
  5/8 label-correct, 4/8 usable**. T1 loses successful controls and has no both-order
  family recovery. Two F02 reports wrongly make the separate motion contradiction
  mandatory; every T h03 report folds the lost earlier event into the endpoint.
- [x] Record R C2 and R1 each **8/8 valid, 6/8 label-correct, 5/8 usable**. R1 fixes
  h03 fulfillment labels in both orders (**8/8 correct group labels versus 6/8**),
  but the endpoint error persists. All eight h03 reports across T/R make that error.
  Both interfaces correctly handle F05/F06's independent duplicate repairs.
- [x] Apply unchanged decisions: T and R **retain_limited_evidence_no_advancement**;
  D **incomplete_no_advancement**. Preserve R1's narrow label improvement as
  diagnostic evidence, with no production or literary-quality qualification.
- [x] Record new usage **208,787 input / 29,417 output tokens**, **140.616 active
  seconds**; combined known usage **295,988 / 37,154**, **175.716 seconds**. New
  reference-rate estimate **$0.09793650**, combined known **$0.11631656**; aggregate
  actual usage/billing remain unknown because of the original failed attempt.
- [x] Pass **9 post-run offline tests**, Ruff lint/format and strict mypy on four
  analysis scripts. Verify all request/receipt bindings, source-grounded notes,
  counters, sentinels, tamper rejection, invalid preservation and decision replay.
  Retain the sealed 93-test preparation record; no preparation or production code changed.
- [x] Seal execution/analysis evidence, publish the local result document and update
  the local issue index. Preserve all fourteen GitHub links and issue bodies;
  no external issue edit/closure or additional live call occurred.
- [x] Complete local regression fixtures for requirement attribution/aggregation
  and the malformed C2 capture; verification and the unapproved next proposal
  are recorded in the 2026-10-23 follow-up below. No prompt change is implemented.
- [ ] Full workflow canary remains **ON HOLD**.

Private execution:
`data/diagnostics/reviewer-tr-continuation-v61-2026-10-22-live/`.
Execution manifest SHA-256:
`0f1dd72cda2767af82ec1814de1ff89dc8a6d6eece1ae83acf9be3855451d546`.
Private inspection/analysis:
`data/diagnostics/reviewer-tr-continuation-v61-2026-10-22-analysis/`.
Analysis manifest SHA-256:
`28600949de8908c2ec30ad4417dd081b1148a989c37bfc518ed5df5800d734f1`.
Production **prompt 61 / graph 9 / fulfillment policy 1**, historical evidence and
nine human ties remain unchanged. **Step 19 IN PROGRESS; Step 20 NOT STARTED.**

### Reviewer scope and malformed-output regressions 2026-10-23

**COMPLETE LOCALLY: ZERO LIVE INFERENCE AND ZERO DAEMON DISCOVERY CALLS.**
See the [regression handoff](../docs/handoffs/reviewer-scope-regressions-2026-10-23.md)
and [proposed requirement-ownership comparison](../docs/handoffs/reviewer-requirement-ownership-proposal-2026-10-23.md).

- [x] Preserve all **32 logical T/R responses** as source-bound fixtures: 31 new
  continuation captures and one carried T1 response; 31 valid, one invalid.
  Bind source/version IDs, complete prose/context, original expected labels,
  requests, raw body, receipts and inspection. Replay the original validator and
  scorer without accepting repairs or changing historical outcomes.
- [x] Reproduce **eight h03 endpoint errors, one h04 earlier-event error and two
  F02 mandatory-scope errors**. The same two F02 errors also violate the critics'
  own task-to-aggregate consistency; do not count them twice. Preserve successful
  F01/F05/F06 controls and unsupported explanations in otherwise correct reports.
- [x] Add local ownership controls crossing event retention and final state, plus
  narrow/broad mandatory scope with the same craft defect. Keep defects visible;
  optional success cannot cancel a mandatory loss. Preserve uncertainty and
  reject missing, duplicate or undeclared task/requirement identities.
- [x] Retain the exact malformed C2 response as invalid JSON after normal stop:
  **4,165 characters, 860 output tokens**, unclosed root and misplaced fields.
  Reject a brace-only in-memory mutation under the unchanged schema. Distinguish
  length, non-200, duplicate-key and capture-integrity failures; no answer repair.
- [x] Pass **81 tests** (72 new local + nine unchanged post-run), Ruff lint/format
  and strict mypy on three new scripts. Verify the supported offline audit,
  tamper rejection, source seals and unchanged historical decisions. Preserve
  the initial test-authoring failure record and corrected final verification.
- [x] Document decisions and a **provisional 48-attempt** DeepSeek C2/M1 comparison:
  twelve cases across four fresh families, both orders, one requirement-ownership
  card intervention, separate evidence/mapping/aggregation scoring and explicit
  controls for real craft defects. No cases, requests or live plan are frozen.
- [x] Seal local artifacts and update the issue index; preserve all fourteen
  user-posted GitHub links and original issue bodies. No external issue changes.
- [x] Select and locally prepare the proposed comparison after the user's
  authorization; the frozen C2/M1 preparation is recorded below.
- [x] Review the frozen cases/requests/scoring/budget/stops and obtain the user's
  new plan-bound approval. The completed 48-call execution is recorded below;
  further live calls remain paused.
- [ ] Full workflow canary remains **ON HOLD**. No issue closure, production
  adoption, writer-policy qualification or whole-story benefit is established.

Private regression bundle:
`data/diagnostics/reviewer-scope-regressions-v61-2026-10-23/`.
Regression manifest SHA-256:
`2792d986cc5f04e3642513fb289f68f7dae654eef91103a3b75d723615307c10`.
Historical accounting remains **41 combined attempts**, D stopped, original
HTTP-failure usage unknown and seven unallocated slots unavailable. Production
**prompt 61 / graph 9 / fulfillment policy 1**, original seals and nine human
ties remain unchanged. **Step 19 IN PROGRESS; Step 20 NOT STARTED.**

### C2/M1 requirement-ownership preparation 2026-10-23

**COMPLETE LOCALLY; ZERO INFERENCE OR DAEMON DISCOVERY DURING PREPARATION.**
The subsequent approved execution is recorded below; this preparation stays sealed.
See the [frozen C2/M1 plan](../docs/handoffs/reviewer-ownership-frozen-plan-2026-10-23.md).

- [x] Freeze twelve cases in four fresh fiction families: community radio and
  costume workroom event/endpoint 2×2 contrasts; conservatory and sound archive
  identical-prose narrow/broad mandatory-scope pairs. Versions are **268–296 words**.
  Keep permitted departure, independent optional cleanup and genuine contradiction
  controls; bind source catalogs, paragraph groups, exact offsets and withheld labels.
- [x] Freeze **48 requests: 24 C2 + 24 M1**, both display orders, one seed, with
  unchanged C2 system/schema/evidence policy/grouping/vocabulary. M1 adds only an
  assignment-derived ownership card, with no gold labels or selected evidence;
  bind card content hashes and artifact versions. Production prompts are unchanged.
- [x] Freeze DeepSeek settings, archived model digest/capabilities and daemon
  **0.40.8** expectation, 24,000/8,000 per-call token bounds, 300-second active
  limit, **1,152,000 input / 384,000 output** and **14,400 seconds** aggregate.
  Archive the **$0.80640** reference-rate reservation and **$1.00** planning
  allowance, explicitly separate from actual billing. No fresh price/discovery call.
- [x] Freeze the A01/CN eight-call sentinel, per-arm 24-call ceilings, zero retries,
  terminal stop for non-200/transport/length/usage/thinking/version/model failures,
  durable reservations, exact-wire guard, restart/replay and terminal audit/export.
  The earlier seven unused slots remain unavailable; this is a new separate budget.
- [x] Freeze strict delivery and complete-report scoring, source-bound claim
  inspection, separate mandatory aggregation and real-contradiction detection.
  Require at least **22/24 valid M1 reports**, no lost paired usable/target/craft
  control, and both-order grounded recoveries across an A/B and C/D family.
  Count only the relevant semantic failure class, not delivery-only gains,
  one-order gains or post-hoc aggregate repairs. Passing remains diagnostic only.
- [x] Pass **119 tests** (97 preparation/harness + 22 gateway/contract), Ruff
  lint/format and strict mypy on five private scripts. Exercise all 48 adapter
  requests through mocks, restart without duplicate dispatch, sentinel thresholds,
  all sixteen non-200 fixtures, terminal accounting/export, evidence binding,
  target-specific screening and tamper rejection. Preserve initial failures and
  their local corrections; no live provider request or daemon discovery occurred.
- [x] Seal preparation, source/runtime fingerprints and public plan; run sealed
  verification. Update the issue index, preserving all fourteen GitHub links and
  original issue bodies. No external issue changes or issue closure.
- [x] Obtain new plan-bound live approval covering full prose/context, Ollama Cloud
  through the local daemon, **48 maximum attempts / 24 per arm**, zero retries and
  no canary. No approval record or live execution directory exists at preparation.
- [x] Execute and inspect only after approval; keep production prompts unchanged
  and full workflow canary **ON HOLD**. No story-quality qualification follows
  from preparation, mock outputs or diagnostic screening.

Private preparation:
`data/diagnostics/reviewer-ownership-v61-2026-10-23/`.
Frozen plan SHA-256:
`d5d71fb62ccbe39ec1dad871fbfc9b44f9a3ade09e63d87521d33769105b091d`.
The **74-file** preparation seal binds five scripts, cases, requests, policies,
local case inspection and verification; **35** source/runtime files and the
public plan are also pinned. Previous seals and the nine human ties remain
unchanged. Production **prompt 61 / graph 9 / fulfillment policy 1**;
**Step 19 IN PROGRESS; Step 20 NOT STARTED.**

### C2/M1 requirement-ownership execution 2026-10-23

**COMPLETE: 48/48 CALLS; LIMITED EVIDENCE, NO ADVANCEMENT.**
See the [C2/M1 results](../docs/benchmark_reports/reviewer-ownership-v61-results-2026-10-23.md).

- [x] Verify the frozen preparation and record plan-bound approval for full
  prose/context to Ollama Cloud through the local daemon before preflight.
  Match daemon **0.40.8**, model digest/capabilities and every frozen wire request;
  preserve all cases, source versions, settings, scoring and stop rules.
- [x] Execute **24 C2 + 24 M1 attempts**, with zero retries or replacement calls.
  Both initial sentinels pass 4/4 valid; all 48 responses are HTTP 200, normal stop,
  with no thinking, length or terminal failure. Keep the separate earlier budget
  at 41 attempts, D stopped and seven unused slots unavailable.
- [x] Preserve **35 valid + 13 invalid** reports. Eleven repeat `group_id` keys
  (27 repeated occurrences with identical values); one closes JSON prematurely;
  one cites absent `R020`. Retain every raw failure without repair or semantic credit.
- [x] Inspect all 35 valid assessments against complete prose/context with arm
  and order hidden. Seal **425 field-bound claims** and source/version/offset
  evidence before decoding the key; record unsupported and uncertain premises
  separately from literary preference. Audit all thirteen rejected captures.
- [x] Record C2 **16/24 valid, 14/24 target-correct, 12/24 usable** versus M1
  **19/24 valid, 19/24 target-correct, 15/24 usable**. All 20 valid A/B reports
  correctly separate event and endpoint; twelve A/B cells remain invalid,
  including all four A00 cells. No event/endpoint treatment recovery is shown.
- [x] Retain **CN's both-order mandatory-scope recovery**: M1 reports the real
  contradiction without elevating it into the narrow mandatory aggregate. Both
  arms correctly block CB, and all valid C/D reports identify both incompatible
  assertions. DN controls already succeed; no second scope recovery exists.
- [x] Apply frozen **retain_limited_evidence_no_advancement**: M1 misses the
  22/24 valid threshold, loses both B01 controls through delivery and A01/RO
  usability through an uncertain comparative premise, and lacks the required
  A/B plus C/D recoveries. Preserve correct labels alongside false consultation-
  before-action explanations; do not treat the aggregate projection as a repair.
- [x] Record **265,282 input / 49,109 output tokens**, **208.036 active seconds**
  and **$0.13851540** at archived reference rates. Actual billing remains unknown.
- [x] Pass **23 offline post-run tests**, Ruff lint/format and strict mypy on
  four analysis scripts. Verify exact requests, budget/runtime, all invalid
  captures, source-bound notes, tamper rejection and decision replay with HTTP
  blocked. Preserve the initial two incorrect exception expectations and final
  passing record; retain the unchanged sealed **119-test** preparation evidence.
- [x] Seal execution and analysis artifacts, document results and next local
  recommendations, and update the issue index while preserving all fourteen
  GitHub links and original issue bodies. No external issue edits or closures.
- [x] Complete the local delivery audit and separate aggregate evaluation below
  before proposing another bounded live comparison. No new experiment is frozen
  or approved; further live calls remain paused.
- [ ] Full workflow canary remains **ON HOLD**; no production adoption or
  story-quality qualification follows from this diagnostic.

Private execution:
`data/diagnostics/reviewer-ownership-v61-2026-10-23-live/`.
Private analysis:
`data/diagnostics/reviewer-ownership-v61-2026-10-23-analysis/`.
Execution manifest SHA-256:
`0310a354c726882ae2da62e8e0a4bfc4905e01ff172cbe625b15aaa39752507e`.
Analysis manifest SHA-256:
`7dc4fd1c531fe6bfe1c8928dac7d4b8611b038b9ee4f5287a73c5ec5defcffaa`.
Production **prompt 61 / graph 9 / fulfillment policy 1**, historical seals and
the nine human ties remain unchanged. **Step 19 IN PROGRESS; Step 20 NOT STARTED.**

### Local delivery and mandatory-aggregation audit 2026-10-23

**COMPLETE LOCALLY: ZERO INFERENCE AND ZERO DAEMON DISCOVERY.**
See the [audit and decisions](../docs/handoffs/reviewer-delivery-aggregation-audit-2026-10-23.md)
and [proposed delivery comparison](../docs/handoffs/reviewer-delivery-repeat-proposal-2026-10-23.md).

- [x] Pin all 48 C2/M1 captures and replay their source/request/receipt bindings,
  historical scores and seals: **35 valid / 13 invalid**, unchanged. All 27
  duplicated group objects start with `group_id` then follow the required-field
  list, repeating that ID. Preserve malformed JSON and unknown-reference failures.
- [x] Compare C2 with exact archived D1 rendering and a local identity-first D2
  prototype. Verify equivalent validation rules, unchanged contract prose and
  aligned property/required lists across 480 object-schema instances. Replay all
  64 older C2 controls: 32 Gemma invalid / 32 DeepSeek valid remain unchanged.
  No raw answer is repaired; Gemma D's prior stop remains intact.
- [x] Evaluate a separate source-bound application aggregate using explicit
  mandatory membership and validated whole reports. Preserve uncertainty,
  optional findings and genuine craft defects. Derived flags match the withheld
  aggregate on **35/35 valid inputs**, versus 33/35 model flags; the two CN
  differences are consistency findings, not repaired successes. All eight
  historically unusable valid reports remain unusable; thirteen invalid inputs
  receive no derived aggregate.
- [x] Add eleven authored controls, including false task verdicts that show why
  correct arithmetic cannot establish semantic truth. Keep original model flags
  and explanations; no production gate, persisted schema or writer dispatch changes.
- [x] Pass **104 offline tests** (81 audit + 23 unchanged execution), Ruff
  lint/format and strict mypy on four scripts. Preserve the initial exact-D1
  renderer failures and corrected verification; historical evidence is unmodified.
- [x] Document a **provisional 48-call C2/D1/D2** delivery comparison: eight cases,
  four historical and four across two fresh families, both orders, sixteen
  attempts per arm. Keep ownership/semantic changes separate and measure the
  application aggregate locally without changing primary scoring.
- [x] Seal local evidence and update the issue index; preserve all fourteen
  GitHub links and issue bodies. No issue closure or external GitHub changes.
- [x] Select and locally freeze the proposed cases, requests, scoring, budget,
  schedule and stop rules; verified preparation is recorded below. Live execution
  still requires new plan-bound approval.
- [ ] Full workflow canary remains **ON HOLD**. No production or story-quality
  qualification follows from this local audit.

Private audit:
`data/diagnostics/reviewer-delivery-aggregation-v61-2026-10-23/`.
Audit manifest SHA-256:
`f69c1a370683fd1342476a21a2df8b505d735b222c21a53b4cc20ddc77374fe7`.
The 62-file seal also binds both public documents; source manifests preserve the
prior execution, analysis, preparation and production fingerprints.
Production **prompt 61 / graph 9 / fulfillment policy 1**, prior budgets/seals
and nine human ties remain unchanged. **Step 19 IN PROGRESS; Step 20 NOT STARTED.**

### DeepSeek C2/D1/D2 delivery preparation 2026-10-23

**COMPLETE LOCALLY; ZERO INFERENCE AND ZERO DAEMON DISCOVERY.**
See the [frozen delivery plan](../docs/handoffs/reviewer-layout-frozen-plan-2026-10-23.md).

- [x] Record the user's between-session update to **Ollama 0.40.9** as the new
  expected baseline, not a discovered version. Preserve the archived DeepSeek
  digest/capabilities and all 0.40.8 evidence; future approved preflight must match.
- [x] Freeze four unchanged historical packets (A00, B10, CN, DB) and four new
  cases across flooded-footbridge and bakery-order families. Retain compound
  loss, supported optional cleanup and identical-prose narrow/broad scope
  contrasts, source/version/offset catalogs and withheld inspection. Prose is
  **270–327 words**; six family clusters, not 48 independent stories.
- [x] Freeze **48 requests: 16 C2 + 16 D1 + 16 D2**, both display orders with
  counterbalanced arm positions. C2 and D1 use their exact archived renderers;
  D2 moves group identity first. Schema semantics, evidence policy and all
  non-schema instructions remain unchanged; no M1 card or semantic intervention.
- [x] Freeze one attempt per cell, zero retries, 24,000/8,000 token bounds,
  300 active seconds per attempt, aggregate reservations of 1,152,000/384,000
  tokens and 14,400 seconds. Preserve the archived-rate **$0.80640** estimate and
  $1.00 planning allowance; actual billing remains unknown.
- [x] Freeze the twelve-call A00/E-clean sentinel, zero-valid and repeated-
  signature stops for every arm, terminal evidence/export, exact-wire guards,
  durable reservations and version checks across calls/restarts. No budget
  transfer; Gemma D remains stopped and prior unused slots remain unavailable.
- [x] Freeze separate delivery and complete-report scoring: 15/16 valid, 7/8
  fresh valid, four paired usable delivery recoveries across two families with
  one both-order case, and no valid/usable/target/craft/optional control losses.
  Prefer D1 if both pass unless D2 adds two fully usable reports without losses.
  Require source-bound notes for every assessment field before decoding the key.
- [x] Retain application-owned aggregation as a separate local diagnostic view
  only. Do not repair model flags, rescore history, dispatch writer instructions
  or treat a derived flag as semantic truth or a production acceptance gate.
- [x] Pass **138 offline tests** (116 preparation/harness + 22 gateway/contract),
  Ruff lint/format and strict mypy on five scripts. Exercise all 48 mocked wire
  requests, restart/ceilings, all-arm stops, sixteen non-200 fixtures, source
  integrity, complete field coverage and candidate preference. Record the Windows
  local-asyncio sandbox limitation; successful tests keep real HTTP blocked.
- [x] Seal cases, requests, executable policies, runtime/source fingerprints,
  verification and public plan. Update the issue index while preserving all
  fourteen GitHub links and original issue bodies; no external issue changes.
- [x] Obtain new plan-bound live approval for full prose/context to Ollama Cloud
  through the local daemon, **48 maximum attempts / 16 per arm**, no retries and
  no canary. Approval was recorded after the preparation closure, against the
  immutable plan hash; the historical preparation seal remains intact.
- [x] Execute, inspect and document after that approval; the completed run is
  recorded below. Production prompts remain unchanged and the full workflow
  canary remains **ON HOLD**.

Private preparation:
`data/diagnostics/reviewer-layout-v61-2026-10-23/`.
Frozen plan SHA-256:
`4afe9850924396075a722056bafabaaaf089615377b3f2264fdee5f6724dd3f0`.
The 69-file preparation seal also pins 48 source/runtime files and the public plan.
Production **prompt 61 / graph 9 / fulfillment policy 1**, historical seals,
earlier budgets and nine human ties remain unchanged. **Step 19 IN PROGRESS;
Step 20 NOT STARTED.**

### DeepSeek C2/D1/D2 delivery execution 2026-10-23

**COMPLETE: 48/48 ATTEMPTS; ZERO RETRIES.** See the
[results and inspection](../docs/benchmark_reports/reviewer-layout-v61-results-2026-10-23.md).
Both candidates receive **retain_limited_evidence_no_advancement**.

- [x] Record the user's full-prose/context approval before dispatch; match the
  frozen model/capabilities and **Ollama 0.40.9** at preflight and every call.
  Execute exactly sixteen attempts per arm, with unchanged wire requests,
  source versions, settings, scoring and stop rules.
- [x] Pass the twelve-call sentinel at **3/4 valid per arm**. Complete all 48
  attempts with HTTP 200 and normal stop, no thinking, truncation, terminal
  failure, retry, budget transfer or daemon-version drift.
- [x] Record **263,746 input / 43,807 output tokens**, **184.664 active seconds**,
  and archived-rate estimate **$0.13169220**. All frozen limits hold; actual
  billing remains unknown. Preserve earlier closed budgets and Gemma D's stop.
- [x] Inspect every field of all **40 valid reports**, with **487 source-bound
  claims**, arm/order hidden and notes sealed before key decoding. Separately
  inspect all eight invalid captures without repair or semantic rescue.
- [x] Record C2 **14/16 valid, 14/16 supported target, 11/16 usable**;
  D1 **11/16 valid, 10/16 target, 7/16 usable**; D2 **15/16 valid, 15/16 target,
  12/16 usable**. D1 misses delivery thresholds and has no qualifying recovery.
  D2 has one qualifying A00/RO recovery, loses valid A00/OR and both usable B10
  controls. Only two C2-invalid cells exist, below the required four recoveries;
  do not expand or relax the frozen screen.
- [x] Retain D2's lack of observed duplicate group IDs as limited component
  evidence. Preserve five duplicate-key reports (twelve duplicated group
  objects), two D1 syntax failures and D2's extra `effect_note` fields.
  None is an outage or truncation; identical duplicate values remain invalid.
- [x] Keep application aggregation separate: **40/40** valid model flags and
  derived flags match the frozen scope. All **22/22** valid contradiction cases
  detect both assertions and all **18/18** valid optional edits are recognized.
  No model flag is repaired. Nine reports still have unsupported premises and
  one more has the wrong group-relation label; correct arithmetic is not truth.
- [x] Pass **20 post-run offline tests**, Ruff lint/format and strict mypy on
  three scripts. Preserve the initial Windows temporary-directory limitation
  and type-annotation correction; final verification uses local temporary
  storage with HTTP blocked. Keep the sealed 138-test preparation unchanged.
- [x] Seal execution/analysis evidence, document findings and next local work,
  and update the issue index. Preserve all fourteen GitHub links and original
  issue bodies; no external issue or production source changes.
- [x] Complete the report's local delivery and explanatory-premise follow-up;
  verification and a provisional next comparison are recorded below. No new
  inference is authorized; no candidate advances to a writer test or canary.

Private execution: `data/diagnostics/reviewer-layout-v61-2026-10-23-live/`.
Private analysis: `data/diagnostics/reviewer-layout-v61-2026-10-23-analysis/`.
Execution manifest SHA-256 (435 files):
`9354d23ca73b7a45230b616cb93d6011c19d69cf6ef28f43fdae9449121a8a55`.
Analysis manifest SHA-256 (21 files, plus the public report):
`c7991a17528d8c846d102ffa672efd5cc9e7fb95f30dc1bcd14323a160b11008`.
Production **prompt 61 / graph 9 / fulfillment policy 1**, historical evidence
and nine human ties remain unchanged. **Step 19 IN PROGRESS; Step 20 NOT STARTED;
full workflow canary ON HOLD.**

### Extra-field and explanatory-premise audit 2026-10-24

**COMPLETE LOCALLY; ZERO INFERENCE AND ZERO DAEMON DISCOVERY.** See the
[audit and fixtures](../docs/handoffs/reviewer-field-premise-audit-2026-10-24.md) and
[proposed next comparison](../docs/handoffs/reviewer-premise-comparison-proposal-2026-10-24.md).

- [x] Replay all 48 C2/D1/D2 captures, preserving **40 valid / 8 invalid** and all
  historical scores. Verify the prior analysis/execution/preparation seals and
  exact requests against wire payloads; production fingerprints remain unchanged.
- [x] Trace the two empty `effect_note` fields in L-A00-D2-OR to captured provider
  content. Find no occurrence in any of the 48 exact requests/wire payloads or
  48 pinned input/runtime files. A bounded 160-capture inventory finds only this
  one affected response; do not generalize it to a model-wide error rate.
- [x] Record that all four craft effects are mixed while only two contain the
  extra field, and all four already have assessments/evidence. Preserve the
  closed schema and rejection; do not infer a deterministic trigger, repair the
  response or claim a discovered internal generation cause.
- [x] Add **20** extra-field mutations covering four craft dimensions and five
  values under all archived layouts, plus tests for required assessments and
  the legitimate uncertainty/evidence exception. Keep all captured bytes intact.
- [x] Bind **26 captured premise examples**: all eleven unsupported claims from
  nine reports plus fifteen supported controls, with complete source context,
  exact fields and source/version/offset evidence. Preserve literary interpretation
  boundaries and the separate wrong group label; do not rescore history.
- [x] Add **nine authored response contrasts**: four supported/unsupported pairs
  and one uncertainty case. Verify that correct labels/aggregate arithmetic do
  not repair unsupported explanations. These test supplied adjudications and
  binding/scoring, not automatic semantic understanding or new model performance.
- [x] Pass **94 offline tests** (74 new + 20 unchanged previous execution tests),
  Ruff lint/format and strict mypy on three new scripts with HTTP blocked.
  Preserve initial/final static verification; no production/frontend changes.
- [x] Propose **32 new attempts**, unchanged D2 versus D2 plus one premise-check
  card, four historical cases plus four fresh counterexample families and both
  orders. Keep delivery protected and distinguish insufficient recovery opportunity
  from demonstrated benefit. D2 remains an unqualified diagnostic baseline.
- [x] Seal the local evidence and both public documents; update the issue index,
  preserving all fourteen GitHub links and original issue bodies. No external
  issue was changed or closed.
- [x] Select the proposal and prepare/freeze exact cases, requests, scoring,
  budgets and stops in the local preparation below. The diagnostic card and
  request bundle now exist; production prompts are unchanged and no live
  approval record exists.

Private audit: `data/diagnostics/reviewer-field-premise-audit-v61-2026-10-24/`.
Audit manifest SHA-256 (14 local files plus two public documents):
`528605218b782574bc6d3d3c1dc77889a9a394da89cf14b060d6f0e2d29780ee`.
Production **prompt 61 / graph 9 / fulfillment policy 1**, prior budgets/seals
and nine human ties remain unchanged. **Step 19 IN PROGRESS; Step 20 NOT STARTED;
live calls PAUSED; full workflow canary ON HOLD.**

### Frozen D2/premise-check preparation 2026-10-24

**COMPLETE LOCALLY; AWAITING NEW LIVE APPROVAL.** See the
[frozen 32-call plan](../docs/handoffs/reviewer-premise-frozen-plan-2026-10-24.md).

- [x] Freeze **eight cases across eight scene families**, both OR/RO orders and
  unchanged D2 versus one fixed premise-check card (PC). Preserve A00, B10,
  E-compound and F-narrow packets and their eight D2 wire requests byte-for-byte.
  Add ferry-terminal, observatory, plant-nursery and map-archive counterexamples.
  Freeze source/version/offset catalogs, complete paragraph groups, acceptance
  labels and withheld inspection anchors. No literary winner is prescribed.
- [x] Freeze **32 requests, sixteen per arm**, the counterbalanced serial schedule,
  exact card, archived model/capability fingerprints and expected Ollama **0.40.9**.
  This is the last verified baseline, not new discovery. Retain temperature 0.2,
  top-p 0.95, seed 20261022, no thinking/streaming, 24k input / 8k output / 300
  active seconds per call, and **zero retries or replacements**. Aggregate
  reservations are 768k input / 256k output / 9,600 seconds; reference cost
  $0.53760 within a $0.75 planning allowance, with actual billing unknown.
- [x] Freeze the **first-eight B10/H-before sentinel**, four calls per arm across
  both families: stop if either arm has zero valid reports or a shared structural
  signature appears at least three times across both families. Retain terminal
  stop, unknown-usage/error-chain capture, exact-wire enforcement, operator lock,
  reserve-before-dispatch, cell seals and clean-boundary restart only.
- [x] Freeze full-field source inspection, secondary unsupported-claim categories,
  supported targets, optional repair and genuine contradiction scoring. Require
  PC **15/16 valid**, **7/8 fresh valid**, and **three paired semantic recoveries
  across two families including one historical case in both orders**, with no
  protected losses or new fresh blanket false rejection. Delivery-only gains do
  not count. Explicitly distinguish **insufficient recovery opportunity**; an
  independent delivery/regression failure still blocks advancement.
- [x] Pass **132 offline tests** (110 harness + 22 unchanged gateway/contracts),
  Ruff lint/format and strict mypy on five private scripts. Exercise all 32
  requests via mocked HTTP, stop/restart/budget behavior, sixteen non-200 fixtures,
  terminal export, inspection binding, opportunity limits and regression precedence.
  Record the Windows async sandbox hang and completed tests with real HTTP blocked.
  Preserve the initial type-check path failure and final successful verification.
- [x] Seal **56 local files, 71 source fingerprints and the public plan**. Update
  this tracker and the issue index while preserving all fourteen GitHub links,
  original issue bodies and historical evidence. No issue is closed or changed
  externally; no new model performance claim is made.
- [x] Obtain plan-bound approval for the 32-call ceiling and full unpublished
  prose/context destination. Record the approval and attempt frozen preflight;
  the terminal version-mismatch result is documented below.
- [ ] Complete the comparison and inspect generated reports. Frozen preflight
  stopped before all model calls; continuation requires an explicit baseline
  amendment and new execution identity, not resume of the terminal ledger.

Private preparation: `data/diagnostics/reviewer-premise-v61-2026-10-24/`.
Plan SHA-256:
`388c3402b1f6c3f09b35f1f121d290e3e4374aecaa2d1384ec32b67c16b93681`.
**Zero inference and zero daemon discovery.** Production **prompt 61 / graph 9 /
fulfillment policy 1**, human checkpoints and nine human ties are unchanged.
Story-quality qualification remains open; these eight short families do not
establish whole-story benefit. **Step 19 IN PROGRESS; Step 20 NOT STARTED;
live calls PAUSED; canary ON HOLD.**

### D2/premise-check execution attempt 2026-10-24

**STOPPED BEFORE INFERENCE; LOCAL TERMINAL AUDIT COMPLETE.** See the
[preflight-stop report](../docs/benchmark_reports/reviewer-premise-v61-results-2026-10-24.md).
The comparison remains **INCOMPLETE**, with **0/32 model calls used**.

- [x] Verify the frozen plan and source fingerprints, bind the user's approval
  to its exact hash, and invoke the approved runner with its unchanged stops.
  The initial daemon-version response did not exactly match **0.40.9**; retain
  `ValueError: daemon baseline changed` and obey the terminal stop.
- [x] Preserve **zero reserved / zero dispatched / zero completed model calls**,
  with no retries, replacements, prose dispatch, model-metadata preflight or
  sentinel evaluation. Keep `not_dispatched` separate from unknown usage on a
  dispatched call; leave actual billing unreported. Do not change the baseline
  or restart this terminal ledger.
- [x] Export the terminal evidence through the supported audit path, seal empty
  inspection notes and replay **`incomplete_no_advancement`**. There are no
  reports or assessment fields to inspect, no model-quality measurements and
  no new evidence for or against the premise-check treatment.
- [x] Document the initial-version observability gap: comparison occurs before
  persistence of the returned version, and the version transport does not save
  its response. The saved evidence cannot identify the observed version. A
  bounded local-log read did not recover it; no extra daemon discovery occurred.
- [x] Pass **14 offline tests**, Ruff lint/format and strict mypy on three new
  analysis scripts, with HTTP sends blocked. Verify approval/source binding,
  exact zero-call accounting, terminal resume rejection, supported empty export,
  tamper rejection and frozen decision replay. Preserve all preparation evidence.
- [x] Seal both terminal files through the execution manifest and **18 local
  analysis files plus the public report** through the analysis manifest. Update
  this tracker and issue index; preserve all fourteen GitHub links, original
  issue bodies and historical results. No external issue was changed or closed.
- [x] Prepare tested version capture before comparison, obtain authorized current
  metadata, and freeze the explicit baseline amendment below with a new execution
  identity. Preserve all cases, exact model messages, settings, scoring and the
  **32-call ceiling**. The amendment is shown for review; inference approval is
  still pending and the original terminal ledger remains non-resumable.

Private terminal run: `data/diagnostics/reviewer-premise-v61-2026-10-24-live/`.
Private analysis: `data/diagnostics/reviewer-premise-v61-2026-10-24-analysis/`.
Execution manifest SHA-256:
`494943141433c8c38c454379013ef705175043802bd754286c8074176c9fd500`.
Analysis manifest SHA-256:
`884a6395eb1e5fcea7f7cc7171921c62e08fdd3790cf9d759fdf044cab13c4a7`.
Production **prompt 61 / graph 9 / fulfillment policy 1**, human checkpoints and
nine human ties remain unchanged. **Step 19 IN PROGRESS; Step 20 NOT STARTED;
live inference PAUSED; full workflow canary ON HOLD.**

### D2/premise-check version-capture fix and baseline amendment 2026-10-24

**COMPLETE LOCALLY; APPROVED AND EXECUTED.** See the execution entry below.
See the [frozen amendment](../docs/handoffs/reviewer-premise-baseline-amendment-2026-10-24.md).

- [x] Preserve the original preparation, approval, zero-call terminal run,
  analysis/report and all seals. Create a separate amended execution identity;
  do not resume the original terminal ledger or replace missing historical data.
- [x] Persist and seal initial/before/after version request/response observations
  before validation, including expected/observed versions, UTC times, response
  status, exact body bytes/hash and parse/transport outcomes. Exclude headers and
  credentials. Add observations to cell seals, terminal evidence and supported
  export; reject incomplete/tampered observations and preserve unknown usage.
- [x] Use the user's metadata-discovery authorization for **four ordered metadata
  requests only**: version, tags, selected-model show, version. Verify **0.40.10**
  before and after, with the selected DeepSeek tag, digest, normalized details,
  capabilities, model information and thinking configuration unchanged. No prose
  or generation request was sent. The old returned-version value remains unknown.
- [x] Copy **43 experimental input files byte-for-byte**, including all **32
  prepared requests**, and verify identical wire payloads. Preserve D2/PC prompts,
  card, cases, schemas, artifact versions, schedule, settings, scoring, stops and
  budget. Pin current metadata and unchanged runtime/source fingerprints.
- [x] Keep **32 total model attempts / sixteen per arm / zero retries**. Prior
  model calls used are zero, so the combined ceiling stays 32. Retain the same
  first-eight sentinel, 24k/8k token limits, 300 active seconds per call, 768k/256k
  aggregate tokens, 9,600 active seconds and archived $0.53760 reservation within
  the $0.75 planning allowance. Actual billing remains unverified.
- [x] Pass **177 offline tests** (110 inherited harness + 45 version/amendment +
  22 unchanged gateway/contracts), Ruff lint/format and strict mypy on seven
  private scripts. Test all 32 mocked requests, restart/ceilings/sentinels,
  version failures at all three checkpoints, non-200/malformed/missing/duplicate/
  invalid-UTF-8 responses, transport failures, terminal export, tampering,
  metadata-only endpoint guards and rejection of old approvals. Real HTTP is
  blocked during tests. Preserve initial/final static verification records.
- [x] Seal **69 local files, 131 source fingerprints and the public amendment**.
  Update the tracker and issue index while preserving all fourteen GitHub links,
  issue bodies and historical performance evidence. No external issue is changed
  or closed; this creates no new reviewer or story-quality result.
- [x] Obtain explicit approval bound to the amended plan hash and original parent
  hash before inference, covering full unpublished prose/context to Ollama Cloud
  through the local daemon and the unchanged 32-call ceiling. At preparation
  closure no approval/live directory existed; the subsequent approval and
  completed execution are recorded below.
- [x] Recheck the approved pinned current baseline, execute the unchanged
  schedule under its stops, inspect every valid report, document the results and
  update this tracker. Further version drift stops rather than refreshing silently.

Private amendment: `data/diagnostics/reviewer-premise-amendment-v61-2026-10-24/`.
Amended plan SHA-256:
`9f3421d30db0e361736146d9adecdb7bf81fd41dd81a46ad422beb63c6d37810`.
Metadata manifest SHA-256:
`0ba49dfc906c82a20eebc87b74b8b2813023d066050713cd56fa66829cf6bcdf`.
**Preparation closure: four authorized metadata requests; zero inference calls.**
The approved execution below used 32 calls. Production **prompt 61 / graph 9 /
fulfillment policy 1**, human checkpoints and nine human ties stay
unchanged. **Step 19 IN PROGRESS; Step 20 NOT STARTED; inference PAUSED;
full workflow canary ON HOLD.**

### Amended D2/premise-check execution 2026-10-24

**COMPLETE: 32/32 CALLS; LIMITED EVIDENCE, NO ADVANCEMENT.** See the
[amended results](../docs/benchmark_reports/reviewer-premise-amendment-v61-results-2026-10-24.md).

- [x] Record the user's exact approval against the amended and parent plan hashes,
  covering full unpublished prose/context to Ollama Cloud through the local
  daemon. Count zero earlier model calls plus **32 new calls**, sixteen per arm,
  with **zero retries** under the unchanged 32-call ceiling.
- [x] Verify **Ollama 0.40.10** and the frozen selected DeepSeek model metadata;
  capture/seal all **65 initial/before/after version observations**. Recheck all
  exact requests, wire payloads and source fingerprints. Preserve the original
  zero-call stop and its missing observed version without retroactive repair.
- [x] Pass the first-eight sentinel (D2 4/4 valid, PC 3/4 valid). Complete the
  schedule without terminal failure, truncation or thinking output. Preserve
  every reservation, response, usage record and strict validation result.
- [x] Export shuffled reports and inspect **31 valid reports / 387 explanatory
  fields** against complete source pairs. Seal exact source-bound notes before
  key decoding. Preserve unsupported versus uncertain claims and reasonable
  literary interpretations. Audit the sole rejected report without repair.
- [x] Record **D2 16/16 valid, 9/16 fully usable; PC 15/16 valid, 6/16 fully
  usable**. Both deliver 8/8 fresh valid reports. PC earns one semantic recovery
  (A00 RO), no both-order historical recovery and no delivery-only recovery.
  Seven eligible D2 premise failures across four families provide sufficient
  recovery opportunity, but four usable losses and one delivery loss prevent
  advancement. Frozen decision: **retain_limited_evidence_no_advancement**.
- [x] Preserve the exact failure distinctions: PC B10 OR cites changed-unit IDs
  U02/U03 where only prose refs are allowed; eight valid reports miss group
  labels; fourteen valid reports contain **25 unsupported fields** (22
  decision-relevant relations/constraints/events, three narrow wording errors).
  Two PC fields remain uncertain. No schema exception or primary score repair.
- [x] Retain successes without generalizing: all valid task/endpoint/mandatory
  labels are correct, separate application aggregation matches on 31/31 valid
  reports, all four real crate contradictions are noticed within narrow scope,
  and all four genuine duplicate-cleanup controls are usable. D2 A00 RO has one
  wrong outcome label. Human preference remains nine ties, not machine preference.
- [x] Reconcile **179,932 input / 31,662 output tokens**, **131.545 active
  generation seconds** and archived-rate estimate **$0.091974**. All ceilings
  hold; usage is complete and actual billing remains unknown. Analysis and
  verification make no inference calls.
- [x] Pass **14 post-run offline tests**, Ruff lint/format and strict mypy on
  three analysis scripts, with real HTTP blocked in tests. Verify tamper
  rejection, version evidence, namespace contamination, paired-loss priority,
  masked-note replay and group-label/event-verdict separation. Preserve initial
  verification failures and final passing records.
- [x] Seal execution and analysis/report evidence; update this tracker and the
  issue index while preserving all fourteen issue bodies and GitHub links.
  No external issue changed or closed.
- [x] Before another live proposal, bind the new evidence-type and false-
  contradiction contrasts locally and audit request-relation semantics. Any
  future schema or taxonomy change needs its own isolated design and controls;
  do not extend this run or automatically promote the premise-check card.

Private execution: `data/diagnostics/reviewer-premise-amendment-v61-2026-10-24-live/`.
Private analysis: `data/diagnostics/reviewer-premise-amendment-v61-2026-10-24-analysis/`.
Plan SHA-256: `9f3421d30db0e361736146d9adecdb7bf81fd41dd81a46ad422beb63c6d37810`.
Execution manifest SHA-256: `8b554a6023b9225b98bcec6a47b05f044eb2cd99a01fd23b40da1b8e38844376`.
Analysis manifest SHA-256: `ff387312984aee7e5e7bbfa491ee155e2c94897479ad3fc1b0edac7fb3ee2e8d`.
Production **prompt 61 / graph 9 / fulfillment policy 1**, human checkpoints and
nine human ties remain unchanged. **Step 19 IN PROGRESS; Step 20 NOT STARTED;
further live calls PAUSED; full workflow canary ON HOLD.**

### Local reference and group-relation audit 2026-10-24

**COMPLETE: LOCAL FIXTURES AND AUDIT; NO NEW MODEL EVIDENCE.** See the
[audit](../docs/handoffs/reviewer-reference-relation-audit-2026-10-24.md) and
[next bounded proposal](../docs/handoffs/reviewer-claim-verification-proposal-2026-10-24.md).

- [x] Bind and replay the rejected U02/U03 capture and all **32 historical
  responses**. Preserve strict rejection, exact requests, raw captures and
  original D2 **9/16** / PC **6/16** usable results. Fingerprint **715 historical
  source files** without changing any frozen input or historical adjudication.
- [x] Add **72 reference mutations** across nine report-row locations, valid
  O/R controls and the retained uncertainty exception. Audit a local catalog-enum
  schema prototype: it rejects the same one capture as the existing boundary
  and preserves the other 31. It adds 2,256–2,592 schema characters and proves
  neither generation improvement nor claim support. No prompt or wire change.
- [x] Bind **42 captured explanation fixtures**: all 25 unsupported and two
  uncertain fields plus fifteen supported controls. Include seven false-
  contradiction fields across four H-before reports. Add **twelve authored
  contrasts** for consultation/action, explanation/action, version ownership
  and genuine contradictions. Preserve qualified literary readings and other
  existing report failures. These are fixed adjudication/scoring regressions,
  not an automatic truth detector or new model/human preference evidence.
- [x] Audit **54 groups**: seven fulfillment-label mismatches and one dependency
  mismatch. Distinguish carrying out the task, touching its subject, permission
  and dependence on another complete edit. Preserve optional cleanup and mixed-
  group uncertainty. Keep frozen gold unchanged. A non-scoring projection that
  omits only the group-label gate would leave D2 at 9/16 and PC at 8/16; it does
  not remove the remaining unsupported explanations or invalid delivery.
- [x] Retain the earlier R1 rename evidence: h03 fulfillment improves in both
  orders, but C2 and R1 both remain 5/8 usable. Do not propose that rename again
  as an untested mechanism or silently adopt a different taxonomy.
- [x] Pass **158 offline tests** (144 new audit cases plus fourteen unchanged
  preceding execution tests), Ruff lint/format and strict mypy on the three new
  private scripts. Block HTTP during tests; verify capture/source/oracle binding,
  tamper rejection, authored contrast replay, uncertainty and independent label
  dimensions. Retain initial and final verification records.
- [x] Seal the new local bundle and public recommendations; update this tracker
  and the issue index. Preserve all fourteen original issue bodies and GitHub
  links. No issue is closed or changed externally.
- [x] Record the user's deferral of provider investigation. Provider attribution
  for semantic failures remains unproven; established delivery limitations and
  interruptions are not erased. Make **zero inference and zero discovery calls**.
- [x] Propose an isolated **24-attempt fixed-claim verification diagnostic**:
  three historical and three fresh families, both source orders and two exact
  repetitions. Separate recognition of supplied claims from generating a full
  review. Preserve supported craft controls, source inspection and strict
  failure accounting. This is a descriptive diagnostic, not a production
  reviewer or a paired improvement claim against historical D2/PC scores.
- [x] Prepare and freeze exact cases, claim controls, requests, scoring, stops,
  metadata and budget; verify locally and present the concrete plan. The
  authorized local preparation is recorded below.
- [x] Obtain separate plan-bound live approval before any inference. The frozen
  24-call plan below was subsequently approved and executed as recorded below.

Private bundle: `data/diagnostics/reviewer-reference-relation-audit-v61-2026-10-24/`.
Audit manifest binds seventeen files, including both public recommendations.
Audit manifest SHA-256:
`1e5e576433777c074a02afe82be993d02708ba61547eddc13f496dbfb644ddbb`.
Historical analysis SHA-256 remains:
`ff387312984aee7e5e7bbfa491ee155e2c94897479ad3fc1b0edac7fb3ee2e8d`.
Production **prompt 61 / graph 9 / fulfillment policy 1**, human checkpoints and
nine human ties remain unchanged. **Step 19 IN PROGRESS; Step 20 NOT STARTED;
live calls PAUSED; full workflow canary ON HOLD.**

### Frozen fixed-claim verification preparation 2026-10-24

**COMPLETE LOCALLY; SUBSEQUENT APPROVED EXECUTION RECORDED BELOW.** See the
[frozen plan](../docs/handoffs/reviewer-claims-frozen-plan-2026-10-24.md).

- [x] Freeze **six complete source pairs and eighteen claims**. H/B/G preserve
  the exact historical packets and nine captured claim texts; K/L/M add fresh
  concert-hall, pottery-workshop and railway-shed scenes and nine authored claims.
  Bind expected judgments, full-source rationales and version/offset evidence.
  Retain true constraint violations and defensible literary criticism alongside
  false contradictions, invented prerequisites and imported original-version acts.
- [x] Freeze **24 attempts: six families × two source orders × two exact
  repetitions**. Interleave H/K in the first eight, followed by B/L and G/M.
  Keep claim positions fixed across source orders and repeats. Bind every exact
  request and wire payload; repeat payloads are identical. Keep ten supported
  and eight unsupported unique claims outside the requests' answer metadata;
  complete execution yields 40 supported and 32 unsupported judgment opportunities.
- [x] Use the compact diagnostic claim contract with strict JSON, record order,
  namespace/cardinality checks, application-owned source binding and bounded
  reasons. Do not add the catalog enum, premise card, new group taxonomy or a
  repair pass. Do not disclose expected labels, prior adjudications or gold
  excerpts. Freeze separate correctness, reason support, citation support,
  uncertainty, invalid-delivery and whole-request usability accounting.
- [x] Freeze descriptive reporting by family/origin/order/repeat, repeat
  disagreement and persistent false-premise acceptance. Mask order/repeat IDs
  for full-source inspection and require sealed notes before key decoding.
  Invalid and dispatched terminal answers stay in attempted denominators;
  unstarted calls are separate. No production advancement threshold or paired
  improvement claim against historical D2/PC results is introduced.
- [x] Pin the last verified **Ollama 0.40.10 / DeepSeek** metadata and unchanged
  temperature 0.2, top-p 0.95, seed 20261022 and thinking=false. Capture no new
  metadata during preparation. Approved live preflight must match rather than
  refreshing silently; retain durable initial/before/after version evidence.
- [x] Freeze **24 total attempts, zero retries**, 24k/8k per-call tokens,
  576k/192k aggregate tokens, 300 active seconds per call and 7,200 aggregate.
  Retain the archived-rate **$0.40320** reservation within a **$0.50** planning
  allowance; actual billing is unknown. Stop on terminal errors, truncation,
  unknown/invalid/excess usage, drift, tampering or incomplete captures. First-
  eight sentinel stops on zero valid or three matching structural failures
  spanning both families. No terminal continuation or transferred allowance.
- [x] Pass **125 offline tests**, Ruff lint/format and strict mypy on seven
  private scripts. Exercise every wire request through the production adapter
  with mocked HTTP, restart/ceilings, terminal export, sixteen non-200 fixtures,
  version capture, structured rejection, source/oracle tampering and scoring.
  Retain the reproduced restricted-Windows asyncio socket-pair stall; completed
  tests run outside that restriction with real HTTP blocked. No inference occurs.
- [x] Seal **51 local files, 733 historical source fingerprints and the public
  plan**; independently verify the seal and regenerate every request. Update
  this tracker and issue index without changing the fourteen issue bodies,
  user-posted GitHub links or historical results. No external issue is changed.
- [x] Obtain explicit approval tied to the plan hash below for full unpublished
  prose/context/claims to Ollama Cloud via the local daemon and the **24-attempt
  ceiling**. Approval and execution were added after preparation closure.
- [x] After approval, check the pinned baseline, execute the frozen schedule under
  its stops, inspect every returned reason/evidence, seal notes before decoding,
  document descriptive results and update the tracker. Do not dispatch a writer
  or begin the full workflow canary.

Private preparation: `data/diagnostics/reviewer-claims-v61-2026-10-24/`.
Plan SHA-256:
`8c02702da5d54df9b3a074f87463e6a7fb97a87e3fbef734f83dedd5b911fff7`.
**Preparation: zero inference calls, zero daemon-discovery calls.** Provider
investigation remains deferred. Production **prompt 61 / graph 9 / fulfillment
policy 1**, human checkpoints and nine human ties stay unchanged. **Step 19
IN PROGRESS; Step 20 NOT STARTED; live calls PAUSED; full workflow canary ON HOLD.**

### Approved fixed-claim execution 2026-10-24

**COMPLETE: 24/24 attempts; `complete_descriptive_only`, no production
qualification.** See the
[results and recommendations](../docs/benchmark_reports/reviewer-claims-v61-results-2026-10-24.md).

- [x] Bind the user's approval to the frozen plan and full unpublished
  prose/context/claim payload to Ollama Cloud through the local daemon. Match
  **Ollama 0.40.10 / DeepSeek** metadata before dispatch and preserve all **49
  version observations**. Keep requests, settings, scoring and stops unchanged.
- [x] Complete **24 calls, zero retries**, with no terminal stop or truncation.
  The first-eight sentinel continued with 7/8 valid responses. Reported usage is
  **92,888 input / 6,773 output tokens**, 29.134 active generation seconds, all
  within the frozen ceilings. Archived-rate arithmetic is **$0.035994**; actual
  billing remains unknown.
- [x] Inspect all **22 valid responses / 66 reasons** against complete sources;
  seal masked notes before decoding order/repetition IDs. Inspect both invalid
  captures separately without repair or semantic credit. Preserve representative
  citation policy and the frozen gold; this is assistant factual adjudication,
  not a new human preference review.
- [x] Record **49/72 correct labels, 48/72 usable claims, 8/24 all-label-correct
  responses and 7/24 fully usable responses**. Unsupported opportunities split
  into 12 correct rejections, **13 false acceptances**, four abstentions and
  three lost to invalid delivery. All **37/37 supported controls in valid
  responses** retain their labels; three more are lost to invalid delivery.
- [x] Preserve the semantic distinctions: H/K accept false status contradictions;
  B accepts invented prerequisites; G abstains on an unsupported earlier-choice
  premise. L is fully usable in 4/4 responses; M has 4/4 correct label triples but
  one unsupported exhaustive action count. Some reasons recognize an error yet
  approve a looser core claim. Do not infer an internal model cause or a general
  historical/fresh advantage from these selected cases.
- [x] Retain **CV-K-OR-2** as duplicate-evidence-key rejection with a conflicting
  label/reason, and **CV-B-RO-1** as nine-reference overflow above the eight-ref
  maximum. Both are HTTP 200 normal stops with complete usage. Among ten repeat
  pairs with both deliveries valid, all label triples match; repeat stability
  includes stable errors. No source-order remedy is demonstrated.
- [x] Pass **16 post-run offline tests**, Ruff lint/format and strict mypy on the
  three new private analysis scripts. Verify actual request/usage/version seals,
  masked inspection provenance, tamper rejection, invalid captures and exact
  frozen score replay with real HTTP blocked. No production code changed.
- [x] Seal execution, analysis and the public report; update this tracker and
  issue index. Preserve all fourteen original issue bodies, user-posted GitHub
  links, historical evidence and scores. No external issue is changed or closed.
- [x] Before another live proposal, extend local delivery regressions for the two
  new captures, retaining the label/reason conflict without normalization credit.
- [x] Audit whole-claim adjudication locally: explicit false factual clauses,
  true constraints and defensible literary inferences remain separate. If the
  audit supports more inference, propose an isolated factual-clause assessment
  before a whole-claim verdict with unchanged controls, fresh families, both
  orders and positive craft controls. The local audit and provisional proposal
  are recorded below; freezing and separate live approval remain outstanding.

Private execution: `data/diagnostics/reviewer-claims-v61-2026-10-24-live/`.
Private analysis: `data/diagnostics/reviewer-claims-v61-2026-10-24-analysis/`.
Execution manifest binds **366 live JSON files** and approval. SHA-256:
`9635d524e8e6491cb576d3c5f2edfab17eaf69945797f2bdfd51050a1dc78832`.
Analysis manifest binds **19 files**, including the public report. SHA-256:
`bca3b1fa2b39fbf1c08c6c939b84da82a80d27b06ebebdc33f706d88369c8685`.
Plan SHA-256 remains:
`8c02702da5d54df9b3a074f87463e6a7fb97a87e3fbef734f83dedd5b911fff7`.
Retain **nine human ties**; report usability and minimal edits do not establish
story quality. Provider investigation remains deferred. Production **prompt 61 /
graph 9 / fulfillment policy 1** and human checkpoints are unchanged. **Step 19
IN PROGRESS; Step 20 NOT STARTED; further live calls PAUSED; full workflow canary
ON HOLD.**

### Local delivery and whole-claim audit 2026-10-24

**COMPLETE LOCALLY; zero inference and zero daemon-discovery calls.** See the
[audit and evaluation caveats](../docs/handoffs/reviewer-whole-claim-audit-2026-10-24.md)
and [provisional 36-call comparison](../docs/handoffs/reviewer-material-claims-proposal-2026-10-24.md).

- [x] Replay the complete 24-call evidence and frozen scoring unchanged: **22/24
  valid, 49/72 correct labels, 7/24 fully usable responses**. Bind **1,174 source
  fingerprints** and preserve original requests, gold, captures and inspection.
- [x] Add unchanged **CV-K-OR-2** duplicate-evidence and **CV-B-RO-1** nine-ref
  fixtures, plus **24 authored boundary mutations** covering all claim positions.
  Retain the invalid capture's supported-label/unsupported-reason conflict.
  Accept structural eight-ref and uncertain-empty controls without semantic
  credit; reject duplicates, overflow, unknown refs and missing required evidence.
- [x] Inventory **18 unique claims and all 66 captured valid judgments**, with
  exact reasons, source versions, offsets, context and existing inspection notes.
  Separate material facts, genuine assignment constraints and defensible craft
  interpretations. Preserve **sixteen authored contrasts**; none is new model
  evidence or a replacement for a historical capture.
- [x] Qualify the previous interpretation of **B/C03 and G/C03**. Deferred-
  consultation logic can express a craft impression; an earlier choice can mean
  across-version comparison rather than within-revision chronology. Keep their
  frozen scores, but do not use ambiguous wording to gate future factual recovery.
  Of thirteen frozen false acceptances, **ten involve explicit factual targets**
  and three B/C03's scope-sensitive claim. Four G/C03 abstentions remain unchanged.
- [x] Preserve recognized-but-excused false clauses, substituted propositions,
  genuine supported controls and the one correct M/C01 label with an overbroad
  explanation. A local conjunction helper operates only on supplied adjudications;
  it is not a semantic classifier, production verifier or automatic relabeling.
- [x] Pass **90 offline tests** (74 new audit tests plus sixteen unchanged prior
  execution tests), Ruff lint/format and strict mypy on three new private scripts.
  Block real HTTP; verify boundary behavior, tamper rejection, source binding and
  historical score replay. Resolve formatting and static import paths locally.
- [x] Seal the audit and both public documents; update this tracker and the issue
  index. Preserve all fourteen original issue bodies and user-posted GitHub links.
  No external issue is changed or closed.
- [x] Propose **36 attempts, zero retries**: six unchanged families plus three
  fresh families, two arms and both source orders. Compare unchanged CV with a
  brief material-premise assessment in the existing reason field; retain schema,
  evidence limits, settings and positive craft controls. Separate the two ambiguous
  probes from primary recovery scoring. Define delivery, recovery, protected-loss,
  insufficient-opportunity and terminal-stop rules without production advancement.
- [x] Following local authorization, create and scope-audit exact fresh
  cases and claims, freeze requests/scoring/stops/budget, verify the harness and
  present the sealed plan. Completed preparation is recorded below; separate
  live approval remains pending.
- [ ] Obtain separate plan-bound approval before any new inference. No writer,
  production role, production prompt change or full workflow canary is authorized here.

Private bundle: `data/diagnostics/reviewer-whole-claim-audit-v61-2026-10-24/`.
Audit manifest binds **21 files**, including both public documents. SHA-256:
`c7b308c95844f3e562bc1d0a010f44e5130a8464a61c70ddb9e852b62de05b79`.
Historical analysis seal remains:
`bca3b1fa2b39fbf1c08c6c939b84da82a80d27b06ebebdc33f706d88369c8685`.
Provider investigation remains deferred. Preserve **nine human ties** and future
human review of feel/emotion, flow, character and story-breaking problems.
Production **prompt 61 / graph 9 / fulfillment policy 1** and human checkpoints
are unchanged. **Step 19 IN PROGRESS; Step 20 NOT STARTED; live calls PAUSED;
full workflow canary ON HOLD.**

### Frozen CV/MC material-claim preparation 2026-10-24

**COMPLETE LOCALLY; APPROVED AND EXECUTED BELOW.** See the
[frozen 36-call plan](../docs/handoffs/reviewer-material-claims-frozen-plan-2026-10-24.md).

- [x] Freeze **nine complete source pairs and 27 claims**. Preserve H/B/G/K/L/M
  packets, eighteen claim texts and historical gold exactly; add floodgate,
  bookbinding and seed-archive families with explicit factual scope, genuine
  constraints and defensible literary controls. Bind source versions, offsets,
  claim hashes and material-check annotations; keep those annotations out of input.
- [x] Freeze **36 attempts, eighteen per arm, zero retries**, both source orders
  and balanced arm order. All twelve historical CV wire payloads match the first
  preceding repetition exactly. MC adds one frozen instruction requiring brief
  material-premise assessment in the existing reason field; schema, evidence
  cardinality, reason length, provider wire settings and production prompts stay
  unchanged. No extra model, correction pass or writer is introduced.
- [x] Keep **B/C03 and G/C03 secondary** with unchanged historical gold, outside
  primary recovery/opportunity/protected-semantic-loss scoring. Each arm has **50
  primary opportunities** (32 supported/eighteen unsupported) plus four secondary.
  Retain invalid and dispatched terminal answers in attempted denominators and
  unstarted calls separately. Correct labels with unsupported reasons remain
  unusable. Material coverage is descriptive; whole-response gold usability is
  secondary, and supported interpretation need not be a unique literary preference.
- [x] Freeze MC's diagnostic screen: **17/18 valid, 5/6 fresh valid**, no paired
  valid-delivery loss; **four paired primary semantic recoveries across two
  families**, including an unchanged claim in both orders and a fresh recovery;
  no protected usable-claim, supported-label or grounded-explanation loss.
  Separate delivery gains and insufficient opportunity. Independent failures
  cannot be hidden by insufficient opportunity. No result qualifies production.
- [x] Pin archived **Ollama 0.40.10 / DeepSeek** metadata, temperature 0.2,
  top-p 0.95, seed 20261022 and thinking=false. Freeze **24k/8k** tokens per call,
  **864k/288k** aggregate, **300/10,800** active seconds and archived-rate
  reservation **$0.60480** within a **$0.75** planning allowance. Actual billing is
  unknown; approved preflight must match without a silent baseline refresh.
- [x] Freeze the first-eight H/N sentinel: stop on zero valid in either arm or
  three matching structural signatures across both families, pooling both arms.
  Preserve terminal stops for non-200/transport/timeout/cancellation, truncation,
  thinking, usage, drift, tampering and incomplete captures. Count all dispatched
  attempts; retain gateway error chains and unknown usage. No terminal continuation.
  A clean boundary restart can dispatch only the untouched frozen remainder.
- [x] Pass **153 offline tests**, Ruff lint/format and strict mypy on seven private
  scripts. Exercise all 36 requests through the production adapter with mocked HTTP,
  exact CV equivalence/MC-only differences, latest duplicate-evidence/nine-ref
  captures, paired score gates, source/inspection tampering, restart/ceilings,
  sixteen non-200 fixtures and durable version evidence. Real HTTP is blocked.
  Retain the interrupted restricted-Windows asyncio run and the completed mock-only
  suite outside that restriction. No inference or daemon discovery occurs.
- [x] Seal **66 local files, 1,196 historical source fingerprints and the public
  plan**. Independently verify and regenerate every request. Update this tracker
  and issue index while preserving original issue bodies, user-posted GitHub links,
  historical results and prior seals. No external issue is changed or closed.
- [x] Obtain explicit approval bound to the plan hash below, full unpublished
  prose/context/claims to Ollama Cloud via the local daemon, **36 total attempts**
  and zero retries. No approval file or live-run directory exists at preparation
  closure; earlier experiment approvals do not authorize this run.
- [x] After approval, execute the frozen schedule under its stops, inspect every
  returned reason/evidence, seal masked notes before key decoding, document paired
  outcomes and update the tracker. No writer or full workflow canary dispatch.

Private preparation: `data/diagnostics/reviewer-material-claims-v61-2026-10-24/`.
Plan SHA-256:
`2b83e01b80ba59cc59ad7cf1a388391b85062e8fb76642cd7da2e2ae0924e84e`.
Public plan SHA-256:
`47db33b1803e5cf3a1573bf90190abf92019e2eacc09581f73b0b199336fd675`.
**Preparation: zero inference calls, zero daemon-discovery calls.** Provider
investigation remains deferred. Preserve **nine human ties** and future reader
review of feel/emotion, flow, character and story-breaking problems. Production
**prompt 61 / graph 9 / fulfillment policy 1** and human checkpoints stay unchanged.
**Step 19 IN PROGRESS; Step 20 NOT STARTED; live calls PAUSED; canary ON HOLD.**

### Approved CV/MC material-claim execution 2026-10-24

**COMPLETE; RETAIN LIMITED EVIDENCE, NO ADVANCEMENT.** See the
[36-call results](../docs/benchmark_reports/reviewer-material-claims-v61-results-2026-10-24.md).

- [x] Bind explicit approval to the unchanged frozen plan, full unpublished
  prose/context/claims and Ollama Cloud via the local daemon. Complete **36/36
  attempts, eighteen per arm, zero retries**, within all frozen allowances.
  Preflight and **73 version observations** match **Ollama 0.40.10 / DeepSeek**.
  Sentinel passes; all generations have HTTP 200, normal stop and complete usage.
  No terminal failure, restart, correction call or unstarted cell.
- [x] Preserve exact requests, raw responses, receipts, usage and per-cell seals.
  Record **141,640 input / 10,828 output tokens**, **53.48 active seconds** and
  archived-rate arithmetic **$0.0554856**. Actual billing remains unknown.
- [x] Inspect all **102 valid reasons** against nine complete source pairs and
  context packets. Seal masked notes before key decoding. Treat this as partially
  masked assistant source adjudication, not human preference.
- [x] Replay the frozen primary/secondary scoring: **17/18 valid per arm**;
  primary labels **42/50 CV, 43/50 MC**; primary usable **42/50 CV, 41/50 MC**.
  All **31 supported primary controls per arm** in valid deliveries retain their
  labels. B/C03 and G/C03 remain secondary, with unchanged historical gold.
- [x] Record sufficient opportunity: **six CV failures across four families**,
  H/C01 in both orders and two fresh N/C02 failures. MC obtains **one recovery**
  (K/C02 OR), but loses K/C02 RO and Q/C03 OR. Four machine loss flags describe
  **two distinct claim/order losses**. No fresh recovery, no unchanged claim
  recovered in both orders, and no delivery gains or paired valid-delivery losses.
  Frozen outcome: **retain_limited_evidence_no_advancement**.
- [x] Preserve remaining failures: all four N/C02 answers endorse a false status
  contradiction; MC-H-RO recognizes consistency but accepts a substitute core;
  MC-H-OR has a correct rejection with an unsupported dismissal of defensible
  craft interpretation; MC-Q-OR adds a false exhaustive packet-handling count.
  L/P/M controls remain successful without establishing a treatment gain.
- [x] Inspect both B/RO invalid captures without repair or credit: each has nine
  distinct catalog-valid references for C03 above the eight-ref bound. No duplicate
  members, unknown references or transport failure in those captures. All six
  affected claim opportunities remain failed delivery opportunities.
- [x] Pass **16 post-run offline tests**, Ruff lint/format and strict mypy on three
  analysis scripts. Check actual requests, ceilings, version/sentinel evidence,
  exact invalid-output replay, all sealed notes, paired scores and tamper rejection;
  HTTP is blocked. Resolve two initial restricted temporary-directory setup errors
  with a new workspace temp path; all sixteen then pass.
- [x] Preserve the frozen plan, 66 bound files and 1,196 historical fingerprints.
  Seal execution/analysis and update this tracker and issue index. Preserve all
  fourteen original issue bodies and user-posted GitHub links; no external issue
  is changed or closed.
- [x] Before any new experiment, add the latest delivery and semantic contrasts
  as local regressions; audit separately stated material assertions and whole-claim
  aggregation while retaining defensible craft interpretation. Address evidence
  cardinality separately. No new live plan or budget is approved here.

Private live captures: `data/diagnostics/reviewer-material-claims-v61-2026-10-24-live/`.
Private analysis: `data/diagnostics/reviewer-material-claims-v61-2026-10-24-analysis/`.
Plan SHA-256:
`2b83e01b80ba59cc59ad7cf1a388391b85062e8fb76642cd7da2e2ae0924e84e`.
Execution manifest SHA-256:
`c79247d211289155425fc4db3516c5e8d4cff6c0446944d8902d6001b622d278`.
Analysis seal SHA-256:
`f35243f068d5a321ddc42be91170cf3d583d29e2a2e012a02b1a01d48f05c9c7`.
Production **prompt 61 / graph 9 / fulfillment policy 1**, human checkpoints and
the nine human ties remain unchanged. Provider investigation remains deferred.
Neither verifier is promoted and no writer dispatch is authorized. **Step 19
IN PROGRESS; Step 20 NOT STARTED; further live calls PAUSED; full workflow canary
ON HOLD.**

### Local aggregation and cardinality audit 2026-10-25

**COMPLETE LOCALLY; NEXT COMPARISON PROPOSED, NOT PREPARED OR APPROVED.** See the
[audit](../docs/handoffs/reviewer-aggregation-cardinality-audit-2026-10-25.md) and
[provisional 32-call CV/CA comparison](../docs/handoffs/reviewer-component-assessment-proposal-2026-10-25.md).

- [x] Preserve the completed **36-call CV/MC** run, frozen scores, source notes and
  report. Verify the analysis seal and **1,829 historical source fingerprints**.
  Primary usable remains **42/50 CV, 41/50 MC**, with one recovery and two distinct
  losses; no new model result or historical rescoring.
- [x] Add both unchanged B/RO overflow captures and **24 authored delivery
  mutations**. Retain strict eight/nine-reference, duplicate-key/reference,
  unknown-reference, definite-evidence and empty-uncertainty boundaries. Neither
  invalid response is repaired, normalized or given partial semantic credit.
- [x] Bind all **102 captured valid judgments** and their exact reasons to the
  sealed source adjudication; inventory **27 claims** and authored material-scope
  annotations. Add **twelve authored semantic contrasts** for status versus
  condition/resolve, craft defensibility, prerequisite scope and exhaustive versus
  narrow handling claims. B/C03 and G/C03 stay secondary and keep historical gold.
- [x] Audit whole-claim aggregation with a local response-boundary prototype:
  exact component coverage/identity, explicit factual/constraint/craft kinds,
  application-derived conjunction, propagated uncertainty, no model override.
  Five authored conditional illustrations show both potential enforcement of a
  recognized false premise and limitations from wrong labels, incomplete
  decomposition, craft overrejection and invented explanations. These are not
  model component outputs, recoveries or a production truth classifier.
- [x] Audit all **108 evidence arrays**: every list has distinct catalog-valid
  refs; only the two B/C03 RO lists exceed eight, each with nine. Authored
  representative eight-ref examples pass the existing structural boundary without
  establishing semantic truth or model reliability. Preserve actual failures.
  Keep the eight-ref bound for the next semantic comparison; count CA's union
  across components per claim, and cap total component reasons at 2,000 characters.
- [x] Pass **91 offline tests**, Ruff lint/format and strict mypy on three private
  scripts. Tests block HTTP and cover capture/quote binding, tamper rejection,
  delivery mutations, all 27 three-component label combinations, missing/duplicate
  components, uncertainty, union/length budgets and explicit non-semantic limits.
- [x] Record **Ollama 0.40.11 as user-reported on 2026-10-25**, not independently
  captured. No daemon query occurs. The last observed baseline stays 0.40.10;
  future preparation must capture current daemon/model metadata and explicitly pin
  its own baseline without revising old evidence.
- [x] Propose **32 CV/CA calls, sixteen per arm, zero retries**, six unchanged
  families plus two fresh ones and both source orders. CV stays unchanged; CA
  assesses supplied components with application aggregation and unchanged evidence
  and reason allowances. Propose delivery/protected-control gates, four paired
  recoveries across two families including both orders and a fresh recovery,
  insufficient-opportunity handling and existing terminal stops. Exact cases,
  component maps, requests and scoring remain future preparation work.
- [x] Update this tracker and issue index; seal local artifacts and public audit/
  proposal. Preserve all fourteen original issue bodies, user-posted GitHub links,
  earlier reports and seals. No external issue is changed or closed.
- [x] Prepare and freeze the accepted comparison's complete cases, component maps,
  requests, scoring, budgets, stops and verified daemon/model baseline. See the
  frozen preparation below; separate live approval remains pending.

Private bundle: `data/diagnostics/reviewer-aggregation-audit-v61-2026-10-25/`.
Local audit manifest SHA-256:
`9e06ca8daeda8fc2f5502a1b60b6f5f1f1d682c68971b260d76743a1654a5524`.
Source analysis seal:
`f35243f068d5a321ddc42be91170cf3d583d29e2a2e012a02b1a01d48f05c9c7`.
**Zero inference and zero daemon-discovery calls.** Production **prompt 61 /
graph 9 / fulfillment policy 1**, human checkpoints and the nine human ties remain
unchanged. Provider investigation stays deferred. **Step 19 IN PROGRESS;
Step 20 NOT STARTED; live calls PAUSED; full workflow canary ON HOLD.**

### Frozen CV/CA component-assessment preparation 2026-10-25

**COMPLETE LOCALLY; FROZEN; LIVE APPROVAL PENDING.** See the
[32-call plan](../docs/handoffs/reviewer-components-frozen-plan-2026-10-25.md).

- [x] Freeze **eight families, 24 whole claims and 71 components**: unchanged
  H/B/K/N/P/Q plus fresh greenhouse U and instrument-conservation V. Freeze full
  original/revised prose, assignments, source identities, component maps, withheld
  gold and rationales. Retain false relational assertions, quantifiers, negation,
  version ownership and qualified literary interpretations in the model-visible
  maps. These are authored decompositions, not autonomous model decomposition.
- [x] Freeze **32 exact requests, sixteen per arm, zero retries**, both source
  orders and balanced arm order. All **twelve historical CV wire payloads match**
  the previous comparison. CA supplies keyed component assessments and derives
  whole labels in the application; it cannot override the aggregate with a final
  model verdict. Diagnostic changes do not alter production prompts.
- [x] Keep evidence at **eight distinct refs per whole claim**, counting CA's
  union across components, and **2,000 total reason characters per claim**. Reject
  incomplete/duplicate/reordered components, extra fields, duplicate JSON and
  invalid refs without repair. Authored examples for all 24 claims fit the bound,
  including B/C03 at eight; they are withheld and receive no model/recovery credit.
- [x] Freeze **46 primary and two secondary judgments per arm**. CA adds 128
  primary and fourteen secondary component opportunities. Correct aggregates
  cannot hide wrong material components or unsupported explanations. B/C03's
  deferred-consultation wording remains a secondary craft interpretation; its
  unchanged unsupported historical gold is reported separately from component
  correctness. No retrospective gold change or primary credit from this probe.
- [x] Freeze CA's diagnostic screen: **15/16 valid, 3/4 fresh valid**, four paired
  primary recoveries across two families including one historical claim in both
  orders and one fresh recovery, with no protected delivery/semantic/reason loss.
  Keep delivery-only gains, insufficient opportunity, abstentions and invalid or
  terminal attempted opportunities separate. No incomplete run advances.
- [x] Independently capture **Ollama 0.40.11** via three successful read-only
  version/tag/show responses. DeepSeek's selected tag, digest, capabilities and
  thinking metadata match the previous capture. Preserve raw sealed responses and
  the earlier sandbox-blocked socket attempt. Preserve all 0.40.10 archives;
  future runtime drift stops execution. Provider attribution remains deferred.
- [x] Freeze **24,000 input / 8,000 output tokens and 300 active seconds per
  attempt**, aggregate 768,000 / 256,000 tokens and 9,600 seconds; archived-rate
  reservation **$0.53760**, planning allowance **$0.70**, actual billing unknown.
  H/U's first eight calls enforce the per-arm zero-valid and pooled recurrent
  structural-failure stop. Retain terminal non-200/error/usage/drift/tamper stops,
  exclusive lock, reservation-before-dispatch, zero terminal retries and only
  clean cell-boundary restart within the untouched original allocation.
- [x] Pass **279 offline tests** (188 new harness, 91 prior aggregation), Ruff
  lint/format and strict mypy on nine new private Python files. Real HTTP is
  blocked in tests. Verify all **1,851 historical source fingerprints**, exact
  control payloads, masked source inspection and complete mock execution/stops.
- [x] Seal **69 local files**, this public plan and historical source identities.
  Update tracker/index in the same change; preserve fourteen issue bodies,
  user-posted GitHub links, prior reports and scores. No issue is closed or
  externally changed; no production qualification or better-story claim is made.
- [x] Obtain separate approval for the frozen full prose/context and claims/
  components payload to Ollama Cloud through the local daemon, then complete
  **32 attempts** and inspect/document results. See the approved execution below;
  preparation itself used no inference.

Private bundle: `data/diagnostics/reviewer-components-v61-2026-10-25/`.
Frozen plan SHA-256:
`ae0f7bb219b2ac76ebbb9165d931444bfb94825e46a3519697e92ac0232d8b40`.
Public plan SHA-256:
`f52eea112c95985b61e249914ee036fc1c7c737304276b719f828cc5e1cf49d5`.
**0/32 inference calls; three successful metadata-only responses.** Production
**prompt 61 / graph 9 / fulfillment policy 1**, human checkpoints and nine human
ties remain unchanged. Future reader review remains about feel/emotion, flow,
character and story-breaking concerns, with machine-prepared mechanics.
**Step 19 IN PROGRESS; Step 20 NOT STARTED; canary ON HOLD.**

### Approved CV/CA component-assessment execution 2026-10-25

**COMPLETE; RETAIN LIMITED EVIDENCE, NO ADVANCEMENT.** See the
[results report](../docs/benchmark_reports/reviewer-components-v61-results-2026-10-25.md).

- [x] Execute all **32/32 frozen calls**, sixteen per arm, with **zero retries**
  and no terminal failure. Preserve exact full-prose/context requests, reservations,
  raw responses and receipts. All **65 version observations** match Ollama
  **0.40.11**; selected DeepSeek metadata matches the frozen baseline. Production
  prompts and all 1,851 historical source fingerprints still verify.
- [x] Enforce the frozen sentinel: **CV 4/4 valid, CA 2/4 valid**, with both
  failures in H, so the recurrent-failure rule across two families did not trigger.
  Continue only within the approved allocation. All responses finish normally;
  no truncation, missing usage, drift or additional model call occurs.
- [x] Record **CV 16/16 valid, 6/16 fully usable; CA 5/16 valid, 2/16 fully usable**.
  Primary usable judgments are **36/46 CV and 12/46 CA**. CA has 31 primary failed
  delivery opportunities; its five valid reports give the same twelve usable
  primary claims as CV in those matched cells. Ten valid control failures provide
  sufficient recovery opportunity; CA yields **zero recoveries and eleven paired
  valid-delivery losses**, with no extra semantic losses among both-valid pairs.
- [x] Audit all **eleven invalid CA captures** without repair or partial credit.
  Each is well-formed, normal-stop JSON with exact component identities but uses
  non-prose evidence refs. Inventory **24 occurrences in twenty fields**: twelve
  artifact-ID, six task-ref, four edit-unit, one artifact-kind and one packet-key
  occurrence. These values are visible in other input namespaces. Thirteen
  affected fields assess constraints. B/C03 also has unions of **13 OR / 11 RO**,
  containing ten/eight prose refs respectively; preserve both additional failures.
- [x] Inspect and seal **21 valid reports, 63 whole reasons and 38 component
  reasons** before decoding trial/order keys. Partial masking is disclosed. CA
  has **35/38 correct delivered components**, with three false C02.A02 status
  relations in U/OR, U/RO and N/OR. The attempted component denominator stays 142.
  Correct fact restatements do not entail a contradiction, and application
  conjunction cannot fix falsely supported components.
- [x] Retain the successful P and V controls without claiming improvement:
  explicit exhaustive violin handling is rejected in both CV orders and valid
  CA/V-OR; before-explaining is distinguished from a before-deciding condition in
  both CV orders and valid CA/P-RO. All supported primary controls in valid reports
  retain correct labels. B/C03 remains secondary with unchanged historical gold;
  both CV explanations support a defensible craft reading, while both CA B reports
  are invalid. Document the narrow Q/RO sequence-reading adjudication explicitly.
- [x] Record **130,894 input / 11,435 output tokens**, **36.23 active generation
  seconds**, maximum **4,945 input / 900 output tokens** and **1.99 active seconds**
  per call. Archived-rate estimate **$0.0529902**, actual billed cost unknown; all
  limits stay within the original ceiling. Analysis uses zero inference calls.
- [x] Pass **twenty post-run offline tests**, Ruff lint/format and strict mypy on
  three analysis scripts. Verify captured-response replay, reference namespaces,
  union cardinality, exact requests/usage, source-bound inspection, tamper rejection
  and frozen scoring. Seal **486 execution JSON files** and fifteen analysis files,
  plus this report; update tracker/index while preserving prior reports, original
  issue bodies and user-posted GitHub links. No issue is closed or externally changed.
- [x] Complete the local evidence-namespace coverage audit, decide diagnostic
  prose/context reference ownership, and add relation-label and resolve/status
  fixtures. See the local follow-up below. No new live budget, prompt change or
  production integration is approved by this audit.

Private execution: `data/diagnostics/reviewer-components-v61-2026-10-25-live/`.
Private analysis: `data/diagnostics/reviewer-components-v61-2026-10-25-analysis/`.
Execution manifest SHA-256:
`011b4e010da1584ff225ff04e3679cca1ec56ab0893cd844e1f0af9bd28d44f8`.
Analysis seal SHA-256:
`c6a4839f084ecbdda3fadcbfdd26f57dba98347be5bd1444e5f7ceddcd36cacb`.
Report SHA-256:
`ee70784e105095263000fd9f4c7665d8d9844a24e5892a8c39ae80aed741672a`.
Production **prompt 61 / graph 9 / fulfillment policy 1**, human checkpoints and
nine human ties remain unchanged. Provider investigation remains deferred; future
reader review remains about feel/emotion, flow, character and story-breaking
concerns. **Step 19 IN PROGRESS; Step 20 NOT STARTED; further live calls PAUSED;
full workflow canary ON HOLD.**

### Local evidence-namespace and relation follow-up 2026-10-25

**COMPLETE; LOCAL REGRESSIONS AND DESIGN ONLY.** See the
[audit](../docs/handoffs/reviewer-namespace-relation-audit-2026-10-25.md) and
[provisional namespace/polarity pilots](../docs/handoffs/reviewer-namespace-polarity-proposal-2026-10-25.md).

- [x] Census all **190 evidence arrays**, comprising 142 CA components and 48 CV
  whole-claim arrays. Retain **24 forbidden occurrences in twenty CA fields**;
  locate every value in the exact input namespaces. Affected fields are
  **13/18 constraint, 4/92 fact and 3/32 craft**. Preserve both B/C03 union
  overflows and all eleven historical invalid reports without repair or credit.
- [x] Audit all eight packets' duplicated context views: **forty mirror checks
  pass**. Identify P/Q's identical-content assignment-version reuse. Prototype
  application-owned, packet-bound O/R prose and C context-leaf identity; resolve
  **81 context leaves plus 295 prose entries**. Keep model source selection,
  the combined eight-reference bound and strict historical rejection. Context
  requirements do not certify manuscript events, and no current boundary changes.
- [x] Preserve **32 byte-identical captured responses**, all 21 sealed valid-report
  adjudications, and **eleven focused relation failures**: eight CV whole claims
  and three CA components. Retain the true-but-incomplete N/OR restatement and
  the two U explanation failures. Application conjunction still cannot identify
  false semantic components; the original **35/38** delivered-component result
  and all frozen scores remain unchanged.
- [x] Add **eighteen authored local contrasts** for compatible status, genuine
  contradiction, actual obligation, fulfilled conditions, resolve, defensible
  craft, false explanatory premises, uncertainty, version/time/subject ownership
  and narrow/exhaustive scope. These are regression annotations, not model
  successes or an automatic semantic classifier. B/C03 stays secondary.
- [x] Pass **100 offline tests** (80 new audit, twenty unchanged execution), Ruff
  lint/format and strict mypy on four new private scripts. Block real HTTP in
  tests; verify **2,427 historical source fingerprints**, capture replay, source
  and registry tampering, cardinality, relation scoring and protected craft.
- [x] Document the ownership decision and propose **two isolated sixteen-call
  pilots, 32 total**: unchanged CA versus a context-citation candidate, and
  unchanged CV versus logically complemented target assertions. Keep delivery
  gains distinct from relation-polarity signals; neither qualifies production.
  Preserve all fourteen issue bodies, posted links and prior reports. No external
  issue is edited or closed.
- [x] Prepare and freeze both pilots, three fresh scene families, exact controls/
  candidates, source bindings, scoring, budget and stops. See the frozen
  preparation below. **Prepared locally; separate live approval still pending.**

Private bundle: `data/diagnostics/reviewer-namespace-relation-audit-v61-2026-10-25/`.
**Zero inference and zero daemon-discovery calls.** Ollama **0.40.11** is the last
sealed observation, not a new availability check. Production **prompt 61 / graph
9 / fulfillment policy 1**, human checkpoints and nine human ties remain
unchanged. Provider investigation is deferred. Future human review remains about
feel/emotion, flow, character and story-breaking details, with machine-prepared
mechanics. **Step 19 IN PROGRESS; Step 20 NOT STARTED; live calls PAUSED; canary
ON HOLD.**

### Frozen namespace and relation-polarity preparation 2026-10-25

**PREPARATION COMPLETE; APPROVED EXECUTION COMPLETED BELOW.** See the
[frozen 32-call plan](../docs/handoffs/reviewer-namespace-polarity-frozen-plan-2026-10-25.md).

- [x] Freeze two independent **sixteen-call pilots**, eight attempts per arm:
  CA/NC reference delivery on H/W/B/V and CV/CP relation polarity on N/X/U/Y,
  with both source orders. Retain all five inherited source/claim packets and
  **ten byte-identical historical control wire payloads**. Author three complete
  fresh families: letterpress state change, foundry same-instant contradiction,
  and archive unresolved timing. No short local fixture is relabeled fresh.
- [x] Freeze **24 original claims, four complete-assertion complements and 41
  component specifications**. The allocation has **96 whole-claim opportunities:
  92 primary and four secondary**, plus 82 component judgments per N arm. Keep
  B/C03 secondary. Preserve exact inner assertion text under CP's sentential
  negation and disclose Y's uncertain-versus-unestablished contract ambiguity.
- [x] Freeze NC's packet-bound O/R/C registry, allowed-value schema and citation
  instructions. Preserve the combined **eight-reference union** and 2,000 reason
  characters per claim. Authored examples fit; B/C03 keeps its eight-ref prose-only
  example. Bare identifiers, duplicate keys, unknown refs, partial delivery and
  both historical B overflows remain rejected without repair or salvaged credit.
- [x] Freeze separate screens for **delivery evidence only** and **relation-framing
  signal only**, with contemporary opportunity checks, both-order controls,
  complete grounded coverage and protected losses. Keep raw CP labels alongside
  normalized target analysis; no formulation-sensitive gain is called a same-claim
  repair. Neither screen can qualify production or authorize writer edits.
- [x] Independently capture three successful metadata-only responses confirming
  **Ollama 0.40.11** and unchanged selected DeepSeek digest/capabilities. Preserve
  the first restricted socket failure separately. Freeze temperature 0.2, top-p
  0.95, seed 20261022, thinking=false, stream=false and no format override.
- [x] Freeze **32 attempts**, zero retries or cross-pilot reallocation; per-attempt
  reservations **24,000 input / 8,000 output tokens / 300 active seconds**.
  Aggregate reservations are 768,000 / 256,000 tokens and 9,600 active seconds;
  archived-rate estimate **$0.53760**, planning allowance **$0.70**, billing unknown.
  Independent eight-call sentinels skip only the stopped pilot; infrastructure,
  drift, tampering, unknown usage and ambiguous dispatch stop the entire run.
- [x] Pass **230 offline tests** (150 new harness, eighty prior regressions), Ruff
  lint/format and strict mypy on nine new private scripts. Block real HTTP in tests;
  verify all **2,477 historical fingerprints**, exact requests, source bindings,
  mock execution, independent stops, clean restart, terminal failure after skipped
  cells, unknown usage, approval binding and masked export. Preserve metadata and
  evidence seals. No production/API/worker/frontend code changed.
- [x] Seal cases, claims, components, complements, registries, requests, scoring,
  budget, stops, verification and this public plan. Update tracker/index while
  preserving fourteen issue bodies, user-posted links and all historical results.
  No issue is closed or externally edited.
- [x] Obtain separate plan-bound approval to send the frozen full prose/context,
  claims, components and registry/complement variants to Ollama Cloud through
  the local daemon within **32 calls**, then execute and inspect. **32/32 calls
  completed, zero retries; both decisions retain limited evidence, no advancement.**

Private bundle: `data/diagnostics/reviewer-namespace-polarity-v61-2026-10-25/`.
Production **prompt 61 / graph 9 / fulfillment policy 1**, human checkpoints and
nine human ties remain unchanged. Provider attribution remains deferred. Future
human review concerns feel/emotion, flow, character and story-breaking details,
with machine-prepared mechanics. **Step 19 IN PROGRESS; Step 20 NOT STARTED;
live inference PAUSED; full workflow canary ON HOLD.**

### Namespace and relation-polarity execution 2026-10-25

**APPROVED RUN COMPLETE; BOTH PILOTS RETAIN LIMITED EVIDENCE, NO ADVANCEMENT.**
See the [results report](../docs/benchmark_reports/reviewer-namespace-polarity-v61-results-2026-10-25.md).

- [x] Execute the exact frozen **32/32 calls**, sixteen per pilot/eight per arm,
  through the local daemon to Ollama Cloud under explicit full-payload approval.
  Preserve all reservations, requests, raw captures, receipts and seals. No
  retries, reallocation, terminal stop or extra inference. All **65 version
  observations match 0.40.11** and selected DeepSeek metadata remains unchanged.
- [x] Complete the N delivery comparison: **CA 3/8 valid, 9/22 usable primary;
  NC 6/8 valid, 13/22 usable primary**. There are three paired delivery gains,
  but only H's two gains count toward four required inherited gains. Four
  contemporary inherited failures provide sufficient opportunity. NC fails
  minimum delivery and gain requirements, with no protected paired loss.
- [x] Audit all seven invalid reports without repair or semantic credit. Five
  CA reports contain twenty wrong-namespace ref occurrences across sixteen
  component arrays. Both NC B/C03 reports use valid refs but exceed the combined
  union with **fourteen each: eight prose and six context**. CA B unions also
  exceed eight (twelve/eleven). All seven are normal-stop, well-formed JSON;
  none is truncated. B/C03 remains secondary with historical gold unchanged.
- [x] Preserve newly delivered semantic failures: H still falsely supports the
  status-relation component in both orders and abstains on defensible craft;
  W/RO rejects an actual endpoint violation despite locating its rule/event.
  W's empty-then-filled relation and both V orders remain successful controls.
  These are diagnostic findings, not semantic recoveries credited from invalid
  controls, and they do not qualify NC for production.
- [x] Complete P: **CV 8/8 valid, 17/24 usable primary; CP 8/8 valid, 16/24**.
  Both have eighteen correct primary labels. All four false-acceptance
  opportunities in N/U recur; CP yields **zero target recoveries**. Normalized
  target labels agree in all eight pairs: two both-correct X pairs, six neither
  under primary gold, zero endorsement of both opposites. CP fails framing,
  uncertainty-control and protected-explanation screens.
- [x] Inspect the false N/OR acceptance-test explanation, incomplete N/RO
  contractual reasoning and CV X/RO missing structured counterpart citation.
  Preserve Y's predeclared uncertain-versus-unestablished ambiguity: true
  observations of missing support are not automatically false timing claims,
  nor do they prove the complete complement. No retrospective gold or prompt edit.
- [x] Source-inspect **25 valid reports, 75 whole reasons and 72 component
  reasons**, sealing masked notes before decoding trial IDs. Disclose partial
  masking and assistant adjudication; no blind human preference claim. Preserve
  exact source/context/claim/component bindings and all seven invalid captures.
- [x] Verify **56 offline post-run tests**, Ruff lint/format and strict mypy on
  three private analysis scripts. Replay all captures, budgets, sentinels,
  labels, explanation/coverage gates, evidence tampering and exact decisions.
  Verify frozen plan/public plan and 2,477 historical fingerprints. Preserve
  all fourteen issue bodies and user-posted links; close or externally edit none.
- [x] Record usage **161,544 input / 12,434 output tokens / 46.754 active seconds**,
  within reservations. Archived-rate arithmetic estimate **$0.063384**; actual
  billed cost unknown. Seal execution manifest, source inspection, analysis and
  report; update authoritative tracker and issue index.
- [x] Audit bounded whole-claim citation planning locally using both NC/B
  fourteen-ref captures. Add regressions for endpoint-label, craft-abstention,
  relation/negation-scope and acceptance-explanation failures. Resolve the
  prospective diagnostic epistemic label contract locally before proposing any
  further live budget. Completed in the 2026-10-26 follow-up below; production
  and historical label contracts remain unchanged.

Private bundles: `data/diagnostics/reviewer-namespace-polarity-v61-2026-10-25/`,
its `-live/` and `-analysis/` siblings. Production **prompt 61 / graph 9 /
fulfillment policy 1**, human checkpoints and nine human ties remain unchanged.
Provider attribution remains deferred. Future human assessment remains focused
on feel/emotion, flow, character and story-breaking details, with machine-prepared
mechanical evidence. **Step 19 IN PROGRESS; Step 20 NOT STARTED; further live
calls PAUSED; full workflow canary ON HOLD.**

### Local citation-budget, relation and uncertainty audit 2026-10-26

**COMPLETE LOCALLY; ZERO INFERENCE OR DAEMON CALLS.** See the
[audit](../docs/handoffs/reviewer-citation-relation-uncertainty-audit-2026-10-26.md)
and [provisional 28-call proposal](../docs/handoffs/reviewer-epistemic-status-proposal-2026-10-26.md).

- [x] Preserve all **32 raw captures**, prior inspection and both limited-evidence
  decisions. Verify **3,061 historical fingerprints**. Historical usable primary
  totals stay CA 9/22, NC 13/22, CV 17/24 and CP 16/24; no old gold, label, prompt,
  request, limit, response or score is rewritten.
- [x] Trace both NC/B/C03 fourteen-ref unions to exact sources/components:
  **eight prose plus six context**, maximum four per component. Three redundant
  context refs can be omitted from an authored alternative witness basis, but
  **eleven remain**. Preserve the eight-ref prose-only convention with its
  implicit-context limitation; eleven is an authored basis, not a proved minimum.
  Neither is a repaired model response. Both historical reports stay rejected.
- [x] Verify an application-owned local citation-plan accounting prototype:
  exact packet/claims/component-map/registry binding, complete component identity,
  source text/version and namespace checks, and the unchanged eight-ref union.
  No automatic evidence selection, silent trimming, dispatch or production
  promotion. Keep the explicit eleven-ref plan over budget. Defer a live citation
  comparison until explicit context coverage and allowance policy are decided.
- [x] Add **32 source-bound regression records**: 22 failure/ambiguity records
  and ten positive controls. Cover status versus rule/resolve relations,
  whole-assertion negation, endpoint rejection, craft abstention, reversed
  acceptance explanations, incomplete reasoning/citations, genuine conflict,
  exhaustive action scope and qualified craft. Preserve Y's disclosed ambiguity.
- [x] Add **eighteen authored local contrasts**, explicitly not new model evidence
  or fresh full-scene cases. Test actual and apparent contradictions, sequential
  states, intention versus obligation, missing versus explicitly unresolved
  premises, before-explaining versus before-deciding, and whole conjunction scope.
- [x] Clarify a **prospective diagnostic** four-status contract: established true,
  established false, unestablished and explicitly unresolved. Map both unknown
  states to uncertain; negation preserves unknown states. False material parts
  refute conjunctions; all-true parts establish them. Keep craft defensibility
  separate. Verify that projection cannot correct a falsely supplied relation
  status and cannot substitute for grounded, complete source inspection.
- [x] Pass **184 offline tests** (128 new plus all 56 prior execution regressions),
  Ruff lint/format and strict mypy on four new scripts, with HTTP blocked. Verify
  byte-identical captures, historical scoring, bounded plans, stale/malformed
  evidence rejection, epistemic projection and source integrity. Seal the private
  bundle and public audit/proposal. No production/API/worker/frontend changes.
- [x] Update tracker/index while preserving fourteen issue bodies and user-posted
  GitHub links. No issue is closed or externally edited. Recommend a single
  **28-call NC/ES evidence-status comparison**: seven full-scene families, both
  orders, fourteen attempts per arm, three fresh families, zero retries, protected
  controls and explicit uncertainty limits. At audit completion this was **not
  prepared, frozen or approved**. Local preparation is completed below;
  its approved execution is completed below.
- [x] Prepare the NC/ES comparison locally: author three full fresh
  families and missing component maps, freeze exact cases/requests/scoring/stops
  and the 28-call ceiling, capture current metadata without generation, verify
  the harness, and show the frozen plan before any separate live approval.
  Completed in the frozen preparation below.

Private bundle: `data/diagnostics/reviewer-citation-epistemic-audit-v61-2026-10-26/`.
Production **prompt 61 / graph 9 / fulfillment policy 1**, human checkpoints and
nine human ties remain unchanged. Provider attribution stays deferred. Preserve
story ambiguity and defensible craft; humans assess feel/emotion, flow, character
and story-breaking details with machine-prepared mechanics. **Step 19 IN PROGRESS;
Step 20 NOT STARTED; live calls PAUSED; full workflow canary ON HOLD.**

### Frozen NC/ES evidence-status preparation 2026-10-26

**COMPLETE LOCALLY. At preparation: 0/28 inference calls used and separate live
approval pending. The approved 28-call execution is completed below.**
See the [frozen plan](../docs/handoffs/reviewer-evidence-status-frozen-plan-2026-10-26.md).

- [x] Freeze **28 attempts, fourteen per arm**, seven full-scene families, both
  orders, zero retries and no reallocation. Preserve H's two historical NC wire
  payloads exactly. Reuse H/U/X/Y source/claims; preserve H/U maps; author X/Y maps
  and three fresh pottery, railway-office and reservoir-record scene families.
- [x] Freeze **21 whole claims, 49 material components**, gold, source-bound
  registries, schemas, exact prepared/wire requests and schedule. Per arm,
  **42 whole claims / 98 components / 14 targets / 84 non-targets** are scored.
  Gold and witness answers never enter model messages. Preserve the same
  eight-reference whole-claim union and 2,000 summed reason-character limit.
- [x] Resolve the proposal's scope ambiguity before inference: ES changes only
  the designated relation to four evidence statuses. Project that target before
  unchanged three-label whole-claim aggregation; retain other component and
  qualified craft semantics. Derived target negation is not a second observation.
  Check whole four-status conjunction/negation only on authored offline fixtures.
- [x] Freeze delivery, exact-status, projected-label, grounded-complete reasoning,
  citation, recovery-spread and protected-loss screens. Require at least 12/14
  valid ES reports, all fresh deliveries, three grounded contemporary H/U
  recoveries across both families and both orders in at least one, all required
  contradiction/compatible/unresolved targets, and no protected losses. Preserve
  legacy uncertainty ambiguity separately; no retroactive gold or score changes.
- [x] Freeze the first-eight-call structural sentinel and global terminal stops.
  Preserve raw gateway/version evidence and unknown usage; prohibit retries,
  terminal restart, ambiguous-cell replay and excess dispatch. Clean-boundary
  continuation uses only remaining original cells. Aggregate reservations:
  **672,000 input / 224,000 output tokens / 8,400 active seconds**; archived-rate
  arithmetic **$0.47040**, **$0.60** planning allowance, actual billing unknown.
- [x] Capture three metadata-only responses confirming **Ollama 0.40.11** and
  unchanged selected DeepSeek tag/show/digest. Retain the initial sandbox
  connection failure without treating it as provider evidence. No generation
  probe or inference occurs; later drift remains terminal.
- [x] Pass **336 offline tests**: 152 new harness tests, 128 preceding local audit
  regressions and 56 prior execution regressions. Ruff lint/format and strict
  mypy pass on ten scripts. Exercise all 28 requests through mocked HTTP,
  sentinels, budget/approval binding, terminal audit/export, unknown usage,
  source tampering and independent losses. Real HTTP is blocked during tests.
- [x] Seal the private bundle/public plan and verify **3,110 historical source
  fingerprints**. Update this tracker and issue index; preserve all fourteen
  issue bodies and posted GitHub links. No issue is closed or externally edited.
- [x] After separate approval of this exact plan, payload, destination and
  28-call ceiling, run the frozen comparison, source-inspect all valid reports,
  document results and update the tracker. Completed below under the recorded
  plan-bound approval; the preparation itself supplied no inference authority.

Private bundle: `data/diagnostics/reviewer-evidence-status-v61-2026-10-26/`.
Production **prompt 61 / graph 9 / fulfillment policy 1**, human checkpoints and
nine prior human ties remain unchanged. Retain only diagnostic evidence even if
the screen passes; do not authorize writer edits or infer better stories from
status projection. Humans assess feel/emotion, flow, character and story-breaking
details with machine-prepared mechanics. Provider attribution and a separate live
citation comparison remain deferred. **Step 19 IN PROGRESS; Step 20 NOT STARTED;
live calls PAUSED; full workflow canary ON HOLD.**

### Approved NC/ES evidence-status execution 2026-10-26

**COMPLETE: 28/28 CALLS; ZERO RETRIES; RETAIN LIMITED EVIDENCE, NO ADVANCEMENT.**
See the [results](../docs/benchmark_reports/reviewer-evidence-status-v61-results-2026-10-26.md)
and unchanged [frozen plan](../docs/handoffs/reviewer-evidence-status-frozen-plan-2026-10-26.md).

- [x] Record approval of the exact frozen plan, 28-call ceiling, full fictional
  prose/context and Ollama Cloud through the local daemon. Run fourteen attempts
  per arm with no probe, replacement, retry or reallocation. All 28 HTTP responses
  finish normally; the first-eight sentinel continues with 4/4 valid per arm.
  No terminal failure occurs. **57/57 version observations match Ollama 0.40.11**;
  selected DeepSeek metadata remains unchanged.
- [x] Record **NC 13/14 valid, 7/14 usable targets, 30/42 usable whole claims;
  ES 14/14 valid, 10/14 usable targets, 35/42 usable whole claims**. Usable
  components are 81/98 versus 89/98; usable non-targets 74/84 versus 79/84.
  ES has 36 correct whole labels, but one correct label lacks complete component
  evidence. Invalid delivery stays in all scheduled denominators.
- [x] Preserve all **four contemporary H/U false-acceptance opportunities and
  zero ES recoveries**. Every H/U target is falsely supported in both arms and
  orders; ES calls each established_true. Separate factual compatibility from
  the actual rule/resolve breach. Preserve wrong-relation substitution and false
  compound premises rather than crediting true fact restatements as recovery.
- [x] Retain ES's **ten correct, grounded required X/Y/fresh targets**, including
  explicitly_unresolved for both Y and F3 orders. NC's Y unsupported labels
  retain their disclosed unestablished interpretation: their factual explanations
  are true, though primary labels are wrong. This run does not test a live gold
  cell requiring the unestablished subtype.
- [x] Inspect two NC endpoint label/reason disagreements: F1/OR and F3/OR explain
  real violations accurately but label the violation propositions unsupported.
  ES labels them correctly. Retain those limited gains without repairing NC.
- [x] Apply protected-loss screens independently of the higher overall score.
  ES loses H/RO craft support and U/OR complete craft evidence. Nine overlapping
  flags describe **two paired cells**, not nine independent failures. H's craft
  readings need defensibility, not unique entailment; U's omitted R010 witness
  cannot be supplied silently from a sibling component. Both recovery and
  preservation screens fail: **retain_limited_evidence_no_advancement**.
- [x] Reject E-NC-F1-RO intact: normal-stop output duplicates claim_id in all
  three claim objects. Preserve raw bytes and all three duplicate members as one
  failed report. No loose-JSON salvage, trimming, retry or semantic credit.
- [x] Inspect **27 valid reports, 81 whole reasons and 190 component reasons**
  against complete source/context; seal masked notes before key decoding.
  Disclose partial masking and assistant adjudication, not human preference.
  Keep source truth, citation sufficiency, coverage and label correctness separate.
- [x] Pass **55 offline post-run tests**, Ruff lint/format and strict mypy on
  three analysis scripts. Verify all raw replays, source/inspection bindings,
  duplicate-key rejection, accounting, uncertainty distinctions, protected losses
  and the exact frozen decision. Preserve the prepared 336-test harness and
  **3,110 historical fingerprints**; make no production code or prompt changes.
- [x] Record **232,418 input / 10,753 output tokens / 44.818 active seconds**,
  within reservations. Archived-rate estimate **$0.082629**; actual billed cost
  unknown. Seal approval, execution, inspection, analysis and report; update this
  tracker and issue index. Preserve fourteen issue bodies and posted links;
  close or externally edit no issue.
- [x] Before another live proposal, preserve new delivery, endpoint-label,
  relation-scope, craft-abstention and incomplete-witness regressions locally.
  Audit explicit assertion-pair/relation identity and label/reason consistency,
  keeping genuine-conflict, uncertainty and craft successes as controls. Require
  a materially different hypothesis before more inference; no new budget is
  frozen or authorized. Any later isolated-pair versus full-scene probe would
  diagnose context sensitivity, not justify removing production story context.
  Completed in the local relation-object audit below; its operating-mode proposal
  is materially different but remains unfrozen and unauthorized.

Private bundles: `data/diagnostics/reviewer-evidence-status-v61-2026-10-26/`,
its `-live/` and `-analysis/` siblings. Production **prompt 61 / graph 9 /
fulfillment policy 1**, human checkpoints and nine human ties remain unchanged.
No writer revision or human preference test ran. Provider attribution remains
deferred. Humans assess feel/emotion, flow, character and story-breaking details
with machine-prepared mechanics. **Step 19 IN PROGRESS; Step 20 NOT STARTED;
further live calls PAUSED; full workflow canary ON HOLD.**

### Local relation-object audit and model assessment 2026-10-26

**COMPLETE LOCALLY; NO NEW MODEL OR DAEMON CALLS.** See the
[relation-object audit](../docs/handoffs/reviewer-relation-object-audit-2026-10-26.md)
and [DeepSeek attribution assessment](../docs/handoffs/deepseek-model-attribution-assessment-2026-10-26.md).

- [x] Preserve byte-identical copies of all **28 NC/ES raw captures**, source
  packets, receipts and sealed adjudications. Add **48 selected component
  regressions** and a separate duplicate-member fixture. Preserve E-NC-F1-RO
  intact as one invalid normal-stop report with three duplicate claim_id members;
  do not salvage JSON, repair, retry or award semantic credit.
- [x] Retain all eight H/U relation errors, two endpoint label/reason mismatches,
  six craft abstentions, the false craft premise and incomplete intention
  witnesses, with genuine-conflict, sequential, uncertainty, rule/intention and
  qualified-craft controls. Tags overlap and are not independent observations.
  Preserve historical labels/gold, NC/Y ambiguity and all prior scores.
- [x] Author **eleven source-bound relation objects**: seven factual pairs and
  four H/U rule/intention pairs, with exact assertions, namespaces, versions,
  timing witnesses and claim/component identity. Audit all eight target reasons:
  six infer a false contradiction from the requested pair, NC-U-OR substitutes
  a real intention conflict, and ES-U-OR conflates resolve and status.
- [x] Verify local identity checks reject stale/substituted commitments without
  claiming semantic truth or correcting model labels. Confirm ES-U-OR's omitted
  R010 craft witness has **zero incremental whole-union cost**; sibling evidence
  cannot silently supply a missing component premise. Keep craft defensibility
  distinct from unique entailment and from factual-premise correctness.
- [x] Assess model attribution using saved evidence and official mode documentation.
  Raw answers establish limitations of the tested DeepSeek deployment/configuration;
  earlier Gemma failures and mixed matched comparisons rule out attributing the
  entire history to DeepSeek. The latest 28 wires request **think: false**; captured
  metadata supports high thinking. Its performance on these cases is untested.
  Do not attribute failures solely to weights, precision or the provider.
- [x] Pass **175 offline tests** (120 new plus all 55 preceding execution tests),
  Ruff lint/format and strict mypy on two new scripts. Real HTTP is blocked.
  Verify **3,632 historical source fingerprints**, exact replays and unchanged
  sealed results; seal the local bundle and both public notes. No application
  code, production prompts, graph or policy changed.
- [x] Update tracker/index; preserve fourteen issue bodies and posted GitHub links.
  No issue is closed or externally edited. Require a materially different
  hypothesis before inference; enum/wording changes alone do not qualify.
- [x] If the user chooses further testing, separately prepare and freeze a matched
  non-thinking/high-thinking comparison with unchanged NC controls/full packets,
  known and fresh families, both orders, protected semantic/craft controls, explicit
  mode/usage accounting, new budget and stops. The current proposal is **unfrozen
  and unauthorized**. A separate later isolated-pair/full-scene probe remains an
  alternative for context sensitivity; do not combine both interventions initially.
  The user selected the 48-call mode comparison; its preparation is completed below.

Private bundle: `data/diagnostics/reviewer-relation-object-audit-v61-2026-10-26/`.
Production **prompt 61 / graph 9 / fulfillment policy 1**, human checkpoints and
nine human ties remain unchanged. Machines prepare mechanics; humans assess
feel/emotion, flow, character and story-breaking details. Provider attribution
remains deferred. **Step 19 IN PROGRESS; Step 20 NOT STARTED; live calls PAUSED;
full workflow canary ON HOLD.**

### Frozen DeepSeek thinking-mode preparation 2026-10-26

**COMPLETE LOCALLY; 0/48 INFERENCE CALLS USED; SEPARATE LIVE APPROVAL PENDING.**
See the [frozen plan](../docs/handoffs/reviewer-thinking-mode-frozen-plan-2026-10-26.md).

- [x] Freeze **48 attempts, 24 per mode**, twelve full-scene families, both
  presentation orders and zero retries. Compare the same DeepSeek deployment with
  **think: false (NC)** versus **think: high (TH)**. Keep each paired wire request
  identical except for think; interleave modes with twelve pairs starting each way.
- [x] Preserve all seven existing cases/claims/maps and fourteen historical NC
  message sequences exactly. Add five fresh 281–313-word originals: letterpress,
  ferry boathouse, aquarium, bakery photographs and radio ledger. Separate factual
  compatibility from real rule/intention conflicts, genuine simultaneous conflict,
  explicitly unresolved timing and missing timing evidence. Retain assignment,
  endpoint, decision and qualified-craft controls.
- [x] Freeze **36 claims / 83 components**, complete source/version bindings,
  registries, withheld gold/witnesses, exact prepared/wire requests, schemas,
  authored examples, readable casebook and schedule. Per mode: **72 whole claims,
  166 components, 24 targets and 142 non-targets**. Preserve the NC three-label
  contract, eight-reference whole-claim union and 2,000 summed reason characters.
- [x] Freeze equal limits of **24,000 input / 16,000 total generated tokens /
  600 active seconds per call**, with 40,000 requested context capacity. Aggregate
  reservations: **1,152,000 input / 768,000 generated / 28,800 active seconds**.
  Thinking and final output share the generated-token limit. Archived-rate estimate
  **$1.26720**, planning allowance **$1.50**, actual billing unknown. These are
  ceilings, not forecasts; the larger common allowance changes historical wire
  settings, while contemporary NC/TH pairs differ only in mode.
- [x] Freeze mode-observation and accounting checks, first-eight delivery sentinel,
  and global terminal stops. Nonempty TH thinking is required to observe the
  manipulation; absence is unverified mode delivery, not semantic incapacity.
  Preserve normal malformed reports, raw terminal errors, unknown usage, failed
  reservations and clean-boundary-only continuation. No probes, retries,
  reallocation, terminal restart or mid-run budget adjustment.
- [x] Freeze six grounded paired recoveries across H/U/G1/G2 with sufficient
  contemporary opportunities and order spread; at least **22/24 valid TH**, all
  **ten fresh deliveries**, all **sixteen required target controls**, and no
  protected target, whole-claim, non-target, craft, citation or delivery losses.
  Insufficient opportunity and incomplete execution cannot advance. Keep known
  and fresh results separate; no generic model or production qualification.
- [x] Capture latency, provider timing, input/cache counts, generated tokens and
  explicitly reported reasoning breakdowns. Preserve unknown splits; never infer
  tokens from characters. Report paired ratios and input/generated/combined tokens
  and time per usable report. Score only final content; exclude thinking and
  resource measurements from the masked source-review export. Do not use a trace
  to rescue an incorrect final answer or pass it into story truth/writer context.
- [x] Capture three metadata-only responses confirming **Ollama 0.40.11** and
  unchanged selected DeepSeek metadata with false/high supported. Preserve the
  sandbox connection failure separately. No generation occurs. Requested sampling
  settings match, but effective mode-dependent sampling remains unverified.
- [x] Pass **381 offline tests**: 206 new preparation tests, 120 preceding audit
  regressions and 55 prior execution tests. Ruff lint/format and strict mypy pass
  on eleven scripts. Exercise all 48 calls through MockTransport; block real HTTP.
  Verify **3,678 historical source fingerprints**, seal the public/private plan,
  and update tracker/index while preserving fourteen issue bodies and posted links.
- [x] Obtain separate approval of this frozen plan, the full unpublished fictional
  prose/context payload, Ollama Cloud via the local daemon, and the **48-call
  ceiling**. Complete execution and source inspection; results are recorded below.

Private bundle: `data/diagnostics/reviewer-thinking-mode-v61-2026-10-26/`.
No live approval file or live run exists at preparation. Production **prompt 61 /
graph 9 / fulfillment policy 1**, human checkpoints and nine human ties remain
unchanged. No writer or human-preference test is included. Selective production
thinking, a lower-thinking arm, another model and context isolation are deferred.
Humans assess feel/emotion, flow, character and story-breaking details with machine-
prepared mechanics. **Step 19 IN PROGRESS; Step 20 NOT STARTED; live inference
PAUSED; full workflow canary ON HOLD.**

### Approved DeepSeek thinking-mode execution 2026-10-26

**COMPLETE — 48/48 calls; retain limited evidence, no advancement.** See the
[NC/TH results](../docs/benchmark_reports/reviewer-thinking-mode-v61-results-2026-10-26.md).

- [x] Execute the exact approved freeze: 24 NC (`think: false`) and 24 TH
  (`think: "high"`) calls through the local daemon to Ollama Cloud. Preserve
  all original requests, source versions, raw responses, reservations, receipts
  and seals. No retries, replacements, extra probes or terminal failure. All
  97 daemon-version observations match **0.40.11** and model metadata matches.
- [x] Observe all 24 TH responses with nonempty thinking and all 24 NC responses
  without thinking. Score final content only; exclude thinking and resource
  observations from the masked review. Do not claim independent verification of
  internal effort allocation or effective sampling.
- [x] Preserve **NC 23/24 valid; TH 24/24 valid**. M-NC-F1-OR repeats claim_id in
  all three claim objects and remains one invalid delivery without repair or
  semantic credit. The first-eight sentinel passes at four valid per mode.
- [x] Inspect and seal **47 valid reports, 141 whole reasons and 326 component
  reasons** against full source/context before decoding the trial key. Keep
  label accuracy, factual truth, citation support and completeness separate.
- [x] Record **eight of eight grounded TH recoveries** across H/U/G1/G2 in both
  orders, including both fresh relation families. NC/TH usable targets are
  **8/24 versus 16/24**, usable whole claims **48/72 versus 62/72**, usable
  components **137/166 versus 156/166**, and usable complete reports **5/24
  versus 14/24**. This is operating-mode diagnostic evidence, not story preference.
- [x] Preserve five endpoint label/reason alignment gains and craft-label gains
  alongside failures. TH fails eight uncertainty controls: seven accurate
  unestablished explanations with unsupported labels, plus F3/RO's supported
  conditional substitution. F3/OR loses NC's correct uncertain judgment.
- [x] Preserve two H craft explanation defects: OR's inaccurate direct-adjacency
  assertion and RO's missing resolve witness. Six overlapping protected-loss
  flags occur in four cells, not six independent failures. Even forgiving the
  two H annotations leaves the frozen no-advancement decision unchanged.
- [x] Record resource tradeoffs: median latency **2.441 s NC / 10.323 s TH**;
  median paired latency **3.83×** and generated-token ratio **4.81×**. Total
  usage is **400,096 input / 59,336 generated tokens / 338.825 active seconds**.
  TH uses 18.852 active seconds and 3,566.1 generated tokens per usable report,
  versus NC's 14.980 seconds and 1,882.2 tokens. Reasoning/final token splits and
  prompt/load/generation timing splits remain unknown. Archived-rate estimate
  **$0.191232**, actual billed cost unknown; no automatic efficiency qualification.
- [x] Pass **67 post-run offline tests**, Ruff lint/format and strict mypy on four
  analysis scripts. Verify all 48 exact raw/wire replays, sealed source notes,
  budget/version accounting, recovery/loss screens, sensitivity and resource
  denominators. Real HTTP is blocked. Preserve the frozen 381-test preparation
  and verify all **3,678 historical source fingerprints**.
- [x] Seal the analysis, report, tracker and issue-index update. Preserve all
  fourteen issue bodies and posted GitHub links; no external issue is edited or
  closed. No production code or prompt changes occur.
- [x] Before another live proposal, add the new local capture regressions and
  audit uncertainty semantics, conditional-versus-observed claims and incomplete
  craft witnesses. A separately frozen follow-up may assess the remaining failure
  with unchanged high-thinking controls and fresh full scenes. No new budget,
  lower-thinking arm, writer test or production rollout is authorized here.

Private evidence: `data/diagnostics/reviewer-thinking-mode-v61-2026-10-26-live/`
and `data/diagnostics/reviewer-thinking-mode-v61-2026-10-26-analysis/`.
Production **prompt 61 / graph 9 / fulfillment policy 1**, human checkpoints and
nine prior human ties remain unchanged. Humans assess feel/emotion, flow, character
and story-breaking details with machine-prepared mechanics. Provider attribution
remains deferred. **Step 19 IN PROGRESS; Step 20 NOT STARTED; further inference
PAUSED; full workflow canary ON HOLD.**

### Local thinking-mode epistemic/scope audit 2026-10-26

**COMPLETE — local evidence preservation and contract audit; no live calls.**
See the [audit](../docs/handoffs/reviewer-epistemic-scope-audit-2026-10-26.md) and
[proposed 32-call follow-up](../docs/handoffs/reviewer-epistemic-clarity-proposal-2026-10-26.md).

- [x] Preserve byte-identical copies of all **48 raw NC/TH captures** and all
  **326 valid component assessments**, exact source bindings and sealed prior
  judgments. Retain the eight paired relation recoveries with real rule/intention
  controls, five endpoint label/reason disagreements, duplicate-ID delivery,
  conditional substitution, craft explanation defects and successful controls.
  Raw thinking is not semantic evidence; no historical output or score is repaired.
- [x] Audit the actual identical system definitions in all 48 requests. Legacy
  unsupported explicitly includes premises the sources **do not establish**;
  uncertain also covers inability to judge. Of sixteen uncertain-source targets,
  **fourteen** have grounded unestablished explanations labeled unsupported,
  **one** is correctly uncertain and **one** substitutes a conditional answer.
  Preserve primary scores while disclosing that fourteen outcomes fit a literal
  legacy definition and cannot isolate a reasoning failure.
- [x] Record prospective disjoint factual-label semantics without changing any
  prompt: refuted differs from unestablished, unknown remains unknown under
  negation, and defensible craft need not be uniquely compelled. Keep source
  uncertainty, incomplete citations and evidence-capacity abstention distinct.
- [x] Bind **eight source relation audits** to exact assertions, identity, timing
  and state witnesses; add **twelve authored logic contrasts**. A true conditional
  does not establish its antecedents. Disclose F3's possible conditional reading
  of “as descriptions … at the same instant” alongside its frozen observed-instance
  target. No internal model cause is inferred from that one capture.
- [x] Verify the diagnostic scope/status utility rejects changed bindings and
  missing premises but cannot establish semantic truth from hashes or enums.
  Preserve a negative test where a falsely supplied established-time premise
  causes a wrong projected result. No automatic label correction or writer action.
- [x] Correct the preceding report's citation arithmetic explicitly: M-TH-H-RO/C01
  has union **R014/R015**; adding R012 costs **one**, expanding two refs to three,
  not zero. R012 is in other claims. The omission still fits within the eight-ref
  limit; the missing-witness finding and all historical scores are unchanged.
- [x] Pass **177 offline tests**: 110 new audit checks plus all 67 preceding
  execution tests. Ruff lint/format and strict mypy pass on four scripts. Block
  real HTTP; verify **4,521 historical fingerprints**. Update tracker/index and
  seal local artifacts, preserving all fourteen issue bodies and posted links.
- [x] Propose **32 calls**: eight full-scene families, both orders, unchanged
  high-thinking TH versus disjoint factual-definition EC, sixteen calls per arm.
  Retain three exact known control families and propose five fresh families,
  including separate observed/conditional components shared by both arms.
  Distinguish label alignment from semantic recovery; no new budget is frozen.
- [x] Prepare and verify the TH/EC comparison locally on 2026-10-27, including
  exact requests, current metadata, source/citation feasibility, scoring, stops
  and the 32-call ceiling. See the frozen preparation below. Selective production
  thinking, lower-thinking efficiency and writer tests remain deferred.

Private bundle: `data/diagnostics/reviewer-epistemic-scope-audit-v61-2026-10-26/`.
**Zero inference and daemon calls.** Production **prompt 61 / graph 9 / fulfillment
policy 1**, human checkpoints and nine human ties remain unchanged. Humans assess
feel/emotion, flow, character and story-breaking details with machine-prepared
mechanics. No issue is closed or externally edited. **Step 19 IN PROGRESS;
Step 20 NOT STARTED; live calls PAUSED; full workflow canary ON HOLD.**

### Frozen TH/EC epistemic-clarity preparation 2026-10-27

**COMPLETE — local preparation only; 0/32 inference calls. Awaiting live approval.**
See the [frozen plan](../docs/handoffs/reviewer-epistemic-clarity-frozen-plan-2026-10-27.md).

- [x] Freeze **32 attempts / sixteen per arm / zero retries**: eight full-scene
  families, both source presentation orders, high-thinking TH control and EC
  factual-label-definition candidate. Preserve six historical H/F3/G5 TH wire
  payloads exactly; EC changes only the unsupported/uncertain definition span.
  Supported and defensible-craft standards, schema and production prompts stay intact.
- [x] Author five fresh full scenes (295–314 original words): pool appeal, bakery,
  quartet, community kitchen and puppet theatre. J1–J4 separate actual-instance
  and conditional components, with unresolved, absent, same and different timing.
  J5 preserves authorization-status versus real intention/obligation conflicts.
  Freeze **24 whole claims / 58 components**, sources, context, registries and
  withheld gold; both orders yield 48 whole claims / 116 components per arm.
- [x] Verify complete material witnesses fit the unchanged **eight-reference union
  / 2,000 reason-character** bounds; maximum complete union is seven. Include
  explicit assignment/rule/voice witnesses and preserve the R012 citation correction.
  No historical output, request or primary score is repaired.
- [x] Freeze separate contract-alignment and observed-scope conclusions. Require
  six alignment opportunities/recoveries across all four unknown families with
  both orders in two; scope replication requires two recovered families including
  one fresh and no converse scope error. Source-inspect explanations independently
  of labels. Require all sixteen EC deliveries, all sixteen EC targets, all eight
  conditional controls and no protected paired loss. Incomplete runs cannot advance.
- [x] Freeze paired balanced schedule, F3/G5 first-eight sentinels, reservations
  of **768,000 input / 512,000 generated tokens / 19,200 active seconds**, 24k/16k/600s
  per call, 40k requested context. Both arms require nonempty high-thinking output;
  missing splits remain unknown. Retain terminal raw evidence, no-retry stops and
  clean-boundary continuation only within the original unspent allocation.
- [x] Capture metadata only: **Ollama 0.40.11**, unchanged selected DeepSeek digest
  `e04da138d31e0c9468e982e1ae9503d06cb7e170caa16a90c17d931c4aa140f8`.
  Preserve the initial sandbox socket denial and successful three-response capture.
  No prose sent and no inference performed during preparation.
- [x] Pass **385 offline tests** (208 current, 110 scope regressions, 67 prior
  execution checks), Ruff lint/format and strict mypy on twelve scripts. Exercise
  all 32 gateway dispatches through mocks, exact-wire treatment isolation,
  cardinality/bindings, separate scoring, stops/restart, terminal export and approval.
  Verify **4,590 historical fingerprints**; seal local artifacts and update index.
  Preserve all fourteen issue bodies and posted links; no external issue changes.
- [x] Obtain separate plan-bound approval and complete the 32-call TH/EC run on
  2026-10-27: full unpublished prose/context plus claims/components to Ollama Cloud
  through the local daemon, both arms high thinking, zero retries. See execution
  below. No selective production-thinking rollout or canary authorization.

Private bundle: `data/diagnostics/reviewer-epistemic-clarity-v61-2026-10-27/`.
No new model evidence or story-quality conclusion. Human review remains overall
feel/emotion, flow, character and story-breaking details with machine-prepared
mechanical evidence. Production **prompt 61 / graph 9 / fulfillment policy 1**,
Blueprint approval and nine prior human ties remain unchanged. Provider attribution
and writer tests are deferred. **Step 19 IN PROGRESS; Step 20 NOT STARTED;
live inference PAUSED; full workflow canary ON HOLD.**

### Approved TH/EC epistemic-clarity execution 2026-10-27

**COMPLETE — 32/32 calls, sixteen per arm, zero retries.** See the
[results](../docs/benchmark_reports/reviewer-epistemic-clarity-v61-results-2026-10-27.md).
Frozen decision: **retain_limited_evidence_no_advancement**.

- [x] Execute the exact approved plan with both arms high thinking; EC changes only
  unsupported/uncertain factual definitions. Preserve all six historical TH wires.
  Reserve and dispatch exactly 32 calls; first-eight sentinels pass (TH 3/4, EC 4/4).
  No terminal stop, HTTP failure, length finish or retry. All 65 daemon observations
  match **0.40.11** and selected model metadata remains frozen.
- [x] Retain **15/16 valid reports per arm**. TH/F3/RO and EC/J3/RO each repeat
  `claim_id` in all three claim objects: six duplicate-key occurrences across two
  normal-stop responses. Reject both intact; no repaired parse or semantic credit.
- [x] Source-inspect **30 valid reports / 90 whole reasons / 219 component reasons**
  from a masked export; seal notes before key decoding. Exclude thinking, arm/order
  and resource observations, while disclosing partial masking. Preserve exact
  artifact/claim/component/registry bindings and separate primary labels from reasons.
- [x] Record TH **8/16 primary-correct / 6/16 usable targets / 34/48 usable whole
  claims / 4/16 usable complete reports**; EC **11/16 / 10/16 / 40/48 / 10/16**.
  Invalid attempts remain in all denominators. All valid assignment and qualified
  craft labels are supported as intended; explanation precision remains separate.
- [x] Count **seven alignment opportunities, three recoveries**: F3/OR and G5 in
  both orders. EC's four preserved uncertainty targets are usable, but all eight
  fresh J1/J2 targets across both arms remain unsupported. Their reasons recognize
  unknown timing; keep the frozen uncertain gold and disclose the possible
  underlying-event versus evidence-entailment reading of “actually establish.”
  The present design cannot isolate wording from scene family as the cause.
- [x] Record **zero observed-scope opportunities** and **not_reproduced**, not a
  demonstrated EC recovery. The exact historical TH/F3/RO failure cell is invalid
  and unavailable for semantic observation. All fifteen valid fresh conditional
  components pass; EC has 7/8 because J3/RO is invalid. H/J5 preserve the distinction
  between unauthorized status and early action, separate from real rules/intentions.
- [x] Retain six explanation concerns: three J4 source-attribution overstatements
  (“no claim” becomes explicit denial), EC/J2/RO's one-lamp/another slip, TH/J5/RO's
  empty-chair-to-absence inference, and an explicitly qualified TH/H/OR precision
  concern. The four overlapping protected loss flags span EC J2/RO and J3/RO.
  Relaxing all explanation concerns still cannot change the frozen decision.
- [x] Record **288,432 input / 86,777 generated tokens / 292.433 active seconds**.
  Median latency TH **8.269s**, EC **8.587s**; paired median ratios **1.076x latency
  / 0.979x generated tokens**. All 32 reasoning-token splits and actual billing
  remain unknown. Archived-rate estimate **$0.190662**, not a confirmed charge.
- [x] Pass **53 offline tests**, Ruff lint/format and strict mypy on four analysis
  scripts. Replay all 32 captures, sealed notes/results, duplicate-key rejection,
  budgets, source binding, masked coverage, protected losses and denominator logic.
  Verify all **81 frozen preparation artifacts / 4,590 historical fingerprints**;
  analysis makes zero additional model or daemon calls. Update tracker/index and
  seal execution/analysis evidence; preserve fourteen issue bodies and posted links.
- [x] Before another inference proposal, carry duplicate captures into local
  regressions; audit event truth versus source entailment and assertion of negation;
  add source-attribution, referent and unsupported-absence fixtures with positive
  craft/conditional controls. Set prospective semantics explicitly without repairing
  historical gold. Further inference, selective routing and writer work are deferred.

Private evidence: `data/diagnostics/reviewer-epistemic-clarity-v61-2026-10-27/`,
its `-live/` sibling and `-analysis/` sibling. Retain the narrow EC known-case
alignment and high-thinking relation distinctions as diagnostic evidence only.
No human story-preference or prose-quality conclusion; humans retain feel/emotion,
flow, character and story-breaking review with machine-prepared mechanics.
Production **prompt 61 / graph 9 / fulfillment policy 1**, Blueprint approval and
nine prior human ties remain unchanged. No issue is closed or externally edited.
**Step 19 IN PROGRESS; Step 20 NOT STARTED; further live calls PAUSED;
full workflow canary ON HOLD.**

### Local duplicate-ID, attribution and claim-object audit 2026-10-27

**COMPLETE — local regression preservation and semantic audit; no live calls.**
See the [audit](../docs/handoffs/reviewer-claim-object-audit-2026-10-27.md) and
[proposed 24-call ER/SE comparison](../docs/handoffs/reviewer-claim-object-proposal-2026-10-27.md).

- [x] Preserve all **32 exact raw captures / 219 valid component regressions**,
  exact source bindings and sealed judgments. Retain both duplicate-ID failures
  (TH/F3/RO and EC/J3/RO), six duplicate keys and six attribution/precision
  fixtures. Strict parsing remains unchanged; invalid output earns no semantic
  credit. Historical gold, scores and no-advancement decision stay unchanged.
- [x] Distinguish narrated event relation, bounded-source entailment and explicit
  source assertion, including inner/outer negation. Unknown events stay unknown;
  a fully reviewed source can fail to establish an event without establishing its
  negation. Negative source findings require complete, explicitly bounded review,
  not a general closed-world assumption about missing story facts.
- [x] Bind six full-packet source audits and one selected-span audit. J4's complete
  scene establishes different times independently of R013's "no claim that";
  the latter is not itself an explicit negative assertion. Preserve one-lamp/two-
  entries identity, empty-chair countermodels and the qualified adjacency concern.
  Maintain defensible craft and conditional-without-antecedent positive controls.
- [x] Audit all **fifteen valid unknown-source targets**: eleven unsupported and
  four uncertain, including eight fresh J1/J2 unsupported answers. Their "actually
  establish" claim form admits a source-entailment reading. Record that prospective
  distinction without inferring the model's internal interpretation or rescoring
  historical event-relation gold. Prior wording and family were not crossed.
- [x] Verify the local claim-object utility rejects changed identities, missing
  statuses, mismatched scopes and incomplete negative source audits. It consumes
  authored source judgments, cannot prove semantic truth and cannot route writers.
  Preserve a false-premise countertest alongside **48 authored claim/negation
  contrasts** and **twelve attribution controls**.
- [x] Pass **163 offline tests** (110 current plus all 53 preceding execution
  checks), Ruff lint/format and strict mypy on four scripts. Block real HTTP;
  verify **5,179 historical fingerprints**. Seal local artifacts and documentation;
  preserve all fourteen issue bodies and posted links. No external issue changes.
- [x] Propose **24 calls**: six full-scene families, both presentation orders,
  event-relation ER versus source-entailment SE, twelve per form. Keep EC system
  definitions and high thinking unchanged; preserve four exact historical J1/J2
  EC wire controls and add four fresh families. State the prospective SE gold
  explicitly; test claim-form discrimination, not retrospective recovery.
- [x] Prepare and verify this comparison locally on 2026-10-27: current metadata,
  full scenes/claims, prospective gold, exact requests, budget, stops, witness
  feasibility and mocked dispatches. See frozen preparation below; separate live
  approval remains pending.

Private bundle: `data/diagnostics/reviewer-claim-object-audit-v61-2026-10-27/`.
**Zero inference and daemon calls.** Production **prompt 61 / graph 9 / fulfillment
policy 1**, Blueprint approval and nine prior human ties remain unchanged. Humans
retain feel/emotion, flow, character and story-breaking review with machine-prepared
mechanics. Selective thinking, writer testing and provider attribution stay deferred.
**Step 19 IN PROGRESS; Step 20 NOT STARTED; live calls PAUSED;
full workflow canary ON HOLD.**

### Frozen ER/SE claim-form preparation 2026-10-27

**COMPLETE — local preparation only; 0/24 inference calls. Awaiting live approval.**
See the [frozen plan](../docs/handoffs/reviewer-claim-form-frozen-plan-2026-10-27.md).

- [x] Freeze **24 attempts / twelve per form / zero retries**: six full-scene
  families, both presentation orders, source-entailment SE control and event-relation
  ER contrast. Both use unchanged EC instructions, component schema and high
  thinking. Only C02.A01 and its corresponding whole-claim text differ; restored
  SE text reproduces each paired wire exactly. Preserve all four historical J1/J2
  EC wire requests under the matching baseline.
- [x] Author four new full scenes: ferry refund, theatre costume room, orchard
  water allocation and museum bell return, **308–329 original words** each. Freeze
  unresolved/absent/same/different observation timing, retained discovery/decision,
  endpoint changes, qualified craft and separate supported conditional controls.
  Twelve family/form records contain **36 whole claims / 84 components**; both
  orders give **36 whole claims / 84 components / 72 non-targets per arm**.
- [x] Make prospective gold explicit: unknown event ER is uncertain; complete
  bounded-source insufficiency makes the stronger SE claim unsupported. Preserved
  J1/J2 historical uncertain gold and scores remain untouched. Bind full-packet
  scope audits and complete witness sets; all 36 unions fit within eight references,
  maximum **six**, and reason examples fit 2,000 summed characters.
- [x] Freeze separate primary-label and exact-object explanation scoring. Require
  all 24 deliveries, all eight unknown matched pairs, all eight individual known-
  time targets, all 24 conditional components and no protected SE-to-ER loss.
  Judge whole aggregates against their own claim forms; different correct labels
  are not losses. Partial masking hides metadata, while claim form remains visible.
  Seal source notes before key decoding; thinking is never semantic evidence.
- [x] Freeze balanced adjacent pairs, J1/J2 first-eight sentinels, **576,000 input /
  384,000 combined generated tokens / 14,400 active seconds**, 24k/16k/600s per call,
  40k requested context. Retain reservation-before-dispatch, terminal evidence and
  unknown usage, zero retries/reallocation and clean-boundary continuation only.
- [x] Capture metadata only: **Ollama 0.40.11**, selected model digest unchanged
  (`e04da138d31e0c9468e982e1ae9503d06cb7e170caa16a90c17d931c4aa140f8`). Preserve the
  initial sandbox denial and successful three-response capture. No prose sent.
- [x] Pass **393 offline tests**: 230 current, 110 claim-object regressions and all
  53 prior execution checks. Ruff lint/format and strict mypy pass on twelve
  scripts. Real HTTP is blocked; mock all 24 gateway dispatches, exact requests,
  prospective scoring, delivery boundaries, budgets, drift, stops/restart,
  terminal export and approval enforcement. Verify **5,234 historical fingerprints**;
  seal preparation and update the issue index, preserving all fourteen issue
  bodies and posted links. No external issue changes or production edits.
- [x] Obtain separate plan-bound live approval and complete **24/24 calls** on
  2026-10-27: full unpublished prose/context and frozen claims/components to Ollama
  Cloud via the local daemon, both high thinking and zero retries. See execution
  below. Selective production thinking and writer work stay deferred.

Private bundle: `data/diagnostics/reviewer-claim-form-v61-2026-10-27/`, including
the frozen casebook and `plan.json` seal. This is prospective claim-form discrimination,
not retrospective recovery or story-quality qualification. Humans retain overall
feel/emotion, flow, character and story-breaking review with machine-prepared
mechanics. Production **prompt 61 / graph 9 / fulfillment policy 1**, Blueprint
approval and nine prior human ties remain unchanged. **Step 19 IN PROGRESS;
Step 20 NOT STARTED; inference PAUSED; full workflow canary ON HOLD.**

### Approved ER/SE claim-form execution 2026-10-27

**COMPLETE — 24/24 calls, twelve per form, zero retries.** See the
[results](../docs/benchmark_reports/reviewer-claim-form-v61-results-2026-10-27.md).
Frozen decision: **retain_limited_evidence_no_advancement**.

- [x] Execute the approved frozen schedule with unchanged EC instructions and high
  thinking. Preserve all four historical J1/J2 EC wire controls. Reserve/dispatch/
  complete exactly 24 calls; first-eight sentinels pass (SE 3/4, ER 4/4). No terminal
  stop, HTTP failure, truncation or retry; all **49 version observations** match
  **Ollama 0.40.11** and selected model metadata stays frozen.
- [x] Retain **SE 10/12 valid / ER 12/12 valid**. SE/J2/OR adds `claim_id_note` to
  all three claim objects; SE/K3/OR adds empty `components_note` fields to all three.
  Both are HTTP-200 normal-stop captures with six forbidden-field occurrences,
  no duplicate keys, no unknown refs and no cardinality/reason overflow. Neither
  field appears in any frozen wire. Reject intact; no repair or semantic credit.
- [x] Inspect **22 masked valid reports / 66 whole reasons / 154 component reasons**
  against complete sources, and seal notes before key decoding. Exclude thinking,
  arm/order/trial metadata and resources while disclosing visible claim form.
  Preserve exact artifact/claim/component/registry bindings and alternative
  complete witnesses without demanding an exact withheld reference list.
- [x] Record **SE 8/12 primary-correct / 7/12 usable targets / 27/36 usable whole
  claims / 67/84 usable components / 7/12 usable complete reports**; ER **12/12 /
  11/12 / 35/36 / 83/84 / 11/12**. Non-target usability is **60/72 versus 72/72**;
  all valid non-target components pass. These are different prospective claim
  objects, not a general model ranking or a retrospective score correction.
- [x] Retain **4/8 strict unknown-timing discriminating pairs**, J1/K1 in both
  orders. J2/RO also has correct differing primary labels but shared qualified
  "then" precision concerns; J2/OR SE is invalid. Both K2 SE targets remain
  uncertain despite accurate missing-time explanations; ER is correctly uncertain.
  All eight ER unknown targets and four ER known-time targets have correct labels.
- [x] Record **7/8 usable known-time controls / 22/24 usable conditionals**, with
  unavailable cells caused by invalid delivery, and all valid controls passing.
  No protected SE-to-ER paired loss or valid conditional substitution occurs.
  The delivery, unknown-pair and control-total screens still fail.
- [x] Keep the two J2/RO "then" concerns explicitly qualified: entry order versus
  observation chronology is ambiguous, while both explanations recognize unknown
  timing. Relaxing both raises unknown discriminating pairs to **5/8**, usable
  targets to **SE 8/12 / ER 12/12**, and leaves no advancement unchanged. No proven
  invented chronology or new story-quality failure is asserted.
- [x] Record **223,584 input / 72,116 generated tokens / 403.831 active seconds**.
  Median call latency is **13.302s SE / 17.256s ER**; median paired ER/SE ratios are
  **0.977x latency / 1.051x generated tokens**. All 24 reasoning/final token splits
  and actual billing remain unknown. Archived-rate estimate **$0.1536144**;
  both forms use high thinking, so no thinking-mode efficiency conclusion follows.
- [x] Pass **44 post-run offline tests**, Ruff lint/format and strict mypy on four
  scripts. Replay exact requests/captures, source notes, scoring, field rejection,
  version/budget accounting and precision sensitivity; real HTTP is blocked.
  Verify **74 preparation artifacts / 5,234 historical fingerprints**. Seal analysis
  and documentation; preserve all fourteen issue bodies and posted links.
- [x] Before another live proposal, preserve the new forbidden fields and qualified
  temporal wording as local regressions; audit K2 source-entailment wording and
  whole-claim composition against the successful forms. Require a materially
  isolated hypothesis with crossed forms/families before preparing more inference.
  No new requests, budget, prompt changes or writer experiments are authorized here.
  Completed in the local source-sufficiency audit below.

Private evidence: `data/diagnostics/reviewer-claim-form-v61-2026-10-27/` and its
`-live/` and `-analysis/` siblings. Retain claim-form sensitivity as limited
diagnostic evidence. Historical gold, production **prompt 61 / graph 9 / fulfillment
policy 1**, Blueprint approval and nine prior human ties remain unchanged. Humans
retain feel/emotion, flow, character and story-breaking review with machine-prepared
mechanics. No issue is closed or externally edited. **Step 19 IN PROGRESS;
Step 20 NOT STARTED; further live calls PAUSED; full workflow canary ON HOLD.**

### Local forbidden-field, temporal-wording and K2 audit 2026-10-27

**Status: COMPLETE — local regressions and source-sufficiency audit; no inference.**
See the [audit](../docs/handoffs/reviewer-source-sufficiency-audit-2026-10-27.md) and
[proposed 36-call SE/BS/ER comparison](../docs/handoffs/reviewer-source-sufficiency-proposal-2026-10-27.md).

- [x] Preserve all **24 raw ER/SE captures / 154 valid component regressions**,
  source bindings and sealed annotations. Reproduce historical SE **10/12 valid,
  8/12 primary-correct, 7/12 usable targets** and ER **12/12, 12/12, 11/12** with
  `retain_limited_evidence_no_advancement`; no historical rescoring.
- [x] Add intact forbidden-field fixtures for SE/J2/OR `claim_id_note` and
  SE/K3/OR empty `components_note`: **six occurrences across two normal-stop
  reports**, distinct from duplicate JSON keys. Preserve two earlier duplicate-ID
  comparators. Reject extra fields at root, claim and component levels, including
  empty/null/false values; no repaired delivery or semantic credit.
- [x] Retain both J2/RO “then” concerns as qualified, not proven chronology errors.
  Bind exact source quotes and the reports' timing qualifications. Add **twelve
  authored temporal contrasts** separating entry order, observation chronology,
  reversed timestamps, explicit simultaneity, absent/unresolved timing, unrelated
  events, conditionals and source insufficiency. Preserve the prior sensitivity.
- [x] Audit **twelve source-bound family/form records**. K2 has one hook and two
  literal opposite-state entries with no observation times in the complete packet.
  An unsupported source-sufficiency assertion does not refute the event relation.
  Keep incomplete source scope distinct from a completed insufficiency audit.
- [x] Replay all four K2 raw C02 judgments. A01 is uncertain and A02 supported;
  application conjunction correctly preserves uncertain. The SE mismatch precedes
  aggregation. Both SE reasons retain grounded `source_insufficient` annotations;
  no automatic label correction or claim about the internal interpretation.
- [x] Record an additional confound: J1/J2/K1 C03.A02 discusses timing, while K2
  discusses hook identity. Family, target phrasing and neighbor cues were not
  independently crossed. Their causal contributions remain unproved.
- [x] Pass **124 offline tests**: 80 current checks plus all 44 preceding execution
  checks, Ruff lint/format and strict mypy on four scripts. Correct initial local
  formatting/module-path findings; preserve both verification records. All
  **5,697 historical fingerprints** verify. Tests block real HTTP; **zero new
  inference or daemon calls**. Seal audit assets and documentation.
- [x] Propose **36 calls**, six families × three forms × both orders: unchanged SE,
  direct bounded-source BS, unchanged ER. Preserve K2/J2/K1 and add fresh absent,
  same-instant and different-time scenes. Hold neighboring claims fixed within
  families; separate new matched recoveries from non-reproduced failures.
- [x] If requested, prepare and freeze the SE/BS/ER cases, exact control/treatment
  requests, source adjudication, scoring, budget and stop rules; verify current
  metadata and mocked dispatch, then present the plan for separate live approval.
  The proposal does not prepare or authorize live requests or writer calls.
  Local preparation is completed below; inference still requires separate approval.

Private bundle: `data/diagnostics/reviewer-source-sufficiency-audit-v61-2026-10-27/`.
Production **prompt 61 / graph 9 / fulfillment policy 1**, Blueprint approval,
historical budgets and nine human ties are unchanged. Human review retains
feel/emotion, flow, character and story-breaking judgments with machine-prepared
mechanics. Selective production thinking, writer tests and provider attribution
remain deferred. All fourteen issue bodies and posted links remain intact; no
external issue is edited or closed. **Step 19 IN PROGRESS; Step 20 NOT STARTED;
live calls PAUSED; full workflow canary ON HOLD.**

### Frozen SE/BS/ER source-sufficiency preparation 2026-10-27

**Status: COMPLETE — locally frozen and verified; 0/36 inference calls used.**
See the [frozen plan](../docs/handoffs/reviewer-source-sufficiency-frozen-plan-2026-10-27.md).

- [x] Freeze **36 attempts**, twelve each SE/BS/ER, zero retries/replacements:
  preserved K2/J2/K1 plus three fresh full-scene families L1/L2/L3, both source
  presentation orders. Preserve all **twelve historical SE/ER wire controls**.
  Adjacent triples use each of the six form orders twice; first twelve K2/L1
  cells constitute the delivery sentinel within the same budget.
- [x] Freeze **18 family/form records, 54 whole claims and 126 components**, exact
  original/revision/context artifacts, source registries, claims, requests and
  prospective gold. Fresh originals have **327 / 337 / 341 words**. Change only
  the target source-sufficiency proposition and matching whole C02 text within
  sets; retain EC instructions, separate conditional, assignment/craft controls
  and neighboring qualifications. All forms use high thinking.
- [x] Audit complete source scope: no context-only observation time changes BS
  versus SE gold. Unknown ER relations stay uncertain while the corresponding
  finite-source sufficiency assertion is unsupported. Preserve explicit same-
  and different-time controls. Claims under assessment are not story evidence.
  All **54 witness unions fit within eight references; maximum six**.
- [x] Freeze scoring: 36 valid deliveries, twelve usable targets each BS/ER,
  twelve individual known-time control targets, 36 conditionals, no protected
  SE-to-BS/ER loss and a contemporary valid matched recovery in each of K2/L1.
  Invalid SE is not a recovery opportunity; correct controls that do not reproduce
  a failure cannot create recovery credit. Record label and source recoveries,
  alignment without reproduced recovery, limited evidence and incomplete outcomes
  separately. No production qualification, historical rescoring or writer dispatch.
- [x] Freeze per-call **24,000 input / 16,000 combined generated tokens / 600 active
  seconds**, context 40,000; total **864,000 / 576,000 / 21,600 seconds**. Archived
  reference reservation **$0.95040**, retained $1 planning allowance; current
  tariff/actual billing unknown, no enforced billed-dollar ceiling. Largest rough
  quarter-byte estimate **8,761 tokens**; actual counts remain unknown pre-inference.
- [x] Freeze twelve-call sentinel and global transport, version/model, usage,
  thinking-observation, truncation, timing, cancellation, tamper and ambiguous-
  dispatch stops. Preserve terminal error chains and unknown usage; no retry,
  budget reallocation or semantic early stop. Resume only at a clean completed
  boundary within unspent allocation.
- [x] Capture three successful metadata-only responses: **Ollama 0.40.11**,
  unchanged DeepSeek digest/capabilities. Retain the earlier sandbox socket denial.
  **Zero inference calls; no prose sent.** No live approval file or live ledger.
- [x] Pass **416 offline tests**: 292 current checks, all 80 preceding audit checks
  and all 44 prior execution checks. Ruff lint/format and strict mypy pass on
  thirteen scripts. Exercise all 36 mock dispatches, restart, stops, malformed
  output, sealed inspection, scoring and no-approval refusal. The initial sandbox
  attempt stalled before mock dispatch; the complete permitted offline rerun passes
  with real HTTP blocked. Verify **5,743 historical fingerprints** and seal the plan.
- [x] Obtain separate approval before sending the frozen full prose/context/claims
  payload to Ollama Cloud via the local daemon, within the 36-call ceiling. Do not
  start a writer test, production prompt rollout or the full workflow canary.
  Approved and executed with the authorized 0.40.12 amendment on 2026-10-28 below.

Private bundle: `data/diagnostics/reviewer-source-sufficiency-v61-2026-10-27/`,
including the complete casebook, exact wire requests and `plan.json` seal.
Production **prompt 61 / graph 9 / fulfillment policy 1**, Blueprint approval,
historical budgets and nine human ties remain unchanged. Humans retain feel/emotion,
flow, character and story-breaking judgments with machine-prepared mechanics.
All fourteen issue bodies and posted GitHub links remain intact; no external issue
is edited or closed. **Step 19 IN PROGRESS; Step 20 NOT STARTED;
inference PAUSED; full workflow canary ON HOLD.**

### SE/BS/ER source-sufficiency execution 2026-10-28

**Status: COMPLETE — 36/36 calls; limited evidence, no advancement.** See the
[results](../docs/benchmark_reports/reviewer-source-sufficiency-v61-results-2026-10-28.md)
and [approved version amendment](../docs/handoffs/reviewer-source-sufficiency-baseline-amendment-2026-10-28.md).

- [x] Capture current **Ollama 0.40.12** metadata and unchanged DeepSeek metadata.
  Preserve the original zero-call plan and seal. All **56 experimental input
  files / 36 prepared requests** remain byte-identical; twelve historical SE/ER
  wires remain exact. The new approval binds the original parent, amended plan
  and approved daemon version, retaining the combined **36-call** ceiling.
- [x] Pass **419 offline tests**, Ruff lint/format and strict mypy before inference.
  Correct stale version-test expectations caught by initial verification; rerun
  the whole suite successfully. Seal **84 artifacts / 5,833 historical fingerprints**.
- [x] Execute **36 reservations / 36 dispatches / 36 completed responses**, twelve
  per form, zero retries/replacements/probes/terminal stops. All **36 deliveries
  validate**; first-twelve sentinel is 4/4 per form. All **73 runtime version
  observations** match 0.40.12; selected model metadata remains frozen.
- [x] Inspect and seal **36 masked reports / 108 whole reasons / 252 component
  reasons** before trial-key decoding. Exclude thinking/resources from the review
  view; retain partial masking and assistant factual-audit limitations.
- [x] Record correct and usable targets **SE 8/12, BS 10/12, ER 12/12**. BS recovers
  both fresh **L1** SE label failures but neither known **K2** failure: **2/2 versus
  0/2** valid matched opportunities. Explanations already recognize missing timing;
  both recoveries are labels, not grounding repairs. K2 SE and BS raw component
  judgments remain uncertain before correct whole-claim aggregation.
- [x] Record **6/8 BS/ER unknown-timing pairs**, **12/12 known-time targets** and
  **36/36 conditionals** usable, with no protected SE-to-BS/ER paired-loss flags.
  All assignment/craft primary labels remain supported. Preserve two qualified
  SE craft-wording concerns: L2/RO before/until timing and L1/OR hand-guidance
  attribution. Relaxing both leaves target scores, recoveries and decision unchanged.
- [x] Retain **`retain_limited_evidence_no_advancement`**. Failed screens are
  `all_BS_targets` and `known_and_fresh_recoveries`. The L1 recovery is diagnostic
  evidence; BS is not qualified. A clean delivery batch does not establish a
  permanent fix or an Ollama-update effect. Historical gold/scores stay unchanged.
- [x] Record **337,268 input / 113,756 generated tokens / 502.942 active seconds**.
  Maximum call **9,681 / 5,336 / 24.144 seconds** stays within frozen ceilings.
  Archived-rate estimate **$0.2376876**; actual billing and reasoning/final-token
  splits remain unknown. All forms use high thinking; no production latency or
  thinking-on/off conclusion is drawn.
- [x] Pass **57 post-run offline tests**, Ruff lint/format and strict mypy on seven
  analysis scripts; replay exact captures, requests, seals, annotation bindings,
  aggregation, recoveries, denominators and sensitivity. Update the issue index;
  preserve fourteen issue bodies and user-posted links. No external issue edit.
- [x] Preserve K2 failures, L1 failures/recoveries and qualified craft wording as
  local regressions; audit K2/L1 predicate, timing and source-scope contrasts.
  Require a materially different, locally justified hypothesis before another
  live plan. Evaluate any typed claim/source-obligation projection only against
  validated premises and complete scope; no silent label correction or rollout.
  Completed in the local source-obligation audit below.

Private amendment/live/analysis roots begin
`data/diagnostics/reviewer-source-sufficiency-amendment-v61-2026-10-28`.
Production **prompt 61 / graph 9 / fulfillment policy 1**, Blueprint approval,
historical budgets and nine human ties remain unchanged. Human feel/emotion,
flow, character and story-breaking judgments remain separate from machine-prepared
mechanics. **Step 19 IN PROGRESS; Step 20 NOT STARTED; further inference PAUSED;
full workflow canary ON HOLD.**

### Local K2/L1 source-obligation audit 2026-10-28

**Status: COMPLETE — local regressions and audit; zero inference.** See the
[audit](../docs/handoffs/reviewer-source-obligations-audit-2026-10-28.md) and
[proposed BS/PO/ER comparison](../docs/handoffs/reviewer-source-obligations-proposal-2026-10-28.md).

- [x] Preserve **36 raw captures / 252 component regressions**, exact requests,
  source bindings and sealed historical annotations. Add four focused K2
  SE/BS × OR/RO fixtures: raw source labels uncertain, expected unsupported,
  supported conditional, correct uncertain whole-claim aggregation. No repair
  or rescoring; historical **SE 8/12, BS 10/12, ER 12/12** remains unchanged.
- [x] Audit twelve K2/L1 form/order records and six complete source/form records.
  Both have one referent, literal opposite states and absent observation timing;
  both have a neighboring referent qualification. BS recovers **L1 2/2**, **K2 0/2**
  valid opportunities. Family, predicate/negation wording and narrative were not
  independently crossed; no causal claim about negation, internal reasoning or
  the provider follows. Retain two qualified craft-wording fixtures separately.
- [x] Add **42 authored local contrasts** and six predicate-implication controls.
  Separate identity, literal opposition and same-instant evidence; bind a local
  typed projection to exact source, claim and observation pair. Distinguish a
  complete visible packet from an incomplete declared record, incomplete review,
  conflicting authority and figurative/compatible predicates. A deliberate false
  premise proves the algebra does not validate semantic truth or authorize edits.
- [x] Pass **164 offline tests**: 107 current checks plus all 57 preceding execution
  checks, Ruff lint/format and strict mypy on four scripts. Preserve the initial
  passing run and a scope-check lint finding, corrected before final verification.
  Verify **6,488 historical fingerprints**; real HTTP blocked, **zero daemon and
  inference calls**. Record audit/documentation seals. All fourteen issue bodies
  and user-posted GitHub links remain intact; no external issue edited or closed.
- [x] Propose a materially different **48-call BS/PO/ER** diagnostic: eight cases,
  three arms, both orders; unchanged BS/ER controls and a primitive-obligation
  ledger with application-derived source/event labels. Retain K2/L1 and add six
  fresh families, including context-only timing, incomplete declared scope and
  different referents. Require accurate premises and actual known/fresh matched
  recoveries; wrong premises cannot earn credit through a correct aggregate.
  This is a proposal only, not a frozen budget, prepared request or live approval.
- [x] If requested, prepare/freeze the proposed cases, obligations, exact controls
  and PO requests, source gold, scoring, 48-call budget and stops. Capture current
  metadata, verify mocked execution and scope/citation feasibility, then present
  the frozen plan before separate live approval. Do not launch automatically.
  Completed in the local BS/PO/ER preparation below; live execution is not approved.

Private bundle: `data/diagnostics/reviewer-source-obligations-audit-v61-2026-10-28/`.
Production **prompt 61 / graph 9 / fulfillment policy 1**, Blueprint approval,
historical budgets and nine human ties remain unchanged. Human feel/emotion, flow,
character and story-breaking review stays separate from machine-prepared mechanics.
No production qualification, writer dispatch or story-quality improvement is
claimed. **Step 19 IN PROGRESS; Step 20 NOT STARTED; live calls PAUSED;
full workflow canary ON HOLD.**

### Frozen BS/PO/ER source-obligation preparation 2026-10-28

**Status: COMPLETE — locally frozen and verified; 0/48 inference calls used.** See
the [frozen plan](../docs/handoffs/reviewer-source-obligations-frozen-plan-2026-10-28.md).

- [x] Freeze **48 attempts**, sixteen per arm, eight cases × BS/PO/ER × both source
  orders, zero retries/replacements. Preserve **eight historical K2/L1 BS/ER wire
  requests** exactly. Keep three-arm sets adjacent with balanced arm orders;
  first twelve K2/L1 cells are the included delivery sentinel, four per arm.
- [x] Author six fresh full-scene families M1–M6 (**329 / 320 / 324 / 327 / 325 /
  332 original words**): occupancy/negation and antonym missing-time transfer,
  context-only clock key, explicit different times, unavailable declared-source
  appendix and different objects at a shared instant. Freeze **24 case/form
  records, 72 whole claims, 168 component specifications**, scope audits, registries
  and exact requests. Gold remains outside the requests; no literary winner given.
- [x] Freeze PO's target-only protocol: independently return same-entity,
  literal-opposition and same-instant statuses/reasons/references. Bind and derive
  source/event labels separately; keep projections provisional until semantic
  inspection. The full visible-source review, every primitive status, explanation
  and citation must be inspected. Wrong premises cannot earn recovery through a
  correct derived label. Preserve other components and the independent conditional.
- [x] Audit M3's context key as prose-linked observation provenance rather than an
  assignment proving an action. For M5, explicitly judge declared S including its
  unavailable appendix, without substituting visible V or inventing hidden facts.
  All **72 authored witness unions** fit within eight refs; maximum **six**. The
  largest authored reason total is **495 characters** within the unchanged 2,000
  per-claim limit, including all PO primitives and the conditional.
- [x] Freeze screens: **48 valid deliveries, 16 usable PO targets / 48 correct and
  grounded primitives, 16 usable ER targets, 24 M3–M6 control targets, 48 usable
  conditionals**, both retained L1 BS targets and no protected BS-to-PO loss.
  Require a contemporary valid matched recovery in K2 and at least one of M1/M2;
  distinguish alignment, limited evidence and incomplete outcomes. No promotion.
- [x] Freeze per-call **24,000 input / 16,000 combined generated tokens / 600 active
  seconds**, context 40,000; total **1,152,000 / 768,000 / 28,800 seconds**. Largest
  rough input estimate **10,075 tokens**. Archived-rate reservation **$1.26720**,
  $1.50 planning allowance; actual tariff/billing and unreported token splits remain
  unknown. No enforced billed-dollar ceiling or separate thinking allowance.
- [x] Capture three metadata-only responses: **Ollama 0.40.12**, unchanged DeepSeek
  digest/capabilities. Preserve the initial sandbox socket denial. No prose sent,
  no inference performed. Retain twelve-call delivery and global transport,
  version/model, usage, timing, truncation, thinking, tamper, cancellation and
  ambiguous-dispatch stops; terminal evidence and unknown usage stay observable.
- [x] Pass **450 offline tests**: 286 current preparation checks, all 107 preceding
  audit checks and all 57 preceding execution checks. Ruff lint/format and strict
  mypy pass on fifteen scripts. Preserve the initial sandbox stall/type findings
  and the 449-pass run that caught a stale SE resource-ratio selector; correct to
  BS and pass the full rerun. Real HTTP blocked throughout all tests. Verify
  **6,548 historical fingerprints** and seal **106 preparation artifacts** plus
  this public plan; no live approval file or live ledger exists.
- [x] Obtain separate approval before sending the frozen full prose/context/claims
  and PO obligation map to Ollama Cloud through the local daemon, within **48
  attempts / 16 per arm**. Execute only the approved sealed plan and inspect all
  results before another proposal. Do not start a writer test or the canary.

Private bundle: `data/diagnostics/reviewer-source-obligations-v61-2026-10-28/`.
Plan SHA-256: `c4bb1cb9824ae410db133f89b924bba864f3b9ec7ecb13bc53046a4aae7a1bd5`.
Production **prompt 61 / graph 9 / fulfillment policy 1**, Blueprint approval,
historical budgets/scores and nine human ties remain unchanged. Humans retain
feel/emotion, flow, character and story-breaking judgments with machine-prepared
mechanics. All fourteen issue bodies and user-posted links remain intact; no
external issue is edited or closed. **Step 19 IN PROGRESS; Step 20 NOT STARTED;
live calls PAUSED; full workflow canary ON HOLD.**

### Executed BS/PO/ER source-obligation comparison 2026-10-28

**Status: COMPLETE — 48/48 calls, sixteen per arm; retain a bounded source-obligation
recovery signal only.** See the
[results](../docs/benchmark_reports/reviewer-source-obligations-v61-results-2026-10-28.md).
This execution supersedes the preparation's zero-call/no-approval state above.

- [x] Record approval of the exact frozen payload/destination/plan. Complete
  **48 reservations / 48 dispatches / 48 responses**, all valid, with no probe,
  retry, replacement, truncation or terminal stop. The first-twelve delivery
  sentinel passes **4/4 per arm**. Keep all requests/settings/scoring/stops fixed.
- [x] Preserve **eight exact historical K2/L1 BS/ER wire controls**, the 106 sealed
  preparation artifacts and **6,548 historical fingerprints**. All **97 runtime
  version observations** match **Ollama 0.40.12** and the model metadata stays
  unchanged. All responses contain high-thinking output, excluded from grading.
- [x] Inspect **48 masked reports / 144 whole reasons / 336 component reasons /
  48 additional PO primitive judgments** against full original/revision/context.
  Seal source-bound notes before decoding identities; disclose partial masking.
  Every PO primitive is correct, grounded and complete; both projections pass
  in all sixteen PO reports. Preserve raw outputs without repair or relabelling.
- [x] Record correct/usable targets **BS 11/16, PO 16/16, ER 16/16**. PO recovers
  all **five** contemporary BS failures: **K2 OR/RO, M1 OR/RO, M2 OR**. These are
  label recoveries; BS already notices missing timing. Known/fresh usable targets
  are BS **2/4 + 9/12**, PO and ER each **4/4 + 12/12**.
- [x] Preserve **48/48 PO primitives, 24/24 M3–M6 control targets, 48/48 conditionals,
  both L1 BS targets and 10/10 unknown-time PO/ER pairs**, with **zero protected
  BS-to-PO or BS-to-ER losses**. In M5 both source and event remain uncertain
  because declared S includes the unavailable appendix. All frozen screens pass:
  **`retain_source_obligation_recovery_signal_only`**. No production qualification.
- [x] Retain one qualified BS/L1/OR craft-wording concern about “seating Tavi.”
  Strict BS usable whole claims/components/non-targets/complete reports are
  **42/48, 106/112, 95/96, 10/16**; accepting that wording gives **43/48, 107/112,
  96/96, 11/16**. Targets, five recoveries and the frozen decision are unchanged.
  PO/ER each have **48/48, 112/112, 96/96, 16/16**. No human preference measured.
- [x] Record **476,614 input / 191,195 combined generated tokens / 738.21 active
  request seconds**. All caps hold. PO uses **11.3% more generated tokens / 10.1%
  more active time than BS in aggregate**, but less per usable report. Active
  time excludes local verification overhead. Archived-rate estimate **$0.3724182**;
  actual billing and all reasoning/final token splits remain unknown.
- [x] Pass **84 post-run offline tests**, Ruff lint/format and strict mypy on seven
  scripts; preserve the first 83-test passing attempt with one lint finding.
  Replay all captures, check version/request/inspection bindings, wrong-premise
  rejection and precision sensitivity. The preparation's sealed **450-test**
  verification remains intact. No real HTTP during post-run tests or analysis.
- [ ] Before another live proposal, preserve failed-BS/successful-PO pairs and
  scope/time/identity controls as local regressions; audit how production would
  obtain obligations and complete source scope without assuming hidden evidence,
  confusing assignments with performed facts, or permitting stale/false premises.
  Only locally justified generalization work should lead to a separately frozen
  comparison. Do not authorize writer edits or the full workflow canary.

Private evidence: `data/diagnostics/reviewer-source-obligations-v61-2026-10-28/`
and sibling `-live/`, `-analysis/` bundles. The successful treatment combines
model premise assessment with application-owned projection; it does not show that
direct BS verdicts are repaired or that arbitrary literary claims fit this algebra.
Production **prompt 61 / graph 9 / fulfillment policy 1**, Blueprint approval,
historical scores/budgets and nine human ties remain unchanged. Humans retain
feel, flow, character and story-breaking judgments with machine-prepared mechanics.
All fourteen issue bodies and posted links are preserved; no external issue is
edited or closed. **Step 19 IN PROGRESS; Step 20 NOT STARTED; further live calls
PAUSED; full workflow canary ON HOLD.**

20. [ ] **Tune prompts and graph routing** based on blind human preference—not isolated attractive examples.

21. [ ] **Package the stable system with Tauri** and test crash/restart, offline, missing-model, invalid-key, provider-timeout, and low-disk-space behavior.

22. [ ] **Consider broader formats and hosted features only after the core is proven:** songs, poems, video scripts, collaboration, or hosted accounts.
