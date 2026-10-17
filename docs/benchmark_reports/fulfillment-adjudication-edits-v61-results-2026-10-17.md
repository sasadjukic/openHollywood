# Adjudication and exact edits: completed comparison

Date: 2026-10-17. **COMPLETE: 45/100 live inference calls. J1 meets the frozen
diagnostic judgment criterion; E1 does not meet the writer criterion. Neither craft
source qualifies, so craft editing remains untested.** Production remains prompt 61 /
graph 9 / fulfillment policy 1. **Full workflow canary ON HOLD; NOT STARTED.**

The user approved the [frozen plan](fulfillment-adjudication-edits-v61-plan-2026-10-17.md)
and sending complete unpublished prose/context to Ollama Cloud through the local
daemon. Approval binds plan SHA-256
`765fd0499eb2ddb87f97e32cdfcb65b338b544c9be2e452f34bc16e4da0368a2`,
the 100-call ceiling and canary exclusion. Source checkout:
`4a6c9bdf0474e2f59fdc1c0c52d378ac1cd55242`.

## Execution and verification

| Block | Completed probes | Calls used | Frozen ceiling |
| --- | ---: | ---: | ---: |
| A: ordinary and adjudication-only critics | 24 | 27 | 48 |
| B: fixed writers and ordinary post-reviews | 16 | 16 | 32 |
| C: ordinary craft-source critics | 2 | 2 | 20 |
| **Total** | **42** | **45** | **100** |

Eight conditional craft slots were skipped: four writers and four posts. All 50
scheduled slots remain accounted for. There were three structural retries, five
invalid responses and two terminally invalid probes, all in J0. All eight writers,
eight posts and both craft-source critics validated on their first attempts.
No semantic reroll, replacement, extra writer revision or transport retry occurred.
Unused and skipped allowances do not authorize further calls.

All **34 static requests** matched the freeze. Every actual request was saved and
reserved before dispatch. Offline reconciliation reconstructed and replayed all
**42 completed probes / 45 attempts**, including rejected responses, and reconciled
requests, reservations, response hashes, outcomes, usage and dependent skips.
The five identity checks—preflight plus four phases—matched the frozen
`gemma4:31b-cloud` digest:
`c382fbfbc73b6fdd08c8549c23caedc6e62eb09933c65a1fb82dbf3398320a4e`.
The craft-writer phase recorded skips and made zero inference calls.

Usage was **696,412 input / 45,716 output tokens**, with **224.15 active dispatch
seconds**. At the frozen October 8 rates, the historical estimate is
**USD 0.11578408**. Actual billed charges are unknown; this is not a current-price
or billed-dollar guarantee. All block, stage, token and time ceilings were respected.

## A. Adjudication-only meets its narrow criterion

| Measure | J0 ordinary | J1 adjudication-only |
| --- | ---: | ---: |
| First attempt structurally valid | 9/12 | 12/12 |
| Final structurally valid | 10/12 | 12/12 |
| First valid, correct shared tuple | 7/12 | 12/12 |
| Final valid, supported shared tuple | 8/12 | 12/12 |
| Invalid attempts | 5/15 calls | 0/12 calls |
| Extractable correct raw tuple on first attempt | 9/12 | 12/12 |
| Extractable correct raw tuple on final attempt | 10/12 | 12/12 |

Raw tuples in rejected reviews remain invalid evidence; they were not salvaged as
production critiques or writer sources. The smaller J1 schema's validity is not
evidence that full-review routing or craft assessment has been solved.

Both seeds had the same final pattern:

| Case | Expected outcome / boundary | J0 final | J1 final |
| --- | --- | --- | --- |
| Elena clean | met / no overrun | Correct | Correct |
| Elena separate match | met / overrun | **Wrong: outcome unmet** | Correct |
| Elena embedded match | met / overrun | **Invalid**; raw met / overrun | Correct |
| Elena missing decision | unmet / no overrun | Correct | Correct |
| Elena compound outcome | unmet / overrun | Correct | Correct |
| Elara embedded entry | met / overrun | Correct | Correct |

J1 correctly preserves the distinction this experiment targeted. Retrieving the
journal establishes Elena's decision; a later confirmed match violates the separate
endpoint without undoing that decision. Where the no-match requirement belongs to
the compound outcome itself, J1 correctly marks the complete outcome unmet. It also
retains the missing-decision and clean controls. Its cited passages support these
judgments in the full prose. All extractable turning-point and boundary statuses
match expectations in both arms; the native outcome and ordinary output contracts
account for the failures. Missing-turn detection was not tested.

### Ordinary failures and retry behavior

| J0 probe | First attempt | Permitted retry |
| --- | --- | --- |
| 19401 Elena embedded | Wrong outcome unmet; malformed condition uses singular `source_ref` and `exact_quote` outside `source_refs` | Correct raw met, but duplicate generic outcome violation; terminally invalid |
| 19403 Elena embedded | Correct raw met, but outcome-owned repair conditions without an unmet outcome | Correct raw met, but unsupported `exit_state` generic anchor and stale outcome issue link; terminally invalid |
| 19401 Elena compound | Correct unmet judgment, but non-null recommendation on a linked assignment issue | Valid correct review with null linked recommendation |

The second embedded attempt at 19401 improves the raw judgment while still failing
the output contract. At 19403 the correct raw judgment survives both failed attempts.
Thus this batch does **not** reproduce the previous comparison's met-to-unmet retry
drift. The two separate-match probes are structurally valid but wrong immediately;
they do not receive semantic retries.

J0 advice remains a separate audit axis. The 19401 separate-match condition demands
no definitive conclusion, which is broader than the actual no-match constraint:
a negative comparison could satisfy that constraint. Several ordinary next-scene
comparisons also equate confirming handwriting with accepting the warning as genuine;
that additional acceptance is not established by the draft. The current-endpoint
overrun is independently supported. Clean, missing-decision, compound and Elara
reviews have supported core judgments and repair requirements; no independent craft
finding appears in these initial ordinary reviews.

**Decision:** J1 meets 12/12 supported final shared tuples and improves over J0's
8/12, with all controls retained. This supports further investigation of separating
adjudication from the complete review task. It does not isolate routing removal from
removing scoring/craft/advice tasks, schema simplification or shorter output. J1 has
no production verdict, repair advice or craft assessment and remains ineligible as
a production Critique or writer source. No architecture or prompt change is made.

## B. Exact edits work mechanically but do not qualify for preservation

Both arms repaired all four fixed cases, retained the fulfilled facts and passed all
four ordinary post-reviews. Every post returned raw `pass`, native met/met, no overrun
and all original repair tests met, with no new issues. Full-prose inspection supports
those factual results. All four E1 patches applied atomically on their first attempt:
two spans for each separate-entry case, one for each embedded-entry case. No fuzzy
matching, fallback or automatic semantic repair was used.

All eight revisions preserve the prose before the final main paragraph. E0 restores
the clean scene exactly once; E1 never does. Seven revisions change the ending beyond
removing completed entry. These counts describe preservation; they are not literary
scores or a requirement to make the smallest possible edit.

| Seed / case | E0 full-scene output | E1 exact edits | Operator preservation comparison for E1 |
| --- | --- | --- | --- |
| 19401 separate | Deletes only the separate entry paragraph | Also replaces purposeful bracing with a hammering-heart sensation | **Loss** |
| 19401 embedded | Keeps bracing and the pending step; mildly rephrases the outside stance | Keeps those facts but repeats bracing/intention immediately after the existing bracing sentence | **Small loss**; benign-rephrasing sensitivity: tie |
| 19403 separate | Adds a heartbeat wait and commitment to the first step | Avoids that wait/commitment, but replaces both preparatory sentences with weight shifting/readiness | **Mixed** |
| 19403 embedded | Retains bracing purpose but drops the conditional future step and adds a static gaze | Keeps the future step but replaces bracing purpose with cold-concrete sensation and expands the stance | **Mixed** |

The primary operator assessment is **0 wins, 2 losses, 2 mixed**. Treating the small
19401 embedded difference as benign gives **0 wins, 1 loss, 1 tie, 2 mixed**. Even a
favorable reading of both mixed pairs leaves the clear separate-case loss and the
missing craft controls. The frozen requirement of at least two wins including an
embedded win, no losses, four factual repairs and both craft controls is not met.

The heartbeat in E1's first separate case is a new bodily tension beat, not an
explicit new decision. E1's repeated bracing is physical/intention repetition, also
not a new explicit decision assertion. E0's 19403 separate ending adds a wait before
commitment, despite the already fulfilled decision; that extra psychological beat
is distinguishable from a completed crossing, which the revision does not establish.
This distinction prevents labeling every ending change as the same restatement bug.

The mixed pairs expose real tradeoffs for future quality work. E1 can retain forward
motion that E0 drops, while adding tactile description or replacing existing purpose.
A reader might prefer some of those choices. No human preference is inferred from
this assistant assessment, patch size, exact restoration or the uniformly favorable
post-critic prose scores.

**Decision:** do not promote E1. Exact location and atomic application make edits
auditable, but do not make the model choose only changes warranted by the supplied
repair. The candidate still rewrites adjacent fulfilled expression. This is a
representation experiment on two sources and two seeds, not proof that all patch
interfaces harm preservation or that those additions are universally bad prose.

## C. Both ordinary craft sources are ineligible

Both complete craft scenes contain the adjacent duplicate of the bracing sentence.
At both seeds the ordinary critic correctly identifies native met/met and the entry
overrun, but reports **only the boundary issue**, assigns prose quality **5/5**, and
provides no independent repetition repair. Consequently neither source passes the
first craft-specific gate. Both also cite only the first repeated sentence in native
positive evidence (`draft_evidence_0050_...`); they do not cover both repeated ranges
(`0050` and `0051`) required by the frozen control.

The primary failure is the absent independent craft finding, not solely the strict
overlap requirement. Relaxing overlap after seeing results would still not supply
the missing ordinary craft feedback. No source was edited, manufactured, replaced
or rerolled. Eight dependent slots were skipped as frozen. **Zero of two craft pairs
qualified; no craft writer or craft post call ran.** This tests the source gate and
reveals a craft-detection miss; it does not establish either writer's ability or
inability to repair craft inside fulfilled evidence.

This is one deliberately obvious repetition stress case at two seeds. It is not a
general repetition policy or a complete measure of critic literary judgment. The
miss does show why successful constraint adjudication and high critic ratings cannot
stand in for quality-sensitive review.

## Evidence, decisions and remaining work

Private evidence is saved under:
`data/diagnostics/fulfillment-adjudication-edits-v61-2026-10-17-live/`.
It includes every raw attempt, actual request, reservation and outcome; phase/model
receipts; gates and skips; `audit.json`; `assessment.json`; complete original/revised
prose and diffs; and the human-review export with its private order key. Four available
anonymous pairs are exported from six scheduled pair slots; both unavailable craft
pairs remain recorded. The human review sheet is **pending and empty**.

The final closure binds these files, the unchanged preparation bundle and approval,
production dependency hashes, this report and the tracker snapshot. Frozen plan and
historical reports are preserved. Offline checks include all-attempt replay, static
request equality, atomic patch replay, source/plan seals, complete denominator and
budget reconciliation, public documentation links/whitespace and Ruff lint/format
for the two new inspection scripts. The preparation's **75 focused regressions** and
repository lint/type checks remain recorded against unchanged frozen code; they are
not misreported as new live-run tests. No application/client code changed, so frontend
tests/build and additional application regressions were not rerun for this result-only
change. An initial sandboxed offline verification stalled and was interrupted before
approval creation; the successful offline verification and approved execution used
the permitted local runtime. No model dispatch was lost or repeated because of that.

1. Retain J1 as promising diagnostic evidence only. Any future production design must
   preserve supported repair advice, independent craft review and exact artifact lineage.
2. Retain E1 as a mechanically successful but unqualified preservation candidate.
   Do not add protected spans, a diff quota or more preservation reminders on the
   strength of this run. Changes inside fulfilled passages can be necessary and useful.
3. Keep the missing craft-in-fulfilled-evidence coverage explicit. Future experiments
   need a new bounded plan and approval; no remaining allowance is spent now.
4. Keep human review pending. Later story-quality qualification still uses the
   [accepted weighted rubric and hard gates](../../open_hollywood_bible/product_contract_and_benchmarks.md),
   the full intended Cloud corpus and a comparable single-model baseline. Continuity
   and constraint adherence account for only 5% of that rubric. This run establishes
   neither literary superiority nor full-story workflow recovery.

Production prompts, graph, policy, validators, runtime and canonical artifacts are
unchanged. **Step 19 IN PROGRESS; Step 20 NOT STARTED; full workflow canary ON HOLD.**
