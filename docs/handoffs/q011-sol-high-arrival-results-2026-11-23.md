# Q011 results for the original ending and the authored arrival

**The original ending failed judgment and evidence. The authored arrival passed both.** With baseline B and high reasoning, `gpt-6.1-sol` changed its judgment when the draft added “Elias stood at the threshold.” It correctly identified that sentence as proof of arrival. On the genuine ending, it found the relevant passage but treated fulfillment as disproved where the draft leaves it open. The frozen decision is **`hold`**. [Frozen comparison](q011-sol-high-arrival-freeze-2026-11-23.md) · [Joined scores](../../data/diagnostics/q011-arrival-results-2026-11-23/scores.json)

## Judgment and evidence

Q011 claims that the achieved state fulfills two assignments in Scene Plan v1. Elias is drawn to the entrance and stands at the threshold. Both responses cited the correct outcome (`E0233`), exit state (`E0229`) and complete assessed prose (`E0883`). Both identified the relevant final passage within that prose. The historical critique remained bound to the genuine draft in both requests.

| Ending | Frozen gold | Returned | Judgment | Evidence |
| --- | --- | --- | --- | --- |
| Original draft v1 | `uncertain` | `unsupported` | Fail | Fail |
| Authored arrival | `supported` | `supported` | Pass | Pass |

**Original.** Sol located Elias stepping past the shoes and moving “toward the dark, open threshold.” It credited his attraction and concluded that Q011 “incorrectly treats the depicted endpoint as satisfying both.” The sentence establishes direction and motive. It supplies no incompatible position that would contradict standing at the threshold. Sol did not say Elias physically stopped short. Its evidence failed because the explanation settled a question the final passage leaves open.

**Authored arrival.** Sol located the same attraction in the closing paragraph, then identified and quoted the added final sentence, “Elias stood at the threshold.” That observation establishes the physical position required by the separate exit-state field. The full-draft citation was sufficiently precise in both cases. [Verbatim reasons and citations](../../data/diagnostics/q011-arrival-results-2026-11-23/worksheet.json)

The evidence worksheet exposed the case, citations and reason while withholding the returned label field. I inspected those citations in each exact draft, sealed the passage-specific decisions, then joined the labels to gold. The pair required four passing scores. This single observation per ending supports a narrower finding: Sol recognized explicit arrival and overread an ending that showed only approach. Repeatability and literary quality remain unmeasured. [Sealed evidence decisions](../../data/diagnostics/q011-arrival-comparison-2026-11-23/sealed-evidence-decisions.json) · [Frozen gold and witnesses](../../data/diagnostics/q011-arrival-comparison-2026-11-23/gold.json)

## All four live slots

The runner sent the frozen full prose and context to OpenAI. Both counts passed the 16,384-token gate before generation began. Each generation’s reported input matched its pre-count.

| Slot | Case and operation | HTTP | Input tokens | Output tokens | Of which reasoning | Elapsed | Result |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | --- |
| 1 | Original · input count | 200 | 7,968 | — | — | 1.46 s | Admitted |
| 2 | Authored arrival · input count | 200 | 7,983 | — | — | 1.53 s | Admitted |
| 3 | Original · generation | 200 | 7,968 | 594 | 400 | 15.17 s | Complete and eligible |
| 4 | Authored arrival · generation | 200 | 7,983 | 454 | 282 | 10.55 s | Complete and eligible |

Generations used **15,951 input and 1,048 output tokens**, including 682 reasoning tokens and zero cached input tokens. The frozen rates give a generation cost estimate of **$0.0503575** against the $0.16384 ceiling. Actual billing was unavailable. The four requests took 28.72 seconds in total transport time. [Usage and receipt readback](../../data/diagnostics/q011-arrival-results-2026-11-23/delivery-readback.json)

Offline replay verified the approved manifest, both counts, the four request-body hashes, the intent and terminal chains, four distinct provider request IDs, both raw finals and their Q011 bindings. It reproduced the sealed evidence and joined scores. The journal is closed and spent after two counts, two generations and zero retries. B remains the assessment default, with the full workflow canary on hold. [Observed audit](../../data/diagnostics/q011-arrival-results-2026-11-23/audit.json) · [Single-use journal](../../data/diagnostics/q011-arrival-comparison-2026-11-23/output/)
