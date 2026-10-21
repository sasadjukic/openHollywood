# Critics treat a later boundary violation as erasing an earlier fulfilled event

Local ID: **CW-001**. Status: **OPEN**, evidence through 2026-10-20.

## Problem

A scene can establish a required event and subsequently violate a separate endpoint rule. Critics sometimes mark the earlier event unmet instead of retaining its fulfillment and reporting the later violation separately. This can send a writer an unnecessary request to restate or recreate something already present.

## Recorded evidence and attempts

- In the October 17 route-index comparison, both arms incorrectly marked Elena's decision to check the handwriting unmet when the scene later established a prohibited match. Each arm matched 8/12 final classifications; the clean, genuinely missing and explicitly compound-outcome controls behaved correctly.
- Event-scoped guidance and narrow adjudication produced useful diagnostic gains, but did not qualify the ordinary critic. A route index did not resolve the attribution problem.
- In the October 20 comparison, both DeepSeek interfaces said departure lost or dissolved an already established truce. Departure violated the locked-room endpoint; the agreement still occurred. The V2 report was valid, the C1 report invalid for a separate reason. Gemma correctly separated these facts.

## Expected behavior and diagnostic case

Use a scene with an explicit agreement followed by forbidden departure. Compare it with an agreement-only version, a genuinely missing-agreement version, and a version whose assignment explicitly requires the agreement to remain in force at the endpoint. Event fulfillment and final-state compliance must be evaluated against their own conditions. Implicit action can establish a decision; an explicit declaration is not inherently required.

## Closure criteria

- [ ] Correctly separate fulfilled events, genuine missing events, revoked states and explicit compound obligations on saved cases and fresh contexts.
- [ ] Attribute repair advice to the actual failed condition without requiring redundant fulfillment.
- [ ] Demonstrate valid, supported ordinary reports as well as correct raw labels under a separately frozen comparison.

This issue is about obligation attribution, not a rule that later events can never negate an ongoing state. It does not establish a literary preference between endings.

## Sources

- [Route-index results](https://github.com/sasadjukic/openHollywood/blob/08cd9bca404f614b4be527e3d986813bb47abc15/docs/benchmark_reports/fulfillment-routing-framing-v61-results-2026-10-17.md)
- [Gemma/DeepSeek results: r08](https://github.com/sasadjukic/openHollywood/blob/08cd9bca404f614b4be527e3d986813bb47abc15/docs/benchmark_reports/reviewer-gemma-deepseek-v61-results-2026-10-20.md)
