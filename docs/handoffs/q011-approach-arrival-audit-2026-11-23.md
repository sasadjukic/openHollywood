# Q011 audit of approach and arrival

Sol found the right ending. Its error was the move from “the narration ends during an approach” to “the critic is wrong about the final position.” The first observation is grounded. The second requires evidence that Elias was somewhere incompatible with standing at the threshold when the scene cut. The original supplies no such observation. The reported reason does not say that Elias stopped short. [Observed explanations and citations](../../data/diagnostics/q011-arrival-regression-2026-11-23/capture/operator/worksheet.json)

| Ending assessed with baseline B | Frozen factual gold | Sol returned | Judgment | Evidence |
| --- | --- | --- | --- | --- |
| Genuine draft v1 | `uncertain` | `unsupported` | Fail | Fail |
| Authored arrival | `supported` | `supported` | Pass | Pass |

## What the two responses establish

The ordinary Q011 claim says the achieved state matches both assignments. Plan v1 requires that Elias be drawn to the entrance (outcome, `E0233`) and stand at the threshold (exit state, `E0229`). Both responses cited those fields, credited the attraction and located the final passage in the correct version of the complete prose (`E0883`). Standing at the threshold requires no crossing into the building. [Frozen whole claim, versions and evidence criteria](../../data/diagnostics/q011-arrival-regression-2026-11-23/capture/run/gold.json)

**Genuine ending.** Elias steps past the circle of shoes and moves “toward the dark, open threshold.” The shoes establish a point he passed. The threshold is his destination. The final sentence spans code points 3129–3284, ending at the cut. The prose does contain “Elias stopped.” at 1470–1484, but “He stepped forward” follows at 1595, well before his final movement. That earlier stop cannot settle his position at the cut. Sol's reason says the review “incorrectly treats the depicted endpoint as satisfying both.” That last inference cost the evidence point independently of its returned label. [Original source packet](../../data/diagnostics/q011-arrival-regression-2026-11-23/capture/source/A.json) · [Sealed evidence decisions](../../data/diagnostics/q011-arrival-regression-2026-11-23/capture/run/sealed-evidence-decisions.json)

**Authored arrival.** The diagnostic version preserves every character of the original and adds one space and “Elias stood at the threshold.” Sol cited that new final observation (3285–3314) for the assigned position. Both the approach and the attraction are present here too. The added sentence settles the authored ending. It supplies no retrospective fact about the genuine one. [Authored source packet](../../data/diagnostics/q011-arrival-regression-2026-11-23/capture/source/B.json)

## Why the negative judgment was plausible

B defines `unsupported` as a material part contradicted by supplied evidence. The complete draft was available. Its account leaves one material fact undetermined. The brief also asks how the **depicted ending** compares with the plan, and the reviewer calls this the **achieved state**. Sol’s repeated appeal to what was *depicted* is consistent with assessing whether the closing paragraph shows fulfillment. A reader can reasonably say that arrival was never shown. Under the frozen factual gold, this observation leaves the position open. An assessor can record that limit without directing the writer to add a sentence. [Frozen instructions and brief](../../data/diagnostics/q011-arrival-regression-2026-11-23/capture/run/requests/A-B-generation.json)

This is an inference from the returned explanations and paired drafts. With one response per ending, the cause and frequency of the error remain open. The earlier P01 comparison saw a similar overread with B on the same passage, but the proposition there was whether **crossing had begun**. Both arms correctly handled P07, whose complete draft preserves the original and adds a final stop “a full stride short of the sill.” Both also handled fresh R06, where a hood obscured the destination at a later bell. P07 offers a candidate negative control for Q011. Its prior score belongs to the crossing claim. [P01 and P07 results](q010-paired-uncertainty-results-2026-11-23.md) · [P07 source packet](../../data/diagnostics/q010-endpoint-controls-2026-11-23/frozen/packets/P07.json) · [R06 results](q010-fresh-endpoint-repeat-results-2026-11-23.md)

## Preserved regressions and verification

The private archive contains 26 sealed members. It preserves the original 19 run files, all five operator records, and two source-only packets reconstructed from the registered inputs. The 24 copied files matched the originals byte for byte. The manifest SHA-256 is `6fd99ab0749bdc1c47f2c9e9270b96cf7200ab34ceb7f0c7a004aeb42813c4b2`. The verifier rebuilds both requests for each draft, checks the spent journal and all four observed outcomes, binds the two raw finals to Q011, and reproduces the original evidence worksheet and independently joined scores. Decision **`hold`**. [Archive manifest](../../data/diagnostics/q011-arrival-regression-2026-11-23/capture-manifest.json) · [Offline verifier](../../scripts/q011_arrival/regression.py)

Run `python -m scripts.q011_arrival.regression` with the repository interpreter. The six archive tests passed with networking blocked, including rejection of a swapped generation, a substituted source packet and removal of the sealed evidence decision, gold or score file. The focused evaluation suite passed all 147 tests, including those six. All 15 Q011 harness tests passed using local fixtures. Ruff lint, format and strict mypy passed. The private capture is required for exact replay. The six archive tests skip on checkouts without it. No provider calls were made in this audit. [Regression tests](../../tests/evaluations/test_q011_arrival_regression.py) · [Evaluation results](../../data/diagnostics/q011-arrival-regression-2026-11-23/verified.xml) · [Harness results](../../data/diagnostics/q011-arrival-regression-2026-11-23/q011-harness.xml)

## Recommended next step

**Rehearse two explicit claims locally against three endings.** Keep attraction established in each. Ask once about Elias’s physical position at the cut and once whether the complete closing paragraph gives an observation placing him there. Treat equivalent descriptions of position as evidence. Use the genuine cut, the existing authored arrival and the explicit stop from P07. Give the stop its own Q011 assessment binding and gold. P07’s earlier score applies to Q010.

| Ending | Elias stands at the threshold at the cut | The closing paragraph depicts Elias standing there |
| --- | --- | --- |
| Original approach | Uncertain | Unsupported |
| Authored arrival | Supported | Supported |
| Explicit stop a stride short | Unsupported | Unsupported |

These are proposed expectations. Qualify them locally before freezing anything. For the physical claim, a contradiction needs an incompatible observation at the specified instant. For the coverage claim, inspect the complete declared paragraph for an observation establishing the position. Score the judgment and its evidence separately. If a reasonable reading still makes the two claims indistinguishable, hold the comparison.

If the scopes qualify, propose **six counts before up to six Sol-high B generations, zero retries**, for separate approval. Keep the draft, plan, model, schema and assessment instructions fixed within each pair and vary only the claim’s subject. The original is the discriminating case. The two authored endings test whether the distinction preserves clear positive and negative judgments. B remains the default. Live work and the full workflow canary stay on hold.
