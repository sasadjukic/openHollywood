# The Wading Path · Sol-high B visit and cut-position results

**Five of six assessments passed both judgment and evidence.** Sol correctly located both people at the cut in all three drafts. It also recognized when the prose expressly ruled out a visit over the entire scene. The remaining failure was S1, where the prose records a final stop and leaves an earlier visit open. Sol returned `unsupported` on both versions of the visit claim, although their gold labels differ. The frozen decision is **`hold_claim_scope`**. [Approved plan](wading-path-visit-position-sol-high-freeze-2026-11-25.md) · [Scorer output](../../data/diagnostics/wading-path-visit-position-results-2026-11-25/scores.json)

## Judgment and evidence by case

| Case | Draft | Claim | Gold | Sol returned | Judgment / 1 | Evidence / 1 |
| --- | --- | --- | --- | --- | ---: | ---: |
| S1-B | Measured stop | Visit during scene | Uncertain | Unsupported | 0 | 0 |
| X1-B | Full-scene exclusion | Visit during scene | Unsupported | Unsupported | 1 | 1 |
| S2-B | Measured stop | At housing at cut | Unsupported | Unsupported | 1 | 1 |
| X2-B | Full-scene exclusion | At housing at cut | Unsupported | Unsupported | 1 | 1 |
| A1-B | Explicit arrival | Visit during scene | Supported | Supported | 1 | 1 |
| A2-B | Explicit arrival | At housing at cut | Supported | Supported | 1 | 1 |

**Visit during the scene.** S1 cited the correct measured-stop draft (`2f9e80a0-29b4-579f-8075-b6e064788b24`), distinguished entry into the plenum from reaching the housing, and accurately located the final gap. Its reason then said, “The full sequence shows no earlier arrival followed by retreat.” The absence of a narrated visit cannot exclude one throughout scene four. The final paragraph (4806–4945) establishes where the approach ends. S1 supplied no evidence covering the earlier interval and treated the claim as contradicted. Both scores therefore failed under the frozen criteria. [Masked explanations](../../data/diagnostics/wading-path-visit-position-results-2026-11-25/evidence-sheet.json) · [Evidence requirements](../../data/diagnostics/wading-path-sol-high-visit-position-2026-11-25/evidence-criteria.json)

X1 cited the exclusion draft (`4da86d35-9337-54d8-896b-c212ba05516c`). Its explanation identified the added final paragraph (4947–5149), which names both people and sets a minimum distance of three full strides from the opening huddle through the cut. That passage excludes an earlier visit. Sol earned the evidence point by locating and using the retrospective. The added sentence changed the evidence in Sol’s explanation, while the returned label stayed `unsupported`. [Resolved citations](../../data/diagnostics/wading-path-visit-position-results-2026-11-25/cited-locations.json)

**Position at the cut.** S2 and X2 both used the shared observation at 4806–4945 that Elias and Maya stop short and stay there. That observation suffices for this claim in either draft. X2 also used the retrospective to confirm the separation. Both earned both points.

**Explicit-arrival controls.** A1 and A2 each cited the last sentence (4806–4920) of draft `02037781-6b73-5869-ba09-337008c50d4f`. It records Elias and Maya reaching the housing and standing there side by side. A1 used the arrival to establish the visit. A2 used their placement in that final sentence to establish position at the cut. Both controls passed. All offsets are zero-based and end-exclusive. [Sealed evidence decisions](../../data/diagnostics/wading-path-sol-high-visit-position-2026-11-25/sealed-evidence-decisions.json)

## Inspection of all 12 slots

The runner sent six serial input counts before six serial generations. Every response returned HTTP 200. Each generation returned `gpt-6.1-sol`, matched its earlier input count, bound to the active claim and qualified for both scores. All six explanations cited `E1420` in their exact selected draft version. There were zero retries.

| Slot | Endpoint | Case | Input tokens | Output tokens | Reasoning tokens | Seconds |
| ---: | --- | --- | ---: | ---: | ---: | ---: |
| 1 | Count | S1-B | 90,998 | — | — | 1.83 |
| 2 | Count | X2-B | 91,046 | — | — | 0.31 |
| 3 | Count | A1-B | 90,989 | — | — | 0.24 |
| 4 | Count | S2-B | 91,004 | — | — | 1.37 |
| 5 | Count | X1-B | 91,035 | — | — | 0.47 |
| 6 | Count | A2-B | 91,004 | — | — | 0.25 |
| 7 | Generation | S1-B | 90,998 | 417 | 250 | 12.28 |
| 8 | Generation | X2-B | 91,046 | 289 | 158 | 7.05 |
| 9 | Generation | A1-B | 90,989 | 214 | 85 | 8.21 |
| 10 | Generation | S2-B | 91,004 | 229 | 84 | 5.77 |
| 11 | Generation | X1-B | 91,035 | 290 | 150 | 10.70 |
| 12 | Generation | A2-B | 91,004 | 304 | 177 | 7.39 |

Generations used **546,076 input tokens and 1,743 output tokens**, including 904 reasoning tokens. OpenAI reported zero cached input tokens. Summed endpoint time was 4.47 seconds for counts and 51.40 seconds for generations. Estimated generation cost under the frozen catalog was **$1.38262** against the **$2.64576** ceiling. [Slot inspection and terminal hashes](../../data/diagnostics/wading-path-visit-position-results-2026-11-25/slot-inspection.json) · [Single-use journal](../../data/diagnostics/wading-path-sol-high-visit-position-2026-11-25/output)

## Verification and disposition

Readback verified approval `e6274e578c2036d5be76318b0e30cb16d9e61f47791ec20102c72b5d2c1bcbb6`, the exact request bodies and the closed intent and terminal chain. Evidence was graded with returned labels and dispatch order masked. The evidence seal was `c25863bfb6b4002cb9758d87c42f600abbadfeb9c6442b05edc1e630bde32b23` before the scorer joined the judgments to gold. All eight local scoring checks passed. [Journal audit](../../data/diagnostics/wading-path-visit-position-results-2026-11-25/audit.json) · [Scoring checks](../../data/diagnostics/wading-path-visit-position-results-2026-11-25/scoring-tests.xml)

The unresolved case is a definite factual rejection based on an ending that leaves earlier events open. This run contains one delivery per claim and draft in one scene family. The earlier original-ending failures R1 and P1 retain their recorded scores. B remains the default, production prompts are unchanged and the full workflow canary remains on hold.
