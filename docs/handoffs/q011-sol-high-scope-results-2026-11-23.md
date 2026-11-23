# Q011 Sol-high results for physical position and paragraph depiction

**The frozen decision is `hold`.** On the genuine ending, Sol returned `unsupported` for both claims. That was correct for the claim about what the paragraph depicts. For the claim about Elias’s physical position, the gold was `uncertain`. Sol cited the right passage and credited his attraction to the entrance, then treated the last narrated approach as sufficient evidence against his standing at the threshold. The four authored controls passed both judgment and evidence. [Frozen comparison](q011-sol-high-scope-freeze-2026-11-23.md) · [Joined scores](../../data/diagnostics/q011-scope-results-2026-11-23/scores.json)

## Original approach

| Case | Frozen gold | Sol returned | Judgment | Evidence |
| --- | --- | --- | --- | --- |
| AP · Elias stands at the threshold at the cut | `uncertain` | `unsupported` | Fail | Fail |
| AD · The closing paragraph depicts him standing there | `unsupported` | `unsupported` | Pass | Pass |

**Physical position.** The final sentence says Elias passed the shoes and “moved toward the dark, open threshold.” Sol correctly attributed standing at the threshold to the plan and attraction to the draft. Its reason then asserted, “At the final narrated instant, he is approaching,” and judged the claim of an achieved position incorrect. The passage supplies his direction and motive. It contains no final observation that places him short of the threshold. That missing basis for contradiction independently costs the evidence point.

**Paragraph depiction.** Here the entire paragraph is available for inspection. Sol located the motion toward the threshold and explained that the paragraph ends without depicting Elias standing there. This answers the textual claim. Both responses cited the same outcome (`E0233`), exit state (`E0229`), full draft (`E0883`) and closing paragraph (`D01`) in the correct versions. The difference in evidence credit comes from what each claim asks those sources to establish. [Verbatim reasons and citations](../../data/diagnostics/q011-scope-results-2026-11-23/worksheet.json) · [Exact source witnesses](../../data/diagnostics/q011-scope-comparison-2026-11-23/witnesses.json)

## Clear controls

| Case | Frozen gold | Sol returned | Judgment | Evidence | Decisive observation Sol located |
| --- | --- | --- | --- | --- | --- |
| RD · Arrival, paragraph depiction | `supported` | `supported` | Pass | Pass | The paragraph concludes, “Elias stood at the threshold.” |
| RP · Arrival, physical position | `supported` | `supported` | Pass | Pass | The same final sentence establishes his position at the cut. |
| SP · Stop short, physical position | `unsupported` | `unsupported` | Pass | Pass | He stops a full stride short of the sill, both feet planted in the dirt. |
| SD · Stop short, paragraph depiction | `unsupported` | `unsupported` | Pass | Pass | The complete paragraph depicts approach followed by that explicit stop short. |

Each control credited the depicted attraction, distinguished the two plan assignments and located the final observation in its own assessed draft. The authored endpoints supply decisive evidence in both scopes. On the genuine ending, Sol answered the separately worded paragraph claim correctly. Its definite negative on the physical-position claim repeated the earlier overread of the same passage. Each case received one generation. Repeatability, transfer to other stories and story quality remain open. [Previous Q011 result](q011-sol-high-arrival-results-2026-11-23.md) · [Sealed evidence decisions](../../data/diagnostics/q011-scope-comparison-2026-11-23/sealed-evidence-decisions.json)

## All twelve slots

The runner sent full prose and context to OpenAI’s input-count and Responses endpoints. All six counts passed before slot 7 dispatched. All six generations completed with `gpt-6.1-sol` at high reasoning and bound to their own `Q011-scope` request. Each generation’s reported input matched its count.

| Slot | Case | Operation | HTTP | Input tokens | Output tokens | Included reasoning tokens | Seconds |
| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: |
| 1 | AP | Count | 200 | 8,038 | — | — | 0.99 |
| 2 | AD | Count | 200 | 8,046 | — | — | 0.95 |
| 3 | RD | Count | 200 | 8,061 | — | — | 0.24 |
| 4 | RP | Count | 200 | 8,053 | — | — | 0.20 |
| 5 | SP | Count | 200 | 8,087 | — | — | 0.20 |
| 6 | SD | Count | 200 | 8,095 | — | — | 0.25 |
| 7 | AP | Generation | 200 | 8,038 | 539 | 354 | 12.01 |
| 8 | AD | Generation | 200 | 8,046 | 648 | 432 | 11.88 |
| 9 | RD | Generation | 200 | 8,061 | 525 | 330 | 11.02 |
| 10 | RP | Generation | 200 | 8,053 | 370 | 170 | 7.96 |
| 11 | SP | Generation | 200 | 8,087 | 508 | 300 | 11.02 |
| 12 | SD | Generation | 200 | 8,095 | 466 | 242 | 8.64 |

Generations used **48,380 input and 3,056 output tokens**, including 1,828 reasoning tokens. Reported cached input was zero. The frozen rates give an estimated generation cost of **$0.12732** against the **$0.49152** ceiling. Actual billing was unavailable. Summed transport time for all twelve slots was 65.36 seconds. [Slot receipts and usage](../../data/diagnostics/q011-scope-results-2026-11-23/delivery-readback.json)

## Verification

I inspected the six reasons with the returned label field withheld, resolved each cited field against its exact plan and draft version, and sealed the six evidence decisions before comparing the labels with gold. Offline replay checked the approved manifest, all twelve request bodies, the intent, terminal and closure hashes, twelve distinct provider request IDs, and the six raw finals and their active-claim bindings. The single-use journal is closed and spent after six counts, six generations and zero retries. Production prompts remain unchanged and the full workflow canary remains on hold. [Observed audit](../../data/diagnostics/q011-scope-results-2026-11-23/audit.json) · [Single-use journal](../../data/diagnostics/q011-scope-comparison-2026-11-23/output/)
