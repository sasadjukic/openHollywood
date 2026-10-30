# Diagnostic-probe adapter and twelve-capture export

Date: **2026-10-30**. **COMPLETE — tracked adapter and all twelve local exports.**
Production **prompt 61 / graph 9 / fulfillment policy 1** are unchanged.
Model, daemon and database calls for export: **zero**. Inference **PAUSED**,
full workflow canary **ON HOLD**.

## Delivered

The [audited adapter proposal](reviewer-probe-adapter-next-steps-2026-10-30.md) is
implemented under [ADR 0039](../adr/0039-diagnostic-probe-review-export.md):

- [Typed probe evidence](../../engine/open_hollywood_engine/evaluations/probe_review_evidence.py)
  keeps diagnostic identities separate from production creators, validates saved
  records and resolves native-selected spans through the unchanged v61 catalog.
- [File adapter and publication](../../apps/api/open_hollywood_api/services/probe_review_export.py)
  verify pinned archive seals, source/dependency chains and repeat exports.
- [Operator CLI](../../scripts/probe_review_export.py) accepts an explicit archive,
  one to twelve exact trial IDs and an output destination. It has no live mode.

The existing SQLite exporter, production prompts, graph, fulfillment handoff and
acceptance rules are unchanged. No public API, persistence schema, dependencies,
model settings or new human checkpoint were added.

## Export location and coverage

Open the local index:

```text
data/diagnostics/reviewer-probe-export-v61-2026-10-30/exports/index.md
```

The directory contains **26 files**: twelve Markdown/JSON pairs, `index.md` and
`manifest.json`, totaling **6,033,980 bytes**. The pairs use the exact trial IDs
from the [prior twelve-capture selection](reviewer-probe-provenance-audit-2026-10-30.md).
Six initial reviews and all six post-reviews remain selected; no replacements,
new samples or model calls were introduced.

| Export measure | Result |
| --- | ---: |
| Selected successful critic captures | 12 / 12 |
| Native checks, saved met / unmet | 24; 21 / 3 |
| Exact selected excerpt bindings | 55 / 55 |
| Selected excerpts identical to assignment wording | 0 / 55 |
| Application-added repair-advice records preserved | 3 |
| Raw reject → saved revise transformations preserved | 3 |
| Linked failed predecessor attempts | 2 |
| Post-review writer/parent dependency chains | 6 |
| Original draft bodies marked recovered after review | 6 |

All 55 text differences are literal comparison results, not defects or repair
instructions. The historical event/endpoint failure and ending-preservation
observations remain unchanged. The exports do not qualify those judgments or
create twelve genuine production reviews. Their origin is `diagnostic_probe`,
with synthetic unapproved context and null production creator/critique IDs.

Each Markdown file shows full raw model content, the saved normalized review and
the native audit separately, followed by application comparisons, source
visibility and failed-predecessor information. Each JSON file retains exact source
JSON text and byte hashes, including complete selected requests/responses and
dependency snapshots. Saved current catalogs, visible historical repair quotations
and old prose recovered locally remain distinct. The index supplies navigation;
this is not a new request for humans to count details or re-rate near-duplicates.

## Integrity and behavior

The registered contract pins the October 16 plan, preparation closure and live
closure. All **19 preparation evidence members, 252 live evidence members and
five operator evidence members** are verified. Selected request reservations,
role/content hashes, response hashes, receipts, source versions and native handles
must agree. The export preserves saved validation status; it does not execute
historical Python or repeat model validation under a later prompt implementation.

The earlier provenance audit already checked historical validator replay. This
adapter uses authenticated saved records and independent mechanical source checks.
It does not require old implementation files to remain the current checkout.
External historical report/source hashes remain in the retained plan/closures;
the adapter does not claim a fresh verification of every upstream external file.

The command re-reads authenticated sources before publication and recomputes its
derived comparisons. Missing, modified, unsupported or inconsistent records abort
the batch before output. There is no partial salvage, identity fabrication or
automatic repair. Source reads are bounded and archive-relative; no archive code
is executed. Credential detection aborts without silently modifying quotations.

The real CLI was run twice. The first run created the exports; the second returned
`reused`, verified every file byte and preserved all modification timestamps.
Changed/partial destinations and destinations inside either source archive are
rejected. A final manifest binds the exact trial order and all exported files.

## Verification

**83 focused tests pass: 37 new adapter tests plus 46 existing comparison-core
tests.** They use authored sealed fixtures with network and SQLite connections
disabled. Coverage includes met/unmet checks, duplicate occurrence offsets,
successful structural retry, writer/parent lineage, failed/missing captures,
wrong identities/hashes/handles/advice, caller-altered output, changed sources,
path traversal, selection limits, secrets, size bounds and publication conflicts.

Repository-wide Ruff lint/format and strict mypy pass on **212 Python files**.
The full Python unit/integration suite passes **1,197 tests in 368.97 seconds**,
including the focused tests; exact output is retained in `verification.json`
and the tracker. Frontend/build checks are not applicable to this Python-only
operator addition, which changes no API or generated client contract.

All twelve actual exports were inspected against the prior audit: raw content,
normalized review and audit digests, every native check, all 55 handles/quotes/
offsets, canonical source hashes and actual view hashes match. Every retained
snapshot file equals its original archived bytes. The manifest and repeat-export
checks also pass. These real-capture checks are separate from authored unit tests.

Preservation checks confirm **202 existing Python files**, **278 source archive
files**, **12 prior-audit artifacts**, all fourteen issue bodies and their posted
links unchanged. Earlier verification attempts remain recorded: the sandbox's
default temporary directory failed setup; a workspace test directory resolved
that. An authored fixture initially omitted the assignment `scene_id` and was
corrected without weakening the source check. Initial lint/type findings were
also corrected. Existing production behavior was not changed to pass the tests.

Private evidence is under `data/diagnostics/reviewer-probe-export-v61-2026-10-30/`:
the preserved baseline, export/inspection runner, `export-inspection.json`,
verification records, the `exports/` directory and publication closure.

## Next steps

The bounded mechanical-export work is complete. Retain these bundles as a stable
operator reference for the existing unresolved issues. No additional export
infrastructure, new human rescoring or live repeat is required for this sample.

The next useful decision is which **single unresolved semantic workflow issue**
to prioritize. Use the existing issue documents and completed experiment reports
to specify an unanswered question and a materially different intervention before
preparing another comparison. The known event/endpoint and ending examples alone
do not provide a new hypothesis; this implementation supplies no new model
reliability evidence. No live plan or call budget is proposed here.

Recommended priority is [CW-013: unsupported review explanations](../../issues/013-unsupported-review-explanations.md):
whether a material repair premise follows from the complete source, rather than
whether its quotation is bound correctly. This also matters to CW-006's writer
scope problem, but neither issue can be closed by these exports. The next bounded
design note should identify one unanswered production-source question, compare
it with the already completed provenance/entailment experiments, and state what
new result would change the workflow decision. If no materially different
hypothesis survives that comparison, keep inference paused. Only a justified
hypothesis should lead to another frozen comparison with controls, fresh scene
families, scoring, stops and a separately approved budget.

Keep mechanical checks available to support later human review of feel, flow,
character and story-breaking details. Exact identity, critic pass and fewer edits
remain distinct from literary quality. All fourteen issues stay open; no external
issue was edited. **Step 19 IN PROGRESS; Step 20 NOT STARTED.**
