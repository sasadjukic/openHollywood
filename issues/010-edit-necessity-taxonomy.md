# Edit-necessity scoring conflates request status, task relevance and repair authorization

Local ID: **CW-010**. Status: **OPEN EVALUATION-DESIGN ISSUE**, identified in the 2026-10-20 inspection.

## Problem

The current categories do not cleanly distinguish whether a task is optional, whether an edit directly addresses it, and whether an adjacent change is needed only because another edit was made. This can penalize a supportable explanation or make an unsupported rewrite look necessary.

## Recorded evidence

Six valid reports classified requested optional cleanup as `optional_craft` where the frozen key expected `direct_repair`: Gemma r04 in both interfaces, Gemma/C1 r10, and r11 in Gemma/C1 and both DeepSeek interfaces. Their prose generally recognized that the request was addressed without inventing a mandatory obligation.

In r05, Gemma/C1 rejected the core deletion but classified later callback adjustments as `required_adjacent`. Recognizing conditional consistency work does not authorize the original deletion. The rubric allowed grammatical dependencies while the key rejected every fragment. In r09, `a` → `an` supports `study` → `exercise`, creating another plausible dependency interpretation.

There are genuine contradictions too: both raw DeepSeek r05 reports called deletion of required content destructive while labeling the deletion `direct_repair`. Ambiguous scoring must not conceal that failure.

## Proposed local investigation

Represent request obligation, relationship to the request, support for the selected change, and conditional dependency as separate questions. Specify what qualifies as necessary repair versus optional craft before writing a new answer key.

## Closure criteria

- [ ] Give requested optional cleanup an unambiguous classification without turning it into a production obligation.
- [ ] Distinguish a justified grammar dependency from permission for the edit that created it.
- [ ] Resolve known rubric/key disagreements offline, retaining uncertainty where warranted.
- [ ] Version the revised rubric and preserve every historical frozen score and sensitivity note.

This is not evidence that all six optional-cleanup reports justified unnecessary rewrites. Human literary preference must remain separate from these task-accounting categories.

## Source

- [Latest report: necessity taxonomy and scoring sensitivities](https://github.com/sasadjukic/openHollywood/blob/08cd9bca404f614b4be527e3d986813bb47abc15/docs/benchmark_reports/reviewer-gemma-deepseek-v61-results-2026-10-20.md)
