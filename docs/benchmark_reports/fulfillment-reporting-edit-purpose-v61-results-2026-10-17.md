# Reporting retry and edit purpose: bounded results

Date: 2026-10-17. **COMPLETE: 46/96 calls; neither frozen success criterion met.**

Expanded critic feedback produced no additional qualified recovery over ordinary
feedback. Edit purposes produced two primary preservation wins, but also unsupported
justifications and a mixed ending rewrite. Both arms repaired the optional craft
control. These are useful diagnostic results, not production qualification.
Production remains at prompt **61**, graph **9**, fulfillment policy **1**.
**Full workflow canary: ON HOLD; NOT STARTED.**

## Approved scope and accounting

The user explicitly approved the [frozen 96-call plan](fulfillment-reporting-edit-purpose-v61-plan-2026-10-17.md),
including full unpublished prose, critique and story context sent to Ollama Cloud
through the local Ollama daemon. Cases, sources, requests, scoring, settings and
validators remained frozen. The plan retains its historical preparation status;
this report records the subsequent approval and execution.

- Plan SHA-256: `ee346c83e38643f9f1438279cde5863067e51896d8da2519fd9788651cc22844`.
- Preparation closure SHA-256:
  `aa50bb7e2e6ad772ae5d4fd1d80d2a7d6b32e3f9d9a39098786ca6061df2f2c6`.
- Model: `gemma4:31b-cloud`. Preflight and both phase checks matched Cloud deployment
  and digest `c382fbfbc73b6fdd08c8549c23caedc6e62eb09933c65a1fb82dbf3398320a4e`.
- Seeds 19601/19603, reversed arm order at the second seed, top-p 0.95,
  thinking disabled; critic temperature 0.2 and both writer temperatures 0.85.

| Stage | Scheduled slots | Executed calls | Valid responses | Skipped slots |
| --- | ---: | ---: | ---: | ---: |
| A: shared P1 initials | 16 | 16 | 13 | 0 |
| A: conditional R0/R1 corrections | 32 | 6 | 4 | 26 |
| B: exact-edit writers | 12 | 12 | 12 | 0 |
| B: ordinary P0 posts | 12 | 12 | 12 | 0 |
| **Total** | **72** | **46** | **41** | **26** |

The 26 skips are exactly the two correction branches for each of 13 valid shared
initials. Three rejected initials and two rejected correction branches account for
the five invalid responses. Every executed slot used one call; B needed no structural
retry. The six A corrections are the frozen conditional branches, not extra rounds.
No semantic reroll, transport retry, source replacement or additional revision occurred.

A used **22/48** calls; B used **24/48**. No budgets were transferred. The remaining
50 calls authorize no additional experiments. Usage was **778,005 input tokens,
45,432 output tokens and 253.56 active seconds**, within every per-attempt, stage,
block and aggregate limit. At the recorded October 8 rates, the estimate is
**USD 0.12709350**; actual billed charges are unknown. Three model identity checks
were discovery calls, separate from the 46 inference calls.

## A: expanded feedback does not add a qualified recovery

P1's continuous prose and ordinary critic instructions were common to every initial.
Only structurally invalid initials branched into R0 ordinary retry feedback and R1
the same feedback plus bounded structural diagnostics. Both branches received the
same rejected parent hash and ordinary failure details. Shared valid initials are
one observation each, not independent successes for both policies.

| Measurement per policy | R0 | R1 |
| --- | ---: | ---: |
| Valid shared initials | 13 / 16 | Same 13 shared |
| Qualified recoveries among failed initials | 2 / 3 | 2 / 3 |
| Final valid, supported native/boundary tuples | 15 / 16 | 15 / 16 |
| Raw supported duplication detection | 4 / 4 | 4 / 4 |
| Valid supported duplication findings | 3 / 4 | 3 / 4 |
| Supported native repair conditions in Elena controls | 4 / 4 | Same 4 shared |
| Unsupported repetition-removal demands on controls | 0 / 8 | 0 / 8 |

R1 achieved **zero paired qualified rescues and zero paired losses** relative to R0.
There were enough failed initials to evaluate the frozen comparison; this is not the
fewer-than-two-failures inconclusive outcome. R1 fails the required two rescues,
complete duplication coverage and complete qualified native/boundary coverage.

| Failed initial | Initial defect | R0 correction | R1 correction |
| --- | --- | --- | --- |
| 19601 duplicate + overrun | Missing boundary reference in independent craft comparison | Valid; retains minor duplication finding | Valid; retains minor duplication finding |
| 19601 functional recurrence + overrun | Linked boundary issue authors its own recommendation instead of null | Valid | Valid |
| 19603 duplicate + overrun | Missing boundary reference in independent craft comparison | Still invalid: comparison reference remains empty | Still invalid: fixes comparison coverage but adds forbidden model-written `boundary` conditions |

The duplication finding survived all eight relevant raw responses: two within-
boundary initials, two combined initials and four combined corrections. Every finding
remained minor, independent and actionable, with accurate citations to both adjacent
copies. No finding was dropped or reclassified to obtain validity. The final rejected
combined reviews therefore remain correct observations in unusable reports.

The two combined initials already exposed comparison groups through ordinary
validation feedback. R1 added a concrete explanation but did not deliver an extra
usable result; at the second seed it moved the failure to condition ownership. No
initial in this run had the earlier model-written-boundary ownership error masking
comparison coverage. The local counterfactual checks covered that pattern, but this
live run does **not** directly establish whether R1 improves recovery from it.

The Elena conditions remained narrow: make the genuinely missing verification
decision, or remove the prohibited definitive match while retaining the decision.
The compound-case next-scene explanations nevertheless overclaimed what a match
alone establishes: acceptance of the warning at one seed, and verification of a
particular flourish at the other. The explicit current no-match constraint independently
supports both boundary judgments; neither extra claim entered the actual repair
condition. Correct core judgments do not certify every sentence of a critic's rationale.

## B: some preservation gains, but purposes do not reliably justify the edits

W0 used unchanged E1 exact edits. W1 added target references and per-edit purposes.
Both received the same frozen historical critique, full context, fulfillment packet
and required repairs. The optional craft source retained its original **pass/minor**
status and received the same explicit diagnostic task in both arms, with no invented
mandatory craft test. A's new responses did not select or gate these sources.

All **12/12 patches validated immediately**. Each arm repaired all four boundary
cases and both optional craft cases, retaining touch, psychic pull and the indirect
decision. The complete body before the ending was unchanged in all twelve revisions.
All **12/12 ordinary post-reviews passed immediately**, with met/met/no-overrun
judgments; all eight existing boundary tests were met. The four craft posts had no
manufactured mandatory test. Full originals, revisions, selected edits and diffs were
inspected, including the changes inside positively cited passages.

The frozen paired judgments compare **W1 relative to W0**:

| Seed / source | Primary | Additions-neutral sensitivity | Full-prose rationale |
| --- | --- | --- | --- |
| 19601 / separate | Win | Win | W1 keeps the conditional first-step sentence that W0 deletes and avoids W0's added hammering heart. Both unnecessarily remove the bracing purpose. |
| 19601 / embedded | Win | Tie | W1 keeps the original bracing sentence and avoids W0's added heartbeat and trembling threshold wording. It still adds a threshold image. With additions neutral and the bracing-purpose omission treated as implicit paraphrase, neither has a clear advantage. |
| 19603 / separate | Mixed | Loss | W1 substitutes “as soon as she let go of the daylight” for the strap contingency and terminal outside state. The emotional framing is a plausible craft gain, but concrete timing/state is lost. Treating that new framing as neutral leaves a preservation loss. |
| 19603 / embedded | Tie | Tie | Both keep the bracing action, first-step contingency and outside state. W0 adds a poised-at-the-dark image; W1 adds remaining-in-place/staring language. Neither clearly preserves more. |
| 19601 / optional craft | Tie | Tie | Both remove one duplicate and produce identical complete prose. |
| 19603 / optional craft | Tie | Tie | Both remove one duplicate. W1 leaves a double intersentence space; the prose otherwise agrees. |

Primary totals: **2 wins, 0 losses, 3 ties, 1 mixed**. Sensitivity: **1 win, 1 loss,
4 ties**. Both primary wins are boundary pairs and one is embedded, satisfying that
part of the frozen requirement. These are operator preservation judgments, not
independent human literary preference. The mixed label follows the frozen rule for
a plausible craft gain coupled with meaningful loss; it does not count as a win.

### What the purposes establish—and what they do not

W1 returned eight purpose claims. Their target references and schema were valid, but
full inspection found **four fully supported, two partly supported and two unsupported**:

- The two separate-entry deletions and two optional duplication repairs have fully
  supported purposes: the actual changes directly remove their supplied defects.
- Both embedded edits correctly identify the forbidden entry, but their rationales
  do not justify the added threshold image or staring/remaining-in-place wording.
  A true claim about the old defect does not justify every part of its replacement.
- Both separate-case adjacent edits claim necessity without establishing a repair-
  caused grammatical or flow defect. At 19601, the claim treats “to carry herself
  through” as a forbidden entry implication even though preparation is compatible
  with remaining outside. At 19603, a desired tonal shift is presented as necessary
  and used to justify a new heartbeat and a different condition for proceeding.

W1 therefore **fails the all-supported-purpose requirement**, even though it meets
the primary paired-win threshold and repairs all six cases. Correct references and
fluent explanations did not prevent unnecessary edit selection. Even classifying
the two embedded purposes generously would leave both adjacent justifications
unsupported. No semantic retries were used to improve these results.

All eight boundary revisions still alter compatible ending material beyond removing
entry. The new wording is not uniformly an explicit decision restatement; it includes
physiological beats, threshold imagery, and changed timing or agency. Preserving
fulfilled facts is distinct from preserving their expression or improving the story.
Potential craft merit remains open rather than being ruled out by edit size.

### The optional craft control succeeds in both arms

All four optional-craft revisions remove exactly one adjacent duplicate while retaining
the bracing action, decision, preparation and unrelated prose. Three exactly restore
the clean reference; the fourth differs only by a doubled space. This is a successful
local craft repair, not evidence that exact restoration is a literary oracle.

Three patches select a range containing both copies, overlapping the first copy's
positive evidence; one deletes only the uncited second copy. The positive wording
survives in every output. These observations show that this control did not freeze
all cited text against editing. They do **not** qualify a task that necessarily changes
fulfilled prose: deleting the uncited copy was always available.

Every post-review awarded **5/5 on all three craft dimensions** and raised no issue.
Those 36 maximum scores do not distinguish the lost preparation, new imagery or
unsupported purposes. The post messages contain the revised catalog and ordinary
context, not the full original plus diff, and receive no purpose records. They support
the inspected factual repairs, not comparative preservation or literary qualification.

## Decisions and story-quality implications

1. Retain J1 and P1 as diagnostic evidence and E1 as mechanically successful but
   preservation-unqualified. Promote none of these components into production.
2. Do not adopt R1 as an improved retry policy: this run adds no qualified recovery
   and leaves a combined case invalid under both policies. Retain the error transition
   and the untested masked-error limitation for future diagnosis.
3. Record W1's two primary preservation wins and successful craft repairs as limited
   diagnostic evidence, alongside its unsupported purposes and sensitivity result.
   Do not treat an editorial explanation as proof of necessity or a production gate.
4. Keep factual repair, preservation and artistic improvement separate. The optional
   craft success is encouraging, while the mixed ending illustrates why a universal
   smallest-edit rule would be an inadequate story-quality policy.
5. Preserve all six anonymous full-prose pairs for human review. The review sheet is
   empty and preference remains **PENDING**. Later qualification still needs the
   accepted weighted rubric and hard gates, the full intended Cloud corpus and a
   comparable single-model baseline. Two seeds and this narrow source family do not
   establish broad quality or model reliability.

No next experiment, prompt change or workflow canary is started by this results task.
**Step 19 IN PROGRESS; Step 20 NOT STARTED.**

## Evidence and verification

Private preparation: `data/diagnostics/fulfillment-reporting-edit-purpose-v61-2026-10-17/`.
Private results: `data/diagnostics/fulfillment-reporting-edit-purpose-v61-2026-10-17-live/`.

The live bundle preserves explicit approval, all 46 exact requests, durable reservations,
raw responses, receipts and outcomes; 46 executed slot summaries; 26 justified skips;
three identity checks; full replay audit; per-response critic policy assessments;
per-edit purposes and full-prose writer judgments; six anonymous pairs; verification
and tracker snapshot. The closure binds these files, the unchanged preparation,
142 frozen dependencies and this public report. Full prose remains private evidence.

Offline replay reconciles every attempted and skipped slot, all 28 static snapshots
and all dependent requests. Verification checks identities, per-call/aggregate usage,
full-prose exports, empty human-review sheets and unchanged source seals, with external
connections and gateway construction blocked. Private helper Ruff/format, documentation
links, UTF-8/LF and whitespace checks pass. Preparation's 75 focused regressions and
strict mypy across 201 files remain prior evidence against unchanged production code,
not a new regression run. No production or client code changed.
