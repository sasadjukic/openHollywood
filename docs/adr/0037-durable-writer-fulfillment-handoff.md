# ADR 0037: Durable writer fulfillment evidence

- Status: Accepted
- Date: 2026-10-16
- Extends: ADR 0013's revision contract and ADR 0033's native assignment audit.

## Context

The fulfillment experiments support preservation of some already successful prose
while repairing a supplied defect. Their strongest transfer results used a separate
diagnostic critic and synthetic event wording. They do not establish ordinary critic
reliability or improved literary quality. The October 15
[design examination](../handoffs/fulfillment-evidence-production-design-2026-10-15.md)
identified an existing successful critic audit as a possible production source.

The writer needs the exact current review's evidence, including defects inside a
cited passage. Rebuilding that packet from mutable invocation settings on every
retry could change the request fingerprint, reset failure history, or duplicate a
completed call. Copying only a positive assessment into a prompt is insufficient.

## Decision

New production runs use prompt contract **61**, graph **9**, and handoff policy **1**.
Version 60 already identifies a historical, withdrawn writer-guidance experiment;
its identity is not reused. Only WRITE revisions receive the optional
`revision_contract.latest_fulfilled_requirements` field. First drafts receive no
packet. Critics, continuity reviewers and adjudicators receive no fulfillment packet.
Their instructions, output schemas, interpretation of `met`, and acceptance gates
are unchanged. The new run version also appears in existing invocation and
continuity-contract version labels.

The service-local reader follows `task.previous_critique` to its creator, requiring
an ordinary successful, schema-validated scene critic in the same project and run.
Supported sources are explicitly prompt 59 or 61 with scene-boundary audit schema 7.
Failed captures, adjudication and historical repair audits are not sources. A failed
critic attempt can supply no output; its successful retry's exact creator can.

Validate the immediate review, previous draft revision and scene, artifact keys,
canonical content hashes, exact standalone Scene Plan and its complete assignment,
approved Blueprint, current Bible, and accepted prior-scene version sets. Additional
writer character/context inputs do not have to equal the critic's full input list.
The frozen run supplies benchmark constraints. Same prose under another version is
not interchangeable evidence.

Validate both native anchors, including unmet records; emit only complete checks
marked `met`. Each record retains exact assigned text, the saved bounded assessment,
and one to three distinct excerpts from the reviewed draft's original evidence
catalog. There is no partial certification of an unmet compound requirement and no
inference from score, verdict, satisfied historical complaint or boundary status.
The pure projection imports neither database nor provider types.

Retain the tested policy verbatim, including permission to repair a defect inside
a cited passage. All mandatory repair tests, continuity feedback, independent craft
findings, revision limits and acceptance gates remain effective. Fulfillment is
fallible review evidence, not canon or an exact-text preservation gate.

Missing, unsupported, stale or malformed optional source data omits the whole
packet with a bounded reason. No older review or valid fragment rescues it. A valid
audit without met checks records `no_met_requirements`. Invalid writer task/lineage
errors still fail. Credential detection raises the existing security error; exact
quotations are never silently redacted. Check secrets before the size limit.
The complete compact JSON packet is capped at **16,384 UTF-8 bytes**, inclusive.
Larger packets are omitted whole as `packet_too_large`; source prose and mandatory
feedback are never trimmed to make room. Byte size is not exact token accounting.

## Persistence, retry and recovery

Use additive versioned JSON in `AgentInvocation.request_settings`, with no table,
canonical artifact or public API schema change. Persist `writer_fulfillment_handoff`
and the redundant `writer_logical_task_key` alongside the existing prompt and hash
before the gateway is called. The snapshot records:

- Included/omitted decision, reason, exact packet or explicit null, and packet digest.
- Source invocation, critique, draft and plan identities; dependency identities,
  content hashes and shared authority; source response and audit digests.
- Schema/policy versions, logical key, snapshot digest and final task fingerprint.

The logical key binds the existing run/operation/role/unit/revision/input/profile/
seed/request-version fingerprint and handoff policy. The final fingerprint also
binds the selected snapshot digest. A response hash identifies response bytes; it
does not prove the saved judgment's semantic correctness or recover an absent body.

Look up an existing snapshot before projecting evidence. On retry, restart or
successful replay, verify its hashes, dependencies, source state and identical
copies across attempts, then reuse it. An omitted packet is pinned too. Changed
source audits, missing/corrupt/conflicting snapshots and fingerprint mismatches
raise an integrity error rather than creating a new request or retry allowance.

Recheck dependencies and source state after the invocation insert acquires SQLite's
write lock, within the same transaction as prompt/snapshot persistence. Reject a
second start if that logical task is already running or successful. The transaction
also checks the current failure count so a stale prepared attempt cannot bypass a
newly recorded failure. It rolls back on an integrity failure, before a gateway
call. Existing worker ownership,
cancellation cleanup, interruption reconciliation and graph retry limits still apply.
A recovered interrupted call retains its snapshot and the existing distinction
between an unknown provider outcome and a structured-response failure.

These digests detect inconsistent state under the application's existing storage
trust model. They are not signatures against an attacker who can rewrite the entire
database and recompute all hashes.

## Frozen-run compatibility and rollback

Persist `production_prompt_template_version` in new production-run input state and
carry the same value through the graph checkpoint and executor. Reject unsupported
or disagreeing run/checkpoint versions before inference. The executor supports 59
and 61; it uses the frozen version for messages, invocation identity, retry lookup
and fingerprint construction instead of the current module constant.

Existing run inputs without the new field retain the v59 path; no handoff fields
are retrofitted into those requests or invocations. Existing v59 checkpoints must
agree. Earlier incompatible checkpoints require their matching historical runtime;
they are not silently upgraded. Completed results and sealed historical evidence
are not rewritten. New v61 critics deliberately remain eligible schema-7 sources.

Rollback is a code/runtime rollback, not removal or editing of persisted snapshots.
Finish or pause v61 runs before selecting an older runtime; resume them with a
compatible v61 runtime. The older service's exact handoff-input comparison rejects
the added v61 run field. Never remove that field to force an old runtime to proceed.
No database downgrade or canonical-artifact migration is needed.

## Qualification and subsequent quality work

Local verification is reported in the implementation tracker. Real SQLite/fake
gateway tests cover exact lineage, malformed/omitted evidence, native coverage,
UTF-8 boundaries, security, persistence-before-submission, retries, cancellation,
interruption recovery, replay, concurrent starts and metadata changes. Existing
workflow, worker and quality checks remain required. These fixtures establish
application behavior, not model repair success or literary truth.

Live qualification remains a separate task using ordinary production critic
semantics and a frozen, authorized comparison. Record eligibility failures rather
than importing the failed-clause diagnostic or forcing a met classification.
Keep the implementation fixed during that comparison.

Future story-quality work must retain independent craft feedback and the necessary
edit exception. A fulfilled passage may still need improved voice, dialogue,
characterization or pacing. Smaller diffs and exact preservation are diagnostics,
not literary quality scores. Subsequent improvements need blind human comparisons,
the accepted rubric and a stable baseline. **Step 19 remains IN PROGRESS; Step 20
is NOT STARTED.** No new calls, token/cost allowances, specialist roles, graph nodes,
dependencies, UI controls or additional human story checkpoints are introduced.
