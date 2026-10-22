# Unresolved critic and writer issues

Inventory date: **2026-10-21**. Evidence reviewed through the completed 64-call Gemma/DeepSeek C2 repeat on 2026-10-21.

These are **14 local issue documents**, published to GitHub by the user. The table preserves the user-supplied links. `CW-001` through `CW-014` remain local tracking IDs; their corresponding GitHub issue numbers are shown in the linked URLs. Local documents provide the evidence and scope for each issue; a preparation update does not close the GitHub issue.

The inventory covers the critic/writer investigation and its unresolved evaluation dependencies. It is not an inventory of every historical application or provider failure. Each file has its own expected behavior and closure criteria; related symptoms are not counted as independent experiments or independent story samples.

| Local ID | Focused issue | Current status | GitHub issue |
| --- | --- | --- | --- |
| [CW-001](001-event-fulfillment-versus-endpoint.md) | A later boundary violation is mistaken for a missing earlier event | Open; C2 retains earlier events, but missing-event/final-state conflation persists | https://github.com/sasadjukic/openHollywood/issues/97 |
| [CW-002](002-compound-critic-report-routing.md) | Independent craft plus boundary findings produce invalid ordinary reports | Open; improved noticing has not fixed delivery | https://github.com/sasadjukic/openHollywood/issues/98 |
| [CW-003](003-structural-repair-semantic-drift.md) | Structural correction changes judgments or answers the wrong comparison | Open; restricted correction only partly effective | https://github.com/sasadjukic/openHollywood/issues/99 |
| [CW-004](004-repetition-discrimination.md) | Accidental repetition is missed or valid repetition is condemned | Partial diagnostic improvement; word controls deferred | https://github.com/sasadjukic/openHollywood/issues/100 |
| [CW-005](005-word-repair-inconsistency.md) | Word-repair advice contradicts its count or removes too much | Deferred; no later closure evidence | https://github.com/sasadjukic/openHollywood/issues/101 |
| [CW-006](006-writer-edit-scope.md) | Writers expand a repair into unsupported surrounding edits | Open; exact patching works, selection unqualified | https://github.com/sasadjukic/openHollywood/issues/102 |
| [CW-007](007-model-authored-evidence-binding.md) | Model-written hashes and quote identities break evidence binding | Partial mitigation with application-owned binding | https://github.com/sasadjukic/openHollywood/issues/103 |
| [CW-008](008-diagnostic-report-delivery.md) | Diagnostic reports violate response shape or required evidence fields | Open; all 32 Gemma/C2 reports duplicate the endpoint key | https://github.com/sasadjukic/openHollywood/issues/104 |
| [CW-009](009-evidence-cardinality.md) | Short-reference reports exceed the evidence-array bound | Partial C2 mitigation; no eight-ref overflow in this repeat | https://github.com/sasadjukic/openHollywood/issues/105 |
| [CW-010](010-edit-necessity-taxonomy.md) | Necessity scoring mixes request status, edit relevance and authorization | Partial C2 separation; request-relation confusion persists | https://github.com/sasadjukic/openHollywood/issues/106 |
| [CW-011](011-editorial-diff-grouping.md) | Token fragments are treated as independent editorial decisions | Partial diagnostic mitigation through complete groups | https://github.com/sasadjukic/openHollywood/issues/107 |
| [CW-012](012-no-op-comparative-invariance.md) | Unchanged prose receives a comparative loss label | C2 DeepSeek 8/8 valid no-ops invariant; broader closure outstanding | https://github.com/sasadjukic/openHollywood/issues/108 |
| [CW-013](013-unsupported-review-explanations.md) | Correct verdicts contain unsupported narrative premises | Open; labels alone miss these failures | https://github.com/sasadjukic/openHollywood/issues/109 |
| [CW-014](014-story-quality-qualification.md) | Diagnostic gains do not establish improved whole-story experience | Open qualification gap | https://github.com/sasadjukic/openHollywood/issues/110 |

## How the drafts fit together

- CW-002 concerns the ordinary production critic's ownership and comparison routes. CW-003 concerns what changes during correction of a report. CW-007 concerns exact identity binding. CW-008 concerns the diagnostic response shape and required fields. CW-009 isolates the evidence-count policy. Fixing one does not close the others.
- CW-004 concerns whether a defect exists; CW-005 concerns the proposed repair after a defect is identified. The older combined [31B draft](../docs/issue_drafts/gemma4-31b-critic-repair-follow-up.md) is retained as history. Its unresolved detection and repair concerns are represented here; do not also publish that broad draft as a duplicate. Its score-calibration concern belongs with CW-014.
- CW-006 tracks edit selection. CW-010 and CW-011 track how we represent and score those edits. Their ambiguities must not be reported as demonstrated writer errors.
- CW-014 is an evaluation follow-up, not an umbrella bug to close by resolving the other thirteen. Earlier full-story evaluations exist; current diagnostic candidates have not established a whole-story quality benefit.

The three preparation changes recommended in the latest report map to: interface audit (CW-007, CW-008, CW-010, CW-011); bounded evidence policy (CW-009); and a later repeat with fresh contexts and controls (especially CW-001, CW-012, CW-013, with qualification limits in CW-014).

Preparation update **2026-10-21**: the [local audit and evidence-policy decision](../docs/handoffs/reviewer-interface-audit-2026-10-21.md) and [frozen 64-call C2 repeat](../docs/handoffs/reviewer-interface-repeat-frozen-plan-2026-10-21.md) now exist. C2 separates task relation, edit support and conditional dependency, groups complete paragraph changes, and bounds evidence at eight distinct references. Eight historical/fresh pairs cross both models, seeds and display orders. Local verification passes 80 tests. All issues remain open; no live calls, production adoption or external issue updates have occurred.

Subsequent approved execution **2026-10-21**: the [C2 results](../docs/benchmark_reports/reviewer-interface-repeat-v61-results-2026-10-21.md) record **64/64 calls**, no retries or truncation. Gemma delivers **0/32 valid** because every answer repeats `endpoint_check`; six also contain another structural defect. DeepSeek delivers **32/32 valid, 22/32 usable**, failing the total and per-case screening thresholds. Its eight valid no-ops are invariant, all sixteen valid permissible controls avoid mandatory false alarms, and neither model exceeds the eight-reference bound. Remaining findings include missing-event/endpoint conflation, request-relation confusion and two correct-label reports with unsupported contradiction claims. Conditional cleanup is distinguished from permission for the bad root edit. These are limited diagnostic findings, with no simultaneous C1 control or demonstrated whole-story benefit. All issues remain open; the linked issue bodies retain their original historical evidence, and no external issue was changed or closed.

## Completed work that is not reopened

- Shared repair ownership and consolidation passed their focused matrix. The durable version-bound fulfillment handoff is implemented. Remaining compound-report and semantic failures have separate drafts above.
- Exact edit application has worked mechanically, and several optional duplicate repairs succeeded. CW-006 does not claim that exact patching itself is broken.
- The nine-pair human review is complete, including the eighteen machine-prepared editing-request evidence fields. Blank concern fields mean no major concern; the packet is not awaiting completion.
- The failed preflight was followed by a completed 74-call comparison. That historical interruption is not an outstanding outage.
- The first Gemma/DeepSeek run completed 48 calls and the C2 repeat completed 64, both without truncation. Earlier truncation remains historical delivery evidence; C2's current delivery failure is duplicate-key output.
- The focused v59 assignment/repair matrix improved over earlier unsupported causal demands. Those old failures are not presented as universally unresolved; later event-attribution and unsupported-explanation failures remain separately evidenced.

## Evidence and boundaries

Issue bodies link to committed reports at a fixed repository revision, so their links remain usable when copied into GitHub. Detailed raw requests, unpublished prose and captures remain in local ignored evidence bundles; a source report may contain links into those private bundles. No issue body depends on a public upload of that material, and this task does not publish it. Case IDs identify recorded observations, not a runnable public fixture package.

The reader reported **nine overall ties** across closely related samples. Preserve that result: extra editing is not established literary harm, byte preservation is not a quality metric, and a valid report is not necessarily a true report. Future human review should focus on feel/emotion, flow, character and story-breaking concerns, with mechanical evidence prepared by machines.

Production remains **prompt 61 / graph 9 / fulfillment policy 1**. The full workflow canary is **ON HOLD**; Step 19 remains **IN PROGRESS**, Step 20 **NOT STARTED**. Creating these drafts authorizes no new model calls, prompt changes, experiment budget, production role or human checkpoint. Closure criteria below describe future work; none is marked complete by this inventory.

Starting references: [latest C2 report](../docs/benchmark_reports/reviewer-interface-repeat-v61-results-2026-10-21.md), [earlier reviewer report](../docs/benchmark_reports/reviewer-gemma-deepseek-v61-results-2026-10-20.md), [retrospective](../docs/handoffs/critic-writer-retrospective-and-next-tests-2026-10-19.md), [human review](../docs/handoffs/critic-writer-human-review-results-2026-10-20.md), and [authoritative tracker](../open_hollywood_bible/step_by_step_implementation.md).
