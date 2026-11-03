# Tracked assessment work: local integration and provider preparation

Date: **2026-11-02**. Scope: implement the small read-only component recommended in
the [investigation synthesis](critic-writer-evidence-and-production-direction-2026-11-02.md),
then prepare the workload comparison for both Ollama/DeepSeek and OpenAI/Luna.
No new inference, production prompt change or canary execution.

## Implemented component

[ADR 0041](../adr/0041-read-only-assessment-work.md) records the decision.
The tracked [assessment-work module](../../engine/open_hollywood_engine/evaluations/assessment_work.py)
extends the tested local staged-handoff/workload behavior into provider-neutral
typed records. It preserves full context, whole statements, declared dependencies,
request-bound receipts, exact-once completion and known/unknown usage accounting.
The [tracked tests](../../tests/evaluations/test_assessment_work.py) contain authored
synthetic fixtures; they do not require private unpublished captures.

The component cannot infer whole-claim truth, materiality or edit necessity from
successful delivery or citation binding. Its public result retains support,
necessity and craft as unassessed and writer authorization as false. Invalid or
missing batches cannot produce a complete case. Literal rendering recomputes the
typed boundary and preserves the entire context without executing embedded markup.

This is a usable read-only engine boundary, exercised by the new private harness.
It is not a production critic route, automatic claim extractor or new generic
exporter. The existing ordinary-review and diagnostic-probe exporters retain their
separate provenance contracts. There is no public API, persistence schema, client,
dependency, profile or mandatory-checkpoint change.

## Provider readiness and runtime baseline

The user explicitly approved reusing the application's Windows User
`OPENAI_OH_KEY` for preparation and non-generating checks. It was imported into the
metadata process's memory only; no key or credential file was created or changed.
The general `OPENAI_API_KEY` is not an application inference fallback.

Metadata-only preflight confirms **Ollama 0.40.13** and the same selected DeepSeek
metadata, plus account-visible **`gpt-5.6-luna`** through the existing OpenAI adapter.
The checks sent no story payload, token-count request or generation. Model listing
does not certify a successful forthcoming generation. The prior provider-addition
smoke test remains historical evidence, not an extra call in this preparation.

The user committed OpenAI support between sessions as `a6cdc0b`, following the
previous audit commit `da09633`. Sixteen tracked runtime/test files differ from
the old source pins. The preparation verifies both historical and current Git
blobs and records `runtime-baseline-amendment.json`; it does not pretend that the
old runtime is still installed or edit old fingerprints. No historical diagnostic
capture, case, request, annotation or score changed. The new source baseline checks
**3,146 fingerprints** before adding current engine/runtime pins to the freeze.

The first sandboxed metadata process did not return and was interrupted. The
metadata-only check then completed outside the Windows sandbox. No generation
endpoint exists in that script. The repository already documents the Windows
event-loop/socket-pair limitation; no provider outage is inferred from it.

## Preparation fixes caught locally

The first draft inherited `response_schema: null` from the historical Ollama
request. That historical route carries its schema in prompt text, because its
cloud adapter does not enforce a native schema. A dedicated mock assertion caught
the missing OpenAI `text.format` before any live request. The new harness now
derives the identical canonical contract from the saved response-contract message
and supplies it to the existing OpenAI schema adapter. DeepSeek's control wires
stay exact. The initial unapproved derived files are retained under
`preparation-attempt-001/`; they are excluded from the final executable freeze.

Other preparation corrections concerned exception expectations in negative
tests, formatting/type annotations, terminal metadata retention and the explicit
runtime amendment. They do not constitute live model failures or improvements.

## Verification and evidence

The private bundle is
`data/diagnostics/reviewer-assessment-workload-v61-2026-11-02/`.
It contains source pins, the baseline amendment, metadata, sixteen work records,
sixty exact requests, two schedules/budgets/stop policies, frozen gold and adequate
evidence criteria, literal work renderings, runner, tests and verification records.

The local checks cover **38 tracked component tests and 105 private harness tests**.
They include every proposed request through the real provider adapter with mocked
HTTP; the original eight DeepSeek control wires; full context and all original
selections in every narrow request; native Luna schemas; refusals, truncation,
empty/duplicate outputs, HTTP errors and unknown usage; input-count overflow with
no generation dispatch; approved-plan identity, locking, retirement and refusal to
resume a terminal comparison. Real HTTP transports and SQLite are blocked in the
private tests. Sixteen saved controls/captures pass through the tracked completion
boundary without granting semantic or writer authority.

Repository-wide Ruff lint/format and strict mypy pass across **222 Python files**;
the six private scripts also pass. The full repository suite passes **1,278 tests**
and final focused verification passes **143 tests**. The 38 tracked tests overlap
the full suite, for **1,383 unique tests overall**. Actual results are recorded in
the preparation verification records and tracker. No
frontend, API or generated-contract behavior changed, so frontend build and UI
tests are not repeated for this engine-only slice.

Repeat local verification from the repository root with unused output paths:

```powershell
$env:PYTHONPATH='engine;apps/api;apps/worker'
.venv/Scripts/python.exe -X utf8 data/diagnostics/reviewer-assessment-workload-v61-2026-11-02/verify_local.py data/diagnostics/reviewer-assessment-workload-v61-2026-11-02/verification-next.json data/diagnostics/assessment-preparation-next
```

This command has no metadata or inference operation. The public
[frozen approval plan](reviewer-assessment-workload-frozen-plan-2026-11-02.md)
separately describes any future payload and destination.

## Next step

Review the two independent frozen **30-attempt** plans, **60 maximum combined**.
The freeze binds 24 preparation files and 3,153 source fingerprints. A first
failure stops that provider's comparison; there is no automatic repair, retry,
model substitution, extra smoke request or budget transfer. Cross-provider results
will be descriptive because native schema enforcement and effective reasoning/
sampling controls differ. The within-provider workload contrasts are the primary
experiments. Approval of preparation is not approval of live inference.

After execution, inspect complete claims and source coverage before interpreting
resource gains. Better delivery alone does not qualify edit necessity or literary
quality. The next production qualification remains actual bounded scene repairs
and human feel/flow/character/story-breaking assessment, supported by machine
mechanics. Production prompt 61 / graph 9 / fulfillment policy 1 remain unchanged;
Step 19 **IN PROGRESS**, Step 20 **NOT STARTED**, canary **ON HOLD**.
