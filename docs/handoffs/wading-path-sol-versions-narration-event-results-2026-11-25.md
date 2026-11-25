# The Wading Path · Sol 6.1 and 6.2 narration/event results

**Sol 6.2 tied Sol 6.1 on every judgment and evidence score.** Each earned 5/6 for judgment, 4/6 for evidence and 4/6 on both together. Both missed the primary case, whether Elias and Maya had visited the housing earlier in the scene when the only distance measurement was at the cut. Both handled the explicit positive and negative histories correctly. The frozen comparison is complete, with zero paired gains, zero losses and no 6.2 recovery on the open event. [Frozen plan](wading-path-sol-versions-narration-event-freeze-2026-11-25.md) · [Scorer output](../../data/diagnostics/wading-path-sol-versions-results-2026-11-25/scores.json)

## Scores by model and case

Judgment and evidence each have a maximum of one point. Both models cited `E1420`, the correct complete selected draft, in every response. The two models returned the same label in each row.

| Case | History and claim | Gold | Both returned | 6.1 judgment | 6.1 evidence | 6.2 judgment | 6.2 evidence |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: |
| SE | Stop alone · visit during scene | uncertain | unsupported | 0 | 0 | 0 | 0 |
| SN | Stop alone · explicit narration | unsupported | unsupported | 1 | 0 | 1 | 0 |
| XE | Visit excluded · visit during scene | unsupported | unsupported | 1 | 1 | 1 | 1 |
| XN | Visit excluded · explicit narration | unsupported | unsupported | 1 | 1 | 1 | 1 |
| VE | Visit confirmed · visit during scene | supported | supported | 1 | 1 | 1 | 1 |
| VN | Visit confirmed · explicit narration | supported | supported | 1 | 1 | 1 | 1 |

**SE · No recovery on the open event.** The measured-stop version (`2f9e80a0-29b4-579f-8075-b6e064788b24`) places both people at the eastern wall and in the service plenum, with the housing farther down the passage (3995–4804). They stop three strides short and stay there (4806–4945). Sol 6.1 explicitly inferred “no earlier arrival followed by retreat.” Sol 6.2 summarized the route with “they reach the wall, not the housing.” The former ruled out an unreported earlier visit; the latter described the depicted approach without addressing the earlier interval. Both labeled the event `unsupported`. The passages establish the final gap and leave the scene-wide visit uncertain. Both missed judgment and evidence. This reproduces the earlier S1 failure on a fresh 6.1 attempt. [Actual explanations](../../data/diagnostics/wading-path-sol-versions-results-2026-11-25/evidence-sheet.json) · [Historical S1](wading-path-measured-stop-visit-audit-2026-11-25.md)

**SN · Correct label, overbroad reason.** On that same draft, both models correctly rejected the claim that the narrator explicitly recounts a joint arrival. Sol 6.1 then wrote that the stop “contradicts the claim that they reach the housing during the scene.” Sol 6.2 concluded that they “do not reach it during the scene.” Their descriptions of entering the plenum and stopping short were accurate. Each added a factual conclusion extending beyond what the narrator reported. That cost the evidence point even though the judgment was correct. [Sealed evidence decisions](../../data/diagnostics/wading-path-sol-versions-narration-event-2026-11-25/sealed-evidence-decisions.json)

**XE and XN · Earlier visit explicitly excluded.** The exclusion draft (`4da86d35-9337-54d8-896b-c212ba05516c`) adds a minimum distance for both people from the opening huddle through the cut (4947–5149). On XE, both models located that retrospective and used its coverage of the whole scene to rule out an earlier visit. On XN, both described the narrated plenum entry and stop and accounted for the retrospective. Each earned both points on both claims. [Resolved citations and selected versions](../../data/diagnostics/wading-path-sol-versions-results-2026-11-25/cited-locations.json)

**VE and VN · Earlier visit explicitly confirmed.** The confirmed draft (`58a48fd1-3acd-5e69-9f1b-a89c67170c20`) recounts a joint arrival after plenum entry and before the light steadied, followed by a walk back up the passage (4947–5132). On VE, both models identified that earlier event and placed the final stop after it. On VN, both cited the retrospective as an explicit account of reaching the housing together. Each earned both points on both claims. [Case criteria](../../data/diagnostics/wading-path-sol-versions-narration-event-2026-11-25/evidence-criteria.json) · [Verbatim explanations](../../data/diagnostics/wading-path-sol-versions-results-2026-11-25/evidence-sheet.json)

## Inspection of all 24 slots

All 12 counts passed before generation began. All 24 terminals returned HTTP 200 with distinct request IDs. Each generation returned its requested model, bound to the single active claim and reported the same input-token count as its own pre-count. There were zero retries and all 12 generations qualified for scoring. Each row below records a count slot and its corresponding generation slot. [Slot inspection and terminal hashes](../../data/diagnostics/wading-path-sol-versions-results-2026-11-25/slot-inspection.json) · [Closed dispatch journal](../../data/diagnostics/wading-path-sol-versions-narration-event-2026-11-25/output)

| Count slot | Gen slot | Case | Sol | Count and gen input | Gen output | Reasoning | Count seconds | Gen seconds |
| ---: | ---: | --- | --- | ---: | ---: | ---: | ---: | ---: |
| 1 | 13 | SN | 6.1 | 91,025 | 283 | 149 | 1.91 | 7.19 |
| 2 | 14 | SN | 6.2 | 91,151 | 150 | 0 | 0.28 | 4.98 |
| 3 | 15 | XE | 6.2 | 91,161 | 133 | 0 | 0.27 | 5.35 |
| 4 | 16 | XE | 6.1 | 91,035 | 294 | 162 | 0.26 | 7.86 |
| 5 | 17 | VN | 6.1 | 91,048 | 310 | 165 | 0.30 | 9.48 |
| 6 | 18 | VN | 6.2 | 91,174 | 144 | 0 | 0.34 | 4.22 |
| 7 | 19 | SE | 6.2 | 91,124 | 203 | 47 | 0.25 | 5.81 |
| 8 | 20 | SE | 6.1 | 90,998 | 477 | 320 | 0.26 | 13.32 |
| 9 | 21 | XN | 6.1 | 91,054 | 273 | 126 | 0.19 | 8.98 |
| 10 | 22 | XN | 6.2 | 91,180 | 136 | 0 | 0.26 | 4.31 |
| 11 | 23 | VE | 6.2 | 91,156 | 137 | 0 | 1.08 | 4.49 |
| 12 | 24 | VE | 6.1 | 91,030 | 306 | 162 | 0.20 | 8.02 |

## Resources and disposition

| Sol | Generation input | Output | Reported reasoning within output | Count time | Generation time | Estimated generation cost |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 6.1 | 546,190 | 1,943 | 1,084 | 3.12 s | 54.85 s | $1.384905 |
| 6.2 | 546,946 | 903 | 47 | 2.47 s | 29.17 s | $1.376395 |

Sol 6.2 completed each of the six matched generations faster and used fewer output tokens in each. Both requested high reasoning. The API reported zero reasoning tokens for five 6.2 generations and 47 for SE. It counted 126 more input tokens for 6.2 in every pair despite the matching story payload. Both models reported zero cached input reads. The combined generation estimate was **$2.76130** against the frozen **$5.29152** ceiling, using the frozen standard rates and cache-write allowance. [Slot-level resource readback](../../data/diagnostics/wading-path-sol-versions-results-2026-11-25/slot-inspection.json)

The offline audit verified approval `6eaadeb7d5290667d3e63a47eb9974a0d1d9f89ba9f5bda2f5a5d45934a40a93`, the exact requests and the closed intent and terminal chain. Evidence decisions were sealed under `9197f99a29dc576d63a6b7bbe5cc8fe0ffbf0d41e1d1061cb59bda18c1d70ea0` with model, returned label and dispatch order masked. The scorer then joined all 12 decisions to gold. All five scoring checks passed. [Journal audit](../../data/diagnostics/wading-path-sol-versions-results-2026-11-25/audit.json) · [Scoring checks](../../data/diagnostics/wading-path-sol-versions-results-2026-11-25/scoring-tests.xml)

This run provides evidence of a resource difference on these six requests. The model upgrade showed no improvement in factual assessment on this scene family. B remains the default, production prompts are unchanged, further live calls are paused and the full workflow canary remains on hold.
