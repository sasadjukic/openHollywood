# Q011 rehearsal of physical position and paragraph depiction

**The original approach separates the two claims.** The paragraph shows Elias passing the shoes and moving toward the threshold. His position when the scene cuts remains uncertain. We can, however, read the whole closing paragraph and establish that it supplies no observation of him standing there. Both claims become supported when the draft adds an arrival. Both become unsupported when it adds a final stop a stride short. All six grounded, locally authored responses passed judgment and evidence independently. [Case gold and complete closing paragraphs](../../data/diagnostics/q011-scope-rehearsal-2026-11-23/gold.json) · [Scored responses](../../data/diagnostics/q011-scope-rehearsal-2026-11-23/scores.json)

## What was assessed

Both authored claims begin “Elias is drawn to the entrance.” The physical claim continues “At the scene cut he stands at the threshold.” The depiction claim continues “The complete closing paragraph depicts him standing at the threshold at the scene cut.” The first asks about a fact in the story. The second makes a positive assertion about the contents of a complete passage. An equivalent description of Elias’s position would satisfy the depiction claim.

The original Gemma Q011 field remains intact in critique v2, bound to the genuine draft. Each authored claim occupies a separate diagnostic work item. The baseline B instructions, neutral brief, response schema, full story context and available citations were identical within each pair. Scene Plan v1 assigns attraction (`E0233`) and standing (`E0229`). The assessed draft supplies the observations. Its `D01` citation resolves to the full closing paragraph and `E0883` to the complete prose of that version. [Parent Q011 audit](q011-approach-arrival-audit-2026-11-23.md) · [Local replay](../../scripts/q011_arrival/scope_rehearsal.py)

| Ending | Subject | Gold and authored judgment | Judgment score | Evidence score | Decisive evidence |
| --- | --- | --- | --- | --- | --- |
| Original approach | Physical position | `uncertain` | Pass | Pass | Passing the shoes and moving toward the threshold establish motion and attraction. The cut leaves final placement open. |
| Original approach | Paragraph depiction | `unsupported` | Pass | Pass | He continues without looking back, passes the shoes and moves toward the threshold. Those actions exhaust the paragraph. None places him standing there. |
| Authored arrival | Physical position | `supported` | Pass | Pass | The new last sentence places Elias standing at the threshold at the cut. |
| Authored arrival | Paragraph depiction | `supported` | Pass | Pass | “Elias stood at the threshold” occurs inside the closing paragraph. The fixture’s paraphrase earned full evidence credit. |
| Explicit stop short | Physical position | `unsupported` | Pass | Pass | The final observation places both feet in the dirt a full stride short of the sill. |
| Explicit stop short | Paragraph depiction | `unsupported` | Pass | Pass | The paragraph follows approach with a final placement short of the sill. It never depicts him standing at the threshold. |

The genuine and arrival drafts retain versions `b74efc96-dbe6-4147-8dd3-a1c24f295321` and `4111438c-aff2-5041-8703-e1cbf6ce303b`. The stop prose was authenticated against P07 source S02, version `43c97975-3aae-505b-8861-8febf7fa0039`. Both authored texts preserve the entire genuine prose and append one sentence. I gave the stop its own full Q011 draft binding, `974ba7f4-7d1f-5834-a5c3-889ff1b8626f`, and scored it against new Q011 gold. P07 originally assessed whether crossing had begun. [P07 source packet](../../data/diagnostics/q010-endpoint-controls-2026-11-23/frozen/packets/P07.json)

## Independent scoring checks

The six judgments, source versions, paragraph spans and evidence requirements were sealed before authoring the responses. I inspected each distinct explanation and its resolved citations in a worksheet that withheld the returned label. I sealed those decisions before joining labels to gold. The ten authored responses produced nine distinct evidence entries because the label-only control reused the grounded explanation and citations byte for byte. [Authored responses](../../data/diagnostics/q011-scope-rehearsal-2026-11-23/authored-fixtures.json) · [Evidence worksheet](../../data/diagnostics/q011-scope-rehearsal-2026-11-23/evidence-sheet.json) · [Sealed decisions](../../data/diagnostics/q011-scope-rehearsal-2026-11-23/evidence-decisions.json)

| Challenge fixture | Returned | Judgment | Evidence | What the score detects |
| --- | --- | --- | --- | --- |
| Infer non-arrival from the original cut | `unsupported` | Fail | Fail | The reason turns the end of the narration into a physical contradiction. |
| Change only the grounded original-position label | `unsupported` | Fail | Pass | The explanation still identifies what the passage leaves open. |
| Look only for the word “stood” in the original paragraph | `unsupported` | Pass | Fail | Word absence cannot exclude a synonymous depiction. |
| Cite “Elias stopped.” earlier in the stop draft | `unsupported` | Pass | Fail | Elias steps forward again. The ending contains a decisive later stop, and the fixture fails to locate it. |

Offline replay reproduced the six distinct work bindings and all ten scores. Tests verified that only the two source packets, their manifest, P07 and its seal were needed to construct the work. They also verified that a receipt for the original physical claim is rejected for the depiction claim and for the stop draft. All 153 focused tests passed with network connections blocked. The claim-scope and brief tests emitted 22 Pydantic serialization warnings. The replay requires the private diagnostic files. Run `python -m scripts.q011_arrival.scope_rehearsal` from the repository root. [Regression checks](../../tests/evaluations/test_q011_scope_rehearsal.py) · [Verification results](../../data/diagnostics/q011-scope-rehearsal-2026-11-23/verification.xml)

## Readiness

**Ready to prepare a freeze for a six-case Sol-high B diagnostic.** Preserve these source versions, claims and independent scores. Counterbalance which subject is presented first across endings, with one claim per request. Propose six input counts before up to six generations, zero retries, and submit the exact requests, scoring and stops for approval. Require both scores to pass on the original split and on each of the four clear control cases. Report the original pair separately so a control pass cannot conceal a repeated overread.

This rehearsal establishes that the questions have distinct, defensible answers and that the scorer can detect a correct label backed by weak evidence. The responses were authored locally. Sol’s ability to make the distinction and its transfer to other stories remain open. The finding creates no need to revise the genuine ending. Production prompts remain unchanged, live calls paused and the full workflow canary on hold.
