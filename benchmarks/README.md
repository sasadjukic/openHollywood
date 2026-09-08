# Open Hollywood benchmarks

Benchmark inputs are product artifacts, not ad-hoc development prompts.

`v0.1/corpus.json` contains the accepted 12 short-prose prompts with immutable
IDs and versions, target length, required elements, forbidden shortcuts, likely
failure modes, stressed rubric dimensions, research policy, and stable seeds.

Validate it and print its canonical digest:

```powershell
uv run --extra api python scripts/evaluation_harness.py validate-corpus
```

After all three model presets are completely configured in the local database,
create a campaign plan:

```powershell
uv run --extra api python scripts/evaluation_harness.py plan `
  --database data/open_hollywood.db `
  --output data/evaluations/campaign-plan.json
```

The plan expands the corpus into 48 cases: one direct single-model baseline and
Local, Cloud, and Hybrid agentic runs for every prompt. It pins the corpus hash,
workflow versions, exact secret-free profile configurations, model identifiers,
and per-prompt seeds. Existing plan files are not overwritten unless
`--overwrite` is explicit.

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

Run or resume agentic Blueprint preparation. The command stops at the mandatory
human checkpoint and never approves a Blueprint on the operator's behalf:

```powershell
uv run --extra api python scripts/evaluation_harness.py prepare-agentic `
  --database data/open_hollywood.db `
  --plan data/benchmarks/v0.1/formal-2026-08-01/plan.json
```

Once every selected case has either failed terminally or reached that checkpoint,
create a deterministic review packet, readable Markdown dossier, and reviewer
CSV. This step is offline and makes no model calls:

```powershell
uv run --extra api python scripts/evaluation_harness.py package-blueprint-review `
  --database data/open_hollywood.db `
  --plan data/benchmarks/v0.1/formal-2026-08-01/plan.json `
  --reviewer-id primary-reviewer `
  --packet-output data/benchmarks/v0.1/formal-2026-08-01/blueprint-review-packet.json `
  --guide-output data/benchmarks/v0.1/formal-2026-08-01/blueprint-review-guide.md `
  --form-output data/benchmarks/v0.1/formal-2026-08-01/blueprint-review.csv
```

Review every Blueprint in the Markdown dossier. Enter `yes` in `approved` only
after approving the exact Blueprint version shown; notes are optional. Do not
edit the prefilled lineage fields. The approval command rejects incomplete
coverage, changed lineage, a foreign campaign, or a Blueprint whose immutable
version or digest no longer matches the packet. It is also offline:

```powershell
uv run --extra api python scripts/evaluation_harness.py approve-blueprints `
  --database data/open_hollywood.db `
  --plan data/benchmarks/v0.1/formal-2026-08-01/plan.json `
  --packet data/benchmarks/v0.1/formal-2026-08-01/blueprint-review-packet.json `
  --review-form data/benchmarks/v0.1/formal-2026-08-01/blueprint-review.csv
```

Each applied approval writes a durable human event containing the reviewer ID,
review-packet digest, and exact Blueprint version/digest before resolving the
existing LangGraph interrupt. Replaying the same completed form is idempotent.
After all approvals are applied, run or resume autonomous production:

```powershell
uv run --extra api python scripts/evaluation_harness.py run-agentic `
  --database data/open_hollywood.db `
  --plan data/benchmarks/v0.1/formal-2026-08-01/plan.json `
  --report data/benchmarks/v0.1/formal-2026-08-01/report.json
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

The private blinding key and generated answer key must not be distributed with
the public A/B review packet. None of these files may contain API keys.

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
