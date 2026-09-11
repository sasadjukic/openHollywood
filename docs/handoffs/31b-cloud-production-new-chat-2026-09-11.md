# New-chat handoff: 31B Cloud production evaluation

Prepared **September 11, 2026**. This is context for the next conversation, not
an instruction to launch model calls merely because the document was attached.
Follow the user's accompanying request.

## Objective and agreed direction

Determine whether `gemma4:31b` can reliably complete Open Hollywood's full
short-fiction production workflow, how it recovers from failures, and whether
its completed stories are good. Since September 11, it is our designated testing
model, requested through Ollama Cloud as **`gemma4:31b-cloud`**.

Start with the latest **production prompt v29 / graph v7**. Both are present in
`engine/open_hollywood_engine/workflows/production_contracts.py` at handoff.
Do not revert to v25 or introduce v30 merely to start testing.

E4B-driven tuning and further narrow proofreading experiments are deferred.
Keep Local, Hybrid and Cloud in the product; test only Cloud now. Consider Hybrid
only after successful Cloud workflows and completion of the scoped Cloud-first
Step 19 evaluation. Step 19 remains **IN PROGRESS**.

## Production plan: three runs, four stories each

Cover the frozen 12-prompt corpus in **three four-story batches**. Default split,
unless the user selects another grouping:

| Batch | Cloud corpus cases |
| --- | --- |
| 1 | OH-V01-001 through OH-V01-004 |
| 2 | OH-V01-005 through OH-V01-008 |
| 3 | OH-V01-009 through OH-V01-012 |

These are 12 distinct stories, not three repetitions of the same four. The user
may request one batch or all three together. Preparing all three does not imply
concurrent model execution: use bounded sequential execution by default and
verify isolation before any concurrency. Keep the contract, profile, seeds and
comparison conditions frozen across a cycle; label any changed-condition rerun
separately.

Use clean production state and preserve historical databases, reports, logs and
approvals. Reuse only verified, exactly approved Blueprint versions with valid
lineage; otherwise obtain human Blueprint approval before autonomous production.
Never resume an old production checkpoint under a new contract. The inherited
Local OH-V01-006 failure is **not** an exclusion for Cloud case 006.

## Essential evidence from the previous conversation

- Cloud completed **4/4** selected stories under v23, **4/4** under v25 and
  **3/4** under v26. Preserve v23/v25 as reference canaries. v26 Cloud-002 failed
  the critic's exact-evidence contract. No full v27/v28/v29 canary has completed.
- 31B scored **18/18** on the matched frozen POV comparison, **24/24** on novel
  POV labels, and **9/9** valid and target-POV-correct on v29 full-critic transfer.
  These focused tests do not establish full-production or literary quality.
- c05 demonstrated actual minimal sentence repair: **3/3** exact removals of two
  duplicate sentences, all other prose preserved, followed by **3/3** clean
  re-critiques. The corrected human judgment is “fix the repetition,” not “the
  whole scene is bad.”
- Word-repair advice remains unreliable. The latest comparison scored **17/21**
  minimal recommendations for the reference versus **15/21** for the candidate;
  both falsely required changes to valid “He passed her her mittens.” Word edits
  were not executed. Do not silently adopt the diagnostic minimal-repair
  instruction or prose-plus-catalog input in production.

## What to establish before and after a run

Before launch, inspect `AGENTS.md`, current Git state, actual contract versions,
Cloud role assignments, source approvals, budgets and provider availability.
At handoff the branch is `main`; September 11 documentation changes are still
uncommitted. Preserve them and recheck rather than assuming a clean checkout.
The reported allowance of roughly 4,000 requests per two weeks is an operator
planning estimate, not an independently verified quota.

Inspect the existing harness before staging: its historical campaign and canary
comparison tools enforce all-profile/matched-case invariants. Do not weaken those
checks to label a new Cloud-only 12-story campaign comparable. Declare the new
scope and compare matched historical Cloud cases separately.

After each batch, report completion, accepted/planned scenes, clean versus
recovered successes, terminal failures, retries and human intervention. Diagnose
failure layers and recurring criticism; inspect whether repairs preserve good
prose. Record usage, latency and environmental events. The earlier two-hour
clock correction came from the operator's Ubuntu/Windows dual boot, not the app.

Provide completed manuscripts for human review. Completion is not quality, and
12 completions alone do not close Step 19: retain the direct-model baseline,
blind human rubric/hard gates, preference, budget and repeatability requirements.

## References, only as needed

- [Current testing policy and rationale](../benchmark_reports/model-testing-direction-2026-09-11.md)
- [Exact 31B results, caveats and source receipts](../benchmark_reports/gemma4-31b-evaluation-register-2026-09-11.md)
- [Deferred critic/word-repair issue draft](../issue_drafts/gemma4-31b-critic-repair-follow-up.md)
- [Step 19 tracker](../../open_hollywood_bible/step_by_step_implementation.md) and [canonical evaluation criteria](../../open_hollywood_bible/product_contract_and_benchmarks.md)
- [Harness operations](../../benchmarks/README.md), [frozen corpus](../../benchmarks/v0.1/corpus.json) and [pinned v23/v25 baselines](../../benchmarks/v0.1/canary-baselines.json)

Raw evidence remains in local, git-ignored `data/diagnostics/` and
`data/benchmarks/v0.1/`; a public checkout will not contain it. The old conversation
is useful background, but the repository and immutable evidence are the working
sources of truth. No run was staged or launched by this handoff.
