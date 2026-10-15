# Critic own-requirement failed clauses, fixed v59 — 2026-10-15

Status: **DIAGNOSTIC COMPLETE — PARTIAL IMPROVEMENT; PRODUCTION V59 UNCHANGED.**

All sixteen approved probes completed in seventeen calls, including one structural
retry. The diagnostic kept the fulfilled decision met while blocking the separate
overrun in **3/4** final reviews, versus **0/4** for ordinary v59. Both arms accepted
both valid baselines and detected both missing-date and both missing-decision
controls. One experimental review still cites a valid requirement and draft passage
but makes an unsupported contradiction claim. This is partial improvement, not a
production qualification.

The [previous fulfillment-scope diagnostic](critic-fulfillment-scope-v59-2026-10-15.md)
did not improve classification: both arms marked an already fulfilled decision
unmet in all four cases with a later forbidden match. They correctly blocked the
endpoint violations and detected genuinely missing dates and decisions. This test
makes the alleged failure directly inspectable inside each check.

Source commit: `d44605aa5bfddf2b1878e481ad61204d3c217e99`.
Branch: `codex/critic-failed-clause-v59`.
Production remains **prompt v59 / graph v9**. Main, production prompts, schemas,
validators and writer behavior are unchanged. Step 19 remains IN PROGRESS; Step 20
is NOT STARTED.

## Diagnostic intervention

The experimental arm replaces this system span:

> Overruns become blockers; still assess the complete assigned outcome independently in assignment_checks.

With:

> Overruns remain blockers. Each assignment check must copy its requirement_binding from its schema. For unmet, failed_clause identifies verbatim text from that same named requirement, whether the fact is missing or contradicted, and 1-3 current draft_evidence_refs. Its assessment must explain why those passages fail that clause, accounting for actions or indirect narration that may fulfill it. For met, failed_clause is null. A separate exit-state violation belongs in scene_boundary_check; it cannot supply the failed clause of another requirement unless that requirement itself contains the violated condition. Preserve this separation in repair advice and verdicts: a fulfilled check never cancels a separate blocker. The diagnostic schema's two added fields are required; every other v59 output rule and complete-fact meaning of met remains.

Each native turning-point and outcome check gains two required fields:

| Field | Contract |
| --- | --- |
| `requirement_binding` | Exact versioned source reference and complete text of this check's own current Scene Plan requirement. |
| `failed_clause` when met | Null. |
| `failed_clause` when unmet | Verbatim clause from that requirement, `missing` or `contradicted`, one to three distinct current-draft evidence references, and an explanation of why the evidence fails the clause. |

The existing four native fields remain unchanged. The diagnostic adapter validates
keys, source identity, exact requirement text, quote membership and evidence
references. It records a separate audit resolving the source and cited passages,
then removes only the two diagnostic fields before ordinary v59 materialization
and audits. It never changes a status, rewrites advice, suppresses a blocker or
decides whether the cited passage semantically supports the allegation.

The new schema and binding instructions persist in the existing single structural
retry. Wrong references or malformed fields can trigger that retry; a valid but
unsupported claim cannot. Boundary checks and structured mandatory repair
conditions keep their existing routes. An endpoint violation should remain blocking
without being attributed to another requirement unless that requirement itself
contains the violated condition.

This is a combined guidance/schema/diagnostic-validation treatment. It cannot
isolate which component caused any change. Ordinary-v59 requests exactly match the
previous current arm. All input artifacts, settings and budgets match within each
pair. No writer evidence packet is supplied.

## Frozen matrix

Use the same four private OH-V01-002 drafts and seeds **19101 and 19103** under both
ordinary v59 and the failed-clause treatment:

| Draft | Turning point | Decision to verify | Separate endpoint | Expected verdict |
| --- | --- | --- | --- | --- |
| Accepted inconclusive investigation | Met | Met through actions | Compliant | Pass |
| Same draft plus forbidden definitive match | Met | Met through unchanged actions | Overrun | Revise |
| Missing future date plus definitive match | Unmet | Met through unchanged actions | Overrun | Revise |
| Future date, genuinely unresolved decision | Met | Unmet | Compliant | Revise |

All drafts and the synthetic plan are unchanged from the previous diagnostic.
The plan assigns a decision to verify and separately prohibits an established
handwriting match at scene end. Fresh revision-zero context contains no historical
repair advice. Both the missing-date and missing-decision controls are retained
exactly; no canonical story or approved production Blueprint is edited.

Run all **16 independent critic probes**, counterbalancing arm order across seeds.
Allow at most one structural retry each. No rerolls, replacement cases, writer
calls, full-story runs or canonical writes.

Maximum: **32 calls / USD 0.20992**, using the recorded October 8 rates of USD 0.14/M
input and USD 0.40/M output, with 24,000 input / 8,000 output tokens per call. Actual
charges remain unknown. Use the existing `gemma4:31b-cloud` deployment and frozen
model digest, temperature 0.2, top-p 0.95 and thinking disabled.

## Local verification

- Twenty no-network mock calls exercise the complete matrix, two successful
  structural repairs and a permanent failure after two attempts.
- Thirteen malformed source, clause and evidence variants are rejected. All eight
  pairs retain identical artifacts/settings/budgets; current requests exactly match
  the prior current arm. Production hooks are restored after each run.
- Sixteen previous raw responses reproduce their canonical outputs. Adding only
  synthetic, locally constructed diagnostic annotations also preserves those
  outputs, including eight incorrect unmet judgments. These are fixture checks,
  not new model results, and demonstrate that validation does not impose semantics.
- Verify 1,932 prior sealed files, their reports, the source database and v59 hashes.
- Forty-five focused regressions pass in 13.48 seconds. Repository Ruff, formatting
  and strict mypy pass for 198 files; diagnostic formatting/error checks pass.

## Assessment protocol

Replay every sent request, raw response, diagnostic audit and canonical result.
Inspect every failed clause and explanation against both its own assignment and
the cited draft evidence. A source-valid quote can still be an unsupported claim.
Record first-attempt and final validity separately.

The primary joint result requires the fulfilled decision to remain met, the later
endpoint violation to remain blocking, and mandatory advice not to demand another
expression of the already fulfilled decision. Check raw and canonical verdicts,
boundary findings, native conditions and consolidated generic advice. A met status
alone does not qualify if advice adds an unsupported requirement or the verdict
passes a defective scene.

Both negative controls must remain unmet in their respective checks with supported
clauses and necessary repairs; valid baselines must remain accepted. Record
duplicate reporting separately. If the ordinary arm does not reproduce its previous
judgment, report that variation rather than attributing it to the treatment.

This is one scene/provider and two seeds, with a synthetic split outcome/exit state
and fresh review context. It does not test writer repairs, general story quality,
or a terminal restriction embedded within the outcome itself. There is no automatic
production promotion.

## Live results

| Observation | Ordinary v59 | Failed-clause diagnostic |
| --- | ---: | ---: |
| First-attempt valid reviews | 8/8 | 7/8 |
| Final valid reviews | 8/8 | 8/8 |
| Valid baselines accepted | 2/2 | 2/2 |
| Fulfilled decision stays met while the overrun is blocked | **0/4** | **3/4** |
| Later endpoint violation detected and blocked | 4/4 | 4/4 |
| Genuinely missing future date detected | 2/2 | 2/2 |
| Genuinely unresolved decision detected | 2/2 | 2/2 |

The primary result includes the unchanged decision in both the future-date and
missing-date overrun drafts. The diagnostic succeeds on the future-date draft at
seed 19101 and on the missing-date draft at both seeds. It fails on the future-date
draft at seed 19103. Two successful results are first-attempt valid; the third
requires a link repair. The raw native classification was already correct before
that retry, but the response as a whole was structurally invalid.

The ordinary arm reproduces all four disputed native classifications. The treatment
does not change any final boundary status or canonical verdict; its improvement is
in attributing failures to the correct requirement. Replay verifies that all sent
requests match the frozen protocol and that the adapter does not alter judgments.

### A correct citation can still support an incorrect claim

In `s19103-preserve-clause`, the critic quotes the complete assigned decision and
labels it `contradicted`. Its evidence is the later sentence establishing a match.
The explanation says the draft does not end with the decision and instead completes
verification. The quote contains no requirement that the decision be the final
event. Earlier journal comparison and replication remain valid evidence that the
decision occurred. The match violates the separate exit state, which is correctly
blocked, but does not negate the prior decision.

All five final experimental failed-clause objects have valid own-requirement quotes
and current-draft references. Four are semantically supported negative-control
findings; this fifth is not. All nine experimental responses, including the invalid
first attempt, pass the diagnostic source/evidence binding checks. The remaining
error is therefore not missing source identity or a validator silently correcting
the model. Traceability has made the unsupported inference visible.

### Repair advice, controls and retry

In the three successful overrun reviews, the critic adds no mandatory condition to
repeat the fulfilled decision. The canonical repair is the unchanged v59 boundary
policy, which removes unassigned advancement while preserving inconclusive tests.
That policy still broadly says to restore the outcome and exit state, and canonical
boundary findings retain the existing `scene_assignment:outcome` category. The
native checks and boundary audit remain distinct; no writer preservation result is
established by this critic-only test.

In the remaining experimental failure, advice requires removing the match and
ending with the decision or initial inconclusive attempts. Removal is supported;
requiring those actions at the ending adds a restriction absent from the quoted
outcome. The alternative allows existing inconclusive actions, so it does not
explicitly demand a fresh decision, but the native unmet classification is still
incorrect.

Both missing-decision controls cite the explicit unresolved choice and require a
decision without prescribing dialogue, immediate causation or completed verification.
Both missing-date controls correctly identify that the card is dated today instead
of ten years ahead. The second-seed missing-date treatment initially attaches generic
boundary criticism to the met outcome. Existing v59 validation rejects that link.
Its single retry correctly links the complaints to the turning point and boundary,
preserving the met decision and supported date clause.

That retry also shortens the date repair condition to changing the date, omitting
an explicit instruction for Elena to realize the discrepancy. The complete
realization requirement remains in the finding and assessment. This is a remaining
advice-completeness concern; detection is established, but complete writer repair
has not been tested.

One ordinary-arm overrun retains duplicate native/boundary canonical complaints;
none does in the diagnostic arm. Other ordinary reviews consolidate the incorrect
native assessment with the legitimate boundary failure. All generic complaints in
this matrix concern assignments, rather than independent craft defects. Several
next-scene comparisons also overstate a handwriting match as acceptance of a genuine
warning. The explicit no-match restriction independently supports the blocker;
acceptance itself is not established by the added sentence.

Final raw verdicts are four passes, ten rejects and two revisions. Unchanged v59
handling normalizes repairable rejects, yielding four canonical passes and twelve
revisions. No defective draft passes. There are no failed probes, skipped probes,
writer calls, rerolls or canonical changes.

All seventeen requests, responses and audits replay exactly. Usage: **332,418 input /
24,794 output tokens**; **USD 0.05645612** at recorded October 8 rates, with actual
charges unknown. Production hashes, source artifacts and prior sealed evidence
remain unchanged.

## Next focused recommendation

Keep production v59. Hold this diagnostic implementation fixed and contrast the same
draft under a decision explicitly required to occur during the scene versus a
condition explicitly required to hold at scene end. Retain both negative controls.
This tests the observable remaining interpretation: treating an event requirement
as a terminal restriction. A genuine terminal condition must still be judged unmet
when violated; a past fulfilled decision must not be undone by a separate overrun.

Do not force statuses in application code, promote the current candidate, or proceed
to writer transfer on the strength of three successful cases. This completed run
does not authorize another cloud experiment.

## Private evidence and approval

Bundle: `data/diagnostics/critic-failed-clause-v59-2026-10-15/` (ignored locally).
Evidence includes the runner, replay script, local fixtures and receipts, sixteen
frozen requests, artifact versions/hashes, predeclared assessment protocol, explicit
approval, seventeen live receipts, exact replay and independent semantic inspection.

Plan SHA-256:
`c6bf9802721de83859002fcc42a61a5c96f43a0e7776ed4dcb41cd3044ef37e9`.

Prior diagnostic closure SHA-256:
`59be349b427b524124dccd2eb203826e0563b676645b9fc593c115619f304e19`.

Explicit approval is recorded against the frozen plan. The closure hashes the
report and private evidence bundle. Production remains v59; promotion is not
warranted by this partial result.
