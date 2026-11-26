# Wading Path measured-stop repeat results

**Keep B as the default and hold advancement.** On four fresh, byte-identical measured-stop requests per arm, Astra X correctly left the earlier visit unresolved once. Sol B, Sol X and Astra B each did so zero times. All eight determinate controls earned all three points. Astra X passed both controls, but its one grounded pass fell below the required three and its one-pass lead fell below the required two. [Frozen plan and decision rule](wading-path-se-repeat-freeze-2026-11-26.md)

## Measured stop and controls

The claim asks whether Elias and Maya reached the panel housing together **at any time during scene four**. All three drafts end with them three strides short. SE leaves their earlier position unresolved. VE attests an earlier joint visit and return. XE supplies a minimum distance for the whole scene. Each score below counts passes on one axis under the frozen rubric. A grounded pass requires both the correct label and a factually sufficient explanation.

| Arm | SE correct label /4 | SE factually sufficient /4 | SE diagnostically complete /4 | SE grounded /4 | SE false denials /4 | VE label/factual/diagnostic | XE label/factual/diagnostic |
| --- | ---: | ---: | ---: | ---: | ---: | --- | --- |
| Sol B | 0 | 0 | 0 | 0 | 2 | 1/1/1 | 1/1/1 |
| Sol X | 0 | 0 | 0 | 0 | 3 | 1/1/1 | 1/1/1 |
| Astra B | 0 | 0 | 0 | 0 | 4 | 1/1/1 | 1/1/1 |
| Astra X | 1 | 1 | 1 | 1 | 3 | 1/1/1 | 1/1/1 |

**The successful explanation** came from Astra X on repeat 3 (generation slot 38). It placed the joint stop at the close, recognized the earlier sightline and explained why an earlier visit stayed possible. Its reason reads, “Seeing it does not establish arrival, and the closing observation does not rule out an earlier arrival.” The same request produced three other explanations that denied the visit. One of those failures used 1,256 reasoning tokens. The pass used 1,189. The observed reasoning-token count does not by itself distinguish a grounded answer. The first comparison’s Astra X success is retained separately from this repeat’s denominator. [November 25 result](wading-path-sol-astra-scope-results-2026-11-25.md) · [All joined scores](../../data/diagnostics/wading-path-se-repeat-results-2026-11-26/scores.json)

**The failure had two forms.** Fifteen of the 16 SE answers returned `unsupported`. Twelve explanations asserted an unwarranted physical non-arrival. The other three accurately described the approach or the absence of a depicted arrival, but left open what their author concluded about the earlier interval. Those three received zero for factual sufficiency and diagnostic completeness with the denial flag clear. By contrast, every arm used the actual retrospective evidence correctly on both controls. On this scene, locating the correct draft and even identifying the limits of its last sentence often coexisted with an overreach about the preceding action.

## False denials and grading boundaries

| Generation slot | Arm and repeat | Exact assertion in the explanation |
| --- | --- | --- |
| 25 | Sol B 1 | “The sequence shows that they never reach the housing during scene four.” |
| 26 | Sol X 1 | “the preceding approach shows that they had not reached the housing before they stopped either.” |
| 27 | Astra X 1 | “They never reach the housing during scene four.” |
| 28 | Astra B 1 | “Neither reaches the housing at any point in the scene.” |
| 33 | Sol X 2 | “the preceding approach shows that they had not reached the housing earlier either.” |
| 34 | Astra B 2 | “Neither reaches the housing at any point in the scene.” |
| 36 | Astra X 2 | “They never reach it during the scene.” |
| 37 | Astra B 3 | “Neither reaches it at any point in the scene.” |
| 45 | Astra X 4 | “neither covers the remaining distance.” |
| 46 | Sol B 4 | “They approach the housing but never reach it.” |
| 47 | Astra B 4 | “Neither reaches the housing at any point in the scene.” |
| 48 | Sol X 4 | “They do not reach the housing at any point in the scene.” |

The denial annotation grades assertions in the explanation independently of the returned label. For slots 26 and 33, the reasons first rule out arrival from the stop onward, then explicitly rule it out before the stop too. Those clauses jointly cover the scene. In slot 45, “neither covers the remaining distance” was read as an assertion about the people’s earlier movement, following the separate exclusion from the stop onward. A narrower reading confined to the depicted approach would remove that one flag, leaving the scores and advancement decision unchanged.

Slots 35, 39 and 40 confined their conclusions to the approach or what the draft shows. Slot 39 illustrates that boundary. It says the approach “shows no earlier arrival” and describes which places they reach on it. The masked reading found an incomplete factual answer without a categorical denial. On the controls, a precise final-sentence locator with the scene-wide minimum distance was accepted for XE. Ordering VE’s visit and walk back between entry and the later measured stop was accepted as an equivalent time locator. [Masked worksheet](../../data/diagnostics/wading-path-se-repeat-results-2026-11-26/evidence-sheet.json) · [Sealed individual readings, excerpts and rationales](../../data/diagnostics/wading-path-se-repeat-2026-11-26/sealed-evidence-decisions.json)

## Paired comparisons

Each row compares six matched observations (four SE repeats and the two controls). Values are gains / losses / ties for the first named condition relative to the second. The one gain on each axis in two comparisons comes from the same Astra X answer on SE repeat 3. All controls tied.

| Comparison | Label G/L/T | Factual G/L/T | Diagnostic G/L/T |
| --- | --- | --- | --- |
| Astra vs Sol under B | 0/0/6 | 0/0/6 | 0/0/6 |
| Astra vs Sol under X | 1/0/5 | 1/0/5 | 1/0/5 |
| X vs B for Astra | 1/0/5 | 1/0/5 | 1/0/5 |
| X vs B for Sol | 0/0/6 | 0/0/6 | 0/0/6 |

## All 48 fixed slots

Slots 1–24 were serial input counts. All 24 passed before the first generation. Slots 25–48 were serial generations. All 48 had HTTP 200 receipts and distinct returned request IDs. Every generation used the high-reasoning request, returned the requested model, bound to A001, cited E1420 on the exact selected draft and reported input usage equal to its own count. Each row pairs a count slot with its generation. All generations were eligible. Zero retries. [Closed audited journal](../../data/diagnostics/wading-path-se-repeat-results-2026-11-26/audit.json) · [Slot-by-slot receipts, hashes, scores, usage and latency](../../data/diagnostics/wading-path-se-repeat-results-2026-11-26/slot-inspection.json)

| Count / generation slots | Case · repeat | Arm | Counted input | Count / generation seconds | Output / reasoning tokens | Returned label | Label / factual / diagnostic | False denial |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 01 / 25 | SE · 1 | Sol B | 91,124 | 1.83 / 5.39 | 189 / 46 | unsupported | 0/0/0 | Yes |
| 02 / 26 | SE · 1 | Sol X | 91,155 | 1.63 / 9.14 | 336 / 156 | unsupported | 0/0/0 | Yes |
| 03 / 27 | SE · 1 | Astra X | 91,155 | 0.28 / 19.46 | 703 / 533 | unsupported | 0/0/0 | Yes |
| 04 / 28 | SE · 1 | Astra B | 91,124 | 0.29 / 5.68 | 184 / 43 | unsupported | 0/0/0 | Yes |
| 05 / 29 | VE · 1 | Astra X | 91,187 | 0.24 / 5.62 | 154 / 0 | supported | 1/1/1 | No |
| 06 / 30 | VE · 1 | Astra B | 91,156 | 0.24 / 6.29 | 144 / 0 | supported | 1/1/1 | No |
| 07 / 31 | VE · 1 | Sol X | 91,187 | 0.25 / 4.69 | 151 / 0 | supported | 1/1/1 | No |
| 08 / 32 | VE · 1 | Sol B | 91,156 | 0.23 / 4.15 | 141 / 0 | supported | 1/1/1 | No |
| 09 / 33 | SE · 2 | Sol X | 91,155 | 0.25 / 7.51 | 330 / 147 | unsupported | 0/0/0 | Yes |
| 10 / 34 | SE · 2 | Astra B | 91,124 | 0.23 / 5.37 | 200 / 50 | unsupported | 0/0/0 | Yes |
| 11 / 35 | SE · 2 | Sol B | 91,124 | 0.29 / 4.48 | 179 / 38 | unsupported | 0/0/0 | No |
| 12 / 36 | SE · 2 | Astra X | 91,155 | 0.24 / 37.57 | 1,430 / 1,256 | unsupported | 0/0/0 | Yes |
| 13 / 37 | SE · 3 | Astra B | 91,124 | 0.37 / 4.90 | 137 / 0 | unsupported | 0/0/0 | Yes |
| 14 / 38 | SE · 3 | Astra X | 91,155 | 0.21 / 33.87 | 1,358 / 1,189 | uncertain | 1/1/1 | No |
| 15 / 39 | SE · 3 | Sol X | 91,155 | 0.23 / 7.13 | 310 / 126 | unsupported | 0/0/0 | No |
| 16 / 40 | SE · 3 | Sol B | 91,124 | 0.25 / 4.81 | 223 / 73 | unsupported | 0/0/0 | No |
| 17 / 41 | XE · 1 | Sol B | 91,161 | 0.28 / 3.73 | 131 / 0 | unsupported | 1/1/1 | No |
| 18 / 42 | XE · 1 | Sol X | 91,192 | 0.25 / 5.04 | 147 / 0 | unsupported | 1/1/1 | No |
| 19 / 43 | XE · 1 | Astra B | 91,161 | 0.24 / 5.36 | 140 / 0 | unsupported | 1/1/1 | No |
| 20 / 44 | XE · 1 | Astra X | 91,192 | 0.22 / 5.91 | 154 / 0 | unsupported | 1/1/1 | No |
| 21 / 45 | SE · 4 | Astra X | 91,155 | 0.25 / 24.76 | 947 / 779 | unsupported | 0/0/0 | Yes |
| 22 / 46 | SE · 4 | Sol B | 91,124 | 0.31 / 4.96 | 185 / 42 | unsupported | 0/0/0 | Yes |
| 23 / 47 | SE · 4 | Astra B | 91,124 | 0.28 / 4.13 | 142 / 0 | unsupported | 0/0/0 | Yes |
| 24 / 48 | SE · 4 | Sol X | 91,155 | 0.22 / 5.82 | 232 / 48 | unsupported | 0/0/0 | Yes |

## Resource use and verification

| Arm | Generation input | Output | Reasoning within output | Cached input | Count seconds | Generation seconds | Estimated generation cost |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Astra B | 546,813 | 947 | 93 | 273,363 | 1.65 | 31.74 | $2.8817252 |
| Astra X | 546,999 | 4,746 | 3,757 | 273,456 | 1.45 | 127.19 | $3.0346524 |
| Sol B | 546,813 | 1,048 | 199 | 273,363 | 3.19 | 27.52 | $0.7214413 |
| Sol X | 546,999 | 1,506 | 477 | 273,456 | 2.83 | 39.33 | $0.7262631 |

Total generation usage was **2,187,624 input tokens** (1,093,638 reported cached) and **8,247 output tokens**, including **4,526 reasoning tokens**. Under the frozen rate and cache assumptions the generation estimate was **$7.364082** against a **$26.45760** ceiling. This is an estimate from reported usage. The receipts do not document a billed amount.

The runner and offline auditor verified approval SHA-256 `91d46c7d2e445a47d72ede07919e5a44c666aa987a3705cb4bdf9bb8013698c8`. The 24 masked readings were sealed under `342777e1f71431e637d3328d6435ff92f2f697588486d9db7635358fdbe98106` before joining model, presentation, order or returned label. Fourteen focused offline checks passed. B stays the production default, further live calls are paused and the workflow canary remains on hold. [Verification record](../../data/diagnostics/wading-path-se-repeat-results-2026-11-26/verification.xml)

The next local step is to preserve the one grounded Astra X answer alongside its three same-request misses and the two determinate controls. They form a compact regression for separating a narrated approach from an actual whole-scene exclusion. This repeat supplies no basis for advancing Astra X to the held-out live test.
