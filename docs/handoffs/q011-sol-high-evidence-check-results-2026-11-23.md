# Q011 Sol-high B/E results for physical position at the cut

**The frozen decision is `genuine_paired_recovery`. There was no baseline recovery.** On the genuine ending, B again treated movement toward the threshold as evidence against standing there at the cut. E identified what the last sentence establishes about Elias’s movement and what it leaves open about his position. E also recovered the case in which Elias moves again after an observed gap. It retained both scores on the three cases whose endings settle his position. [Frozen plan](q011-sol-high-evidence-check-freeze-2026-11-23.md) · [Joined scores for all five pairs](../../data/diagnostics/q011-evidence-check-results-2026-11-23/scores.json)

## Judgment and evidence for each arm

Both arms assessed the claim “Elias is drawn to the entrance. At the scene cut he stands at the threshold.” Every explanation credited the attraction and distinguished the plan’s assigned exit state from the assessed draft. The difference arose in interpreting the closing action.

| Ending | Gold | B returned | B judgment | B evidence | E returned | E judgment | E evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Genuine approach | `uncertain` | `unsupported` | Fail | Fail | `uncertain` | Pass | Pass |
| Explicit arrival | `supported` | `supported` | Pass | Pass | `supported` | Pass | Pass |
| Explicit stop short | `unsupported` | `unsupported` | Pass | Pass | `unsupported` | Pass | Pass |
| Gap at the cut | `unsupported` | `unsupported` | Pass | Pass | `unsupported` | Pass | Pass |
| Gap before renewed motion | `uncertain` | `unsupported` | Fail | Fail | `uncertain` | Pass | Pass |

**Genuine approach.** Both arms cited the same plan fields, full draft and closing paragraph. B treated “moved toward the dark, open threshold” as a decisive observation against standing there at the cut. E explained that passing the shoes identifies a landmark Elias crossed and moving toward the threshold gives his direction. The paragraph leaves his terminal position unresolved. The baseline reproduced its earlier miss on identical request bytes. E gained both scores in the current pair. [Masked explanations](../../data/diagnostics/q011-evidence-check-results-2026-11-23/worksheet.json) · [Previous genuine-position result](q011-sol-high-scope-results-2026-11-23.md)

**Gap at the cut.** The last sentence places a full stride of bare earth between Elias’s boots and the sill. Both arms tied that measurement to the final instant and correctly ruled out standing at the sill. The distance settles the claim even though the draft never says he stopped. [Exact GC source](../../data/diagnostics/q011-evidence-check-comparison-2026-11-23/witnesses.json)

**Gap before renewed motion.** Here the identical measurement precedes another sentence in which Elias moves toward the entrance. B read the events in the correct order, then used the final movement to reject standing at the threshold. The draft gives no distance traveled after the measurement. E explicitly explained why the earlier gap cannot fix the final position and why the later movement cannot prove arrival. Both scores improved. [Passage-specific evidence decisions](../../data/diagnostics/q011-evidence-check-comparison-2026-11-23/sealed-evidence-decisions.json)

**Arrival and stop short.** For arrival, both arms located the final sentence placing Elias standing at the threshold. B used the full-prose reference and located the sentence precisely. For stop short, both arms located his feet planted a full stride from the sill at the cut. Both controls retained both scores.

E passed **5/5 judgments and 5/5 evidence reviews**. B passed **3/5 on each axis**. The two gains occurred on endings whose final position is unresolved. The three determinate endings had no axis losses. This was one observation per arm in one scene family. Whether the result repeats elsewhere or improves story quality remains open.

## All twenty slots

The registered runner sent the approved full prose and context to both OpenAI endpoints. All ten input counts returned HTTP 200 and passed before generation 11 began. All ten generations returned HTTP 200 from `gpt-6.1-sol`, bound to their own Q011 work and were eligible. Each generation’s reported input matched its paired count. [Slot receipts, request hashes and usage](../../data/diagnostics/q011-evidence-check-results-2026-11-23/delivery-readback.json)

| Slot | Case and arm | Operation | Input tokens | Output tokens | Included reasoning tokens | Seconds |
| ---: | --- | --- | ---: | ---: | ---: | ---: |
| 1 | AP-B | Count | 8,038 | — | — | 1.14 |
| 2 | AP-E | Count | 8,074 | — | — | 0.25 |
| 3 | RP-E | Count | 8,089 | — | — | 0.22 |
| 4 | RP-B | Count | 8,053 | — | — | 0.22 |
| 5 | SP-B | Count | 8,087 | — | — | 0.18 |
| 6 | SP-E | Count | 8,123 | — | — | 1.03 |
| 7 | GC-E | Count | 8,135 | — | — | 0.19 |
| 8 | GC-B | Count | 8,099 | — | — | 0.21 |
| 9 | GM-B | Count | 8,091 | — | — | 0.55 |
| 10 | GM-E | Count | 8,127 | — | — | 0.18 |
| 11 | AP-B | Generation | 8,038 | 419 | 225 | 10.48 |
| 12 | AP-E | Generation | 8,074 | 999 | 757 | 22.13 |
| 13 | RP-E | Generation | 8,089 | 456 | 230 | 10.01 |
| 14 | RP-B | Generation | 8,053 | 492 | 289 | 10.93 |
| 15 | SP-B | Generation | 8,087 | 598 | 378 | 11.17 |
| 16 | SP-E | Generation | 8,123 | 594 | 357 | 11.08 |
| 17 | GC-E | Generation | 8,135 | 551 | 322 | 11.93 |
| 18 | GC-B | Generation | 8,099 | 378 | 158 | 7.33 |
| 19 | GM-B | Generation | 8,091 | 534 | 313 | 11.03 |
| 20 | GM-E | Generation | 8,127 | 1,010 | 784 | 20.56 |

On these five generations per arm, E used 3,610 output tokens and 75.71 seconds, compared with B’s 2,421 output tokens and 50.94 seconds. Total generation usage was **80,916 input and 6,031 output tokens**, including 3,813 reasoning tokens. Reported cached input was zero. Estimated generation cost at the frozen rates was **$0.26260** against the $0.81920 ceiling. Actual billing was unavailable. Summed transport time across all twenty requests was 130.83 seconds.

## Verification

The evidence worksheet withheld arm, slot order and returned label. I checked every explanation against the assigned plan fields and assessed draft, recorded a version-bound passage, instant and relation, and sealed all ten evidence decisions before joining labels to gold. Offline replay verified the approved manifest and exact request bodies, all twenty intent and terminal records, twenty distinct provider request IDs, ten raw finals and the journal closure. The sealed evidence SHA-256 is `b875591aa990325740cf657b4261e41f5e10e900e845553b98ae2e56651cf926`. [Observed audit](../../data/diagnostics/q011-evidence-check-results-2026-11-23/audit.json) · [Raw journal](../../data/diagnostics/q011-evidence-check-comparison-2026-11-23/output/)

The single-use journal is closed and spent after ten counts and ten generations, with zero retries. The three historical depiction controls stayed offline. Production prompts are unchanged and the full workflow canary remains on hold.
