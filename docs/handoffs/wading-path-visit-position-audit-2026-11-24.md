# The Wading Path · Evidence for a visit and for position at the cut

**The original leaves both R1 and P1 uncertain.** Elias and Maya reach the eastern wall, tumble into the service plenum and look deeper. The final paragraph places the breaker housing at the passage end. No passage fixes the pair’s distance from it at the cut or excludes a visit throughout scene four. The completed ending does settle the narrower question of whether it explicitly narrates their arrival. [Exact draft passages and versions](../../data/diagnostics/wading-path-three-claims-regression-2026-11-24/scope-audit.json)

## R1 · Did both reach the housing at some time during scene four?

A single joint arrival during the scene establishes the claim, even if both leave afterward. To rule out the claim, the draft needs a fact incompatible with both people having reached that housing anywhere in the relevant interval. Two sufficient forms are a reliable statement covering the entire interval or a continuous physical constraint. For example, a barrier can exclude a visit if the account establishes that at least one named person started on the other side, the barrier blocked every route to the housing, and it held through the cut. The exclusion must also cover time before the barrier appeared or after it ceased to hold. This is a criterion for the assessor. The writer can convey it through ordinary action or leave it open.

In the original, the opening places both people in the center of the flooded room (0–488). Later they cross the room (3558–3993), reach the wall and enter the plenum (3995–4323). The look deeper and the description of the housing (4325–4804) close the account. Sol’s R1 explanation said the scene ended “without their traversing the passage.” Its citation establishes the order of narrated actions. It supplies no scene-wide exclusion. This matters even if its last sentence is read as saying that arrival lacks proof. That reading still leaves the evidence needed for a definite negative missing. [Observed R1 explanation and sealed decision](../../data/diagnostics/wading-path-three-claims-regression-2026-11-24/capture/run/sealed-evidence-decisions.json) · [Masked explanations](../../data/diagnostics/wading-path-three-claims-regression-2026-11-24/capture/operator/evidence-sheet.json)

## P1 · Are both at the housing at the final narrated instant?

One observation can settle P1 if it locates the named people relative to the housing at the cut. The explicit-arrival ending leaves both there. The measured stop and the retreat endings leave both three strides away. An earlier observation can also suffice when the prose establishes that the position persists through the cut. If motion resumes and the destination remains open, the earlier distance loses that force. For this joint claim, locating one person elsewhere at the cut would also rule out both being there. The text would still need separate evidence to locate the other person.

Sol’s P1 explanation correctly identified tumbling into the plenum as the last narrated movement, then said the staging “places the housing ahead of them.” The light is farther down the shaft (4325–4571), and the housing stands at the passage end (4573–4804). Those descriptions leave the pair’s exact final position open. The plan’s `E0258` assigns reaching the housing. Its authority concerns the assignment. Evidence for fulfillment comes from the selected draft’s `E1420`. [Version-bound audit](../../data/diagnostics/wading-path-three-claims-regression-2026-11-24/scope-audit.json)

| Audited draft | Visit during scene four | Position at the housing at the cut | Decisive evidence |
| --- | --- | --- | --- |
| Original | Uncertain | Uncertain | Wall, entry, look deeper, then housing description through 4804. |
| Explicit arrival | Supported | Supported | The last sentence places both people at the housing, 4806–4920. |
| Measured stop short | Uncertain | Unsupported | Both stop three strides short and stay there, 4806–4945. Earlier visits remain open. |
| Arrival then retreat | Supported | Unsupported | Both arrive at 4806–4920, step back three strides and stay there at 4922–5008. |

The stop and retreat controls give the same answer about the cut and different answers about a visit. The arrival and retreat controls give the same answer about a visit and different answers about the cut. **None of these four drafts supplies a scene-wide exclusion.** The arrival-only and stop-short readings are local source controls from the earlier rehearsal. The latest live comparison assessed the original and retreat. Offsets are zero-based Unicode character offsets, end exclusive. [Earlier frozen gold](../../tests/fixtures/wading_path_three_claims_gold.json) · [Live results](wading-path-three-claims-sol-high-results-2026-11-24.md)

## Seven observed regressions

| Case | Frozen gold | Sol returned | Judgment / 1 | Evidence / 1 |
| --- | --- | --- | ---: | ---: |
| R1 · Original, visit during scene | Uncertain | Unsupported | 0 | 0 |
| P1 · Original, position at cut | Uncertain | Unsupported | 0 | 0 |
| N1 · Original, narrated arrival | Unsupported | Unsupported | 1 | 1 |
| N2 · Retreat, narrated arrival | Supported | Supported | 1 | 1 |
| R2 · Retreat, visit during scene | Supported | Supported | 1 | 1 |
| P2 · Retreat, position at cut | Unsupported | Unsupported | 1 | 1 |
| Q008 B · Ordinary assignment and narration control | Unsupported | Unsupported | 1 | 1 |

The private archive seals 61 members under SHA-256 `344884c7adbb929cd2c57ecb16e9c6d319393730d374504180aa91b535e825ee`. Offline replay rebuilt both request bodies for each case, verified all 14 intents and terminals against the closed journal, resolved the citations and reproduced every score from frozen gold and the original sealed evidence decisions. Q008 also matched both historical request hashes. The observed decision stays `hold_claim_scope`. [Archive manifest](../../data/diagnostics/wading-path-three-claims-regression-2026-11-24/capture-manifest.json) · [Replayed scores](../../data/diagnostics/wading-path-three-claims-regression-2026-11-24/replay.json)

The archive is stored in the project’s local diagnostics directory. With that archive present, run `python -m scripts.wading_path_three_claims.regression` to replay the observed responses or `python -m scripts.wading_path_three_claims.coverage` to inspect the four drafts. All 47 focused tests passed, including checks for missing or exchanged deliveries, an exchanged draft request, damaged gold or evidence and source-version binding. Repository-wide Ruff lint, formatting and strict mypy passed across 445 Python files. This audit made zero provider calls. [Regression tests](../../tests/evaluations/test_wading_path_visit_position_audit.py) · [Test results](../../data/diagnostics/wading-path-three-claims-regression-2026-11-24/verified.xml)

## Proposed next step

**Rehearse ten local cases by adding just one diagnostic draft.** Keep the measured-stop ending verbatim and append one reliable observation establishing that, from the opening huddle through the cut, neither person was ever closer to the housing than the final three strides. Keep their final position identical. Freeze the exact version, both claims and their evidence criteria before writing any fixture answers.

Score the visit and cut-position claims on the original, arrival, measured stop, retreat and new full-scene exclusion. The decisive comparison is measured stop versus full-scene exclusion. Only the visit label should change, from `uncertain` to `unsupported`. Final position should remain `unsupported` in both. Include a fixture that gives the correct negative visit label but cites only the last gap. It should earn the judgment point and lose the evidence point. Carry the five passing observed controls forward. A successful rehearsal would justify considering a separately frozen model comparison. B remains the default, production prompts are unchanged and the full workflow canary stays on hold.
