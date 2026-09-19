# Open Hollywood benchmarks

Benchmark inputs are product artifacts, not ad-hoc development prompts.

`v0.1/corpus.json` contains the accepted 12 short-prose prompts with immutable
IDs and versions, target length, required elements, forbidden shortcuts, likely
failure modes, stressed rubric dimensions, research policy, and stable seeds.

Validate it and print its canonical digest:

```powershell
uv run --extra api python scripts/evaluation_harness.py validate-corpus
```

## Campaign scope

For the current Cloud-first qualification phase, configure the complete Cloud
preset in the local database, then create a new campaign plan:

```powershell
uv run --extra api python scripts/evaluation_harness.py plan `
  --scope cloud-first `
  --database data/open_hollywood.db `
  --output data/evaluations/campaign-plan.json
```

The scope fixes the required matrix for all 12 frozen prompts:

| Scope | Required presets | Cases | Blind pairs when all cases succeed |
| --- | --- | ---: | ---: |
| `cloud-first` | Cloud | 24: 12 baseline + 12 Cloud | 12 Cloud/baseline |
| `all-profiles` (CLI default) | Local, Cloud, Hybrid | 48: 12 per target | 60 across the existing five comparison types |

Pass `--scope all-profiles`, or omit `--scope`, to retain the full matrix.
Cloud-first does not require Local or Hybrid to be configured. The direct baseline
uses the frozen Cloud scene-writer selection. Plans pin provider/model identities,
exact secret-free profile configurations, corpus hash, workflow versions and seeds.
New schema-2 plans also pin their explicit scope and require one complete,
consistent matrix across the corpus. Use a new campaign ID and output location for
a different model or scope. Existing files are protected unless `--overwrite` is
explicit; do not overwrite historical evidence.

Schema-1 plans remain readable with unchanged canonical hashes and historical
completion requirements. In particular, the old 48-case v29/v33 canary plans cannot
be relabeled or sealed as complete Cloud-first campaigns from their Cloud results.
A new scoped plan starts a new campaign. See
[ADR 0016](../docs/adr/0016-scoped-benchmark-campaigns.md).

Provider and model choices are independent of scope. The current executable CLI
uses Ollama transports, including Ollama Cloud; provider-neutral plan support
does not supply native OpenAI or Gemini adapters. Keep later model comparisons
in separate campaigns with their exact identities and settings frozen.

The commands below use one campaign plan/report pair throughout. Use your chosen
isolated campaign database and output directory consistently. Planning is offline;
`run-baseline`, `prepare-agentic` and `run-agentic` invoke the configured models.

## Execution and review

Run or resume the 12 direct single-model baseline cases:

```powershell
uv run --extra api python scripts/evaluation_harness.py run-baseline `
  --database data/open_hollywood.db `
  --plan data/evaluations/campaign-plan.json `
  --report data/evaluations/campaign-report.json
```

This command uses the local Ollama service endpoint. A model identifier ending
in `cloud` can still consume Ollama Cloud capacity through that service. The
report is replaced atomically after every newly executed case and again at
clean completion. Existing successful report results and succeeded SQLite
workflow lineage are reused; pass `--retry-failed` only when failed cases
should be attempted again.

The baseline runtime persists each frozen prompt input, bounded model
invocation, and complete story version in SQLite. It assigns only syntactic
hard gates automatically. Gates requiring literary judgment remain `null`
until a blind reviewer submits the canonical rubric.

Run or resume agentic Blueprint preparation. Preparation, Blueprint review and
approval, and production default to the agentic targets in the plan: Cloud only
for `cloud-first`, all three profiles for `all-profiles`. An explicit `--target`
excluded from the plan is rejected. Existing `run-agentic --batch-size 4
--batch-number 1` selection still supports three Cloud batches in one campaign;
use the same report for all batches and the baseline.

Preparation stops at the mandatory human checkpoint and never approves a
Blueprint on the operator's behalf:

```powershell
uv run --extra api python scripts/evaluation_harness.py prepare-agentic `
  --database data/open_hollywood.db `
  --plan data/evaluations/campaign-plan.json
```

Once every selected case has either failed terminally or reached that checkpoint,
create a deterministic review packet, readable Markdown dossier, and reviewer
CSV. This step is offline and makes no model calls:

```powershell
uv run --extra api python scripts/evaluation_harness.py package-blueprint-review `
  --database data/open_hollywood.db `
  --plan data/evaluations/campaign-plan.json `
  --reviewer-id primary-reviewer `
  --packet-output data/evaluations/blueprint-review-packet.json `
  --guide-output data/evaluations/blueprint-review-guide.md `
  --form-output data/evaluations/blueprint-review.csv
```

Review every Blueprint in the Markdown dossier. Enter `yes` in `approved` only
after approving the exact Blueprint version shown; notes are optional. Do not
edit the prefilled lineage fields. The approval command rejects incomplete
coverage, changed lineage, a foreign campaign, or a Blueprint whose immutable
version or digest no longer matches the packet. It is also offline:

```powershell
uv run --extra api python scripts/evaluation_harness.py approve-blueprints `
  --database data/open_hollywood.db `
  --plan data/evaluations/campaign-plan.json `
  --packet data/evaluations/blueprint-review-packet.json `
  --review-form data/evaluations/blueprint-review.csv
```

Each applied approval writes a durable human event containing the reviewer ID,
review-packet digest, and exact Blueprint version/digest before resolving the
existing LangGraph interrupt. Replaying the same completed form is idempotent.
After all approvals are applied, run or resume autonomous production:

```powershell
uv run --extra api python scripts/evaluation_harness.py run-agentic `
  --database data/open_hollywood.db `
  --plan data/evaluations/campaign-plan.json `
  --report data/evaluations/campaign-report.json
```

Create a private blinding key, then build separate public and private review
artifacts:

```powershell
uv run --extra api python scripts/evaluation_harness.py create-review-key `
  --output data/evaluations/private-review.key

uv run --extra api python scripts/evaluation_harness.py package-review `
  --plan data/evaluations/campaign-plan.json `
  --report data/evaluations/campaign-report.json `
  --blinding-key data/evaluations/private-review.key `
  --public-output data/evaluations/review-packet.json `
  --answer-key-output data/evaluations/private-answer-key.json
```

Aggregate technical evidence without human reviews:

```powershell
uv run --extra api python scripts/evaluation_harness.py summarize `
  --plan data/evaluations/campaign-plan.json `
  --report data/evaluations/campaign-report.json `
  --output data/evaluations/summary.json
```

Supplying `--reviews` also requires the separate `--answer-key`. Review files
use the strict `HumanReviewBundle` contract, including campaign identity and
unique reviewer/comparison pairs.

Cloud-first summaries contain only baseline and Cloud metrics. Missing or failed
Cloud cases remain in the 12-case completion denominator; excluded Local/Hybrid
targets are neither failures nor passes. Blind packets contain only comparisons
whose two stories completed, so retain unpaired failures in the technical report.

Create the reviewer form and guide, then import it only after actual human review:

```powershell
uv run --extra api python scripts/evaluation_harness.py create-review-form `
  --public-bundle data/evaluations/review-packet.json `
  --reviewer-id primary-reviewer `
  --output data/evaluations/review.csv `
  --guide-output data/evaluations/review-guide.md

uv run --extra api python scripts/evaluation_harness.py import-reviews `
  --public-bundle data/evaluations/review-packet.json `
  --input data/evaluations/review.csv `
  --output data/evaluations/reviews.json
```

Recompute the summary with those reviews, then seal and verify the evidence:

```powershell
uv run --extra api python scripts/evaluation_harness.py summarize `
  --plan data/evaluations/campaign-plan.json `
  --report data/evaluations/campaign-report.json `
  --reviews data/evaluations/reviews.json `
  --answer-key data/evaluations/private-answer-key.json `
  --output data/evaluations/summary.json `
  --overwrite

uv run --extra api python scripts/evaluation_harness.py seal-evidence `
  --plan data/evaluations/campaign-plan.json `
  --report data/evaluations/campaign-report.json `
  --public-bundle data/evaluations/review-packet.json `
  --answer-key data/evaluations/private-answer-key.json `
  --reviews data/evaluations/reviews.json `
  --summary data/evaluations/summary.json `
  --output data/evaluations/evidence.zip

uv run --extra api python scripts/evaluation_harness.py verify-evidence `
  --archive data/evaluations/evidence.zip
```

Sealing a scoped campaign requires exactly one terminal result per planned case,
all eligible successful comparison pairs, exact generated story content, complete
human-review coverage and a matching recomputed summary. A terminal failure can
be included in a complete evidence archive; sealing establishes evidence integrity,
not that the campaign met the acceptance criteria. Partial batches cannot be sealed
as a completed campaign. A sealed archive can retain unknown cost acceptance;
sealing does not resolve missing billing evidence or establish live repeatability.

The private blinding key, generated answer key and sealed archive must not be
distributed with the public A/B review packet. The archive contains private
provenance. None of these files may contain API keys.

## Cost evidence and acceptance

Before running the updated application or database-backed harness, apply migration
0008 through the usual `uv run alembic upgrade head` command against the intended
active database. The migration adds `cost_basis` and leaves historical amounts
unchanged. Existing invocations receive `unknown`; no past zero or positive amount
is promoted to verified billing evidence. Preserve historical campaign databases.

New responses and invocations distinguish three cost bases:

| Basis | Meaning | Eligible dollar amount |
| --- | --- | --- |
| `provider_reported` | The adapter explicitly records a provider-reported charge | Nonnegative amount, including an explicit zero |
| `local_inference` | Inference executed locally, with zero provider charge | Zero; excludes electricity, hardware and other operating costs |
| `unknown` | No supported dollar-cost evidence, including interrupted calls | `null` in the portable cost-evidence record |

The existing numeric `estimated_cost_usd` field remains for compatibility and
runtime accounting. It is not the source of truth for current acceptance. Each
new benchmark output carries one cost-evidence record for every invocation ID.
Agentic totals cover both Blueprint and production calls, including recovered
failures. Baselines also retain failed attempts on the path to a successful story.
If any invocation is unknown, the complete story cost is unknown.

Summary schema 2 exposes `known_cost_cases` and `unknown_cost_cases` per target.
Unknown coverage includes missing cases, failed cases without a complete story,
and successful stories whose invocation costs are incomplete. A target median is
available only with complete cost coverage. The Cloud/Hybrid budget criterion is:

- `true`: every planned applicable case has complete cost evidence and the median
  is within the configured acceptance budget.
- `false`: coverage is complete and the median exceeds that budget.
- `null`: evidence is insufficient. This is not a zero cost, a pass or a failure.

The baseline has its own cost coverage and median. Its costs do not enter the
agentic Cloud/Hybrid acceptance criterion. The acceptance budget still defaults
to `$2.00`; `--normal-cloud-run-budget-usd` must match between summary and sealing.
Runtime call/production ceilings, token budgets, retries and model routing are
unchanged. Unknown provider costs cannot substantiate an enforced dollar-spend
ceiling even though the existing runtime checks continue to operate.

The current Ollama Cloud adapter reports token usage but no dollar charge, so
current Cloud cost acceptance remains `null`. Subscription capacity, unused quota,
a zero placeholder or a configured ceiling cannot establish a per-story price.
This implementation does not invent token rates, allocate subscription fees or
add pricing/billing integrations. A future pricing estimate would need its own
explicit, reproducible provenance.

Current `summarize` commands apply these rules even to historical reports and
plans. Save a new summary separately when inspecting old evidence. Original
reports, summaries and archives should remain unchanged. New `seal-evidence`
requires summary schema 2; regenerate an old summary before creating a new seal.
Existing schema-1 archives still verify byte for byte under their historical
policy. `verify-evidence` identifies `legacy_numeric_costs` versus
`explicit_cost_evidence`; historical archive integrity is not current cost
qualification. See [ADR 0017](../docs/adr/0017-evidence-based-cost-acceptance.md).

## Cross-version production canaries

v23 and v25 are the reference runs until a stronger matched canary replaces them.
`v0.1/canary-baselines.json` pins their exact report bytes. Preserve the original
directories, databases, reports, approvals, and logs; never retag or resume an
old graph checkpoint under a new production graph version.

After a separately authorized clean canary has finished, compare it offline:

```powershell
uv run --extra api python scripts/canary_review.py compare `
  --candidate data/benchmarks/v0.1/v26-canary-YYYY-MM-DD
```

The command reads SQLite in read-only mode and prints JSON. It rejects changed
baseline report hashes, mismatched corpus/profile/seed/case snapshots, changed
non-production workflow versions, different attempted case sets, mismatched
database lineage, multiple production runs per selected case, and changed
approved Blueprints. It reports raw and eligible completion denominators,
retained/new/lost successes, accepted/planned scenes, all production attempts
(including recovered failures), tokens, provider latency, and diagnostic layers.
Only the exact inherited Local OH-V01-006 missing-beats error can be excluded.
The comparison does not infer quality, and cannot prove models or host hardware
remained identical beyond the recorded snapshots. Record environmental changes
separately. Older traces without failure layers are explicitly unknown.

For cross-version human quality, use the existing private-key creation command
above and keep it outside the public directory. Then package a matched pair:

```powershell
uv run --extra api python scripts/canary_review.py package-review `
  --left data/benchmarks/v0.1/v25-canary-2026-09-07 `
  --right data/benchmarks/v0.1/v26-canary-YYYY-MM-DD `
  --blinding-key data/evaluations/private-review.key `
  --public-directory data/evaluations/v25-v26-public `
  --private-key-output data/evaluations/v25-v26-private-answer-key.json `
  --reviewer-id primary-reviewer
```

This creates a provenance-free A/B JSON packet, rubric guide, and blank CSV form.
The separate private answer key identifies each candidate's run, case, report,
and exact content. Existing outputs and source-canary directories are protected
against overwrite. Repeat for v23; compare only cases completed in both versions,
and keep every unpaired failure in the technical report. Do not distribute
answer keys or source reports to reviewers. Do not manufacture completed forms.

After actual reviewers score every dimension and hard gate, summarize their forms:

```powershell
uv run --extra api python scripts/canary_review.py summarize-reviews `
  --public-bundle data/evaluations/v25-v26-public/public-bundle.json `
  --answer-key data/evaluations/v25-v26-private-answer-key.json `
  --reviews data/evaluations/v25-v26-public/review.csv
```

Blank cells, foreign packets, duplicate reviewer/comparison pairs, and mismatched
content bindings are rejected. The summary separates weighted scores, hard-gate
failures, preferences/ties, and pending comparison coverage. Multiple reviewers
are supported; their rows are equally weighted, so balance reviewer coverage.
These are canary-quality summaries, not completion of the formal Step 19 campaign.

### Repeatability protocol

1. Predeclare the usual six Local / four Cloud case IDs, approved Blueprint seed,
   frozen corpus/profile/seed, graph/prompt versions, budget, and host/model
   configuration. Use a new named output directory and clean approved-seed copy
   for each repeat. Verify no production invocations/artifacts leaked into it.
   Keep the mandatory prior human approvals intact; new Blueprints need new
   approval. Never copy completed production checkpoints as a fresh experiment.
2. Obtain authorization for the live runs and their aggregate cost. Run at least
   three independent fresh repeats before claiming repeatability. Fixed seeds
   do not guarantee identical provider output. Do not use cached successes or
   retry-only reports as independent repeats. Record environmental interruptions
   separately, retaining them in the raw accounting.
3. Compare each repeat against both pinned baselines. To beat their observed
   completion count requires at least seven of nine runnable completions, while
   also reporting any lost previous success, per-profile results, scene progress,
   validation failure/recovery rates, tokens, and cost. Do not promote a baseline
   merely because one aggregate count increased while important cases regressed.
4. Blind-review matched completed stories for voice, originality, character,
   pacing, coherence, continuity, and the full canonical rubric/hard gates.
   Require no material quality or safety-gate regression and report all partial
   review coverage. A three-run sample is still small; report individual outcomes
   and uncertainty rather than claiming statistical proof.

The v26 implementation adds this tooling and protocol only. It does not launch
live canaries, create human scores, or mark Step 19 complete.

### Isolated saved-input probes before another canary

Graph v7 / prompt v27 repairs are tested against the eight predeclared selections
in `v0.1/production-probes-v27.json`: five Local first critics, Cloud 002's first
critic, and the v25 Local 002/003 late Bible failures. Source artifacts are read
from SQLite with read-only access and checked against their exact content hashes.
Requests use the current production contract, original model, seed, artifact
versions, and per-call budgets. They are diagnostic re-evaluations, not clean
canaries, new v25 runs, human scores, or canonical story updates.

Inspect one selection without any model call or filesystem write:

```powershell
uv run --extra api python -m scripts.production_probe inspect `
  --database data/benchmarks/v0.1/v26-canary-2026-09-08/campaign.db `
  --invocation-id b3f1fb35-9c93-4df2-ad11-d9bf8d637125
```

After explicit authorization, run that one Local specialist probe:

```powershell
uv run --extra api python -m scripts.production_probe run `
  --database data/benchmarks/v0.1/v26-canary-2026-09-08/campaign.db `
  --invocation-id b3f1fb35-9c93-4df2-ad11-d9bf8d637125 `
  --output-directory data/diagnostics/v27-probes/local-002-critic
```

Use each registry entry's `source` and `invocation_id` for the other selections.
Cloud additionally requires `--allow-cloud` and uses the existing signed-in local
Ollama Cloud route, not a new credential or provider. Each probe allows at most
two sequential calls with 900-second timeouts. The manifest states its maximum
token/cost envelope. Eight probes therefore allow at most 16 calls; inspect
their budgets before authorizing the batch.

The output directory must be new and outside source/protected canary directories.
Requests are recorded before calling the model; completed attempts include
provider usage, response hash/length, bounded diagnostics, and validated output.
Raw failed response bodies are not stored. Interrupted output directories are
preserved and cannot be silently reused. Bible probes additionally apply the real
reducer in memory, preserving resolved-thread history. No writer, production graph,
campaign report, checkpoint, or original database is modified.

Inspect the actual reviewer judgments, not just `validated`: allowed interiority
must not become a hard POV blocker, genuine unauthorized viewpoint changes must
still be caught, and historical Bible resolutions must remain unchanged. Passing
these isolated checks only authorizes consideration of a separately approved full
canary; it does not establish production completion or literary quality.

### Targeted viewpoint follow-up (prompt v28 / graph v7)

The completed v27 isolated suite validated all eight responses on their first
attempt, but Local 005 missed its intended other-character-private-state control.
The full canary was held. See
`docs/benchmark_reports/step-19-v27-isolated-probes-2026-09-08.md` and ADR 0009.

`v0.1/production-probes-v28.json` predeclares three follow-up Local critic probes
using the unchanged historical invocations for Local 002, 003, and 005. They are
**prepared, not run**. Use the existing `production_probe inspect` command to
verify inputs without model calls; after separate authorization, use `run` with
each entry's source/invocation and a new diagnostic output directory. Do not reuse
the completed v27 directory or alter the old registry or report.

Expected viewpoint outcomes are separate from response validation:

- Local 002: no hard blocker for the assigned character's first-person interiority.
- Local 003: no hard blocker for the assigned investigator's deductions.
- Local 005: a blocking finding for Cora's unauthorized private state, supported
  by exact current-draft evidence (reference `draft_evidence_0044`) and interpreted
  against Elara's explicit assignment and the approved style.

The registry expectations are manual semantic-review criteria; the harness does
not turn `validated` into an automatic semantic pass or launch another workflow.
Actual craft judgments may differ. Inspect the finding, evidence, and surrounding
prose instead of relying on overall scores or a single keyword. This batch permits
at most six calls, all Local, under the original per-call envelopes. It does not
authorize a full canary or claim a repeatability result.
