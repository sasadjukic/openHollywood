# Planetarium repeat results for Sol 6.2 and Astra 6.2

**All four arms earned both points on the open event.** Sol B, Sol with explicit scope, Astra B and Astra with explicit scope each returned `uncertain` and explained why a blank dome at closing leaves an earlier projection possible. The frozen decision is **shared open-event recovery**, including a Sol B baseline recovery. On The Wading Path only Astra with explicit scope had earned both points on the analogous claim. B remains the default. [Approved planetarium plan](planetarium-sol-astra-scope-freeze-2026-11-25.md) · [Wading Path result](wading-path-sol-astra-scope-results-2026-11-25.md)

## Scores for all 24 assessments

Each cell shows **judgment / evidence**, one point available on each axis. Every arm returned the label in the gold column. B uses the ordinary work brief. X adds the frozen claim-specific scope instruction. Both models ran at high reasoning.

| History and claim | Gold and returned label | Sol B | Sol X | Astra B | Astra X |
| --- | --- | ---: | ---: | ---: | ---: |
| ON · Open history, explicitly narrated | unsupported | 1/0 | 1/1 | 1/0 | 1/1 |
| OE · Open history, occurred at any time | uncertain | 1/1 | 1/1 | 1/1 | 1/1 |
| DN · Excluded, explicitly narrated | unsupported | 1/1 | 1/1 | 1/1 | 1/1 |
| DE · Excluded, occurred at any time | unsupported | 1/1 | 1/1 | 1/1 | 1/1 |
| PN · Confirmed, explicitly narrated | supported | 1/1 | 1/1 | 1/1 | 1/1 |
| PE · Confirmed, occurred at any time | supported | 1/0 | 1/1 | 1/1 | 1/1 |
| **Totals out of six on each axis** | | **6/4** | **6/6** | **6/5** | **6/6** |

All **24 judgments** and **21 evidence explanations** passed. Sol X and Astra X met the all-six-case criterion. The four arms earned 4/4 joint passes on the open event, 2/4 on its narration counterpart and 15/16 across the four determinate controls. [Scores and all paired contrasts](../../data/diagnostics/planetarium-sol-astra-scope-results-2026-11-25/scores.json)

## What the explanations established

**OE, the transfer target.** Every explanation identified the mounted slide, recognized that the account leaves execution of its cue unreported and confined the blank-dome observation to the closing interval. Sol B explicitly identified the summary of the rehearsal’s middle as leaving the image unspecified. Other answers located the same gap by describing the unreported earlier cue. Neither the cue sheet nor the closing observation settled the event. [Masked explanations](../../data/diagnostics/planetarium-sol-astra-scope-results-2026-11-25/evidence-sheet.json) · [Selected drafts and context](../../tests/fixtures/planetarium_scope_sources.json)

**ON, the open narration claim.** Both B answers correctly said the complete draft never recounts a projection. They mentioned the slide and the blank ending but left the reader to locate the omission between them. The frozen criterion also required grounding that gap. Both X explanations identified the limit of the closing observation relative to the earlier rehearsal. This counted as an equivalent temporal locator for the skipped cues. The two B evidence misses were omissions in otherwise accurate explanations. Neither B answer denied that an earlier projection could have occurred. The relevant spans in E1420 are the slide at 329–651, the summarized middle at 937–1176 and the closing at 1178–1300. [Frozen passage criteria](../../tests/fixtures/planetarium_scope_gold.json) · [Sealed grading decisions](../../data/diagnostics/planetarium-sol-astra-scope-2026-11-25/sealed-evidence-decisions.json)

**PE, the confirmed event.** Sol B correctly cited direct narration of the middle-cue projection. That sentence establishes the existential claim. The frozen evidence criterion also asked the reviewer to locate the image going out before Kit returned. Sol B jumped from the projection to the blank dome at closing and omitted that transition. Its 1/0 records the difference between proving the event and satisfying the full evidence request. The other three arms located the transition. All four PN explanations identified the narrated projection and disappearance. On DN and DE, every arm used the explicit exclusion through the closing cue and the continued blank dome through the end bell. [Gold with exact source versions](../../tests/fixtures/planetarium_scope_gold.json) · [Verbatim deliveries and audit](../../data/diagnostics/planetarium-sol-astra-scope-results-2026-11-25/audit.json)

## Paired changes

Each comparison covers the same six cases. All six judgment comparisons tied in every row.

| Comparison | Evidence gains | Losses | Ties | Cases gaining evidence |
| --- | ---: | ---: | ---: | --- |
| Astra against Sol under B | 1 | 0 | 5 | PE |
| Astra against Sol under X | 0 | 0 | 6 | — |
| X against B on Sol | 2 | 0 | 4 | ON, PE |
| X against B on Astra | 1 | 0 | 5 | ON |

Explicit scope improved the completeness of explanations for the open narration claim on both models. **The open-event gain specific to Astra X on The Wading Path did not repeat.** Both baseline arms already got that case right here. The fresh packet is a shorter authored story, at 2,413–2,491 counted tokens per request. The earlier family used roughly 91,000. With one delivery per case and arm, this comparison cannot distinguish effects of story content, context length and run-to-run variation. It gives no reason to route ordinary assessments to Astra by default. A useful local follow-up is to preserve the four OE passes and the three evidence omissions, distinguishing evidence needed for the claim from extra detail required by a diagnostic. Story quality and writer behavior were outside this comparison. [Prior family and resource readback](wading-path-sol-astra-scope-results-2026-11-25.md)

## Slot inspection and resources

All **24 counts** returned HTTP 200 and passed before generation. All **24 generations** returned HTTP 200, completed on the requested model and bound to A001 on the exact selected draft. Every answer cited E1420. Each generation’s reported input matched its count. The journal contains 48 intents, 48 terminals, 48 distinct provider request IDs and a verified closure. There were **zero retries**. Per-slot records include exact request and terminal hashes, source binding, eligibility, elapsed time and provider usage. [All 48 inspected slots](../../data/diagnostics/planetarium-sol-astra-scope-results-2026-11-25/slot-inspection.json)

| Arm | Generation input tokens | Output tokens | Reported reasoning tokens | Count seconds | Generation seconds | Estimated generation cost |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Sol B | 14,620 | 807 | 0 | 2.18 | 17.11 | $0.0446200 |
| Sol X | 14,803 | 845 | 0 | 5.45 | 18.67 | $0.0454575 |
| Astra B | 14,620 | 788 | 0 | 3.13 | 26.68 | $0.17772 |
| Astra X | 14,803 | 822 | 0 | 2.20 | 27.50 | $0.18091 |
| **Total** | **58,846** | **3,262** | **0** | **12.96** | **89.96** | **$0.4487075** |

All 24 provider responses explicitly reported zero reasoning tokens and zero cached input tokens. The cost estimate uses the frozen conservative cache-write allowance and is below the $26.45760 generation ceiling. [Resource and terminal records](../../data/diagnostics/planetarium-sol-astra-scope-results-2026-11-25/slot-inspection.json)

The offline audit replayed approval SHA-256 `8ee223cb4b4bd7251a6ec0c7bfbe764a12383e5aef90ff8dd1a8a0f75da26cd4`. Evidence was graded with model, presentation, order and returned label masked, then sealed under `fb63d35fe127491212c95b2c39758801ee4727c56b33a3a62dfdd5288b44c3d5` before the frozen scorer joined the labels. All nine focused offline source, request, scoring and tamper checks passed. Production prompts are unchanged, further live calls are paused and the canary remains on hold. [Masked worksheet](../../data/diagnostics/planetarium-sol-astra-scope-results-2026-11-25/evidence-sheet.json) · [Verification record](../../data/diagnostics/planetarium-sol-astra-scope-results-2026-11-25/scoring-and-source-tests.xml)
