# Assignment versus craft claim comparison: v45

Date: 2026-10-10. Production contract v45 / graph v9.

**Implementation, local verification and the five approved live probes are
complete. All 829 Python tests and final quality gates pass. Four probes produced
valid reviews; the unchanged control failed both attempts.** Live semantic
performance is not qualified. See
[ADR 0030](../adr/0030-explicit-assignment-and-craft-comparison.md).

## Problem and change

The [v44 campaign](restatement-retries-v44-2026-10-10.md) showed that correcting
references can produce a structurally valid review with duplicate repair work.
The ambiguous revision's major `Plot Pacing` issue repeated the early-verification
allegation already covered by its original blocking outcome repair.

The existing critic now must compare each generic issue with its current reported
assignment findings. For independent craft, the question is: after minimally
repairing the assignment breach, what distinct evidence-backed craft defect still
needs correction? Category, severity and shared quotations do not decide this.
An automatic consequence of the same breach is insufficient. The comparison is
required even when the answer is that there are no current assignment findings.

A declared repetition can consolidate at any severity. The validated assignment
finding keeps its blocking severity; the audit retains the source issue's actual
severity. Descriptions, advice and resolved evidence are retained. A separately
explained craft claim keeps its own issue, even with the same passage or category.
Separate historical repair IDs remain separate in either case.

The new wire field contains selected current finding references and a nonblank
assessment of at most 1,000 characters. Independent claims must cover every
distinct reported assignment finding; one alias of a consolidated finding is
enough. Repetitions must include their selected target. Invalid coverage rejects
the review; the application never supplies an interpretation automatically.

Audit schema 3 retains these comparisons outside canonical story artifacts.
Structural retry policy 12 provides bounded current finding groups and static
comparison instructions, excluding rejected review prose. No writer changes,
new specialists, calls, retries, dependencies, canonical fields or migrations
are introduced. System instructions and story context are unchanged.

## Local verification

The 23 new regression cases exercise all four severities, independent criticism
with shared evidence, coverage of consolidated and separate findings, malformed
or missing comparisons, preserved original repair identities, audit redaction
and exclusion of comparison prose from retries.

Two persisted workflow cases retain the original repair identity and send exactly
one new assignment repair plus one separate craft repair to the next writer and
critic. They cover both met and unmet original obligations. These are simulated
review judgments, not proof that a model can distinguish the claims reliably.

The v43/v44/v45 focused group passes all 71 cases. The first full run reports
828 passes and one old v40 fixture missing the newly required comparison of its
combined craft/viewpoint/assignment findings. That fixture now explicitly supplies
the comparison; no production validator was weakened. The final full run passes
all **829 tests** in 168.66 seconds. Ruff lint/format and strict mypy over 182
files pass. Frontend formatting, lint, types, all 11 tests and the production
build pass. The frontend tests ran alone and passed on their first invocation.

## Saved-response replay and labeled counterfactuals

All eight raw v44 responses are replayed without edits:

| Saved response | v45 offline result |
|---|---|
| Unchanged draft, attempts 1 and 2 | Rejected; missing route and invalid reference remain real failures |
| Repair 19102, attempt 1 | Rejected for invalid evidence handles |
| Repair 19102, attempt 2 | Identical canonical PASS |
| Repair 19103 | Identical canonical PASS |
| Repair 19104, attempt 1 | Rejected for invalid restatement reference |
| Repair 19104, attempt 2 | Rejected because the previously valid generic issue lacks the new comparison |
| Missing-turn control | Identical canonical REVISE with one new turn repair |

Two explicitly edited copies of repair 19104's second response test the mechanics:

- Declare its major pacing issue a repetition of the outcome claim and explain
  equivalence: one canonical original repair, zero new repair targets.
- Replace that issue with a synthetic independent criticism of abstract emotional
  phrasing, explain why it survives an assignment correction, and keep null:
  original outcome repair plus one independent craft repair.

The second copy changes the allegation as well as its metadata. Neither copy is
a model response or evidence that the critic would make this judgment. No source
response or canonical story is changed. The handwriting-match ambiguity itself
remains unresolved.

## Frozen live comparison

The same five cases are frozen with identical private inputs, seeds, settings,
budgets and system messages. Only the generic issue schema changes in initial
requests, adding **1,242 characters** to each. Conditional retries use policy 12.

| Case | Predeclared observation |
|---|---|
| Unchanged draft | Valid REVISE retaining both original repair identities once each |
| Repair 19102 | Valid PASS, original checks met with empty links |
| Repair 19103 | Valid PASS, original check met with empty links |
| Repair 19104 | No forced verdict; if it reports the same endpoint allegation twice, inspect comparison and consolidation; retain independently justified craft |
| Missing-turn control | Valid REVISE with original outcome met and exactly one new turn repair |

At most ten calls are permitted: five initial critic calls and one structural
retry per case. Each call is bounded at 24,000 input and 8,000 output tokens.
At recorded October 8 rates of USD 0.14/M input and USD 0.40/M output, the maximum
estimate is **USD 0.06560**. Actual charges are unknown. Destination: existing
Ollama Cloud Gemma4 through the local Ollama daemon. No writer, full-story,
semantic reroll or extra revision is included.

The user explicitly approved the revised private payload set: "Yes, run the five
v45 probes". The fixed campaign is complete; no additional sampling or writer
calls occurred.

## Live results

| Case | Calls | Final result | Assessment |
|---|---:|---|---|
| Unchanged draft | 2 | Failed validation | First response declared repetition but used a string comparison; retry changed its judgment and omitted comparison references |
| Repair 19102 | 1 | PASS; zero issues | Both original repairs met |
| Repair 19103 | 1 | PASS; zero issues | Original outcome met |
| Repair 19104 | 1 | PASS; zero issues | Ambiguous prose interpreted as inconclusive again; no generic comparison exercised |
| Missing-turn control | 1 | REVISE; two new repair targets | Correct missing-turn finding plus an additional, questionable outcome complaint |

The **six calls** used **75,950 input tokens and 6,581 output tokens**, estimated
at **USD 0.0132654** using the recorded October 8 rates. This is within the
ten-call / USD 0.06560 allowance. Actual charges remain unknown. Every exact
request was reconstructed, valid and failed responses replayed, invocation audit
evidence reproduced, and original repair lineage verified. Frozen code, inputs,
prior evidence and the source database are unchanged.

### Recognition changed during structural repair

The unchanged draft's first response selected `assignment:outcome` for its major
tension complaint. Its comparison explicitly called the complaint a direct
consequence of establishing the match too early. This is evidence that the model
can recognize the repeated claim under the new instructions. However, it supplied
the comparison as a bare string instead of the required reference/assessment
object, and omitted the boundary link from the original outcome repair.

The retry received both the precise comparison group and the missing original
repair route. It corrected the boundary link and returned a comparison object.
It also changed the generic complaint to independent craft with null and claimed
that emotional skepticism differed from the plot endpoint. It left
`finding_refs=[]` despite the reported outcome finding, so the response failed
coverage validation. The explanation distinguishes labels/effects without
identifying what separate defect survives a minimal endpoint correction. This
does not establish successful semantic discrimination.

Two additional labeled offline counterfactuals isolate the consequences:

- Wrap the first response's existing comparison text, select its already-declared
  target, and add the missing boundary link: valid REVISE with the two original
  repair identities and no new target.
- Add only comparison coverage to the second response, preserving its declared
  independence and empty original craft link: valid REVISE with three issues and
  one new craft target. Its `Dramatic Tension` category differs from the original
  `dramatic_tension`, and the application does not guess or rewrite that link.

These edited copies are not live successes or production repairs. They demonstrate
why merely correcting references would not necessarily remove duplicate work.

### Additional outcome complaint in the missing-turn control

The original outcome repair remains met and the critic correctly identifies the
missing future-date revelation. It also creates an outcome violation, arguing
that an inconclusive verification attempt lacks a forward-looking decision to
verify further. Its recommendation is to end with a decision to conduct a more
rigorous verification.

An exact-text comparison confirms that the journal comparison and attempted
replication passage is identical to the accepted revision 19103. All noncandidate
artifacts and settings match; the synthetic draft changes only date-related text.
The critic accepted the verification as satisfying the outcome in one context
and objected to the same action in the other. The extra complaint appears to
demand a more explicit future step than the planned decision plus unestablished
match, and therefore warrants false-positive investigation. This is contextual
judgment variation, not proof that the date change caused a specific reasoning
failure. The new target is distinct from the old premature-match allegation, so
category-only consolidation would be inappropriate.

All four valid live responses have empty generic issue arrays. Consequently, this
campaign does not demonstrate a successfully validated live claim comparison or
cross-severity consolidation. Repair 19104's return to PASS also cannot establish
that the v44 duplication was fixed: the model no longer alleged the underlying
endpoint defect in that response.

### Recommended next slice

First address the boundary between structural repair and re-deciding claim
identity. The first unchanged response recognized repetition; the metadata retry
changed that classification and still failed. Evaluate a simpler comparison
shape and precise repair guidance that preserves already valid reference choices
without treating rejected explanatory prose as story truth. Use these two saved
responses locally before another live campaign. Do not automatically repair or
accept either saved failure, merge original obligations, or expand retry limits.

Track the missing-turn control's extra outcome complaint separately. A controlled
check of decision-to-investigate versus an inconclusive investigation is warranted;
this assignment judgment is outside the generic craft comparison mechanism.
Full-story generation should wait for more reliable review behavior.

## Evidence and limits

Private diagnostics remain under ignored
`data/diagnostics/claim-comparison-v45-2026-10-10/`: `experiment.py`, `plan.json`,
five `prepared/*.json` requests, `offline-replays.json`, `local-verification.json`,
`approval.json`, six request/raw response/result records under `live/`, `assess.py`,
`assessment.json`, `diagnose.py`, `live-diagnosis.json` and `postcheck.json`.
The local verification record retains its pre-live permission status; approval
and postcheck records capture the subsequent authorized campaign. Source commit:
`944d889ac31fb9be9d83e3a8978aabd6186c8382`. The plan freezes exact candidate code,
requests and prior evidence. Archived source reconstruction adds explicitly
synthetic comparison metadata only while replaying old source reviews; strict
validation is restored before current probes, and their canonical inputs are
asserted identical to the v44 frozen inputs.

The completed v33 repeat-3 source database retains SHA-256
`71618ce4d66ffd3b8ecc46fa4d034105b4e59aa5a80946b5364272b87caeafb2`.
Canonical stories, Blueprints, sealed benchmarks and prior diagnostic evidence
remain unchanged.

Explicit comparison improves inspectability and provides a way to declare
nonblocking repetitions. It does not establish semantic equivalence mechanically.
A model can still provide a weak explanation, omit a defect or combine distinct
claims incorrectly. The completed five-case campaign has one model and one seed
per case and no independent-craft positive control in live prose; local synthetic
controls alone cannot qualify model sensitivity. It is not a causal ablation,
full-story recovery test or literary-quality evaluation. The valid-review count
remains four of five. Six calls rather than v44's eight do not establish a cost or
reliability improvement, and the missing-turn control gained an extra repair.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**
