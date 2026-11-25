# The Wading Path evidence-coverage rehearsal

The local check flagged the four stop-only explanations from the paired Sol comparison and accepted all eight retrospective explanations. The separate S2 endpoint control also passed. The same three-stride gap can establish where Elias and Maya stand at the cut while leaving open whether they visited the housing earlier. [Paired results](wading-path-sol-versions-narration-event-results-2026-11-25.md) · [S2 capture](../../tests/fixtures/wading_path_measured_stop_observed.json)

## Frozen expectations and results

Before annotating the responses or implementing the check, we froze an outcome, exact generation receipt hash and draft version for each of the twelve responses and S2. We also froze the wording, source and expected outcome of five authored controls. The expectation file has SHA-256 `315a415cbd71136ba38814b85140959fb495666db0f04ef568d5d0bd69a25d30`. These are acceptance tests on previously scored material. [Frozen expectations](../../tests/fixtures/wading_path_evidence_coverage_expected.json)

Each historical score below is **judgment / evidence**, with one point available on each axis. The coverage check flags explanations for review. The original labels and scores are reported separately.

| History and claim | Sol 6.1 coverage (scores) | Sol 6.2 coverage (scores) | Evidence used in the explanation |
| --- | --- | --- | --- |
| SN · Measured stop, narrated arrival | Flag (1/0) | Flag (1/0) | Both correctly rejected explicit narration of arrival. Both went further and denied reaching the housing during the scene. |
| SE · Measured stop, visit at any time | Flag (0/0) | Flag (0/0) | 6.1 expressly ruled out an earlier visit and retreat. 6.2 described reaching the wall and stopping short. Its account left the earlier interval unanswered. |
| XN · Whole-scene exclusion, narrated arrival | Pass (1/1) | Pass (1/1) | Both addressed what the draft recounts and the retrospective minimum distance. |
| XE · Whole-scene exclusion, visit at any time | Pass (1/1) | Pass (1/1) | Both used the retrospective that covers both people from the opening huddle through the cut. |
| VN · Earlier joint visit, narrated arrival | Pass (1/1) | Pass (1/1) | Both identified the narrator's retrospective account of reaching the housing together. |
| VE · Earlier joint visit, visit at any time | Pass (1/1) | Pass (1/1) | Both located the visit before the pair walked back. Their later stop is compatible with that history. |

**S2, scored separately, passed (1/1).** Its claim concerns the final narrated instant. The reason locates both people three strides short of the named housing and observes that they stay there. The final-gap passage at `E1420 [4806,4945)` covers that instant. [Saved paired explanations](../../tests/fixtures/wading_path_sol_versions_observed.json) · [Per-response replay](../../data/diagnostics/wading-path-evidence-coverage-rehearsal-2026-11-25/replay.json)

## How coverage was checked

An operator read the explanations against the selected drafts and marked the clauses that express a conclusion and the clauses that invoke evidence. The replay verifies those exact words in the saved delivery, the generation receipt, the `E1420` citation and the full draft's version and prose hash. It resolves the invoked passages on that version. In the exclusion draft the decisive retrospective occupies `[4947,5149)`. In the visit draft the retrospective occupies `[4947,5132)`. The stop-only draft ends at 4945. [Anchored readings](../../tests/fixtures/wading_path_evidence_coverage_readings.json) · [Draft versions and source text](../../tests/fixtures/wading_path_narration_event_gold.json)

The rule receives the claim scope, the explanation's assertions, the evidence it invokes and the witnesses available on that version. It checks whether the explanation answers the claim and whether its evidence covers each conclusion, including additional claims the explanation makes. A complete-draft citation alone earns no credit for an unused retrospective. The rule has no model ID, case ID, returned label, historical grade or expected outcome as an input. Mapping free prose to those assertions and witnesses was a manual step. Performance on new, unannotated reviews remains untested. [Offline check](../../scripts/wading_path_sol_versions/evidence_coverage.py)

## Authored controls

| Control | Outcome | What it established |
| --- | --- | --- |
| Paraphrase of the whole-scene distance bound | Pass | Describing both people as outside touching distance from the opening huddle to the final moment preserves the relevant interval. |
| Final gap alone, event claim on the exclusion draft | Flag | The decisive retrospective existed on the cited version. This explanation never used it. |
| Identical final-gap explanation, endpoint claim | Pass | The change in claim scope changes what evidence suffices. |
| Complete account of approach, explicit limit to narration | Pass | The explanation identified what the narrator omitted and made no wider physical claim. |
| Final position established, earlier visit expressly left open | Pass | The explanation covered both the endpoint fact and the unresolved interval. |

All 41 focused offline tests passed. They included the source-bound replay under a network block, the same gap under two scopes on the same source, an extra unsupported physical conclusion, a borrowed witness, and a changed explanation anchor. Repository-wide Ruff lint and format checks and strict mypy passed across 467 Python files. B remains the default, live calls are paused and the canary is on hold. [Regression tests](../../tests/evaluations/test_wading_path_evidence_coverage.py) · [Verification record](../../data/diagnostics/wading-path-evidence-coverage-rehearsal-2026-11-25/verified.xml)

The full Python suite collected 3,033 tests. The sandbox stalled during Windows event-loop setup in the first API test. A rerun with loopback access progressed through the API tests and was stopped before completion. The 41-test verification record covers the requested rehearsal and its historical regressions.

The next useful check would be a small offline transfer rehearsal on a different saved scene family. Freeze the claim scope and evidence spans first, mask the historical scores while annotating the explanations, and record any case where two plausible readings give different coverage decisions. That would test the manual interpretation step before considering a production review flag or asking a writer to revise.
