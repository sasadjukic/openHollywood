# The Wading Path · what “before the barrier” and “matches the outcome” meant in Q011

**Keep B as the default.** Both measured-stop answers found the decisive sentence and quoted the right distance. Their failure under the frozen rubric was deciding *which requirement* that distance contradicted. On the original ending, B and O both rejected fulfillment. Only O’s explanation stayed within what the narration established. The seven historical scores and the decision `hold_controls` are preserved. [Frozen criteria](wading-path-sol-high-observations-freeze-2026-11-24.md) · [Observed results](wading-path-sol-high-observations-results-2026-11-24.md)

## Why three strides short counted as “before”

In scene-four plan v1, the goal is “Reach the master breaker panel.” The outcome, `E0258`, is “They reach the breaker panel housing.” The exit state, `E0254`, is “They are standing before the final barrier.” Read together, these describe ending the scene at the housing. Read separately, “before” can also describe a position on the approach side of the barrier. The exit field supplies no distance, contact or reachability criterion. The declared assessment scope lists two material components and leaves `unresolved_qualifiers` empty. The narrower proximity reading used to score the measured stop was explicit in the operator gold. The model received the plan’s original wording. [Exact request and declaration](../../data/diagnostics/wading-path-observations-regression-2026-11-24/capture/run/requests/K3-B-generation.json) · [Frozen gold](../../data/diagnostics/wading-path-observations-regression-2026-11-24/capture/run/gold.json)

The authored final sentence puts **both people three full strides short and keeps them there** (draft `2f9e80a0…`, offsets 4806–4945). B and O both treated that as being before the barrier. O explicitly said the wording required “no specified distance or contact.” Both used the shortfall to reject reaching the housing. The frozen criterion assigns the contradiction to **position at the cut**. Where the pair finish cannot by itself exclude a visit earlier in the scene. Sol and the frozen gold reached the same whole-claim label through different components. Under the broader spatial reading, the final gap alone still cannot settle whether they reached the housing during the scene. That explains the two **1/0** scores. It also limits what they establish about model ability on a claim that specifies its spatial relation clearly. [Verbatim answers](../../data/diagnostics/wading-path-observations-regression-2026-11-24/capture/operator/evidence-worksheet.json) · [Version-bound passages](../../data/diagnostics/wading-path-observations-regression-2026-11-24/capture/operator/cited-locations.json)

The historical critic request gives the outcome blocking weight and the exit state advisory weight. The next scene assigns opening the panel and tripping the breaker. These fields help explain the intended staging and why reaching the housing is salient. They describe assignments. They cannot establish a visit, standing position or contact in this draft. Neither answer invoked the enforcement weights, so attributing the error to those weights would go beyond the record. [Historical assignment and scene boundary in the saved request](../../data/diagnostics/wading-path-observations-regression-2026-11-24/capture/run/requests/K3-O-generation.json)

## Why the original still drew `unsupported`

The original draft locates the pair at the eastern wall and entering the plenum (3995–4323), then looking deeper (4325–4571). The final paragraph places the **housing** at the passage end and identifies it as the barrier (4573–4804). The light farther down locates the light. None of these observations fixes the pair’s final distance or posture. The complete text can settle whether a traversal is narrated while leaving physical attainment unresolved. Q008 tested the narration question on this very draft and earned **1/1**. [Original draft and sources](../../data/diagnostics/wading-path-observations-regression-2026-11-24/capture/operator/cited-locations.json)

| Response | What the reason did with the missing arrival | Judgment / evidence |
| --- | --- | --- |
| Q011 B | Said “no subsequent movement brings them to it,” placed the barrier ahead at the endpoint and called the fulfillment claim inaccurate. That extends the last narrated movement into a physical conclusion. | 0/0 |
| Q011 O | Bounded the observation to the pair’s “last narrated position” and explained why identifying the barrier does not establish either endpoint. It still selected `unsupported`, which requires a material contradiction. | 0/1 |
| Q008 B | Restricted its conclusion to what the full account depicts through its final line. It correctly rejected the review’s claim of a **narrated** arrival. | 1/1 |

The Q011 brief asks “Does the ending fulfill the assigned outcome and exit state?” Its declaration uses `endpoint_compliance` and `positive_depiction`. A reader can reasonably ask whether the writing *demonstrates compliance*. The frozen factual question asks whether the events occurred. For that question, missing demonstration plus no incompatible observation leaves the answer `uncertain`. The system definition associates uncertainty with unavailable material evidence. Here the draft is available and the pair’s position is unknown. This mismatch is a plausible explanation for O’s label. The records give Sol’s stated reasons. Its internal decision process is unobserved. The byte-identical earlier Q011 B request scored **0/1**. This B repeat scored **0/0**. A single paired evidence gain cannot establish a stable effect of repeating observations. [Delivered request](../../data/diagnostics/wading-path-observations-regression-2026-11-24/capture/run/requests/K1-O-generation.json) · [Earlier baseline](wading-path-position-and-judgment-audit-2026-11-24.md)

## Regressions and verification

| Preserved case | B judgment / evidence | O judgment / evidence |
| --- | --- | --- |
| Q011 original | 0/0 | 0/1 |
| Q011 explicit arrival | 1/1 | 1/1 |
| Q011 measured stop short | 1/0 | 1/0 |
| Q008 original, narrated arrival | 1/1 | B only |

The private archive contains 51 run files, seven operator files and four historical source/provenance files. Its manifest SHA-256 is `f053b71703ef5d1df3a0aa76cbce3d18c99ebdbac7485504096757111b7ca980`. Replay reconstructs the seven work items from the archived intake and selected drafts, checks all 14 request bodies against their recorded intents and terminals, resolves the cited versions, then reproduces the masked worksheet and both scores from the sealed decisions. The capture contains the historical baseline fingerprints and scores used in this audit. [Sealed inventory](../../data/diagnostics/wading-path-observations-regression-2026-11-24/capture-manifest.json) · [Replay output](../../data/diagnostics/wading-path-observations-regression-2026-11-24/replay.json)

Run `python -m scripts.wading_path_observations.regression` with the repository interpreter. If reconstruction is needed, `--preserve` verifies the original local records against the pinned manifest before installing a replacement archive. Full story and response captures live under the ignored local data directory. The observed-capture tests require those files. [Replay code](../../scripts/wading_path_observations/regression.py) · [Regression tests](../../tests/evaluations/test_wading_path_observations_regression.py)

All 72 focused tests passed, including 11 for this archive. The new tests check all seven observed score pairs, the byte-identical B repeats, and rejection of exchanged arm responses, a substituted request or missing capture evidence. The standalone replay test disables network access. Repository-wide Ruff lint, formatting and strict mypy passed across 435 Python files. [Archive, rehearsal and selection checks](../../data/diagnostics/wading-path-observations-regression-2026-11-24/verified.xml) · [Injected harness checks](../../data/diagnostics/wading-path-observations-regression-2026-11-24/injected.xml)

## Recommended next step

**Rehearse three single factual questions locally before another live test.** Keep the current stories, baseline and scores. Use the same draft to ask (1) whether the ending explicitly narrates both people reaching the housing, (2) whether they reached it at any time during this scene, and (3) whether both are at the housing at the cut. Preserve Q008 as the narration control. For a production claim worded “standing before,” record whether the source authorizes a proximity reading. If that choice remains open, retain the ambiguity for editorial review.

Add one authored control in which both reach the housing, then step back three strides and stay there. It separates arrival during the scene from position at the cut. These are **proposed local expectations** for the new questions. Freeze each whole claim and its passage-level criteria before writing fixture answers.

| Ending | Narrates arrival | Reached during this scene | At housing at cut |
| --- | --- | --- | --- |
| Original | Unsupported | Uncertain | Uncertain |
| Explicit arrival | Supported | Supported | Supported |
| Measured stop | Unsupported | Uncertain | Unsupported |
| Proposed arrival then retreat | Supported | Supported | Unsupported |

Require independent evidence and judgment scores. A correct label justified by the wrong component must still fail evidence. If a local reader can defend the component relations and equivalent evidence independently, a small Sol-high comparison on the original and retreat cases could test whether those distinctions survive inference. An unresolved reading belongs in the scope record before spending more calls. B remains the default, live calls are paused and the full workflow canary stays on hold.
