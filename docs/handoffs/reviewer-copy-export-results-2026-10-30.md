# Read-only review export: implementation and saved-record inventory

Date: **2026-10-30**. The tracked operator export is implemented. Compatible
saved-review inspection has **zero coverage** in the inventoried databases.
Production **prompt 61 / graph 9 / fulfillment policy 1** are unchanged. Live
calls and daemon calls: **zero**. Inference **PAUSED**, canary **ON HOLD**.

The [local integration design](reviewer-copy-integration-design-2026-10-30.md)
is now a tracked, typed operator command under [ADR 0038](../adr/0038-read-only-review-evidence-export.md).
It can prepare mechanical evidence from a supported saved review without changing
that review or any manuscript. The local tests establish application behavior;
no new model reliability or story-quality conclusion follows from this work.

## Implemented surface

```powershell
uv run --extra api python scripts/review_evidence_export.py inventory --database data/open_hollywood.db
uv run --extra api python scripts/review_evidence_export.py export `
  --database data/open_hollywood.db `
  --invocation-id "REPLACE_WITH_EXACT_INVOCATION_UUID" `
  --output data/diagnostics/saved-review-evidence
```

Replace the placeholder with an exact ID. Repeat `--invocation-id` for up to
twelve distinct reviews. The command has no inference mode. Inventory exposes
metadata candidates only; export validates complete provenance in one SQLite
read transaction. An unsupported invocation may be explicitly exported as a
non-result while retaining its safe, verified original critique.

The implementation separates:

- [Typed domain records and comparison](../../engine/open_hollywood_engine/evaluations/review_evidence.py):
  exact field/handle/offset identity, pinned v61 catalog replay, message recovery,
  source validation, and literal comparisons independent of met/unmet judgments.
- [Read-only SQLite adapter and bundle publication](../../apps/api/open_hollywood_api/services/review_evidence_export.py):
  creator/target/run validation, consistent source reads, explicit non-results,
  credential guards and conflict-safe repeat export.
- [Operator command](../../scripts/review_evidence_export.py): explicit database,
  exact invocation selection and new output destination, with bounded errors.

No production executor, prompt, graph, fulfillment handoff, database schema,
API/client contract or acceptance rule changed. No new dependencies, model
settings, UI controls or human checkpoints were introduced.

Each completed export contains `review-evidence.json`, `review-evidence.md` and
`manifest.json`. It preserves complete safe original critique/native-audit data
and displays separate application comparisons for every native-selected excerpt.
The JSON also retains exact canonical sources and the recovered saved request.
These local exports contain story material and are not public issue attachments
by default.

Source versions, canonical/field/view/catalog hashes, the assignment-contract
hash, source/target labels, offsets, quotations and visibility remain available.
View hashes preserve actual field presence rather than adding default fields.
The local replayer hash identifies this comparison implementation; it does not
attest to which binary produced a historical request.

An exact comparison is allowed alongside an unmet saved check, and different
wording alongside a met check. Multiple excerpts remain separate; there is no
aggregate equality or inferred fulfillment. Original/revision semantic mapping
is explicitly unresolved. Source mismatches prevent comparisons, and a missing
display never becomes a manuscript finding or automatic writer instruction.

## Bounded inventory and inspection outcome

The discovery scope was the project's `data/` tree, including the configured
default database `data/open_hollywood.db`. It found **1,386 SQLite files** before
this task's new test databases were created. **1,332 test-named paths** were
excluded using `pytest`, underscore-prefixed directory and `test_` path markers.
All remaining **54 database candidates** were inventoried successfully.

This is a bounded workspace inventory, not a claim about every database on the
computer. Multiple campaign/completed snapshots remain separate database records;
they are not counted as independent reviewer observations.

| Inventory measure | Result |
| --- | ---: |
| Databases inspected for metadata | 54 |
| Ordinary-critic invocation rows, including duplicate database snapshots | 1,712 |
| Distinct ordinary-critic invocation IDs | 1,254 |
| Distinct successful / failed / running invocations | 1,197 / 56 / 1 |
| Highest observed prompt version | 33 |
| Invocations with the required schema-7 native audit | 0 |
| v61/schema-7 metadata candidates | 0 |
| Compatible saved reviews selected / inspected | **0 / 0**, maximum 12 |

The default database's CLI inventory independently reports **147 metadata rows**
and zero candidates. No inference was used to fill the gap, no older review was
retagged, no failed record was salvaged and no fixture was counted as an inspected
production review. No user review bundle was manufactured from incompatible
sources. The selected invocation list is explicitly empty.

The distinction matters: the tool is locally qualified, while inspection of
genuine compatible SQLite reviews remains unavailable. This inventory supplies
no evidence of improved or worsened semantic selection, preservation or story
quality. The successful SQLite exports in the test suite use fake gateways and
remain clearly identified as application tests.

Private evidence is in `data/diagnostics/reviewer-copy-export-v61-2026-10-30/`:
`inventory.json`, `inventory-summary.json`, `inventory-cli-default.json`,
`inspection-selection.json`, verification records and the closure manifest.
Main database bytes matched before and after each metadata inventory. The reader
uses SQLite read-only/query-only modes, never migrations or application startup.

## Verification

The **63 focused tests pass**. They cover the twelve source/status cases,
unchanged-production catalog parity, Unicode/whitespace exactness, duplicate
occurrences, multiple excerpts, unavailable/recovered historical sources,
conflicting bindings, actual rendered-view hashes, exact message recovery,
native-check preservation and JSON replay.

Real migrated SQLite/fake-gateway tests additionally cover source creator and
successful-retry identity, unsupported frozen-run contracts, missing inputs,
read-only enforcement even if query-only is disabled, a stable read snapshot
during another connection's commit, special-character paths, repeat export,
changed/partial-output rejection, guarded errors and credential rejection before
destination creation. Supplied comparison text is recomputed before publication.

The first focused run had **60 passes and one fixture setup failure**: removing
an input through an ORM relationship correctly triggered existing artifact
immutability protection. The corruption fixture now removes only a link in its
disposable test database through explicit SQL. The production immutability guard
was preserved. Subsequent tests include the frozen-run and view-hash regressions.

Repository-wide Python Ruff lint/format and strict mypy pass on **207 files**.
The full Python unit/integration suite passes: **1,160 tests in 324.19 seconds**,
including the focused tests above. Exact command output is retained in the private
verification record. Windows asynchronous fixtures run outside the
sandbox's loopback restriction, using fake gateways. No live model or daemon
check is part of verification. Frontend/build commands are not applicable to
this Python-only operator feature; there is no API or generated-client change.

## Decisions and next steps

Retain the tracked exporter for compatible future records or another explicitly
identified existing database. Do not expand old-contract support merely to make
the sample count nonzero: these inventoried rows do not contain the native
assignment checks the comparison requires. A compatibility shim cannot recover
judgments that were never saved.

There is an existing evidence path worth auditing locally. The
[October 16 ordinary-critic report](../benchmark_reports/production-fulfillment-v61-results-2026-10-16.md)
records **seventeen validated ordinary-v61 reviews**, with exact requests and
responses in a separate probe bundle. Those captures are not persisted ordinary
production invocation records. Their provenance must remain explicitly labeled
as diagnostic probe evidence.

The [next-step proposal](reviewer-copy-export-next-steps-2026-10-30.md) is a bounded
zero-inference provenance audit of up to twelve of those saved successful critic
captures before deciding whether a separate adapter is justified. It does not
authorize creating production records, replaying a model, modifying prompts or
starting the canary. Another PO/EX repeat remains unjustified by this work.

All fourteen issue bodies and posted links remain intact; no issue is closed.
Human feel, flow, character and story-breaking review remains the story-quality
authority. **Step 19 IN PROGRESS; Step 20 NOT STARTED.**
