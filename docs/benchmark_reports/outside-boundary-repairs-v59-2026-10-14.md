# Fixed-v59 outside-boundary writer repairs — 2026-10-14

Status: **COMPLETED — FOUR LOCALIZED BOUNDARY REPAIRS; INDIRECT STYLE PRESERVATION STILL OPEN.**

All four writer revisions repair the boundary while preserving every word before
the original final sentence. All four follow-up critics and all four outside
controls pass. The twelve probes use thirteen calls because one critic needs its
existing structural retry to correct a mistyped repair ID. All four generated
endings use explicit decision narration; the indirect controls establish critic
acceptance, not writer preservation of an independently valid indirect expression.

Start from `7adb39074669aacd442719470bae4e20e68216cd`, which merged the
[endpoint-wording comparison](endpoint-wording-v59-2026-10-14.md). Work is on
`codex/outside-boundary-repairs-v59`. Production remains prompt version 59 / graph
version 9, including the meaning of met, writer/critic instructions, schema,
repair rendering, compaction and retry policy. Step 19 remains IN PROGRESS;
Step 20 is NOT STARTED.

## Question and frozen inputs

Can the writer repair the four explicit outside-at-scene-end violations while
preserving the already fulfilled facts and decision? Does the following critic
recognize the repaired boundary without reopening the earlier touch/decision
repairs or replacing an indirect decision with a completion requirement?

Use the four saved `entered-outside_required` reviews, one for each combination
of source writer family 19101/19103 and critic seed 19101/19103. These are two
distinct prose revisions with four corresponding boundary reviews, not four
independent story samples. Retain each canonical review's claim, exact draft
evidence and application-rendered recommendation without editing their wording.
Both saved native assignment checks and both earlier repairs were met; each
review adds one blocking exit-state defect.

The synthetic Scene Plan and matching embedded Blueprint plan remain unchanged:

- Turning point: Elara touches the stroller and feels a psychic pull; both facts
  are required, with no assigned order or causal connection between them.
- Outcome: **Elara decides to enter the windowless building.**
- Exit state: **Elara stands at the threshold of the monolith. At scene end, she
  remains outside the building and has not crossed the sill.**

Keep the exact Story Bible, broader context and next-scene reservation from the
source comparison. These synthetic plans are diagnostic controls, not approved
canonical changes.

## Matrix and existing repair path

Twelve probes: **four writer/critic pairs plus four matched critic controls**.

| Source prose family | Saved review / new writer and critic seed | Input ending | Paired control |
|---|---|---|---|
| 19101 | 19101 | Completed entry; explicit decision narration retained | Saved outside ending |
| 19103 | 19101 | Completed entry; decision supported by reasoning/action | Saved indirect outside ending |
| 19103 | 19103 | Same source prose; its own saved boundary review | Saved indirect outside ending |
| 19101 | 19103 | Same source prose; its own saved boundary review | Saved outside ending |

Each writer receives its revision-1 draft, the existing source repair history,
and that exact canonical boundary review through the normal bounded revision
contract. It produces revision 2. The follow-up critic receives only that
validated output as its current candidate, with the same plan, source history
and shared repair tests. Its exact dependent request is frozen before generation.
No hand-written repair directions are added to production messages.

There are **three shared original repair tests**: the earlier missing-touch claim,
the earlier missing-decision claim, and the new boundary claim. The two outcome
claims share a category but have distinct obligations and repair identities.
They must not be collapsed because their categories match. The earlier raw audit's
met labels are not injected as extra instructions; the usual version-bound claims
and current prose determine fulfillment.

Standard compaction keeps the writer's latest prose, retains old draft identities,
projects historical review claims into shared tests, and omits duplicated review
scores/rationales. The critic receives the complete current candidate and exact
evidence catalogs. Identical Scene Plan/Blueprint copies retain the existing
duplicate-plan compaction.

Each control substitutes the previously accepted outside prose from the matching
source/seed case, changing only the revision number and derived draft identity.
It receives the same three repair tests as its writer/critic pair. Controls run
first; their results do not change which writer cases run. Writer and critic use
the corresponding saved critic seed, with existing temperatures 0.85 and 0.2,
top-p 0.95 and thinking disabled.

## Assessment declared before generation

Read the full revisions and exact diffs independently of the critic verdict.

1. The final position must be outside, without crossing the sill. Merely deleting
   the last entry sentence is insufficient if doing so removes the evidence that
   Elara has decided to enter.
2. Preserve the established touch, psychic pull, character motivation, identity,
   setting and unrelated successful prose/beats. Check for unrequested causal
   mechanics, premature later-scene material and broad rewriting.
3. Accept purposeful action and indirect narration as evidence of the decision.
   Added explicit decision narration is a style/scope observation, not automatically
   a logical failure. Track it separately from actual nonfulfillment.
4. Assess native turning point and outcome, both earlier repairs, the new boundary
   repair, the current boundary check and final verdict separately. A new defect
   must not reopen an unrelated original repair or claim its links.
5. All four fixed outside controls should have both native checks and all three
   repairs met, no overrun and a pass verdict. For generated prose, judge the actual
   achieved facts first: a writer failure with a correct critic rejection differs
   from a false acceptance or rejection by the critic.
6. Inspect first/final structural attempts, current finding links, duplicate
   reporting, condition sources and all mandatory advice. Traceability alone is
   not semantic support. Similarity scores are inspection aids, not quality gates.

## Local verification

- Verify **456 sealed files** across the three predecessor bundles, their reports,
  the frozen database and unchanged implementation hashes.
- Reconstruct all 24 previous endpoint requests and replay all 24 raw responses
  unchanged through production validation, including boundary/repair audits.
- Verify shared assignment, boundary and all three repair tests for each pair;
  retain exact prior feedback and standard context projection. Expected labels and
  diagnostic names are excluded from model messages.
- Seven mock gateway calls exercise all four writer builders, one structural retry
  recovery and permanent failure after the allowed retry. Mock prose is deliberately
  unchanged; this makes no claim of successful creative repair.
- Eight explicit local critic fixtures check both repaired and unresolved boundary
  states for all four cases. Both native checks and the earlier two repairs remain
  met; an unresolved boundary yields one blocker linked to its own repair, while
  the accepted outside fixture clears it. These are local validation fixtures,
  not fresh model judgments.
- **45 relevant tests pass** in 14.21 seconds: isolated probes, v31 repair
  acceptance, v39 boundaries and v59 consolidation. The first sandboxed run
  stalled on its first database-backed test without reporting an assertion
  failure and was interrupted. The identical test selection passed outside the
  sandbox with a 60-second stack-dump diagnostic enabled; no stack dump fired.
  This distinguishes the successful rerun from the uncompleted first run without
  claiming a proven root cause for the stall.
- Diagnostic scripts pass Ruff formatting and syntax/undefined-name checks.
  No application implementation changed; the full application suite and frontend
  build were not repeated for this diagnostic/documentation change.

## Bounds and provenance

Private bundle: `data/diagnostics/outside-boundary-repairs-v59-2026-10-14/`.
Plan SHA-256: `bce2738d3d7d777a49f6b077d536249b5adbe363942d73b54e57ff366c5a1eae`.
Source database SHA-256:
`71618ce4d66ffd3b8ecc46fa4d034105b4e59aa5a80946b5364272b87caeafb2`.

- Maximum **12 probes / 24 calls**, including at most one existing structural
  retry per probe. A failed writer has no follow-up critic call.
- Per-call limits: 24,000 input / 8,000 output tokens, with existing provider
  selection and the recorded `gemma4:31b-cloud` digest checked before generation.
- Maximum recorded-rate estimate: **USD 0.15744**, using October 8 rates of
  USD 0.14/M input and USD 0.40/M output tokens. Actual charges remain unknown.
- Destination: the existing local Ollama daemon forwarding to Ollama Cloud.
- No additional prose-revision round, valid-response rerolls, outcome-dependent
  additions, adjudication, continuity/full-story calls or canonical writes.
- Reconstruct dependent requests, replay every returned response, inspect actual
  prose and advice, report usage and reverify source hashes before sealing results.

The user explicitly approved this frozen matrix on October 14: “Yes, run the v59
boundary-repair experiment.” `approval.json` records the authorization and exact
plan hash. The approved run completed in thirteen calls: four writer calls and nine
critic calls, including one existing structural retry. No further generation ran.

## Results and prose inspection

| Source family / seed | Writer result | Follow-up critic | Outside control |
|---|---|---|---|
| 19101 / 19101 | Outside; decision retained; final sentence replaced | Pass on first attempt | Pass on first attempt |
| 19103 / 19101 | Outside; decision expressed directly; final sentence replaced | Pass on first attempt | Pass on first attempt |
| 19103 / 19103 | Outside; decision expressed directly; final sentence replaced | Pass on first attempt | Pass on first attempt |
| 19101 / 19103 | Outside; decision retained; final sentence replaced | Pass after one ID correction | Pass on first attempt |

All four writers validate on their first attempt. The actual prose supports the
boundary repairs: Elara remains outside, has decided to enter, and does not begin
the encounter with Thorne reserved for the next scene. **Every word before the
original completed-entry sentence remains identical in all four revisions.**
Thus the touch, psychic pull, existing causal/temporal wording, motivation, prior
reasoning and unrelated scene material are preserved exactly. Other draft fields
also remain unchanged apart from the revision number. No new story mechanics or
immediate-causation requirement is added.

The replacements are:

- Family 19101 / seed 19101: “She stood at the threshold, her gaze locked on the
  windowless dark, and resolved to enter.”
- Family 19101 / seed 19103: “She stood at the threshold, staring into the
  windowless dark, and resolved to enter.”
- Family 19103 / seed 19101: “Elara took a sharp, decisive breath and made her
  choice. She would go inside.”
- Family 19103 / seed 19103: “With a sharp, decisive breath, Elara resolved to
  enter. She stood at the threshold, staring into the gloom, her feet still
  anchored in the daylight, but her mind already inside.”

The last replacement uses an internal metaphor while explicitly keeping her feet
outside; it does not describe literal entry. The third relies on the unchanged
earlier statement that both boots are outside and supplies only a decision, with
no subsequent movement. Word counts change from 695 to 700/698 in family 19101
and from 671 to 669/685 in family 19103. Exact diffs and complete prose are retained
in the private `inspection/` directory.

All eight final critic reviews have both native checks **met**, all three original
repair checks **met**, an empty current-finding link list for each satisfied repair,
`no_overrun` and a pass verdict. No canonical issues, generic complaints, assignment
violations or new authored condition sets are emitted. The missing-decision and
boundary claims remain separately recognized despite sharing a category.

All four outside controls pass on their first attempt. Two retain an earlier
explicit decision sentence; the two family-19103 controls establish the decision
through reasoning, preparing the torch and bracing to enter. The critic accepts
those indirect cases without requiring an explicit declaration or actual entry.

### Structural retry

The first review of `f19101-s19103-entered-outside_required-critic` omits one
character from its boundary repair ID (`58a6553` instead of `58a65553`). The existing
exact-ID check rejects it with `repair_test_coverage_invalid`. The sole allowed
retry corrects the ID and validates. First-attempt validity is **11/12 probes**,
or **7/8 critic probes**; all twelve ultimately validate. The failed first response
is retained and is not counted as an accepted review.

Native assignment statuses, boundary status and verdict remain unchanged across
the retry. Explanatory wording changes; `assessment.json`'s
`first_to_final_check_drift` compares complete check objects and therefore flags
that wording change. The separate semantic inspection records no status drift.
There was no second writer revision, manual response correction or reroll.

### What the indirect-decision result establishes

The boundary and factual repair succeeds in all four cases. The writer chooses
explicit decision narration in all four replacements. In family 19101 this even
adds “resolved to enter” after the already preserved “decided she could not leave
without knowing,” making the decision redundant. In family 19103 it replaces an
action-based ending with a direct statement while preserving the preceding
reasoning. These are observable prose choices, not evidence that the critic or
repair conditions required explicit wording.

The original family-19103 decision was partly expressed by the very crossing that
had to be removed. This matrix consequently does **not** isolate whether the
writer preserves an already valid indirect decision that is independent of the
defect. The accepted outside controls show that the critic can accept such an
expression under this repair history, but the writer never revises those controls.
Do not report this as either proven indirect-style preservation or a proven
general writer regression.

## Verification, usage and next focused test

All thirteen exact requests/responses, including the rejected response and retry,
were reconstructed and replayed through unchanged production validation. Dependent
critic candidates match the unedited writer outputs. Source reports, frozen code,
456 prior sealed files and the database were reverified. Local fixtures, regression
results, full prose/diffs, semantic inspection and receipts are retained;
`closure.json` indexes the new private evidence and this report.

Usage: **223,055 input / 18,028 output tokens**, estimated **USD 0.03843890** at
the recorded October 8 rates, below the approved USD 0.15744 ceiling. Provider
receipts still report an unknown cost basis and a zero placeholder; actual charges
remain unknown. Production, main, canonical stories and sealed benchmarks remain
unchanged. Only this diagnostic and its documentation were added.

Keep v59 fixed. To isolate the remaining preservation question, start with an
already accepted indirect outside decision and append a separate forbidden entry
sentence. Test whether the writer removes that overrun while preserving the
independent indirect expression. That permits a correct repair without rewriting
the decision itself and distinguishes scope preservation from the necessary
replacement of the action that previously conveyed it. Prepare and approve a new
bounded matrix before generation; no such calls were made here. No further critic
guidance change is warranted by this result alone.

This is one scene/provider, two source prose families and four reviews at two
seeds. Writer seeds and feedback vary together within each source family, so
differences are not attributable to seed alone. These results do not establish
full-story scope preservation, preference or cost acceptance.
