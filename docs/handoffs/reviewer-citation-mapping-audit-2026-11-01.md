# VA/MA citation mapping and semantic-error audit — 2026-11-01

**Local work complete. No inference, daemon discovery or database access.**
Production prompt61 / graph9 / fulfillment policy1 remain unchanged. Inference
is **PAUSED**; the full workflow canary remains **ON HOLD**.

The [VA/MA results](../benchmark_reports/reviewer-selected-assessment-v61-results-2026-11-01.md)
show two distinct problems: correct assessments with inadequate citations, and
unsupported assessments that better citation placement cannot fix. The source
map itself is correct in every frozen request checked. A small presentation
experiment is justified as a citation-placement diagnostic, with semantic
failures retained as independent negative controls. It would not qualify the
reviewer or authorize story edits.

## Preserved evidence

The local bundle is
[`data/diagnostics/reviewer-citation-mapping-audit-v61-2026-11-01/`](../../data/diagnostics/reviewer-citation-mapping-audit-v61-2026-11-01/).
It preserves **269 exact capture/support files**, with source paths and SHA-256
fingerprints. Four failing MA reports are paired with their four VA controls:

| MA capture | VA control | Preserved failures |
| --- | --- | --- |
| M-MA-H1-PC | M-VA-H1-PC | Q006: unsupported private-flourish inference |
| M-MA-H1-CP | M-VA-H1-CP | Q002/Q003/Q005/Q006: citation gaps; Q007: unsupported private-flourish inference |
| M-MA-H2-PC | M-VA-H2-PC | Q001/Q002: citation gaps; Q005: unsupported starting-inside inference |
| M-MA-H2-CP | M-VA-H2-CP | Q004: citation gap; Q005: unsupported starting-inside inference |

The other eight F2/F4 captures remain positive controls. Raw responses, exact
requests, receipts, cell seals, source cases, selections, pair definitions and
sealed inspection notes are preserved. Thinking text remains in raw captures;
it was not used to adjudicate meaning. This is local assistant inspection, not
new blind human review.

`regressions.json` binds all **65 assessments** to their original notes:
**54 positive, seven citation-only failures and four semantic failures**.
The two failure categories are exclusive for this summary; a semantic failure
may additionally have misplaced evidence. Four exact-pair losses and all three
contextual-relation flags remain explicit. No historical label, citation, reason,
score, denominator or stop has been repaired.

The source chain verifies **1,467 fingerprints**, including the prior frozen
bundle, historical evidence and result closure. The existing **63 frozen files /
1,108 source pins** remain intact. The audit anchors the prior publication closure
`f4754e356778409c6595cc19b9ac03423f6fede7c2adcdd43187f2a9106aad45`
and plan `beeeeb915ca0d5a953e7e6c44b85f7174d9fec2fe48053d6a7c996d647c180b2`.

## The application map is correct in these captures

An independent scanner reconstructs nonempty paragraphs directly from the full
prose in the frozen wire messages. It checks source versions/roles, JSON field
pointers, exact text, Unicode code-point offsets, source/field hashes and the
wire's one-based paragraph numbers. The check also verifies that all source
fields remain available and report/scope content is unchanged.

| Family | Distinct source references | Draft paragraphs | Presentations checked |
| --- | ---: | ---: | ---: |
| H1 | 312 | 11 | 4 |
| H2 | 342 | 13 | 4 |
| F2 | 13 | 4 | 4 |
| F4 | 14 | 4 | 4 |

**681 distinct family references / 2,724 presented entries pass**, with zero
mapping discrepancies across sixteen requests. These are repeated mechanical
checks of four families, not 2,724 independent model observations.

Short paragraphs are real entries. H1's `Ten years. `, including its trailing
space, is paragraph 9/S308; the journal comparison is paragraph 10/S309. H2's
handle contact is paragraph 9/S336; preparation is paragraph 12/S339; actual
entry is paragraph 13/S340. Neither short paragraphs nor Unicode characters were
dropped or shifted by the application. All returned reference IDs are valid IDs.

The model sometimes gives an incorrect paragraph number in its explanation:
H1/CP Q003 calls the comparison paragraph 9; H2/PC Q002 calls handle contact
paragraph 10. The errors go in different directions, and other gaps omit
components. A single global off-by-one correction would be unjustified.

## Citation placement versus evidence coverage

The following witnesses illustrate the missing evidence; they are **not an exact
citation whitelist**. Another sufficient set could pass the original inspection.

| Correct-label failure | Returned citations | Missing evidence | Classification |
| --- | --- | --- | --- |
| H1/CP Q002: decision-making process | S308 | S309: purposeful journal comparison | Adjacent paragraph |
| H1/CP Q003: definitive match | S308 | S309: observed match | Adjacent paragraph |
| H1/CP Q005: dates and realization | S299/S305/S306/S307 | S308: observed `Ten years.` realization | Missing component |
| H1/CP Q006: current-scene resolution | S308 | S309: comparison and match | Adjacent paragraph |
| H2/CP Q004: crossed sill | S339 | S340: actual entry | Adjacent paragraph |
| H2/PC Q001: decision through reasoning/preparation | S340 | S339: selected reasoning and preparation | Adjacent paragraph |
| H2/PC Q002: contact and fixed pull | S337/S338/S340 | S336: handle contact | Missing component |

Five gaps select an adjacent paragraph; two omit a required component. Citing
an assignment does not establish its occurrence. Entry alone does not establish
the selected explanation of *how* the decision was expressed. H1's observed
realization is a frozen component requirement, not a newly tightened scoring rule.

Four of these are losses on exactly matching VA/MA units: H1/CP Q002 and Q005,
H2/PC Q001 and Q002. The successful VA controls remain paired. The MA workload
changes both selection count and composition; one attempt per cell cannot isolate
workload from sampling variation.

The negative controls prevent over-penalizing citations. H2/CP Q001 has sufficient
evidence for its selected decision claim in S339 even though its incidental later
boundary-violation assertion lacks complete evidence. H2/CP Q002 cites contact
and pull adequately. An extra irrelevant citation alone is not a failure.

## Exact-excerpt lookup: useful location evidence, limited authority

The local prototype accepts an explicit immutable source version, field pointer
and exact excerpt. It returns a reference and code-point range only for a unique
occurrence in one registry unit. It reports missing or ambiguous text and refuses
unknown scope, empty excerpts and automatic cross-paragraph binding. It does not
normalize punctuation, whitespace or Unicode, search the report as story truth,
pick the first duplicate occurrence, or issue writer instructions.

Seven authored probes locate the seven missing witnesses. **Six excerpts are
already literal substrings of the model's reason; one, H1/CP Q006, was selected by
the auditor from the source.** This demonstrates local locatability, not automatic
evidence selection or seven model recoveries. In particular, finding one missing
component does not prove that a compound claim now has complete coverage.

Every lookup retains `source_support: unassessed`. Valid quotations about another
actor or an assignment remain merely located text. Tests cover duplicate and
overlapping occurrences, wrong versions/fields, changed negation, curly versus
straight apostrophes, composed versus decomposed Unicode, trailing spaces and
cross-paragraph quotations. The original assessment record remains untouched.

Requiring the model to copy full quotes again is not the recommended next step.
The [earlier V2/C1 comparison](../benchmark_reports/reviewer-gemma-deepseek-v61-results-2026-10-20.md)
already exposed delivery tradeoffs when models supplied versions and quotations.
The present lookup is an offline audit instrument, not a production repair path.

## Semantic failures remain after location is separated

**General match versus specific verification:** H1/PC Q006 cites the correct
S215 planned private flourish and S309 observed general handwriting match. Its
conclusion that the specific next-scene verification has been consumed is still
unsupported under the frozen claim contract. H1/CP Q007 repeats this inference
and additionally misplaces the match citation. Fixing its S308 reference would
not establish the missing specific event. The separate current-scene no-match
boundary criticism remains valid. A reader could still judge the beats redundant
as a literary opinion; that is a different claim from factual fulfillment.

**Location versus entry timing:** both H2 Q005 assessments cite interior location,
cautious/frightened entry affect and the valid current-scene outside obligation.
These do not establish that the next scene starts *after* entry has already
happened. The complete next-scene summary, S228, explicitly includes entering.
The real current-scene boundary violation does not validate this extra temporal
premise. Citation repair cannot supply the missing entailment.

The contextual outcomes also remain separate: H1/CP never explicitly assesses
the complete endpoint relation; H2/CP asserts a boundary violation without its
complete evidence; F4/CP grounds the relation explicitly. Supported member labels
do not automatically earn whole-relation credit.

## Verification

**161 offline tests pass:** 74 new mapping/lookup/regression tests, 46 existing
review-evidence tests and 41 prior handoff tests. Ruff lint/format and strict mypy
pass on five audit scripts. Historical ledger, frozen wires, sealed inspection
and scores replay unchanged: VA **24/24 grounded**, MA **37/41 correct labels /
30/41 grounded**, four paired losses, both original gates failed.

The first verification recorded two lint findings; adding explicit strict zip
length checking and wrapping one string resolved them. Tests and typing already
passed on that attempt. Both verification records are retained. Fixture export
is idempotent, preserving bytes and modification times. HTTP, sockets/DNS and
SQLite are blocked in the audit/tests. No metadata or model endpoint was called.

To reproduce from the repository root in PowerShell:

```powershell
$env:PYTHONPATH = 'engine;apps/api;apps/worker'
.venv/Scripts/python.exe -X utf8 data/diagnostics/reviewer-citation-mapping-audit-v61-2026-11-01/mapping_audit.py verify
```

`verification-attempt-002.json` records the exact lint, typing, pytest and historical
replay commands. `fixtures-manifest.json`, `sources.json`, `regressions.json` and
`mapping-audit.json` retain provenance and detailed observations. The publication
closure binds the final local evidence and this report. Fourteen original issue
bodies and posted URLs are preserved; no external issue is edited or closed.

## Proposed next step: isolate paragraph-reference presentation

**Provisional MA/PE comparison, sixteen calls; not frozen or approved.** The
testable hypothesis is narrow: displaying the exact paragraph beside its reference
can reduce the observed location errors without changing assessment scope. There
is no evidence yet that it will improve results or cure either semantic pattern.

| Arm | Proposed diagnostic difference |
| --- | --- |
| MA control | Existing full-context selected-premise assessment, unchanged |
| PE: paragraph excerpts | Add the application-resolved exact paragraph text to every `/prose` entry in the existing source registry; retain all complete sources, context fields, selected claims and the same response contract |

This eliminates the prose paragraph-counting indirection while retaining short
reference output. It adds no relevance labels, selected gold witnesses, semantic
hints, scope reduction or model-authored quote requirement. All prose paragraphs
receive the same treatment. The larger, duplicated input is part of this
presentation intervention and must be measured; it is not a pure token-neutral
test. Earlier route indexes and namespace registries did not establish entailment;
this proposal targets the newly documented paragraph-placement failures only.

Use H1/H2 as historical sentinels plus **two fresh long-context scene families**,
each with both prose/context presentation orders: four families × two orders ×
two arms = **16 calls**, zero retries or repair calls. Historical MA controls must
match their frozen wires exactly. Fresh cases should include adjacent preparation
and action, a short standalone realization, split evidence, attribution/negation,
and positive/negative versions of the two semantic contrasts. Keep claim counts,
selection scope and workload identical within each arm pair; preserve full fields.
F2/F4 remain local positive regressions, not substitutes for fresh cases.

Before inference, prepare and verify the renderer locally, freeze cases, exact
requests, per-claim judgments, adequate-evidence criteria, budget and stops, and
submit the plan for separate approval. Suggested limits retain 24,000 input /
16,000 combined generated tokens / 600 active seconds per call, with high thinking
and the existing sampling settings. These are proposed limits, not reservations
or a new approved ceiling. Check current metadata only during an authorized
preparation/preflight; do not silently inherit a changed daemon/model baseline.

Score structural delivery, label accuracy, substantive reason accuracy, citation
coverage and explicit relation support separately. Missing/invalid outputs retain
their fixed denominators. A useful screening result should produce at least two
paired citation recoveries among the seven historical failure targets: the new MA
control still fails that unit's citations while PE grounds it. Recovery in both
arms is not treatment evidence. Require valid delivery, no loss of a grounded
paired unit and no new semantic error, including on the fresh families. If controls
no longer reproduce enough failures, report the contrast as inconclusive. Freeze
the exact promotion rule before calls. Even a favorable result
would qualify only further citation-presentation evaluation. Continued semantic
failures would still block autonomous reviewer-to-writer routing.

Preserve the usual zero-retry terminal policy for non-200/transport/unknown usage,
metadata drift, cancellation, tampering and budget violations. Freeze any
delivery sentinel retirement before dispatch; no output-dependent replacements.
If the local renderer cannot preserve every source binding within the input limit,
do not run. If the comparison adds no citation recovery, do not keep expanding
the same prompt intervention without a different supported hypothesis.

Human review stays focused on feel, flow, character and story-breaking details.
Neither mechanically correct citations nor factual critique support establishes
edit necessity, preservation or story quality. No writer, production prompt,
canonical prose, graph, persistence or mandatory Blueprint checkpoint changed.
CW-007/CW-013 remain open; this audit does not close CW-008 or qualify CW-014.
**Step 19 IN PROGRESS; Step 20 NOT STARTED; inference PAUSED; canary ON HOLD.**
