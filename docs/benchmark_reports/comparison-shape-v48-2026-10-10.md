# Explicit comparison retry shape v48: 2026-10-10

Implementation, required local quality checks and three approved controlled
retries are complete. All three reviews validate with the same two original
repairs and no new targets. Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.

## Change

V47 excluded the invalid craft link in all three controlled retries. Two reviews
validated, while seed 19103 returned `assignment_comparison` as plain text. The
output schema already required an object; the targeted retry directive described
claim comparison and reference coverage without restating the field structure.

Production contract v48 / graph v9, critic retry policy 15 makes that structure
explicit in the existing comparison directive:

- `finding_refs`: an array of distinct reference strings, bounded to eight and
  limited to assignment findings reported in the rejected review.
- `assessment`: a nonblank string of at most 1,000 characters.
- Both fields are required. A string, null, missing field or additional key is
  invalid. With no reported assignment findings, the array must be empty, while
  the assessment remains required.

The directive includes `required_shape`, derived from the existing comparison
schema builder. It preserves the adjacent semantic comparison instructions and
finding groups; it neither supplies an assessment nor chooses the model's
references. Normal validation still checks the replacement response's actual
findings, selected target and coverage. Classification retention and independent
craft link restrictions remain intact.

This refines the instruction established by [ADR 0030](../adr/0030-explicit-assignment-and-craft-comparison.md).
There is no schema, canonical artifact, persistence, writer, system prompt or
initial-review content change. Retry budgets and failure behavior are unchanged.
Rejected prose is not replayed or automatically wrapped into an object. Other
specialists retain retry policy 10.

## Local verification

Eight new regressions cover local/cloud delivery, repeated and independent
classification, absent and multiple assignment findings, and persisted retries
with both independent craft ownership and a consolidated assignment repetition.
The two persisted cases preserve the same two original repairs and five writer
calls; each malformed review fails before one permitted structural retry succeeds.
The output schema remains identical between first review and retry. Returning the
same malformed comparison still fails rather than being silently corrected.

Saved v47 responses replay unchanged: the two successes produce identical
canonical results, and the malformed comparison remains rejected. Its previously
labeled offline correction also produces the same canonical result. No v47
outcome is reclassified as new live success.

Ruff lint/format, strict mypy across 187 Python files, frontend formatting/lint/type
checks, 11 frontend tests and production build pass. The full Python suite passes:
**892 tests in 180.94 seconds**.

## Controlled comparison

Use the same saved v45 first rejection, private OH-V01-002 unchanged draft,
synthetic explicit endpoint and seeds 19102, 19103 and 19104 as v47. Each receives
one remaining structural retry. This starts from the original first rejection;
it does not extend the failed v47 sequence or grant a third attempt.

Prepared-request comparisons verify identical artifact inputs, model settings,
budgets, system message and output schema. Only the retry policy version and the
comparison directive's shape instruction change. Each user packet grows by
**804 characters**. Classification preservation and every other directive match.

Expected observations: valid comparison objects, retained classification,
empty original craft links, no craft ID on the consolidated complaint, complete
boundary/outcome links, and exactly the two original repair targets.

- Destination: existing Ollama Cloud `gemma4:31b-cloud` via the local daemon.
- Maximum: **three calls**, 24,000 input / 8,000 output tokens per call.
- Recorded October 8 rates: USD 0.14/M input and USD 0.40/M output.
- Maximum recorded-rate estimate: **USD 0.01968**; actual charges unknown.
- No fresh first reviews, additional retries, writer calls, full-story runs or
  canonical changes. Sealed benchmark results remain unchanged.

Private frozen requests, hashes, saved-response replays and runnable harness are
under `data/diagnostics/comparison-shape-v48-2026-10-10/` (ignored by Git).
The source database is read-only, SHA-256
`71618ce4d66ffd3b8ecc46fa4d034105b4e59aa5a80946b5364272b87caeafb2`.

This is one saved failure and one model, without a live independent-craft control.
Seeds are controlled settings, not a guarantee of provider determinism. Any
improvement would be narrow retry evidence, not proof of overall critic accuracy,
full-story recovery, human preference or cost acceptance.

## Results

The user explicitly approved the revised requests. Exactly three calls ran, with
no additional attempts. Each exact request and response hash was verified;
responses were replayed without edits, including their repair and boundary audits.
Frozen source evidence and the read-only source database remain unchanged.

| Observation | Result |
| --- | --- |
| Fully validated REVISE reviews | **3/3**, versus 2/3 in v47 |
| Valid comparison object and selected-target reference | 3/3 |
| Original classification and metadata retained | 3/3 |
| Consolidated complaint excluded from separate craft links | 3/3 |
| Original outcome includes boundary and outcome links | 3/3 |
| Exactly two original repair tests retained; no new targets | 3/3 |

All three comparisons describe immediate handwriting confirmation as the same
endpoint breach, with prematurely resolved skepticism as its craft consequence.
Each comparison selects `assignment:outcome`. The synthetic endpoint forbids
establishing the match, and the cited draft passages explicitly establish one.
Manual inspection found no switch to an independent craft claim, omission of the
original obligation, or newly introduced repair target.

The original tension check remains unmet with empty links; the original outcome
check remains unmet with both native links. This preserves both historical
obligations while consolidating the current repeated complaint. Optional craft
IDs are omitted in seeds 19102 and 19104 and explicitly null in 19103; both forms
are valid. No application-side correction was needed.

Usage: **43,581 input / 4,244 output tokens**, estimated **USD 0.00779894** at the
recorded October 8 rates, below the approved USD 0.01968 maximum. Provider numeric
cost is zero with an unknown cost basis, which does not establish zero billing.
Actual charges remain unknown.

The previously failing seed now returns the required object, and the other two
remain valid. This supports the focused instruction change for this saved case;
three retries cannot establish a general failure rate or attribute the difference
with certainty to the instruction. No production code changed during or after
the campaign; all local checks still apply. Canonical stories and sealed benchmark
results remain unchanged.

## Remaining work

The comparison-format defect is resolved in this controlled sample. The next
focused investigation should return to the missing-turn control's separate
decision-to-verify complaint from v45. Its inconclusive verification passage was
identical to an accepted revision, but the critic additionally demanded a future
decision to verify. Compare those contexts and the assigned outcome before making
another production change; this is a different judgment problem from comparison
format or duplicate craft links.

Broader reviewer sensitivity, fresh reviews and full-story recovery remain
unqualified. Human preference and cost acceptance are also still open for Step 19.
