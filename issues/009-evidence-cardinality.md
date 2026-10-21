# Short-reference evidence arrays exceed the diagnostic contract's six-reference limit

Local ID: **CW-009**. Status: **OPEN**, observed in DeepSeek/C1 on 2026-10-20.

## Problem

Moving exact quotation binding into the application reduced copying work, but some reports then supplied more evidence references than the contract permits. We need an explicitly usable bounded evidence policy; silently dropping references would conceal the failure and could discard necessary support.

## Recorded evidence

All five invalid DeepSeek/C1 reports—r04, r05, r07, r08 and r12—contained seven or eight references in at least one array capped at six. They were complete JSON responses with known references and normal stop reasons. This was not truncation or an inability to generate JSON.

DeepSeek validity fell from 10/12 under V2 to 7/12 under C1, and usable supported assessments fell from 6/12 to 5/12. Two previously usable cases were lost specifically to this bound. Gemma/C1 delivered 12/12 valid reports. These observations identify the rejection mechanism, not the model's internal reason for ignoring the limit.

## Proposed local investigation

Replay the five saved outputs, examine which references are necessary, and decide whether the interface should request representative support, group evidence differently, or use another justified finite bound. Evaluate the policy against both short and distributed evidence. A higher limit is not automatically the correct solution.

## Closure criteria

- [ ] Document the intended evidence-selection policy and its finite limits before a new freeze.
- [ ] Exercise lower-bound, exact-bound, excessive, duplicate, irrelevant and distributed-support cases offline.
- [ ] Preserve enough support for each claim without silently trimming returned arrays.
- [ ] Keep altered-contract replay separate from historical results; confirm any live improvement only in an approved bounded comparison.

This issue does not require new prose, a provider change or an immediate live experiment. Other structural defects and factual accuracy remain independently scored.

## Source

- [Gemma/DeepSeek delivery failures and next steps](https://github.com/sasadjukic/openHollywood/blob/08cd9bca404f614b4be527e3d986813bb47abc15/docs/benchmark_reports/reviewer-gemma-deepseek-v61-results-2026-10-20.md)
