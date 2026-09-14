# v33 Cloud canary — batch 2, 2026-09-14

## Result

**4/4 stories completed, 21/21 scenes accepted, and 99/99 production calls
succeeded.** There were five prose revisions across four scenes, no failed
responses, no terminal failures, no manual retries and no adjudication calls.
Both prior v29 failures in this subset, **005 and 007**, now complete.

Scope is Cloud OH-V01-005–008, batch 2 of the frozen v33 cycle. Together with
[batch 1](step-19-cloud-v33-batch-1-2026-09-14.md), the cycle currently has
**8/8 completed cases and 42/42 accepted scenes**, 187 production calls
(186 succeeded, one recovered failure), and six prose revisions. The final four
cases have not been staged or run. This is not the full 12-case result.

| Cloud case | Status | Scenes | Calls (failed) | Revisions | Input / output tokens | Words |
| --- | --- | --- | --- | --- | --- | --- |
| OH-V01-005 | SUCCEEDED | 4/4 | 28 (0) | 4 | 311,253 / 26,343 | 3,236 |
| OH-V01-006 | SUCCEEDED | 5/5 | 20 (0) | 0 | 210,867 / 18,012 | 4,641 |
| OH-V01-007 | SUCCEEDED | 6/6 | 27 (0) | 1 | 253,850 / 20,465 | 3,347 |
| OH-V01-008 | SUCCEEDED | 6/6 | 24 (0) | 0 | 244,552 / 18,765 | 4,111 |

All four outputs meet their frozen advisory word ranges. 006 and 008 needed no
prose revision. Every final accepted version has a passing critique and no
blocking continuity findings. No exhausted-revision acceptance occurred.
Human story quality remains ungraded; Product Step 19 remains **IN PROGRESS**.

## Setup and frozen conditions

The user authorized the second batch after batch 1 completed. A new isolated
copy of the original human-approved pre-production seed was migrated from schema
0006 to 0007. The source seed SHA-256 remains
`400379c746487cecc0f26dca055c4f51ded5674407b16a0a7d42b7cc9071ab3f`.
It contained no production runs or artifacts; no old production checkpoint was
resumed. All four exact approval decisions and Blueprint hashes were verified.
No new Blueprint calls or human approvals were necessary.

Prompt **v33 / graph v9**, commit `70f408be142695a5bbb19e2e79432e49b4efce42`, and all
108 tracked runtime source hashes match batch 1. Existing documentation changes
from batch 1 were preserved. The original 48-case plan/campaign identity retains
approval lineage; `v33-cloud-cycle-2026-09-14` and the explicit four-case selection
define this execution. Historical deterministic run IDs may recur in different
isolated databases; directory plus run ID identifies the evidence.

| Case / seed | Production run ID | Approved Blueprint ID | Blueprint SHA-256 |
| --- | --- | --- | --- |
| OH-V01-005 / 19005 | `45fdb296-ac0f-5e95-b212-75de1d187f2b` | `39aa8578-f543-42b3-a16c-c1618972c95a` | `a75a46dd326824555baeac8e4161e8513c93a49c62f643f1feb0aa1c63c56302` |
| OH-V01-006 / 19006 | `634392b7-fe15-5536-a5d8-a08845cbd3bb` | `ac53818a-3c92-44a3-9fac-f38f439aa450` | `2c7d362abe7d9cc95d59526436cd8a81af3389331f30ca525c9c6eb87dc95e4e` |
| OH-V01-007 / 19007 | `899004a4-640f-5a29-ae11-c9ccc704f243` | `1a5fcba9-7098-4120-8336-39d85842eae1` | `bb4f57cf6310b549e67deab1c5e049c5363359836681d2ecde3241cb361c1c02` |
| OH-V01-008 / 19008 | `e9630c05-fb77-5fbe-b59c-24bdb86a785a` | `f0d170ff-fe13-4836-a9f2-60a48ebdd025` | `40ed2f2bd60ba4cc9162e2a27bbb4b35e237880c4c589fa65ab7bec178277aaf` |

All new calls request `gemma4:31b-cloud`, report `gemma4:31b`, and finish with
provider reason stop. Cloud profile digest is
`5feda6671bdb89f311cc171cf0917e7f6227596a2a42a9c4916778211a783c70`.
Ollama remains 0.34.0; the model alias digest matches v29 and v33 batch 1.
Remote weights and provider seed enforcement are not independently pinned.
The route remains the signed-in local Ollama Cloud endpoint at port 11434.

Seeds are 19005–19008. Limits match v29: $5 per story / $20 aggregate application
cost ceiling; 252 calls maximum across the batch (48/60/72/72); two prose
revision cycles per scene; 24,000 input / 8,000 output tokens and $0.20 per call;
7,200 seconds per story; 600-second HTTP timeout. The runtime, model settings,
limits and original evidence were not tuned during execution.

## Reviews and revisions

The 99 calls reconcile to **26 writer, 26 critic, 26 continuity and 21 Bible
calls**. All succeeded. There were 22 pass and four revise verdicts across the
26 critiques. Four revisions were critic-driven; one was continuity-driven.
All prose changes and original review artifacts are preserved, including
version-bound acceptance tests. No revision is identical to its prior draft.

| Case / scene | Trigger | Observed change | Character similarity |
| --- | --- | --- | --- |
| 005 / 1 | Critic: Henderson's private interpretation under Elias POV | Replaced private judgment with watch-checking and observable demeanor | 97.22% |
| 005 / 2, revision 1 | Critic: Elias's private realization under Sarah POV | Added perspective framing, but retained To Elias attribution; repair assessed unmet | 97.14% |
| 005 / 2, revision 2 | Critic: continued POV allegation and retained repair target | Explicitly filtered interpretation through Sarah observing Elias's expression; both targets assessed met | 98.45% |
| 005 / 4 | Continuity: identity-rejection evidence and alleged conflict with resolved identity | Expanded a surgical-graft reference into a reminder of the erased scar | 99.43% |
| 007 / 5 | Critic: Elara's inference of Julian's grief | Replaced feel grief radiating with suggested almost taste phrasing; repair assessed met | 98.87% |

Similarity is character-level SequenceMatcher with autojunk disabled, not a
quality metric. Four critic re-reviews carry five explicit repair assessments:
four met and one unmet. The scene-2 sequence in 005 demonstrates that an unmet
repair can remain blocking until another bounded revision passes. It does not
establish that every assessment was semantically correct.

Three diagnostic concerns remain for consolidation:

- **005/2:** the final assessment credits the phrase she realized with establishing
  Sarah's perspective, although it was already in the rejected revision. The
  final prose does add to Elias and an explicit observation of his expression.
  Those actual differences must be distinguished from overcrediting retained text.
- **005/4:** continuity selected the resolved identity as its canonical source,
  while the draft acknowledged that same resolution. It also said rejection
  evidence had been satisfied in earlier scenes, yet issued both a contradiction
  and missing-requirement blocker. Adding a recap satisfied the recheck. The
  cited assertions do not establish incompatible history; the remaining question
  concerns the scope of a story-level requirement. This is a concrete example of
  continued review overreach after v33's continuity-policy change.
- **007/5:** the original I could feel the grief radiating off him and the accepted
  The air around him felt heavy with a grief I could almost taste are both framed
  as first-person experience. The critic's met assessment also credits palpable,
  crushing weight, which was retained. The localized edit follows the requested
  wording, but the necessity of the original POV violation remains disputed.

No terminal adjudication was exercised: 005's second scene cleared at the existing
revision cap, and 007 cleared after one revision. These successes therefore do
not validate the live adjudicator path. They provide better inspectable repair
history while retaining unresolved questions about inference and requirement scope.

## Matched v29 comparison

The [consolidated v29 report](step-19-cloud-v29-consolidated-2026-09-12.md)
and the original batch-2 archive remain unchanged. Exact cases, approved
Blueprints, corpus, seeds, profiles and non-production workflow versions match.

| Contract | Completed | Accepted scenes | Calls | Failed | Revisions | Input tokens | Output tokens |
| --- | --- | --- | --- | --- | --- | --- | --- |
| v29 | 2/4 | 16/21 | 88 | 4 | 5 | 901,158 | 73,653 |
| v33 | 4/4 | 21/21 | 99 | 0 | 5 | 1,020,522 | 83,585 |

v29's 005 stopped on structured continuity repair exhaustion alongside unresolved
critic feedback; 007 stopped on hard-critic POV revision exhaustion. v33 completes
both, while retaining 006 and 008's completions and eliminating failed response
attempts in this execution. Accepted scenes increase from 16 to 21.

Calls increase from 88 to 99 because the candidate completes more of the stories.
Recorded tokens increase from 974,811 to **1,104,107** (1,020,522 input plus
83,585 output). Comparing these totals as if both versions completed the same
amount of work would misstate efficiency. The five-revision totals are equal but
occur in different scenes and for different reasons.

All **18 comparable initial drafts differ** from v29. Three more v33 initial
scenes lie beyond v29's failed production points and have no initial-draft pair.
This is a matched starting-condition comparison, not identical-prose evidence
that the reviewers became more accurate. The result is a completion improvement
on this subset, with semantic qualifications retained above.

## Time and accounting

Runner interval: 2026-09-14T19:31:07.500760+00:00 to 2026-09-14T19:45:48.686721+00:00,
approximately **21:31:08–21:45:49 Europe/Belgrade**. Elapsed time was
**881.186 seconds (14 minutes 41 seconds rounded)**. Summed recorded
invocation latency was **721.978 seconds**.

| Case | Production interval, local | Elapsed seconds | Recorded call latency |
| --- | --- | --- | --- |
| OH-V01-005 | 21:31:08–21:35:52 | 283.957 | 143.748 s |
| OH-V01-006 | 21:35:52–21:41:01 | 308.292 | 303.506 s |
| OH-V01-007 | 21:41:01–21:43:28 | 147.658 | 141.253 s |
| OH-V01-008 | 21:43:29–21:45:48 | 139.330 | 133.471 s |

006's first critic request recorded 200.630 seconds and succeeded without retry.
005's run elapsed time also exceeds its summed invocation latency substantially;
the available records do not identify the entire gap as provider time. Run
elapsed, recorded invocation latency and active timers measure different things.
No recovery, workflow failure, budget-pause or in-app control event was needed.
This batch was slower than v29's 453.888-second partial-completion run; it does
not establish a speed improvement. All stored estimated costs are $0.00, which
is app accounting rather than a verified provider bill.

## Evidence and checks

Local archive: `data/benchmarks/v0.1/v33-cloud-batch-2-2026-09-14/`.
The report is schema-valid, matches its plan digest and contains exactly the four
selected result IDs. All **201 selected-project artifact versions** passed
recomputed hashes. Final manuscripts match exact canonical scene references and
report content hashes. Database integrity and foreign-key checks passed; the
existing secret-export audit passed before the consistent snapshot was created.

Inherited non-production run/call counts, human-decision counts and run-control
counts match the original seed. Runtime source, source-seed, v29 evidence and
v33 batch-1 receipts were verified unchanged. No model call, new approval or
application change was introduced by diagnostic analysis.

The archive contains four manuscripts, the final snapshot, exact prompts/settings,
all production invocation/event evidence, review audits, five revision diffs,
initial-draft comparisons and inspection notes. The partial-story-evidence file
is empty because no story failed. Raw evidence remains local and git-ignored.
Hashes below identify it; they do not provide public access or replication.

| File | SHA-256 |
| --- | --- |
| plan.json | `9186049d072373428cf5fbbd14ae722e3336352d772c131b750066db8cf9cd34` |
| preflight.json | `a77740d8a475a6222b1751a93c9d48f31fb7aafae267c5a5e632001898831b15` |
| report.json | `d142f3449bd3cf18046ad1ae1278c12fc6a538a57b39f713436330825a0d8874` |
| completed-snapshot.db | `9b62b65bbe80e434cacdec05c29474f747be180a8db1e648947f051635d68eca` |
| diagnostics/analysis.json | `cc1becccc729805fc7749d6050da74e1420d5ebe790388dd6a64f0f66276e540` |
| diagnostics/invocation-evidence.json | `ca3b627d9306d950e640ec18d083bf370229963e657577185460726be349ee99` |
| diagnostics/inspection-notes.json | `15a67c9f18d1f93a3ce162b44db87a6e7eda293a7c432afad24c420e119960f0` |
| diagnostics/evidence-manifest.json | `c12801d58cb50baf928bb61370b84c02e71807baa0e9fdd03fa21a1faec243a0` |

The full-cycle diagnostic consolidation remains deferred until batch 3,
OH-V01-009–012, finishes. Batch 3 has not been staged or launched. Human reading,
quality and preference judgments remain separate work; no new combined score
with the manual samples is inferred.
