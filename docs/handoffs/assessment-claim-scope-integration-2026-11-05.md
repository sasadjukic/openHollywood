# Read-only claim-scope integration and repeat/order regressions

Date: 2026-11-05. Local integration completed; live calls remain PAUSED and the
full workflow canary remains ON HOLD.

The tracked assessment component now has an **authored claim-scope declaration
and audit display**. It binds the original selected claim to its declared question,
evidence obligation, source authority and material qualifiers. Missing or conflicting
declarations stay visible. Full source context remains available, and consistent
declarations do not establish factual truth or authorize a writer.

This implements the bounded next step from the
[scope-separated repeatability results](../benchmark_reports/reviewer-scope-repeatability-v61-results-2026-11-05.md).
The existing production prompts, profiles, graph and writer routes are unchanged.
No inference, input-count, catalog or daemon requests occurred; no credentials or
application database were accessed.

## What changed

The new [assessment_claim_scope.py](../../engine/open_hollywood_engine/evaluations/assessment_claim_scope.py)
module is pure, provider-neutral code beside the existing work/result components.
[ADR 0043](../adr/0043-read-only-claim-scope-declarations.md) records the contract.

- A declaration binds to an exact work fingerprint, selected statement, field
  pointer, offsets and quotation. The application displays the complete report
  field as well as the selection, so surrounding qualifications are not hidden.
- Authored claim and evidence predicates distinguish obligations, observed events
  and choices, defined procedures, means, endpoints, attribution, plans, unavailable
  documents and editorial effect. Material components and unresolved qualifiers
  remain explicit. Expected labels and new gold are not part of the contract.
- Source roles reference the existing validated registry. The audit exposes missing
  authority, such as draft-only scope for an obligation or an endpoint without both
  assignment and draft. Every supplied declaration is identity-checked, including
  those outside the active batch; missing active declarations become visible findings.
- Complete-scope absence review, explicit nonperformance and unavailable scope stay
  distinct. For declared complete fields, the checker verifies coverage of all
  non-whitespace text by the located sections. An unavailable document can have no
  citation. The checker cannot establish that the author chose the right field or
  interpreted it correctly.
- The renderer recomputes the audit and preserves full context as literal, sorted
  JSON with safe fences. It can also display a native bound result through the
  unchanged result validator, retaining its raw response and original receipt.

The original work, active-scope, response-schema, result and completion contracts
are unchanged. Declarations remain local sidecars; they are not inserted into model
requests. Historical diagnostics use a different response contract and are retained
as original captures, without fabricating a new native delivery receipt.

This adds no CLI, production caller, ordinary-export eligibility, persistence,
migration, dependency, API/client schema, automatic claim classifier or human
checkpoint. It integrates with the tracked **read-only engine component**, not the
autonomous revision or acceptance path.

## What the local replay showed

The private bundle preserves **448 exact captured files** and verifies **5,307
historical fingerprints**. It contains all **56 exact-repeat pairs and 56
presentation-order pairs**, including their 112 original inspected slots, request
identities, receipt/assessment hashes and favorable controls. Complete requests,
sources, final responses, reasons and original evidence inspections remain available.
All **169 exact evidence quotations** remain in the unmodified captures; this local
integration does not make new semantic judgments about them.

The adapter exercises the tracked contract and renderer on all sixteen new reports
and all sixteen prior interpretation reports: **32 full-work renders, 224 selected
claim declarations**.

| Source set | Local declaration result | Original model score |
| --- | --- | --- |
| Scope-separated repeatability, 112 slots | 112 declared consistent | 112/112 grounded, unchanged |
| Prior interpretation, 112 slots | 92 declared consistent; 20 need scope review | M 48/56; E 50/56 grounded, unchanged |

The same twenty historical slots are flagged as in the previous local audit:
twelve bare-event controls evaluated under obligation criteria and eight mixed
targets, including the means/qualifier issues. All twenty retain declared predicate
and material-coverage conflicts; eight also retain editorial-effect scope. These
findings overlap and are not twenty-eight separate failed claims.

The historical adapter translates the earlier audit's authored predicates and
component-coverage annotations into the new declaration vocabulary. This is a
consistency replay of that explicit audit, **not independent semantic discovery**.
No original model response, label, score, gold, citation or evidence criterion was
changed. Neither `declared_consistent` nor `needs_scope_review` is a replacement
accuracy score.

## Limits that remain

The application can verify identity, literal source coverage and consistency between
declared fields. It cannot prove that an author noticed every material qualifier,
assigned the right source role, chose the only defensible reading or distinguished
fact from literary effect correctly. The tests explicitly retain a false means claim
whose declaration is internally consistent: its factual support remains unassessed.

Likewise, source-scope references describe the obligation being audited. They are
not a whitelist of acceptable model citations and do not prove that a model's
actual citations are adequate. Location, semantic support, editorial effect, edit
necessity and craft remain separate. Whole-relation credit and writer authorization
remain false even after successful declaration and result binding.

The new layer has not yet been qualified on ordinary saved critic reports or used
to generate declarations autonomously. The successful Sol diagnostic involved
deliberately explicit authored claims and short scenes. It does not resolve
ordinary editorial judgment or prove better storytelling.

## Verification

The repository's full Python suite passes **1,394 tests**, including **31 new
tracked scope tests**. A separate private replay suite passes **37 tests**. These
are **1,431 distinct passing tests**, with nothing deselected. The earlier focused
68-test run overlaps these totals and is not added again.

Repository-wide Ruff, formatting and strict mypy pass for **226 Python files**;
the same checks pass separately for **four integration scripts**. The source
preservation, all 32 renders and declaration summaries replay deterministically.
Verification pins the new engine and test files before/after the checks. Provider
credentials are removed from the test environment; repository database tests use
temporary databases and mocked gateways. New focused tests block socket/HTTP/SQLite
access explicitly.

The new tests cover selected claims within larger fields, Unicode/paragraph
coverage, missing declarations, omitted qualifiers, mismatched predicates, missing
authority, complete absence review, unavailable documents, duplicate/foreign IDs,
inactive-record validation, unchecked caller mutation, literal rendering, failed
delivery, raw-response identity and unchanged completion. Deliberately malformed
Pydantic construction fixtures emit expected serializer warnings before rejection.

Two early focused failures exposed a missing-declaration branch variable and an
incorrect completion-field assertion in the new tests; both were corrected before
final verification. There was no provider activity or historical evidence change.
The uv-managed environment ran the README Python commands through
`.venv/Scripts/python.exe -X utf8 -m`. Frontend/build checks are inapplicable to this
engine-only addition; no frontend or generated API contract changed.

Private evidence and command logs:
`data/diagnostics/assessment-claim-scope-integration-2026-11-05/`.
The [summary](../../data/diagnostics/assessment-claim-scope-integration-2026-11-05/summary.json),
[pair regressions](../../data/diagnostics/assessment-claim-scope-integration-2026-11-05/repeat-order-regressions.json)
and [verification record](../../data/diagnostics/assessment-claim-scope-integration-2026-11-05/verification.json)
are local private artifacts, not GitHub attachments.

## Recommended next step

Do a bounded **local ordinary-review scope-admission audit** before another live
experiment:

1. Reuse up to **twelve saved ordinary-v61 probe captures** already covered by the
   authenticated diagnostic-probe export path. Recheck their exact source lineage
   and full context; retain incompatible or incomplete cases with explicit reasons.
2. Author scope declarations against their unchanged selected statements. Preserve
   surrounding report fields and genuine means/endpoint qualifications. Record
   factual claims with declared scope, mixed/editorial claims requiring separate
   assessment, missing authority and unresolved interpretation. Do not rewrite a
   difficult original claim into an easier factual claim and call it equivalent.
3. Exercise the new renderer and validation locally; report applicability and
   declaration disagreements separately from original model accuracy. Keep this
   bounded rather than automatically expanding the sample. It will show whether
   the component can describe ordinary review work without stripping away the
   editorial concerns that matter to story quality.

If that audit establishes a usable ordinary-review workload, propose a small
separately frozen Sol-high diagnostic using those source/claim classes and fresh
controls. Decide its questions and budget from the audit rather than repeating the
already successful explicit fixtures. No new live plan or allowance is frozen here.

Only after reliable factual assessment and independent edit-necessity evidence
should writer integration and craft comparison be considered. Human quality review
should remain focused on feel, flow, character and story-breaking details, supported
by prepared mechanical evidence. This introduces no routine human checkpoint.

All fourteen issues remain open, with original bodies and posted URLs unchanged.
CW-007/CW-013 gain local integration evidence; CW-014 remains unqualified.
**Step 19 IN PROGRESS; Step 20 NOT STARTED; production prompts unchanged;
live calls PAUSED; full workflow canary ON HOLD.**
