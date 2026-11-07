# Saved-review authority-control admission

Date: 2026-11-07. Bounded local audit complete.
**The proposed 24-attempt B/H comparison is not ready to freeze from this selection.**
Live calls remain **PAUSED** and the full workflow canary **ON HOLD**.

Inspection of twelve saved ordinary-review captures admitted **ten positive and
four unavailable/uncertain whole-field controls**, but **no clear negative authority
control**. Eleven potentially misleading whole fields remain held for interpretation.
The twelve captures cover only the two familiar Elara/Elena scene families, with
no fresh family in this selection. This is an admission result, not a claim that
the model made no errors or that suitable negatives exist nowhere else.

This follows the [read-only authority integration](assessment-authority-integration-2026-11-07.md)
and its [contract](../adr/0045-read-only-assessment-authority-and-obligations.md).
No production implementation, prompt, profile, graph, gate, provider adapter or
database changed. No new model requests, budget or live experiment were frozen.

## Scope and method

The selection is the exact twelve captures from the
[ordinary-review scope admission](reviewer-ordinary-scope-admission-2026-11-05.md)
and [diagnostic-probe export](reviewer-probe-export-results-2026-10-30.md): six initial
and six post-revision reviews, with no replacements or additional semantic reviews.
These are ordinary production v61 critic prompts executed in synthetic diagnostic
contexts, not twelve independent stories or durable production reviews. Neither
the historical raw labels nor their normalized versions were treated as gold.

The complete current prose, assignment, boundary and raw review were inspected
for each capture. Whole explanatory fields, exact pointers, source hashes and
original messages remain intact. All **163 fields** retain an inventory disposition:
14 admitted controls, 11 detailed interpretation holds and 138 fields not selected
for authority gold. The latter are not declared true or false. Prior scope-only
admissions are preserved separately; this is not a full accuracy rescore of 163 fields.

Gold here means **identified assistant-authored, prospective judgments**, not blind
human adjudication or automatic semantic certification. Each admitted field has
explicit material components and illustrative evidence locations. Complete sources
remain available; those locations are not an exclusive citation whitelist. The
authority scope is the original visible request plus the catalog-complete current
draft. Locally recovered history and hidden blueprint fields remain provenance,
not retroactive evidence that the critic saw them.

Private evidence: [complete admission record](../../data/diagnostics/reviewer-authority-admission-v61-2026-11-07/admission.md),
[controls and evidence](../../data/diagnostics/reviewer-authority-admission-v61-2026-11-07/controls.json),
[all dispositions](../../data/diagnostics/reviewer-authority-admission-v61-2026-11-07/dispositions.json),
[review inspections](../../data/diagnostics/reviewer-authority-admission-v61-2026-11-07/review-inspections.json),
[readiness](../../data/diagnostics/reviewer-authority-admission-v61-2026-11-07/readiness.json).
Full unpublished prose stays in ignored local data, including twelve exact works
and twelve literal full-context views.

## Admitted controls

| Controls | Whole-field assessment retained | Admission |
| --- | --- | --- |
| P01 | Elara's actual crossing violates the explicit current outside endpoint. | Positive: the criticism is supported. |
| P02–P03 | Revised preparation/decision and outside ending satisfy the named current obligations. | Positive: repair assessment is grounded in current assignment and prose. |
| P04 | Elena's established handwriting match violates the explicit current no-match endpoint. | Positive without needing an inference about the later private flourish. |
| P05–P06 | An explicit unresolved choice fails the decision obligation; the turning-point definition requires realization. | Positive: the actual assignment supports these obligations. |
| P07–P09 | Known R3 Q002/Q003/Q004: realization, corrected date relation and achieved state. | Positive with separate claim-specific evidence obligations. |
| P10 | Known R4 Q003: attributed unresolved choice, current decisive motion/purpose and the required decision. | Positive: attribution and current fulfillment remain distinct. |
| U01–U04 | All four Elara next-scene comparisons assert or rely on a next-scene starting state. | Uncertain under the declared authority reading: the visible next-scene object lacks that field. |

“Positive” describes support for the **reviewer's claim**. P01/P04/P05 criticize
defective drafts; they are not negative authority controls. A negative control
would require a clearly unsupported or contradicted reviewer inference under an
agreed whole-field reading. Relabeling a valid criticism of a bad draft would not
test false criticism.

R3 Q003's prospective obligation covers the historical date-claim attribution,
current dates and actual required date relation. It does not add a separate
realization event. Q002/Q004 and the story assignment still require realization.
The previous frozen gold and **U 52/64; B 63/64** results are unchanged; B remains
unqualified under that run's original gate.

The four uncertain controls are not four proven hallucinations. Their visible
next-scene objects contain identity, turn and outcome, with no starting-state
field. The current ending is inspectable; the claimed starting state is not
established by that authority. A recovered local blueprint cannot retrospectively
resolve this source-availability question. These four closely related fields are
also not four independent generalization samples.

## Why no negative was admitted

The strongest apparent negatives require choosing among materially different
readings. The [eleven holds](../../data/diagnostics/reviewer-authority-admission-v61-2026-11-07/holds.json)
retain the exact fields and reasons:

- A general match allegedly “consumes” or “prematurely satisfies” the private-flourish
  turn. This could concern literal procedure completion or editorial loss of a
  later reveal. The former is not the only reasonable reading of the whole field.
- A “specific decision-making process” can demand extra dramatization; it is not
  interchangeable with whether purposeful action establishes a decision.
- “Incorrectly as today” can mean wrong against the assignment or a character's
  misperception. “Logically flawed” and “preserving the next scene's outcome” also
  mix possible factual and editorial relations.
- Initial knowledge and an instruction are different authority types, even when
  both constrain the intended story. Verification “beginning,” threshold geometry
  and completed preparations also need explicit readings.
- Known R1 Q003's “previous violation” remains held: an attributed repair target
  and a historically established event/violation demand different proof. The
  current assignment cannot silently stand in for the earlier assignment.

Neither ambiguity nor unavailable authority was counted as a negative. No clause
was trimmed, reviewer claim rewritten or authored counterexample passed off as a
saved natural error to complete the desired balance.

## Verification

**242 tests pass: 214 existing assessment-component tests and 28 private admission
tests.** Repository Ruff, formatting and strict mypy pass for 230 Python files;
the same checks pass for all four private helpers. Seven recorded checks pass.
The 56 Pydantic warnings come from existing deliberately unchecked fixtures.
Full-suite/frontend/build checks were not repeated: tracked code, contracts,
dependencies and frontend behavior did not change.

All **450 scope-audit seal members**, **88 authority-integration seal members**
and **304 immutable original capture files** match their hashes. These are separate,
partly overlapping preservation checks, not a count of independent observations.
The older preservation record also names 23 tracked references; three have changed
since that earlier audit through subsequent implementation/documentation work.
Their old/current fingerprints are recorded explicitly, separately from immutable
capture verification. No original saved request, response, gold or score changed.

All **11 historical quotation occurrences across six post-reviews**, comprising
six unique texts, match the supplied old prose. Their offsets and version/critique
links are retained. The actual requests show the old draft as metadata, with the
selected quotations visible; its complete body was recovered locally. Exact copying
does not establish the alleged violation, the authority of a requested repair or
the need for a new edit.

The private checks cover full-field/source preservation, literal full-context
rendering, evidence-binding corruption, missing selectors, source/output mutation,
path containment, the date/realization distinction and refusal to fill the negative
bucket with uncertainty. Semantic gold remains an authored responsibility. The
first recorded run passed 241 tests and failed one new assertion because its
hand-counted immutable-file expectation was 303 rather than 304; the expectation
was corrected and the failed log retained. Earlier helper lint/type invocation
issues were corrected before the recorded passing verification; no historical
evidence or model scoring was changed.

Verification removes provider credentials. New audit/tests deny network and
database access. No inference, input-count, catalog, daemon, credential-store or
application-database action occurred. All fourteen issue bodies remain unchanged.
See [verification](../../data/diagnostics/reviewer-authority-admission-v61-2026-11-07/verification.json)
and [source checks](../../data/diagnostics/reviewer-authority-admission-v61-2026-11-07/source-verification.json).

## Readiness and recommended next step

The component passes its local checks, but **B/H is not ready to freeze using these
reviews**. More supported repetitions would not establish discrimination against
false authority inferences. The missing natural negative is the substantive gap;
the lack of fresh families further limits generalization.

Next, prepare a small **explicitly authored authority-control set locally** across
three fresh scene families. In each packet, keep full context and include supported,
clearly contradicted and unavailable-authority claims. Specify earlier and current
assignments separately, bind historical excerpts to their actual sources and
distinguish a required date relation from a required realization. Make gold and
interpretation reviewable before inference. Retain the saved controls as calibration
evidence, without presenting the authored negatives as natural-error precision.

Only after that local admission passes should we decide whether to freeze an
**authored-mechanism** B/H diagnostic at the proposed 24 attempts: three packets ×
two conditions × two presentation orders × two exact repeats. B would retain the
explicit brief; H would add the provenance/visibility receipt. Whole claims, context,
workload and prospective gold must be equal. Success would be limited evidence
about authority discrimination on those authored cases, not production qualification.
Exact requests, scoring, budget and stops still require a separate freeze and live
approval. This recommendation does not authorize inference or construct new cases.

This protects future story-quality work from unnecessary edits triggered by
unsupported criticism. Factual support, evidence completeness, repair necessity,
prose preservation and craft remain separate. Human review should continue to
focus on feel, flow, character and story-breaking details, with mechanical evidence
provided by the application.

CW-007/CW-013 remain open; CW-014 remains unqualified. No external issue was edited.
**Step 19 IN PROGRESS; Step 20 NOT STARTED; production prompts unchanged;
live calls PAUSED; canary ON HOLD.**
