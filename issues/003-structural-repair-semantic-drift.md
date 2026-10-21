# Structural report correction can change a correct judgment or repair the wrong explanation

Local ID: **CW-003**. Status: **OPEN**; restricted correction is only partly effective.

## Problem

A correction intended to make a report structurally valid can change its meaning. Preserving some classifications or restricting edit locations does not guarantee that the resulting judgment and explanation remain supported.

## Recorded evidence and attempts

- In the route-index experiment, two rejected responses correctly marked the decision met. Their structurally valid retries changed it to unmet, making condition ownership legal by introducing a wrong story judgment.
- Expanded feedback did not add recoveries over ordinary feedback. Full regeneration still required the model to recreate substantial report content; error locations could change between attempts.
- Restricted correction F1 recovered 6/8 failed parents versus F0's 4/8, but its two a01 responses replaced the comparison with an explanation about entry alone. The duplicate survives removing entry; that independence was not explained. Both corrections were structurally valid but unqualified. The later output-contract comparison reproduced this semantic gap in F1.

## Expected behavior and diagnostic case

Start with a saved report containing a localized structural error and otherwise supported findings. After correction, compare every changed judgment and explanation with the original prose. An explanation added for independent duplication must answer that question, not merely restate a genuine boundary breach.

## Closure criteria

- [ ] Correct the declared structural defect without unsupported changes to unaffected judgments, findings or evidence.
- [ ] Verify the meaning of changes inside permitted locations, not only preservation outside them.
- [ ] Preserve already valid control reports and reject incomplete or unsupported repairs within the frozen retry limit.

Do not blindly freeze every claim from an invalid parent as truth. Supported preservation and correction of an unsupported parent claim need distinct policies. Exact parent binding and response-shape failures have separate drafts.

## Sources

- [Route-index retry drift](https://github.com/sasadjukic/openHollywood/blob/08cd9bca404f614b4be527e3d986813bb47abc15/docs/benchmark_reports/fulfillment-routing-framing-v61-results-2026-10-17.md)
- [Restricted-correction results](https://github.com/sasadjukic/openHollywood/blob/08cd9bca404f614b4be527e3d986813bb47abc15/docs/benchmark_reports/fulfillment-repair-surface-review-v61-results-2026-10-18.md)
- [Later F1/F2/F3 results](https://github.com/sasadjukic/openHollywood/blob/08cd9bca404f614b4be527e3d986813bb47abc15/docs/benchmark_reports/fulfillment-output-contract-v61-retry-results-2026-10-19.md)
