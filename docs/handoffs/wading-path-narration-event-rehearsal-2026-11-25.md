# The Wading Path · A narrated visit and a visit during the scene

**The measured stop alone gives different answers to the two questions.** The complete draft contains no explicit account of Elias and Maya reaching the housing. Whether they reached it earlier in the scene remains open. The six grounded, locally authored answers each earned one judgment point and one evidence point. The archived Sol response to the open event claim still scores zero on both. [Scores and historical replay](../../data/diagnostics/wading-path-narration-event-rehearsal-2026-11-25/scores.json)

## What was frozen first

The gold file fixed both claims, three exact draft versions and six claim-specific evidence criteria before the rehearsal answers were authored. Its canonical SHA-256 is `860841fa62b1a951b7778c128d788e106f01f1fde6ca8a117f24b42111724185`. The narration claim asks whether the complete scene explicitly recounts a joint arrival. The event claim keeps the exact S1 wording, “Elias and Maya reached the master breaker panel housing at some time during scene four.” [Frozen gold](../../tests/fixtures/wading_path_narration_event_gold.json) · [Gold-first copy](../../data/diagnostics/wading-path-narration-event-rehearsal-2026-11-25/gold-first.json)

All three histories have the same first 4,945 characters, including the entire stop paragraph at offsets 4806–4945. Both retrospectives begin at offset 4947, after the stop on the page. Neither adds motion after the cut.

| History | Selected version | What the retrospective adds |
| --- | --- | --- |
| Stop alone | `2f9e80a0-29b4-579f-8075-b6e064788b24` | The draft ends with both people three strides short, where they stay. |
| Earlier visit excluded | `4da86d35-9337-54d8-896b-c212ba05516c` | Neither person had ever been closer than three strides between the opening huddle and the cut. |
| Earlier visit confirmed | `58a48fd1-3acd-5e69-9f1b-a89c67170c20` | After entering the plenum and before the light steadied, both had reached the housing together and walked back up the passage. |

## Judgment and evidence

Each case had a grounded answer and a control answering `unsupported` with the same true observation about the final gap. Evidence was graded against the exact selected draft with the returned label hidden. The grader recorded a reason for each evidence point before joining the judgments. Scores below are out of one. [Authored answers](../../tests/fixtures/wading_path_narration_event_answers.json) · [Masked evidence sheet](../../data/diagnostics/wading-path-narration-event-rehearsal-2026-11-25/masked-evidence.json) · [Sealed evidence decisions](../../tests/fixtures/wading_path_narration_event_evidence.json)

| History | Claim | Gold and grounded answer | Judgment | Evidence | Gap-only judgment | Gap-only evidence |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| Stop alone | Narration | unsupported | 1 | 1 | 1 | 0 |
| Stop alone | Event | uncertain | 1 | 1 | 0 | 0 |
| Earlier visit excluded | Narration | unsupported | 1 | 1 | 1 | 0 |
| Earlier visit excluded | Event | unsupported | 1 | 1 | 1 | 0 |
| Earlier visit confirmed | Narration | supported | 1 | 1 | 0 | 0 |
| Earlier visit confirmed | Event | supported | 1 | 1 | 0 | 0 |

The gap-only answer got three labels right and earned zero evidence points across all six cases. On the excluded history, the minimum distance **throughout the scene** supplies the missing evidence for the event judgment. On the confirmed history, the retrospective itself recounts the visit and places it within the scene. On the unamended draft, changing only the grounded event label to `unsupported` dropped judgment from one to zero while the identical explanation retained its evidence point.

The observed S2 endpoint assessment replayed at 1/1 under its original rubric. Its question asks where both people are at the cut, so the final gap suffices. S1 replayed at 0/0 on the scene-wide visit. Both are historical model deliveries, recorded separately from the authored cases. [Original S1/S2 audit](wading-path-measured-stop-visit-audit-2026-11-25.md)

## Verification

All 40 focused tests passed, including rejection of a swapped draft, a wrong version, an altered citation, a missing claim, changed gold and a changed evidence decision. The harness resolved every citation to its exact character range, reproduced the masked evidence sheet and replayed the endpoint control offline. Repository-wide Ruff lint, formatting and strict mypy passed across 457 Python files. [Rehearsal harness](../../scripts/wading_path_visit_position/narration_event.py) · [Regression tests](../../tests/evaluations/test_wading_path_narration_event.py) · [Verification results](../../data/diagnostics/wading-path-narration-event-rehearsal-2026-11-25/verified.xml)

## Readiness

**Ready to prepare a six-case Sol-high B diagnostic for approval.** Use one request per claim and history, with six input counts before up to six generations and zero retries. Keep S2 as an offline endpoint control. Require both scores for each eligible response. The decisive result is whether Sol can reject explicit narration on the stop-only draft, leave the event uncertain there, and cite the corresponding retrospective when the history settles the event. Keep the frozen event wording for comparison with S1. All three histories concern the pair together; separate visits by the two characters are outside this rehearsal.

The local results qualify the cases and scoring procedure. Sol's performance on the six-case panel still requires a separately approved run. The retrospectives are diagnostic source variants. B remains the default, production prompts are unchanged, live calls are paused and the full workflow canary stays on hold.
