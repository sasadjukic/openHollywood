# ADR 0009: Distinguish viewpoint inference from private access

- Status: Accepted
- Date: 2026-09-08

## Context

The graph v7 / prompt v27 isolated suite returned eight valid responses in eight
calls. Local 002/003 recovered from the earlier false viewpoint blockers, and
both Bible probes preserved resolved-thread history. However, Local 005 passed
with no issues despite directly narrating Cora's private feelings with Elara
explicitly assigned. Its approved literary/internalized style did not specifically
authorize that perspective shift. Response validation therefore concealed a
failed semantic positive control.

## Decision

Clarify the critic's prompt rather than adding a new workflow node, response
certificate, keyword-based prose gate, or general ban on interiority.

- Preserve the assigned character's thoughts, feelings, deductions, and free
  indirect narration. They need not be spoken or marked as hypotheses.
- Preserve other characters' speech, observable reactions, and inferences
  attributable to the assigned character in context. No special inference label
  is required.
- Direct assertions of another character's unspoken feelings, thoughts, memories,
  or knowledge require specific approved narrative permission. Generic literary,
  internalized, emotional, or empathetic style, an ensemble cast, and familiarity
  with the other character do not supply that permission. A brief intrusion can
  be a violation even when the rest of the scene remains correctly focused.
- Honor approved omniscient narration and authorized within-scene shifts. Keep
  the approved style verbatim; do not infer permission from matching a keyword
  such as "omniscient" without interpreting negation or scope.
- Use surrounding narrative attribution, not isolated mental-state verbs. The
  plausibility of an emotion does not itself convert direct private narration
  into an inference by the assigned character.

The critic receives compact, explicitly non-canonical contrasting examples.
Actual findings still use only the existing exact current-draft evidence handles
and typed violation route. Aligned reviews remain status-only; reviewer-format
repair does not acquire authority over the manuscript. No new response fields
or model calls are required.

New requests use prompt v28 with unchanged graph v7. Existing v27 probes,
requests, reports, and approved artifacts are not retagged. Writer instructions,
continuity/adjudication behavior, output schemas, Bible reducers, profile routing,
budgets, revision limits, and human approval remain unchanged. No SQL migration
is needed.

## Verification and rollout

Offline tests cover prompt delivery on Local and Cloud, exact preservation of
approved style, unassigned/fallback origins, certificate-free aligned responses,
and conversion of a reported true violation into an exact blocking issue despite
a high craft score. Simulated responses do not establish model comprehension.
An explicit false-negative test demonstrates that an incorrect aligned judgment
can still validate; semantic evaluation remains separate.

`benchmarks/v0.1/production-probes-v28.json` predeclares Local 002, 003, and 005
against unchanged historical inputs. Local 002/003 must not acquire false
viewpoint blockers; Local 005 must identify Cora's unauthorized private access.
The registry's expected outcomes are review criteria, not fabricated model
results or an automatic canary trigger. These probes have not been run.

Keep the full canary on hold pending live semantic checks and separate launch
authorization. Preserve v23/v25 comparison baselines and Step 19's IN PROGRESS
status. Do not claim repeatability or literary quality from these controls.
