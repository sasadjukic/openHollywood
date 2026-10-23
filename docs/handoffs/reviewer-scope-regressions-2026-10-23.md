# Reviewer scope and malformed-output regressions

Date: **2026-10-23**. Status: **COMPLETE LOCALLY**.

The [T/R continuation](../benchmark_reports/reviewer-tr-continuation-v61-results-2026-10-22.md)
now has source-bound regression fixtures for endpoint attribution, mandatory-task
scope and malformed C2 delivery. **No inference or daemon discovery occurred.**
Production remains **prompt 61 / graph 9 / fulfillment policy 1**. The canary
remains **ON HOLD**; live calls remain paused.

## Evidence preserved

The private bundle is
[`data/diagnostics/reviewer-scope-regressions-v61-2026-10-23/`](../../data/diagnostics/reviewer-scope-regressions-v61-2026-10-23/).
It contains all **32 logical T/R responses**: 31 from the continuation and the
one carried T1 response. Thirty-one are structurally valid; one is invalid.
These are copies of existing observations, **not new trials or model successes**.
The earlier failed HTTP attempt is not a logical answer and is not converted
into a fixture success. Historical accounting remains **41 combined attempts**,
with D stopped and the original HTTP failure's usage unknown.

Each fixture binds the full source packet, artifact versions, original withheld
labels, prepared request, exact wire request, raw response body, original receipt
and operator inspection. Source file hashes and the prior analysis seal are
checked before replay. Raw answer strings are preserved exactly. The original
validator and scorer reproduce every receipt. Earlier preparation, execution,
inspection, report and production files remain unchanged.

The fixtures preserve complete reports, including craft judgments and unsupported
explanations. The new audit only projects selected fields; it does not replace
the broader historical usability judgment or infer that a report is sound
because the selected fields pass.

## Regression coverage and findings

| Evidence | What the fixture catches | Control retained |
| --- | --- | --- |
| All eight T/R h03 reports | The missing ten-year realization is correctly found, then wrongly used to fail the endpoint, even though the unsettled, pre-verification final state survives | F06 correctly keeps a satisfied endpoint despite losing an earlier required fact |
| T-h04-C2-OR | Departure violates the final-state requirement but does not erase the earlier formation of a truce | T-h04-T1-OR and recovered C2/RO preserve the event and correctly fail the endpoint |
| T-F02-C2-RO and T-F02-T1-OR | Each reports the mandatory task met, yet sets mandatory failure because of a separate motion contradiction outside that task's explicit acceptance scope | The other two F02 reports keep mandatory failure false while still identifying the contradiction |
| F01, F05, F06 | Permitted departure, successful optional duplication cleanup, and a mixed mandatory failure plus successful optional cleanup remain distinct | Optional success cannot offset a required loss; optional concerns cannot silently expand a mandatory task |
| Carried T-h04-T1-RO and remaining reports | Correct labels do not erase an unsupported explanation or make a report usable | The carried false simultaneous-contradiction claim remains unsupported; prior n03 notes also remain intact |
| T-F01-C2-OR | Normal provider stop with syntactically incomplete and structurally misplaced JSON remains invalid | Length finishes, non-200 responses, bad hashes and duplicate keys retain their separate rejection paths |

The audit reproduces **eight endpoint errors, one fact-attribution error and two
mandatory-scope errors** among the valid responses. The two mandatory-scope errors
also fail internal task-to-aggregate consistency; those are **the same two errors,
not two additional failures**. All eight endpoint errors are h03 observations,
including repeated C2 requests across T/R; they are not eight independent stories.

### Finding evidence, assigning scope, aggregating

The local diagnostic separates three questions:

1. **What did the reviewer find?** Preserve its event, final-state and craft
   claims, exact evidence, and the independent source-grounded inspection.
2. **Which requirement owns that finding?** Compare event and endpoint labels
   independently against the original withheld labels. Authored local controls
   cross event retained/lost with endpoint satisfied/violated. They also change
   whether a real craft defect is expressly mandatory while keeping the defect.
3. **Does the mandatory aggregate follow the declared tasks?** A local consistency
   projection considers only explicitly identified mandatory task statuses. An
   unmet required task yields failure; all met yield no mandatory failure;
   uncertainty remains unknown unless another required task is definitely unmet.
   Missing, duplicate, undeclared or invalid identities/statuses are rejected.

The third check exposes both F02 errors without asking a model another question.
It is **conditional on the truth and completeness of the task verdicts**. It
cannot establish that the verdicts are correct, detect a false explanatory
premise by itself, or resolve h03's wrong endpoint mapping. It is diagnostic-only:
no model answer is overwritten, rescored as a success or accepted for production.

The local scope controls are explicitly authored test inputs, not additional
model responses or a frozen future live casebook. They test the accounting rule,
not a machine's ability to interpret arbitrary prose. Neither keyword matching
nor a case-ID rule is used to infer an endpoint.

F02's craft defect remains visible in all four captures: each cites the
motionless/moving sentences and records a naturalness loss. The scope controls
also require a mandatory failure when consistency is explicitly added to the
requirements. Thus a narrow assignment pass is never advertised as a clean story.

### Malformed C2 capture

The exact captured answer has **4,165 characters**, HTTP 200, `done:true`,
`done_reason:stop`, and **860 output tokens**. Parsing fails at EOF. The root is
unclosed; six required root fields are misplaced inside `craft`.

The regression verifies that appending a brace in memory still fails the
unchanged C2 schema. This deliberate invalid mutation is not saved as a repaired
answer. The original receipt remains `invalid_stop` / `invalid_json`, without
semantic scores or repair credit. It is not classified as a length finish or as
a duplicate-key response. Non-200 input is rejected before answer/length scoring;
the existing [terminal support](reviewer-terminal-evidence-support-2026-10-22.md)
continues to own gateway error chains and unknown-usage preservation.

## Verification and repeatable commands

**81 tests pass:** 72 new scope/capture checks plus the nine unchanged continuation
post-run checks. Ruff lint, Ruff format and strict mypy pass on the three new
private scripts. The supported offline `--verify` command reproduces the saved
audit. New tests block socket connections, DNS and real HTTP transports.

An initial test run had four test-authoring errors: the new F02 assertion treated
the existing string `literary_comparison` field as an object. Correcting that
assertion preserved every source capture and expected outcome. The initial XML
is retained alongside final verification. Import-export typing errors were also
resolved locally without editing historical modules.

Run from the repository root, using a fresh pytest base directory if repeating:

```powershell
.venv/Scripts/python.exe -X utf8 data/diagnostics/reviewer-scope-regressions-v61-2026-10-23/scope_audit.py --verify
.venv/Scripts/python.exe -X utf8 -m pytest data/diagnostics/reviewer-scope-regressions-v61-2026-10-23/test_scope_regressions.py data/diagnostics/reviewer-tr-continuation-v61-2026-10-22-analysis/test_postrun.py -q
$files = @(Get-ChildItem data/diagnostics/reviewer-scope-regressions-v61-2026-10-23 -Filter *.py | ForEach-Object { $_.FullName })
.venv/Scripts/ruff.exe check @files
.venv/Scripts/ruff.exe format --check @files
$env:MYPYPATH = 'engine;data/diagnostics/reviewer-tr-continuation-v61-2026-10-22-analysis;data/diagnostics/reviewer-tr-continuation-v61-2026-10-22;data/diagnostics/reviewer-isolated-pilots-v61-2026-10-22;data/diagnostics/reviewer-terminal-evidence-v61-2026-10-22'
.venv/Scripts/mypy.exe --strict @files
```

`build_fixtures.py` is the recorded one-time construction script and refuses to
replace an existing fixture directory. Routine verification uses `--verify` and
pytest. Scripts and detailed prose remain in the ignored private bundle, matching
the earlier diagnostic evidence policy. They require that local evidence chain;
this document alone is not a self-contained public CI fixture package.

Relevant checks cover the diagnostic changes. No application source, schema,
gateway, production prompt or workflow changed, so application-wide tests and
the frontend production build were not repeated. The bundle manifest binds the
new scripts, fixtures, verification and public documents; its digest is in the
tracker. No historical seal is regenerated.

## Decision

This completes the requested local follow-up. It closes no critic/writer issue
and supplies no new literary preference evidence. Preserve the nine human ties
and the focus on feel/emotion, flow, character and story-breaking concerns.

The local evidence justifies a **provisional 48-call requirement-ownership
comparison**, described in the [next experiment proposal](reviewer-requirement-ownership-proposal-2026-10-23.md).
The deterministic aggregation question itself needs no further inference. The
remaining model question is whether explicitly assigning requirements to report
fields improves grounded judgments on fresh material without hiding craft defects.
That proposal is **not prepared, frozen or approved for execution**. Production
prompts are unchanged, live calls remain paused and the canary remains **ON HOLD**.
