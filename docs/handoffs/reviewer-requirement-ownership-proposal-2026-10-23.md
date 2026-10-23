# Proposed requirement-ownership comparison

Date: **2026-10-23**. Status: **PROPOSAL ONLY — NOT FROZEN OR APPROVED**.

The [local regressions](reviewer-scope-regressions-2026-10-23.md) support testing
one remaining hypothesis: a reviewer may find the relevant evidence yet assign
it to the wrong requirement. The two F02 mandatory aggregates can already be
flagged deterministically from their task verdicts. More inference is useful
only to test the model's requirement mapping and the truth of those verdicts.

I recommend **one 48-attempt DeepSeek comparison**, with unchanged C2 controls,
one candidate and four genuinely new scene families. No Gemma delivery pilot,
writer revision loop, structural-repair call or full workflow canary is included.
The seven unused slots from the prior run remain unavailable; this would require
a new budget and separate approval after local preparation.

## One intervention

**Control: unchanged C2.** Preserve its system text, output schema, vocabulary,
evidence cardinality, full source/context, grouping method and settings. Only the
new scene material and assignment contracts change between cases.

**Candidate M1: C2 plus an application-authored requirement ownership card.**
For each case, the card restates the supplied requirements with stable IDs and
their report destinations: earlier discoveries/decisions to their fact checks;
the explicitly assigned final state to `endpoint_check`; exact mandatory test
IDs to task checks and the mandatory aggregate; optional requests and other
craft concerns to their existing fields. Where a required task covers several
requirements, the card lists that membership explicitly.

The card must contain **no expected status, selected evidence, answer, critique
of the revision, gold aggregate or claim that any edit succeeded**. Scope comes
only from the supplied assignment. If scope cannot be stated unambiguously,
reject or clarify the case before freezing it. An instruction to report a craft
defect separately does not instruct the reviewer to ignore it.

M1 keeps the C2 response schema and field order unchanged. It does not incorporate
T1's extra temporal instructions, R1's renamed categories or D1's schema ordering.
This isolates a case-specific ownership representation against C2. It still
changes input length and salience: a positive result would support this card as
a package, not prove that any individual phrase caused the improvement.

The local aggregation projection runs on both arms **after capture**, as a
diagnostic. It never overwrites the model's `mandatory_failure` field or turns a
wrong report into a primary success. An optional secondary counterfactual may
measure how many disagreements the projection flags, clearly labelled as such.

## Proposed matrix: 12 cases, four new families, 48 attempts

| Case group | Planned contrasts | Cases | Calls: two arms × two display orders |
| --- | --- | ---: | ---: |
| Fresh family A | Required earlier event retained/lost × explicit final state satisfied/violated | 4 | 16 |
| Fresh family B | Same 2×2 contrast with different characters, conflict, narration and setting | 4 | 16 |
| Fresh family C | Identical original/revision pair with a real contradiction; narrow assignment versus an assignment explicitly requiring consistency | 2 | 8 |
| Fresh family D | A different contradiction and narrative form, again with narrow versus explicit consistency scope | 2 | 8 |
| **Total** | **12 cells × C2/M1 × OR/RO** | **12** | **48** |

In family A, retain a permitted later transition in the endpoint-satisfied
variants, so departure itself cannot stand in for failure. In family B, hold a
successful optional cleanup constant across the four variants: it must neither
cancel a mandatory failure nor manufacture one. Do not make every positive
endpoint mean physical confinement or every lost event mean a date change.

Use genuinely new scenes, not renamed versions of the card, safehouse, tram or
ferry. Aim for roughly 200–600 words with different emotional stakes and at least
two narrative styles. Keep the original, surrounding context and unrelated edits
constant within each contrast. Across C/D's scope pairs, prose must be identical;
only the explicit acceptance contract changes. Verify each intended difference
locally before freezing. A scope contrast is not an independent story replicate.

Each case runs once per arm in **both original-first and revision-first order**.
Use one fixed seed, alternate the first arm within matched blocks, and freeze
the full schedule before dispatch. This remains four family clusters, not 48
independent literary judgments. No human needs to reread all variants to count
mechanics; machines prepare the relevant evidence and changes.

## Proposed scoring

Freeze labels, full-source inspection anchors and exact acceptance criteria
before requests are run. Hide them from model inputs. Keep the following outcomes
separate:

1. **Delivery:** strict JSON, exact schema and IDs, valid source-bound evidence,
   terminal status, usage and finish checks. Invalid answers fail the scheduled
   denominator and receive no semantic rescue.
2. **Finding and mapping:** independently correct earlier-event and final-state
   labels; correct mandatory task verdicts; preservation of the genuine craft
   defect under both narrow and broad contracts. Explanations must not contradict
   their own labels, import requirements, or invent source facts.
3. **Aggregation:** declared mandatory failure versus the explicit mandatory
   task statuses, alongside whether those task statuses are themselves correct.
   A consistent aggregate over false premises remains a failure.
4. **Whole report usability:** unchanged C2 group/evidence checks plus grounded
   explanations. A targeted scope gain must not conceal new fulfillment,
   delivery or comparative-premise failures.

Do not prescribe a literary winner for changed prose or reward a smaller diff.
Inspect the contradiction itself using exact narrative referent/time/scope
evidence. Do not equate disagreement about emotional effect with a factual error.
Mask arm/order for operator inspection where practical and disclose that card
wording may reveal the condition. Seal notes before decoding the key. This is
operator factual inspection, not independent blind human preference evidence.

**Proposed screening rule:** retain M1 as promising only if all scheduled cases
finish, it produces at least 22/24 structurally valid reports, introduces no
mapping/mandatory false alarm or missed real contradiction on a paired control
that C2 gets right, and gains complete grounded report recoveries in both orders
on cases spanning at least two distinct families. At least one gain must concern
event/endpoint ownership and one must concern mandatory scope. Also report every
paired regression in other C2 fields; a lost usable C2 report blocks advancement.
These are conservative screening thresholds to freeze, not a significance claim
or a production promotion rule. If C2 already gets the new contrasts right and
M1 adds no recoveries, report no demonstrated benefit rather than expanding the run.

## Proposed budget and stops

- **48 inference attempts total; 24 per arm.** Every dispatched request counts,
  including HTTP errors, invalid answers, unknown usage, timeouts and cancellation.
  No retries, repairs, replacements, follow-up judging calls or budget transfer.
- Retain the archived DeepSeek route and settings: `deepseek-v4.1-flash:cloud`
  through the local daemon; temperature 0.2, top-p 0.95, seed 20261022,
  `think:false`, context 32,000, input reservation 24,000, output maximum 8,000,
  active limit 300 seconds per attempt. These are proposed for continuity;
  exact requests, reservations and model identity checks still need local freeze.
- Maximum token reservation is **1,152,000 input + 384,000 output tokens**;
  maximum active inference reservation is **14,400 seconds**. Record an explicit
  cost reservation at preparation using identified reference rates; actual
  provider billing and unknown usage remain separate. No new price claim is made here.
- Preflight only after live approval. Require the frozen model identity and
  capabilities, a stable daemon version and intact request/source seals. A
  changed daemon baseline requires a documented decision before dispatch;
  a version or model change during execution stops the run.
- Any non-200 response, transport error, timeout, unexpected thinking, incomplete
  finish, length finish, usage overrun or unknown required usage stops all calls.
  Preserve the gateway chain and full reservation; unknown usage stays unknown.
- Freeze an initial **eight-call delivery sentinel**: one event/endpoint case
  and one scope case, both arms/orders. Stop if either arm has zero valid answers,
  or the same structural signature occurs in at least three of its four answers
  across both cases. All malformed reports remain invalid even below this stop.
  Do not adapt the remaining cases or stop based on an attractive semantic result.
- Stop on cancellation, tampering, missing source binding or ledger inconsistency.
  A partial run remains incomplete; unused calls cannot fund another comparison.

## What a result would mean

If M1 improves supported labels in both orders without hiding craft defects,
retain it for a separate confirmation and possible design review. It would not
yet qualify a production reviewer or a writer-edit policy.

If scope labels remain wrong despite correct evidence finding, the next question
would be whether separate per-requirement judgments help; that would be another
experiment, not extra calls added here. If individual task labels are correct but
only aggregates remain wrong, application-owned aggregation merits a separate
implementation decision and tests; rerunning the same semantic pilot would add
little. Delivery failures remain their own issue and are never repaired inside
this comparison.

The nine earlier human ties remain unchanged. Better diagnostic bookkeeping
does not demonstrate better fiction. Later story-quality qualification needs
meaningfully different stories and human ratings of overall feel, flow,
character and story-breaking details, with mechanical evidence prepared in
advance. Production prompts stay unchanged and the canary stays **ON HOLD**.

The next action, if selected, is **local preparation and a reviewable frozen
plan**. This document creates no requests, live approval, execution ledger or
new model evidence.
