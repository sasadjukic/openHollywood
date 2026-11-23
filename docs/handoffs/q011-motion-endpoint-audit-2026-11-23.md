# When a review says the character reached the destination

**B is the default wording for factual assessment. One of six previously unassessed ordinary-review fields qualified for the harder endpoint test.** In the Elias review, Q011 claims that the depicted state fulfills both the assigned attraction to the entrance and the assigned position at the threshold. Attraction is established. The final position remains open. The whole-claim gold is **`uncertain`**. This is a new claim on a familiar draft. No assessor output was opened and no provider call was made. [Frozen Q011 gold](../../data/diagnostics/q010-motion-endpoint-audit-2026-11-23/gold.json)

## What P01 and R06 actually tested

| | P01 · Elias and the threshold | R06 · Lale and the pouch |
| --- | --- | --- |
| Asserted fact | Elias “is entering the threshold.” Has crossing **begun**? | The pouch “is in the receiving pan.” Is it **in the pan** at the bell? |
| Observation time | The final narrated movement. | A bell after the pouch has gone behind the hood. |
| What the reader sees | Elias passes the shoes and moves toward the open threshold. The narration ends there, with no stated obstruction and no further placement of his feet. | The pouch travels toward the pan and disappears behind a copper hood. At the bell, Lale sees her reflection in the inspection hole. |
| What remains open | His direction and attraction are clear. The sentence leaves the start of a crossing unsettled. | The belt carries the pouch toward the pan. The text leaves its location at the bell open. |
| Earlier observed scores | B failed claim and evidence. C passed both. | B and C each passed claim and evidence. |

Both gold labels are `uncertain`. The cases differ in both the asserted fact and the reader’s view of the endpoint. The earlier scores cannot tell us which difference mattered. One hypothesis is that B handles an explicitly blocked view more reliably than a scene that simply ends during motion. [P01 result](q010-paired-uncertainty-results-2026-11-23.md) · [R06 result](q010-fresh-endpoint-repeat-results-2026-11-23.md)

## The admitted ordinary claim

Gemma wrote the following in `/saved_native_audit/check/current_endpoint_comparison`. The quotation is the entire Q011 field.

> The achieved state matches the outcome ('drawn to the entrance') and exit state ('stands at the threshold') defined in the scene plan.

The original critic instruction asks for the **draft’s achieved state** to be compared with the current endpoint. That fixes the question as fulfillment in the prose. Agreement between two fields of the critic’s own report cannot supply the physical observation.

| Evidence obligation | Source and finding |
| --- | --- |
| What the current plan assigns | Scene Plan v1, `E0233`, says Elias is drawn to the entrance. Its separate exit state, `E0229`, says he stands at the threshold. Q011 accurately attributes both targets. |
| What the draft establishes | Draft v1 shows longing displacing dread in `E0315`. In the final sentence, `E0321`, Elias steps past the shoes and moves “toward the dark, open threshold of the monolith, drawn by the silent promise of the thing that waited inside.” This fulfills attraction to the entrance. |
| What the cut leaves open | The final movement supplies direction. There is no subsequent placement at the threshold and no observation incompatible with arrival. **Standing there remains undetermined.** The critic’s conjunction asserts fulfillment of both targets. |

The audit bound critique v2 `2268e6e8-b82b-4cca-932f-55cc418a58b5`, draft v1 `b74efc96-dbe6-4147-8dd3-a1c24f295321` and plan v1 `b5179ac9-5585-5e5b-9555-20ca70b68f6a`. The final sentence occupies code points **3129–3284** of the 3,284-character draft, with the end excluded. A precise locator in the full draft `E0883` is also adequate. The prospective evidence score requires covering both plan fields and explaining both the depicted attraction and the limit on final position. The whole-claim label is scored separately.

Q011 gives us an **achieved-destination claim at a narrative cut with no stated occlusion**. It shares the exact passage with Q010/P01, which asks whether crossing has begun. That makes the pair useful for comparing what each field requires. It adds no independent scene family, and Q011 also introduces the obligation to compare two plan fields.

## Six-field intake

The selection was fixed from field pointers before reading the six candidate texts. It used the two registered provider-generated ordinary v61 captures in capture order, then numeric field order within each review. Eligible pointers covered turning-point and outcome assessments and the three scene-boundary explanations. The three already-assessed units and Elara’s previously adjudicated Q016 hold were excluded by critique version and field ID. All six remaining matches were read, without replacements. Other archives and editorial score rationales were outside this bounded intake. [Protocol](../../data/diagnostics/q010-motion-endpoint-audit-2026-11-23/protocol.json) · [Fixed selection](../../data/diagnostics/q010-motion-endpoint-audit-2026-11-23/selection.json)

| Archive / field | Instant and assertion | Disposition |
| --- | --- | --- |
| Elias Q008 / Q009 | At the stroller, before the cut, Elias notices the circle of shoes. The contact passage says “something soft”; identification of the red shoe follows. | Outside the endpoint test. This is recognition during the turning point. |
| Elias Q008 / Q011 | At the cut, the review claims fulfillment of attraction **and** standing at the threshold. No obstruction is stated. | **Admit**, with whole-claim gold `uncertain`. |
| Elias Q008 / Q012 | “The draft stops at the threshold; it does not advance into the building or introduce the disembodied voice of Julian Vane reserved for scene 2.” | **Hold the whole field.** The complete draft supports the narrative boundary and depicts no Julian Vane voice; the Blueprint reserves it. Reading “the draft stops” as Elias physically standing there changes the referent and leaves the position uncertain. |
| Elara Q013 / Q012 | At the cut, Elara stares at the ink, haunted by the possibility of a future self. The plan assigns the haunted outcome. | Outside the endpoint test. This is a depicted mental outcome. |
| Elara Q013 / Q015 | At the cut the field interprets Elara’s state as “visceral dread and haunting curiosity.” Dread and competing explanations have witnesses. | **Hold the interpretation.** The feel of her curiosity belongs with editorial review. |
| Elara Q013 / Q017 | Across the current scene, the field says the draft has yet to depict the exact shaking pattern or confirm authenticity. | Outside the endpoint test. Steady writing, later trembling fingers and the unresolved final possibility bear on a next-scene reservation. |

The Elara records bind critique v3 `ca5915a5-5b82-4bad-82ce-e5c31a519dc0`, draft v1 `c3689bce-e108-4761-bafe-390f6e7ea1b3` and plan v1 `2a13f5a3-8a0b-561f-b889-05eb1af338a7`. The private audit preserves all six verbatim fields, per-field digests, exact source versions, draft spans and relevant plan or Blueprint witnesses. Only Q011 received new whole-claim gold. [Full audit record](../../data/diagnostics/q010-motion-endpoint-audit-2026-11-23/audit.json)

## Verification

The gold and audit were sealed at **09:02:53 UTC on November 23, 2026**. Source-only replay reproduced both byte-for-byte. Both critic reports matched their original HTTP captures and schema-7 exports under prompt v61 and graph 9. Read-only SQLite queries verified the creating invocations and immutable input versions. All 40 Elias and 43 Elara excerpts relocated in their respective complete drafts, and the original capture files retained their hashes and modification times. The application’s existing compact system message matched B in both historical studies at both endpoints. C remains a diagnostic variant.

- Q011 gold SHA-256 `d8717921ea635eb6d9d5ff548ff448d5ce37e4025ac487efb4350284c15aab8e`
- Audit seal SHA-256 `6692a930fddf2844c51e79a01427a3223bea93ae45cff58716d1a0fbac53bc1f`

From the repository root on Windows, replay with `.\.venv\Scripts\python.exe data/diagnostics/q010-motion-endpoint-audit-2026-11-23/audit.py verify`. All **112 focused regressions passed** across claim binding, work briefs and independent scoring. The work-brief tests emitted nine existing Pydantic serialization warnings. [Seal](../../data/diagnostics/q010-motion-endpoint-audit-2026-11-23/seal.json) · [Regression results](../../data/diagnostics/q010-motion-endpoint-audit-2026-11-23/regressions.xml)

## Recommended next steps

1. **Rehearse Q011 locally with B.** Bind it to the exact critique, draft and plan. Verify that the assessor sees the whole claim, both plan targets and the complete draft, with scorer gold excluded. Use fixtures for grounded uncertainty, a claim of arrival justified only by the plan, and a claim that Elias definitely stopped short. Require the evidence score to distinguish all three. Keep Q012 and Q016 outside the assessor request.
2. **If the rehearsal passes, propose one B-only comparison with two cells.** Keep the Q011 claim, plan, question and unoccluded scene cut fixed. Use the genuine ending in one cell and a separately versioned authored control in which the final observation explicitly places Elias standing at the threshold in the other. The control would receive its own provenance, references and prospective gold. This isolates whether the assessor changes its judgment when the draft supplies the missing destination fact. It tests a different question from another B/C wording repeat.
3. **Budget only after local qualification.** The proposed ceiling is two counts before at most two generations, zero retries, with claim and evidence scored independently. One observation per cell can diagnose a failure of plan-versus-draft grounding. Broader reviewer accuracy and story quality require separate evidence. Live calls remain paused and the full workflow canary stays on hold.
