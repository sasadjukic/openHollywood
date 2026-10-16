# Fulfillment failures: diagnosis and next bounded experiment

Date: 2026-10-16. **DIAGNOSIS COMPLETE; FOLLOW-UP PROPOSED, NOT PREPARED OR RUN.**

The ordinary critic has two distinct reliability problems: output routing and
requirement attribution. The writer preserved the supplied quotations but still
restated a fulfilled decision outside those quotations. The captured behavior is
clear; the evidence does not establish a unique internal cause or a general harmful
effect of the evidence packet. Keep production unchanged while testing those
questions separately.

This document follows the [completed comparison](../benchmark_reports/production-fulfillment-v61-results-2026-10-16.md)
and [ADR 0037](../adr/0037-durable-writer-fulfillment-handoff.md). It proposes new
work; it does not amend the sealed plan/results or authorize inference. The earlier
72-call authorization ended with that experiment. Its unused allowance is not a
budget for this proposal. The full workflow canary remains excluded.

## 1. What failed at the critic gates

Only one of four writer pairs qualified. These failures must remain separate:

| Failure | Direct evidence | Interpretation |
| --- | --- | --- |
| Invalid repair route | Elara, seed 19101, first attempt authored a `boundary` repair-condition record. | Boundary advice is application-authored. The retry corrected this and qualified. |
| Invalid assignment route | Elara, seed 19103, used `assignment_violations.anchor=exit_state`; the retry kept it and removed its condition record. | Neither response validated. This is an unusable review, not a missing story decision. |
| Assessment length | Elena embedded, seed 19103, first outcome assessment exceeded 600 characters. | The retry fixed structure but retained the disputed semantic judgment. |
| Wrong attribution of a real defect | Both final Elena embedded reviews marked the decision unmet because the draft established a forbidden handwriting match. | The endpoint violation is real, but it does not erase the decision already made during the scene. |

### Output routing is difficult despite a correct rejection

The sent assignment contract contains `exit_state`. The generic-violation schema
allows only `assigned_character_ids`, `location_id` and `scene_id` in these requests.
The instructions say to select a populated assignment anchor, while separate rules
reserve endpoint overruns for `scene_boundary_check` and exclude boundary advice
from `assignment_repair_conditions`. A model must reconcile all three views.

`repair_ref` is a bounded string in the schema, with its applicable values checked
by application code. The recorded cloud requests have `response_schema=null`;
their output schema is included in the user message. Consequently the prompt does
not guarantee legal enum choices or length limits before application validation.
This is a property of the recorded request path, not a claim about every provider.

The seed-19103 retry focuses on `assignment_violations.0.anchor` with the generic
directive “repair this review-response field only.” The full schema remains present,
but the directive does not itself spell out the allowed values or boundary route.
The returned JSON keeps the invalid anchor. Repair-condition rendering runs before
anchor validation, so the newly missing condition record becomes the next reported
error. That changed error is not evidence that the original anchor was repaired.

The application correctly refused these responses. Do not salvage their met checks,
silently reroute findings, loosen validation, or grant more retries to get eligibility.
An explicit route map or more informative retry directive is a possible later
intervention, not an implemented fix or a proven explanation of model behavior.

### Requirement attribution failed in the raw judgment

The clean and embedded Elena cases contain the same purposeful action:

> She pulled her old journal from the desk drawer and laid it beside the card to check whether the handwriting was her own.

The embedded version appends the definitive match in that same sentence. Both
critics accept the clean action as a decision. Both embedded critics cite the
compound excerpt for the outcome and boundary, yet mark the outcome unmet. One
explains that the scene proceeds beyond the decision; the other also demands a
specific decision-making process. The outcome explicitly says the decision occurs
“During this scene.” Its separate exit state prohibits establishing a match.

Thus the failure was not missing draft evidence, packet extraction, or normalization
changing a met result. It was the model treating endpoint compliance as part of the
event requirement, with an additional explicitness demand in one response.

The prompt already says to assess obligations independently and accept intentional
actions as decisions. It also stresses the whole draft, every applicable condition,
and completing the boundary assessment before scoring. The requirement-scope view
lists exit state among the outcome's companion requirements; exit state is advisory
there, while advancement beyond the endpoint is blocking in the boundary contract.
Those overlapping representations are plausible contributors to attribution errors,
not proof of which instruction caused them. A separate exit-state defect and a
failed condition inside the outcome itself must remain distinguishable.

The earlier [scope clarification](../benchmark_reports/critic-fulfillment-scope-v59-2026-10-15.md)
already failed to improve this distinction: 0/4 in each arm. The
[failed-clause diagnostic](../benchmark_reports/critic-failed-clause-v59-2026-10-15.md)
improved it to 3/4 but still allowed an unsupported contradiction claim. Neither
justifies adding another paragraph blindly or promoting diagnostic semantics into
ordinary production. Also, the latest run confounded story and defect placement:
Elara's defect was separate; Elena's was embedded. It did not isolate that factor.

## 2. Why the evidence arm could still restate the decision

The eligible Elara requests differed only by the optional fulfillment packet. The
current-context writer deleted the forbidden entry sentence and restored the clean
720-word scene. The evidence writer removed entry, but replaced the final clean
sentence with:

> Both boots remained outside in the daylight, but her resolve was fixed; she would enter.

This adds a verbal declaration to an already sufficient action-based decision.
No independent craft finding requested it. There are four relevant observations:

1. **The policy arrived intact.** It explicitly prohibits restatement merely to
   emphasize fulfillment. The global revision contract also preserves unrelated
   prose. There is no evidence of a dropped packet or lost instruction.
2. **The citations did not cover the edited sentence.** The packet cited the
   stroller-as-bridge sentence and the hand braced on the jamb, plus three turning
   point excerpts. All five survived. The subsequent sentence about securing the
   strap, taking the first step and keeping both boots outside was uncited and changed.
   Citation retention measures a subset of the prose; it cannot prove restraint.
   This does not make uncited text freely editable under the global contract.
3. **Positive and negative context frame the outcome differently.** The packet
   declares the decision met. The application presents the endpoint blocker under
   `scene_assignment:outcome`, with advice to “Restore the current scene's planned
   outcome and exit state.” Repeating the requirement and assessment may make a
   declaration of resolve more salient, while that blocker may encourage rewriting
   the nearby ending. These are hypotheses. Both writer arms received the same
   negative advice, so that advice alone cannot explain the paired difference.
4. **Post-pass is insensitive to this preservation loss.** The post-critic accepts
   the current arm's indirect decision and cites the evidence arm's new explicit
   resolve. Both repair the boundary. A pass establishes neither minimal editing
   nor better prose; the direct full-text diff is necessary.

The [earlier positive writer trial](../benchmark_reports/writer-fulfilled-evidence-v59-2026-10-15.md)
was not an identical replication. Its writer used revision 2 with seven input
artifacts and three repair tests, including historical missing-touch and
missing-decision complaints. The latest writer used revision 1 with five artifacts
and only the current boundary test. The old positive assessment and citations also
differed: its outcome included the torch sentence as a third citation. **Neither
packet cited the changed final clean sentence.** System text and preservation policy
were identical. These differences prevent attributing the reversal to production
integration or citation coverage alone.

Earlier [endpoint-only advice](../benchmark_reports/writer-boundary-advice-v59-2026-10-15.md)
also yielded 0/2 exact restorations in both arms. Narrowing that wording alone is
already an unsuccessful intervention in its tested context.

One current pair at writer temperature 0.85 cannot distinguish a repeatable packet
effect from response variability. A shared seed is a useful control, not a promise
of identical behavior for different prompts. The best supported diagnosis is a
failure to preserve the whole successful passage despite correct positive evidence;
the model's reason for that choice remains uncertain. The four unmet controls
worked, but their evidence-only design cannot measure treatment effects on broader
ending edits. The embedded necessary-edit exception was not exercised live.

## 3. Recommended next experiment: fixed-contract contrasts and writer replication

**Question:** Does defect placement change ordinary critic attribution, and does
the evidence packet repeatedly increase restatement with one fixed valid review?
This is diagnosis, not a candidate prompt rollout. Keep prompt 61, graph 9,
handoff policy 1, validators, repair advice and retry policy unchanged.

### Step A — Prepare and freeze locally, before inference

Create a new diagnostic bundle; never edit the sealed sources. Reconstruct and
hash the full contexts, artifact lineage, requests, expected labels, sampling,
dispatch order, dependency rules and scoring sheet. Replay saved responses and
verify the writer pair differs only by the fulfillment field at each seed. Exercise
the call ledger, one structural retry, permanent failure, skipped post-review,
unknown outcome and replay using a fake gateway. Present that manifest for approval
before live execution. This document is not that completed freeze.

Retain the complete benchmark constraints, Bible, Blueprint and future-scene context.
Synthetic plan edits must agree in the Blueprint and standalone Scene Plan, with
new diagnostic identities and consistent Bible references. They never amend canon.

### Step B — Twenty ordinary critic probes

Use both story contexts at new seeds **19201 and 19203**. Prepare these five
conditions for each story, always retaining the fulfilled turning point:

| Condition | Outcome expected | Boundary expected | Purpose |
| --- | --- | --- | --- |
| Clean indirect decision | Met | No overrun | Matched positive baseline |
| Same decision, forbidden result in a separate sentence | Met | Overrun | Separate event from endpoint |
| Same decision, forbidden result in a compound sentence | Met | Overrun | Isolate sentence/excerpt grouping |
| Explicitly unresolved decision, no forbidden result | Unmet | No overrun | Reject a genuinely absent decision |
| Embedded result, outcome itself also requires no result at scene end | Unmet | Overrun | Enforce the complete compound outcome |

Concrete construction:

- Elara clean and separate cases reuse the frozen v61 texts. For embedded entry,
  replace only the separator between the last clean sentence and “She stepped
  across the sill and entered the building.” with a semicolon and lower-case “she”.
  Preserve the action order. For missing decision, replace the complete final clean
  paragraph with: “She looked from the passage to the path back to the road. The
  pull from the building intensified, but she could not decide whether to enter or
  walk away. She stayed at the threshold, both boots outside in the daylight, the
  choice unresolved.” Keep the earlier touch and pull unchanged.
- Elena clean, embedded and missing-decision cases reuse their frozen v61 texts.
  For the separate match, split “; after comparing them,” into “. After comparing
  them,” at the same position. No action is added, removed or reordered.
- The last row reuses each embedded draft but changes only its assigned outcome
  and matching Blueprint copy. Elara: “During this scene, Elara decides to enter
  the windowless building, and at scene end she has not crossed the sill.” Elena:
  “During this scene, Elena decides to verify the handwriting, and no handwriting
  match is established by the end of this scene.” The separate exit state remains.
  These controls prevent a future blanket rule from declaring an entire compound
  requirement met merely because its decision clause holds.

Run all twenty planned probes regardless of semantic results. Do not require a
particular excerpt selection to keep a critic result: record sentence grouping and
actual citations, including whether they overlap. Existing validation remains in
force. Distinguish raw semantic judgments, structural failures, retry recoveries,
rendered advice and normalized verdicts. No semantic rerolls or replacement cases.

### Step C — Six writers and six ordinary post-critics, independent of Step B gates

Use the already successful v61 `s19101-elara-separate-initial` review, its exact
draft/context and the saved current/evidence writer requests. Verify and replay that
source; do not generate another source review or substitute a failed one. This is
explicit reuse of a fixed validated experimental input, not a production fallback.

Run current context versus the unchanged production evidence packet at writer seeds
**19201, 19203 and 19205**, keeping source artifacts and feedback fixed. Alternate
order: current/evidence, evidence/current, current/evidence. Each writer produces
one revision, followed by an ordinary critic at that pair's seed using unchanged
feedback and production post-review construction. Save the dependent request before
dispatch. If a writer remains structurally invalid, skip its post-review, retain the
failure and do not replace the pair. Step B misclassifications do not suppress these
writer trials; an integrity or provider failure stops the experiment globally.

This isolates repeatability from critic eligibility and review-history variation.
It does not isolate packet assessment prose from quotation granularity or identify
the optimal handoff. Such ablations would require a separate single-variable plan.

### Step D — Inspect and decide without automatic promotion

For critics, report first-attempt and final validity separately. The strict
classification target is 4/4 clean positives, 8/8 event-plus-overrun distinctions,
4/4 missing-decision detections and 4/4 complete-outcome detections, with all
turning points met. Correct statuses with unsupported advice or a raw pass on a real
defect do not count as a sound review. Report denominators including invalid probes.

Within each story/seed, compare separate versus embedded errors. Errors only in the
embedded condition implicate grouping in that context; errors in both suggest a
broader attribution problem. Divergent stories remain evidence of limited transfer.
Terminal controls must remain unmet, including when the event occurred. Recurrent
invalid routes motivate a separate route/schema/retry intervention, not extra calls.

For each writer, inspect the complete original, revision and diff. Score factual
repair, fulfilled facts, redundant restatement, changed uncited prose, unnecessary
ending changes and independent craft feedback separately. Report exact clean
restoration only for this controlled repair, plus paired wins/ties/losses. Prelabel
the existing indirect decision and forbidden entry before seeing outputs. Prepare
randomized anonymous full-text pairs for human review of voice, tension, agency and
naturalness; mark human review pending until it actually happens. An assistant
inspection is not a blind human preference result.

If at least two of three evidence arms introduce avoidable restatement absent from
their controls, treat it as recurrence warranting a handoff ablation, not proof of
a general causal effect. If controls also restate, investigate revision behavior
shared by both arms. If neither does, record non-reproduction. Any evidence benefit
must coexist with correct repairs and preserved facts. Ties or mixed results do not
justify claiming a preservation benefit. None of these outcomes authorizes canary,
prompt promotion or completion of Step 19.

### Proposed budget and stop rules

- **32 planned probes; 64-call absolute ceiling**, including at most one existing
  structural retry per probe: 20 critics + 6 writers + 6 post-critics. This is a new
  proposed allowance, not the remainder of the prior 72-call approval.
- Same recorded `gemma4:31b-cloud` deployment/digest, critic temperature 0.2,
  writer temperature 0.85, top-p 0.95, thinking disabled. A changed model identity
  stops preparation/execution for review; it is not silently substituted.
- Per attempt: 24,000 input / 8,000 output tokens and 900 seconds. Aggregate
  reserved maxima: **1,536,000 input / 512,000 output tokens**, and 57,600 seconds
  of active calls. Existing application cost admission remains; actual charges
  are unknown. At the historical October 8 rates only, the ceiling is USD 0.41984;
  this is not a current price quotation or a guaranteed billed-dollar cap.
- Reserve and hash every attempt before dispatch, including failure/cancellation
  and unknown outcomes. Calls sequential; no transport retries, semantic rerolls,
  replacement cases, extra revisions, continuity/adjudication calls or canon writes.
  Stop on integrity, budget, model-identity, authentication or transport failure.
  Unused slots are never reassigned. A third attempt is forbidden.

## 4. Preserve the path to better stories

The objective is reliable repair with room for artistic improvement. Preserve
fulfilled **meaning** while allowing a justified edit to its expression. Do not
turn quotations into locked spans, force explicit declarations of decisions,
demote real craft defects, or treat every advisory story detail as a hard blocker.
The necessary-edit exception and ordinary craft channel remain intact.

This next diagnostic still does not exercise an ordinary-critic-sourced craft repair
inside a fulfilled passage. Before promoting any later handoff change, qualification
must include that case, the embedded boundary repair, genuine unmet controls and
clean prose that should be left alone. A small diff is useful evidence of restraint
only when no meaningful repair or craft improvement requires more.

The [canonical rubric](../../open_hollywood_bible/product_contract_and_benchmarks.md)
gives continuity and constraint adherence 5% of its weighted quality score, alongside
separate hard gates. Voice, character, dialogue, originality, structure, emotion and
pacing still need blind human evaluation on complete stories against a comparable
single-model baseline. These scene probes cannot replace that work or justify a
system that produces more explicit, repetitive prose merely to make critics pass.

## 5. Verification and status

Inspection uses the exact saved requests, raw failure/success responses, full writer
diffs and production contract/validation code at the current documentation commit
`ee7bbb8`. Production implementation remains the frozen `c1bacab638e91dadfd69016ac9226b4885e0f10f`
baseline. Verification passed all **280 closure/hash checks**, including the 252
live evidence files, preparation files/closure, operator records and sealed reports.
The frozen verifier also reconstructed the twelve prepared requests, checked the
implementation/cases and verified 483 historical source files. All seven local
document links resolve, and the repository diff check passes. No historical result
is edited to agree with this interpretation.

Only this diagnosis/proposal and the tracker are changed. No new inference, prompt,
schema, runtime, canonical artifact or canary change is made. Relevant verification
is evidence integrity, frozen-request reconstruction, documentation links and diff
checks; no new application test/build result is claimed for a documentation-only
change. **Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**
