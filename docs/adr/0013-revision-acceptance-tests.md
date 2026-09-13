# ADR 0013: Version-bound acceptance tests for scene revisions

- Status: Accepted
- Date: 2026-09-13

## Context

The v29 OH-V01-007 revision loop changed small phrases while its critic kept
rejecting the scene. The writer received the preceding critique, but the critic
reviewing the new draft received no earlier critique. It could not explicitly
recheck the original repair target. Rejected review-format responses must still
remain separate from manuscript defects (ADR 0008).

Step 3 gives revisions a specific acceptance test without adding calls, retries,
revision cycles, adjudicators or longer instruction blocks.

## Decision

New runs use prompt v31 / graph v8. The graph passes the current scene's earlier
critique references to both writer and critic. The history is bounded by the
existing revision count and selected from the graph's completed critique history;
it does not include another scene's reviews. The application resolves every
review's exact target draft into invocation lineage before fingerprinting.

Build repair tests from canonical blocking issues and major issues on a revise
verdict. Each test identifies the source critique version, source draft version,
issue index, severity, original claim and cited evidence, requested change, and
a category-specific acceptance condition. For POV, qualifying a statement is
neither proof of repair nor proof of a continuing violation; context and approved
narrative permission remain decisive. Assignment tests reference the approved
obligation; craft tests address the original weakness and intended repair effect.

Writer and critic receive the same tests. Prior reviews remain allegations,
not new canon. The original wording and evidence stay frozen. Exact repeated
category/severity/claim/repair text across reviews reuses the first test; separate
original issues remain separate, and severity changes cannot disappear through
deduplication. No fuzzy matching or automated semantic equivalence is attempted.
A newly worded allegation may still require a new test; critic calibration is
not solved by this mechanism.

On a revision with these tests, the critic supplies one keyed repair_checks
entry per test: met/unmet, an assessment and one to three distinct current-draft
evidence references. Application validation rejects missing/invented tests,
empty assessments and stale/invalid evidence. Unmet tests materialize the
original issue with current evidence and its original severity and force revise.
Thus a perfect craft score cannot clear an unresolved blocking repair. A met
test cannot override an independent current blocker.

There is no text-difference acceptance heuristic. An unchanged passage may
already satisfy the condition if the earlier allegation was unsupported.
Conversely, changing words does not establish repair. Model assessments remain
fallible; the application verifies structure and provenance, not literary truth.

## Context and diagnostics

Replace duplicated historical review prose with the compact test packet.
Keep the writer's immediate prior draft complete and retain advisory feedback
without turning it into a hard repair gate. Preserve the critic's complete
current draft. On revision, the critic receives previous accepted-scene
identities and the canonical Bible instead of duplicating earlier scene prose;
continuity review retains its existing inputs. An exact duplicate scene-plan
projection is omitted only when the standalone plan supplies the same values.

A shared schema definition avoids repeating the repair-check structure.
On repair-bearing critic calls, omit application-owned target artifact fields
from the response schema; the application still binds those IDs. Canonical
Critique artifacts remain unchanged. No SQL migration or generated API contract
change is required.

Successful invocation diagnostics retain the tests, exact candidate version,
statuses, current evidence handles and redacted assessments. Failed checks use
step 1's bounded review-failure capture. Neither successful audit metadata nor
failed response text is copied into story canon or retry instructions.

The isolated probe tool can explicitly restore preceding review/draft versions
missing from historical critic requests. It verifies same run/scene, revision
order, persisted output, target lineage and content hashes, and records expanded
input provenance separately. Probe success and failure exports retain repair
diagnostics. Source canary databases remain read-only.

## Verification and rollout

Offline tests cover shared targets, original evidence, stable repeated tests,
severity escalation, stale references, incomplete rechecks, independent hard
blockers, advisory preservation, secret redaction, exact SQLite lineage, existing
repair/revision limits and replay. Existing continuity and viewpoint controls
remain in the regression suite.

Instruction text shrank from 638 to 586 characters for the writer and from
3,887 to 3,848 for the critic. Three matched Cloud probe requests were shorter
than their v30 equivalents: 007 revision 1, 56,010 to 44,887 characters;
006 revision 1, 73,405 to 52,045; 009 scene 2, 44,242 to 44,203.
These are measured message sizes for those inputs, not a universal token bound.

Four isolated Cloud calls covered those three scenes, including one repeat of
007 to verify the successful-repair export. All validated and returned pass on
the first attempt of each probe. 007 (both probes) and 009 retained non-blocking notes; 006 had no issues.
The repeated 007 repair assessment reported met, but overcredited wording already
present in the original. Preserve that reasoning limitation rather than treating
the pass as proof of correct adjudication.

Evidence is under data/diagnostics/v31-step3-cloud-2026-09-13/. These are frozen
scene-review probes, not fresh writer runs, full-story completions or a new
canary score. No claim is made that the three failed stories are now solved.
Further manual production tests remain necessary. Critic adjudication and
continuity-policy work remain steps 4 and 5.

