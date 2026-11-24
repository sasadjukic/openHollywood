# The Wading Path · Sol-high Q011 exact-observation results

**Keep B as the default. The frozen decision is `hold_controls`.** Repeating the exact closing paragraphs earned an evidence point on the original ending in this pair. Both arms still judged the original `unsupported`, and both missed the same evidence requirement on the measured-stop control. The explicit-arrival pair and the Q008 narration control passed both scores. [Approved comparison](wading-path-sol-high-observations-freeze-2026-11-24.md) · [Sealed scores](../../data/diagnostics/wading-path-observations-results-2026-11-24/scores.json)

## Judgment and evidence

B received the ordinary brief. O received the same request with the version-bound closing paragraphs repeated. Judgment earns one point for the frozen whole-claim label. Evidence earns one point for adequately explaining the cited facts as they bear on the claim.

| Field and ending | Arm | Gold | Returned | Judgment / 1 | Evidence / 1 | Evidence finding |
| --- | --- | --- | --- | ---: | ---: | --- |
| Q011 original | B | uncertain | unsupported | 0 | 0 | Located entry, gaze and housing, then said no subsequent movement brings the pair there and treated fulfillment as inaccurate. The prose leaves their position open. |
| Q011 original | O | uncertain | unsupported | 0 | 1 | Located the housing relative to the pair’s “last narrated position” and explained why its identity as a barrier fails to establish either physical endpoint. |
| Q011 explicit arrival | B | supported | supported | 1 | 1 | Used the authored final sentence to establish both people reached the housing and stood before it. |
| Q011 explicit arrival | O | supported | supported | 1 | 1 | Matched both plan requirements to the selected draft’s explicit arrival and standing position. |
| Q011 measured stop | B | unsupported | unsupported | 1 | 0 | Found the persistent three-stride gap, then counted it as fulfillment of standing before the barrier. |
| Q011 measured stop | O | unsupported | unsupported | 1 | 0 | Found the same gap and argued that standing before the barrier requires no specified distance or contact. This conflicts with the frozen exit-position criterion. |
| Q008 original, narrated arrival | B | unsupported | unsupported | 1 | 1 | Traced entry and gaze through the final line. The housing is described at the passage end. The account omits an arrival there. |

**Original endpoint.** The same B request scored 0/1 in the preceding live comparison and 0/0 here. There was no baseline recovery. The current B answer calls entry with the barrier ahead the pair’s endpoint and rejects fulfillment. O limits the position claim to what the narration last places and explains the evidentiary gap, yet selects the contradiction label. The paired gain was on evidence alone. One response per arm and the change on the byte-identical B repeat limit attribution of that gain to the added observations. [Prior B result](wading-path-sol-high-be-results-2026-11-24.md) · [Verbatim explanations on the masked worksheet](../../data/diagnostics/wading-path-observations-results-2026-11-24/evidence-worksheet.json)

**Measured stop.** Both arms cited the correct plan fields and the selected draft. Both quoted “three full strides short” and recognized that the pair stayed there. They obtained the correct whole-claim label by treating reaching as the failed requirement and standing before the barrier as fulfilled. Under the frozen gold, the measured separation contradicts the **exit position at the cut**. That alone defeats the conjunction. Whether the pair ever reached the housing earlier remains open. O’s explanation makes the difference in interpretation explicit. It read “before” as allowing an unspecified distance. Supplying the passage twice left that reading intact. This is a limit on interpreting the spatial requirement in this test. It supplies no editorial reason to change the original story. [Per-case gold](../../data/diagnostics/wading-path-sol-high-observations-2026-11-24/gold.json) · [Resolved citations and draft versions](../../data/diagnostics/wading-path-observations-results-2026-11-24/cited-locations.json)

## All 14 slots

The runner sent seven counts before seven generations, with zero retries. All 14 endpoints returned HTTP 200. Every count was positive and in budget. Each generation returned `gpt-6.1-sol`, bound to its selected claim, matched the input tokens reported by its count and qualified for both scores. Reasoning tokens are included in the output column.

| Slot | Endpoint | Field and arm | Counted or used input | Output | Reasoning | Seconds |
| ---: | --- | --- | ---: | ---: | ---: | ---: |
| 1 | Count | Original · B | 91,632 | — | — | 11.19 |
| 2 | Count | Arrival · O | 92,055 | — | — | 9.31 |
| 3 | Count | Measured stop · B | 91,715 | — | — | 10.28 |
| 4 | Count | Q008 narration · B | 91,711 | — | — | 10.07 |
| 5 | Count | Original · O | 91,932 | — | — | 10.90 |
| 6 | Count | Arrival · B | 91,693 | — | — | 9.83 |
| 7 | Count | Measured stop · O | 92,097 | — | — | 8.57 |
| 8 | Generation | Original · B | 91,632 | 725 | 510 | 29.94 |
| 9 | Generation | Arrival · O | 92,055 | 356 | 199 | 19.59 |
| 10 | Generation | Measured stop · B | 91,715 | 568 | 371 | 23.87 |
| 11 | Generation | Q008 narration · B | 91,711 | 580 | 382 | 24.87 |
| 12 | Generation | Original · O | 91,932 | 639 | 408 | 27.21 |
| 13 | Generation | Arrival · B | 91,693 | 445 | 272 | 20.49 |
| 14 | Generation | Measured stop · O | 92,097 | 538 | 314 | 26.17 |

Generations used **642,835 input tokens and 3,851 output tokens**, including 2,456 reasoning tokens. OpenAI reported zero cached input tokens. The summed endpoint times were 70.16 seconds for counts and 172.13 seconds for generations. Generation cost at the frozen catalog rates was an estimated **$1.64560** against the $3.08672 ceiling. [Slot inspection and terminal hashes](../../data/diagnostics/wading-path-observations-results-2026-11-24/slot-inspection.json) · [Original single-use journal](../../data/diagnostics/wading-path-sol-high-observations-2026-11-24/output)

## Verification

Offline readback verified the approval manifest, exact request bodies and the intent and terminal chain. All seven explanations were reviewed with the arm, dispatch order and returned label masked. The local scorer sealed the evidence decisions before joining the returned labels to gold. The evidence seal is `7c6704098ea7376b693ea29f7f4e0e3ed23b89ff559ef024f079842811b8f5ed`. Production prompts are unchanged, live calls are paused and the full workflow canary remains on hold. [Journal audit](../../data/diagnostics/wading-path-observations-results-2026-11-24/audit.json) · [Sealed evidence decisions](../../data/diagnostics/wading-path-sol-high-observations-2026-11-24/sealed-evidence-decisions.json)
