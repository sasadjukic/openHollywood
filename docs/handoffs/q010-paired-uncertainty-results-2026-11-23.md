# Sol-high B/C comparison results

**The uncertainty clarification met the frozen criterion for a fresh repeat.** Baseline B passed whole-claim correctness and evidence adequacy on 7 of 8 cases. Clarified C passed both on 8 of 8. The sole recovery was P01, the previously known Elias threshold case. Both arms already passed the other open ending and all six controls. The run used 16 counts and 16 generations with zero retries. [Frozen comparison and decision rule](q010-paired-uncertainty-freeze-2026-11-23.md)

## All eight eligible pairs

B used the original wording. C added “Material evidence can be unavailable even when the relevant source is complete but leaves the material fact undetermined.” The source text, brief and schema were fixed within each pair. Each arm had one observation per case.

| Case and final-instant evidence | Frozen gold | B label | B claim | B evidence | C label | C claim | C evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| P01 · Elias moves toward the threshold | uncertain | unsupported | **Fail** | **Fail** | uncertain | Pass | Pass |
| P02 · Both wings are motionless at the flash | unsupported | unsupported | Pass | Pass | unsupported | Pass | Pass |
| P03 · Witness saw Elias pass the shoes, then turned away. Draft missing. | uncertain | uncertain | Pass | Pass | uncertain | Pass | Pass |
| P04 · Moth lifts and lowers its wings at the flash | supported | supported | Pass | Pass | supported | Pass | Pass |
| P05 · One foot is crossing the sill | supported | supported | Pass | Pass | supported | Pass | Pass |
| P06 · The flash reveals silver crescents on the wings | uncertain | uncertain | Pass | Pass | uncertain | Pass | Pass |
| P07 · Elias stops a full stride short with both feet planted | unsupported | unsupported | Pass | Pass | unsupported | Pass | Pass |
| P08 · Witness saw Inez lift the cover, then left. Draft missing. | uncertain | uncertain | Pass | Pass | uncertain | Pass | Pass |

**Why P01 changed.** Both responses cited the same three sources, gave their correct versions and located the final movement. B credited Elias with passing the shoes and correctly observed that the complete draft ends with him moving toward the threshold. It then said that “is entering” **“therefore misstates that action.”** The draft gives no final position incompatible with beginning to cross. B missed the label and the separate evidence requirement to explain what remains unsettled. C explicitly said the passage **“neither establishes nor decisively rules out that crossing.”** It credited the earlier action, identified the limit of the final sentence and returned `uncertain`. The difference was in how the two answers interpreted the same passage. [Exact gold and witnesses](../../data/diagnostics/q010-endpoint-controls-2026-11-23/frozen/gold.json)

The earlier Q010 smoke is a separate delivery. Its explanation earned evidence credit for identifying where the depiction ended. This B response went further in calling the entering claim a misstatement. The four-way control set also had an explicit, pre-frozen requirement to identify what an open passage leaves unsettled. Both evidence decisions remain attached to the response and rubric that produced them. [Earlier Q010 scores](q010-sol-high-smoke-results-2026-11-22.md)

**Where the distinction held.** In P06 both arms explained that the silver markings could be visible with wings moving or still. In P03 and P08 each cited the eyewitness for the first action and the inventory for the missing draft, and explained why the witness could not establish the endpoint. In P02 and P07 each located a fact incompatible with the claim at the specified instant. In P04 and P05 each located the action in progress. There were zero control losses on either axis.

## Independent scoring and verification

The scorer read all 16 reasons and citations alongside the sealed source witnesses. The worksheet withheld arm, dispatch order and the returned label field and sorted rows by opaque response ID. Some explanations spelled out a conclusion in prose. The scorer recorded a separate evidence decision and passage basis for each ID, then sealed the file before joining arms and comparing labels with gold. Exactly one evidence decision failed. All 16 joined deliveries were eligible. [Masked worksheet](../../data/diagnostics/q010-paired-uncertainty-results-2026-11-23/evidence-sheet.json) · [Sealed evidence decisions](../../data/diagnostics/q010-paired-uncertainty-results-2026-11-23/evidence-decisions.json) · [Both scores, citations and verbatim reasons](../../data/diagnostics/q010-paired-uncertainty-results-2026-11-23/scores.json)

| Verification record | SHA-256 |
| --- | --- |
| Approved plan | `3600fc37fcd142cd1fe733895f19c77a1ca4a1aa0595d18c4481524840869729` |
| Previously sealed gold | `494cd0b61fa0ebddf5506377819f306b231ba32001595dc19d0b7809cd997633` |
| Masked worksheet | `7d5df3817712d97b927e175cb8778c9f3499f95eca48af4615a8174041e479bf` |
| Evidence decisions before label join | `617bb1da27c037aa27312aa19e1abe7cd1b312a81303d632b77cdec644690153` |

## All 32 fixed slots

The journal opened at 08:10:29 UTC on November 23, 2026. All 16 count POSTs returned HTTP 200 and passed the gate before generation began. All 16 generation POSTs returned HTTP 200 with a completed `gpt-6.1-sol` response bound to the exact active claim and request. Reasoning was set to `high`. Every generation reported the same input usage as its corresponding count. The audit verified the manifest, request bytes, response hashes and closing chain. All 32 provider request IDs were distinct. The single-use journal is spent. [All slot records](../../data/diagnostics/q010-paired-uncertainty-results-2026-11-23/audit.json) · [Original intents and terminals](../../data/diagnostics/q010-paired-uncertainty-2026-11-23/output/)

| Case and arm | Count / generation slot | Counted and used input tokens | Output tokens | Included reasoning tokens | Count / generation seconds |
| --- | --- | ---: | ---: | ---: | ---: |
| P01-B | 1 / 17 | 2,974 | 696 | 491 | 1.40 / 17.39 |
| P01-C | 2 / 18 | 2,994 | 469 | 236 | 0.21 / 8.47 |
| P02-B | 3 / 19 | 1,746 | 380 | 208 | 0.21 / 7.63 |
| P02-C | 4 / 20 | 1,766 | 313 | 141 | 1.89 / 5.42 |
| P03-C | 5 / 21 | 1,391 | 489 | 279 | 0.20 / 9.41 |
| P03-B | 6 / 22 | 1,371 | 393 | 191 | 0.25 / 9.04 |
| P04-C | 7 / 23 | 1,779 | 401 | 233 | 0.20 / 8.82 |
| P04-B | 8 / 24 | 1,759 | 335 | 179 | 0.18 / 7.73 |
| P05-B | 9 / 25 | 3,010 | 386 | 217 | 0.23 / 7.27 |
| P05-C | 10 / 26 | 3,030 | 322 | 150 | 0.18 / 6.86 |
| P06-C | 11 / 27 | 1,757 | 480 | 250 | 0.15 / 9.62 |
| P06-B | 12 / 28 | 1,737 | 477 | 257 | 0.27 / 10.05 |
| P07-C | 13 / 29 | 3,030 | 311 | 138 | 0.17 / 6.61 |
| P07-B | 14 / 30 | 3,010 | 350 | 174 | 0.18 / 6.97 |
| P08-B | 15 / 31 | 1,365 | 465 | 266 | 0.16 / 9.88 |
| P08-C | 16 / 32 | 1,385 | 586 | 386 | 0.19 / 11.02 |

Generations used **34,104 input and 6,853 output tokens**, including **3,796 reasoning tokens**, with zero cached input tokens reported. The clarification added exactly 20 counted input tokens to each case. The frozen rates give an estimated generation cost of **$0.15379** against the $0.98304 ceiling. Actual billing was unavailable. Summed request latency was 6.05 seconds for counts and 142.17 seconds for generations. [Offline scoring and replay](../../data/diagnostics/q010-paired-uncertainty-results-2026-11-23/score_and_verify.py)

## Decision

**Prepare a fresh paired repeat locally.** Use new scene families and include an ending where motion toward a destination leaves arrival open, alongside explicit confirmation, same-instant contradiction and missing-source controls. Keep the B/C wording, separate scores and counterbalanced order, and seal the new gold before inference. The present comparison supplies one recovery on a known case. Transfer to other ordinary reviews and effects on story quality remain unmeasured. Production prompts remain unchanged and the full workflow canary is on hold.
