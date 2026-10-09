# Worker cancellation cleanup and critic v42

Date: 2026-10-09. Production contract v42 / graph v9.

**Both worker failures have reproduced causes and local fixes, and all 758 Python
tests pass. The approved v42 diagnostic improves satisfied-repair formatting and
independent-turn reporting, but exposes two remaining reporting problems.** Four
of five probes validate; the unchanged-draft control fails both permitted
attempts. Reviewer reliability remains unqualified.

## Worker failure: cause and correction

The [v41 report](linked-repair-findings-v41-2026-10-09.md) records two final full
Python runs with 737 passes and one failure: an invocation remained RUNNING after
worker shutdown. This follow-up reproduces the race by delaying the existing
cancellation database write, rather than treating a passing rerun as a fix.

The local trace showed this order before the correction:

1. Worker stop began and the specialist started its cancellation cleanup.
2. The graph wrapper and worker stop returned before that cleanup completed.
3. Repeated cancellation interrupted the cleanup await while its database
   thread continued running.

The application now tracks the actual specialist tasks within each graph call.
On failure or cancellation it drains those tasks before allowing the workflow
service to close. The Blueprint and production executors shield and join their
cancellation persistence across repeated cancellation. Cleanup errors propagate;
the worker does not silently report a successful stop when that cleanup fails.
After the fix the delayed trace finishes persistence before stop returns.

Regression tests gate cleanup explicitly, cancel again, assert shutdown remains
pending, then release the write and verify terminal invocation state and no
outputs. They retain operator-stop and restart checks. Separate tests cover the
real production service, early-returning graph wrappers, failure propagation,
and isolation from a concurrently running workflow. No delay is added to
production. See [ADR 0026](../adr/0026-durable-worker-cancellation-cleanup.md).

A subsequent full run passed the cancellation assertions but failed while
recording an operator STOP: `database is locked` at the control-command insert.
The command service performed that synchronous write on the event loop, blocking
an asynchronous checkpoint transaction from committing and releasing its lock.
A controlled SQLite regression reproduced the same insertion failure before the
correction. The four generic control-store mutations (pause, stop, budget update,
resume) now run in worker threads. Cancel/wake callbacks still execute on the
event loop after commit. Four real-lock tests verify progress, callback ordering
and command idempotency. No production timeout increase or lock retry is added.

This proves the tested orderly-cancellation path. Abrupt process termination
still depends on durable recovery; protection at every database boundary and
all providers is not claimed.

## Critic contract

The v41 linked-finding mechanism remains intact. v42 changes its shared repair
check schema to status-specific alternatives. A `met` check allows only `[]` for
`current_finding_refs`; an `unmet` check retains the existing link contract.
Invalid model responses are still rejected, never repaired by silently clearing
links.

The critic must assess the fixed original claim separately from other defects.
Each independent assignment failure requires its own finding, evidence and
repair. A missing turn must be reported through `assignment_violations`, including
when an outcome repair is already unmet. Mentioning it only in a boundary
comparison or repair assessment creates no writer task.

Persisted integration tests show that a separately reported turn receives a new
source-bound repair ID and reaches both the next writer and critic, while the
original test remains unchanged. Tests cover the original repair being either
met or unmet. Assessment prose alone is deliberately not parsed into defects.
See [ADR 0027](../adr/0027-satisfied-repair-schema-and-independent-findings.md).

The instructions remain within the existing 3,887-character limit. Against the
five frozen v41 requests, system messages grow by 7 characters and inline schema
messages by 1,056 characters each. Story artifacts, context, current evidence,
original repair tests, settings and budgets remain identical. There are no new
roles, model calls, retries, canonical fields or migrations.

## Local verification

**All final local gates pass:** 758 Python tests, Ruff lint/format, strict mypy
over 177 files, frontend format/lint/type checks, 11 frontend tests and the
production build. The Python suite includes 20 new regression cases relative to
v41. The 17 focused worker/cancellation/control cases also pass.

During development, a full run passed 753 of 754 tests and failed the critic
instruction-size guard. Compacting the wording then required updating two
existing literal wording assertions; the size limit and substantive assignment
policy remain unchanged. After those corrections, a full run had 753 passes and
the separate SQLite stop failure described above. The final 758-test pass follows
its reproduced cause and correction, not an unchanged rerun to hide the failure.

Six saved v41 raw responses were replayed without annotations. All four valid
responses produce exactly the same canonical critiques; both invalid attempts
for repair 19102 still fail with the same validation error. This is an offline
compatibility check, not new model evidence.

## Approved five-case comparison

The experiment reuses the exact v41 private OH-V01-002 inputs: the unchanged
draft, three saved writer revisions, and the synthetic missing-turn control.
Standard story context and the synthetic explicit no-match endpoint remain.
The approved canonical Blueprint and stories are not edited.

| Case | Predeclared expectation |
|---|---|
| Unchanged draft, 19102 | REVISE; two original obligations retained once each, with valid links |
| Saved repair 19102 | Valid PASS with satisfied original checks and empty links |
| Saved repair 19103 | PASS with its original outcome repair met |
| Saved repair 19104 | Inspect the ambiguous handwriting-match/authorship judgment; no forced verdict |
| Missing-turn control, 19103 | Original outcome repair met; missing future-date turn reported independently with a new repair target |

The user explicitly approved five critic probes, at most ten calls: one initial call
and at most one structural retry per case. No writer calls, semantic rerolls,
second revisions or full-story generation are included. Recorded October 8
rates of USD 0.14/M input and USD 0.40/M output, with 24,000 input / 8,000 output
tokens per call, give a maximum estimate of **USD 0.06560**. Actual charges remain
unknown. The destination is the existing Ollama Cloud Gemma4 deployment reached
through the user's local Ollama daemon.

## Live results

| Case | Calls | Valid final result | Observation |
|---|---:|---|---|
| Unchanged draft, 19102 | 2 | None | Both attempts link an outcome finding to the original tension repair; validation rejects them |
| Saved repair 19102 | 1 | PASS | Both original repairs met with empty links; v41 failed this case twice |
| Saved repair 19103 | 1 | PASS | Original outcome met, empty links, no issues |
| Saved repair 19104 | 1 | PASS | Same verdict as v41; match/authorship ambiguity remains |
| Missing-turn control, 19103 | 1 | REVISE | Original outcome met; a separate turn finding is emitted, plus a duplicate generic plot blocker |

The six calls use **72,298 input / 6,296 output tokens**, estimated at **USD
0.01264012** using the recorded rates, within the approved USD 0.06560 allocation.
Actual charges remain unknown. There were no writer calls or full-story runs.

### Satisfied repairs: observed improvement

Repair 19102 now validates on its first call with both checks met and both link
lists empty. All met checks in the four valid reviews have empty links. This
supports the status-specific schema on these cases, not a general reliability
claim across seeds or models.

### Missing turn: independently reported, but duplicated

Unlike v41, the critic keeps the original handwriting-outcome repair met and
reports the removed future-date realization through
`assignment_violations[turning_point]`, citing the current-day date. That creates
the intended new assignment repair target. However, it also emits a blocking
generic `plot` issue for the same missing future date. Both survive correctly
under the existing rules: v40 consolidates boundary/assignment overlap, while
v41 consolidates explicit links to historical repairs. Neither rule establishes
equivalence between a new generic craft issue and a new assignment issue.

Offline reconstruction therefore produces **two new repair targets**, one
`plot` and one `scene_assignment:turning_point`, beside the unchanged original
test. Detection and separation from the old outcome improve, but one defect is
still reported twice. No live writer consumed this new critique.

### Unchanged control: wrong original-repair link

The raw reviews identify the overrun and propose REVISE, but neither is accepted.
Both original checks are unmet. The original `dramatic_tension` / `major` repair
links to `assignment:outcome`, a `scene_assignment:outcome` / `blocking` finding.
The outcome repair also claims that same finding along with `boundary`. This
violates category/severity compatibility and single ownership. The bounded
structural retry repeats the error. A failed review is not a valid manuscript
rejection and does not count as a successful negative control.

As an explicitly labeled offline diagnosis, removing only the invalid tension
link lets each saved attempt materialize as REVISE with exactly the two original
repair tests retained. The unmet tension repair needs no current link when no
separate current tension finding exists. This isolates the rejected link; it is
not a model-generated correction. Raw failures and production validation remain
unchanged. Silently clearing links in production is not the proposed fix.

### Ambiguous repair: still unresolved

Repair 19104 passes again. Its review says the draft no longer asserts an
identical match, while its selected evidence includes: "At a glance, they seemed
identical, but the very perfection of the match sparked a new suspicion."
The qualified appearance and uncertainty about authorship still require careful
interpretation. The review again invokes preserving a more specific later
verification. Its PASS is recorded without treating that disputed interpretation
as proof of correct endpoint enforcement.

## Evidence and reproducibility

Requests, code, source evidence and database hashes are frozen in the ignored
private directory `data/diagnostics/satisfied-repair-v42-2026-10-09/`:

- `experiment.py`, `plan.json`, `prepared/*.json`: reconstructable bounded plan.
- `offline-replays.json`: six unchanged old-response outcomes.
- `local-verification.json`: final local gate and source-hash record.
- `live/`: all six exact requests, raw responses, validation results and audits.
- `assessment.json`: reconstruction of every request, response and repair target.
- `link-diagnosis.json`: explicitly manual counterfactuals; live failures remain failed.

Source database: the completed v33 repeat-3 snapshot, SHA-256
`71618ce4d66ffd3b8ecc46fa4d034105b4e59aa5a80946b5364272b87caeafb2`.
Source commit is `23a64b47257775c82fa7e1dbb0c9bc2591dcd53c`; candidate file hashes
identify the uncommitted v42 implementation. Every valid and failed response
replays exactly, including rejection evidence and the structural retry request.
Original repair lineage, the source database and prior evidence remain unchanged.

## Remaining work

The next narrow protocol target is to constrain link choices to findings
compatible with each original repair's category and severity, while retaining
single-ownership validation. Separately, assignment failures need one reporting
route so they are not copied into generic craft issues. Avoid fuzzy deletion or
silently accepting malformed links. Qualify those changes with the same controls
before a full-story campaign. Match-versus-authorship interpretation remains open.

This small, one-model sample evaluates two coordinated contract changes, not
their individual causal contributions. It cannot establish full-story recovery
or general story quality. Technical repeatability, human preference and cost
acceptance remain open. **Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**
