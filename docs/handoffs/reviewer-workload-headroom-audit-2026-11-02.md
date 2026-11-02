# Quote-witness regressions, delivery headroom and assessment workload

Date: **2026-11-02**. **LOCAL AUDIT COMPLETE AND VERIFIED.** No model, daemon or
database calls. Production **prompt 61 / graph 9 / fulfillment policy 1** is
unchanged; live calls are **PAUSED**, the full workflow canary **ON HOLD**.

The new captures are preserved without changing the
[MA/quote-witness results](../benchmark_reports/reviewer-quote-witness-v61-results-2026-11-02.md).
The audit supports testing a smaller assessment workload while retaining complete
context. It does not establish that this will fix delivery or semantic errors.
Repeating the context increases the number of calls and may increase total cost.

For the broader investigation and recommended production direction, see the
[evidence synthesis](critic-writer-evidence-and-production-direction-2026-11-02.md).

## Preserved evidence and regression expectations

Private bundle:
`data/diagnostics/reviewer-workload-headroom-audit-v61-2026-11-02/`.
It preserves **163 byte-identical capture/support files**, checks **2,966 historical
source fingerprints**, and retains all four attempted cells, the complete source
contexts, prepared and dispatched requests, raw responses, receipts, inspection
notes, scores, usage, stops and publication evidence. Copied Python files are
inert historical evidence; the new reader does not import them.

The original plan hash is
`9dcc2a77932fb5b6888c422d9a0f869b7801f4305b731c27fda1cf0df48a8f0e`;
the prior publication-closure hash is
`8582fc51e8b19827e618c5f53e249a6989bf6ceac3b8b6812172795ae48a682d`.
The original 69-file / 2,800-source freeze remains unchanged.

| Regression | Preserved expectation |
| --- | --- |
| Fourth call, `Q-MA-H2-CP-R1` | HTTP 200, length finish, 16,000 combined generated tokens; final JSON ends inside a reason string. No semantic score, no repaired JSON, no retry or released reservation. |
| H1/PC Q007 date realization | MA's explanation describes the dates and realization but omits the realization's source from its references. WB binds the needed witnesses: one distinct paired citation recovery. |
| H1/PC Q006 private flourish | Both arms make the unsupported factual inference despite correctly locating the relevant source passages. Binding success does not repair entailment. |
| WB H2/CP Q005 next-scene opening | Planned darkness and an interior location do not establish that the scene starts inside when its summary places entry during the scene. MA is unavailable, so this is not a paired treatment loss. |
| Successful WB witnesses | All 23 exact witnesses locate; all twelve WB assessments are mechanically bound. These successes remain separate from semantic correctness. |
| Successful judgments and fixed denominators | All fifteen grounded judgments remain positive fixtures, alongside one citation-only and three semantic failures. All 141 unavailable slots remain unavailable. |

The frozen decision remains **`incomplete_delivery`**: four calls used, twenty
unstarted calls retired, three valid reports and nineteen inspected judgments.
Only seven judgments have valid paired results. No fresh or repeated block ran.
The retired calls are not a continuation allowance.

The private-flourish fixture preserves the historical factual-scope score. A
reader could separately find that a general handwriting match reduces suspense
around a later specific test. That editorial assessment is not the assertion that
the specific test already occurred or its factual obligation was fulfilled.
Neither the local audit nor a wording clarification retroactively changes gold.

## Delivery headroom

The audit reads the twelve controls from the
[baseline repeatability run](../benchmark_reports/reviewer-baseline-repeatability-v61-results-2026-11-02.md)
and the four new deliveries. Each MA group below has an identical complete wire
request across its observations. These are sixteen saved deliveries, not sixteen
new calls or an independent estimate of a population failure rate.

| MA wire | Earlier generated-token totals | Latest total | Latest remaining output allowance |
| --- | --- | ---: | ---: |
| H1/PC | 13,629; 6,694; 11,457 | 5,834 | 10,166 |
| H1/CP | 8,646; 6,418; 6,814 | Not attempted | Not applicable |
| H2/PC | 10,376; 7,259; 7,656 | Not attempted | Not applicable |
| H2/CP | 9,535; 8,885; 15,094 | **16,000, length stop** | **0** |

The two new WB responses used 10,012 and **15,816** generated tokens, leaving
5,988 and **184** respectively. The latter completed validly with very little
remaining allowance. It does not establish that WB caused the subsequent MA stop.

All observed counters remain known as recorded. They count combined reasoning
and final generation; the separate token counts are **unknown**. Final character
counts cannot supply that split. The four latest calls used approximately
14,500–17,800 input tokens, within the 24,000-token reservation. That fact does
not prove an internal context-window or generation mechanism. The latest MA
input counters differ by one token from earlier identical wires; the difference
is preserved without inventing an explanation.

The evidence establishes variation and inadequate headroom in particular
deliveries. It does **not** establish provider fault, an input truncation, a causal
effect of the number of claims, or that raising the cap would yield a valid answer.
Larger limits were not applied. No per-claim reasoning cost can be recovered from
these aggregate counters.

## A narrower workload with complete context

The local prototype is a **data-only design preview**, not a provider request or
production adapter. It keeps the entire original wire as inert context, including
all source artifacts, their versions, the full report, source registry and all
original admitted spans. A separate active set identifies the whole propositions
that a hypothetical assessment batch would judge. It creates no new prompts,
response schemas, transport, approval file or live budget.

The checks cover every one of the 24 frozen requests at two proposed workload
limits. They preserve every selected proposition exactly once and retain the
existing authored relation links. In particular, H1/CP Q003–Q004 and H2/CP
Q003–Q004 remain together. The two components cannot be put in separate calls and
then treated as proof of their relation. Compound selected statements are never
split into easier subclaims.

These links come from the existing diagnostic inspection. The application has
**not** learned to discover semantic dependencies in arbitrary production reviews.
A linked group larger than a proposed limit is rejected; the prototype does not
silently sever it or trim its context. Unknown, duplicate, missing, empty and
oversized selections are also rejected.

| Projection of the entire old schedule | Calls needed | Selected judgments | Context policy |
| --- | ---: | ---: | --- |
| Original MA/WB schedule | 24 | 160 | Original full context |
| At most three whole units per call | 64 | 160 | Full original context repeated in every batch |
| At most two whole units per call | 88 | 160 | Full original context repeated in every batch |

These are arithmetic projections, not live plans. They show why one-claim-at-a-time
or ever-smaller batches cannot be presumed efficient. The number of judgments
stays fixed while full-context deliveries multiply.

The prototype also checks a completion boundary: each expected batch must arrive
exactly once, with the same immutable scope and a valid delivery. Missing, duplicate,
unknown, invalid or mixed-scope batches cannot produce a complete case. Even
complete delivery grants **no semantic, whole-relation or writer authorization**.
It is not an automatic merger of model judgments.

## Verification

**251 unique offline tests pass**:

- 85 new tests for captured successes/failures, headroom, all 48 workload
  projections, whole-group preservation, context tampering, incomplete delivery,
  exact copying and offline boundaries.
- 46 existing read-only evidence-rendering checks.
- 98 unchanged quote-witness comparison checks and 22 gateway/contract checks.

Only the historical preparation-only assertion that no approval exists is
deselected: execution already has an approved record. Ruff lint, Ruff formatting
and strict mypy pass for the five new scripts. Historical score replay and
deterministic audit replay pass. HTTP/socket/DNS and SQLite access are blocked in
the relevant offline audit/test paths; mocked responses do not make provider calls.

The first combined verification attempt incorrectly discovered preserved Python
captures as runnable modules/tests. It failed on duplicate module identity and
test collection. The verifier now explicitly selects the five current scripts and
the current test file; copied evidence remains inert and byte-identical. Both
verification records are retained. An earlier preparation path typo was corrected
before successful artifact generation. These were local harness defects, not
additional model failures or repairs to historical evidence.

Replay from the repository root:

```powershell
$env:PYTHONPATH='engine;apps/api;apps/worker'
.venv/Scripts/python.exe -X utf8 data/diagnostics/reviewer-workload-headroom-audit-v61-2026-11-02/workload_audit.py verify
```

For a fresh full verification, supply two unused local output paths:

```powershell
.venv/Scripts/python.exe -X utf8 data/diagnostics/reviewer-workload-headroom-audit-v61-2026-11-02/verify_local.py data/diagnostics/reviewer-workload-headroom-audit-v61-2026-11-02/verification-next.json data/diagnostics/workload-check-next
```

The recorded successful run is `verification-attempt-002.json`. No product code,
client UI or API contract changed; frontend/build checks were therefore not part
of this local Python and documentation change. Source fingerprints, exact-copy
fixtures, original issue bodies and posted URLs are preserved.

## Recommended next work and optional experiment

First, turn the already tested staged-handoff and workload-completion prototypes
into a small **tracked, read-only assessment work-item contract**, reusing existing
evidence/export primitives. This is proposed work, not implemented here. The
[production recommendation](critic-writer-evidence-and-production-direction-2026-11-02.md)
specifies the boundaries and acceptance criteria. It should make incomplete
assessment, missing source coverage and unsupported inference visible without
turning any of them into a new story defect or an instruction to the writer.

If another live comparison is then warranted, propose **30 calls**:

- Four families, both presentation orders: the two historical families and the
  two still-unrun fresh families from the quote-witness plan.
- **Eight unchanged full-workload MA controls** versus **22 MA batch calls**, at
  most three whole selected units per call with linked units kept together.
- **56 judgments per condition**, 112 fixed slots overall. MA's evidence-output
  interface and thinking/settings stay matched; do not simultaneously add WB.
- Retain full sources, full report and all selected assertions in every request.
  Change only which whole assertions receive an assessment in that batch.
- Judge delivery and grounded coverage at the **complete-case** level. Report
  all batch input/output/latency together; a cheap individual response is not a
  cheap complete review. Keep citation, semantics and contextual-relation scores
  separate; partial successes cannot rescue an incomplete case.
- Interleave fresh and historical cases from the start, preserve positive controls,
  and retain a hard first-delivery-failure stop with no automatic retries. Freeze
  the exact schedule, payloads, resource reservations, scoring and stops separately.

The hypothesis is that limiting simultaneous assessment work improves completed
delivery without losing grounded judgments. It is **not** that fewer claims imply
less total cost or automatically cure the private-flourish/plan-scope failures.
Eight paired case/order observations would be a feasibility diagnostic, not a
repeatability or population-reliability qualification.

**No requests or 30-call budget are frozen or approved.** No original retired
allowance is reused. All fourteen issues remain open; no GitHub issue was changed.
Step 19 remains **IN PROGRESS** and Step 20 **NOT STARTED**.
