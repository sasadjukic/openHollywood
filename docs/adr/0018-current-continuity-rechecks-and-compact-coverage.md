# ADR 0018: Current continuity rechecks and compact requirement coverage

- Status: Accepted
- Date: 2026-10-04

## Observed failures

Repeat 3 of the formal v33 Cloud assessment stopped two stories at continuity
response validation. Its original campaign and reviewed evidence remain sealed.
These failures did not establish manuscript defects.

- **OH-V01-002, scene 2, revision 2:** both attempts returned the historical
  `continuity_issue_45120e1ba552c1ab` as a current recheck key. The latest report,
  `4d428e48-683b-430d-b171-fcbaf91b3e25`, had no findings. The older report was
  still supplied for recurrence analysis, and the request listed historical
  blocking IDs alongside guidance to audit prior findings. Exact-key validation
  correctly rejected the stale key, but the request blurred history and current
  obligations.
- **OH-V01-010, scene 2, initial draft:** the first response supplied an absent
  time-context assessment, repair suggestion and explicit empty evidence list,
  but omitted a redundant summary. Materialization reported the error at
  `findings.1.summary`, a canonical output location rather than the model's keyed
  coverage entry. The second response supplied a summary but omitted
  `evidence_refs`. The generic evidence diagnostic could be mistaken for an
  invalid selected reference; the captured entry actually had no reference field.

The source invocations are `0bba9f2421d54207b4ed18f42b1b07d3` and
`672e702000454c1d986ef3c20c3eb0be` for 002, and
`8c21a18099074a1790e5c59f74dda494` and `20fa106d83714c94ab574c39db774cdf`
for 010. Their allowlisted failed-review evidence is explicitly unvalidated.

## Decision

New production requests use **prompt v34 / graph v9**. The writer and critic
instructions, narrative policies, model settings, token/cost budgets, structural
retry allowance, revision cap and mandatory Blueprint approval are unchanged.

### Current versus historical findings

Expose `continuity_recheck.required_prior_finding_ids` from the latest report,
replacing the duplicate historical-ID list. Keep historical reports and exact
artifact lineage for recurrence analysis. Explain that historical findings are
not active recheck keys. Active missing-requirement findings continue through the
separate requirement-coverage route.

When there are no active model findings, omit `prior_finding_rechecks` and its
unused entry definition from the model-facing schema. The application interprets
an omitted empty partition as no decisions; successful audit handling agrees.
An explicitly empty object remains harmless. Supplied stale keys, nulls, malformed
partitions and omitted active keys still fail. No reviewer decision is invented
and no active blocker is silently discarded. New findings remain independently
validated, including current-evidence and recurrence checks.

### Requirement coverage

Ask for one `coverage_assessment`, and use that same model-authored text as the
canonical gap finding's `summary`. Keep the recommended repair mandatory for
partial and absent coverage. Validate missing, blank and wrongly typed text at
its original `requirement_coverage.<id>.<field>` location before materialization.
Met coverage also requires its declared assessment.

Every status still requires an explicit `evidence_refs` list. Met and partial
need valid current-candidate evidence. Absent coverage cites closest passages or
uses `[]` after searching the complete candidate and finding none. Remove the
redundant `evidence_search_result` choice from the response schema. Older echoes
of that selector still cannot contradict the evidence list. Never default a
missing/null list, invent a handle, or substitute canonical-source evidence for
candidate evidence. Existing exact-evidence normalization is unchanged.

Repair guidance now explicitly distinguishes absent coverage with `[]` from an
omitted field, and an empty current recheck set from historical IDs. Repair policy
version is 8. This uses the existing single structural repair allowance.

Advisory versus blocking enforcement is unchanged: absent time context remains
advisory, partial coverage remains advisory, and complete absence of an
application-designated hard requirement remains blocking. This does not change
the model's literary or semantic judgment.

## Compatibility

Canonical artifact and API schemas are unchanged. No database migration,
dependency, UI change or generated client update is needed. Previous invocations,
reports, campaign scores and seals retain their original versions. The tracker
receives a new dated entry; the closed v33 assessment is not rewritten or resumed.

## Verification

All **629 Python tests** pass, including **44 new v34 regression cases**. Ruff
lint and formatting, strict mypy on 166 files, frontend formatting/lint/type checks,
all 11 frontend tests and the production build pass. `git diff --check` is clean.

`tests/api/test_production_v34.py` covers Local and Cloud schema delivery, mixed
historical/current finding sets, omitted empty partitions and successful audits,
rejection of stale/malformed/current-missing partitions, unchanged requirement
gates, exact evidence, and precise coverage failure locations. Migrated SQLite
workflows cover a cleared continuity finding followed by another critic-requested
revision, missing-summary coverage, recovery within two attempts, terminal failure
at the same limit, failed-review isolation and replay without duplicate calls.

Offline reconstruction used the frozen completed Repeat 3 snapshot. Both v33
request hashes exactly matched the recorded invocations; every input artifact's
content hash and the snapshot's before/after hash were verified. On identical
inputs, total message content decreased as follows (characters, not tokens):

| Input | v33 | v34 | System instructions, v33 to v34 |
| --- | ---: | ---: | ---: |
| OH-V01-002 scene 2 revision 2 | 41,436 | 39,997 | 9,477 to 9,437 |
| OH-V01-010 scene 2 initial draft | 40,738 | 40,495 | 7,184 to 7,171 |

Replaying 010's captured review fields reproduces `findings.1.summary` under v33.
Those same fields validate under v34, with the time cue still advisory and the
separate attempted contradiction still blocking. That is a validator check, not
proof that the contradiction is semantically correct or that the story completes.

Local reconstruction scripts, matched requests and results are under
`data/diagnostics/v34-continuity-validation-2026-10-04/`. The source snapshot remains
SHA-256 `71618ce4d66ffd3b8ecc46fa4d034105b4e59aa5a80946b5364272b87caeafb2`.
### Authorized live probes — 2026-10-04

After the initial automatic approval rejection, the user explicitly authorized
sending the frozen story inputs to Ollama Cloud. Both isolated continuity probes
ran at 12:09:53–12:10:04 UTC (14:09:53–14:10:04 Europe/Belgrade). A local import-path
error on the first launch occurred before network access or model inference; it
was corrected in the diagnostic script. The production source was unchanged.

The probes used Ollama 0.35.1, local daemon routing to `gemma4:31b-cloud` / remote
`gemma4:31b`, and the same alias digest recorded for Repeat 3:
`c382fbfbc73b6fdd08c8549c23caedc6e62eb09933c65a1fb82dbf3398320a4e`.
Seeds remained 19204 and 19210, with per-call limits of 24,000 input tokens,
8,000 output tokens and the original USD 0.20 configured ceiling. Actual monetary
cost remains unknown; a numeric zero placeholder is not a billing measurement.

| Frozen input | Response validation | Attempts | Input / output tokens | Provider latency | Retained findings |
| --- | --- | ---: | ---: | ---: | --- |
| OH-V01-002 scene 2 revision 2 | Validated | 1 | 9,642 / 1,069 | 4.596 s | One blocker |
| OH-V01-010 scene 2 initial draft | Validated | 1 | 10,023 / 1,000 | 4.398 s | One blocker, one advisory |

Exactly **two model calls** ran, using **19,665 input / 2,069 output tokens**.
Neither response needed a structural retry. The live request hashes matched the
offline v34 request hashes above; the frozen snapshot's hash remained unchanged.
Requests, manifests, validated reports, response hashes, runtime metadata and
summaries are stored under the local diagnostic directory's `live/` subdirectory.
No writer, adjudicator or full production workflow ran, and no canonical artifact
or campaign result was changed.

### Remaining judgment and recurrence concerns

These are two valid review responses, not two passing scenes or recovered stories.

- **002:** the reviewer again called Elena's repeated handwriting verification a
  blocking contradiction. The latest report's active recheck list was empty, so
  the valid response reached materialization through the new-findings route. The
  existing historical semantic-identity logic assigned the old finding ID and
  `still_blocking` disposition. Consequently the `newly_exposed` changed-evidence
  guard does not apply to that historical recurrence. The stale-key format failure
  is gone in this probe, but the older allegation can still return through this
  separate path. Repeating an investigation can be redundant prose without
  contradicting its earlier occurrence; the selected evidence does not by itself
  establish incompatible facts. This is a remaining judgment/recurrence concern,
  not proof that the scene is sound or would complete the graph.
- **010:** absent time context materialized correctly as advisory, with an
  explicit empty evidence list and a summary derived from the assessment. The
  reviewer separately blocked Elias's claim that no digital back-door remains,
  citing his Blueprint secret about having left one. Its proposed repair asks for
  an explanation of deletion in version 2.0, but the very next supplied sentence
  already says Maya deleted the redundancies in that rollout
  (`draft_evidence_0054`, after cited 0052–0053). This suggests incomplete treatment
  of adjacent counterevidence. The Blueprint's statement that the current system
  flagged the back-door still warrants comparison with the complete scene and
  its timing; structural validation cannot settle that semantic dispute.

The targeted format failures did not recur in these two calls. Broader model
conformance, correct contradiction judgments and full-story recovery remain
unqualified. Preserve these findings for focused continuity-policy analysis
before treating v34 as a demonstrated production-recovery improvement.

Product Step 19 remains IN PROGRESS. These changes do not improve the frozen
34/36 completion record or qualify preference, monetary cost or literary quality.
