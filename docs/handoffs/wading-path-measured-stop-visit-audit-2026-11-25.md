# The Wading Path · What the measured stop establishes

**S1 found the right passage and applied it to too much time.** The final paragraph places Elias and Maya three strides short of the housing and says they stayed there. That settles their position at the cut. It leaves open whether they were at the housing earlier in scene four. The frozen visit judgment is `uncertain`. Sol returned `unsupported` and its explanation made the same overreach, so judgment and evidence each scored zero. [Frozen criteria and live results](wading-path-visit-position-sol-high-results-2026-11-25.md)

## Six observed regressions

| Case | Draft | Factual question | Gold | Sol | Judgment / 1 | Evidence / 1 |
| --- | --- | --- | --- | --- | ---: | ---: |
| S1-B | Measured stop | Visited during scene? | uncertain | unsupported | 0 | 0 |
| X1-B | Full-scene exclusion | Visited during scene? | unsupported | unsupported | 1 | 1 |
| S2-B | Measured stop | At housing at cut? | unsupported | unsupported | 1 | 1 |
| X2-B | Full-scene exclusion | At housing at cut? | unsupported | unsupported | 1 | 1 |
| A1-B | Explicit arrival | Visited during scene? | supported | supported | 1 | 1 |
| A2-B | Explicit arrival | At housing at cut? | supported | supported | 1 | 1 |

The repository fixture preserves the six returned labels, verbatim explanations, selected draft versions, citations, independent scores, evidence adjudications and terminal hashes. The local archive preserves the requests, gold, original count and generation receipts, and sealed scoring records. Its 57 members are bound to SHA-256 `6339d86c0c033d470161f9b931f3bc09ac6bb3b06d522feb2ddc80e4ce132344`. Offline replay reconstructed all 12 slots and reproduced the original decision, `hold_claim_scope`. [Portable regressions](../../tests/fixtures/wading_path_measured_stop_observed.json) · [Private archive manifest](../../data/diagnostics/wading-path-visit-position-regression-2026-11-25/capture-manifest.json) · [Score replay](../../data/diagnostics/wading-path-visit-position-regression-2026-11-25/replay.json)

## Where S1's explanation overreaches

The active claim was “Elias and Maya reached the master breaker panel housing at some time during scene four.” The B brief assigned authority to the complete selected draft, `E1420`, and directed Sol to use the interval or instant in the claim. The supplied definition of `unsupported` required evidence contradicting a material part of the claim. S1 and X1 had identical claim scopes and briefs. S2 used the same measured-stop draft as S1 and asked about the final instant. All six generations completed, matched their pre-counts and cited the correct version of `E1420`. [Request and passage audit](../../data/diagnostics/wading-path-visit-position-regression-2026-11-25/s1-scope-audit.json) · [Slot inspection](../../data/diagnostics/wading-path-visit-position-regression-2026-11-25/capture/operator/slot-inspection.json)

| Evidence in the selected draft | What it establishes |
| --- | --- |
| Measured stop, characters 3995–4804 | They reach the eastern wall, enter the plenum and look farther down the passage. The description places the housing at the end of the passage. Sol correctly distinguishes the wall from the housing. |
| Measured stop, 4806–4945 | Both stop three full strides short and stay there. “Stayed there” extends forward from the stop through the cut. It supplies no minimum distance for the preceding interval. |
| Full-scene exclusion, 4947–5149 | After the identical measured-stop paragraph, the narrator states that neither had ever been closer than three strides from the opening huddle through the last moment in the plenum. This covers every opportunity for a visit in the scene. |
| Explicit arrival, 4806–4920 | Both reach the named housing and stand before it. That one observed instant establishes a visit and is also the final instant of this version. |

S1’s explanation moves from “The full sequence shows no earlier arrival followed by retreat” to “Reaching the wall and seeing the housing do not establish reaching the housing at any time during the scene.” The latter observation is accurate. The decisive error is treating the absence of a narrated visit as evidence that no visit occurred. A correct citation earns no evidence point when the passage cannot support the conclusion drawn from it. X1 makes the distinction visible. It returned the same label and explicitly cited the added scene-wide minimum distance. S2 needed only the final gap for its narrower claim. [Verbatim explanations and sealed evidence decisions](../../tests/fixtures/wading_path_measured_stop_observed.json)

**What plausibly prompted that reading.** The scene presents a continuous-seeming approach from the huddle, across the room and into the plenum. Read as a story, a first approach is natural. S1’s own words “the full sequence” suggest it treated that sequence as an exhaustive account of the pair’s movements. The response establishes that Sol made this inference. A single delivery cannot establish which wording caused it or how often it recurs.

A previously scored control shows why the distinction matters. In the separate retreat draft, both people reach the housing at 4806–4920, then step back three strides and stay there at 4922–5008. Sol correctly judged the visit supported on R2. A three-stride gap at the cut is compatible with a prior visit. The retreat draft illustrates that possibility without supplying any evidence that a visit happened in S1. The saved plan's intended arrival likewise cannot settle events in the selected draft. [Prior control and four-version audit](wading-path-visit-position-audit-2026-11-24.md)

## Local verification

The replay rebuilt the six requests from archived source versions, checked the count and generation receipts against their intents, and reproduced both scores from the sealed records. With network access disabled in the regression tests, all six portable rows matched their original terminals and adjudications. Missing or swapped terminals, a substituted request, missing historical source locations, missing gold and missing evidence decisions each caused replay to reject the damaged copy. All 45 frozen run files matched the archive, and all 46 implementation files listed in the approval matched their original hashes.

All 50 targeted tests passed, including six injected-transport schedule and stop tests. Ruff lint, the format check and strict mypy passed across 455 Python files. This audit made zero provider calls. [Regression tests](../../tests/evaluations/test_wading_path_measured_stop_scope.py) · [44 offline checks](../../data/diagnostics/wading-path-visit-position-regression-2026-11-25/verified.xml) · [Six injected-transport checks](../../data/diagnostics/wading-path-visit-position-regression-2026-11-25/mock-schedule.xml)

## Next step

**Rehearse six answers locally before considering another model call.** Keep the approach and measured-stop paragraph verbatim across three histories. Use S1 as written, X1 with its explicit whole-scene exclusion, and one new diagnostic variant with a retrospective sentence explicitly recounting an earlier joint visit to the housing during this scene. Give the positive and negative retrospectives the same placement and preserve both characters’ final position. Ask two questions separately on each version. Freeze the versions, gold and evidence criteria before inspecting any authored answers.

| History | Does the draft explicitly recount a joint visit? | Did both visit at some time during the scene? |
| --- | --- | --- |
| Measured stop alone | unsupported | uncertain |
| Same stop with whole-scene exclusion | unsupported | unsupported |
| Same stop with explicit earlier visit | supported | supported |

Score judgment and evidence separately. On S1, require the explanation to distinguish an omitted depiction from an unresolved event. On X1, require the interval-wide exclusion for the event judgment. On the positive version, require the in-scene joint visit. Include an answer citing only the final gap as an evidence-failure control and replay S2 as the endpoint check. Proceed to a live proposal only if the local scorer distinguishes those answers with the returned label hidden during evidence grading. This tests the assessment contract while preserving room for a writer to leave motion implicit. B remains the default. Live calls are paused and the full workflow canary is on hold.
