# Q011 audit of the evidence needed to rule out arrival

**The stop-short draft rules out Elias standing at the threshold at the cut. The genuine draft leaves his position open.** What makes the negative judgment defensible is the final observation that Elias is “a full stride short of the sill.” Stopping tells us what his body is doing. The distance tells us where he is, and the sentence places him there at the instant under assessment. The genuine ending gives a direction of travel and a motive, with no corresponding observation of distance or position. [Version-bound passages and offsets](../../data/diagnostics/q011-scope-regression-2026-11-23/witness-audit.json)

## What each passage can establish

Elias is drawn to the entrance in all three drafts. The disputed physical claim is **“At the scene cut he stands at the threshold.”** The sill is the relevant landmark and the cut is the relevant instant. Location and posture matter separately. For example, a character kneeling on the sill has reached it, although that posture contradicts standing there. The actual stop-short control settles location directly. It establishes where Elias is at the cut and leaves any claim about an earlier visit to be evaluated separately. Beginning to cross or entering the building would also require its own evidence. [Frozen claims and gold](../../data/diagnostics/q011-scope-regression-2026-11-23/capture/run/gold.json)

| Source or passage inspected | What it establishes | Effect on the physical claim |
| --- | --- | --- |
| Scene Plan v1 assigns attraction and standing at the threshold | The intended outcome and exit state | The assignment gives no observation of fulfillment. |
| Genuine draft, “Elias stopped.” at 1470–1484, followed by “He stepped forward” at 1595–1613 | He stopped earlier and resumed moving | The stop has the wrong time and gives no position relative to the sill. |
| “He stepped past the circle of shoes” at 3129–3164 | Elias passed a specific landmark | That landmark is the circle of shoes. The passage records no crossing of the threshold. |
| “moved toward the dark, open threshold” at 3169–3206 | The threshold is his destination | Approach is a reasonable reading of the action. It leaves his exact position at the cut unresolved. |
| Entire genuine closing paragraph at 3085–3284 | The paragraph depicts attraction and approach and ends there | Its completeness settles the claim about what it depicts. It supplies no physical fact incompatible with standing at the threshold. |
| Authored arrival, “Elias stood at the threshold.” at 3285–3314 | His final position and posture | Direct support for the physical claim and its depiction. |
| Authored stop, “He came to a standstill a full stride short of the sill, both feet planted in the dirt.” at 3285–3372 | Elias stops at a measured distance from the threshold at the cut | Direct contradiction of the physical claim. “Came to a standstill” alone would leave his location open. |

Offsets are Unicode code points in each version’s complete prose, with the end excluded. Both authored drafts retain every character of the genuine draft, then append one sentence. Their opposite final observations illustrate the information missing from the common approach. Neither addition establishes where the original Elias actually ended up. [Sealed source packets](../../data/diagnostics/q011-scope-regression-2026-11-23/capture/source/) · [Source witnesses](../../data/diagnostics/q011-scope-regression-2026-11-23/capture/run/witnesses.json)

For a factual negative, ask what observation makes the target position impossible **for this character, at this landmark, at this instant**. A final distance can do this while a character is still moving. An earlier observation could also suffice if the draft establishes that it continues through the cut. A correct citation, a missing verb, or a plan instruction does not settle that relation. This standard accepts paraphrase and ordinary narrative implication when the implication actually excludes the claimed position. It gives the writer room to leave the ending open.

## The six preserved regressions

| Ending | Subject | Frozen gold | Sol returned | Judgment | Evidence |
| --- | --- | --- | --- | --- | --- |
| Genuine approach | Physical position | `uncertain` | `unsupported` | Fail | Fail |
| Genuine approach | Paragraph depiction | `unsupported` | `unsupported` | Pass | Pass |
| Authored arrival | Paragraph depiction | `supported` | `supported` | Pass | Pass |
| Authored arrival | Physical position | `supported` | `supported` | Pass | Pass |
| Explicit stop short | Physical position | `unsupported` | `unsupported` | Pass | Pass |
| Explicit stop short | Paragraph depiction | `unsupported` | `unsupported` | Pass | Pass |

All six responses cited the same four reference IDs, each bound to its own plan and draft. For original position, Sol said “At the final narrated instant, he is approaching” and used that conclusion to reject standing there. For original depiction, it confined its conclusion to what the closing paragraph shows. That difference in reasoning explains the different evidence scores despite identical references and labels. The stop and arrival responses each located the decisive final addition. The frozen decision remains **`hold`**. There was one model observation per case. [Original explanations](../../data/diagnostics/q011-scope-regression-2026-11-23/capture/operator/worksheet.json) · [Replayed scores](../../data/diagnostics/q011-scope-regression-2026-11-23/replay.json)

## Verification

The sealed private archive contains **52 members**. It holds 49 byte-identical copies of the run and operator files, including all twelve requests and terminal records, the spent ledger, scoring rules, sealed evidence decisions and joined scores. Three reconstructed source packets allow replay independently of the original run directory. The original files retained their hashes and modification times during preservation. The archive manifest SHA-256 is `46bbeba44b2bf6fea881d5ad3014a8b680cd39ecd3e85a522f1508402ea411c0`. [Archive manifest](../../data/diagnostics/q011-scope-regression-2026-11-23/capture-manifest.json)

Run `python -m scripts.q011_scope.regression` with the repository interpreter. Replay rebuilt the six works and all twelve requests, validated the intent and terminal chains and six raw finals, and reproduced the evidence worksheet and original score file byte for byte. The archive tests block network access and reject exchanged responses, a substituted draft or request, and missing gold, decisions or scores. All **162 focused tests passed**. Ruff lint, formatting and strict mypy passed across 389 Python files. The private capture is needed for exact replay, and its nine tests skip on checkouts without it. [Offline verifier](../../scripts/q011_scope/regression.py) · [Regression tests](../../tests/evaluations/test_q011_scope_regression.py) · [Test results](../../data/diagnostics/q011-scope-regression-2026-11-23/verification.xml)

## Recommended next step

**Rehearse a read-only check of the evidence for a physical contradiction on five cases.** Use the three existing position cases. Add two diagnostic versions containing the same observation of a gap between Elias’s boots and the sill. Put it at the cut while he is moving in one version. Put it earlier, followed by renewed approach with no final placement, in the other. Keep attraction established. Review the complete texts and seal their gold before authoring responses. Hold either new case if its wording permits a different physical conclusion.

For each answer, record the final observation it relies on, the instant it describes, and whether that observation establishes standing, excludes it, or leaves it open. Check the cited span mechanically and score the stated inference separately. Include an answer that cites the correct gap at the wrong instant. Require the local check to catch the genuine overread, retain affirmative arrival and explicit stop short, and distinguish the two time placements. Replay the three depiction cases as compatibility controls. These checks test whether the assessor can justify a negative with an incompatible fact, a question the mere presence of an accurate quotation cannot answer.

If the rehearsal passes, a subsequent baseline-versus-evidence-check comparison on the five position cases would need **ten counts before up to ten generations, zero retries**, subject to a separate freeze and approval. This audit made zero live calls. Production prompts remain unchanged and the full workflow canary stays on hold.
