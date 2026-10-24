# Proposed bounded reviewer premise comparison

Date: **2026-10-24**. **PROPOSAL ONLY: not frozen, not approved for inference.**
Production prompts remain unchanged, live calls remain **PAUSED**, and the full
workflow canary remains **ON HOLD**. This follows the
[local extra-field and premise audit](reviewer-field-premise-audit-2026-10-24.md).

## Question and intervention

Can one explicit check of factual premises reduce unsupported explanations without
losing correct targets, useful literary observations or valid delivery?

Use `deepseek-v4.1-flash:cloud` in **two arms**:

| Arm | Proposed difference | Attempts |
| --- | --- | ---: |
| Unchanged D2 | Exact archived D2 renderer and instructions; historical control messages reused byte-for-byte | 16 |
| D2 plus premise check | Same D2 schema, evidence policy and context, with one fixed case-independent diagnostic instruction card | 16 |

The proposed card would ask the reviewer to check factual premises against the
whole source before finalizing each explanation: distinguish text events from
assignment restrictions, check the actual scope of “before” and “after,” retain
independent reasons, and distinguish incompatible assertions from identical ones.
It would allow a qualified literary interpretation or uncertainty when the text
does not establish a stronger factual claim. Explanations would still use the
existing assessment/evidence fields; no extra field, trace, judge call or report
repair would be introduced.

**The card has not been written into a prompt or rendered into requests.** Its
exact wording, position and size would be reviewed and frozen during preparation.
It must contain no case IDs, quoted answer examples, gold judgments, selected
passages or outcome-dependent advice. Both arms receive the same complete source
and context. Do not combine this with a delivery-layout change, M1 ownership card,
temperature change, shortened output schema or a new writer instruction.

D2 is chosen to keep the layout constant while probing its known explanatory
failures. It remains unqualified. This experiment would not establish superiority
over C2, since C2 would not be a concurrent arm. It would test the premise-check
package, not isolate instruction meaning from added length or attention; any
positive result would still need replication.

## Proposed cases and controls

**Eight cases × two arms × two presentation orders = 32 maximum attempts.**
Retain four unchanged historical packets and add four genuinely new scene
families. The suggested coverage is:

| Historical case | Failure or boundary to retain | Fresh counterexample to construct before freezing |
| --- | --- | --- |
| A00, radio | An absent recognition does not establish an unidentified voice; a deferred question does not itself prohibit broadcast | A scene where an unidentified voice really is present; retain clear event/endpoint distinctions |
| B10, costume | Before explaining is not before deciding/acting; seam alteration is not whole-garment destruction | A scene with an explicit consultation-before-action condition that is actually violated |
| E-compound, footbridge | Routine inspection remains a reason after the immediate hazard is removed | A scene where the text explicitly makes a particular cause the sole reason, and the revision removes it; include a permissible cleanup independently |
| F-narrow, bakery | Same crate/time with different exact counts is a genuine contradiction outside narrow retention scope, not an identical sentence | A scene with an actual accidental exact duplicate and a supported removal, preserving the assigned endpoint |

These fresh counterexamples guard against learning to reject every temporal,
motivational, sensory or repetition claim. They are different families, so they
are conceptual contrasts rather than minimal textual pairs. Treatment/control
comparisons remain paired on each exact case. At preparation, retain complete
prose, explicit scope, source/version/offset catalogs, changed paragraph groups
and withheld judgments for every case. Neither expected literary preference nor
minimum edit size should enter the gold labels.

OR and RO change display order without changing original/revision identities.
Counterbalance arm order. Inspect all valid reports with arm/order hidden and seal
notes before decoding the key. These would be eight family clusters and repeated
presentations, not 32 independent stories. This proposed set does not test long
stories, no-op invariance generally, or writer behavior.

## Budget, stops and execution boundary

- **32 total, sixteen per arm, one attempt per cell, zero retries/replacements.**
  Earlier budgets remain closed; Gemma D remains stopped. No unused allowance
  transfers between experiments.
- Provisionally retain the previous settings: temperature 0.2, top-p 0.95,
  seed 20261022, thinking and streaming disabled, 24,000 input / 8,000 output /
  32,000 context tokens, and 300 active seconds per call. Aggregate reservation:
  **768,000 input / 256,000 output tokens / 9,600 active seconds**. Freeze an
  explicit cost planning allowance before approval; no current pricing claim
  or billing guarantee is made by this proposal.
- Retain the archived model digest and **0.40.9 as the last verified daemon
  version**, not a discovery of today's installation. Preparation must record
  the intended baseline. Approved preflight and before/after-call checks must
  match it; an update or identity change stops execution rather than silently
  changing the experiment.
- First eight calls: one historical case and one fresh case, both orders and
  arms. Prefer B10 plus the fresh temporal counterexample, covering two families.
  Stop the comparison if either arm has zero valid answers or the same normalized
  structural signature occurs in at least three of its four answers across both
  families. Do not substitute cases after seeing results.
- Preserve normal-stop invalid answers as failed cells. Stop on non-200,
  transport/timeout/cancellation, length/incomplete finish, missing/excessive usage,
  unexpected thinking, version/model drift, changed source/request identity,
  unresolved reservation or accounting inconsistency. Preserve unknown usage and
  the gateway error chain; no automatic recovery after a terminal stop.
- Use exact-wire guards, reservations before dispatch, one operator, sealed
  captures and safe completed-cell restart. Completing the ceiling prevents
  further discovery or inference. The new plan must explicitly authorize full
  unpublished prose/context to Ollama Cloud via the local daemon before live work.

## Proposed scoring and interpretation

Keep strict unique-key JSON, closed schemas, complete record coverage and exact
evidence validation. All assessment fields still require source inspection;
brevity, uncertainty everywhere, or correct verdict labels alone do not establish
a usable report. Report separately:

1. Delivery, including extra fields, duplicate keys and syntax failures.
2. Supported target judgments, original mandatory aggregate and separate local
   aggregate, with no substituted or repaired scores.
3. Group labels, optional-cleanup recognition and actual contradiction detection.
4. Factual premise support across every explanation, separating **unsupported**
   from **uncertain**. Preserve a secondary distinction between decision-relevant
   invented constraints/events and narrower wording inaccuracies. Both remain
   visible; no retrospective reclassification of the prior run.
5. Complete usable reports, with no prescribed literary winner. Evidence-backed
   mixed effects, different tastes and qualified interpretations remain allowed.

Proposed screen for retaining a new candidate as promising diagnostic evidence:

- All 32 cells complete; at least **15/16 valid treatment reports**, including
  **7/8 fresh cells**.
- At least **three paired semantic recoveries**, spanning **two families**, with
  **one historical case recovered in both orders**. A semantic recovery requires
  a valid baseline report that failed premise support, and a treatment report
  that is valid and completely usable. Delivery-only gains are reported separately.
- No loss of a baseline valid report, usable report, supported target judgment,
  supported optional success or detected genuine contradiction. No new blanket
  false rejection on the fresh counterexamples.

**Declare opportunity limits explicitly before running.** If the contemporaneous
baseline does not produce enough eligible premise failures to meet the recovery
requirement, report **insufficient recovery opportunity**, along with absolute
performance and any regressions. Do not call stable success proof of improvement,
lower the threshold, add cases, or spend extra calls. A clear delivery/control
regression still remains a failure even when opportunities are insufficient.
The recovery screen can still have too few opportunities, as the previous
delivery screen did with only two C2-invalid cells against four required
recoveries. The proposed interpretation makes that limitation explicit without
rewriting the historical decision or ignoring its independent control losses.

Passing would mean **retain promising diagnostic evidence only**. It would not
qualify D2, change production prompts, authorize writer revisions or release the
canary. The future story-quality question remains whether trustworthy feedback
helps a writer produce a better reading experience, not whether explanations
contain fewer words or revised prose matches its source more exactly.

## Preparation required before live approval

If selected, first create and inspect the four fresh families, freeze the two
exact request variants and all 32 requests, finalize labels and field-level
inspection rules, bind the budget and stops, and verify mocked adapter calls,
restart/accounting and terminal export locally. Keep the existing negative and
positive fixtures as regression controls. Present that frozen plan for approval
before preflight or inference. This document alone authorizes none of those live
actions.

Humans should retain their role in judging feel/emotion, flow, character and
story-breaking details, with machine-prepared mechanical evidence. No new human
production checkpoint is proposed. **Production prompts unchanged; Step 19 IN
PROGRESS; Step 20 NOT STARTED; live calls PAUSED; canary ON HOLD.**
