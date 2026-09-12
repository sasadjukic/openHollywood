# v29 Cloud canary — consolidated diagnostics, 2026-09-12

## Result and interpretation

All three batches finished, covering **12/12 distinct frozen Cloud corpus cases**.
**9/12 stories completed (75.0%)**;
**3 failed**. The graph accepted
**54/64 planned scenes**, including partial
progress from failed stories. **268 production calls** comprised
**261 successes and 7 failures**.
There were **13 prose revisions across 12 scenes**.

The workflow demonstrates useful autonomous completion and bounded recovery,
but this sample does not establish dependable completion across the corpus.
The material weaknesses are structured output at review boundaries and
consistency of POV and continuity judgments. Literary quality remains ungraded.

| Batch / cases | Completed | Accepted scenes | Calls / failed | Prose revisions | Runner time |
| --- | --- | --- | --- | --- | --- |
| 1 / 001–004 | 4/4 | 21/21 | 99 / 0 | 5 | 8m 13s |
| 2 / 005–008 | 2/4 | 16/21 | 88 / 4 | 5 | 7m 34s |
| 3 / 009–012 | 3/4 | 17/22 | 81 / 3 | 3 | 7m 32s |

This is the final diagnostic report for this three-batch production cycle.
The experiment is complete; Step 19 remains **IN PROGRESS**. No v30 prompt,
runtime tuning, manual terminal retry, Hybrid run or later phase was introduced.

## Frozen execution and approvals

Production used **prompt v29 / graph v7**, with inherited Blueprint prompt v9 /
graph v4. Requested model: **gemma4:31b-cloud**; provider-reported model:
**gemma4:31b**. All substantive roles used the frozen Cloud profile.

Runtime commit: `ad48a75891c380ea7ced720a72df187509d0a87e` on main. Runtime
hashes matched across preflights and after execution; existing documentation
changes were preserved. Ollama **0.34.0** served the signed-in Cloud route through
`http://127.0.0.1:11434`. Model alias digest:
`c382fbfbc73b6fdd08c8549c23caedc6e62eb09933c65a1fb82dbf3398320a4e`. Historical references used
Ollama 0.33.3. Remote weights and provider seed enforcement were not independently
pinned.

Seeds were **19001–19012**, one distinct story per case, not repeated trials.
Each batch used a fresh isolated copy of the read-only approved seed, migrated
from schema 0006 to 0007. No prior production checkpoint was resumed. All 12
exact Blueprint approval/version/hash relationships were verified. There were
**zero new Blueprint calls, human decisions or manual run-control commands**.

- Seed SHA-256: `400379c746487cecc0f26dca055c4f51ded5674407b16a0a7d42b7cc9071ab3f`.
- Profile SHA-256: `5feda6671bdb89f311cc171cf0917e7f6227596a2a42a9c4916778211a783c70`.
- Plan content SHA-256: `4907873004add461dffa7c23da43d8f4da59f91d0bbe3f2c6f969997499b233f`.
- Scope: `v29-cloud-cycle-2026-09-12`.

The original 48-case plan envelope and campaign ID preserve seed lineage;
explicit selections and separate directories define this Cloud-only cycle.
It is not a sealed all-profile campaign. Historical comparison invariants and
source reports were preserved. The consolidated local analysis includes all
case, production-run, Blueprint-run, approval and version IDs and content hashes.

Execution was sequential: **$5 per-story application ceiling**, $20 per batch /
$60 summed ceilings; **24,000 input / 8,000 output tokens per call**, $0.20
per-call ceiling, two prose revision cycles per scene, 7,200 seconds per story
and 600-second HTTP timeout. Call limits were 12 times planned scenes: 252, 252
and 264 per batch. These are configured ceilings, not measured bills.

## Story outcomes

| Cloud case | Outcome | Scenes | Calls / failed | Prose revisions | Input / output tokens | Completed words |
| --- | --- | --- | --- | --- | --- | --- |
| 001 | succeeded | 5/5 | 23 / 0 | 1 | 231,040 / 18,463 | 3,165 |
| 002 | succeeded | 5/5 | 20 / 0 | 0 | 192,478 / 15,768 | 3,765 |
| 003 | succeeded | 6/6 | 30 / 0 | 2 | 306,740 / 23,483 | 3,893 |
| 004 | succeeded | 5/5 | 26 / 0 | 2 | 296,045 / 23,897 | 4,454 |
| 005 | failed | 1/4 | 12 / 3 | 1 | 130,309 / 12,552 | — |
| 006 | succeeded | 5/5 | 23 / 0 | 1 | 257,256 / 21,780 | 4,487 |
| 007 | failed | 4/6 | 28 / 0 | 3 | 261,795 / 20,215 | — |
| 008 | succeeded | 6/6 | 25 / 1 | 0 | 251,798 / 19,106 | 3,583 |
| 009 | failed | 1/6 | 7 / 2 | 0 | 54,869 / 4,926 | — |
| 010 | succeeded | 5/5 | 21 / 1 | 0 | 221,738 / 18,689 | 3,915 |
| 011 | succeeded | 5/5 | 29 / 0 | 3 | 292,675 / 23,430 | 3,470 |
| 012 | succeeded | 6/6 | 24 / 0 | 0 | 270,370 / 21,801 | 3,902 |

These are **fresh production calls only**. Inherited Blueprint/direct-baseline
records are excluded. Failed-call repair attempts and prose revisions are
different measures.

- **7 completed stories** had no failed
  call, though some needed prose revisions.
- **2 completed stories** recovered failed
  calls automatically.
- **2 completed stories** had
  neither failed calls nor prose revisions.
- **5 calls** were automatic retry invocations.
  No terminal failure was restarted or replaced. Of the five retry calls,
  three succeeded and two failed; case 005 recovered one earlier error before
  its later terminal failure.
- All accepted versions have passing critiques and zero blocking continuity
  findings. Across all persisted critiques, **61/69 passed**.
  Continuity persisted **8 blocking findings** across all reviews.

Invocation success means the response passed the application boundary; it
does not certify correct criticism, necessary revision or successful semantic
repair. Story completion is separate from human literary quality.

## What went well

1. Autonomous production completed multiple frozen stories without another
   human checkpoint. Batch 1 completed all four with zero failed calls.
2. Validation rejected malformed or inconsistent structured responses, and
   bounded repair recovered some failures. The graph stopped rather than
   accepting unresolved hard blockers or revising indefinitely.
3. Exact lineage, prompts, invocation diagnostics, drafts, reviews and accepted
   references remain available. Failed stories retain partial artifacts.
4. Several edits were localized: the floor reference in 003/2 and the isolation
   repair in 004/4 preserved most surrounding prose. Diffs support locality;
   contextual review is still required to establish necessity and correctness.

## Failed calls and terminal outcomes

| Case | Role | Variant | Retry index | Failure layer | Validation reason | Same-task recovery |
| --- | --- | --- | --- | --- | --- | --- |
| 005 | continuity_supervisor | initial_check | 0 | application_materialization | Partial coverage lacks exact draft evidence | recovered |
| 005 | continuity_supervisor | recheck | 0 | application_materialization | Non-world contradiction lacks one typed claim with provenance | not recovered |
| 005 | continuity_supervisor | recheck | 1 | response_decoding | JSONDecodeError: Extra data: line 92 column 1 (char 4118) | not recovered |
| 008 | scene_critic | canonical | 0 | application_materialization | POV allegation targets assigned character's own interiority | recovered |
| 009 | scene_critic | canonical | 0 | application_materialization | POV allegation targets assigned character's own interiority | not recovered |
| 009 | scene_critic | canonical | 1 | application_materialization | POV allegation targets assigned character's own interiority | not recovered |
| 010 | scene_writer | canonical | 0 | response_decoding | JSONDecodeError: Invalid \escape: line 6 column 3335 (char 3428) | recovered |

Recovery requires a later successful call with the **same task fingerprint in
the same workflow**. Retry index 0 is the original attempt; 1 is its repair.

- **OH-V01-005**: `workflow_execution_failed`. production specialist returned invalid structured output
- **OH-V01-007**: `critique_revision_limit_reached`. critique_revision_limit_reached: hard critique issues remain after revision 2; scene_id=scene_5; blocking_issue_count=1
- **OH-V01-009**: `workflow_execution_failed`. production specialist returned invalid structured output

The harness uses `agentic_production_failed` for failed cases. Runtime
messages distinguish the causes. A continuity current-node label can include
the combined review gate: case 007 stopped on a hard critic blocker, with no
blocking continuity finding at that final gate.

Case 005 recovered its initial continuity evidence-reference error. After one
POV prose revision, the second critique still requested revision. Continuity
recheck then failed typed claim provenance; its repair failed JSON decoding.
The run stopped before another prose revision, not at the prose revision limit.

Case 007 exhausted two scene-5 revisions even though all its calls succeeded.
All three critiques scored 5.0 overall while issuing hard POV blockers;
numeric craft scores did not override the hard gate.

Case 009's critic twice violated the assigned-character interiority rule.
The same validation class occurred and recovered in case 008. This is a
recurring boundary failure in this sample, not a provider connection failure. All seven failed calls are structured-output
failures: five application-materialization failures and two response-decoding
failures. No transport failure is recorded in this cycle.

## Revision preservation and judgment consistency

| Case / scene | Revision pass | Trigger | Character similarity |
| --- | --- | --- | --- |
| 001/5 | 1 | continuity | 80.67% |
| 003/2 | 1 | continuity | 99.37% |
| 003/4 | 1 | continuity | 94.27% |
| 004/2 | 1 | continuity | 97.95% |
| 004/4 | 1 | continuity | 97.65% |
| 005/2 | 1 | critic | 88.83% |
| 006/5 | 1 | continuity | 97.67% |
| 007/2 | 1 | continuity | 99.73% |
| 007/5 | 1 | critic | 98.47% |
| 007/5 | 2 | critic | 99.60% |
| 011/3 | 1 | critic | 99.67% |
| 011/4 | 1 | critic | 98.11% |
| 011/5 | 1 | critic + continuity | 89.43% |

Similarity is character-level Python SequenceMatcher, autojunk disabled, not a
literary quality score. Full diffs and exact old/new version IDs, hashes and
prior reviews are preserved. Revision triggers:
continuity: 7, critic: 5, critic+continuity: 1.

These observations are **review hypotheses, not human adjudications**:

- **003/4:** the writer retained the Archive-entry sentence challenged under
  the confession rule and added advisory escape effort. Continuity cleared
  it. Determine whether the allegation was wrong or recheck missed the issue.
- **004/2:** an unlatched window and a bolted door are distinct objects that
  can coexist. The writer added closure and a night cue; necessity is unproven.
- **005/2:** several Elias internal-state assertions became Sarah's
  observations, but further Elias-centered judgment remained and was blocked.
  An advisory morning cue was also added.
- **006/5:** a tactile object between an embracing pair moved into a cardigan
  pocket and was described as distant. Review whether this satisfies the
  sensory rule during the same embrace despite automatic clearance.
- **007/5:** the initial passage already used “He seemed to be fighting an
  internal battle.” Revisions added “as if”, then “It looked as if”, matching
  forms suggested by the critic. It still blocked unauthorized private state.
  Observable shoulder tension and breathing preceded the inference.
  This is a strong candidate for inconsistent inference handling and advice.
- **007/2:** continuity treated afternoon following morning as contradictory.
  Review the exact sequencing/time requirements before assuming that a
  forward time transition must be repaired.

### Additional batch 3 observations

- **009/2 — repeated assigned-character validation failure.** The initial
  critic call and its one structured repair both treated the assigned
  character's interiority as unauthorized. Unlike 008's recovery, this stopped
  the story. Exact invocations and error messages are retained in the failure
  table and consolidated analysis.
- **010 — writer recovery without prose revision.** One writer response failed
  JSON decoding on an invalid escape. Its structured repair succeeded, and
  the story completed without a review-driven prose revision.
- **011/3 and 011/4 — localized POV repairs that passed.** Scene 3 changed a
  shared internal-state assertion into an explicit Clara perception. Scene 4
  replaced an asserted expectation with visible tension and "as if" wording,
  and rewrote a breath metaphor as observable movement. The re-critiques
  passed. These examples contrast with 007's persistent rejection of similarly
  framed inference; context still matters.
- **011/5 — two feedback sources, larger repair.** The critic requested a Clara
  inference marker. Continuity separately flagged a brass compass as the
  chosen object against retained armchair canon. The writer added the marker
  and replaced the compass passages with loading the armchair into the car.
  The prior story bible records agreement to keep the armchair; the revised
  scene cleared both reviews. This edit is broader than a POV qualifier, but
  has a separate continuity rationale. Physical plausibility and literary
  effect remain human-review questions.
- **012 — clean execution in this sample.** All 24 calls succeeded; six scenes
  were accepted with no prose revisions. This is a completion/validation result,
  not a scored ensemble-quality judgment.


Advisory suggestions and accepted rechecks are not human endorsement. Preserve
v29 evidence and adjudicate these examples before deciding on tuning.

## Usage, timing and cost

**2,767,113 input + 224,110 output =
2,991,223 production tokens**.

| Role | Calls | Failed | Input tokens | Output tokens | Latency total / median |
| --- | --- | --- | --- | --- | --- |
| continuity_supervisor | 71 | 3 | 705,398 | 62,314 | 321.960s / 3.666s |
| scene_critic | 72 | 3 | 1,109,895 | 37,487 | 245.724s / 2.846s |
| scene_writer | 71 | 1 | 560,610 | 71,365 | 472.199s / 6.200s |
| story_bible_maintainer | 54 | 0 | 391,210 | 52,944 | 260.320s / 4.120s |

| Batch | Start UTC | Finish UTC | Runner seconds | Invocation seconds |
| --- | --- | --- | --- | --- |
| 1 | 2026-09-12T16:34:08.080789+00:00 | 2026-09-12T16:42:20.803167+00:00 | 492.722 | 466.596 |
| 2 | 2026-09-12T16:53:07.673966+00:00 | 2026-09-12T17:00:41.562281+00:00 | 453.888 | 428.141 |
| 3 | 2026-09-12T17:05:01.904506+00:00 | 2026-09-12T17:12:34.289204+00:00 | 452.385 | 405.466 |

Summed runner time: **1398.995 seconds
(23m 19s)**, excluding gaps between batches.
Invocation latency sums to **1300.203 seconds**; it differs from
runner time. UTC timestamps are explicit; Europe/Belgrade was UTC+02:00.
No matched Local speedup ratio was established.

Recorded estimated cost totals **USD 0.00**.
Zero-priced app records do not prove free Cloud inference or allocate a
subscription bill. The $5 experimental ceiling does not establish the normal
product $2 target. Budget acceptance remains open. Failed-run records may lack
completed_at; runner receipts and updated_at retain terminal timing context.

## Historical and manual context

| Contract, Cloud 001–004 only | Completed | Scenes | Calls / failed | Revisions | Input / output tokens |
| --- | --- | --- | --- | --- | --- |
| v23 | 4/4 | 21/21 | 92 / 2 | 2 | 856,556 / 77,571 |
| v25 | 4/4 | 21/21 | 90 / 3 | 1 | 779,662 / 73,334 |
| v26 | 3/4 | 16/21 | 84 / 10 | 3 | 757,120 / 68,068 |
| v29 | 4/4 | 21/21 | 99 / 0 | 5 | 1,026,303 / 81,611 |

Only **Cloud 001–004** have the validated completed v23/v25 matched subset used
here. The batch 1 audit checked case/profile/seed, corpus and exact approved
Blueprint equality. v29 retained the four v23/v25 successes and completed
v26's failed Cloud 002. Compared with v25, calls rose **10%** and input tokens
**31.6%**, while failed calls fell from 3 to 0. That is not evidence of better
literature or lower cost. Do not compare a twelve-case v29 rate with a selected
four-case historical rate as if the denominators matched.

The separate [morning manual sample](manual-v29-cloud-production-2026-09-12.md)
completed 10/10 stories and 59/59 scenes, with six recovered failed calls in
265 production calls. It used different premises and fresh Blueprint generation.
It is not pooled with this production-only frozen canary.

## Evidence and manuscripts

Source directories:
`data/benchmarks/v0.1/v29-cloud-batch-{1,2,3}-2026-09-12/`.
Consolidated analysis and reading index:
`data/diagnostics/v29-cloud-cycle-2026-09-12/`.

| Batch | Report SHA-256 | Evidence manifest SHA-256 |
| --- | --- | --- |
| 1 | `e9c23a186af8111d028b9a9fe0ca6374c6b6589dddfc0701c3e35249808efa61` | `18e3bb697ca57ad9665271bfafe0311ca27d8241259ba94a215e034ed8b1c03f` |
| 2 | `895854939ffc74e40194a9dd1a035dfb0c9799b35e731d9531b6fe4274755417` | `5ba974d0c9b040e8f6409a3a5644d845d20b8d33ecc1c397518a22ce3de7831b` |
| 3 | `73b92ca36cd3287f18e358caf06d50cde874eba982d06cfab1a49d787673e5ea` | `368ede2527536e586567b8714dbf75791fb565e87251122c49203f661026f95e` |

Checks covered **52 source archive
files**, **561 artifact content
hashes**, SQLite integrity/foreign keys, 12 terminal selected outcomes,
plan/report schemas, unchanged runtime/seed, approval lineage, manuscript/report
hashes, no new approvals or non-production calls, and clean accepted-scene
review gates. The existing secret guard checked diagnostic exports.
No application code changed.

Completed manuscripts (local-only links):

- [OH-V01-001 — Benchmark Story OH-V01-001](../../data/benchmarks/v0.1/v29-cloud-batch-1-2026-09-12/manuscripts/OH-V01-001.md), 3,165 words.
- [OH-V01-002 — Benchmark Story OH-V01-002](../../data/benchmarks/v0.1/v29-cloud-batch-1-2026-09-12/manuscripts/OH-V01-002.md), 3,765 words.
- [OH-V01-003 — Benchmark Story OH-V01-003](../../data/benchmarks/v0.1/v29-cloud-batch-1-2026-09-12/manuscripts/OH-V01-003.md), 3,893 words.
- [OH-V01-004 — Benchmark Story OH-V01-004](../../data/benchmarks/v0.1/v29-cloud-batch-1-2026-09-12/manuscripts/OH-V01-004.md), 4,454 words.
- [OH-V01-006 — Benchmark Story OH-V01-006](../../data/benchmarks/v0.1/v29-cloud-batch-2-2026-09-12/manuscripts/OH-V01-006.md), 4,487 words.
- [OH-V01-008 — Benchmark Story OH-V01-008](../../data/benchmarks/v0.1/v29-cloud-batch-2-2026-09-12/manuscripts/OH-V01-008.md), 3,583 words.
- [OH-V01-010 — Benchmark Story OH-V01-010](../../data/benchmarks/v0.1/v29-cloud-batch-3-2026-09-12/manuscripts/OH-V01-010.md), 3,915 words.
- [OH-V01-011 — Benchmark Story OH-V01-011](../../data/benchmarks/v0.1/v29-cloud-batch-3-2026-09-12/manuscripts/OH-V01-011.md), 3,470 words.
- [OH-V01-012 — Benchmark Story OH-V01-012](../../data/benchmarks/v0.1/v29-cloud-batch-3-2026-09-12/manuscripts/OH-V01-012.md), 3,902 words.

Failed cases retain partial drafts in their batch
`diagnostics/partial-story-evidence.json` and final database snapshots.
They are not completed manuscripts. Raw databases, prompts and prose are
git-ignored and absent from public checkouts. Hashes identify preserved evidence
rather than provide independent reproduction. The consolidated manifest also
pins this report and its analysis/reading index.

## Recommended next evaluation

1. Human-adjudicate the saved failed POV cases and questionable rechecks.
   Separate label correctness, advice, actual prose changes and recheck accuracy.
2. Reproduce the assigned-character interiority failures and case 007 inference
   loop from frozen inputs as focused regression evidence. Keep validation
   active rather than weakening it to improve completion.
3. If tuning is approved, use a separately named contract/cycle, rerun affected
   cases, then cover the full corpus. Preserve the original v29 failures.
4. Complete blind human rubric/hard-gate scores, matched direct-model preference,
   actual cost acceptance and repeatability before closing Step 19.

No tuning or follow-up experiment is launched by this report.
