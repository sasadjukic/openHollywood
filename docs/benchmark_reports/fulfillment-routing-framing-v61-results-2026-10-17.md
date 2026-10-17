# Critic routing and writer boundary framing: completed comparison

Date: 2026-10-17. **COMPARISON COMPLETE: 42/80 live inference calls. Neither candidate
meets its frozen promising-result criterion.** Production remains prompt 61 /
graph 9 / fulfillment policy 1. **Full workflow canary ON HOLD; NOT STARTED.**

The user approved the [frozen plan](fulfillment-routing-framing-v61-plan-2026-10-17.md),
including complete unpublished prose/context sent to Ollama Cloud through the local
Ollama daemon. Approval binds plan SHA-256
`cf143f6a1ee077a9c8c24b426b90009805b1d9897a517cb2782afdcf7cc4eb37`.
The source commit is `18ca05abba476524d7af38a1266f1b8a6ba57f97`.

## Execution and integrity

| Block | Probes completed | Calls used | Frozen ceiling |
| --- | ---: | ---: | ---: |
| Initial critics | 24 | 26 | 48 |
| Writers | 8 | 8 | 16 |
| Ordinary post-critics | 8 | 8 | 16 |
| **Total** | **40** | **42** | **80** |

Only two initial critic probes needed their one permitted structural retry. No
terminally invalid probe, skipped post-review, transport retry, semantic reroll,
replacement case or extra revision occurred. The writer/post block used 16 of its
nontransferable 32 calls. Unused allowance does not authorize further work.

All 32 static first requests matched the freeze; the dependent post/retry requests
were saved and reserved before dispatch. Reconstructed and replayed **all 40 probes /
42 attempts**, including the two invalid responses, through unchanged ordinary
validators. Reconciled every request, reservation, response hash, outcome and usage
record. Preflight and both phase checks matched the frozen `gemma4:31b-cloud` digest
`c382fbfbc73b6fdd08c8549c23caedc6e62eb09933c65a1fb82dbf3398320a4e`.
Replay and inspection made zero additional inference calls.

Usage: **686,223 input / 51,178 output tokens**, **292.13 active dispatch seconds**.
At the frozen October 8 rates only, the estimate is **USD 0.11654242**. Actual billed
charges remain unknown. This is not a current-price or billed-dollar guarantee.

## A. The route index does not qualify

| Measure | C0 ordinary | C1 route index |
| --- | ---: | ---: |
| First attempt structurally valid | 12/12 | 10/12 |
| Final structurally valid | 12/12 | 12/12 |
| Probes with a routing failure | 0/12 | 2/12 |
| Invalid attempts | 0/12 calls | 2/14 calls |
| Final frozen classification matches | 8/12 | 8/12 |
| Correct raw outcome changes to wrong outcome on retry | 0 | 2 |

Both seeds show the same final classification pattern:

| Case | Expected native outcome | C0 | C1 |
| --- | --- | --- | --- |
| Elena clean | met | met | met |
| Elena separate match | met | **unmet: wrong** | **unmet: wrong** |
| Elena embedded match | met | **unmet: wrong** | **unmet: wrong** |
| Elena genuinely missing decision | unmet | unmet | unmet |
| Elena complete compound outcome | unmet | unmet | unmet |
| Elara embedded entry | met | met | met |

All 24 final turning-point checks and all 24 boundary classifications match the
frozen expectations. The eight mismatches are native outcome attribution errors.
Taking out the journal to check the handwriting establishes Elena's decision;
establishing the forbidden match later does not make that earlier fact absent.
The complete compound outcome really does include the no-match clause, so its
unmet classification is correct. Neither arm loses the clean/missing/compound
classification controls, but neither handles the separate obligation correctly.

The route index fails both parts of its criterion: it does not reduce routing
failures against the concurrent control, and it does not produce 12 supported,
correct final reviews. C0's perfect structural validity is not semantic success.
There is no basis for promoting C1 or interpreting these results as general critic
reliability.

### The two retries recover structure by losing the correct judgment

| C1 embedded Elena probe | First rejected response | Valid second response |
| --- | --- | --- |
| 19301 | Outcome met, but also generic `assignment_violations.anchor=outcome`, outcome conditions and an outcome-linked issue | Removes the duplicate route; changes outcome to unmet and supplies outcome conditions |
| 19303 | Outcome met and a correctly boundary-linked issue, but model-authored `assignment:outcome` conditions despite the met check | Changes outcome to unmet and routes the complaint through outcome/boundary consolidation |

The first validator errors were `duplicate_assignment_check_route` and
`invalid_assignment_repair_conditions`, respectively. The failed raw responses
remain failed evidence; their met claims were never salvaged into a writer source.
The route index was present on both attempts. Ordinary retry construction was
unchanged: structural feedback, no rejected response body, no frozen native statuses.

The resulting native condition ownership becomes legal, while the prose judgment
becomes wrong. This repeats the distinction identified in the
[preceding diagnosis](../handoffs/fulfillment-routing-ending-next-experiment-2026-10-17.md).
It supports investigating obligation attribution and retry stability separately;
it does not justify accepting malformed reviews, adding retries or automatically
pinning unvalidated met judgments.

### Advice and supporting narrative remain separate audit axes

Four clean, four missing-decision and four Elara-control reviews account for 12
of the 16 matching reviews; the four compound reviews account for the rest.
The compound conditions themselves preserve the no-match obligation.
None demands an inconclusive or negative result as the only permitted repair.

Three secondary cautions remain explicit in the private assessment:

- Both C0 compound reviews overclaim that the handwriting match establishes
  acceptance of the card as a genuine warning. The draft establishes the match
  and continuing suspicion, not that additional acceptance. The current no-match
  boundary independently supports the repair.
- C1 compound 19303 says in a support rationale that verification must remain
  “inconclusive.” Its actual mandatory condition simply forbids an established
  match. The broader rationale is a caution, not an extra mandatory repair condition.

Accordingly, the full-review labels are C0: **6 supported, 2 supported with caution,
4 failed attribution**; C1: **7 supported, 1 supported with caution, 4 failed
attribution**. Do not turn the 8/12 classification counts into unqualified
sound-review counts. These cautions do not change the failed C1 decision.

Final raw critic verdicts were four pass, two revise and eighteen reject; ordinary
normalization produced four pass and twenty revise. There was no raw pass on a
known defect. Every generic issue repeated an assignment/boundary finding; no
independent craft issue was reported.

## B. Boundary framing does not improve preservation

All eight writers validate on the first attempt. Full-scene inspection and all
eight ordinary post-reviews agree that the entry defect is repaired and the native
touch, psychic pull and decision remain. All sixteen post native checks and eight
original repair checks are met; all eight boundaries are no-overrun. There is no
writer factual failure to exclude from the four-pair comparison.

Positive evidence was identical within every pair. Source reviews were fixed
before this run; none came from comparison A. Post-critics received the original
feedback/tests and no candidate framing or fulfillment packet.

| Case / seed | W0 ordinary with evidence | W1 boundary framing with the same evidence | W1 pair result |
| --- | --- | --- | --- |
| Separate / 19301 | Deletes only the forbidden entry paragraph | Also replaces the compatible prospective-step sentence with a poised-threshold ending | Loss |
| Separate / 19303 | Deletes only the forbidden entry paragraph | Also replaces the prospective-step sentence with a poised-concrete-edge ending | Loss |
| Embedded / 19301 | Replaces the final composite sentence with a physical poised-state ending | Also reshapes the bracing sentence and adds a new resolve/waiting beat | Loss, with interpretive caution |
| Embedded / 19303 | Retains the prospective first step; removes entry and adds outside/poise wording | Makes the same substantive repair, with slightly shorter poise wording | Tie |

Assistant preservation assessment: **0 wins, 3 losses, 1 tie, 0 mixed**. The frozen
criterion required at least three wins, including one in each case. It is not met.
These are narrow judgments about unnecessary changes relative to the supplied
repair, not blind human literary preferences.

The separate-case contrast is especially clear. Both W0 outputs restore the clean
720-word scene exactly. Both W1 outputs remove the adequate sentence beginning
“The first step would follow as soon as the strap was secure” and substitute a static
poised-state ending. The source already says both boots are outside. This extra
rewrite has no supplied repair need or demonstrated independent craft benefit.
Exact restoration is descriptive evidence of the scope of the edit, not a new
quality gate.

Embedded 19301 needs more care. W1 ends with:

> She braced her free hand on the jamb to carry herself through, her weight shifted
> forward, waiting for the final breath of resolve before she crossed the threshold.

This is a new resolve/hesitation beat in addition to broader editing. It is not an
unambiguous explicit assertion that she has decided, and the full context still
supports her intent to enter. We do not score a factual regression or claim a clear
decision-restatement recurrence from the word “resolve” alone. The primary narrow
preservation judgment is a loss because W1 adds this unsupplied psychological beat
and changes another adequate sentence. A human might prefer its suspense; if that
tradeoff warrants “mixed,” the tally becomes two losses, one tie and one mixed,
still **zero wins**. That preference is unresolved, not silently counted as quality.

At embedded 19303, “poised at the threshold” versus “poised at the edge of the
threshold” is an equivalent minor variation. Fewer words do not make W1 a winner.
Neither candidate needs an explicit decision assertion to pass the ordinary critic.

### Necessary edits inside evidence remain possible

All four embedded writers edit the cited composite sentence to remove forbidden
entry, while retaining the fulfilled meaning. Three retain five of the six original
exact excerpts; W1 embedded 19301 retains four, also changing the bracing sentence.
All four separate writers retain all five source excerpts. These quotation counts
are descriptive: exact quotation retention is neither necessary nor sufficient for
factual preservation.

Across all eight revisions, prose before the final paragraph is unchanged.
Six endings receive wording changes beyond the minimum defect removal. Four of
those are in the embedded cases, where **both arms** edit the ending. W1's reframing
does not eliminate that behavior. There are zero clear new explicit decision
assertions and one ambiguous new resolve beat, reported separately above.

All post-critics pass and report no independent craft issues; their uniformly
positive ratings do not adjudicate this ending preference. Four complete anonymous
original/A/B pairs, full before/after prose and diffs are exported. **Blind human
review remains pending.**

## Decisions and story-quality implications

1. **Do not promote either candidate.** The critic route index fails its structural
   and semantic target. The writer framing produces no preservation win in these
   four pairs. Keep production prompts, schema, validation and normalization fixed.
2. Keep native fact fulfillment, endpoint violations, advice support and structural
   validity distinct in the next diagnosis. A structurally valid false native
   complaint is not a successful gate, and failed raw judgments cannot supply evidence.
3. Retain the embedded necessary-edit result, but do not claim live independent
   craft-in-met-passage qualification. No independent craft repair was exercised.
   Future quality work must allow meaningful improvements to voice, agency, tension
   and dialogue in fulfilled passages; this run authorizes no locked spans or
   added explicit-decision requirements.
4. Use the full anonymous pairs for human preference. Preserve original prose and
   separate assistant preservation judgments from human quality scores. Continue
   complete-story qualification under the accepted rubric, hard gates, full Cloud
   corpus and comparable single-model baseline when separately authorized.

This is two small, isolated comparisons on two story contexts and one recorded
deployment. C1 has no length placebo; W1 bundles three framing fields. The two
writer cases use different saved reviews/evidence, so differences between cases
are not a pure embedding effect. No general causal or literary-quality claim follows.
No additional model calls, prompt tuning or full workflow canary were started.

## Evidence and verification

Private live bundle:
`data/diagnostics/fulfillment-routing-framing-v61-2026-10-17-live/`.

- `requests/`, `reservations/`, `outcomes/`, `probes/`: complete request/response and
  attempt evidence, including both rejected critic responses.
- `audit.json`: exact replay, usage reconciliation, complete raw attempts, normalized
  outputs and evidence catalogs. `assessment.json`: completed assistant semantic
  and prose inspection, pair rationales, cautions and sensitivity reading.
- `inspection/private/`: full originals, revisions, diffs and private A/B order key.
  `inspection/human-pairs/`: four complete anonymous pairs and an unfilled review sheet.
- `verification.json`, `closure.json` and `tracker-snapshot.md`: final seal binding
  this report, local evidence and the tracker state. The preparation report and
  all predecessor evidence remain unchanged.

Reverified the 121 frozen code files and preparation/source seals, and all 42
dispatched requests and response receipts. Both private inspection scripts pass
Ruff lint/format; documentation links and whitespace checks pass. The preparation's
91-test regression result remains historical evidence, not a new test-run claim.
No production/client code changed, so no new application build is claimed.

The comparison itself is complete. Broader qualification remains unfinished:
**Step 19 IN PROGRESS; Step 20 NOT STARTED; canary ON HOLD.**
