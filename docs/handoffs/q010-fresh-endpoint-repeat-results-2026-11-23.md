# Fresh-family B/C repeat results

**Baseline B and clarified C each passed whole-claim correctness and evidence adequacy on all eight fresh cases.** The fresh destination and identity cases were both retained baseline passes. All six controls passed both axes in both arms. The frozen decision is `no_recovery_headroom`: this run observed zero fresh recoveries and zero control regressions. It used all 16 counts and all 16 generations with zero retries. [Frozen plan and decision rule](q010-fresh-endpoint-repeat-freeze-2026-11-23.md)

## Movement to a destination · R06

**Retained pass, zero recovery.** Both arms returned `uncertain`. Both credited Lale with stamping the slip and located the passage in which the pouch travels toward the pan and disappears behind the copper hood. At the closing bell the inspection hole shows Lale’s reflection. That leaves the pouch’s final location open. Both arms cited S01 for the earlier observation, S02 for the depicted movement and S03 for the completeness of the draft. C ran first on this case. [R06 source packet](../../data/diagnostics/q010-fresh-controls-2026-11-23/frozen/packets/R06.json)

The earlier P01 recovery remains specific to its observed pair: B called entering the threshold a misstatement and C correctly left crossing unresolved. P01 asks whether crossing **has begun** when the narration ends on movement toward the sill. R06 asks whether the pouch **is in the pan** at a later bell, after the narration explicitly hides it from view. Claim wording and the visibility of the endpoint both vary between the cases. This run cannot attribute the different baseline outcomes to either feature. [Earlier threshold result](q010-paired-uncertainty-results-2026-11-23.md)

## Identity of the holder · R02

**Retained pass, zero recovery.** Both arms returned `uncertain`. The eyewitness and the opening passage establish that Orsa broke the seal. Both setters then went behind the partition. At shutter closure, the chip in the glass reveals the stick’s nick and four fingertips. Both answers identified the object, explained why the fingertips leave either setter possible, and correctly described the complete draft as available. B ran first on this case. [R02 source packet](../../data/diagnostics/q010-fresh-controls-2026-11-23/frozen/packets/R02.json)

## All eligible scores

Each label shown below was independently returned by both arms and matched the presealed whole-claim gold. Evidence decisions were recorded separately for each of the 16 responses.

| Case and decisive evidence | Returned label, B and C | B claim / evidence | C claim / evidence |
| --- | --- | --- | --- |
| R01 · Pouch visible in the pan at the bell | supported | Pass / Pass | Pass / Pass |
| R02 · The nick and fingertips leave the holder unidentified | uncertain | Pass / Pass | Pass / Pass |
| R03 · Witness saw the stamp. Inventory records the missing draft. | uncertain | Pass / Pass | Pass / Pass |
| R04 · Sabin alone holds the stick. Neri shows two empty hands. | unsupported | Pass / Pass | Pass / Pass |
| R05 · Witness saw the seal break, then went downstairs. Draft missing. | uncertain | Pass / Pass | Pass / Pass |
| R06 · Pouch travels behind the hood. Final location is unseen. | uncertain | Pass / Pass | Pass / Pass |
| R07 · Neri holds the nicked stick in her left hand at shutter closure | supported | Pass / Pass | Pass / Pass |
| R08 · Pouch caught upstream of the empty pan at the bell | unsupported | Pass / Pass | Pass / Pass |

For R03 and R05, both arms cited the earlier witness and inventory, explaining why the final instant could not be checked. On the contradicted cases they each located an incompatible fact at the specified instant. On the confirmed cases they located the observation that established the second clause. [All returned reasons and citations](../../data/diagnostics/q010-fresh-endpoint-repeat-results-2026-11-23/audit.json) · [Per-arm scores and evidence decisions](../../data/diagnostics/q010-fresh-endpoint-repeat-results-2026-11-23/scores.json)

## Scoring and delivery verification

I first read the 16 verbatim reasons and cited sources against the sealed witnesses using the worksheet’s opaque response IDs. The worksheet withheld arm, dispatch order and the returned label field. Some reasons gave a conclusion in prose. I recorded a passage-specific basis for each evidence decision, sealed the decisions with the frozen scoring command, then joined the returned labels to gold. The scorer validated 16 unique eligible decisions against the approval and worksheet digests. [Masked worksheet](../../data/diagnostics/q010-fresh-endpoint-repeat-results-2026-11-23/worksheet.json) · [Sealed decisions](../../data/diagnostics/q010-fresh-repeat-2026-11-23/sealed-evidence-decisions.json) · [Scorer gold](../../data/diagnostics/q010-fresh-controls-2026-11-23/frozen/gold.json)

| Record | SHA-256 |
| --- | --- |
| Approved manifest | `983b8beb98385a8034c8429c92ae2b7bfc5f47bc18079fc6a1568df892284414` |
| Masked worksheet rows | `e9edb60217e21bd55dff7b9e88d858bd2bfb31cbee9b2dcb1738725d64541d34` |
| Evidence decisions sealed before label join | `6dbb5f2eb638c9fdacba1fa1dc8096b1c2c58b8d1c72ccc67cca0b6751d25541` |
| Joined scores | `a7d3ba7754134051440cdb2d083a2d7dcd673c0b4d26f182e7a69f9247ca82df` |

The journal opened at 08:38:17 UTC on November 23, 2026. All 16 input counts passed before the first generation. All 32 POSTs sent the frozen full prose and context to their designated OpenAI endpoints and returned HTTP 200 with distinct provider request IDs. All 16 generations bound to the correct work and claim on `gpt-6.1-sol` with high reasoning requested. Each generation’s reported input usage matched its preceding count. Replay checked the request bodies, destinations, terminal hashes and closing chain. The live journal is closed and spent. [Fixed-slot inspection](../../data/diagnostics/q010-fresh-endpoint-repeat-results-2026-11-23/inspection.json) · [Original journal](../../data/diagnostics/q010-fresh-repeat-2026-11-23/output/)

| Cell | Count / generation slot | Input tokens | Output tokens | Included reasoning tokens | Count / generation seconds |
| --- | --- | ---: | ---: | ---: | ---: |
| R01-B | 1 / 17 | 1,769 | 297 | 144 | 1.08 / 6.38 |
| R01-C | 2 / 18 | 1,789 | 291 | 142 | 0.19 / 5.67 |
| R02-B | 3 / 19 | 1,808 | 484 | 249 | 0.87 / 9.76 |
| R02-C | 4 / 20 | 1,828 | 549 | 315 | 0.18 / 17.27 |
| R03-C | 5 / 21 | 1,415 | 459 | 251 | 0.19 / 8.81 |
| R03-B | 6 / 22 | 1,395 | 423 | 212 | 0.16 / 8.71 |
| R04-C | 7 / 23 | 1,824 | 330 | 164 | 0.23 / 12.29 |
| R04-B | 8 / 24 | 1,804 | 286 | 119 | 0.20 / 45.31 |
| R05-B | 9 / 25 | 1,377 | 481 | 271 | 0.20 / 9.37 |
| R05-C | 10 / 26 | 1,397 | 383 | 180 | 0.15 / 7.30 |
| R06-C | 11 / 27 | 1,812 | 481 | 250 | 0.21 / 10.69 |
| R06-B | 12 / 28 | 1,792 | 501 | 262 | 0.20 / 10.57 |
| R07-C | 13 / 29 | 1,805 | 233 | 87 | 0.24 / 11.54 |
| R07-B | 14 / 30 | 1,785 | 271 | 105 | 0.17 / 6.23 |
| R08-B | 15 / 31 | 1,789 | 354 | 176 | 0.17 / 6.67 |
| R08-C | 16 / 32 | 1,809 | 279 | 120 | 0.19 / 5.76 |

Generation used **27,198 input and 6,102 output tokens**, including **3,047 reasoning tokens**, with zero cached input tokens reported. C added 20 input tokens per case. Summed request latency was 4.64 seconds for counts and 182.36 seconds for generations. The estimated generation cost at the frozen rates was **$0.129015** against the **$0.98304** ceiling. Actual billing was unavailable. [Offline result replay](../../data/diagnostics/q010-fresh-endpoint-repeat-results-2026-11-23/export_results.py)

## Recommended next steps

1. **Retain B as the default.** Preserve P01 as a diagnostic recovery and the fresh R06 and R02 pairs as examples of baseline success. With one observation per arm per case, the fresh data establish correct handling of these scenes and leave C’s incremental benefit unmeasured. The frozen criterion for advancing C was unmet.
2. **Audit the harder distinction locally.** Compare P01 and R06, then inspect up to six previously unassessed ordinary-review claims, in a fixed intake order. Record the exact claim, draft version, narrative instant, and whether the claim asserts motion underway or an achieved destination. Record separately whether the text explicitly obscures the endpoint or simply ends during the motion. Admit only whole factual claims with defensible gold and exact passage witnesses. Keep judgments about how an ending feels with editorial review.
3. **Condition further inference on that audit.** If a fresh ordinary claim with a genuinely unresolved endpoint qualifies, freeze its gold before assessor output and propose a bounded comparison that isolates the distinction the audit found. If none qualifies, record the gap and close this wording experiment with its captures preserved. Production prompts remain unchanged, live calls are paused and the full workflow canary remains on hold.
