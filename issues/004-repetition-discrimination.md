# Repetition detection is sensitive to presentation and can reject valid language

Local ID: **CW-004**. Status: **PARTIALLY MITIGATED** for sentence detection; older word-level generalization remains **DEFERRED**.

## Problem

The critic must distinguish accidental duplication from grammatical or expressive repetition. Catalog presentation has hidden accidental repeats, while stronger proofreading instructions have also condemned valid language. A blanket repeated-word deletion rule would damage prose.

## Recorded evidence and attempts

- September full-critic tests missed an accidental doubled word in 3/3 trials. A general proofreading instruction recovered detection and one-word advice in 3/3 paired trials.
- The subsequent short-excerpt test falsely required changes to the valid sentence “He passed her her mittens.” in 3/3 trials under both compared instructions. These were excerpt diagnostics, not unchanged production-critic results. This concern was explicitly deferred; later closure evidence was not found.
- October P1 continuous prose improved raw sentence-duplicate detection from 0/4 to 4/4, preserving the negative controls. Only 2/4 findings initially arrived in valid reports; a later run reached 3/4. Delivery is separately tracked in CW-002.
- Successful duplicate repairs and functional-recurrence controls are positive evidence. They do not establish general discrimination across constructions or scene families.

## Expected behavior and diagnostic case

Pair clear accidental word/sentence duplication with valid grammatical doubles, interrupted speech and purposeful recurrence, in complete narrative context. Deterministic counting should supply occurrences; contextual judgment should decide whether they are defects.

## Closure criteria

- [ ] Detect and cite accidental duplication without requiring removal of grammatical or intentional repetition.
- [ ] Verify fresh constructions and full-critic transfer, distinguishing raw noticing from valid actionable reports.
- [ ] Keep defect severity proportional and do not infer whole-story quality from a local repeat count.

This issue tracks detection and false positives. Contradictory or excessive repair instructions after detection belong to CW-005. Historical word-level results must not be presented as newly reproduced v61 failures.

## Sources

- [31B evaluation register, T08–T11](https://github.com/sasadjukic/openHollywood/blob/08cd9bca404f614b4be527e3d986813bb47abc15/docs/benchmark_reports/gemma4-31b-evaluation-register-2026-09-11.md)
- [P1 presentation results](https://github.com/sasadjukic/openHollywood/blob/08cd9bca404f614b4be527e3d986813bb47abc15/docs/benchmark_reports/fulfillment-presentation-temperature-v61-results-2026-10-17.md)
- [Later P1 delivery results](https://github.com/sasadjukic/openHollywood/blob/08cd9bca404f614b4be527e3d986813bb47abc15/docs/benchmark_reports/fulfillment-reporting-edit-purpose-v61-results-2026-10-17.md)
