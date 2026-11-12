# ADR 0048: October 17 probe contracts for read-only intake

- Status: Accepted
- Date: 2026-11-12
- Extends: ADRs 0039 and 0047.

## Decision

Register the two separately qualified October 17 preparation/live archive pairs.
Select the contract from the exact live-closure SHA-256, then verify its pinned
plan, preparation closure, all evidence members and operator evidence. No caller
may supply new trust pins through the CLI or intake plan. Existing bounds and
read-only publication rules continue to apply. These are local integrity seals,
not provider-signed attestations.

Support is limited to seven already-audited ordinary-review IDs, listed in the
[qualification report](../handoffs/oct17-intake-qualification-2026-11-12.md).
Do not admit the archives' judgment-only arms, other seeds or writer responses as
ordinary reviews. Writer records are authenticated lineage dependencies only.
The original October 16 contract and receipt requirements remain supported.

## Explicit format differences

The contrasts plan uses `case_sha256` and `prepared_sha256`. Its manifests include
null `writer_source_policy`; its receipts retain response length and terminal
finish reason. Its selected four reviews are ordinary initial critics.

The adjudication/edits plan uses `file_sha256`. Its saved sent-request records
are complete request snapshots and must equal the reservation-bound request.
Its receipts omit response length and finish reason. Require those fields absent
for this format; authenticate raw content hashes, reservation/receipt attempt,
returned outcome, token counts, and the model capture's `stop` finish reason.
Do not invent omitted receipt metadata or relax the October 16/contrasts checks.

Separate typed manifests represent the ordinary craft-source critic and E0/E1
writer/post records. Only the writer E1 dependency permits `exact_edits` projection;
all admitted critics require ordinary production semantics. Exact prepared initial,
craft and writer requests must match their actual saved requests.

## Cross-archive lineage and edit materialization

Both admitted post-reviews descend from the contrasts archive's
`s19201-elara-embedded-initial`. Authenticate that entire parent snapshot under its
own contract and retain it as separately namespaced operator provenance. Require
the writer's input prefix to equal the parent's full inputs, its critique body and
identity to match the normalized parent receipt, and the post-review to consume
the exact writer inputs plus the materialized revision.

Preserve the historically inherited identities: the critique UUID uses the
October 16 experiment namespace; the revised draft UUID uses the contrasts
namespace. Both remain content-derived. Retagging the experiment did not retag
these input versions. No canonical production creator or assessment identity is
inferred from these synthetic diagnostic identities.

E0's raw draft must equal its saved materialization. For E1, reproduce the literal
edit protocol locally: exact base version/hash, at most 64 ordered nonoverlapping
original ranges, one-based occurrence selection including overlapping matches,
exact replacement/deletion text, code-point and UTF-8 byte offsets, full resulting
draft and saved edit audit. No archived Python code is executed. This proves the
saved transformation, not edit necessity, preservation quality or semantic repair.

Protect both the selected preparation/live pair and external parent pair from
export destinations. Re-collect original sources at publication; exact output
reuse verifies bytes without writing. The external snapshot cannot become a
critic-visible evidence location merely because it is available to the operator.

## Intake and limits

Replay N06–N12 with their existing whole fields, declarations, briefs and holds.
Only derived IDs and location references are rebound to the current inventory.
Prior gold stays outside pending work. Full messages, current prose, whole report
and unselected fields remain available; recovered history stays separately labeled.
Ambiguous, mixed and editorial fields remain held under ADR 0047.

This qualification makes no new semantic judgment, live request, database change,
writer permission, workflow integration or production prompt change. Step 19 remains
IN PROGRESS; Step 20 NOT STARTED; live calls PAUSED; canary ON HOLD. Natural-negative,
fresh-family, necessary-edit and story-quality evidence gaps remain open.
