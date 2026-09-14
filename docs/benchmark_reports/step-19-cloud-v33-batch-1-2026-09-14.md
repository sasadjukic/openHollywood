# v33 Cloud canary — batch 1, 2026-09-14

## Result and scope

**4/4 stories completed; 21/21 scenes accepted; 87/88 production calls
succeeded.** One continuity response failed validation and recovered on its next
attempt. One scene received one prose revision. No terminal failure, manual
retry, adjudication or revision-limit exhaustion occurred.

This is Cloud OH-V01-001 through OH-V01-004, batch 1 of the planned three-batch
v33 cycle. Batches 2 and 3 have not been staged or launched. Product Step 19
remains **IN PROGRESS**; these are production outcomes, not human literary grades.
The user's [September 13 manual sample](manual-v29-v33-cloud-production-2026-09-13.md)
and the September 12 canary remain separate evidence sets.

| Cloud case | Status | Scenes | Calls (failed) | Revisions | Input / output tokens | Words |
| --- | --- | --- | --- | --- | --- | --- |
| OH-V01-001 | SUCCEEDED | 5/5 | 21 (1) | 0 | 198,133 / 17,020 | 3,232 |
| OH-V01-002 | SUCCEEDED | 5/5 | 20 (0) | 0 | 185,629 / 15,974 | 3,516 |
| OH-V01-003 | SUCCEEDED | 6/6 | 24 (0) | 0 | 241,312 / 18,799 | 4,086 |
| OH-V01-004 | SUCCEEDED | 5/5 | 23 (0) | 1 | 256,565 / 21,288 | 4,510 |

All four manuscripts meet their frozen advisory word-count ranges. Three stories
had no failed invocation; two (002 and 003) had neither failed calls nor prose
revision. Completion and word count do not establish literary quality.

## Frozen setup and authorization

The user authorized staging and immediately starting the first v33 batch.
Preflight verified the four existing human-approved Blueprints, exact content
hashes, seeds 19001–19004, and Cloud profile against v29 batch 1. No new Blueprint
call or approval was needed. The source was the original clean seed:
`data/benchmarks/v0.1/formal-2026-08-01/pre-production-approved.db`,
SHA-256 `400379c746487cecc0f26dca055c4f51ded5674407b16a0a7d42b7cc9071ab3f`.
It had no production runs or production artifacts. A new isolated copy was
migrated from schema 0006 to 0007; the original seed was preserved.

Runtime: **prompt v33 / graph v9**, commit `70f408be142695a5bbb19e2e79432e49b4efce42`.
Tracked runtime source hashes were frozen before execution and verified unchanged
by the runner and post-run analysis. No production code or prompt was edited.
The worktree was clean at staging; documentation updates record the run afterward.

The original 48-case plan envelope and campaign ID preserve seed and approval
lineage. The separate scope `v33-cloud-cycle-2026-09-14`, batch ID and four explicit
case IDs define this execution. This does not relabel the old all-profile campaign
or weaken whole-canary comparison/sealing rules. Run IDs are deterministic and
can equal historical IDs in separate databases; the evidence directory identifies
the execution.

| Case / seed | Production run ID | Approved Blueprint ID | Blueprint SHA-256 |
| --- | --- | --- | --- |
| OH-V01-001 / 19001 | `7643e3e9-2899-5c27-8b38-c64559f24cde` | `6c3e8a05-6c3f-4c44-95cf-09a10fe36f38` | `49bba4def7783dcb9e9c313c3ff21625dc3760147b0fbbecb4f8b08018ff66e1` |
| OH-V01-002 / 19002 | `b192bed7-e068-54bb-9c52-4749bf1caa50` | `0dcdcc34-65ee-4e82-8706-22a689e76f5e` | `bf7bc76b7f5dae5d533997569e4314c2f98c708cb25306c7433f6888f9e060ef` |
| OH-V01-003 / 19003 | `8de6b17d-9601-5d4f-82d1-0b7eebd8cfb5` | `07969472-3b29-4003-b705-7120095c4d9e` | `3e8cd4907cdee392ae671ed076e612c62020d549b409cdeeb215f26bb83665b1` |
| OH-V01-004 / 19004 | `801723ef-2659-51ed-9d45-a7dabcfa2ecd` | `6523e881-6b59-48a3-954e-021398e9f445` | `a118e18fb30afcf1ad8fb55db08cca77024063b2475e71839fa6f2ac6574dfd1` |

All roles use the frozen Cloud profile digest
`5feda6671bdb89f311cc171cf0917e7f6227596a2a42a9c4916778211a783c70`.
All new calls request `gemma4:31b-cloud` and report `gemma4:31b`. Inference uses
the existing signed-in Ollama Cloud route at `http://127.0.0.1:11434`.
Ollama is 0.34.0, the same as v29, and the model alias digest matches. Remote
weights and provider seed enforcement remain independently unpinned.

Cases ran sequentially with the existing $5 per-story / $20 aggregate application
cost ceiling, at most 252 production calls across the batch, 24,000 input /
8,000 output tokens per call, two prose revision cycles per scene, 7,200 seconds
per story and a 600-second HTTP timeout. Per-call cost ceiling is $0.20.
Full settings and persisted budgets are in preflight and the database.

## Calls, failure evidence and revision

The 88 fresh production records reconcile to **22 writer, 22 critic, 23 continuity
and 21 Bible calls**. There are 22 successful drafts, 22 passing critiques,
22 successful continuity reports and 21 accepted-scene Bible updates. The one
extra continuity record is the recovered response failure. Inherited Blueprint
calls in the seed are excluded from these totals.

Production usage is **881,639 input + 73,081 output = 954,720 tokens**. Failed-
attempt usage is included. Estimated cost is stored as $0.00; this is app
accounting, not proof of free inference or a reconciled subscription bill.

**001, scene 4 revision 0:** continuity marked time coverage partial, described
night as implicit from the previous scene, and supplied no draft evidence handles.
Application materialization rejected the response as
`requirement_coverage_evidence_invalid`. The failed invocation
`e2d5e7e6-082f-4437-bd20-db12038bb32f` retains a bounded, untruncated review-failure
capture with candidate/input identity; it is explicitly unvalidated evidence.
Invocation `6fca13a8-61b5-4ff1-9502-f14ebb01b520` succeeded on attempt 2 with the
same task fingerprint and exact input-version set. No manuscript revision was
needed for that failure. This reproduces the time-coverage interface weakness
seen in the manual review; v33 has not eliminated it.

**004, scene 4:** the critic passed the original scene, but continuity blocked
Maya's encrypted device and apparent active pickup coordination under the
isolation_protocol rule. That rule says the safehouse is physically/electronically
isolated and characters cannot call for help or verify outside information.
The revision removes the device, changes arranging transit to counting seconds,
and makes the five-a.m. pickup an agreement made before entering the house.
The next critic passed and continuity cleared the scene.

Before: `10d95462-9667-408e-b0c8-afc2f79f16b2`; after:
`37a1a66a-6f88-481f-b543-10ecfc7d2fa4`. Character similarity is **96.78%**,
using SequenceMatcher with autojunk disabled. Unlike a no-op edit, this visibly
addresses the alleged communication mechanism while preserving most prose.
However, the original passage implied rather than showed a transmitted message;
the necessity of the allegation and complete rule interpretation remain matters
for contextual review. The finding's companion assessment also says no rule
authorizes pre-arranged pickups while its repair recommendation proposes prior
arrangement; that overbroad wording should not be treated as new canon.

This is the same broad isolation-rule issue seen in v29's 004/4, with different
prose. All 21 final accepted versions have passing critiques and zero blocking
continuity findings. No critic repair test or terminal adjudication was needed.
Successful review does not certify semantic correctness.

## Matched v29 comparison

The [v29 batch-1 report](step-19-cloud-v29-batch-1-2026-09-12.md) remains unchanged.
Post-run verification matched case IDs, corpus, non-production workflow versions,
profile, seeds and exact approved Blueprint hashes for this four-case subset.

| Contract | Completed | Scenes | Calls | Failed calls | Revisions | Input tokens | Output tokens |
| --- | --- | --- | --- | --- | --- | --- | --- |
| v29 | 4/4 | 21/21 | 99 | 0 | 5 | 1,026,303 | 81,611 |
| v33 | 4/4 | 21/21 | 88 | 1 | 1 | 881,639 | 73,081 |

v33 preserves all four completions with **11 fewer calls (11.1%)** and **four
fewer prose revisions**. Recorded total tokens fall from 1,107,914 to 954,720
(**13.8%**). Failed calls rise from zero to one; the new failure recovered within
the existing allowance. This is reduced iteration in this execution, not an
unqualified improvement on every reliability measure.

All **21 initial scene drafts differ** from v29's matched initial drafts, as
recorded by exact prose hashes. Consequently the result does not isolate review
policy from writer variation or show that identical allegations were judged more
accurately. There were no location/timeline blockers in this v33 batch, but their
absence alone is not proof of reduced false positives. A second execution or
saved-input probes would address different questions from this complete-story run.

## Time and the long critic call

Runner interval: **2026-09-14T19:14:39.776365+00:00–2026-09-14T19:26:02.041943+00:00**,
or approximately **21:14:40–21:26:02 Europe/Belgrade**. Total elapsed time was
**682.266 seconds (11 minutes 22 seconds rounded)**. Recorded production
invocation latency sums to **651.548 seconds**.

| Case | Production interval, local | Elapsed seconds | Recorded invocation latency |
| --- | --- | --- | --- |
| OH-V01-001 | 21:14:41–21:16:27 | 106.037 | 100.059 s |
| OH-V01-002 | 21:16:27–21:18:12 | 104.817 | 93.513 s |
| OH-V01-003 | 21:18:12–21:20:24 | 131.803 | 126.066 s |
| OH-V01-004 | 21:20:24–21:26:01 | 337.602 | 331.910 s |

004's first critic request recorded **202.158 seconds** of latency and succeeded
without a retry. The evidence establishes a long request, not its provider-side
cause. No timeout, recovery event, budget pause or manual control was needed.
The batch took longer than v29's 492.722 seconds despite fewer calls, so this
execution does not demonstrate a wall-time improvement. Provider variability and
orchestration separate latency, elapsed time and active timer measurements.

## Evidence and verification

Local evidence directory:
`data/benchmarks/v0.1/v33-cloud-batch-1-2026-09-14/`.

The schema-validated report matches the frozen plan and exactly the four selected
results. Every accepted manuscript matches the canonical scene references and
report hash. All **192 selected-project artifact versions** passed recomputed
content hashes. The final database passed integrity and foreign-key checks and
the existing secret-export audit before its consistent snapshot was created.

The bundle includes plan/preflight, runner status/logs, completed-snapshot.db,
four manuscripts, full production invocation/event evidence, successful and failed
review diagnostics, the exact revision diff, initial-draft hash comparisons and
reproduction scripts. The evidence manifest binds bytes and hashes. Source seed,
v29 plan/preflight/report/snapshot and runtime source hashes were verified intact.
No human scores, new model configurations or additional story executions were
introduced by the analysis.

| Evidence file | SHA-256 |
| --- | --- |
| plan.json | `9186049d072373428cf5fbbd14ae722e3336352d772c131b750066db8cf9cd34` |
| preflight.json | `f66b33fb15885fcfa4607920c14fdeabaa3ea227d8ea36daa377f8ea385dadcd` |
| report.json | `0103503d5a6e3a24bc1eeac0205e535fa5a43930f977d06e2eccf8683a47324b` |
| runner-status.json | `efddbaf491eefc6b65260da74a640ab93564bc3929f023046639b6fb277f87ee` |
| completed-snapshot.db | `215fee8824446b33fe96cf92a8cc0448984ea2add9c78546fc55483a52115c59` |
| diagnostics/analysis.json | `6f1d08470c282a16551348c10c3dc8e7db8fa637a873dc014809013f5eccfeac` |
| diagnostics/invocation-evidence.json | `b3e86c5c15368d439fd04fa6f1dd1d47164e3df1266fcd2e5e091eb874dd0ed9` |
| diagnostics/evidence-manifest.json | `17e36f5b0e4604e16eee44c7b0f7784a6fa2b5628c5b7fc18774f9437a681dea` |

Raw databases and story evidence remain git-ignored local files; the public report
contains conclusions and receipts. Hashes identify evidence but do not supply
public access or independent replication.

## Next batch

Batch 1 is complete. The next planned batch is Cloud OH-V01-005–008, followed by
009–012. Keep v33 and the established limits frozen across the cycle. Cases 005,
007 and 009 failed in v29 and deserve close diagnostic attention, while all cases
remain necessary for regression coverage. Consolidate only after all three
batches finish; do not present 4/4 as a full 12-case result. Human quality and
preference review remain separate outstanding work.
