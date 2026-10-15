# Required event versus terminal condition, fixed v59 diagnostic — 2026-10-15

Status: **DIAGNOSTIC COMPLETE — CLASSIFICATION CONTRAST REPRODUCED; REPAIR QUALIFICATION OPEN.**

All sixteen approved probes completed in eighteen calls, including two structural
link retries. The event-versus-terminal classification contrast held in **4/4 paired
overrun cases**. Both negative controls were detected under both wordings at both
seeds, and all valid baselines passed. Production remains v59. This establishes the
narrow classification result; positive certification of fulfilled parts inside an
unmet compound requirement and complete repair advice remain unqualified.

The [previous failed-clause diagnostic](critic-failed-clause-v59-2026-10-15.md)
preserved the fulfilled decision while separately blocking the overrun in 3/4
experimental reviews, versus 0/4 for ordinary v59. Its remaining unsupported claim
read a decision to verify as a requirement to end with that decision. The source
quote and evidence reference were valid; the added terminal restriction was not.

Source commit: `15aedd381e7f3c7d53a3e0a9bd98f71c57f70c6d`.
Branch: `codex/critic-event-terminal-v59`.
Production remains **prompt v59 / graph v9**. Main, production code, writer behavior
and canonical stories are unchanged. Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.

## Fixed implementation, changed assignment

Reuse the sealed `own_failed_clause_1` diagnostic's request builder, instructions,
schema builder, adapter, materialization, audits and structural retry directly.
There is no additional critic instruction or new response field. Each unmet check
still requires its own exact clause, current-draft evidence and an explanation.
Source validation still establishes traceability rather than semantic support.

Only the synthetic current Scene Plan outcome and its Blueprint copy change:

| Variant | Exact assigned outcome |
| --- | --- |
| Event | During this scene, Elena decides to verify the handwriting. |
| Terminal | At the end of this scene, Elena has decided to verify the handwriting but has not established a handwriting match. |

Both variants retain the separate exit-state prohibition on establishing a match.
The terminal variant also makes that condition part of the outcome itself. It still
requires a decision, so the unresolved-decision draft remains a valid negative
control under both wordings.

Derived synthetic artifact versions, source references, the Story Bible's Blueprint
provenance pointer and schema binding values update consistently. The quote-length
bound is computed from each new requirement by the unchanged schema builder.
All other plan fields, other Blueprint scenes, canon content, prose, draft versions,
evidence handles, settings and budgets remain unchanged. The complete system message
is identical to the previous diagnostic. Fresh revision-zero context contains no
historical repair advice.

This contrast changes requirement ownership as well as explicit temporal wording:
the no-match condition is separately binding in both arms but also belongs to the
terminal outcome. It does not isolate those two components. There is no fresh
ordinary-v59 or original-wording arm; previous results are historical evidence only.

## Frozen matrix

Each row runs under both wordings at seeds **19101 and 19103**:

| Unchanged draft | Turning point, both variants | Event outcome | Terminal outcome | Boundary, both variants | Verdict, both variants |
| --- | --- | --- | --- | --- | --- |
| Accepted inconclusive investigation | Met | Met | Met | No overrun | Pass |
| Same prose plus forbidden definitive match | Met | Met | Unmet: no-match clause | Overrun | Revise |
| Missing future date plus definitive match | Unmet | Met | Unmet: no-match clause | Overrun | Revise |
| Future date, genuinely unresolved decision | Met | Unmet: decision | Unmet: decision | No overrun | Revise |

The missing-date control retains its today-date contradiction. The missing-decision
control retains its explicit unresolved choice and absence of verification actions.
No draft is rewritten to accommodate the new outcome wording.

Run all **16 independent critic probes**, counterbalancing wording order across the
two seeds. Allow at most one existing structural retry per probe. No rerolls,
replacement cases, writer calls, full-story runs or canonical writes.

Maximum: **32 calls / USD 0.20992** at recorded October 8 rates of USD 0.14/M input
and USD 0.40/M output, with 24,000 input / 8,000 output tokens per call. Actual
charges remain unknown. Use the same `gemma4:31b-cloud` deployment and frozen digest;
temperature 0.2, top-p 0.95, thinking disabled.

## Local verification

- Twenty no-network mock calls cover the complete matrix, two successful binding
  retries and a permanent failure after two attempts.
- All eight pairs are identical after normalizing only declared outcome text and
  derived artifact/source identities and quote-length bounds. Both negative-control
  drafts exactly match their sealed source versions.
- Wrong cross-variant assignment references, another field's clause and stale draft
  evidence are rejected. Unsupported event-unmet and terminal-met fixtures still
  validate structurally, preserving the legitimate separate endpoint blocker.
  The adapter does not force the expected semantic result.
- Replay all seventeen previous response attempts, including the failed generic
  link and its repair, against their original frozen inputs. No historical result
  or sealed implementation file is edited.
- Verify 2,155 prior sealed files, reports, source database and production hashes.
- Forty-five focused regressions pass in 13.17 seconds. Repository Ruff, formatting
  and strict mypy pass for 198 files; diagnostic formatting/error checks pass.

## Assessment protocol

Replay all actual requests, raw responses, clause audits and canonical results.
Record first-attempt validity, retries and final validity separately. Inspect every
clause and evidence passage for semantic support; a full-requirement quote can
still hide which part fails.

The primary contrast requires the same overrun draft to retain a met decision under
event wording but become unmet specifically for the terminal outcome's own no-match
clause. Both wordings must retain the separate blocking endpoint violation. The
terminal explanation must recognize the fulfilled decision rather than claiming
that no decision occurred.

Both baselines must remain accepted. Both missing-date controls must keep their
turning point unmet. Both unresolved-decision controls must fail the decision
clause, without incorrectly failing their satisfied no-match condition. Inspect
the complete date/realization repair, including after structural retries.

Inspect native conditions, consolidated generic criticism, duplicate reporting,
application-rendered advice and raw/canonical verdicts. No mandatory repair should
demand another decision or explicit restatement where actions already fulfill it.
Correct recognition of a prior event must not excuse a violated terminal condition
or weaken the separate endpoint blocker.

Interpret the result as a wording/ownership diagnostic on one scene/provider and
two seeds. It does not establish writer preservation, general story quality or
readiness to change production. No automatic promotion is authorized.

## Live results

| Observation | Event wording | Terminal wording |
| --- | ---: | ---: |
| First-attempt valid reviews | 6/8 | 8/8 |
| Final valid reviews | 8/8 | 8/8 |
| Expected native checks, boundary status and canonical verdict | 8/8 | 8/8 |
| Correct outcome status on overrun drafts | 4/4 met | 4/4 unmet |
| Separate endpoint violation remains blocking | 4/4 | 4/4 |
| Missing future date detected | 2/2 | 2/2 |
| Genuinely unresolved decision detected | 2/2 | 2/2 |
| Valid baseline accepted | 2/2 | 2/2 |

Every event overrun review cites the existing journal comparison and replication as
evidence that the decision occurred. The later match remains a separate blocker.
Every terminal overrun review identifies the exact clause **"has not established a
handwriting match"** and cites the later definitive-match sentence as its
contradiction. None alleges that the earlier decision is missing or requires another
decision. The same draft can therefore fulfill the event while failing the explicit
terminal condition, without either interpretation allowing the overrun to pass.

Both unresolved-decision controls instead cite the decision clause and the explicit
indecision passages. They do not accuse the satisfied no-match clause of failure.
The missing-date controls correctly identify today's date as contradicting the
ten-year future relation. All twelve final failed-clause objects have valid source
and evidence references and semantically supported failure claims in this matrix.

The terminal overrun assessments do **not** positively certify the fulfilled decision
clause with its own evidence: **0/4** do so explicitly. They select the correct failed
clause and do not deny the decision, but that is narrower than the predeclared aim
of positively recognizing and preserving fulfilled parts. The existing whole-outcome
`unmet` status cannot be used as a certificate for its fulfilled decision conjunct.
That part of the interpretation remains unqualified, rather than silently counted
as a complete preservation result.

### Structural retries and repair advice

Both event missing-date first responses correctly mark the decision met but link
generic boundary criticism to that met outcome. Existing v59 validation rejects
those links. Each single structural retry points the complaints to the boundary
and turning point instead, retaining all native classifications. First-response
classifications were already correct in all sixteen cases; only fourteen complete
responses were structurally valid. No retry fixes a diagnostic source binding or
changes an event judgment into a terminal judgment.

Final date-repair advice explicitly includes Elena's realization in **1/4** controls.
Both terminal reviews and the second-seed event retry require only changing the
date. The complete realization requirement remains in the cited source and finding,
so this does not prove that a writer would miss it. It does mean complete repair
cannot be inferred from the rendered recommendation alone. The second-seed event
retry drops the explicit realization condition present in its first response.

The event overrun reviews contain no authored decision repair; their boundary
recommendation remains the existing policy to remove unassigned advancement while
preserving inconclusive tests. Terminal overrun advice removes the match and retains
the applicable exit state, without demanding a new decision. One terminal condition
weakens "unsettled and suspicious" to "suspicion or unsettledness"; this is a further
advice-precision concern. Missing-decision repairs require a decision, without
mandating dialogue, immediate causation or completed verification.

One terminal overrun retains separate native and boundary complaints because their
evidence sets differ. Other cases consolidate the overlap or report only the
boundary. All generic criticism concerns assignments, not an independent craft
defect. Several next-scene comparisons still overstate establishing a match as
accepting a genuine warning, and terminal baseline achieved-state prose overstates
inconclusive comparison as a finding of non-identity. Neither inference is needed
to support the correctly classified explicit requirements.

Final raw verdicts are four passes, eight rejects and four revisions. Existing v59
handling normalizes the repairable rejects to revisions, producing four canonical
passes and twelve revisions. Every defective draft remains blocked. There are no
failed probes, skipped probes, writer calls, rerolls or canonical changes.

All eighteen requests, responses and audits replay exactly against the frozen
protocol. Usage: **363,194 input / 28,208 output tokens**; **USD 0.06213036** at
recorded October 8 rates. Actual charges remain unknown. The sealed diagnostic
implementation, production hashes and prior source evidence are unchanged.

## Interpretation and next focused recommendation

Explicit scope is usable by this unchanged critic: it distinguishes an event during
the scene from a no-match condition that belongs to the terminal outcome. This
supports the design distinction, but does not prove that adding "During" alone
fixes the earlier ambiguous wording. The experiment has no contemporaneous
original-wording arm and also changes ownership of the no-match condition.

Keep production v59 and the diagnostic implementation fixed. Resume a bounded,
gated writer-evidence transfer test using the explicit event-scoped assignment,
retaining both missing-date and missing-decision controls. The event reviews now
provide a met decision with evidence and a separate endpoint blocker, the distinction
the earlier transfer gate lacked. Test actual preservation of that indirect decision,
removal of the independent overrun, and complete date-plus-realization repair.

This would test whether incomplete recommendation wording causes incomplete prose
repair despite the full assignment remaining available. Do not assume that result,
certify a fulfilled conjunct from an unmet whole-outcome check, or promote the
diagnostic on this matrix alone. No further cloud run is authorized by this completion.

## Private evidence and approval

Bundle: `data/diagnostics/critic-event-terminal-v59-2026-10-15/` (ignored locally).
It contains the matrix runner, replay script, local fixtures and receipts, sixteen
frozen requests, exact input versions/hashes, predeclared protocol, explicit approval,
eighteen live receipts, exact replay and independent semantic inspection. The critic
implementation is imported from the previous sealed bundle without edits.

Plan SHA-256:
`550711ebef4d6026ec9026258036977d6b721c28b31d820c16e09c6ef7b92a94`.

Prior failed-clause closure SHA-256:
`385c3398738887f32589398f86082a6533f7610f2085d806b03b6d8268ed3090`.

Explicit approval is recorded against the frozen plan. The closure hashes the
report and private evidence bundle. Production remains v59; no promotion or writer
qualification is established by this diagnostic.
