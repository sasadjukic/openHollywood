# Eligible original repair links and assignment restatements: v43

Date: 2026-10-10. Production contract v43 / graph v9.

**All local gates pass. The approved five-case diagnostic removes the duplicate
missing-turn repair on its control, but the unchanged-draft control still fails
both attempts with different protocol errors.** Four probes validate in six
calls. Reviewer reliability remains unqualified; no writer calls or full-story
runs have occurred.

## Changes

The [v42 diagnostic](worker-cleanup-critic-v42-2026-10-09.md) identified two
different problems. Its unchanged control linked a blocking outcome finding to
a major tension repair on both attempts, causing structural rejection. Its
missing-turn control reported the new assignment defect twice, creating both a
plot repair and a turning-point repair.

v43 narrows each original repair's schema choices before inference. Blocking
assignment repairs receive only applicable routes for their exact category;
craft repairs receive only generic issue-index links. Boundary eligibility uses
the same outcome/turning-point mapping as materialization. Inapplicable assignment
anchors and incompatible assignment severity allow only empty links. Category
and severity groups share definitions to avoid copying a schema per repair ID.

The schema still requires empty links for met checks and explicitly permits an
unmet repair with no repeated current finding to use empty links. Actual current
finding existence, category/severity compatibility, single ownership and complete
consolidated-route linking remain application checks. Invalid responses are not
made valid by deleting their bad links.

Generic issues now have a required `assignment_finding_ref`: `null` for an
independent craft issue, or the explicit current assignment report they repeat.
All issues and evidence validate before consolidation. A declared blocking
restatement combines into its reported blocking assignment target, preserving
both descriptions, all distinct evidence and both repair recommendations. The
target receives one repair identity. Independent issues remain separate even
when they share evidence or categories.

A removed generic repetition cannot serve as an issue-index alias for a
historical craft repair. Historical assignment links use their native routes.
Original repair IDs, claims and requested changes remain fixed; linked current
wording is preserved in the existing revision audit. The boundary audit also
records a bounded, redacted list of declared generic repetitions, including on
initial reviews. Rejected-response evidence retains the new wire reference.
See [ADR 0028](../adr/0028-eligible-repair-links-and-assignment-restatements.md).

These are response schema and materialization changes. Writer and critic system
instructions, story context, budgets, retry limits and canonical artifact schema
are unchanged. There is no new role, inference call, dependency or migration.

## Local verification

The 26 new regression cases cover schema grouping and route eligibility,
assignment/viewpoint/boundary restatements, malformed and unreported references,
evidence validation, retained independent defects and secret redaction. Persisted
workflow tests prove that one consolidated turn repair reaches both the next
writer and critic, with the historical outcome repair either met or unmet.

All final local gates pass: **784 Python tests**, Ruff lint/format, strict mypy
over 178 files, frontend format/lint/type checks, 11 frontend tests and the
production build. During development, an
initial full run passed 772 tests and failed 12 existing fixture assertions: eight
assumed that assignment binding never narrows issue schema choices, and four
used a shared generic-issue fixture without the new required field. Those
fixtures now reflect the v43 protocol; production validation remains strict.

## Saved evidence: replay versus manual annotation

All six exact v42 raw responses are tested without changing them:

| Saved response | Unchanged replay under v43 |
|---|---|
| Unchanged draft, both attempts | Same category/severity link rejection |
| Repair 19102 | Identical canonical PASS |
| Repair 19103 | Identical canonical PASS |
| Repair 19104 | Identical canonical PASS; semantic ambiguity remains |
| Missing-turn control | Rejected because its old generic issue lacks the new required field |

The last result is a deliberate wire-version incompatibility. Existing canonical
artifacts are unchanged. Separate, explicitly manual annotations establish the
following mechanical behavior:

- Clearing only the tension repair's invalid link in each unchanged-draft
  response yields REVISE with exactly the two original repairs retained. This
  repeats the v42 offline diagnosis; the real v42 responses remain failures.
- Adding `assignment_finding_ref: null` to the old missing-turn generic issue
  reproduces its canonical two-issue result and two new repair targets exactly.
- Instead declaring `assignment:turning_point` combines those reports into one
  turn finding and one new repair target. Both descriptions, advice and all
  evidence survive; the original outcome test remains unchanged.

These annotations are not model results. They show neither automatic semantic
deduplication nor successful v43 inference. Reconstructing the frozen source
cases uses null wire metadata only while replaying archived initial reviews,
then restores strict materialization before producing any new request. Exact
canonical inputs are asserted equal to the frozen v42 requests.

## Approved five-case comparison

| Case | Predeclared observation |
|---|---|
| Unchanged draft, 19102 | Valid REVISE with two original repairs once each; tension uses empty links when no compatible craft finding repeats it |
| Saved repair 19102 | Valid PASS, original repairs met with empty links |
| Saved repair 19103 | Valid PASS, original outcome met with empty links |
| Saved repair 19104 | Inspect the match/authorship interpretation without forcing a verdict |
| Missing-turn control, 19103 | Original outcome met; one independent turn repair, including any explicitly declared generic repetition |

All five retain the same private OH-V01-002 artifacts, synthetic explicit
endpoint, seeds, settings and budgets as v42. Standard story context remains.
Canonical Blueprints, stories and sealed benchmarks are untouched. Comparing
the serialized user messages after substituting only the old output schema
establishes that no other payload content changed. System messages are identical.
User-message growth is 2,344 characters for the two cases with outcome and
tension repair categories, and 378 for each of the three outcome-only cases.

The user explicitly approved five critic probes, at most ten calls: one initial
call and one structural retry per case. It includes no writer calls, semantic
rerolls, second revisions or full-story generation. At the recorded October 8
rates of USD 0.14/M input and USD 0.40/M output, 24,000 input / 8,000 output
tokens per call give a maximum estimate of **USD 0.06560**. Actual charges remain
unknown. Destination: the existing Ollama Cloud Gemma4 deployment through the
local Ollama daemon. The fixed campaign stopped after the five cases; no semantic
rerolls or further live calls were made.

## Live results

| Case | Calls | Valid final result | Observation |
|---|---:|---|---|
| Unchanged draft, 19102 | 2 | None | Invalid generic assignment reference on both attempts; additional severity, route-coverage and category errors are isolated offline |
| Saved repair 19102 | 1 | PASS | Both original repairs met, empty links, no new issues |
| Saved repair 19103 | 1 | PASS | Original outcome met, empty links, no new issues |
| Saved repair 19104 | 1 | PASS | Empty met links; match/authorship ambiguity remains |
| Missing-turn control, 19103 | 1 | REVISE | Original outcome met; one turn finding and exactly one new repair target |

The six calls use **73,892 input / 6,363 output tokens**, estimated at **USD
0.01289008** using the recorded rates, within the approved USD 0.06560 allocation.
Actual charges remain unknown.

### Missing turn: one independently reported repair

The critic reports the removed future-date realization only through
`assignment_violations[turning_point]`; its generic `issues` array is empty.
The original handwriting-outcome repair stays met with empty links. Offline
reconstruction produces one new turn repair, compared with v42's two.

This is an observed improvement in reporting on the fixed control. The model
avoids the repetition, so this live result does not exercise the new non-null
restatement consolidation path. That path is covered by local tests and the
explicitly annotated replay. The raw verdict is `reject`; the existing hard
assignment materializer produces canonical `revise`, as before this change.

### Unchanged draft: the earlier wrong link is gone, but the review still fails

Both responses use `issue:0` for the original tension repair and
`assignment:outcome` for the outcome repair. The v42 tension-to-outcome link does
not recur. However, both generic major tension issues supply
`assignment_finding_ref: "outcome"`, which is not an eligible reference. Existing
validation rejects both attempts. Neither raw REVISE counts as an accepted
negative-control result.

Further errors sit behind that first rejection. Explicit manual counterfactuals
isolate them without changing production code or the saved raw responses:

1. Replacing only `outcome` with the valid `assignment:outcome` reference still
   fails: the generic issue has `major` severity while the assignment is
   `blocking`. The repetition contract requires both to be blocking.
2. Setting the reference to `null` preserves it as craft. Attempt 1 then fails
   because its original outcome repair links only `assignment:outcome`, omitting
   `boundary` from the consolidated finding. Adding both routes yields a valid
   REVISE with exactly the two original repairs and no new targets.
3. Attempt 2 also changes the craft category from `dramatic_tension` to
   `dramatic tension`. With null reference and complete outcome routes it still
   fails exact category validation. Manually restoring the original category
   then yields the same two-original-repair result.

These are diagnostic annotations, not model-generated repairs. They show that
the remaining failure is not merely a missing reference prefix. The model must
also distinguish independent craft from assignment repetition, preserve exact
category identity and cover all native routes when linking a consolidated
finding. The bounded structural retry does not resolve these errors.

### Saved revisions and interpretation limits

Repairs 19102 and 19103 pass with evidence that handwriting verification remains
inconclusive. Their met checks have empty links. Repair 19104 also passes, citing
the passage that says the hands seem identical while their match sparks a new
suspicion. Its assessment treats uncertainty about authenticity as evidence that
no definitive match is established, and its boundary comparison again mentions
the later, more specific verification. This interpretation remains disputed;
the PASS is recorded without claiming correct endpoint enforcement.

## Evidence and remaining work

Private evidence is saved under the ignored directory
`data/diagnostics/eligible-repair-v43-2026-10-10/`: `experiment.py`, `plan.json`,
`prepared/*.json`, `offline-replays.json`, `annotated-replays.json`,
`local-verification.json`, all six captures under `live/`, `assessment.json`,
`link-diagnosis.json` and `postcheck.json`. The plan
freezes exact code, source evidence and request hashes. Source commit:
`49b6e90c22084aff449e075282d15c042553f400`. Candidate file hashes identify the
uncommitted implementation.

The completed v33 repeat-3 source database retains SHA-256
`71618ce4d66ffd3b8ecc46fa4d034105b4e59aa5a80946b5364272b87caeafb2`.
Every exact request, valid/failed response, validation result and audit has been
reconstructed offline. Original repair lineage and prior evidence are unchanged.

Link eligibility is an application fact; equivalence between allegations remains
a model judgment. Undeclared repetitions can survive, and falsely declared
equivalence can combine different claims. Preserving their wording and evidence
makes this inspectable but does not prove correctness. Historical duplicate
repair IDs are not retrospectively merged.

The next narrow protocol work should make generic restatement choices conditional
on severity, so a nonblocking craft issue can choose only null, and give the
existing structural retry concrete allowed references, exact original category
and missing consolidated routes. Do not silently rename categories, clear links
or accept incomplete ownership. The unchanged control must validate before
claiming this protocol qualified or launching a broader story campaign.

This is a small one-model sample of two coordinated changes, not a causal
ablation or qualification of general reviewer reliability. The new required
field introduces the observed first rejection on the unchanged control even as
the missing-turn reporting improves. Match-versus-authorship ambiguity remains open.
Broader technical repeatability, full-story recovery, preference and cost
acceptance remain outstanding. **Step 19 remains IN PROGRESS; Step 20 is NOT
STARTED.**
