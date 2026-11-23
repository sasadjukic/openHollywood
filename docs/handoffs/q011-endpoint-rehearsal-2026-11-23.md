# Q011 rehearsal of the threshold claim

**Grounded uncertainty passed on judgment and evidence. Both definite readings failed on both.** All three authored responses cited the same two plan fields and the same final draft sentence. Each citation resolved to its exact source. The evidence scores turned on what the explanation inferred from those sources. [Separate scores and findings](../../data/diagnostics/q011-rehearsal-2026-11-23/scores.json)

## Claim and evidence

In *The Pristine Lure*, the sole active claim was Gemma’s whole Q011 field from critique v2. It compares the depicted ending of draft v1 with two obligations in Scene Plan v1. The whole-claim gold, `uncertain`, was sealed in the preceding audit. [Source versions, claim and frozen gold](q011-motion-endpoint-audit-2026-11-23.md)

> The achieved state matches the outcome ('drawn to the entrance') and exit state ('stands at the threshold') defined in the scene plan.

The plan assigns attraction to the entrance in `E0233` and standing at the threshold in `E0229`. In the draft’s last sentence, `E0321`, Elias steps past the shoes and moves “toward the dark, open threshold of the monolith, drawn by the silent promise of the thing that waited inside.” That fulfills the attraction. The narration ends on movement toward the threshold and leaves his position open.

| Authored response | Returned judgment | Judgment score | Evidence score | Reason for the evidence score |
| --- | --- | --- | --- | --- |
| Grounded uncertainty | `uncertain` | Pass | Pass | Identifies both assignments, credits the attraction and locates the approach. Allows for either arrival or continued approach at the cut. |
| Arrival inferred from the plan | `supported` | Fail | Fail | Correctly locates the attraction. Treats the plan’s instruction to stand at the threshold as proof that the draft depicts him there. |
| Definite stop short inferred from the cut | `unsupported` | Fail | Fail | Correctly locates the attraction and direction of travel. Adds a physical stop to the final sentence and uses it to declare the assignment contradicted. |

## Verification

The local renderer rebuilt the intake from the registered Elias capture with scorer files inaccessible. It produced B’s unchanged baseline system message, the verbatim Q011 and a neutral brief. Both endpoint bodies contained the same messages, complete draft and exact plan. Only Q011 was eligible in the response schema. Neighboring Elias fields were available as original review context. Elara’s Q016 had no work item. Injecting the expected verdict or the frozen rationale into either packet was detected in all four checks. [Rendered request bodies](../../data/diagnostics/q011-rehearsal-2026-11-23/rendered/)

All three authored finals passed the response mapping and bound to Q011 and its generation-request hash. The evidence worksheet contained the reason and resolved citations. Its decisions were pinned before joining the returned labels to the frozen gold. Flipping only the label in each scoring control flipped its judgment score and preserved its evidence score. The rehearsal made zero live calls. Sol’s performance on this claim remains unmeasured. [Authored finals](../../data/diagnostics/q011-rehearsal-2026-11-23/bound-fixtures.json) · [Evidence decisions](../../data/diagnostics/q011-rehearsal-2026-11-23/evidence-decisions.json)

For local replay, use the repository Python to run `render.py`, `replay.py` and `score.py` in that order from the diagnostic directory. Each checks existing records for byte-for-byte agreement. [Rehearsal files](../../data/diagnostics/q011-rehearsal-2026-11-23/)

All 147 focused tests passed across intake, result binding, work briefs and the saved-review OpenAI fixture adapter. The work-brief tests emitted nine existing Pydantic serialization warnings. The Windows async fixture suite needed local loopback to initialize its event loop. Provider traffic remained disabled. [Regression results](../../data/diagnostics/q011-rehearsal-2026-11-23/verified-regressions.xml)

## Recommended next step

**Prepare a two-case B-only comparison for separate approval.** Keep the verbatim Q011 claim, plan, brief, model and high reasoning setting fixed. Use the authentic ending for one case. For the other, author a separately versioned draft whose only narrative change explicitly places Elias standing at the threshold. Record the control as an authored variation, preserving the original critic’s association with the genuine draft. Check that both packets expose the correct draft consistently wherever the prose, version or citations appear.

Retain the frozen `uncertain` gold for the original and verify prospective `supported` gold against the authored passage before inference. Score judgment and evidence independently. Success requires a grounded pass in both cases, including a citation to the new observation to justify arrival in the control. The proposed ceiling is two input counts before at most two generations, with zero retries. One observation per case would test sensitivity to the decisive draft fact. It would leave repeatability and the literary quality of either ending open. B remains the default and the workflow canary stays on hold.
