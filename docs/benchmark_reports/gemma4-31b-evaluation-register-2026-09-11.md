# gemma4:31b creative-writing evaluation register

As of **2026-09-11**. This register consolidates completed Open Hollywood tests;
it does not announce a new run or certify production readiness.

## Subsequent production evidence — 2026-09-12

The [September 12 manual v29 Cloud report](manual-v29-cloud-production-2026-09-12.md)
adds **10/10 fresh premise-to-production completions and 59/59 accepted scenes**.
SQLite reconciles all 326 operator-reported Cloud calls: 61 Blueprint plus 265
production, with six failed attempts recovered automatically and no recorded
manual retry or revision command. Eight scenes received one prose revision each.
Human literary grading remains absent.

This retrospective manual sample is separate from the frozen canary corpus.
It updates the evidence available after this register's September 11 snapshot;
the historical tables and then-current conclusions below remain dated records.
Three four-story v29 canary batches and Step 19 acceptance remain pending.

## Subsequent v29 canary batch 1 — 2026-09-12

The [first v29 Cloud canary batch](step-19-cloud-v29-batch-1-2026-09-12.md)
completed Cloud OH-V01-001 through OH-V01-004: **4/4 stories, 21/21 scenes,
99/99 succeeded production calls, zero failed attempts**. Five continuity-driven
prose revisions completed, with two semantic/recheck questions retained for human
review. It matches the four v23/v25 Cloud successes and restores v26 Cloud 002's
completion, with higher usage than v25. This is a named Cloud subset comparison;
historical campaign invariants and evidence are unchanged.

At batch 1 close, batches 2 and 3 remained outstanding. Human quality, direct-model preference,
budget acceptance and repeatability are still pending; Step 19 is IN PROGRESS.

## Subsequent v29 canary batch 2 — 2026-09-12

Cloud OH-V01-005–008 finished with **2/4 stories completed, 16/21 scenes,
88 production calls (84 succeeded, 4 failed) and five prose revisions**, in
453.888 seconds. Cases 006 and 008 completed; 005 stopped on continuity
structured-output repair exhaustion, and 007 stopped on hard-critic revision
exhaustion. The repeated POV finding in 007 needs semantic review. The original
failures were preserved without manual retries or contract tuning.

The local evidence archive is
data/benchmarks/v0.1/v29-cloud-batch-2-2026-09-12/; its execution receipt,
diagnostics, partial drafts, successful manuscripts and final SQLite snapshot
are available for consolidation. At batch 2 close, 8/12 cases had been
attempted and 6 completed. Batch 3 and Step 19 acceptance remained pending;
consolidation was deferred until all three batches finished.

## Completed v29 Cloud canary cycle — 2026-09-12

The [consolidated three-batch report](step-19-cloud-v29-consolidated-2026-09-12.md)
covers all 12 frozen Cloud cases: **9 completed, 3 failed; 54/64 scenes;
268 calls (261 succeeded, 7 failed); 13 prose revisions across 12 scenes**.
Batch 3 completed 010–012; 009 stopped on repeated critic validation failure.
The other failures were 005 (continuity structured repair) and 007 (hard-critic
POV revision limit). Case 007's inference handling and several continuity
rechecks require human adjudication. Seven completed stories had no failed
calls; two completed after automatic recovery.

Recorded production usage totals 2,991,223 tokens, with 1,398.995 seconds of
summed runner time. Three intact archives, nine manuscripts and unsuccessful
partial drafts support the report. Runtime, seed and approvals remained frozen;
no terminal rerun or tuning replaced these outcomes. The manual ten-story
sample remains separate. Step 19 is IN PROGRESS pending quality/preference,
semantic adjudication, cost acceptance and repeatability.

## Reading the scores

The tested Cloud identifier was `gemma4:31b-cloud`; the provider reported
`gemma4:31b`. “Local-002/003/005” below names the historical source draft, not
the inference placement of the 31B evaluation.

Keep four measures separate: accepted structured response, correct judgment,
correct minimal repair recommendation, and successful executed repair.
Production completion and human story quality are separate again. Ratios below
are exact counts from the cited runs, not estimates of general model reliability.

Most comparisons use three requested seeds (19105, 29105, 39105), temperature
0.2, top-p 0.95, thinking disabled, context allowance 28,000 and output allowance
8,000. The 24 novel POV controls have one sample each; the actual c05 writer
uses the existing writer temperature 0.85. Labels and clean counterparts were
withheld from model inputs. Remote weights and seed enforcement are not
independently pinned. Repeated variants of one scene are not independent stories.

The [September 11 decision](model-testing-direction-2026-09-11.md) now prioritizes
Cloud production evaluation. Earlier microtest recommendations to hold all
advancement are historical: the outstanding details are deferred, not silently
fixed, and runtime correctness gates remain intact.

## Production evidence, separate from critic tests

The same saved model profiles route Local substantive roles to E4B and Cloud
roles to 31B. The canaries reuse approved Blueprints rather than retesting
pre-production on every iteration.

| Production contract | Graph | 31B Cloud completions | E4B Local completions |
| --- | ---: | ---: | ---: |
| v23 | 3 | 4/4 | 2/5 |
| v24 | 4 | 4/4 | 0/5 |
| v25 | 5 | 4/4 | 2/5 |
| v26 | 6 | 3/4 | 0/5 |

Only the exact inherited Local OH-V01-006 Blueprint failure is excluded from the
Local production denominator. Thus the latest two completed canaries provide
**4/4 under v25 and 3/4 under v26**, not two perfect Cloud runs. v26 completed
Cloud OH-V01-001/003/004; Cloud 002 failed the critic's exact-evidence contract.
v25's four Cloud completions included recovery from three structurally invalid
production attempts. Completion after recovery is not a first-pass-perfect run.

These are genuine end-to-end production results, but do not establish literary
quality: final blind human evaluations remained absent. v23's affected Local
clock pause was an environmental dual-boot issue. v27/v28/v29 specialist probes
and critic tests below are **not later full canaries**.

Public run diagnostics: [v23](step-19-local-cloud-v23-canary-2026-09-04.md),
[v24](step-19-local-cloud-v24-canary-2026-09-05.md),
[v25](step-19-local-cloud-v25-canary-2026-09-07.md),
[v26](step-19-local-cloud-v26-canary-2026-09-08.md).

## Completed diagnostic ledger

“Valid” includes the existing single-JSON-fence normalization where applicable.
It does not mean perfect adherence to every textual instruction.

| ID | Date | Test / 31B calls | Valid responses | Exact measured result |
| --- | --- | --- | ---: | --- |
| T00 | Sep 8 | v27 Cloud-002 saved-input critic / 1 | 1/1 | Returned pass without findings; no comprehensive literary correctness score assigned |
| T01 | Sep 9 | Frozen POV comparison / 18 Cloud calls, alongside 18 E4B calls | 18/18 | Correct coarse and joint-valid POV judgments: 18/18 |
| T02 | Sep 9 | Novel POV controls n01–n24 / 24 | 24/24 | Correct labels: 24/24; 11 true violations, 13 valid controls, zero false positives/negatives |
| T03 | Sep 9 | v28 full-critic transfer / 9 | 6/9 | Raw target POV: 9/9; usable target-correct responses: 6/9 |
| T04 | Sep 9 | v29 full-critic transfer / 9 | 9/9 | Target POV: 9/9; Cora 0044 correctly cited and blocked: 3/3 |
| T05 | Sep 9 | Six expanded full-critic controls c01–c06 / 18 | 18/18 | Target judgments: 15/18; ordinary sentence repetition detected: 0/3 |
| T06 | Sep 9 | c05/c06 catalog versus prose-plus-catalog / 12 | 12/12 | c05 detection: 0/3 versus 3/3; corrected human action-level match: 3/6 versus 6/6 |
| T07 | Sep 11 | c05 writer repair + fresh critics + clean controls / 9 | 9/9 | Exact two-sentence removal: 3/3; repaired-draft clean pass: 3/3; clean control pass: 3/3 |
| T08 | Sep 11 | Five fresh full-critic craft controls r01–r05 / 15 | 15/15 | Core judgments: 12/15; duplicated-word detection: 0/3 |
| T09 | Sep 11 | Full critic versus added proofreading instruction / 18 | 18/18 | Core judgments: 6/9 versus 9/9; duplicate-word detection/minimal advice: 0/3 versus 3/3 |
| T10 | Sep 11 | Eight excerpt controls w01–w08, baseline versus proofreading / 48 | 23/24 versus 24/24 | Valid verdict matches: 23/23 versus 24/24; minimal advice: 9/12 in each arm |
| T11 | Sep 11 | Known + fresh excerpt controls, proofreading v1 versus minimal-repair v2 / 84 | 42/42 in each arm | Verdict matches: 39/42 each; minimal advice: 17/21 versus 15/21 |

T01–T11 account for **264 Cloud calls**, including three writer calls. Do not
pool their semantic scores: tasks, input representations and denominators differ.
T00 is one additional earlier probe within an eight-probe mixed-model suite.
The first c05 repair harness directory aborted before dispatch (**zero model
calls**); it is not a model failure or an extra nine-call test.

## POV and assignment discrimination: T01–T05

T01 held the supplied rules, input payloads and inline schema constant across
the two models; native schema enforcement was disabled for both arms.

| Frozen condition | 31B valid + target-correct | E4B valid + target-correct |
| --- | ---: | ---: |
| Full saved scene/context | 3/3 | 0/3 |
| Focused full scene | 3/3 | 0/3 |
| Original private-feeling sentence | 3/3 | 0/3 |
| Explicitly attributed inference | 3/3 | 0/3 |
| Assigned character's own feeling | 3/3 | 3/3 |
| Explicit private-feeling cue | 3/3 | 1/3 |
| Total | 18/18 | 4/18 |

E4B's separate coarse decision score was 9/18 and structural score 6/18.
Inspecting a readable decision inside a rejected response does not make it a
usable output. In an earlier E4B native-format diagnostic, a schema repair
recovered validation to 6/6 but expected judgments were only 2/6. Its initial
six HTTP 400s were diagnostic schema/grammar failures with no semantic verdict.

T02 extends the POV evidence to first-/third-person interiority, inference,
dialogue, memories/knowledge, free indirect narration and explicit viewpoint
permission. Its 24 labels were proposed before generation and human-approved
afterward. The 24/24 score is label agreement, not proof that every explanation
or proposed rewrite was flawless.

In T03, all three Local-002 responses confused an evidence identifier with a
quotation. The underlying POV judgments were right, but full responses failed.
Two Local-005 responses also returned raw pass despite a typed POV violation;
the existing application gate correctly normalized them to revise.

T04 fixed the observed interface failures: Local-002, Local-003 and Local-005
were each **3/3 valid and target-POV-correct**; raw/normalized verdict mismatches
fell from 2/9 to 0/9. Broader Local-002 outcome criticism and Local-003 mathematical
or literary praise remain **unscored**: the human reviewer withheld a final
judgment for insufficient context. Do not report them as proven critic errors
or fully correct reviews. T04 emitted no ordinary craft issues, so that path
still needed positive controls.

| T05 expanded control | Current target judgment matches | Model prose scores, seed order |
| --- | ---: | --- |
| c01: missing required outcome | 3/3 | 5, 5, 5 |
| c02: achieved outcome; extra dramatization optional | 3/3 | 5, 5, 5 |
| c03: unauthorized location change | 3/3 | 5, 5, 5 |
| c04: explicitly authorized transition, same prose | 3/3 | 5, 5, 5 |
| c05: accidental tripled opening | 0/3 | 5, 5, 5 |
| c06: clean counterpart | 3/3 | 5, 5, 5 |

The c03/c04 contrast shows that the model used the assignment's permission,
rather than treating any location change as wrong. High prose scores on c01/c03
did not prevent a required assignment revision.

## c05 label correction and actual repair: T06–T07

The original human-approved c05 proposal mistakenly specified a minor note plus
**pass**. The human reviewer subsequently clarified that duplicate sentences
must be removed: **revise**, preserving everything else. We retain both the
original record and the dated correction; we do not retroactively rewrite the
predeclared labels.

- T05 originally had 18/18 verdict matches but only 15/18 target judgments.
  Under the corrected c05 action label, verdict matches are 15/18; its three
  missed repetitions remain failures.
- T06 catalog-only input detected c05 in 0/3 trials; continuous prose plus the
  same catalog detected it and recommended targeted removal in 3/3.
- Both T06 presentations passed clean c06 in 3/3. With the corrected human
  expectation, action-level agreement is **3/6 catalog, 6/6 prose-plus-catalog**.
  These are explicitly retrospective scores, excluding numeric-score and
  severity-enum adjudication.
- T06's c05 prose scores were **5,5,5 catalog versus 2,2,2 prose-plus-catalog**.
  The conclusion that requesting revision was itself a mistake is superseded;
  whether 2/5 fairly represents the whole scene remains a separate question.

T07 then used the actual saved findings with the existing v29 writer instruction.
All **3/3** writer responses removed only the two extra sentences, preserved
unaffected prose and paragraph breaks byte-for-byte, and exactly matched clean
c06. All **3/3** fresh re-critiques passed without findings; all **3/3** clean
controls also passed. Fresh prose scores were **5,5,5** in both groups, with
dramatic progress and character consistency also 5 throughout.

This is positive evidence of a genuinely executed surgical sentence repair—not
merely a recommendation. It does not certify all word-level edits or all
production loops. Continuity, Bible updates and the durable graph were not run.

## Fresh craft and proofreading tests: T08–T09

| T08 case | Required disposition | Core match | Prose scores | Dramatic scores | Character scores |
| --- | --- | ---: | --- | --- | --- |
| r01 clean scene | Pass | 3/3 | 5,5,5 | 5,5,5 | 5,5,5 |
| r02 tripled sentence inside paragraph | Local revision | 3/3 | 2,2,2 | 5,5,5 | 5,5,5 |
| r03 “She checked the the delivery number again.” | Delete one “the” | 0/3 | 5,5,5 | 5,5,5 | 5,5,5 |
| r04 intentional “No. No. No.” | Pass | 3/3 | 5,5,5 | 5,5,5 | 5,5,5 |
| r05 widespread circular/tautological prose | Broader craft revision | 3/3 | 1,1,1 | 2,2,2 | 2,2,2 |

r02 received a localized deletion recommendation, not a request to rewrite the
scene. r05 received broader revision advice supported by actual pervasive
defects, while the critic acknowledged that the planned events were present.
It does not show that ordinary Open Hollywood stories are padded, or that
shorter prose is always better.

T09 reran r01/r03/r04 with unchanged full input context. Adding a general
proofreading paragraph recovered r03 detection, exact evidence and one-word
advice from **0/3 to 3/3**. Both arms preserved the six clean/intentional control
responses (**6/6**). Core judgment agreement was **6/9 reference, 9/9 focused**.

For r03, the reference scored every dimension 5 in all trials; the focused arm
scored prose **4,4,4**, dramatic progress **5,5,5**, character consistency
**5,5,5**, and requested revision with a minor issue. A small correction was
mandatory without condemning the whole scene. No actual r03 writer edit ran.

## Word-level generalization: T10

This is a newly defined short-excerpt critic, **not the unchanged full v29
critic**. One arm adds the preceding generic proofreading paragraph.

| Case | Intended treatment | Minimal advice: baseline / proofreading | Prose: baseline / proofreading |
| --- | --- | --- | --- |
| w01 valid “had had” | Pass | Not applicable | 5,5,5 / 5,5,5 |
| w02 “had had had” | Delete one, retain past perfect | 3/3 / 1/3 | 2,2,2 / 2,3,2 |
| w03 valid “that that” | Pass | Not applicable | 5,5,5 / 5,5,5 |
| w04 “that that that” | Delete one, retain valid double | 0/3 / 2/3 | 2,2,2 / 3,3,2 |
| w05 intentional interrupted speech | Pass | Not applicable | 5,5,5 / 5,5,5 |
| w06 accidental “and and” beside that speech | Delete one “and” | 3/3 / 3/3 | 3,3,3 / 3,3,3 |
| w07 purposeful cross-paragraph “tomorrow” | Pass | Not applicable | 5,5,invalid / 5,5,5 |
| w08 accidental “her her” before “ticket” | Delete one “her” | 3/3 / 3/3 | 4,4,4 / 4,4,4 |

Both arms detected and exactly cited all **12/12** defective presentations.
Neither invented issues on its valid clean controls (**0/11 reference,
0/12 focused**). Unambiguous minimal advice was **9/12 in each arm**:
better w04 handling was offset by tense-changing alternatives on w02.
All valid dramatic/character scores were 5.

The reference's seed-39105 w07 response contained stray unquoted `uma`, causing
JSON parsing to fail. Its visible pass is **not** counted as a valid success.
No repair or retry was performed. One event does not prove a general JSON
reliability difference. The known w05 context explicitly permitted interrupted
speech; the later fresh stammer control omitted that explanatory hint.

## Fresh controls against frozen minimal-repair v2: T11

The candidate adds explicit instructions to make one smallest necessary
correction, preserve grammatical repetition and state the deletion count and
resulting wording. It was frozen before f01–f06 were authored and human-approved.
Both arms received new calls; historical reference outputs were not reused.

| Measure | Proofreading v1 | Minimal-repair v2 |
| --- | ---: | ---: |
| Valid outputs | 42/42 | 42/42 |
| Known verdict matches | 24/24 | 24/24 |
| Fresh verdict matches | 15/18 | 15/18 |
| Known minimal repair recommendations | 8/12 | 9/12 |
| Fresh minimal repair recommendations | 9/9 | 6/9 |
| All minimal repair recommendations | 17/21 | 15/21 |
| Unwanted required revisions on clean controls | 3/21 | 3/21 |
| Combined valid verdict + repair/preservation gate | 35/42 | 33/42 |

The combined gate excludes numeric craft-score calibration; it is not a
production success rate. Both arms detected and exactly cited all true defects:
21 defective responses, containing 24 defect presentations per arm because
f06 has two separate errors.

| T11 defective case | Minimal advice: v1 / v2 | Main result |
| --- | --- | --- |
| w02 | 0/3 / 3/3 | Candidate removes the tense-changing alternative |
| w04 | 2/3 / 0/3 | Candidate contradicts count twice and overdeletes once |
| w06 | 3/3 / 3/3 | Correct one-“and” advice |
| w08 | 3/3 / 3/3 | Correct one-“her” advice in this sentence |
| f02 | 3/3 / 0/3 | Candidate's explicit count contradicts its corrected sentence |
| f04 | 3/3 / 3/3 | Correct “for for” repair; “You—you” preserved |
| f06 | 3/3 / 3/3 | Both defects addressed; candidate correctly deletes two “the” and one “on” |

Fresh clean f03 and f05 pass **3/3 in each arm**. Valid f01 fails **3/3 in each
arm**: “He passed her her mittens.” has a recipient and a possessive determiner.
The reference makes two grammar accusations and one required style rephrase;
the candidate makes three grammar accusations.

For f02's “He passed her her her mittens.”, the candidate says remove **two**
but prints “He passed her her mittens.” in all three samples. The quoted result
requires **one** deletion. The reference's unnumbered plural “instances” is
imprecise, but its single correct resulting sentence resolves the instruction;
an explicit conflicting numeric count does not.

For w04, the candidate's third sample consistently deletes two “that” words.
The result can be grammatical, but it is not the smallest correction: one
deletion preserves the original construction. A count check alone would miss it.

The candidate has **five count/result contradictions**, plus **one consistent
overdeletion**, across its 21 defective responses. Its known-case score of 9/12
is only one above this run's 8/12 reference; that same reference previously
scored 9/12 in T10. The frozen requests match, but remote outputs vary.

Neither arm executed word edits. The fact that correct f02 repair produces the
f01 sentence rejected by both critics suggests a repair/re-review stability
risk; it is not an observed executed loop.

## Interpretation and current priority

31B has demonstrated useful POV/assignment discrimination, detection of substantial
craft defects, and an actual exact-preservation sentence repair. It has also
completed Cloud productions. Its weaknesses include representation-sensitive
review coverage, false required edits on valid language, inconsistent minimal
word-repair specifications, and unresolved score calibration.

We have not demonstrated reliable full-story quality, a perfect reviewer, or
successful full v29 production. There is no basis for claiming that a model
which misses one typo cannot run an agentic story workflow—or that a model
which passes these controls will complete every workflow.

The current next stage is the Cloud-first production assessment described in
the [testing decision](model-testing-direction-2026-09-11.md), not another
automatic proofreading experiment. Preserve these results and the
[deferred follow-up](../issue_drafts/gemma4-31b-critic-repair-follow-up.md).
Do not quietly promote the minimal-repair-v2 paragraph or the prose-plus-catalog
diagnostic input into production.

## Evidence receipts

The source run names below are relative to local `data/diagnostics/`, which is
git-ignored. Raw campaigns and traces are **not included in a public checkout**.
These tables and excerpts are the public summary; hashes identify the source
files without publishing credentials, personal filesystem paths or database
exports. A hash establishes identity, not public access or independent validation.

The following receipts identify the semantic reviews used for T01–T11; T02/T03
share one review. Each review binds its execution report and supporting records.
The c05 correction is listed separately because it supersedes a judgment, not
the original model output.

| Tests | Source directory | Semantic review SHA-256 |
| --- | --- | --- |
| T01 | `viewpoint-frozen-comparison-2026-09-09-1820` | `dc16e0efe24ebc4852c54825411047e77c7d5eb937ccd57ca02f40539364e8a5` |
| T02/T03 | `31b-next-stage-2026-09-09-1837` | `23013a6c4b73683b352dba69a25f4fd60b95007a67d9ffd425d61637ad32e30a` |
| T04 | `critic-transfer-v29-2026-09-09-1952` | `b3923febd62a64c93abe5c4a602da72853f021fe44a8ab17adb6f2c4fa02d206` |
| T05 | `critic-expanded-v29-2026-09-09-2111` | `3d8eb905a009d215dd151873fb4f1fb8b5ec944c09e1593b8a9151ae180f81eb` |
| T06 | `critic-presentation-v29-2026-09-09-2129` | `b5878faf114045839ea74004dd218347c06eb3d126db603d2890957a1f4dddca` |
| T07 | `c05-repair-v29-2026-09-11-0855` | `f0e66e308b114685151d24b3a1bb4093cc92fcd96450215d09b6d6cb34574c41` |
| T08 | `critic-craft-v29-2026-09-11-1222` | `86614254c89648ceeecf639069c218402d3d4644a3235139d1f04a438a3eb597` |
| T09 | `critic-proofreading-v29-2026-09-11-1234` | `799e2d0c6c5d3bf7401fee065e4afa755fe7d68376e6b298578dfab93fdf2c9e` |
| T10 | `word-repetition-ab-2026-09-11-1410` | `a1aba9483d66431c7c015dedd31308f5f58b516480bef1f171238cf98e540901` |
| T11 | `minimal-repair-ab-2026-09-11-1446` | `2f8fc2fb15d17bfa7b3bda0ef9a272dc4cf2fc374889ae48145c05bb356c7bae` |

T06 human correction: `critic-presentation-v29-2026-09-09-2129/c05-adjudication-update-2026-09-09.json`, SHA-256 `0a9b105db0711aabb38c8c4cdb5fcc7b80a824d4592fc92108cd8c999b7c7d82`.

T00 is documented in the [v27 isolated-probe report](step-19-v27-isolated-probes-2026-09-08.md), which includes its report hash. E4B's native-format diagnostic is preserved under `viewpoint-diagnostic-v1-2026-09-08-213008-schema-repair/`; its initial HTTP 400 batch is preserved separately. The [Step 19 tracker](../../open_hollywood_bible/step_by_step_implementation.md) records pre-production staging and public canary report locations.

The E4B native-format `semantic-review.json` SHA-256 is
`865470a8ac4ce5b75950f738da53ed671f298f432139cfdd714350a0bc20d809`.

Historical reports may retain `semantic_review_status: pending` because they are immutable execution snapshots; their separately bound semantic reviews record the subsequent analysis. Prepared controls, offline unit tests and the zero-call setup abort are not counted as live model successes. Except for T07's three sentence repairs, the diagnostic ledger measures reviewers, not executed manuscript corrections. Exact model-emitted craft scores are observations, not human gold scores or proof of story quality.
