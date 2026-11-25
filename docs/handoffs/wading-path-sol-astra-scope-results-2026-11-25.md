# The Wading Path · Sol 6.2 and Astra 6.2 results

**Astra 6.2 with explicit scope earned both points on all six cases.** It was the only arm to leave an earlier visit uncertain on the measured-stop draft. Under the ordinary B brief the two models tied on every score. Explicit scope improved both models’ explanations of what the narrator recounts. All four arms preserved every positive and negative control. [Frozen plan](wading-path-sol-astra-scope-freeze-2026-11-25.md) · [Scorer output](../../data/diagnostics/wading-path-sol-astra-scope-results-2026-11-25/scores.json)

## Scores by case and arm

Each cell shows **judgment / evidence**, one point each. B is the ordinary brief. Explicit scope (X) adds one field identifying the assessment target. All four arms used high reasoning. On SE, Astra X returned `uncertain` and the other three arms returned `unsupported`. On the other five cases every arm returned the gold label.

| Case | History and claim | Gold | Sol B | Sol X | Astra B | Astra X |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| SE | Stop alone · visit at any time | uncertain | 0/0 | 0/0 | 0/0 | **1/1** |
| SN | Stop alone · explicitly narrated arrival | unsupported | 1/0 | **1/1** | 1/0 | **1/1** |
| XE | Whole-scene exclusion · visit at any time | unsupported | 1/1 | 1/1 | 1/1 | 1/1 |
| XN | Whole-scene exclusion · explicitly narrated arrival | unsupported | 1/1 | 1/1 | 1/1 | 1/1 |
| VE | Earlier visit confirmed · visit at any time | supported | 1/1 | 1/1 | 1/1 | 1/1 |
| VN | Earlier visit confirmed · explicitly narrated arrival | supported | 1/1 | 1/1 | 1/1 | 1/1 |
| **Points out of six** | **Judgment / evidence** | | **5/4** | **5/5** | **5/4** | **6/6** |
| **Cases passing both** | | | **4/6** | **5/6** | **4/6** | **6/6** |

**SE · What happened earlier?** All four located the correct draft. It depicts entry into the plenum, the housing farther down the passage and a final stop three strides short (E1420, offsets 3995–4945). Astra X identified where that measurement begins and wrote, “the draft therefore does not establish an earlier arrival, and the closing observation does not rule one out” (initial capitalization normalized). Sol X also identified the closing interval, then asserted “They never reach the housing during the scene.” Astra B made the same scene-wide denial. Sol B described the depicted approach accurately but left the earlier interval unanswered. The frozen evidence criterion required the reason to address that interval. [Masked explanations](../../data/diagnostics/wading-path-sol-astra-scope-results-2026-11-25/evidence-sheet.json) · [Resolved draft passages](../../data/diagnostics/wading-path-sol-astra-scope-results-2026-11-25/cited-locations.json)

**SN · What does the narrator recount?** Both B responses correctly returned `unsupported`. Both lost the evidence point by adding that neither person reached the housing during the scene. Both X responses limited their conclusion to the narrated approach. They used the entry and final stop to explain why the complete draft contains no explicit account of a joint arrival. [Case-specific grading decisions](../../data/diagnostics/wading-path-sol-astra-scope-2026-11-25/sealed-evidence-decisions.json)

**Controls.** All eight responses on XE and XN used the retrospective minimum distance for both people from the opening huddle through the cut (E1420, 4947–5149). All eight on VE and VN identified the earlier joint arrival and walk back (E1420, 4947–5132). Each of these 16 responses earned both points. The unchanged endpoint control S2 remained an offline reference. [Frozen passage criteria](../../data/diagnostics/wading-path-sol-astra-scope-2026-11-25/evidence-criteria.json) · [Earlier S2 readback](wading-path-evidence-coverage-rehearsal-2026-11-25.md)

## Paired comparisons and baseline repeat

Each comparison covers six cases. A gain is a change from zero to one on the same case and axis. Ties include cases where both arms missed.

| Same-case comparison | Judgment gains / losses / ties | Evidence gains / losses / ties | Where a score changed |
| --- | ---: | ---: | --- |
| Astra against Sol, ordinary B | 0 / 0 / 6 | 0 / 0 / 6 | None |
| Astra against Sol, explicit scope | 1 / 0 / 5 | 1 / 0 / 5 | SE gained both |
| Explicit scope against B, Sol | 0 / 0 / 6 | 1 / 0 / 5 | SN gained evidence |
| Explicit scope against B, Astra | 1 / 0 / 5 | 2 / 0 / 4 | SE gained both and SN gained evidence |

**No Sol B baseline recovery.** Its fresh, byte-identical requests reproduced the previous 0/0 on SE, 1/0 on SN and 1/1 on all four controls. The frozen rule qualifies Astra X alone as a within-scene candidate. There was one observation per condition and case, all in one story family. This run establishes neither a production accuracy rate nor how often the Astra X recovery repeats. B remains the production default. [Prior Sol 6.2 scores](wading-path-sol-versions-narration-event-results-2026-11-25.md) · [Paired changes by axis](../../data/diagnostics/wading-path-sol-astra-scope-results-2026-11-25/scores.json)

## Inspection of all 48 slots

All 24 counts passed before generation began. All 48 terminals returned HTTP 200 with distinct request IDs. Every generation returned its requested model, bound to A001, cited E1420 on its exact draft version and reported the same input tokens as its own count. All 24 were eligible. There were zero retries. The inspection records each slot’s exact request hash, terminal and body hashes, request ID, time and usage. [48-slot inspection](../../data/diagnostics/wading-path-sol-astra-scope-results-2026-11-25/slot-inspection.json) · [Closed journal audit](../../data/diagnostics/wading-path-sol-astra-scope-results-2026-11-25/audit.json)

| Model and presentation | Generation input | Output | Reasoning within output | Count seconds | Generation seconds | Estimated generation cost |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Sol B | 546,946 | 882 | 47 | 3.23 | 23.60 | $1.3761850 |
| Sol X | 547,129 | 1,026 | 118 | 1.66 | 25.16 | $1.3780825 |
| **Sol total** | **1,094,075** | **1,908** | **165** | **4.89** | **48.77** | **$2.7542675** |
| Astra B | 546,946 | 908 | 53 | 3.26 | 36.45 | $5.50578 |
| Astra X | 547,129 | 2,031 | 1,139 | 2.03 | 64.04 | $5.55253 |
| **Astra total** | **1,094,075** | **2,939** | **1,192** | **5.29** | **100.49** | **$11.05831** |

The combined generation estimate was **$13.8125775** against the frozen **$26.45760** ceiling, using the approved cache-write allowance. Both models reported zero cached input reads. The successful Astra X event response took 34.32 seconds and reported 1,097 reasoning tokens within 1,259 output tokens. These resource measurements accompany a single recovery and cannot establish what caused it. [Per-slot usage](../../data/diagnostics/wading-path-sol-astra-scope-results-2026-11-25/slot-inspection.json)

The offline audit replayed the approved manifest `01513dd73de11e779413b554a9bb04703e8706d2c6ca4620e254cbb84890c7dd` and the closed intent and terminal chain. All 24 evidence decisions were sealed under `0c79fb8baf8b96195ec2a5cf11b0d7ca5e5c4be5c06b3e6a3cf6e3b77b93522d` with model, arm, order and returned label masked. The scorer then joined the decisions to frozen gold. Seven local request, source, scoring and tamper checks passed on this run. Production prompts remain unchanged, live calls are paused and the full workflow canary remains on hold. [Masked worksheet](../../data/diagnostics/wading-path-sol-astra-scope-results-2026-11-25/evidence-sheet.json) · [Verification results](../../data/diagnostics/wading-path-sol-astra-scope-results-2026-11-25/scoring-and-source-tests.xml)
