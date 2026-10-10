# Independent craft repair links v47: 2026-10-10

Implementation, required local quality checks and three approved live retry probes
are complete. All three exclude consolidated complaints from separate craft links;
two reviews fully validate. One still returns a malformed comparison. Step 19
remains IN PROGRESS; Step 20 is NOT STARTED.

## Change

The v46 retries preserved classification but all selected `issue:0` as a separate
historical craft link after declaring that complaint an assignment repetition.
Consolidation removed the separate finding, making the selected link invalid.

V47 puts the craft repair ID on the independent issue itself. A schema alternative
requires a null assignment-repetition reference and exact matching original craft
category/severity before offering the ID. Repetitions and independent new defects
omit `repair_test_id` or use null. Original craft checks always use empty
`current_finding_refs`; they can remain unmet and actionable without any link.
Native assignment links remain available on their original checks.

Runtime validation rejects legacy index links and invalid ownership, then translates
valid explicit ownership into internal routes for existing original-repair
materialization. It does not silently clear bad links. Original repair IDs,
evidence validation and classification retention remain intact. See
[ADR 0032](../adr/0032-independent-craft-owns-original-repair-links.md).

## Local verification

- 22 new regressions cover independent links in both delivery modes, forbidden
  repetition links, exact labels and IDs, met checks, malformed issues/evidence,
  legacy-route rejection, ordering, distinct same-category defects, multiple
  reports of one original, redacted failure capture and audit provenance.
- A persisted workflow includes both independent craft and an assignment
  repetition. It passes the same two original tests to the next writer and critic,
  with no duplicate repair or additional writer call.
- Existing tests are updated for the new wire representation while retaining
  their canonical-result and malformed-field assertions.
- All three saved v46 model responses remain rejected for the legacy craft link.
  The validator does not manufacture successes by dropping those links.
- In labeled copies, changing only that link to `[]` reproduces each prior v46
  counterfactual's canonical result: the same two original repairs and no new target.

Offline corrections are not live model successes. The v46 campaign remains three
failed reviews. The first full-suite run caught eight instances of the same
generic-versus-bound schema mismatch; both builders now expose the new wire field
consistently, and all 11 tests in that module pass.

Final quality gates passed:

- Ruff lint and formatting; strict mypy across 186 Python files.
- Full Python suite: 884 passed in 173.64 seconds.
- Frontend formatting, ESLint, TypeScript, 11 tests and production build.
- Frozen diagnostic code, source evidence, requests and source database verified.

## Diagnostic campaign

Repeat v46's three controlled retries at seeds 19102, 19103 and 19104, using the
same saved v45 first rejection, private OH-V01-002 unchanged draft and synthetic
explicit endpoint. Do not regenerate the first review or grant another retry.

Exact artifact contents, generation settings, call budgets, system message and
retained classification choices match v46. Only the output schema and structural
retry guidance change. The model-facing user packet grows by 1,832 characters per
request. The source first-response allegation is not replayed as rejected prose.

Expected observations:

- Retain the declared assignment repetition and valid comparison.
- Complete both native boundary/outcome links for the original outcome repair.
- Keep the original craft check's links empty, without moving a craft ID onto
  the consolidated repetition or changing its classification to make linking legal.
- Return a valid REVISE review with both original repair IDs and no duplicate target.

The three-call limit is **USD 0.01968** at the recorded October 8 rates of USD
0.14/M input and USD 0.40/M output, with 24,000 input / 8,000 output tokens maximum
per call. Actual charges remain unknown. Destination: the existing Ollama Cloud
`gemma4:31b-cloud` deployment through the local daemon. No writer, full-story or
canonical changes are included.

Private frozen requests, hashes, source replay and runnable harness are under
`data/diagnostics/independent-repair-links-v47-2026-10-10/` (ignored by Git).
The source database remains read-only with SHA-256
`71618ce4d66ffd3b8ecc46fa4d034105b4e59aa5a80946b5364272b87caeafb2`.

This is one saved failure and one model. Fixed seeds do not guarantee provider
determinism. Positive independent-craft tests are local simulations, not live
sensitivity evidence. Even complete structural recovery would not establish
broader reviewer accuracy, full-story recovery, human preference or cost acceptance.

## Results

The user explicitly approved the three revised requests. Exactly three calls ran;
there were no further retries or writer calls. Frozen requests, source evidence,
response hashes and source database were verified after execution and local replay.

| Observation | Result |
| --- | --- |
| Retained original classification and metadata | 3/3 |
| Original craft check uses empty links | 3/3 |
| Consolidated complaint omits its craft ID or uses null | 3/3 |
| Original outcome repair includes boundary and outcome links | 3/3 |
| Fully validated REVISE reviews | **2/3** |
| Valid reviews retain both original repairs, with no new targets | 2/2 |
| Comparison returned as a string instead of an object | 1/3 |

Seeds 19102 and 19104 validate. Their generic tension complaints remain classified
as assignment repetitions and have `repair_test_id=null`. The original tension
checks stay unmet with empty links. After consolidation, both original repair IDs
and exact original repair tests remain, with no additional target.

Seed 19103 makes the same valid link and classification choices, omitting the
optional craft ID. It fails because `assignment_comparison` is plain text instead
of the required object containing `assessment` and `finding_refs`. This is the
same representation error present in the saved v45 first response. It was absent
from the three v46 retries; this small sample does not establish why it recurred.

Manual inspection shows all three still describe definitive handwriting
confirmation as prematurely resolving skepticism. All explain the complaint as
a consequence of the same endpoint breach. The synthetic endpoint explicitly
forbids establishing a match, and the cited draft evidence declares one. There is
no observed switch to an independent craft allegation to obtain a link. This
supports the narrow classification result without proving broader semantic
accuracy or requiring the two distinct original obligations to be merged.

A labeled offline copy of seed 19103 changes only `assignment_comparison`: its
existing text becomes `assessment`, and its existing `assignment_finding_ref`
becomes the sole `finding_refs` member. That copy validates with exactly the same
two original tests and zero new targets. The actual live response remains failed;
the application does not perform this correction automatically.

Usage: **43,074 input / 4,184 output tokens**, estimated **USD 0.00770396** at the
recorded October 8 rates, below the approved USD 0.01968 maximum. The provider's
numeric zero cost has an unknown cost basis and does not establish zero charges.
Actual charges remain unknown. No production code changed during or after this
campaign; all listed local checks still apply. Canonical stories and sealed
benchmark results remain unchanged.

## Remaining work

The next focused change should make the comparison retry directive state the exact
required object shape alongside its semantic instructions. The current output
schema already requires both fields, but the targeted directive chiefly explains
how to compare claims and covers references without restating the object shape.
This is an identifiable instruction gap to test, not proof of the model's internal
reason for returning text. Preserve classification, link restrictions, strict
validation and the existing retry allowance; do not silently wrap model prose or
give this failed review another live attempt.

Keep the missing-turn control's separate decision-to-verify complaint open.
Full-story recovery, human preference and cost acceptance remain unqualified.
