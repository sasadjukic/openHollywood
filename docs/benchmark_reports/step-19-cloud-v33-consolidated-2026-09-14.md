# v33 Cloud canary — consolidated diagnostics, 2026-09-14

## Result and interpretation

**12/12 stories completed (100%), with all 64/64 planned scenes accepted.**
All three batches are finished. The cycle used **288 fresh production
calls: 286 succeeded and two failed responses recovered
automatically**. Ten prose revisions occurred across nine distinct scenes.
There were no terminal failures, manual retries, new approvals or adjudication
calls. The contract and limits remained frozen throughout.

The matched v29 canary completed 9/12 stories and 54/64 scenes. **005, 007 and 009,
the three v29 failures, all complete under v33**, while all nine prior successes
are retained. This is a meaningful completion gain in this twelve-case run.
It is not proof of perfect reliability, correct criticism or literary quality.

| Batch / Cloud cases | Completed | Scenes | Calls / failed | Revisions | Runner time |
| --- | --- | --- | --- | --- | --- |
| 1 / 001–004 | 4/4 | 21/21 | 88 / 1 | 1 | 11m 22s |
| 2 / 005–008 | 4/4 | 21/21 | 99 / 0 | 5 | 14m 41s |
| 3 / 009–012 | 4/4 | 22/22 | 101 / 1 | 4 | 9m 29s |

This is the final diagnostic document for the entire v33 Cloud cycle, incorporating
[batch 1](step-19-cloud-v33-batch-1-2026-09-14.md),
[batch 2](step-19-cloud-v33-batch-2-2026-09-14.md) and the final batch's preserved
report/database evidence. Earlier batch documents retain their dated partial-cycle
status. The experiment is complete; **Product Step 19 remains IN PROGRESS**.

## Frozen setup and scope

Production used **prompt v33 / graph v9** at commit
`70f408be142695a5bbb19e2e79432e49b4efce42`. All 108 tracked runtime hashes
matched across the three preflights and after execution. There was no production
code, prompt, retry or budget change during this cycle.

Requested model: **gemma4:31b-cloud**; provider-reported model: **gemma4:31b**.
All substantive roles used the frozen Cloud profile through signed-in Ollama
0.34.0 at `http://127.0.0.1:11434`. All calls report provider finish reason stop,
including both responses rejected by application validation.

- Scope: `v33-cloud-cycle-2026-09-14`, Cloud OH-V01-001–012 only.
- Seeds: **19001–19012**, one execution per distinct case, not repeated trials.
- Original approved-seed SHA-256: `400379c746487cecc0f26dca055c4f51ded5674407b16a0a7d42b7cc9071ab3f`.
- Cloud profile SHA-256: `5feda6671bdb89f311cc171cf0917e7f6227596a2a42a9c4916778211a783c70`.
- Plan content SHA-256: `1d7657f30acb6e3f2550704dd8cab399b612d76f8d54374c1bffd880e01ff2c4`.
- Model alias digest: `c382fbfbc73b6fdd08c8549c23caedc6e62eb09933c65a1fb82dbf3398320a4e`.

Each batch used a fresh isolated copy of the same original approved seed,
migrated from schema 0006 to 0007. The seed had no production runs or artifacts.
Exact Blueprint approval/version/hash relationships were checked; inherited
Blueprint/direct-baseline calls are excluded from production totals. There were
no new Blueprint calls, human decisions or in-app run-control commands.

The original 48-case plan envelope and campaign identity preserve approval
lineage; explicit selections define this Cloud-only experiment. It is not a
sealed all-profile campaign. Evidence is identified by directory plus run ID,
since deterministic historical IDs can recur in isolated databases. Remote
weights and provider seed enforcement are not independently pinned.

Limits stayed at **$5 per story / $20 per batch**, $60 summed application ceilings;
24,000 input / 8,000 output tokens and $0.20 per call; **two prose revision cycles
per scene**; 7,200 seconds per story; 600-second HTTP timeout. Aggregate call
ceilings were 252, 252 and 264, respectively. No terminal failure was rerun or
replaced, and no cap was raised to obtain these outcomes.

## All story outcomes

Every case below succeeded. All final manuscripts meet their frozen advisory
word ranges. Every accepted scene's final critique passes, with zero blocking
continuity findings. These are application acceptance results, not human scores.

| Cloud case | Scenes | Calls / failed | Revisions | Input / output tokens | Words |
| --- | --- | --- | --- | --- | --- |
| OH-V01-001 | 5/5 | 21 / 1 | 0 | 198,133 / 17,020 | 3,232 |
| OH-V01-002 | 5/5 | 20 / 0 | 0 | 185,629 / 15,974 | 3,516 |
| OH-V01-003 | 6/6 | 24 / 0 | 0 | 241,312 / 18,799 | 4,086 |
| OH-V01-004 | 5/5 | 23 / 0 | 1 | 256,565 / 21,288 | 4,510 |
| OH-V01-005 | 4/4 | 28 / 0 | 4 | 311,253 / 26,343 | 3,236 |
| OH-V01-006 | 5/5 | 20 / 0 | 0 | 210,867 / 18,012 | 4,641 |
| OH-V01-007 | 6/6 | 27 / 0 | 1 | 253,850 / 20,465 | 3,347 |
| OH-V01-008 | 6/6 | 24 / 0 | 0 | 244,552 / 18,765 | 4,111 |
| OH-V01-009 | 6/6 | 24 / 0 | 0 | 232,011 / 18,743 | 4,253 |
| OH-V01-010 | 5/5 | 20 / 0 | 0 | 211,332 / 17,111 | 3,929 |
| OH-V01-011 | 5/5 | 32 / 0 | 4 | 302,673 / 25,988 | 3,752 |
| OH-V01-012 | 6/6 | 25 / 1 | 0 | 281,937 / 22,480 | 3,979 |

10 stories completed with no failed call;
6 had neither failed calls nor
prose revisions. Two stories completed after automatic structured-response repair.
Prose revisions and failed-call retries are different measures.

Batch 3 completed **009–012, 22/22 scenes, 101 calls (100 succeeded, one
recovered failure)**. Cases 009,
010 and 012 needed no prose revisions. 011 needed four POV revisions, each
accepted on its next review. The prior 009 critic-validation failure did not recur.

## Matched v29 comparison

The [v29 consolidated report](step-19-cloud-v29-consolidated-2026-09-12.md) and
its three source archives remain unchanged. Cases, corpus, approved Blueprints,
seeds, Cloud profile, non-production workflow versions and limits match. Production
prompt/graph versions differ: v29/v7 versus v33/v9.

| Metric | v29, September 12 | v33, September 14 |
| --- | --- | --- |
| Completed stories | 9/12 | 12/12 |
| Accepted scenes | 54/64 | 64/64 |
| Production calls | 268 | 288 |
| Failed calls | 7 | 2 |
| Prose revisions / distinct scenes | 13 / 12 | 10 / 9 |
| Input tokens | 2,767,113 | 2,930,114 |
| Output tokens | 224,110 | 240,988 |
| Total tokens | 2,991,223 | 3,171,102 |
| Summed runner seconds | 1398.995 | 2132.449 |

v29's **005** stopped on continuity structured-repair exhaustion alongside
unresolved POV feedback; **007** exhausted its hard-critic revision limit;
**009** stopped after repeated assigned-character POV validation failures.
v33 completes all three within the original bounds.

The candidate completes ten more scenes, so raw calls and tokens compare different
amounts of finished work. They must not be presented as equal-work efficiency
measurements. All **57 paired initial drafts differ**; 7 v33 initial
scenes have no v29 counterpart because of earlier failure points. These are
matched starting conditions, not identical-prose reviewer comparisons. One run
cannot isolate the effects of individual steps in the v30–v33 changes.

## Failed responses and recovery

Both failed invocations came from the continuity supervisor on original drafts:
**001/4** marked `scene_plan_time_context` coverage **partial**, and **012/3**
marked it **met**, each without exact candidate-draft evidence references. Both
provider responses ended with stop. Application materialization rejected them
with `schema_validation_failed`; neither was a transport failure or a rejected
prose draft.

| Case / scene | Failed invocation | Successful same-task repair |
| --- | --- | --- |
| 001/4 | `e2d5e7e6082f4437bd20db12038bb32f` | `6fca13a861b54ff19502f14ebb01b520` |
| 012/3 | `86a22145902c4a6485b7290e9bd234d6` | `f5a7dec04d9d4cb2b82690ce9c04dbf4` |

Each repair used the same task fingerprint and exact input artifact versions,
passed, and continued without prose revision. Both unvalidated review captures
are retained and untruncated. Two automatic retry invocations occurred and both
succeeded. The recurring coverage-evidence error remains a concrete boundary
weakness despite the improved completion result. No terminal failure, workflow
recovery incident or budget pause is recorded.

The **012/3 capture** also exposes a separate semantic issue. The failed review
alleged that Bunny saying the freezer door “was closed” contradicted Alistair's
canonical observation that it was “unlocked shortly after the commotion.” Closed
and unlocked are compatible states. The allegation also compares a character's
recollection and belief that someone was trapped with an observation at another
moment; it does not establish incompatible canonical history.

The same-draft structured retry drops that allegation and treats unstated time
of day as **absent/advisory**, allowing acceptance. This is semantic variation
during structured-response repair, not a prose repair or formal adjudication.
The failed finding was unvalidated and never became an accepted continuity
artifact. Better failure evidence makes the distinction visible. This narrow
check does not settle the story's broader key/lock causal logic.

## Revisions, acceptance tests and remaining concerns

| Case / scene | Revision | Trigger | Character similarity |
| --- | --- | --- | --- |
| OH-V01-004/4 | 1 | continuity | 96.78% |
| OH-V01-005/1 | 1 | critic | 97.22% |
| OH-V01-005/2 | 1 | critic | 97.14% |
| OH-V01-005/2 | 2 | critic | 98.45% |
| OH-V01-005/4 | 1 | continuity | 99.43% |
| OH-V01-007/5 | 1 | critic | 98.87% |
| OH-V01-011/1 | 1 | critic | 94.65% |
| OH-V01-011/2 | 1 | critic | 99.44% |
| OH-V01-011/3 | 1 | critic | 96.12% |
| OH-V01-011/5 | 1 | critic | 98.75% |

Character similarity uses SequenceMatcher with autojunk disabled. Every revised
prose text differs from its predecessor; similarity measures preservation, not
quality or correctness. Eight revisions were critic-driven and two were
continuity-driven. Across persisted critiques, 66
passed and 8 requested revision. Final passing
reviews do not establish that every earlier allegation was necessary.

Eight critic re-reviews contain **nine version-bound repair assessments: eight
met and one unmet**. In 005/2, the first repair remains blocked; the second clears
both retained and new targets. This demonstrates an inspectable bounded repair
sequence. No case reached terminal adjudication, so this cycle provides no live
coverage of the v32 adjudicator path.

### Batch 1: isolation rule, 004/4

Continuity cited the safehouse isolation protocol against an encrypted device and
arranging transit. The revision removes that mechanism and invokes a previously
agreed five-AM pickup. The actual edit is visible and targeted. The original
passage implied arranging communication rather than showing transmission, and
one assessment denied authorization for a prearranged pickup while the advice
proposed it. The accepted recheck is not proof that every part of the original
reasoning was sound; review allegations and recommendations do not create canon.

### Batch 2: POV, recap demands and overcredited edits

- **005/1:** Henderson's asserted private judgment becomes watch-checking and
  observable demeanor under Elias's POV. The edit directly addresses the cited
  unauthorized access.
- **005/2:** the final assessment credits “she realized,” although it was already
  present in the rejected revision. The final draft also adds “to Elias” and
  “Looking at his expression, she saw he perceived it as.” There are actual
  contextual changes, but the assessment overcredits retained wording.
- **005/4:** continuity cites the resolved identity as authority while the draft
  acknowledges that same resolution. Its assessment says the earlier rejection
  evidence was already satisfied, yet raises both contradiction and missing-
  requirement blockers. Adding a reminder that the surgical graft erased the
  scar passes. The cited assertions do not demonstrate incompatible history;
  the remaining issue is the scope of a story-level requirement. This is a
  concrete instance of review overreach despite the v33 distinction between
  contradiction and development.
- **007/5:** “I could feel the grief radiating off him” becomes the critic's
  suggested “The air around him felt heavy with a grief I could almost taste.”
  Both are subjective first-person experience. The assessment partly credits
  retained “palpable, crushing weight” wording. The requested local change
  passes, but the necessity of the original POV violation remains disputed.

### Batch 3: 011's four POV repairs

Scenes 1, 2, 3 and 5 were revised once each. The original critiques identify
specific other-character interiority: Elias's private perception and desire in
scene 1; Clara's motives in scene 2; Elias's perceived stubbornness and realization
in scene 3; and his acceptance of the house's ghosts in scene 5. Exact before/after
passages and acceptance assessments are preserved in the final batch revision
review. All four re-critiques pass. These successes document targeted repair and
bounded completion; the surrounding context still matters when judging whether
an assertion was already attributable to the assigned perspective.

Two qualifications remain in 011. In **scene 2**, the rejected motive attribution
already follows “Elias observed” and visible whitening knuckles. The accepted
edit adds “To him, it seemed as if.” The explicit qualifier is new, but the
preceding observational context already existed; whether a hard blocker was
necessary remains disputed. In **scene 3**, the revision removes “He realized”
and adds Clara's interpretation and visible posture. Its met assessment also
credits “she saw not a critic, but a man,” which was retained from the earlier
draft. Actual repairs and retained supporting text should be distinguished.

009 completed its multi-perspective story without a hard finding in this run.
That result and 011's repeated POV repairs show differing review demand across
cases, not a causal proof that a genre or character count determines failure.
012 completed its ensemble case in 25 calls, including the recovered continuity
response described above, with no prose revision.

## Time and accounting

**2,930,114 input + 240,988 output =
3,171,102 recorded production tokens.**

| Role | Calls / failed | Input / output tokens | Latency total / median / max |
| --- | --- | --- | --- |
| continuity_supervisor | 76 / 2 | 722,087 / 62,915 | 348.590 / 4.312 / 12.672 s |
| scene_critic | 74 / 0 | 1,144,110 / 40,256 | 672.967 / 3.743 / 202.158 s |
| scene_writer | 74 / 0 | 581,744 / 77,096 | 567.311 / 7.245 / 14.660 s |
| story_bible_maintainer | 64 / 0 | 482,173 / 60,721 | 322.261 / 4.585 / 19.455 s |

| Batch | Start UTC | Finish UTC | Runner seconds | Call latency seconds |
| --- | --- | --- | --- | --- |
| 1 | 2026-09-14T19:14:39.776365+00:00 | 2026-09-14T19:26:02.041943+00:00 | 682.266 | 651.548 |
| 2 | 2026-09-14T19:31:07.500760+00:00 | 2026-09-14T19:45:48.686721+00:00 | 881.186 | 721.978 |
| 3 | 2026-09-14T19:53:49.033026+00:00 | 2026-09-14T20:03:18.030771+00:00 | 568.998 | 537.603 |

Summed runner time is **2132.449 seconds
(35m 32s)**, excluding gaps between batches. Recorded
invocation latency sums to **1911.129 seconds**. Europe/Belgrade
was UTC+02:00; timestamps above are explicit UTC. Runner elapsed time, active
workflow timers and recorded call latency measure different intervals.

The first critic call in 004 took 202.158 seconds; the first in 006 took 200.630
seconds. Both succeeded without retry. 005 also has an elapsed-time gap beyond
summed call latency whose entire cause is not identified in the records. The
cycle is slower than v29 in summed runner time and completes more work; no
Cloud-versus-Local speedup ratio was measured.

Stored estimated costs total **USD 0.00**. These
zero-priced application records are not a verified provider bill or subscription
allocation. The experimental $5 ceilings do not establish the normal product
cost target. Cost acceptance remains open.

## Evidence, verification and reading index

All three batch archives are preserved under
`data/benchmarks/v0.1/v33-cloud-batch-{1,2,3}-2026-09-14/`.
The consolidated analysis, all-case lineage, repair-audit index and reading index
are in `data/diagnostics/v33-cloud-cycle-2026-09-14/`.

| Batch | Report SHA-256 | Evidence manifest SHA-256 |
| --- | --- | --- |
| 1 | `0103503d5a6e3a24bc1eeac0205e535fa5a43930f977d06e2eccf8683a47324b` | `17e36f5b0e4604e16eee44c7b0f7784a6fa2b5628c5b7fc18774f9437a681dea` |
| 2 | `d142f3449bd3cf18046ad1ae1278c12fc6a538a57b39f713436330825a0d8874` | `c12801d58cb50baf928bb61370b84c02e71807baa0e9fdd03fa21a1faec243a0` |
| 3 | `75705a63222b30845e02e0272cabf3605a752fddfc6fc931e70ee80894349004` | `6fa65bcf876b193b04348aa6553fb498f9498beb9d910e5c1d2a8e6ca56440d5` |

Checks covered **59 source archive files,
599 selected-project artifact content
hashes**, all twelve terminal selected cases, plan/report schemas, final manuscript
hashes, exact approved inputs, unchanged seed/runtime/historical receipts, SQLite
integrity and foreign keys, and unchanged inherited approval/non-production counts.
The existing secret guard checked exports; batch snapshots passed the database
export audit. The single nonblocking Blueprint-integrity observation remained an
advisory naming warning; the approved artifact was not edited.

The local archive retains exact prompts/settings, calls/events, review artifacts,
failed-review captures, draft versions, revision diffs and consistent final SQLite
snapshots. No v33 story failed; the batch-2 and batch-3 partial-evidence exports
are empty, and batch 1 has no failed-story export. Raw evidence is git-ignored;
hashes identify the retained files but
do not make them available in a public checkout or guarantee remote reproduction.

Local detailed evidence:

- [Consolidated analysis and all-case lineage](../../data/diagnostics/v33-cloud-cycle-2026-09-14/analysis.json).
- [Exact recovery pairs and additional semantic evidence](../../data/diagnostics/v33-cloud-cycle-2026-09-14/additional-review-evidence.json).
- Revision diffs: [batch 1](../../data/benchmarks/v0.1/v33-cloud-batch-1-2026-09-14/diagnostics/revision-review.md), [batch 2](../../data/benchmarks/v0.1/v33-cloud-batch-2-2026-09-14/diagnostics/revision-review.md), [batch 3](../../data/benchmarks/v0.1/v33-cloud-batch-3-2026-09-14/diagnostics/revision-review.md).

Completed manuscripts:

- [OH-V01-001](../../data/benchmarks/v0.1/v33-cloud-batch-1-2026-09-14/manuscripts/OH-V01-001.md), 3,232 words.
- [OH-V01-002](../../data/benchmarks/v0.1/v33-cloud-batch-1-2026-09-14/manuscripts/OH-V01-002.md), 3,516 words.
- [OH-V01-003](../../data/benchmarks/v0.1/v33-cloud-batch-1-2026-09-14/manuscripts/OH-V01-003.md), 4,086 words.
- [OH-V01-004](../../data/benchmarks/v0.1/v33-cloud-batch-1-2026-09-14/manuscripts/OH-V01-004.md), 4,510 words.
- [OH-V01-005](../../data/benchmarks/v0.1/v33-cloud-batch-2-2026-09-14/manuscripts/OH-V01-005.md), 3,236 words.
- [OH-V01-006](../../data/benchmarks/v0.1/v33-cloud-batch-2-2026-09-14/manuscripts/OH-V01-006.md), 4,641 words.
- [OH-V01-007](../../data/benchmarks/v0.1/v33-cloud-batch-2-2026-09-14/manuscripts/OH-V01-007.md), 3,347 words.
- [OH-V01-008](../../data/benchmarks/v0.1/v33-cloud-batch-2-2026-09-14/manuscripts/OH-V01-008.md), 4,111 words.
- [OH-V01-009](../../data/benchmarks/v0.1/v33-cloud-batch-3-2026-09-14/manuscripts/OH-V01-009.md), 4,253 words.
- [OH-V01-010](../../data/benchmarks/v0.1/v33-cloud-batch-3-2026-09-14/manuscripts/OH-V01-010.md), 3,929 words.
- [OH-V01-011](../../data/benchmarks/v0.1/v33-cloud-batch-3-2026-09-14/manuscripts/OH-V01-011.md), 3,752 words.
- [OH-V01-012](../../data/benchmarks/v0.1/v33-cloud-batch-3-2026-09-14/manuscripts/OH-V01-012.md), 3,979 words.

No application code changed during execution or reporting. Verification was scoped
to live canary evidence and documentation; the application test/build suite was not
rerun for this documentation-only work.

## What this supports next

The frozen corpus now has a full completion result, and the evidence supports
concrete discussion of reviewer accuracy alongside continued human story reading.
The remaining priorities are to adjudicate the saved POV/requirement examples,
assess whether repair explanations track actual changes, address the recurring
time-coverage evidence error, exercise bounded adjudication with appropriate
focused evidence, and establish repeatability and
human quality/preference/cost acceptance before closing Step 19. None requires
assuming that more retries, larger limits or longer prompts are the answer.

The separate manual samples remain **10/10 under v29 on September 12** and
**12/12 across v29–v33 on September 13**. They use different premises and include
Blueprint generation; they are not pooled into one unchanged-contract canary
rate. Human literary grades and the user's reading observations are still pending.
No tuning or further experiment is launched by this report.
