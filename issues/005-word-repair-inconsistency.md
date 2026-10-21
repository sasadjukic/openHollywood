# Word-level repair advice can contradict its deletion count or remove valid wording

Local ID: **CW-005**. Status: **DEFERRED OPEN FOLLOW-UP** from September testing; no later closure evidence.

## Problem

Correct defect detection and valid JSON do not ensure an internally consistent repair. A writer can receive a deletion count that disagrees with the proposed result, or a grammatical correction that unnecessarily removes valid structure.

## Recorded evidence and attempts

The September minimal-repair candidate explicitly requested the smallest correction, preservation of grammatical repetition, a deletion count and resulting wording. All 84 compared responses were structurally valid, but minimal advice was 17/21 for the reference and 15/21 for the candidate.

For “He passed her her her mittens.”, the candidate instructed deletion of two words while printing “He passed her her mittens.” in 3/3 trials. That result requires one deletion. For the tripled “that” control, two candidate responses contradicted their counts; a third consistently deleted two words where one would preserve the original construction. These were recommendations, not executed patches.

The successful sentence-duplicate writer test is useful counterevidence to a general inability to make precise edits. It does not resolve these word-level instructions.

## Expected behavior and diagnostic case

Given exact source text and a proposed replacement, compute the actual change and compare it with the recommendation. Separately check whether a smaller correction retains grammatical meaning: arithmetic consistency alone cannot detect every excessive deletion.

## Closure criteria

- [ ] Make the stated count, selected span and resulting text agree on saved and fresh controls.
- [ ] Preserve valid tense, grammatical repetition and intended meaning while removing the actual defect.
- [ ] Execute accepted repairs and re-review the result without unrelated edits; verify transfer beyond the short-excerpt interface.

This is a mechanical repair-quality issue, not a general preference for the shortest sentence. Repetition classification is tracked separately in CW-004.

## Sources

- [31B register, T10–T11](https://github.com/sasadjukic/openHollywood/blob/08cd9bca404f614b4be527e3d986813bb47abc15/docs/benchmark_reports/gemma4-31b-evaluation-register-2026-09-11.md)
- [Original deferred follow-up](https://github.com/sasadjukic/openHollywood/blob/08cd9bca404f614b4be527e3d986813bb47abc15/docs/issue_drafts/gemma4-31b-critic-repair-follow-up.md)
