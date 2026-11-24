# The Wading Path · Sol-high B results for three claims about arrival

**Sol passed both scores on five of seven assessments.** It identified what the original ending narrates, answered all three questions correctly after an explicit arrival and retreat, and passed the ordinary Q008 control. The two failures concern what the original leaves open. Sol returned `unsupported` both for a visit during the scene and for presence at the cut. Each had frozen gold `uncertain`, and each explanation also failed its own evidence criterion. The frozen decision is `hold_claim_scope`. [Frozen protocol](wading-path-three-claims-sol-high-freeze-2026-11-24.md) · [Scorer output](../../data/diagnostics/wading-path-three-claims-results-2026-11-24/scores.json)

## Original draft

| Claim | Gold | Sol | Judgment / 1 | Evidence / 1 |
| --- | --- | --- | ---: | ---: |
| N1 · The ending explicitly narrates both reaching the housing | Unsupported | Unsupported | 1 | 1 |
| R1 · Both reach the housing at some time during scene four | Uncertain | Unsupported | 0 | 0 |
| P1 · Both are at the housing at the final narrated instant | Uncertain | Unsupported | 0 | 0 |

All three answers cited the complete, correct draft in `E1420`, version `38e82829-604f-40df-b5a0-1c968718573e`. In N1, Sol traced the pair to the eastern wall and into the plenum (characters 3995–4323), followed their look deeper (4325–4571), and identified the housing as the subject of the final description (4573–4804). That covers the ending well enough to rule out **explicit narration** of arrival. All offsets here are zero-based and end-exclusive. [Resolved citations](../../data/diagnostics/wading-path-three-claims-results-2026-11-24/cited-locations.json)

In **R1**, Sol said the scene ends “without their traversing the passage.” That wording turns an omitted movement into a fact about what happened. A narrower reading of its last sentence is that the draft fails to establish a visit. Even on that reading, the explanation never addresses why a visit during the scene remains possible. The frozen evidence criterion required that distinction.

In **P1**, Sol wrote that “This staging places the housing ahead of them.” The last movement places the pair inside the plenum. The closing description places the housing at the passage end. The scene supplies no persistent distance between them at the final instant. Sol correctly located both passages, then inferred a final spatial relationship they do not settle. [Masked explanations](../../data/diagnostics/wading-path-three-claims-results-2026-11-24/evidence-sheet.json) · [Frozen evidence criteria](../../data/diagnostics/wading-path-three-claims-sol-high-2026-11-24/evidence-criteria.json)

## Arrival-then-retreat draft

| Claim | Gold | Sol | Judgment / 1 | Evidence / 1 |
| --- | --- | --- | ---: | ---: |
| N2 · The ending explicitly narrates both reaching the housing | Supported | Supported | 1 | 1 |
| R2 · Both reach the housing at some time during scene four | Supported | Supported | 1 | 1 |
| P2 · Both are at the housing at the final narrated instant | Unsupported | Unsupported | 1 | 1 |

Each answer cited `E1420` from the selected retreat draft, version `ae1fb3f6-5e23-597a-a61f-020b9cc8e254`. Both people explicitly reach the housing at 4806–4920. In the final sentence (4922–5008) they step back three full strides and stay there. For N2 and R2, Sol explained why the departure preserves the narrated arrival and the earlier visit. For P2, it used that same departure to establish the pair’s later position. This is evidence of the distinction on this ending, with one delivery per claim. [Evidence decisions](../../data/diagnostics/wading-path-three-claims-sol-high-2026-11-24/sealed-evidence-decisions.json)

## Q008 B · Ordinary narration control

**Gold `unsupported` · Sol `unsupported` · Judgment 1/1 · Evidence 1/1.** Sol cited the assigned outcome in the exact scene-four plan (`E0258`) and the pair’s entry into the plenum in the original draft (`E1420`). It followed the ending through the look deeper and the description of the housing. It correctly identified the ordinary critic’s assertion that the draft narrates their arrival at the passage end as the unsupported part of the field. Both scores reproduced the historical control on byte-identical requests. [Control and prior result](wading-path-three-claims-rehearsal-2026-11-24.md) · [New scores](../../data/diagnostics/wading-path-three-claims-results-2026-11-24/scores.json)

## Inspection of all 14 slots

The single-use runner sent the seven counts first, then seven generations, with zero retries. All 14 responses were HTTP 200. Each generation returned `gpt-6.1-sol` with the bound active claim and valid citations, and its reported input usage matched its earlier count. All seven qualified for scoring. Reasoning tokens are included in output.

| Slot | Endpoint | Case | Input tokens | Output tokens | Reasoning tokens | Seconds |
| ---: | --- | --- | ---: | ---: | ---: | ---: |
| 1 | Count | N1-B | 90,946 | — | — | 12.98 |
| 2 | Count | R2-B | 91,015 | — | — | 10.35 |
| 3 | Count | P1-B | 90,980 | — | — | 10.39 |
| 4 | Count | Q008-B | 91,711 | — | — | 9.36 |
| 5 | Count | N2-B | 91,002 | — | — | 8.67 |
| 6 | Count | R1-B | 90,949 | — | — | 11.42 |
| 7 | Count | P2-B | 91,016 | — | — | 10.75 |
| 8 | Generation | N1-B | 90,946 | 379 | 229 | 19.57 |
| 9 | Generation | R2-B | 91,015 | 229 | 107 | 14.24 |
| 10 | Generation | P1-B | 90,980 | 393 | 237 | 21.70 |
| 11 | Generation | Q008-B | 91,711 | 696 | 488 | 26.23 |
| 12 | Generation | N2-B | 91,002 | 279 | 147 | 17.27 |
| 13 | Generation | R1-B | 90,949 | 388 | 245 | 20.51 |
| 14 | Generation | P2-B | 91,016 | 218 | 88 | 13.92 |

Generations used **637,619 input tokens and 2,582 output tokens**, including 1,541 reasoning tokens. OpenAI reported zero cached input tokens across the seven generations. Summed endpoint time was 73.91 seconds for counts and 133.43 seconds for generations. Estimated generation cost under the frozen catalog was **$1.61987** against the **$3.08672** ceiling. [Slot inspection and terminal hashes](../../data/diagnostics/wading-path-three-claims-results-2026-11-24/slot-inspection.json) · [Single-use journal](../../data/diagnostics/wading-path-three-claims-sol-high-2026-11-24/output)

## Verification and disposition

Readback verified approval `91285c0d71c0e48e92ba22abf6d83e93b97b2bfc21be015e64cb7b739c45c137`, exact request bytes, source versions, and the closed intent and terminal chain. Evidence was assessed from citations and reasons with the returned labels and dispatch order masked. The evidence seal was `ccbf9d191fa697ef5ff9eadd48d05cb921237e6dbb0ae588f1a98c68f1f020f4` before the scorer joined judgments to gold. All eight local scoring checks passed. [Journal audit](../../data/diagnostics/wading-path-three-claims-results-2026-11-24/audit.json) · [Scoring checks](../../data/diagnostics/wading-path-three-claims-results-2026-11-24/scoring-tests.xml)

The original’s missing movement remains an unreliable basis for an automatic factual rejection. The explicit retreat and Q008 remain useful positive controls for that finding. This single-family diagnostic measures factual assessment only. B remains the default, production prompts are unchanged, and the full workflow canary stays on hold.
