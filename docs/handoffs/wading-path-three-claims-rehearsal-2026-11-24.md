# The Wading Path · narrated arrival, a visit during the scene, and position at the cut

**Ready to freeze a small Sol-high diagnostic on the original and arrival-then-retreat endings.** On the original, the complete account omits arrival and leaves the pair’s physical history and final position open. On the retreat version, both people explicitly reach the housing, then leave it. The local scoring distinguished all three propositions on the same prose. [Prior scope audit](wading-path-observations-scope-audit-2026-11-24.md) · [Local replay](../../data/diagnostics/wading-path-three-claims-rehearsal-2026-11-24/replay.json)

## Gold and exact sources

Before writing any fixture answers, we froze three whole claims, the four complete draft identities and prose hashes, judgment gold, and passage-level evidence criteria for every cell. The three claims ask whether the ending explicitly narrates Elias and Maya reaching the master breaker panel housing, whether both reached it at any time in scene four, and whether both are at it at the final narrated instant. The last claim specifies the destination directly. The historical plan’s “standing before the final barrier” still permits a broader spatial reading. That wording remains an editorial question when the source leaves the intended proximity open. [Frozen claims and gold](../../tests/fixtures/wading_path_three_claims_gold.json)

The retreat control preserves the entire explicit-arrival draft. After the sentence placing Elias and Maya at the housing (4806–4920), the new paragraph reads “Then Elias and Maya stepped back three full strides from the housing and stayed there.” The new paragraph occupies 4922–5008, end exclusive, in diagnostic draft `ae1fb3f6-5e23-597a-a61f-020b9cc8e254`. The measured-stop draft instead ends with both stopping three strides short and staying there. Of these two endings, only the retreat version records arrival before the final gap. [Exact retreat source](../../data/diagnostics/wading-path-three-claims-rehearsal-2026-11-24/retreat-source.json) · [Archived source versions](../../data/diagnostics/wading-path-observations-regression-2026-11-24/capture/operator/cited-locations.json)

## Judgment and evidence

Each cell shows the grounded fixture’s returned label. **All twelve earned 1/1**, one point for judgment and one for evidence. The evidence worksheet showed the claim, exact draft version, prose hash, cited spans with their resolved quotations, and the explanation. We graded those views with the returned labels and fixture names masked, then joined the recorded evidence decisions to the labels. There were 17 answers and 16 distinct views because the label-only control shares its entire evidence with another answer. [Authored answers](../../tests/fixtures/wading_path_three_claims_answers.json) · [Masked evidence worksheet](../../data/diagnostics/wading-path-three-claims-rehearsal-2026-11-24/evidence-worksheet.json) · [Independent evidence decisions](../../tests/fixtures/wading_path_three_claims_evidence.json)

| Selected ending | Ending narrates arrival | Both reached during scene four | Both at the housing at the cut |
| --- | --- | --- | --- |
| Original | Unsupported | Uncertain | Uncertain |
| Explicit arrival | Supported | Supported | Supported |
| Measured stop short | Unsupported | Uncertain | Unsupported |
| Arrival then retreat | Supported | Supported | Unsupported |

In the original ending (3995–4804), the pair reach the eastern wall, enter the plenum and look deeper. The final description locates the housing. This suffices to reject a claim that the text narrates arrival. In the measured-stop ending (4806–4945), the persistent gap also settles where they finish. Neither ending establishes whether they visited the housing earlier in the scene. The separate historical Q008 B control also replayed at **1/1** under its original criteria for the plan assignment and the narrated action. All twelve new answers were authored locally. [Historical Q008 decision](../../data/diagnostics/wading-path-observations-regression-2026-11-24/capture/operator/scores.json)

| Diagnostic answer | Judgment / 1 | Evidence / 1 | Why |
| --- | ---: | ---: | --- |
| Original, reject narrated arrival by claiming physical impossibility | 1 | 0 | The housing’s location cannot establish physical impossibility or cover what the pair did through the ending. |
| Original, rule out any visit because arrival was omitted | 0 | 0 | An omission alone cannot settle the event over the scene. |
| Measured stop, answer uncertain about a visit and cite only final position | 1 | 0 | The explanation answers where the pair finish and leaves the earlier-event question unaddressed. |
| Retreat, reject final presence by denying any visit | 1 | 0 | The preceding sentence explicitly records the visit. |
| Retreat, change only the correct visit label to unsupported | 0 | 1 | The same cited explanation still establishes that both reached the housing before departing. |

## Verification and readiness

Gold SHA-256 is `e900a94f71e68842950fd762080ccc3389af9c25feb0e4485932ebb7332ccb64`. The independent evidence decision SHA-256 is `654da1ab97c5d69bd7fa4f54a4593da507996492d7052a46d55f50ec61e54d19`. Run `python -m scripts.wading_path_observations.three_claims` with the repository interpreter and the private archive present. All 55 focused tests passed, including 16 for this rehearsal. Repository-wide Ruff lint, formatting and strict mypy passed across 437 Python files. The tests check all twelve cells, five diagnostic answers, the Q008 replay, exact versions and offsets, masked scoring, and rejection of stale or changed evidence. [Rehearsal code](../../scripts/wading_path_observations/three_claims.py) · [Regression tests](../../tests/evaluations/test_wading_path_three_claims.py) · [Verification record](../../data/diagnostics/wading-path-three-claims-rehearsal-2026-11-24/verified.xml)

For a next freeze, use B with one active factual claim per request on the original and retreat drafts. That gives six assessments. Include the original Q008 B request once as a live narration control, for seven counts before up to seven generations, zero retries, subject to separate approval. Hold the selected draft and context fixed across its three claims. Keep operator gold and evidence decisions out of the requests. Require both scores on each cell and report the original and retreat results separately.

The rehearsal establishes a usable scoring distinction. Whether Sol applies it remains untested. None of the four drafts rules out a visit throughout the entire scene, so the rehearsal cannot qualify a negative judgment on that wider claim. Such a judgment would need evidence covering the full interval. B remains the default, production prompts are unchanged, live calls are paused and the full workflow canary stays on hold.
