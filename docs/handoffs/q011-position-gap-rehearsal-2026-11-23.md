# Q011 position rehearsal with the same gap at two instants

**Ready to freeze a five-case Sol-high comparison.** The rehearsal distinguished an observation of distance at the cut from the same observation followed by renewed motion. All five grounded authored responses passed both scores. Applying the same evidence rule to Sol’s saved answer for the genuine ending reproduced its failure. The historical decision is still `hold`. [Joined scores](../../data/diagnostics/q011-position-rehearsal-2026-11-23/scores.json)

## Five physical-position cases

The active claim was “Elias is drawn to the entrance. At the scene cut he stands at the threshold.” The plan assigns both parts. Every draft depicts the attraction. The disputed part is Elias’s physical position and posture at the final narrated instant.

Both new versions keep the full genuine draft and append these two sentences in opposite orders. The plan, historical critique, claim, assessment brief and all other story material stay the same.

| Version | First added sentence | Last added sentence |
| --- | --- | --- |
| Gap at cut | He moved on toward the entrance, his eyes on the darkness inside. | A full stride of bare earth lay between his boots and the sill. |
| Gap before renewed motion | A full stride of bare earth lay between his boots and the sill. | He moved on toward the entrance, his eyes on the darkness inside. |

I inspected the complete texts and sealed the gold before authoring the responses. The original approach, arrival and stop were previously scored anchors. Gold for the two new endings was prospective. Both new drafts are 3,414 Unicode code points long. The gap occupies offsets [3351, 3414) in version `5d799e7c-f363-5baf-9c5f-92b6d64e80ed` and [3285, 3348) in version `b4ccc77e-ff44-51ab-b36c-c391ae6bf822`. Both are diagnostic versions derived from the genuine draft. [Sealed gold, versions and passages](../../data/diagnostics/q011-position-rehearsal-2026-11-23/gold.json)

| Ending | Position gold | Judgment, grounded authored answer | Evidence | Decisive observation |
| --- | --- | --- | --- | --- |
| Genuine approach | `uncertain` | Pass | Pass | Elias moves past the shoes toward the threshold. The passage leaves his final position open. |
| Authored arrival | `supported` | Pass | Pass | The last sentence places Elias standing at the threshold. |
| Explicit stop short | `unsupported` | Pass | Pass | His feet are planted a full stride short of the sill at the cut. |
| Gap at cut | `unsupported` | Pass | Pass | The last observation places his boots a stride from the sill. The distance rules out standing there, even without a stop. |
| Gap before renewed motion | `uncertain` | Pass | Pass | Elias moves again after the gap. The draft gives neither distance covered nor final stance. |

## Does a correct quotation support the inference?

The local check resolves the plan and draft references, then validates the selected prose span against the cited immutable draft. The evidence worksheet records the passage, the instant the answer assigns to it and what the answer says it establishes. I scored the reasoning with the returned label withheld and sealed the evidence decisions before comparing labels with gold. The worksheet tests interpretation directly. Matching source bytes alone earns no semantic credit. [Evidence worksheet](../../data/diagnostics/q011-position-rehearsal-2026-11-23/evidence-sheet.json) · [Sealed decisions](../../data/diagnostics/q011-position-rehearsal-2026-11-23/evidence-decisions.json)

| Challenge | Returned label | Judgment | Evidence | What the check caught |
| --- | --- | --- | --- | --- |
| Earlier gap cited as the final measurement | `unsupported` | Fail | Fail | The quote and version match exactly. Renewed motion comes after it. |
| Terminal-gap draft, with the negative justified solely by motion | `unsupported` | Pass | Fail | The label matches gold, but direction alone cannot exclude standing there. |
| Grounded explanation for the earlier-gap draft with only its label flipped | `unsupported` | Fail | Pass | The same explanation and citations received the same evidence decision as the grounded answer. |
| Sol’s **saved** genuine-position answer | `unsupported` | Fail | Fail | Sol located the approach accurately and treated it as physically incompatible with standing at the cut. The source gives no such observation. |

The first three challenges are authored. For the last row, replay used Sol’s saved answer and its original references. The exact span, instant and asserted relation are local annotations of its explanation. Sol did not return those fields. This was an offline replay of one historical observation. [Authored responses](../../data/diagnostics/q011-position-rehearsal-2026-11-23/authored-fixtures.json) · [Historical source and score audit](q011-evidence-at-the-cut-audit-2026-11-23.md)

## Three saved depiction controls

These controls ask whether the complete closing paragraph **depicts** Elias standing at the threshold. A complete paragraph can settle that question even when the character’s exact physical position is open. Replay verified the saved deliveries, version bindings and original scores. [Historical capture manifest](../../data/diagnostics/q011-scope-regression-2026-11-23/capture-manifest.json)

| Saved Sol answer | Returned label | Judgment | Evidence |
| --- | --- | --- | --- |
| Genuine approach, AD-B | `unsupported` | Pass | Pass |
| Authored arrival, RD-B | `supported` | Pass | Pass |
| Explicit stop short, SD-B | `unsupported` | Pass | Pass |

## Verification and next step

Run `python -m scripts.q011_scope.position_rehearsal` with the repository interpreter and the local private captures. The verifier rebuilds all five works, authenticates the previous six deliveries, verifies the rehearsal seals and reproduces the saved scores. Tests cover a wrong draft version, a damaged quote or offset, a reference to the wrong field, the independence of the two scores, and replay with networking blocked. [Verifier](../../scripts/q011_scope/position_rehearsal.py) · [Tests](../../tests/evaluations/test_q011_position_rehearsal.py)

All **63 focused tests passed**, including the earlier Q011 regression and injected-transport checks. Ruff lint, formatting and strict mypy passed across 391 Python files. The sealed gold file has SHA-256 `a184380e82e1f8d7035e5af57c895d58efb5e692c2b1e1f00ecfa25712189005`. [Test results](../../data/diagnostics/q011-position-rehearsal-2026-11-23/test-results.xml)

Prepare a paired comparison of baseline B and a diagnostic brief that asks for the observation, its instant and what it establishes about standing at the sill. Keep the claim, complete source and model settings fixed within each pair. Score both arms by the same rules, with the returned label withheld during evidence review. Report the genuine approach and the two timing cases individually. Require the new arm to pass the genuine case on both scores, distinguish the two gap placements and retain arrival and stop before considering further testing. If B also passes the genuine case, record a baseline recovery. Only a difference within the new pair can show a gain on that case. Keep the three depiction controls as offline compatibility checks.

The proposed ceiling is **ten input counts before up to ten generations, zero retries**, with a separate freeze and approval before inference. These fixtures qualify the scoring procedure in one scene family. Whether the extra question improves Sol’s assessment remains open. No live calls were made. Production prompts are unchanged and the full workflow canary is on hold.
