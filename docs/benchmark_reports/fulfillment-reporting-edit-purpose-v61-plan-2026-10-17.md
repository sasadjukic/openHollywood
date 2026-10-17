# Frozen reporting-retry and edit-purpose comparison

Date: 2026-10-17. **PREPARATION COMPLETE; NO LIVE EXECUTION AUTHORIZED OR STARTED.**

This implements the authorized local preparation from the
[diagnosis and proposal](../handoffs/fulfillment-reporting-edit-purpose-diagnosis-next-experiment-2026-10-17.md).
P1 and J1 remain diagnostic evidence; E1 remains mechanically successful but
unqualified for preservation. Production stays at prompt **61**, graph **9**,
fulfillment policy **1**. **Full workflow canary: ON HOLD; NOT STARTED.**

## Frozen budget and model

| Block | Work | Maximum inference calls |
| --- | --- | ---: |
| A: retry feedback | 16 shared P1 initial reviews; up to one R0 and one R1 correction after each structural failure | 48 |
| B: edit purpose | 12 writers and 12 conditional ordinary posts; one structural retry each | 48 |
| **Total** | **40 primary calls; 72 scheduled slots including conditional A branches** | **96** |

The blocks are nontransferable. Stage ceilings: **16 initial reviews, 32 correction
calls, 24 writer attempts and 24 post-review attempts**. A valid initial review is
shared by both policies and consumes one call; its two correction slots are skipped.
An invalid writer skips only its post. No semantic retries, transport rerolls,
replacement cases, source replacements, extra revisions or third attempts. Earlier
unused budgets do not apply.

Each call reserves 24,000 input tokens, 8,000 output tokens and 900 active seconds.
Aggregate ceilings: **2,304,000 input tokens, 768,000 output tokens, 86,400 active
seconds**. At the historical October 8 rates only, the ceiling estimate is
**USD 0.62976**. Actual billed charges are unknown; this is not a billed-dollar cap.

Model: `gemma4:31b-cloud`, through **Ollama Cloud via the local Ollama daemon**.
Pinned digest:
`c382fbfbc73b6fdd08c8549c23caedc6e62eb09933c65a1fb82dbf3398320a4e`.
No model discovery occurs during preparation. Future approved execution verifies
the identity at preflight and before each phase and stops on mismatch.

Seeds **19601/19603**, top-p **0.95**, thinking disabled. All critics use temperature
**0.2**; both writer arms use **0.85**. R0/W0 run first at 19601; R1/W1 first at
19603. The order is frozen, with separate ledgers for every logical branch.

## A: shared initial review, paired structural correction

Use these eight exact previously sealed full scenes and input versions. No story
text or assignment changes are introduced during this preparation.

| Case | Expected turning point / outcome / boundary |
| --- | --- |
| Elara base, within boundary | met / met / no overrun |
| Elara base, overrun | met / met / overrun |
| Elara adjacent duplicate, within boundary | met / met / no overrun |
| Elara adjacent duplicate, overrun | met / met / overrun |
| Elara functional recurrence, within boundary | met / met / no overrun |
| Elara functional recurrence, overrun | met / met / overrun |
| Elena missing decision | met / unmet / no overrun |
| Elena compound outcome | met / unmet / overrun |

Expected labels and construction rationales stay outside model messages. Functional
recurrence has an intended changed narrative role, not automatic literary immunity.
Specific supported craft criticism remains possible. The two Elena cases require
real native repairs; deleting all condition records cannot satisfy the experiment.

Every initial review uses P1: exact continuous prose alongside the unchanged
sentence catalog, with ordinary critic instructions, schema and validators. A
semantically wrong but structurally valid response receives no retry.

When an initial response is structurally invalid, its exact response hash and
ordinary validation errors bind both branches:

- **R0:** existing ordinary structural retry feedback.
- **R1:** identical system instructions, context, schema, settings and existing
  feedback, plus `schema_repair.additional_structural_feedback`. This contains
  concrete locations and bounded metadata for condition ownership, independently
  authored linked recommendations and craft-comparison coverage where the required
  current findings can be established structurally.

Each branch has **one correction call and no further retry**. The initial response
is not resent as prose or adopted as truth. Existing production classification
retention remains in force when available. Final acceptance uses the unchanged
ordinary validator, not the diagnostic collector.

The collector checks native wire metadata and current evidence before listing
reported condition owners. It does not convert invalid/missing native conditions
into successful repairs. To inspect comparison coverage despite the known ownership
errors, an isolated copy removes only application-boundary condition entries and
separately authored linked advice; the existing renderer and hard-finding validators
then establish usable comparison groups. This copy is discarded. No native condition,
judgment, evidence, accepted review or writer source is generated by that projection.
If dependencies cannot validate, comparison feedback is unavailable rather than
invented. At most 16 diagnostics and 10,000 serialized diagnostic bytes are included;
overflow is explicitly marked partial. This is bounded structural feedback, not a
claim to enumerate every possible error in arbitrary malformed JSON.

A useful R1 signal requires:

- At least two paired qualified rescues, including a duplicate-plus-overrun case,
  and no paired loss.
- Valid supported duplication findings in all four duplicate cells, including both
  combined cells; no dropping, severity manipulation or reclassification to evade
  the correction task.
- Valid supported native/boundary judgments in all 16 cells, with necessary native
  repairs present and supported in the Elena controls.
- No unsupported repetition-removal demand on the eight base/functional-recurrence
  controls. Minor findings count; invented mandatory conditions do not.

Fewer than two failed initials makes the retry comparison **inconclusive**. Do not
manufacture failures or add seeds. Shared valid initials are one observation each,
not independent successes for two critic arms. Raw correct observations in rejected
responses remain diagnostic only. Structural recovery and semantic support are
scored separately, with exact evidence and explanation inspection.

## B: exact edits with a checkable purpose

Freeze three sources, each used by both writer arms at both seeds:

1. The existing ordinary separate-entry source: `s19101-elara-separate-initial`,
   successful attempt 2.
2. The existing ordinary embedded-entry source: `s19201-elara-embedded-initial`,
   successful attempt 1.
3. The existing valid P1 optional craft source:
   `s19501-elara-duplicate-within-initial-P1`, attempt 1. Its original verdict is
   **pass**, severity **minor**, and advice removes one adjacent duplicate.

Each source retains its complete draft, actual critique, receipt, assignment,
fulfillment evidence, context and original mandatory repair tests. A's new results
cannot gate or replace these sources. No corrected response from the diagnosis is
eligible. All source identities and hashes are in `writer-sources.json`.

**W0** uses unchanged E1 exact-edit instructions and schema. **W1** adds the frozen
edit-purpose instruction, a catalog of existing target identities, and a `purpose`
object on each edit:

- `target_refs`: one to eight distinct existing repair-test or requested optional
  issue identities.
- `kind`: `direct_repair` or `necessary_adjacent_adjustment`.
- `defect_if_original_kept`: a nonblank statement of at most 600 characters explaining
  the supplied defect that retaining the selected text would leave, or the adjacent
  grammatical/flow adjustment required by its repair.

This is an inspectable editorial claim. References and field shape are mechanically
validated; its substantive support is not assumed. Generic improvement claims or
invented defects cannot count as successful justification. An unsupported but
well-formed rationale receives no semantic retry.

Both arms retain E1's original occurrence selectors, base hash/version, nonoverlap
requirements and atomic application, including its existing 64-edit representational
limit. No additional edit quota or protected prose is introduced. Both may edit
fulfilled evidence or make a justified broader repair. Exact restoration and minimal
diff size are diagnostic measures, not literary acceptance gates. W1's purpose
objects are saved separately and removed before applying the unchanged E1 patch
contract; they never enter materialized prose or the post-critic's messages.

Both arms receive the same explicit optional-craft task for source 3. Its pass/minor
status is preserved, with **zero manufactured mandatory craft tests** and no claim
that production automatically revises passing scenes. The diagnostic post adapter
supports the genuinely empty mandatory-test list. No-op edits remain structurally
expressible, but failing to address this requested craft task fails semantic scoring.

The craft repair must remove accidental duplication while retaining the bracing
action, indirect decision, boundary and unrelated prose. Only one duplicate copy
has positive native evidence: deleting the other can succeed without touching that
evidence. Inspect actual range overlap; this control does not qualify craft repairs
that necessarily alter fulfilled evidence.

Every valid materialized writer output gets one unchanged ordinary **P0** post-
review, with its one permitted structural retry. Identical W0/W1 materialized prose
must produce identical post messages. Post-critics receive neither edit purposes
nor the optional-task extension; they retain the original critique and ordinary
repair context. Passing these reviews does not establish preservation or successful
optional craft repair. Operator inspection reads complete original/revised scenes
and diffs; anonymous full-prose pairs are exported for separate human review.

Provisional W1 success requires all four boundary repairs and both optional craft
repairs, fulfilled facts retained, at least two clear preservation wins among the
four boundary pairs including an embedded case, no preservation loss in any of the
six pairs, and supported purposes for the actual changes. Invalid or missing outputs
remain in scheduled denominators. Mixed and tie do not count as wins. Record a
sensitivity analysis treating debatable additions as neutral without replacing the
primary labels. Human literary preference remains pending.

## Freeze, verification and execution boundary

Private bundle:
`data/diagnostics/fulfillment-reporting-edit-purpose-v61-2026-10-17/`.
The complete eight cases, three writer sources, schedule, scoring, input versions,
code dependencies and **28 exact static requests** are frozen. Unknown future output
bytes cannot be precomputed: the 32 possible corrections, 12 posts and B retries use
frozen builders, with every actual request saved and durably reserved before dispatch.

Request-size estimates are diagnostics, not exact provider tokenization. Tested
complete requests must fit the local estimate without trimming prose/context; actual
provider usage remains subject to the frozen per-call and aggregate limits. Integrity,
identity, budget, cancellation, transport or unknown-outcome failure stops execution.
No automatic transport resubmission or source substitution is allowed.

Local verification covers paired deltas, valid/invalid native ownership, comparison
references, missing/stale evidence, purpose validation and nonleakage, real optional
source lineage, branch accounting, budget limits, malformed output, cancellations,
unknown outcomes, corrupt evidence and replay. The actual operator is exercised with
fake providers while network connections and real gateway construction are blocked.
The frozen verification record distinguishes fixture evidence from any live success.

Verification passed: **96 valid response fixtures**, 28 paired request-difference
checks, 24 invalid-purpose checks, all four historical failed P1 attempts, and six
identical-post comparisons. The fake operator made **181 fixture calls**: 96 in the
ceiling matrix, 40 with shared valid initials, 42 in the fault matrix and three
terminal-error dispatches. Final code replayed all **178 completed attempts and 63
skipped slots**; completed reruns added zero calls. Six complete anonymous pairs and
five available fault-matrix pairs export correctly, with two scheduled craft pairs.
Approval mismatches, request/response corruption, source mutation, malformed/stale
native evidence and feedback bounds were checked. Assessments remain empty/pending.

All **75 focused fulfillment/probe regressions** passed, as did repository Ruff,
formatting and strict mypy checks across 201 files and lint/format for eight private
helpers. No client changes require frontend checks. The maximum static request
estimate is **17,282 tokens**; the maximum across 96 tested fixture requests,
including dependent retries, is **19,747**. These are estimates, not provider counts.
Preparation and verification made **zero live inference or discovery calls**.

Pre-freeze adapter fixes are recorded in `verification.json`: the reused Elena
source alias, ordinary post construction for the pass/minor source with no mandatory
tests, malformed-reference handling and craft-pair export metadata. Historical
captures remain intact; final replay and exports passed against the frozen builders.

Frozen `plan.json` SHA-256:
`ee346c83e38643f9f1438279cde5863067e51896d8da2519fd9788651cc22844`.
The check counts and preparation seal are recorded in the tracker and private
closure. **Fresh explicit approval binding that plan, full unpublished
prose/context, Ollama Cloud via the local daemon and the 96-call ceiling is required
before any discovery or inference.** This preparation grants no live authorization.

This remains a narrow diagnostic. Keep full-scene voice, tension, agency and
naturalness in the pair assessments, and retain the accepted whole-story rubric,
hard gates, full intended Cloud corpus and comparable single-model baseline for
later quality qualification. No production prompt, validator, runtime, canonical
artifact, graph node or mandatory human story checkpoint changes here.

**Step 19 IN PROGRESS; Step 20 NOT STARTED; canary ON HOLD.**
