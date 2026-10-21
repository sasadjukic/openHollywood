# Diagnostic reviewers still violate response shape and required evidence fields

Local ID: **CW-008**. Status: **OPEN across tested interfaces**; earlier input echo and truncation were mitigated in later comparisons.

## Problem

The diagnostic reviewer sometimes emits an ambiguous or incomplete assessment: duplicate JSON keys, missing output fields, input-shaped content, or empty evidence where the contract requires support. This prevents a usable report independently of whether its narrative labels are correct.

## Recorded evidence and attempts

The first comparative-assessment run produced no valid report in eight completed slots, including their retries. The next call copied input until reaching the 8,000-token output cap and triggered the frozen stop. A later matched comparison improved delivery from V0's 0/18 to V2's 15/18 valid reports. V0 still produced six capped input echoes; V2's three failures lacked required evidence for neutral craft effects.

The October 20 run had **no truncation**. Remaining V2 failures included three Gemma reports without craft citations, one without a task citation, and one DeepSeek report with duplicate `purpose_checks` keys. Both duplicated values were empty, but the strict parser correctly rejected the ambiguity. Gemma/C1 had no structural failures in this draw; that does not qualify all interfaces or deployments.

## Expected behavior and local investigation

Audit the output envelope independently from source payloads. Define useful evidence requirements for neutral and negative judgments explicitly, rather than forcing ornamental citations or silently accepting missing support. Replay saved malformed reports as regression fixtures under any proposed new contract.

## Closure criteria

- [ ] Deliver the exact declared output shape without duplicate keys, copied input envelopes or missing required fields.
- [ ] Specify and exercise evidence rules for no-change, neutral and no-mandatory-failure cases.
- [ ] Keep bounded output and stop handling; never parse a truncated response as a finished review.
- [ ] Demonstrate delivery across the intended models and controls without relaxing the historical scores.

This issue concerns shape and completeness. Exact source binding is CW-007; evidence-array size is CW-009. None should be closed merely because a permissive parser can recover an answer.

## Sources

- [Initial comparative-assessment stop](https://github.com/sasadjukic/openHollywood/blob/08cd9bca404f614b4be527e3d986813bb47abc15/docs/benchmark_reports/fulfillment-repair-surface-review-v61-results-2026-10-18.md)
- [Output-contract comparison](https://github.com/sasadjukic/openHollywood/blob/08cd9bca404f614b4be527e3d986813bb47abc15/docs/benchmark_reports/fulfillment-output-contract-v61-retry-results-2026-10-19.md)
- [Latest delivery failures](https://github.com/sasadjukic/openHollywood/blob/08cd9bca404f614b4be527e3d986813bb47abc15/docs/benchmark_reports/reviewer-gemma-deepseek-v61-results-2026-10-20.md)
