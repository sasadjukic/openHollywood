# Exact-copy evidence: local integration design

Date: **2026-10-30**. **COMPLETE — bounded local integration-design pass**;
**production integration is proposed, not installed**. Live calls and daemon
calls: **zero**. Production **prompt 61 / graph 9 / fulfillment policy 1** remain
unchanged. Inference **PAUSED**, full workflow canary **ON HOLD**.

The application can attach a reproducible literal comparison to a saved critic
review while preserving the critic's original judgment. The local prototype now
connects that comparison to actual persisted invocation and artifact records.
It does not determine whether a cited passage fulfills an assignment, choose a
corresponding original passage, or authorize a writer repair.

This completes the scope of the [proposed local pass](reviewer-copy-rendering-next-steps-2026-10-30.md),
following the [copy-display/source-alignment audit](reviewer-copy-rendering-source-alignment-audit-2026-10-30.md).
Private scripts, twelve fixtures, results, SQLite export examples and verification
records are in `data/diagnostics/reviewer-copy-integration-design-v61-2026-10-30/`.
As with earlier diagnostics, this directory is Git-ignored. The implementation
has no production registration, API route, writer connection or model transport.

## Source record and trust boundary

The read-only adapter starts from the exact successful ordinary critic invocation
that created a canonical critique. It requires a validated v61 critique, schema-7
native audit and graph 9. It verifies the critique's content hash and project,
the critique's exact draft target, the input artifact versions and their hashes,
and the unique standalone Scene Plan for that scene. Failed attempts,
adjudications and similarly worded alternative drafts cannot supply the record.

| Record | Bound fields and interpretation |
| --- | --- |
| Invocation | Project, workflow run, invocation ID, role, operation, attempt, task fingerprint, prompt/graph version, prompt hash and provider response-content hash. A response hash identifies bytes; it does not establish their truth. |
| Saved review | Creator's critique version/content hash and complete saved native audit/hash. The original bounded native status, assessment, selected handles and repair advice remain visible and unchanged. |
| Canonical sources | Artifact kind/key, exact version, project, canonical content/hash; current draft and plan pins and scene identity. No lookup of a newer version or similarly worded source. |
| Reviewer view | Exact hash-matched messages; each rendered artifact's content, scope and view hash; exact assignment-contract field. Canonical availability and visibility in the request are separate facts. |
| Selected location | Version, `/turning_point`, `/outcome` or `/prose`, full-field hash, versioned evidence handle where applicable, code-point start/end offsets and exact selected quotation. No quote-only first-match selection. |
| Catalog | Complete request catalog and its hash, plus the pinned local replay implementation's code hash and v61 contract. This code hash identifies the local replayer; it is **not an attestation of the historical runtime binary**, which existing invocation records do not save. |
| Derived export | Snapshot hash, exact selection, comparison rule, source audit/response identities and fixed application wording. No aggregate semantic verdict or manuscript action. |

Existing native-audit and fulfillment provenance is reused. The prototype does
not replace those records with a second model-authored certificate. Canonical
content, the displayed view and selected quotations have separate hashes because
they are different objects. Hashes detect inconsistent state within the existing
trusted local-storage model; they are not signatures against replacement of the
entire database and all corresponding hashes.

### Recovering the saved request without inference

The current executor persists `prompt_text` as joined message content and
`prompt_sha256` over the ordered role/content array. It does not persist that
array directly. Inspection of the v61 ordinary critic renderer confirms a fixed
system/user pair, including structural retries.

For that supported contract only, the adapter considers possible double-newline
boundaries in the saved text and accepts **exactly one** pair whose serialized
role/content hash equals the stored prompt hash. It also checks the joined text.
It does not rebuild the prompt using current instructions. The saved SQLite
examples recover the same messages captured by their fake gateway, including
the successful structural retry's different request.

Missing/truncated text, mismatched hashes, unsupported roles/versions or no unique
match fail explicitly. Recovery is locally bounded to two million characters and
512 candidate boundaries; exceeding these bounds is an unavailable diagnostic
view, never a story defect. The adapter also accepts externally retained messages
only after the same hash/text checks. No model response is generated to fill a gap.

## Eligible comparisons and explicit non-results

1. **Assignment field → critic-selected current evidence.** Use the exact native
   check's anchor and all its selected current-draft handles, retaining their
   order. Display one comparison per excerpt. This compares a field's literal
   text with a selected span; it does not certify semantic correspondence.
2. **Original excerpt → revision excerpt.** Require an explicit independently
   reviewed location mapping. The fixture mapping is authored test input, not
   evidence of a real human review or an automatic alignment capability.
   An unresolved mapping produces `mapping_unresolved` with no literal claim.
3. **Multiple excerpts.** Keep their individual results and sources. Do not
   concatenate excerpts, pick the most favorable result, infer a whole-claim
   match or turn one differing span into an unmet requirement.
4. **Duplicate text.** Full, version-bound catalog replay locates the ordinal
   handle. Quote-only occurrence candidates remain visible. An unversioned
   quote or stale handle is rejected, even when its wording exists elsewhere.
5. **Compacted historical prose.** An explicitly bound older same-scene version
   may be recovered locally. Label it `recovered_after_review`; do not imply the
   critic saw its omitted prose. A missing source remains `unavailable`, with
   no equality result and no fallback to another version.
6. **Conflicting provenance.** Wrong anchor, version, project, scene, field,
   content hash, catalog or view binding prevents the comparison. It neither
   changes the saved critic judgment nor creates a manuscript finding.

The unavailable historical-source fixture retains an already known identity/hash
while withholding its body. It exercises the pure contract. The SQLite adapter
does not reconstruct a deleted database row's authority: missing relational
lineage remains an integrity failure requiring an explicit unavailable outcome
in a future operator interface.

All literal results use exact Unicode code points without normalization. The
statement names the direction and selected scope, for example:

> Assigned requirement → selected current-draft excerpt: The selected text spans
> are identical character for character.

The original saved check may still say **unmet**. That is intentionally allowed:
an exact quotation could belong to another character, be hypothetical, negate an
event elsewhere, or leave a compound requirement unfulfilled. Similarly,
different wording can preserve the assigned meaning. The preserved N8 and fresh
PO/EX contrasts continue to constrain this boundary; their historical scores and
annotations have not changed.

## Twelve-fixture result matrix

Each row runs once with a saved **met** check and once with a saved **unmet**
check. These are authored judgments rendered through current production code,
not fresh model observations or semantic ground truth.

| Source condition | Literal result under both judgments | Required behavior |
| --- | --- | --- |
| Unique selected handle | Exact | Keep source/target identity and the original check. |
| Duplicate occurrences | Exact | Bind the later selected occurrence, not the first matching quote. |
| Multiple selected excerpts | One exact; one different | Show both independently; no aggregate equality. |
| Compacted older prose recoverable locally | Different | Mark recovery after review; preserve the critic's narrower visible scope. |
| Older prose unavailable | Unknown/unavailable | Keep identity and expected hash; no guessed offsets or quotation. |
| Conflicting anchor/field | Rejected | No comparison claim or replacement judgment. |

The pairs hold mechanical results and source availability constant while varying
the saved judgment. Additional negative tests cover stale handles, quote-only
selectors, duplicate/omitted locations, changed catalogs, conflicting source
metadata and prompt recovery failures.

## Persistence, replay and proposed display

The local adapter reads real migrated SQLite records produced by the existing
fake-gateway fulfillment fixture. It does not modify invocation settings,
canonical artifacts, workflow state, prompt text or review judgments. It writes
an explicitly derived JSON sidecar in a separate diagnostic directory.

Closing and reopening the database session reproduces the same snapshot and
export. Repeating an export to the same path requires identical dependencies
and selection; a changed audit, source identity or selection cannot overwrite
it. The retry test rejects the failed critic attempt and uses the exact creator
of the successful critique, preserving the shared input versions and the
successful attempt's distinct prompt and invocation identity. No retry budget
or workflow idempotency policy changes.

The proposed first integration surface is an **operator review export**, described
in the [next-step proposal](reviewer-copy-integration-next-steps-2026-10-30.md).
Show an “Application text comparison” section beside the saved review, with both
source labels, selected quotations and visibility labels. Keep the original
critic assessment, status, advice and link to the complete critique separately
visible. A missing display must not hide the review or block story completion.

Do not insert these statements into writer/critic prompts, substitute them for
the critic's explanation, add an exact-text acceptance gate or grant automatic
repair authority. Future necessary craft edits remain possible in already
fulfilled passages under [ADR 0037](../adr/0037-durable-writer-fulfillment-handoff.md).
No general manuscript editor or additional human checkpoint is proposed.

### Schema, migration and ADR decision

This pass changes no production schema, canonical artifact, API or persistence
format. Its versioned sidecar is an offline diagnostic artifact. A first tracked
read-only exporter can likewise avoid SQL migrations if it remains a derived
external export using existing records. Document that integration with an ADR
extending the review/prose separation and provenance decisions before adoption.

If later work persists application evidence in SQLite or exposes it through the
API/UI, specify its typed, versioned contract first. A new table/column requires
an Alembic migration; any deliberate reuse of versioned invocation JSON needs
an explicit compatibility/replay policy rather than silent historical backfill.
Public API changes require generated client contracts and corresponding client
checks. None of those changes is included or implicitly approved here.

## Verification and limits

**273 offline tests pass: 59 new design checks, 143 preserved audit/execution
checks and 71 existing fulfillment checks.** Ruff lint/format and strict mypy
pass on all eight local scripts. Results and commands are recorded in the private
bundle's `verification.json`. The checks exercise the twelve cases, strict source
and selection binding, message recovery, real SQLite/fake-gateway capture and
replay, and the preserved historical and fulfillment regressions. The final
guard also requires surviving same-scene/older-revision view metadata for an
unavailable historical body; its three negative fixtures pass.

Initial local verification exposed typing issues, corrected within the prototype.
Sandboxed asynchronous fixtures then stalled in Windows' loopback socket-pair
setup before any gateway execution. A faulthandler trace identified that location;
the same SQLite tests passed outside the sandbox restriction. The test harness
blocks real HTTP transports; no provider or daemon check was performed. These
environmental runs do not count as model evidence or completed tests.

The first completed suite found twelve fixture replay failures caused by JSON
object-key ordering in the local message-hash helper; 258 other checks passed.
The helper now uses the production serializer's explicit role/content field
order, independent of file key order. A saved SQLite snapshot also round-trips
through sorted JSON before comparison. The production serializer, saved prompts,
source captures and historical scores were not changed to obtain agreement.

Production/frontend code is unchanged. Verification is scoped to the local
prototype and affected existing regressions; an unrelated frontend production
build is not evidence for this design. The original capture bundle, production
source fingerprints and all fourteen issue bodies are checked unchanged:
**8,904 historical/production fingerprints**, plus the local baseline of **196
production/test Python files**. These inventories overlap and are not added
together. All fourteen posted issue links remain intact; no external issue was
edited or closed.

This establishes local mechanical provenance and replay behavior. It does not
qualify automatic passage selection, model semantic reliability, writer
preservation or story quality. Human review continues to focus on feel, flow,
character and story-breaking problems, with mechanics prepared by the application.
**Step 19 remains IN PROGRESS; Step 20 remains NOT STARTED.**
