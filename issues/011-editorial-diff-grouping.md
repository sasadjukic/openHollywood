# Token-level diff fragments produce misleading explanations of editorial changes

Local ID: **CW-011**. Status: **OPEN REPRESENTATION ISSUE**, observed on 2026-10-20.

## Problem

A token diff is precise mechanical evidence, but an isolated fragment may not represent a meaningful editorial decision. Requiring a separate explanation or necessity label for each fragment can detach words from their grammar and narrative role.

## Recorded evidence

The r07 ending replacement was split into eleven changed units. Gemma/C1 described the isolated `returning.` → `room` fragment as simplifying a room description. The old phrase concerned the pragmatist returning, not a room description. Both models identified the larger lost truce, so a correct whole-edit observation did not prevent a misleading local explanation.

Another fragment, `can't` → `cannot`, can reasonably be an optional register change even when the complete edit is unacceptable. Treating the whole edit's label as the only permitted label for every token fragment obscures that distinction.

## Proposed local investigation

Use sentence or clause groups as the unit of editorial explanation while retaining exact token differences in a machine appendix. Build deterministic mappings from each group to original/revised spans and individual edits. Grouping must not hide unrelated changes or convert a partly defective sentence into permission to replace all its content.

## Closure criteria

- [ ] Preserve exact, version-bound mechanical differences and account for every changed span.
- [ ] Present enough syntax and context for each editorial judgment to identify what the text actually says.
- [ ] Exercise deletion, insertion, split/merge, local grammar and multi-purpose replacement cases offline.
- [ ] Keep group-level and fragment-level claims distinct in scoring; report unresolved alignment explicitly.

This is a representation fix to evaluate, not evidence that larger replacements improve stories. Necessity-category ambiguity is separately tracked in CW-010, and factual support must still be inspected after grouping.

## Source

- [Latest report: token fragments and local dependencies](https://github.com/sasadjukic/openHollywood/blob/08cd9bca404f614b4be527e3d986813bb47abc15/docs/benchmark_reports/reviewer-gemma-deepseek-v61-results-2026-10-20.md)
