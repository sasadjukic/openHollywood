# Registered authored-source observed completion publisher — 2026-11-15

## Outcome

Implemented the narrow registered read-only publisher for the three saved F01/F02/F03
deliveries. It reuses the original audit, native binding/completion, authority
renderer and guarded publication machinery. The existing authored-fixture and
registered-probe publishers, frozen implementations and production prompts are
unchanged. No live calls, credential provisioning or provider preflight occurred.

The export carries all nine active whole claims, three unselected editorial
summaries, full source context, exact inputs/requests and observed outcomes. Source
origin remains authored; delivery origin remains observed. Binding and accounting
clearance do not establish semantic reliability, revision necessity or story quality.

Implementation: [application adapter](../../apps/api/open_hollywood_api/services/assessment_authored_observed_completion.py),
[operator CLI](../../scripts/assessment_authored_observed_completion.py),
[regressions](../../tests/api/test_assessment_authored_observed_completion.py),
[ADR 0060](../adr/0060-registered-authored-observed-completion.md).

## Operator use

Run locally from the repository root, into a new directory outside source archives:

```powershell
uv run --extra api python scripts/assessment_authored_observed_completion.py `
  --source authored-smoke-2026-11-15 `
  --output data/exports/authored-observed-completion-001
```

The registration pins plan SHA-256
`f474bfc29bee448116993fc6845faccbee3cf60b48e1b1cbf8afc5ac3e93b779`
and audit-manifest SHA-256
`3cd78a547a82832decf5625ec2256f53c09620fd5fdb98fc367e249966c696e9`.
It does not accept caller receipts, arbitrary source paths/hashes, origin overrides,
fixture journals or partial work selection. Existing exact exports are reused
without rewriting; conflicting or partial exports are refused and retained.

The **43-member** export contains:

- Per family: six exact input JSON files, original source and source receipt, exact
  request, presentation, separately request-bound authority, full completion
  envelope and evidence view: thirteen files each.
- Shared: original audit, original audit manifest, exact request set and final
  publication manifest. The source audit manifest authenticates the original
  seventeen-member audit; the publication manifest authenticates this export.

Read `F01.completion.json` through `F03.completion.json` for the full envelopes.
The three `.view.md` files are linked native projections. Original construction
receipts correctly retain `assessment_delivery_authenticated=false`; observed
delivery is authenticated by the separate observation binding and terminal.

## Admission and observed inspection

Publication requires the registered source, exact reusable audit, six observed
terminal slots, closed complete journal and all three original works. Each terminal
is rederived; native whole-work binding is recomputed. Accounting is checked
separately, including cached and reasoning tokens. No successful subset is released.
Unknown usage, accounting overrun, incomplete closure, invalid source/request
binding or altered captures refuse publication before its final manifest.

All original local scopes and authority values remain unchanged. The request-bound
authority copies differ only in request identity. The native views match the original
audited evidence projections, including complete receipt binding. Full raw finals,
citations and held/unselected source material remain available in the envelopes.

Observed generation usage remains **35,134 input / 1,983 output**, with **801
reasoning** and **zero cached input** tokens. Actual billing stays null. The earlier
manual inspection (9/9 labels; 16/16 material components) remains separate historical
evidence; publication does not rescore it or grant semantic approval. All semantic,
evidence, editorial, edit-necessity and craft statuses remain `unassessed`, and writer
permission remains false.

## Verification

**All 38 new regression cases pass**, covering complete publication/reuse, original
source and request identity, native rendering, origin/closure/coverage refusal,
unknown cached usage, overrun, truncated or malformed delivery, altered source/audit/
journal/preparation, manifest-last failures, partial-output preservation and sanitized
secret refusal. The suite passed 37 cases after local corrections; the corrected
secret-sentinel case passed separately (8.59 seconds). No production code changed
between those two runs.

**425 existing tests pass** (590.83 seconds): source admission, authored OpenAI
mapping/smoke audit, both earlier publisher paths, native authority, binding,
completion and work contracts. The run retains **34 existing Pydantic serializer
warnings** from deliberate malformed authority fixtures. These are software tests,
not new model samples. Ruff, formatting and strict mypy pass on **301 files**,
including the two private qualification/preservation helpers. The tracked CLI
independently returns `reused` for the accepted export.

Preservation checks pass for **2,934 earlier sealed members**, the separate **64**
authored controls, **636** archive pins, **1,068** source/preparation/result files
and mtimes, all three closed smoke journals, and the **43** accepted publication
files/mtimes. **827 of 830** baseline files outside the three intended documentation
updates are unchanged. All fourteen issue bodies and posted GitHub URLs remain
intact. Local documentation links and `git diff --check` pass. No frontend build or migration was needed. Full-repository pytest was not run;
the applicable suites and repository-wide Python quality checks were run.

The first saved-data check caught an unresolved receipt label in the new rendered
projection; using the bound terminal receipt now reproduces the reference audit
view exactly. A new test locks that behavior. The initial test also targeted a
nonexistent archive-root manifest; it now mutates the actual admission manifest.
The secret-refusal fixture also needed a sentinel actually present in these authored
sources. These were local implementation/test defects, not new model failures. Initial logs
and the draft export are retained alongside the corrected qualification evidence.

Private evidence: `data/diagnostics/assessment-authored-observed-completion-2026-11-15/`.
The accepted export is `verified-publication/`; `published/` is the retained initial
development export, not the accepted result. Offline qualification denies network,
HTTP/provider dispatch, live/qualification entry points and database access.
Existing secret-refusal guards remain active. No user database or API key resolution
is needed. No frontend, persisted schema or dependency changed.

## Recommended next step

Do one **bounded local consumer-integration design and rehearsal** across up to
seven completed works: these three authored controls and the four existing registered
probe completions. Define the read-only assessment status that the artifact-review
surface would display beside the original critic claim, using existing exports.

Keep original criticism, model judgment, source authority, evidence coverage,
delivery/accounting state and unresolved semantic/editorial obligations distinct.
Exercise failed, missing and unknown-usage fixtures so an absent result cannot look
like a clean review. Retain the full context through artifact links. Specify the
minimal consumer contract and acceptance checks before adding a production route
or workflow consumer; do not create another inference transport or rerun these cases.
This is an optional operator view, not an additional mandatory human checkpoint.

That makes the accumulated evidence useful for production review while preserving
the boundary still unqualified: whether criticism justifies an edit and whether that
edit improves the story. Human review should remain focused on feel, flow, character
and story-breaking effects, with mechanical evidence prepared by the application.

No new live experiment is justified by this publication result alone. CW-007/CW-013
remain open; CW-014 remains unqualified. **Step 19 IN PROGRESS; Step 20 NOT STARTED;
production prompts unchanged; live calls PAUSED; full workflow canary ON HOLD.**
