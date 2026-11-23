# Sol-high B/E transfer results · position at the scene cut

**The frozen decision is `cross_family_recovery`.** With one added question about the draft observation and when it applies, E passed judgment and evidence on all eight cases. B passed both on five. E recovered all three baseline misses, including an approach in each family. Both arms passed all four determinate controls. [Approved plan](q011-sol-high-transfer-freeze-2026-11-23.md) · [Joined scores](../../data/diagnostics/q011-transfer-results-2026-11-23/scores.json)

## All eight pairs

Both arms assessed whether the assigned first action occurred and whether the subject occupied the assigned position at the cut. The stage claim requires Iven to fasten his cuff and stand on the blue star. The harbor claim requires Runa to hoist the pennant and the skiff’s bow to be level with the white post. All sixteen explanations located both plan requirements and the depicted first action. The three failures concerned the final position. [Masked explanations and source fields](../../data/diagnostics/q011-transfer-results-2026-11-23/worksheet.json)

| Case and ending | Gold | B returned | B judgment | B evidence | E returned | E judgment | E evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| T01 · Stage, approach | uncertain | unsupported | Fail | Fail | uncertain | Pass | Pass |
| T02 · Harbor, approach | uncertain | unsupported | Fail | Fail | uncertain | Pass | Pass |
| T03 · Stage, arrival | supported | supported | Pass | Pass | supported | Pass | Pass |
| T04 · Harbor, alignment | supported | supported | Pass | Pass | supported | Pass | Pass |
| T05 · Stage, gap at cut | unsupported | unsupported | Pass | Pass | unsupported | Pass | Pass |
| T06 · Harbor, gap at cut | unsupported | unsupported | Pass | Pass | unsupported | Pass | Pass |
| T07 · Stage, gap before renewed motion | uncertain | unsupported | Fail | Fail | uncertain | Pass | Pass |
| T08 · Harbor, gap before renewed motion | uncertain | uncertain | Pass | Pass | uncertain | Pass | Pass |

### The four unresolved endings

- **T01, Iven walking toward the star.** B cited the correct closing paragraph and treated walking toward the mark as contradicting standing there at the cut. E distinguished the walking action from its unspecified terminal position. Both scores improved.
- **T02, the skiff approaching the post.** B and E cited the same four locations. B inferred that the bow was still short of the post. E identified upstream direction and the absence of a final bow position. Both scores improved, including with E presented first.
- **T07, Iven moving after a measured gap.** The paragraph places both shoes a board’s width upstage and then says Iven walked on. B used that sequence to exclude standing on the star at the cut. E correctly limited the separation to the earlier observation and recognized that the later travel distance was unspecified. Both scores improved.
- **T08, the skiff moving after a measured gap.** B already distinguished a boat-length gap observed before the last pull from the unknown alignment after it. E did likewise. Both scores were retained. The earlier-gap recovery therefore occurred in the stage family only.

The approach recovery appeared in **both** families, with opposite arm orders. The four determinate controls also distinguished chronology correctly. An explicit final placement established the claim in T03 and T04. A measured separation that still held at the cut contradicted it in T05 and T06. Across all eight pairs there were three gains and five retained passes on each axis, with zero losses. The baseline joint passes were T03, T04, T05, T06 and T08. [Sealed passage-specific decisions](../../data/diagnostics/q011-transfer-comparison-2026-11-23/sealed-evidence-decisions.json)

## Delivery and resource use

Full prose and context were sent to the two approved OpenAI endpoints. All sixteen serial counts returned HTTP 200 and passed before generation began. Each generation returned HTTP 200 from `gpt-6.1-sol`, matched its own count exactly and bound to the correct request, claim and source versions. All sixteen were eligible. The audit verified all 32 intents and terminals, 32 distinct provider request IDs, the exact frozen bodies and the closed, spent journal. Zero retries. [All 32 slots, hashes, timings and usage](../../data/diagnostics/q011-transfer-results-2026-11-23/delivery-readback.json) · [Observed audit](../../data/diagnostics/q011-transfer-results-2026-11-23/audit.json)

| Generations | Input tokens | Output tokens | Reasoning tokens included in output | Summed generation time | Estimated generation cost |
| --- | ---: | ---: | ---: | ---: | ---: |
| B · 8 | 12,374 | 3,946 | 2,391 | 79.84 s | $0.070395 |
| E · 8 | 12,694 | 6,733 | 4,962 | 134.99 s | $0.099065 |
| Total · 16 | 25,068 | 10,679 | 7,353 | 214.84 s | $0.169460 |

The sixteen counts took another 6.28 seconds in total. Reported cached input was zero. The cost estimate uses the frozen repository rates and falls within the $1.31072 generation ceiling. Actual billing was unavailable. Most of E’s extra output came from T01, which used 2,247 output tokens and 45.13 seconds under E, compared with 440 tokens and 9.86 seconds under B. These are measurements from one generation per arm and case.

## Evidence review and production decision

The evidence worksheet masked arm, returned label and dispatch order. Each decision recorded the cited first-action and position spans in the exact draft version, the timing, the inferred relation and the reason for the score. All sixteen evidence decisions were sealed before joining judgments to gold. Evidence seal SHA-256 is `78cb8814c7b1cfa58023f89862e3493faa42fbced7b7c1beac065d9cfaf93955`. [Scoring form](../../data/diagnostics/q011-transfer-results-2026-11-23/evidence-form.json) · [Frozen gold](../../data/diagnostics/q011-transfer-comparison-2026-11-23/gold.json) · [Raw journal](../../data/diagnostics/q011-transfer-comparison-2026-11-23/output/)

**Retain E as a candidate for factual claims about position at a stated instant. Keep B as the default.** These two authored families extend the earlier Elias result. They provide one observation per arm in each case and measure factual assessment only. Writer revisions and reader judgments of story quality require separate evidence. The five historical pairs stayed offline. [Earlier Elias result](q011-sol-high-evidence-check-results-2026-11-23.md)

The next bounded step is local. Preserve the eight pairs as regressions, including T08’s baseline pass. Inspect up to six saved ordinary-review claims for a physical endpoint tied to a specific instant and a complete, version-bound draft. Record which claims would receive E under that rule and which would retain B, including editorial or depiction-only claims. This would establish whether ordinary reviews contain suitable cases for selective use before proposing another live comparison. Production prompts remain unchanged and the full workflow canary stays on hold.
