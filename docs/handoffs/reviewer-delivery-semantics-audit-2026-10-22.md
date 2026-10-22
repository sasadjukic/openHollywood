# C2 delivery investigation and follow-up decision

Date: **2026-10-22**. Status: **LOCAL INVESTIGATION COMPLETE; NO NEW INFERENCE**.

Retain DeepSeek/C2 as diagnostic evidence and Gemma's failures as negative delivery
fixtures. The local checks justify a small, staged experiment, described in the
[comparison proposal](reviewer-isolated-comparisons-proposal-2026-10-22.md). They do
not establish a delivery fix or a production-qualified reviewer.

The [October 21 results](../benchmark_reports/reviewer-interface-repeat-v61-results-2026-10-21.md)
remain unchanged: Gemma **0/32 valid**, DeepSeek **32/32 valid and 22/32 usable**.
Production prompt **61**, graph **9**, fulfillment policy **1**, provider behavior
and human checkpoints are unchanged. The full workflow canary remains **ON HOLD**.

## Scope and source integrity

The audit independently rereads every raw Gemma answer, preserving duplicate
occurrences instead of loading the answer into a dictionary that drops one. It
also replays all 32 valid DeepSeek answers as positive delivery controls.

Verified against their historical hashes:

- **104** preparation files and **two** preparation documents.
- **465** execution evidence files, including requests, raw responses, receipts,
  inspection records and the prior analysis.
- Preparation plan SHA-256:
  `9246680ddc52832107f5e814a5cddb07c8b436932ab7f368ffb6a523b1a83142`.
- Execution manifest SHA-256:
  `3d2514cde691c7b87c1eb499a7322d0da2d5987c26384984123110c19f78ad9d`.

Historical bundles and scores were not rewritten. The new work made **zero model
calls and zero daemon discovery calls**. A read-only visit to official Ollama
documentation checked the separate constrained-output question; no story material
was sent to that website.

## What all 32 captures show

Every Gemma capture has exactly this root-field sequence:

```text
task_checks
fact_checks
craft
endpoint_check
group_assessments
literary_comparison
mandatory_failure
mandatory_failure_assessment
overall_assessment
endpoint_check
```

The repeated key is already present in the captured provider text. Application
normalization did not introduce it. All captures completed with normal stop and
were rejected by the strict duplicate-key parser.

| Finding | Captures |
| --- | ---: |
| Root `endpoint_check` occurs twice | 32/32 |
| The two complete endpoint objects are identical | 29/32 |
| Endpoint status and evidence agree between occurrences | 32/32 |
| Another independently observable structural defect | 6/32 |
| Accepted by either the existing validator or the layout prototype | 0/32 |

The three differing endpoint objects differ only in assessment wording:
`h03 / 20261021 / RO`, `h03 / 20261022 / OR`, and `h04 / 20261021 / RO`.
Identical duplicate values are still invalid. Neither the first nor the last
occurrence is silently selected.

The six additional failing cells are:

| Cell: case / seed / order | Independent defect |
| --- | --- |
| h01 / 20261021 / OR | Corrupted task reference, outside the exact task-ID enum |
| n04 / 20261021 / OR | Empty required task evidence |
| n04 / 20261021 / RO | Empty required task evidence |
| n04 / 20261022 / RO | Empty required task evidence |
| h04 / 20261022 / RO | Empty evidence for neutral voice on changed prose |
| n01 / 20261022 / RO | Empty evidence for neutral agency, tension and voice on changed prose |

Thus eliminating the repeated endpoint alone would not establish reliable delivery.
Evidence cardinality is a separate matter: the prior run had no eight-reference
overflow. Exact task identity is also distinct from quotation-reference binding.

## A concrete layout hypothesis, with limits

The schema contains no duplicate property or required name. However, its compact
serializer alphabetizes object keys, including `properties`, while retaining the
construction order of each `required` array. **All 640 object-schema presentations
across the 64 requests have different property and required orders.**

At the root, `endpoint_check` is second in the displayed alphabetical properties
and last in `required`. In the answers it appears fourth and last. That pattern is
consistent with Gemma following a familiar review sequence, then appending a field
again while satisfying the final required list. It does **not** demonstrate this
internal process. The captures do not distinguish schema order from learned output
habits or interactions with the prose instructions. DeepSeek delivered unique keys
under the same interface, so the input does not force the duplication.

A diagnostic-only layout prototype now uses one order for `properties` and
`required` at every object. Its root sequence is:

```text
task_checks, fact_checks, endpoint_check, group_assessments, craft,
literary_comparison, mandatory_failure, mandatory_failure_assessment,
overall_assessment
```

Nested objects follow their existing required order. The prototype changes only
schema presentation: field membership, types, enums, bounds, evidence rules, task
IDs, source packets, system instructions and the final-contract prose are preserved.
All 64 message transformations were checked; every message preceding the final
schema and the final message's prose prefix remain identical.

The parser still accepts any JSON object-member order and requires each field
exactly once. Output order is not a new correctness condition. The 640 presentation
mismatches become zero; **32 valid DeepSeek captures still validate and all 32 Gemma
captures still fail**. This is compatibility evidence for a future layout test,
not offline recovery of failed inference. It is not a request bundle or live freeze.

## Constrained output is a separate provider capability

The current adapter rejects `response_schema` for cloud deployments before any
transport call, including cloud tags routed through the local daemon. Mock-only
tests verify this for both exact tags, `gemma4:31b-cloud` and
`deepseek-v4.1-flash:cloud`. Neither test reaches even its mocked HTTP handler.

Ollama's official [structured-output documentation](https://docs.ollama.com/capabilities/structured-outputs),
checked on October 22, also states that cloud structured outputs are currently
unsupported. Therefore schema enforcement is not a supported fix on this route.
Prompting for JSON is not provider-enforced structure. A different deployment or
future capability would require its own verification; the audit did not bypass the
adapter or try an undocumented cloud option.

## Semantic diagnosis and evaluation decisions

The [explicit contrasts](reviewer-semantic-contrast-design-2026-10-22.md) separate:

1. An event that happened, a state that must continue, and a required final state.
   A causal dependency is tested only when the assignment actually requires it.
2. Carrying out an editing request, touching the same subject, and permission for
   the edit. Supporting a consequence of a bad edit cannot authorize its cause.
3. A forbidden but logically possible transition and incompatible statements
   about the same entity at the same time. Genuine contradictions need a positive
   control, alongside permitted transitions and uncertain narration.

The remaining errors have different causes or plausible explanations. All four
DeepSeek h03 reports strengthen the endpoint into a cause-specific state. Seven
h03/n03 group labels use `direct` for edits that touch the relevant content while
also marking them unsupported; these are **not seven endorsements of bad edits**.
Two h04 reports correctly flag departure but invent a contradiction between staying
earlier and leaving later. Correct labels cannot rescue unsupported explanations.

The name `request_relation` and label `unrelated` themselves invite a relevance
interpretation. C2's explicit definitions do not eliminate that interface problem.
A vocabulary comparison is therefore warranted, rather than assuming every
disagreement proves an inability to judge edit permission. Historical scores remain
the frozen scores; future field names must not retroactively improve them.

The earlier caveat about two invalid Gemma n03 compound task explanations remains:
their wording can refer to the assignment as a whole. Do not upgrade that ambiguity
into a certain contradiction merely to strengthen the diagnosis.

## Verification and durable local evidence

**96 tests pass**, covering all 64 archived delivery outcomes, all 64 layout
transformations, exact quote/version expansion, root and nested duplicates,
missing/extra fields, required evidence, task/record binding, eight versus nine
references, no-op exceptions, valid reordered object members and both cloud
capability guards. Ruff lint/format and strict mypy pass for both new private
scripts. An initial pytest collection-name error was corrected before the final
passing run; its failed XML remains alongside final evidence. No application-wide
build or new production behavior is claimed.

Local ignored bundle:
`data/diagnostics/reviewer-delivery-semantics-audit-v61-2026-10-22/`.

- [Reproducible audit](../../data/diagnostics/reviewer-delivery-semantics-audit-v61-2026-10-22/audit.py)
  and [per-capture findings](../../data/diagnostics/reviewer-delivery-semantics-audit-v61-2026-10-22/audit.json).
- [Eight ordered schema prototypes](../../data/diagnostics/reviewer-delivery-semantics-audit-v61-2026-10-22/layout-prototypes.json).
- [Regression tests](../../data/diagnostics/reviewer-delivery-semantics-audit-v61-2026-10-22/test_local.py)
  and [final test evidence](../../data/diagnostics/reviewer-delivery-semantics-audit-v61-2026-10-22/verification-complete-pytest.xml).
- [Verification record](../../data/diagnostics/reviewer-delivery-semantics-audit-v61-2026-10-22/verification.json).

These private links do not publish the local prose/capture bundle on GitHub. The
public documents preserve the findings, example contrasts and proposed decisions.
CW-001, CW-008, CW-010 and CW-013 remain open, with the qualification limit in
CW-014. No external issue was edited or closed.

The user's nine human ties remain valid. Humans should assess feel, emotion, flow,
character and story-breaking details; machines should prepare mechanical counts,
assignment evidence and editing-request checks. These tests should improve the
reliability of that assistance, not make minimal wording changes a proxy for story
quality. **Step 19 IN PROGRESS; Step 20 NOT STARTED.**
