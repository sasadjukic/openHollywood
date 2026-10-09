# Later scene reservation comparison

Date: 2026-10-09. Production prompt v39 / graph v9 unchanged.

**The explicit next-scene reservation is not necessary for the observed missed
overrun.** The frozen OH-V01-002 scene passes under all three tested seeds both
with and without that reservation. Without it, the critic explicitly recognizes
completed handwriting verification, then treats this as satisfying the assigned
decision to verify. Removing the reservation does not recover detection.

This narrows the explanation; it does not establish why the model makes that
judgment. Story-wide guidance about verification remains in both conditions, so
the experiment cannot separate its influence from interpreting the current
outcome as a minimum achievement rather than a stopping point.

## Controlled design

The user approved twelve isolated critic probes on the existing Ollama Cloud
Gemma4 deployment. The design was fixed before inference:

| Fixture | Seeds | With reservation | Without reservation |
|---|---|---:|---:|
| Original scene-1 overrun | 19102, 19103, 19104 | 3 | 3 |
| Inconclusive preliminary investigation | 19102 | 1 | 1 |
| Explicitly authorized verification | 19102 | 1 | 1 |
| Missing ten-year-future turning point | 19102 | 1 | 1 |

Each pair uses the same exact v39 artifact versions, prose, current assignment,
system instructions, output schema, evidence catalog, model settings and seed.
The only request-content change is `scene_boundary.next_scene`: the existing
reservation in condition A, `null` in condition B. Three pairs run A then B and
three run B then A, in predeclared order. Condition B is 217 characters shorter.
The source seed is 19102; the other two seeds vary only between original-case
pairs, never within a pair.

The original and controls retain their exact versions and content hashes from
the [v39 experiment](binding-endpoint-v39-2026-10-08.md). The inconclusive test
adds a smudged one-letter comparison that establishes nothing. The authorized
control uses the original prose with synthetic current-plan permission to verify
handwriting, while withholding acceptance of the warning. The missing-turn
control replaces the required future date with today's date. Synthetic contexts
remain unapproved diagnostic fixtures.

An isolated process temporarily projects the reservation as absent for both
request construction and result materialization/auditing. Full source artifacts
remain immutable. The projection is restored between trials and never changes
production source. This matters because otherwise an absent-reservation request
could be paired with misleading application-generated repair advice or an audit
that still claimed the model had seen that reservation.

In both conditions, v39's existing schema and validator can still accept an
`overrun` anchored to the current outcome. Offline simulated responses verified
that an overrun forces revision with or without the reservation; removing it
does not disable the route. All other payload fields and provider settings were
verified equal within each pair, including story-wide guidance.

## Verdicts and response repairs

| Fixture | With reservation | Without reservation | Boundary result |
|---|---|---|---|
| Original overrun | PASS, 3/3 | PASS, 3/3 | Missed in both conditions |
| Inconclusive attempt | PASS | PASS | No false overrun |
| Authorized verification | PASS | PASS | No false overrun |
| Missing required turn | REVISE | REVISE | Independent assignment blocker preserved |

Every validated response returns `no_overrun`. All passes have three 5/5 craft
scores; both missing-turn critiques have a 3.67 mean. The positive case is missed
throughout, so passing the legitimate controls does not establish discrimination.

Ten probes validate on their first calls. Two original-case reviews in condition
A, at seeds 19102 and 19104, require one structural repair each: they emit
three-digit evidence ordinals such as `draft_evidence_034_...` instead of the
catalog's exact four-digit `draft_evidence_0034_...`. Validation correctly rejects
the unknown handles. These are review-response failures, not manuscript defects.
Both repaired responses validate and pass.

Accordingly, only the 19103 original pair is a fully validated first-call pair.
All three original responses without the reservation validate on their first
calls. The two rejected initial A responses also propose PASS/no-overrun, but
remain unvalidated evidence and are not counted as accepted critiques. Final
paired outcomes include the declared structural-repair policy, not identical
first-call-only conditions for every seed.

The batch used fourteen calls against the approved maximum of twenty-four.
There were no semantic rerolls or outcome-dependent additions.

## What the explanations show

With the reservation, the original-case reviews continue to describe initial or
preliminary verification while reserving the more specific flourish or full
acceptance of the card as a warning for scene 2.

Without the reservation, all three original reviews explicitly say Elena has
verified the handwriting against her journals. Each then says the current
outcome of deciding to verify is met or achieved. Their next-scene comparisons
acknowledge absent context but call verification and internal crisis the stopping
point, preserving later plot or decision-making in general terms.

Thus the explanation changes while the verdict stays the same. The critic does
not need the explicit reservation to accept a result beyond the assigned
decision. Its wording is consistent with checking whether an outcome occurred
without separately enforcing that the scene stops there. These are observable
review conclusions, not access to the model's internal reasoning.

The authorized-verification control correctly cites the changed current outcome
in both conditions. However, the same prose also passes under the original
decision-only outcome. The pair still fails to demonstrate sensitivity to whether
verification is authorized.

For the inconclusive-test control, the A response now mentions the failed
immediate attempt; B focuses on the later decision to compare journals. Both
pass. Neither selects the inserted test itself as boundary evidence, so this
is evidence of no false positive rather than uniformly complete explanation.

The missing-turn control produces a blocking `scene_assignment:turning_point`
issue in both conditions. Both also add a blocking plot issue: B restates the
date's conflict with the premise; A makes the broader claim that removing the
future date eliminates the speculative element. The assignment violation is the
clear supported blocker. The small sample does not support a broader claim about
changes in criticism quality.

## Remaining context and next target

Condition B removes the explicit adjacent reservation, not all future-oriented
context. Its unchanged Blueprint projection still includes:

- A creative-brief assumption that verification uses copied private flourishes
  and comparisons with old journals.
- A story-wide requirement that handwriting be verified through story action.
- The apartment's story function as the place of arrival and handwriting
  verification.
- Broader premise, character, relationship and world context, alongside the
  current scene's goal of understanding the card and summary of trying to debunk it.

These fields are legitimate story guidance, but they do not allocate that work
to this scene. Their continued presence prevents a conclusion that the critic
would make the same mistake from the current scene plan alone. Three requested
seeds on one story also do not establish general model behavior; the provider's
seed handling and remote weights are not guaranteed immutable.

The next useful diagnostic is to separate story-wide goals from current-scene
obligations: compare the full no-reservation context with a minimal current-plan
and draft context, retaining the same review policy and the inconclusive and
authorized-verification controls. This would test whether broader guidance
contributes before changing production context or adding more instructions.
Neither that experiment nor a further response-contract change is included here.

## Provenance and cost

Source commit: `66be525efb095e9f827cd32ce5f07f96241d52b0`.
The original source critic invocation remains
`d2758b4f-7a66-4587-b7c6-fc5386ff20b6`. The read-only benchmark snapshot retains
SHA-256 `71618ce4d66ffd3b8ecc46fa4d034105b4e59aa5a80946b5364272b87caeafb2`.

The existing local Ollama daemon forwarded `gemma4:31b-cloud` to Ollama Cloud.
The model alias digest remains
`c382fbfbc73b6fdd08c8549c23caedc6e62eb09933c65a1fb82dbf3398320a4e`.
Per-call limits were 24,000 input / 8,000 output tokens. Complete runtime details,
source/code hashes, model outputs and the approved plan are retained locally.

The fourteen calls used **146,702 input / 9,643 output tokens**. At the recorded
October 8 [Gemma4 rates](https://ollama.com/library/gemma4:31b-cloud), assuming
uncached input at USD 0.14/M and output at USD 0.40/M, the estimate is
**USD 0.02439548**, below the approved allocation estimate of USD 0.15744.
Actual charges remain unknown; this is not a newly verified tariff or billing
receipt. The gateway's zero placeholder with `cost_basis: unknown` does not
establish that inference was free.

All prepared/live request hashes, exact artifact hashes, captured response
hashes and projected audits verified. Every attempt's request was reconstructed,
including both structural retries; every validated result rematerialized exactly.
The unchanged probe and endpoint suites passed **36 focused tests**. Application
source did not change, so the full build/test gates were not repeated for this
documentation and isolated diagnostic change.

Evidence is in `data/diagnostics/reservation-context-v39-2026-10-09/`:
`experiment.py`, `plan.json`, `prepared-v2/`, complete `live/` attempts and
`assessment.json`.

Production remains v39 / graph v9. Canonical stories, sealed benchmarks and
historical results are unchanged. **The diagnostic comparison is complete;
Step 19 remains IN PROGRESS and Step 20 is NOT STARTED.**
