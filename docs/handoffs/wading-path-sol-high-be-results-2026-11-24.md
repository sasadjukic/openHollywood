# The Wading Path · Sol-high B/E results

**Keep B as the default.** E recovered neither physical-position judgment. Sol returned `unsupported` on all five assessments. That label was correct for Q008, which asks whether the ending narrates arrival. Q010 and Q011 ask where Elias and Maya are at the cut. Their entry into the service plenum is established, but their position relative to the breaker housing remains uncertain. E also lost the evidence point on Q011. The frozen decision is **hold**. [Approved plan](wading-path-sol-high-be-freeze-2026-11-24.md) · [Scores by arm](../../data/diagnostics/wading-path-be-results-2026-11-24/scores.json)

## Judgment and evidence

| Claim | Brief | Frozen gold | Returned | Judgment / 1 | Evidence / 1 | Basis for evidence score |
| --- | --- | --- | --- | ---: | ---: | --- |
| Q010 · achieved standing position | B | uncertain | unsupported | 0 | 0 | Correctly identifies who enters and what stands at the passage end, then treats the last view as ruling out the pair standing there. |
| Q010 · achieved standing position | E | uncertain | unsupported | 0 | 0 | Again attributes “stood” to the housing, but says the pair’s claimed position conflicts with the staging. The draft supplies no final distance or posture. |
| Q008 · narrated arrival control | B | unsupported | unsupported | 1 | 1 | Locates the plan outcome, credits the depicted entry and follows the account through the final barrier description. The explanation confines the missing arrival to what is narrated. |
| Q011 · fulfillment of the planned endpoint | E | uncertain | unsupported | 0 | 0 | Locates both assignments and the closing passage, but says the draft “depicts an earlier stopping point.” No cited observation places the pair at a definite stop short of the housing. |
| Q011 · fulfillment of the planned endpoint | B | uncertain | unsupported | 0 | 1 | Locates both assignments, the entry, the gaze and the housing. Its explanation limits its conclusion to the last narrated movement and leaves standing before the barrier unestablished. The returned judgment still misses gold. |

**Why the Q011 evidence scores differ.** Both arms cited the same plan fields and the same complete draft. Both recognized the housing as the final barrier. B explained the limit of what the ending depicts. E also recognized that standing there was unestablished, but added an affirmative claim that the draft depicts a stopping point. The passage shows entry, a look deeper into the shaft, and the location of the housing. It gives no subsequent observation fixing the pair’s final position. Under the frozen evidence rule, that extra claim cost E the point. This was a passage-level scoring decision. [Exact responses and resolved citations](../../data/diagnostics/wading-path-be-results-2026-11-24/inspection.json) · [Cited source fields](../../data/diagnostics/wading-path-be-results-2026-11-24/cited-locations.json) · [Frozen evidence criteria](../../data/diagnostics/wading-path-sol-high-be-2026-11-24/gold.json)

Q010 retained both misses. Q011 retained the judgment miss and moved from 1 to 0 on evidence. Neither position baseline passed both axes. Q008 passed both as the separate control. These two related position claims come from one ordinary review of one ending. The result limits the case for transferring E to this review and provides no measurement of writer revisions or reader preference. [Earlier authored transfer comparison](q011-sol-high-transfer-results-2026-11-23.md)

## All ten slots

The five count slots completed before the first generation. All ten calls returned HTTP 200. Each generation returned the registered `gpt-6.1-sol` model and a complete assessment bound to the correct claim. Every generation’s reported input matched its earlier count.

| Slot | Endpoint | Claim and brief | Counted or used input | Output | Reasoning within output | Seconds | Disposition |
| ---: | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | Count | Q010 B | 91,590 | — | — | 1.84 | Admitted |
| 2 | Count | Q010 E | 91,631 | — | — | 0.27 | Admitted |
| 3 | Count | Q008 B | 91,711 | — | — | 0.22 | Admitted |
| 4 | Count | Q011 E | 91,676 | — | — | 0.20 | Admitted |
| 5 | Count | Q011 B | 91,632 | — | — | 0.24 | Admitted |
| 6 | Generation | Q010 B | 91,590 | 691 | 516 | 13.87 | Eligible, scored |
| 7 | Generation | Q010 E | 91,631 | 945 | 756 | 19.58 | Eligible, scored |
| 8 | Generation | Q008 B | 91,711 | 602 | 386 | 12.85 | Eligible, scored |
| 9 | Generation | Q011 E | 91,676 | 1,364 | 1,136 | 37.08 | Eligible, scored |
| 10 | Generation | Q011 B | 91,632 | 788 | 587 | 22.12 | Eligible, scored |

The five generations used **458,240 input and 4,390 output tokens**, including 3,381 reasoning tokens. OpenAI reported zero cached input. Summed endpoint time was 2.78 seconds for counts and 105.50 seconds for generations. The estimated generation cost at the frozen catalog rates was **$1.18950** against the $2.20480 ceiling. Across the two position pairs E used 830 more output tokens than B in this run. [All ten audited slots](../../data/diagnostics/wading-path-be-results-2026-11-24/audit.json) · [Original journal](../../data/diagnostics/wading-path-sol-high-be-2026-11-24/output/)

## Verification

The single-use journal closed after five counts and five generations, with zero retries. The audit rebuilt the approved requests and checked the intent and terminal chain. Each evidence decision used a worksheet that withheld arm, dispatch order and returned judgment. All five decisions were sealed before joining the returned labels to gold. Evidence seal SHA-256 is `6a71160d1f8713162668cfa237c99962dcd86b07e10348eab484adc02520309e`. Production prompts are unchanged, live calls are paused and the full workflow canary remains on hold. [Masked worksheet](../../data/diagnostics/wading-path-be-results-2026-11-24/evidence-worksheet.json) · [Sealed evidence decisions](../../data/diagnostics/wading-path-sol-high-be-2026-11-24/sealed-evidence-decisions.json)
