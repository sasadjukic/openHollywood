# Correct review verdicts can rely on unsupported narrative premises

Local ID: **CW-013**. Status: **OPEN**, observed in ordinary and comparative reviews.

## Problem

A critic can identify a real defect and produce correct labels while adding false or unsupported claims about chronology, motivation, voice or what changed. Those explanations can steer later editing even when the core verdict is defensible. Exact quotation binding and label accuracy do not establish semantic support.

## Recorded evidence

- DeepSeek/C1 r06 passed every frozen label but claimed that reflection already occurred after a completed comparison. The source only placed a journal beside a card to check it. The real boundary violation remained valid; the added chronology did not.
- DeepSeek/V2 r11 extended a character's avoidance of abstraction into a claim about the narration's register, although the narration contains abstraction.
- Earlier ordinary compound reviews overclaimed that a handwriting match established acceptance of a warning. The explicit no-match boundary supported the repair independently of that claim.
- Earlier comparative reviews praised changed imagery without adequately accounting for removed preparation or conditions. A favorable reading can be defensible, but it must not misdescribe the original or omit relevant changes when the review task requires their assessment.

## Expected behavior and next investigation

Inspect claim support separately from the verdict. Contrast preparation with completed action, character voice with narration, explicit text with inference, and retained facts with changed expression. Permit supported disagreement and uncertainty about literary effect.

## Closure criteria

- [ ] Ground consequential factual premises in the full source context, including correct temporal and speaker scope.
- [ ] Catch unsupported explanations even when every categorical label is correct.
- [ ] Account for relevant additions and removals without treating every difference as reader harm.
- [ ] Exercise fresh story families and presentation-order controls in any later approved diagnostic.

This issue tracks explanation reliability. Event/endpoint attribution and no-op contradictions have their own narrower issues. Agreement between two models is not independent validation of a premise.

## Sources

- [Latest semantic inspection](https://github.com/sasadjukic/openHollywood/blob/08cd9bca404f614b4be527e3d986813bb47abc15/docs/benchmark_reports/reviewer-gemma-deepseek-v61-results-2026-10-20.md)
- [Ordinary critic overclaims](https://github.com/sasadjukic/openHollywood/blob/08cd9bca404f614b4be527e3d986813bb47abc15/docs/benchmark_reports/fulfillment-reporting-edit-purpose-v61-results-2026-10-17.md)
- [Comparative trade-off inspection](https://github.com/sasadjukic/openHollywood/blob/08cd9bca404f614b4be527e3d986813bb47abc15/docs/benchmark_reports/fulfillment-output-contract-v61-retry-results-2026-10-19.md)
