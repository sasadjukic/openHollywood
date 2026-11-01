# Context-preserving staged admission audit — 2026-11-01

**Local audit complete; no inference, daemon discovery or database access.**
Production prompt61 / graph9 / fulfillment policy1 remain unchanged. Further
inference is **PAUSED** and the full workflow canary remains **ON HOLD**.

The [SA/SO results](../benchmark_reports/reviewer-selection-only-v61-results-2026-11-01.md)
support testing assessment of the actual model-selected premises. They do not
support routing those selections directly to a writer. This audit implements a
data-only handoff prototype and preserves the relevant captures, without adding
a production adapter, graph node, prompt, persisted schema or model request.

## Decisions

**Preserve a selection as a proposition in its complete field context. Do not
silently change the assessment unit to the whole field.** A field may contain
multiple claims, including a valid boundary criticism beside an unsupported
missing-decision allegation. Full field visibility prevents context loss, but
does not make every statement in that field part of the selected proposition.

The application can establish which exact selection belongs to which complete
field and report version. It cannot infer that two selected components constitute
the same complete claim, or that their correct support labels establish the
report's relation between them. Keep those operations separate:

| Operation | Local result | Authority |
| --- | --- | --- |
| Bind quote, offsets, pointer, full field and report/source versions | Verified for all 41 selections | Mechanical identity evidence |
| Keep selections linked to the same report and field | Verified; all extras and repeats retained | Structural provenance only |
| Preserve the prior inspector's cross-selection coverage links | 24 authored groups retained in a separate audit; two span multiple selections | Authored diagnostic evidence, excluded from model input |
| Infer whole-claim support from component labels | Explicitly disallowed | Still unresolved |
| Turn selected criticism into repair advice | Explicitly disallowed | No writer authorization |

This follows ADRs [0005](../adr/0005-versioned-artifacts-and-bounded-context.md),
[0037](../adr/0037-durable-writer-fulfillment-handoff.md),
[0038](../adr/0038-read-only-review-evidence-export.md) and
[0039](../adr/0039-diagnostic-probe-review-export.md). The existing production and
October-16 probe exporters have narrower source contracts. These SO captures are
not retagged as eligible production critics or inserted into either exporter.
The new prototype lives only in the local diagnostic bundle.

## Sources and regression fixtures

The audit pins the prior publication closure
`62b81b9fcfd89e3b401d4847d21c9caaf5ccc2589c8e62b2893d06d9ff31a659`
and SA/SO plan
`4ab67cbefa480bfec751e58d7a5c66d5b03be05278773027471c6a9a822f9a99`.
It verifies **917 source fingerprints** and preserves **154 exact fixture files**:
the eight valid SO cells, the SA empty-final cell, sealed inspection records,
cases/schedule, execution accounting and results. Historical bytes, scores, stops
and counters are unchanged. New hypothetical contrasts are labeled as authored,
not captured model outputs.

**S-SA-H2-CP** remains an unusable HTTP-200 length response with 15,265 input and
16,000 generated tokens, an empty final and the original two-level gateway error
chain. The handoff rejects it. Verified raw usage neither creates a successful
response nor releases the reservation or permits another attempt. The previous
SA/SO run still has ten consumed attempts and six unspent retired cells.

The new source reader reads sealed JSON data and never imports archive Python.
The separate verification process also replays the existing read-only result
verifier to check that historical conclusions remain unchanged. No live runner
is called.

## Prototype handoff

Each of the eight exported packets includes:

- Exact prepared/live request, wire, raw-response and receipt fingerprints; the
  report and scope artifact identities; all input artifact versions and hashes.
- Complete source artifacts, declared availability/scope, the unchanged source
  citation index, full saved report and report-field inventory.
- Every selected quote with its original ordinal, field ID, pointer, exact Unicode
  code-point offsets and field/quote fingerprints. No Unicode normalization or
  re-selection by similarity occurs.
- Complete bound fields, with explicit selection-to-field and same-report links.
  A field shared by multiple selections is stored once with its selection IDs;
  this is storage sharing, not semantic deduplication.
- Explicit **support unreviewed / materiality unreviewed / semantic links not
  inferred / whole-claim aggregation not authorized / writer dispatch false**.
  Production invocation and canonical review IDs remain null.

The model-facing data view contains no authored targets, expected labels, inspected
evidence, duplicate judgments or semantic group answers. The original critique
remains visible as source data, including its existing scores and opinions.
The local model view is not a request: there are no outgoing messages, model
settings, inference runner or approval file for a new experiment.

Validation reconstructs the packet from authenticated saved data. Recomputing a
modified packet's own hashes cannot make the modified context valid. The export
guards structured data and serialized text before writing, rejects changed or
partial destinations and source/archive destinations, and verifies identical
repeats without rewriting them. A manifest is written last. The local limits are
1 MiB per handoff and 32 MiB per export, with whole-packet rejection and no trimming;
these are tooling limits, not new model or story-length budgets.

## Context and relation findings

There are **41 selected units across 40 field instances**, including **ten partial-field
quotes**. All remain bound to the full field. Three prior coverage decisions
especially depend on this contract:

1. H1/CP selects the observed match and the no-match obligation separately. The
   full U007 field contains their original endpoint comparison.
2. H2/CP selects the outside obligation and observed entry separately. The full
   U003 field contains the original violation claim.
3. F4/CP's selected quote stops before its field's “violating the assigned boundary”
   clause. The complete U005 field preserves that relation.

These links survive the projection. They remain **authored coverage links**, not
application-generated semantic proofs. A later assessment of “the draft establishes
a match” must not be reported as an assessment of the whole endpoint comparison.
Nor may the application declare a comparison supported just because both an event
and an obligation received supported labels.

The local counterexample makes that limitation explicit: “the draft establishes
a match” and “the assignment forbids a match” can both be supported while “therefore
the draft complies with the no-match endpoint” is unsupported. The handoff does not
run conjunction-based truth aggregation.

**120 mutation checks** cover all eight packets: shortened fields, removed
assignment/source context, changed identities/actors/polarity/quotes/offsets,
missing or swapped links, dropped/duplicated selections, injected gold and
promotion to supported status or writer authority. They are rejected even after
the local packet hash is recomputed. This establishes integrity against the saved
source, **not machine understanding of attribution or negation**.

Four additional source-specific authored contrasts change the protagonist to the
dead letter writer, remove the outside obligation's negation, distinguish a scene
containing entry from starting after entry, and distinguish unavailable Appendix B
from the visible receipt. Their expected support changes are inspected annotations;
the application does not infer them. A new legitimate source version would require
a new semantic assessment, even if its copy/binding checks passed.

## Actual assessment workload

| Family/order | Saved selected units | Distinct fields | Partial-field quotes | Exact authored-control matches |
| --- | ---: | ---: | ---: | ---: |
| H1 PC | 7 | 7 | 2 | 2 |
| H1 CP | 7 | 6 | 4 | 2 |
| H2 PC | 5 | 5 | 1 | 2 |
| H2 CP | 5 | 5 | 1 | 2 |
| F2 PC | 4 | 4 | 0 | 2 |
| F2 CP | 4 | 4 | 0 | 2 |
| F4 PC | 4 | 4 | 0 | 2 |
| F4 CP | 5 | 5 | 2 | 2 |
| **Total** | **41** | **40** | **10** | **16** |

The prior authored condition assesses **24 units**, versus **41** in the real
selected sets: seventeen additional units, about 71% more. All extras and the
one inspected overlapping SO premise remain; no semantic deduplication or
three-target substitution is used to make the proposed stage easier.

Only **16 field/quote pairs** exactly match the authored controls. Equivalent
occurrences and jointly covered targets are useful inspection evidence but do not
create more identical paired assessment units. Local selected-proposition gold
contains **31 supported / eight unsupported / two uncertain** units. Those labels
are authored and held outside the model input; they are not new model successes.

The local model-view data occupies approximately **51.2–52.8 kB** for historical
packets and **10.1–11.1 kB** for F2/F4. Full sources and citation indexes still
dominate. These are UTF-8 byte counts, not token predictions or frozen requests.
The existing response contract allows at most 1,200 characters per reason and
8,000 total; seven reasons do not acquire an 8,400-character allowance.

The already-completed SO stage used **eight calls / 63,000 input / 80,000 generated
tokens / 245.31 active seconds**. Its archived-rate reference is **$0.1149**, not
verified billing. A later stage must add its own calls, usage, failures and time
to these selection costs; selection is not free. No later assessment usage is
observed yet, and no end-to-end efficiency claim is established.

## Next bounded experiment: proposed VA/MA assessment comparison

**Proposal only: 16 new calls, not prepared, frozen or approved.** This is a
stage-specific comparison on saved model-selected units, not another selector
test or a fresh-scene generalization study.

| Condition | Assessment input | Proposed calls |
| --- | --- | ---: |
| VA | Eight unchanged frozen authored-span controls from the earlier SA/VA plan | 8 |
| MA | The same source/report/settings/assessment contract, replacing only the admitted span list with the corresponding saved SO selections | 8 |

Use H1/H2/F2/F4 in both original source orders. Balance condition order and pair
each MA selected set with its exact source case. **Do not rerun the selector** or
borrow the six retired SA calls. F2/F4 are now previously seen cases. The narrow
purpose is to determine whether the assessor handles the actual selected scope
and larger workload; fresh end-to-end generalization would remain a later question.

Keep each selected proposition as the assessment unit, with the complete field
and report visible. Full-field context does not silently widen the requested
judgment. The existing full-report message and field inventory can carry that
context while application-side records retain exact provenance. No inspected
semantic links, expected labels, group truth or gold witness sets enter requests.
At preparation, verify exact control wires and freeze the MA projection, all 41
unit judgments, all 24 control judgments, the sixteen exact paired units and
coverage limits before seeking approval.

Proposed scoring:

- Require **8/8 valid MA deliveries and 41/41 grounded selected-unit judgments**
  for assessment feasibility: exact proposition retained, correct support label,
  grounded reason and adequate cited evidence, without material unsupported
  explanations or opinion factualization. Every extra and duplicate receives
  inspection; output validity alone is insufficient.
- Score VA's **24 opportunities** separately and report the sixteen exact paired
  units with zero paired grounded losses as an additional comparison requirement.
  Invalid and unstarted cells remain in their fixed denominators. Do not count
  alternative occurrences as identical comparisons.
- Preserve the three contextual-completion group flags. Correct member labels
  still do **not** earn a complete relation/whole-claim judgment or authorize a
  repair. Report whether a whole relation was actually assessed, separately from
  selection coverage and component correctness.
- Report per-attempt generation, input, active latency and full staged cost with
  the eight historical SO calls included separately. Use complete pairs for
  comparative measures; impose no efficiency threshold on different-sized
  assessment sets and claim no end-to-end savings from this design.

Subject to a new metadata-only check at preparation, retain DeepSeek high thinking,
temperature 0.2, top-p 0.95, seed 20261022, context 40,000, non-streaming and no
format override. The last observed daemon was **0.40.13**; it was **not queried
in this local audit**. Proposed per-attempt caps remain **24,000 input / 16,000
combined generated tokens / 600 seconds**: new-call reservations **384,000 input /
256,000 generated / 9,600 seconds**, zero retries, repairs or replacements.
The archived-rate reference ceiling is **$0.42240**, with a $0.50 planning allowance,
neither a verified current tariff nor a billed-cost guarantee. Historical selection
usage remains separately reported rather than charged again as new inference.

Proposed stops retain the last comparison's explicit policy: a trustworthy
HTTP-200 length response retires the affected condition; non-200/transport,
unknown/conflicting usage, excess limits, metadata/thinking/timing failures,
tampering, ambiguous dispatch or cancellation stop the whole run. After each
condition's four H1/H2 cells, zero valid outputs or the same blocking signature
across both historical families retires that condition. No semantic early stop,
budget reallocation or resumption after a global terminal stop.

A favorable result would support designing further staged evaluation. It would
not establish autonomous admission completeness, whole-claim reasoning, writer
preservation or better fiction. The additional stage may increase total cost.

## Verification and handoff

The local scripts, source baseline, fixture manifest, structural/semantic audits,
negative controls and workload measurements are in
`data/diagnostics/reviewer-staged-handoff-audit-v61-2026-11-01/`.
The eight data-only handoffs and matching model views are exported to the separate
`data/diagnostics/reviewer-staged-handoff-export-v61-2026-11-01/` directory.
Verification passes **171 offline tests**: 41 new handoff tests, 46 existing
review-evidence tests and 84 prior delivery/usage audit tests. The new tests
exercise all 120 mutated packets. Ruff lint/format and strict mypy pass on all
five local scripts. The prior SA/SO result replay and the new deterministic audit
rebuild also pass. Real HTTP, sockets and database connections are blocked in
the new audit and tests; no daemon metadata was requested.

The export contains **eight packets and eight matching data views plus a
manifest** (533,168 payload bytes). An identical repeat verifies bytes without
rewriting them. Implementation/export hashes and preservation checks are recorded
in the local support/publication seals. Initial test corrections are retained in
the preparation notes: changing implementation during an export-repeat check
correctly invalidated its fingerprint, and the secret-guard fixture was corrected
to exercise structured credential detection before serialization. Neither changed
historical captures or production behavior.

```powershell
.venv/Scripts/python.exe -X utf8 data/diagnostics/reviewer-staged-handoff-audit-v61-2026-11-01/handoff_audit.py verify
```

Human review retains feel, flow, character and story-breaking judgments. Neither
faithful copying nor factual premise selection makes a story good, and a supported
requirement does not freeze all surrounding prose. CW-008/CW-013 and the other
issues remain open; no external issue was edited. **Step 19 IN PROGRESS; Step 20
NOT STARTED; production prompts unchanged; inference PAUSED; canary ON HOLD.**
