# Comparative reviewers label byte-identical prose as a loss

Local ID: **CW-012**. Status: **OPEN**, reproduced through 2026-10-20.

## Problem

An existing defect or an unfulfilled request can be mistaken for deterioration caused by a revision. A comparison of identical text under identical context should report no textual gain or loss, while separately reporting that the task remains unaddressed.

## Recorded evidence and attempts

In the October 19 b07 optional-craft no-op, all six raw reviews noticed the retained duplicate and correctly kept mandatory failure false. The second-seed V2 and V3 reviews nevertheless labeled naturalness as a loss. V2 was valid; V3 had a separate binding failure.

The October 20 DeepSeek/V2 r01 report again assigned `naturalness.effect = loss` to byte-identical prose, despite an overall tie and an explanation that the defect was unchanged. Nine of ten valid no-op reports were invariant; the other two no-op cells were invalid. A correct overall preference label therefore does not guarantee consistent dimension labels.

## Expected behavior and diagnostic case

Supply the same prose as original and revision with an optional defect, then with a genuine mandatory defect. The comparative effects should remain neutral in both cases; task completion and the mandatory-failure flag should reflect the still-existing defect. Include successful edits so that invariance does not become an always-neutral response policy.

## Closure criteria

- [ ] Keep overall and dimension-level comparative effects invariant for identical prose and context.
- [ ] Distinguish unchanged defects, missed improvements and actual deterioration in labels and explanations.
- [ ] Detect the invariant mechanically and expose contradictions without silently rewriting model results.
- [ ] Retain sensitivity to real gains and losses under a separately frozen comparison.

This issue does not prohibit a reader from noticing something new on rereading. It concerns the reviewer's claim about a textual change that did not occur.

## Sources

- [October 19 b07 results](https://github.com/sasadjukic/openHollywood/blob/08cd9bca404f614b4be527e3d986813bb47abc15/docs/benchmark_reports/fulfillment-output-contract-v61-retry-results-2026-10-19.md)
- [October 20 r01 results](https://github.com/sasadjukic/openHollywood/blob/08cd9bca404f614b4be527e3d986813bb47abc15/docs/benchmark_reports/reviewer-gemma-deepseek-v61-results-2026-10-20.md)
