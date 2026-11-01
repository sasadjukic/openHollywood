# SA/VA delivery, citation and workload audit

Date: **2026-11-01**. **Local work COMPLETE and verified. Zero new model,
daemon or database calls.** Production **prompt 61 / graph 9 / fulfillment policy
1** unchanged. Inference **PAUSED**; full workflow canary **ON HOLD**.

The [SA/VA results](../benchmark_reports/reviewer-premise-admission-v61-results-2026-10-31.md)
remain **incomplete, no advancement**: six attempted calls, five completed
reports, one terminal length response and eighteen unstarted calls. This work
does not resume that plan or change its scores.

Three local findings guide the next proposal:

1. A rejected final answer can still have independently usable provider-reported
   token counters. Receipt validity, raw usage evidence and billing need separate
   statuses; none authorizes a retry.
2. H2's correct support label does not make its citations complete. An assignment
   obligation cannot replace evidence that the required event occurred.
3. SA's combined selection-and-assessment task used materially more generation
   than VA in the two completed pairs. That warrants isolating selection before
   designing a two-stage workflow, rather than increasing the output ceiling.

The separate local bundle is
`data/diagnostics/reviewer-admission-delivery-audit-v61-2026-11-01/`.
The local audit has a **zero-call budget**. The **16-call SA/SO proposal** below
is not frozen or approved, and no new model request payloads were created.

## Preserved fixtures and scope

The bundle copies **44 exact files** with original bytes and source hashes:

- **A-SA-H1-CP:** the empty-final raw response, request, wire request, reservation,
  model check and available version evidence.
- **A-SA-H2-CP / A-VA-H2-CP:** both complete citation-contrast captures, their
  requests, receipts, version evidence and cell seals.
- The original terminal record/seal, complete frozen cases, inspection notes
  and trial key needed to interpret those captures.

Every copy binds to the original source path and the prior publication closure
`af8638af08eb145722ff96ddbf301850c9c8077905586f38e9cd4ffc88a6d6ca`.
The audit verifies **609 historical/runtime source fingerprints**, including the
original 100-file freeze, live/inspection/analysis evidence, prior source graph
and results report. Mutable tracker updates are not misrepresented as immutable
historical run files. The original plan, captures, annotations and decisions are
unchanged. Synthetic mutations in tests are labeled authored controls, not model
outputs or repaired captures. No model thinking text was interpreted or scored.

This is diagnostic tooling in the ignored local data directory. No production
provider adapter, persistence schema, acceptance gate, writer route or UI changed;
no dependency or additional human checkpoint was added.

## Terminal usage reporting

The current production gateway builds a `ModelResponse` whose contract rejects
empty final content. On this capture that raises before the diagnostic runner's
normal evaluator/receipt and post-call version check. The terminal handler then
sets usage to unknown for any dispatched exception. That conservative handler
preserves the failure correctly, but does not distinguish absent counters from
present, independently checkable counters.

The exact regression reproduces the existing empty-content rejection locally.
The separate `terminal_usage.py` helper and offline export establish:

| Evidence layer | Recorded result |
| --- | --- |
| Delivery | HTTP 200; `done: true`; `done_reason: length`; empty final content |
| Raw reported counters | 14,256 input and 16,000 generated tokens |
| Normal receipt | Absent; never synthesized |
| Historical terminal usage | Unknown, preserved exactly |
| Reasoning/final token split | Unknown; not inferred from 75,181 thinking characters |
| Billing | Unknown; no zero charge or current tariff assumed |
| Reservation and continuation | Attempt consumed; no release, retry or resume |

The helper checks the original body hash, strict JSON including duplicate-key
rejection, HTTP status, model identity, completed finish envelope, message shape,
integer counters, cache-count consistency and any explicit usage breakdown.
Unknown, malformed, missing, negative, boolean, non-finite or conflicting counters
stay unknown. A non-200 body cannot donate apparent success counters. An explicit
valid zero is distinguishable from an absent value. A valid counter over a budget
limit remains visible with a separate over-limit flag; it is not hidden or changed
to zero. The helper observes counters, not response-schema or semantic validity.

Generated output is counted once. An explicit consistent reasoning split can be
reported when present; it is not added on top of total generation. Mixed known
and unknown attempts retain known subtotals, while whole-run totals remain null.
Duplicate attempt IDs are rejected. Actual cost stays null.

Replaying all six responses yields **87,926 reported input / 56,251 reported
generated tokens**, including the terminal response. The five valid receipts
remain **73,670 / 40,251**. The supplement preserves both views and the gateway
error chain; it does not rewrite the historical unknown usage or count the failed
attempt as a sixth completed report. These are integrity-bound provider reports,
not independently attested billable usage.

`admission_audit.py export-usage` writes this separate observation to a new local
directory, with source and implementation hashes and a completion manifest written
last. It refuses existing destinations, evidence directories and source changes
before/during publication. It has no live execution or recovery entry point.
The supported export was exercised locally and is available in the
[usage supplement](../../data/diagnostics/reviewer-admission-usage-export-v61-2026-11-01/usage-audit.json)
with its [manifest](../../data/diagnostics/reviewer-admission-usage-export-v61-2026-11-01/manifest.json).
Future runner integration requires its own frozen implementation and approval.

## H2 component coverage

The preserved claim contains an observed touch, a fixed psychic pull and their
sequence. The local authored witness map binds that exact claim to the exact H2
source packet:

| Reference | Source role and content | What it establishes for this claim |
| --- | --- | --- |
| S316 | Assignment: touch and psychic pull are required; no order imposed | The obligation, not occurrence or sequence |
| S336 | Draft paragraph 9: Elara grips the handle | Observed touch |
| S337 | Draft paragraph 10: fixed pull into the building's center | Observed directed pull; together with S336, sequence |
| S339 | Draft paragraph 12: the pull intensifies; magnetic description | Additional corroboration and description |

The VA report cites **S316/S336**. Its label is correct against the complete
source, but its evidence lacks the observed pull and therefore cannot establish
the complete event sequence. Its reason also locates both events in paragraph 9.
The SA report cites **S336/S337/S339** and distinguishes the paragraph locations.
The original **SA 6/6 and VA 8/9** grounded-target totals remain unchanged.

Authored controls check assignment-only, touch-only, pull-only, irrelevant entry
evidence and complete witness sets. Changed case content, a changed claim,
duplicate references, wrong namespaces and unknown references are rejected.
Adding the actual event witness fixes coverage in an **authored test**, not in the
historical model response.

This map is not a general semantic verifier or a universal citation whitelist.
Its event-to-passage correspondences were authored by source inspection; the
application only checks the declared correspondences and bindings. Other valid
witness sets require inspection. A correct label, a precise citation, and the
materiality of an explanation remain separate measures. This evidence gap does
not authorize a writer to change a story that already contains the event.

## SA workload audit

The four historical SA/VA request pairs differ only by VA's admitted-span message.
Full source text, source index, report, semantic contract, model and settings are
otherwise identical. No source or request was shortened during this audit.

| Packet | Total message-content UTF-8 bytes, SA | Serialized citation-index value | Source references |
| --- | ---: | ---: | ---: |
| H1 | 51,202 | 15,580 bytes | 312 |
| H2 | 53,914 | 17,054 bytes | 342 |
| Four never-run fresh families | 10,469–10,840 | 912–960 bytes | 13–14 |

Byte measurements are not token counts. H1/H2 have 285/313 story-context
references, alongside assignment and draft references. The historical source
packet is substantially larger than each fresh packet. That is a potential
workload factor, but it does not isolate the SA/VA difference: paired VA received
the same large source packet.

| Completed pair | SA returned rows | VA returned rows | SA/VA generated-token ratio | SA/VA active-time ratio |
| --- | ---: | ---: | ---: | ---: |
| H1, prose first | 8 | 3 | 2.53 | 2.18 |
| H2, context first | 4 | 3 | 2.81 | 2.66 |

The H1 SA output has **seven authored output groups across eight rows**: the
boundary comparison occurs twice. Its additional groups cover two obligations,
a compound achieved state, and the specific next-scene turning point. H2 has
four groups across four rows, including an additional next-scene allegation.
Both cover all three primary targets. These groupings describe observed output
units, not the number of atomic claims in the complete report. The extra rows are
not automatically wrong, and deduplication does not prove why the response became
long. SA's omitted final answer in the other H1 order reveals no final selections
to inspect.

The coupled task requires both deciding what matters and judging each selected
premise. VA supplies the first step and limits the assessed set. The observations
justify isolating that task boundary. They do not identify an internal reasoning
loop, establish that the index caused truncation, show a provider failure, or
prove that a two-stage pipeline would be cheaper. A second stage would add
another request and repeated context; those costs must eventually be measured.

## Proposed next experiment: 16-call SA/SO diagnostic

**Proposal only: separate preparation, freeze and approval are required.** This
is a new comparison, not permission to spend the stopped run's eighteen slots.
No prompts or requests have been changed or sent for it.

**Question:** can a selection-only call deliver faithful consequential-premise
selections within the same per-call budget, while reducing the generation needed
by the combined SA task? This is materially different from supplying an authored
answer set to VA. It tests model admission directly, without adding a second live
assessment stage yet.

| Condition | Task | Maximum calls |
| --- | --- | ---: |
| SA | Exact existing combined selection-and-assessment control | 8 |
| SO, selection only | Select exact field/quote pairs; return no support labels, citations or assessment reasons | 8 |

Use **four families × two source orders × two conditions = 16 attempts**:
unchanged H1/H2 historical cases plus **F2 attribution and F4 unavailable-source
scope**, both frozen previously but never sent to a model. They are fresh to
inference, not newly authored scenes. Both orders preserve the original
context/prose presentation contrast and balance condition order.

Keep all sources, reports, field inventories and citation indexes intact in both
conditions. SO changes only the task to admission and the corresponding response
contract: zero to twelve exact, uniquely bound field/quote pairs. It retains the
definition of consequential factual premises, supported criticism and qualified
literary opinion. It receives no target IDs, gold labels, expected evidence,
authored selections or materiality answers. Exact quotations do not themselves
establish semantic faithfulness. Production prompts remain unchanged.

At preparation, recheck current daemon/model metadata without inference. Subject
to that check, retain DeepSeek high thinking, temperature 0.2, top-p 0.95, seed
20261022, context 40,000, no format override and non-streaming. Retain **24,000
input / 16,000 total generated tokens / 600 active seconds per attempt**. The
maximum reservation is **384,000 input / 256,000 generated tokens / 9,600 active
seconds**, with zero retries, repair calls, replacements or reallocation. At the
old reference rates, that is $0.42240 with a provisional $0.50 planning allowance;
neither is a verified current tariff or billing cap. No fresh daemon discovery
was performed in this local pass.

Proposed scoring and advancement boundaries:

- Freeze three targets per family: **24 target opportunities per condition**,
  twelve in fresh families. Inspect every selected proposition, including extras,
  against its complete report field. Score quote binding, faithful admission,
  omissions, changed meanings, duplicate selections and inappropriate promotion
  of qualified literary opinions separately.
- Continue scoring SA's labels and evidence, but mark them **not requested** for
  SO. Do not give SO semantic-judgment or citation-quality credit it did not earn.
  Empty valid selections are omissions, not a retry opportunity.
- A selection-feasibility screen requires **8/8 valid SO deliveries and 24/24
  faithful target admissions**, with no material meaning distortion or false
  factualization of opinion. Extra valid premises are retained, not penalized for
  falling outside the authored target set.
- Report paired latency, total generated tokens and successful admission per
  attempted call, with all failures visible. A provisional resource screen is
  median paired SO/SA generated-token ratio at most **0.75**, without primary
  admission losses; report latency descriptively. Require all eight complete
  pairs for that comparative screen. If controls stop early, retain SO feasibility
  and observed delivery contrasts only; do not infer a complete cost benefit.
- Even a favorable result permits only designing a staged follow-up. It does not
  establish end-to-end cost, downstream judgment accuracy, writer preservation,
  whole-report admission completeness or story quality.

**Proposed stop-policy change, to be explicitly frozen before approval:** a
hash-bound HTTP-200 length response with trustworthy counters retires the affected
condition for its remaining cells. The other condition may finish its own fixed
schedule. The truncated attempt remains consumed and unusable. This avoids a
known control failure automatically preventing observation of the new task; it
does not authorize retries. Non-200/transport failure, uncertain or conflicting
usage, missing required thinking, invalid timing, metadata drift, tampering,
ambiguous dispatch, cancellation or excess resource use still stops the whole
comparison. Repeated blocking delivery errors
across the first two historical families, or zero valid outputs there, stop the
affected condition. No semantic early stopping. Unstarted cells stay in the
original denominators.

The current SA/VA run retains its original **global terminal stop**. Implementing
and testing this isolated-condition policy would be part of a separately
authorized preparation; neither the historical runner nor production behavior
has changed here.

## Verification and handoff

**199 offline tests pass in 54.53 seconds**, covering the new local regressions,
the frozen SA/VA harness and existing gateway/contract tests. Ruff lint/format
and strict mypy pass on all **six new scripts**. The tests cover the exact
gateway rejection, independent raw usage, unknown/malformed/conflicting counters,
duplicate JSON keys, non-200 lookalikes, over-limit visibility, no double counting,
H2 component bindings, unchanged historical scoring, terminal no-resume behavior,
export protection and source-change rejection. Tests block real HTTP; local audit
commands also block sockets and databases. The final verification and earlier
attempts are retained: import/format/type corrections and an authored zero-counter
fixture that initially retained an inconsistent positive cache count. The helper
correctly rejected that inconsistent fixture; no historical capture was altered.
The **609 source fingerprints**, existing **212-file Python baseline**, fourteen
issue bodies and posted links remain intact. No production/API/frontend code
changed, so unrelated application/build suites were not rerun.

Local commands from the repository root:

```powershell
.venv/Scripts/python.exe -X utf8 data/diagnostics/reviewer-admission-delivery-audit-v61-2026-11-01/admission_audit.py verify
```

To create another read-only usage supplement, choose a new destination:

```powershell
.venv/Scripts/python.exe -X utf8 data/diagnostics/reviewer-admission-delivery-audit-v61-2026-11-01/admission_audit.py export-usage --output data/diagnostics/reviewer-admission-usage-export-copy-2026-11-01
```

The [preserved fixtures](../../data/diagnostics/reviewer-admission-delivery-audit-v61-2026-11-01/fixtures-manifest.json),
[usage audit](../../data/diagnostics/reviewer-admission-delivery-audit-v61-2026-11-01/usage-audit.json),
[citation audit](../../data/diagnostics/reviewer-admission-delivery-audit-v61-2026-11-01/citation-audit.json)
and [workload audit](../../data/diagnostics/reviewer-admission-delivery-audit-v61-2026-11-01/workload-audit.json)
remain local. Human review retains feel, flow, character and story-breaking
judgments. The Blueprint checkpoint and prior human ties remain unchanged.
CW-008/CW-013 and all other issues remain open; no external issue was edited.
**Step 19 IN PROGRESS; Step 20 NOT STARTED; production prompts unchanged;
inference PAUSED; canary ON HOLD.**
