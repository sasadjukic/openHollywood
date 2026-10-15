# Fulfillment evidence handoff: production integration examination

Date: 2026-10-15. Status: **EXAMINATION COMPLETE; IMPLEMENTATION NOT STARTED.**

Baseline: `fbd726c48643950d39163d541836726e47d29b64`, production prompt **v59**,
graph **v9**. This is a proposal, not an accepted ADR or an implemented feature.
Production, the failed-clause critic diagnostic, the tested writer projection,
canonical stories and sealed results remain unchanged. No model calls were made.

## Recommendation

Add one optional, version-bound fulfillment packet to the existing writer revision
contract. Derive it from the successful invocation that created the task's exact
previous Critique. Carry only native `turning_point` and `outcome` checks marked
`met`, their assessments and exact current-draft excerpts. Preserve the tested
policy, including permission to edit a cited passage when it contains a defect.

The existing storage can support this without a new agent, model call, graph node,
canonical artifact field, database column, public API or dependency. The necessary
work is a validated reader, a bounded projection, and durable request binding.
Simply copying a positive assessment into the prompt would omit the last safeguard.

Keep all mandatory repair tests, continuity feedback, independent craft findings,
revision limits and acceptance gates. A positive assessment is fallible review
evidence, not canon, a waiver of another defect or an automatic acceptance rule.
Do not change v59's meaning of `met`, classify a partially fulfilled requirement as
met, or convert an end-state obligation into an event obligation in this handoff.

## What production already provides

The following locations refer to the baseline commit above.

| Location | Available behavior | Integration implication |
| --- | --- | --- |
| `engine/open_hollywood_engine/workflows/production_graph.py`, `_draft_node` | Passes exact previous draft and Critique references, bounded history, current Bible and approved assignment. | Select `task.previous_critique`; do not search for the newest review by timestamp. |
| `apps/api/open_hollywood_api/services/production_model_executor.py`, `_complete_invocation` | Persists the Critique, success status, validation flag and `scene_boundary_audit` in one transaction. | A failed response cannot supply the packet. Follow the Critique's creator invocation. |
| Same file, `_scene_boundary_audit` | Schema 7 retains candidate/plan version IDs and both native checks, including status, bounded assessment and exact evidence handles. | No new critic output field is needed. Historical `revision_acceptance_audit` is a different source and is excluded. |
| `apps/api/open_hollywood_api/persistence/models.py`, `ArtifactVersion` / `AgentInvocation` | Immutable artifact content and hashes; creator/input relationships; JSON invocation settings and stored prompt. | Existing lineage can resolve the exact review context. Invocation settings themselves lack the artifact immutability guard. |
| Executor, `_critic_evidence_catalog` | Deterministic excerpts with the complete draft-version suffix in each handle. | Resolve the stored handles against the exact reviewed draft; never search for similar prose. |
| Executor, `_load_execution`, `_replay`, `_start_invocation` | Fingerprint inputs before request execution; replay successful calls; persist prompt/settings before the gateway call. | Add handoff identity before fingerprint/retry lookup and persist the selected snapshot before sending. |
| Executor, `_targeted_revision_contract`, `_messages` | Builds writer acceptance tests and repair ledger; first drafts have no revision contract. | Add one optional field here for WRITE revisions only. |

The saved audit does **not** repeat the full assigned requirement or evidence
excerpt. Load those from the source invocation's immutable Scene Plan and draft.
The successful provider response has a stored hash, but production does not retain
its complete raw body in this path. Do not require diagnostic capture files or
reparse raw responses to build the production packet. The trusted starting point
is the successful, validated application transaction and its artifact lineage.

## Proposed eligibility and validation

Run these checks inside the executor's existing input-loading session, before
choosing the writer fingerprint and retry context. Use normal typed validation,
not the diagnostic builder's Python assertions.

1. **Select the exact task inputs.** Only WRITE with revision greater than zero is
   eligible. Use `previous_critique` and `previous_draft`, not a convenient older
   review or the last database row. Confirm their presence in resolved inputs and
   agreement with the revision contract's immediate review. The draft must belong
   to this project and scene and have revision `writer_revision - 1`.
2. **Resolve the creator.** Follow `Critique.created_by_invocation_id`. Require the
   same workflow run/project, ordinary `critique` operation, `scene_critic` role,
   `SUCCEEDED`, `schema_validation_succeeded is True`, and that exact output
   version. Exclude failed captures, adjudication output, imported diagnostics and
   historical repair checks. For the first implementation, explicitly support the
   ordinary v59/schema-7 source contract; add future compatible versions deliberately.
3. **Bind the draft.** The Critique target and audit `candidate_version_id` must
   equal the task's previous draft version, also present in the creator's input
   relationship. Validate artifact kinds, keys, project membership, scene identity
   and canonical content hashes. Identical prose under a different version is not
   an identity match.
4. **Bind the complete assignment and shared authority.** The audit's current plan
   must be the exact standalone Scene Plan input to both creator and writer. Check
   its scene ID/number and content hash. Reconstruct the source assignment and
   compare it exactly with the writer's assignment, including exit state; copy
   each requirement's exact text into the packet. Also require matching approved
   Blueprint, Story Bible and accepted prior-scene version sets between source
   review and writer. Compare these named shared inputs, not the complete lists:
   writers legitimately have additional character/context and feedback artifacts.
   The same frozen workflow run supplies the benchmark constraints. A changed
   Blueprint/Bible can change an obligation's interpretation even if its sentence
   is unchanged. Do not attempt semantic equivalence across versions.
5. **Validate native coverage.** Require exactly the currently populated native
   anchors and the supported audit shape. Validate both `met` and `unmet` records;
   emit only whole checks marked `met`, with null repair advice. Do not infer
   fulfillment from a pass verdict, score, no-overrun status, satisfied historical
   complaint, or a met clause inside an unmet compound requirement.
6. **Resolve evidence exactly.** Rebuild the critic catalog at the reviewed draft's
   revision, not the writer's upcoming revision. Require one to three distinct
   current handles per check. Resolve complete excerpts without paraphrasing,
   trimming away defects, or choosing alternative passages. Verify version suffix,
   catalog membership and exact excerpt identity. Preserve the stored redacted
   assessment, bounded to 600 characters; do not expand it from raw response text.
7. **Apply bounded, secret-safe projection.** At most two fulfillment records. Use
   the normal secret guard before persistence and model submission. A credential
   failure remains a security error; do not silently redact an exact quotation and
   label the changed text an exact excerpt. Propose a 16,384-byte cap on the complete
   optional model-facing packet. If it exceeds the cap, omit it as a whole and
   record the reason; never truncate its evidence or remove mandatory feedback to
   make room. This new cap requires local boundary tests before implementation is
   considered complete.

For unavailable, unsupported, stale or malformed optional audit data, omit the
**whole packet** with a machine-readable reason and retain the ordinary revision
context. Do not salvage another check from a malformed audit or fall back to an
older positive review. Valid audits with no met checks produce an explicit
`no_met_requirements` omission. Existing invalid-task/lineage errors still fail as
they do now; this optional reader must not catch and suppress them.

Ordinary continuity-only revisions can receive the packet if their immediate
Critique passes these checks. A first draft cannot. Terminal critic adjudication
does not trigger another writer in the current graph and is not a new evidence
source for this feature.

## Packet and unchanged writer policy

Retain the tested model-facing field:

```text
revision_contract.latest_fulfilled_requirements
  source_critique_version_id
  reviewed_draft_version_id
  source_response_sha256
  scene_id
  policy
  requirements[]
    requirement: turning_point | outcome
    assigned_requirement: exact text
    assignment_source_version_id: exact Scene Plan version
    status: met
    assessment: validated saved assessment
    evidence[]: { evidence_ref, exact_excerpt }
```

Carry the tested policy verbatim:

> These are the latest critic's findings about this exact draft, not new canon.
> Preserve the existing expression in the cited passages when repairing unrelated
> defects; do not add explicit restatement just to emphasize fulfillment. If a
> cited passage itself needs change to repair another supplied defect, make that
> necessary repair. Requirements absent here are not certified met: satisfy all
> acceptance tests, including any genuinely unmet requirement.

Do not add this packet to critic, continuity or adjudication messages. A cited
passage containing both a valid decision and a forbidden match stays intact in the
packet: its flaw must remain visible, and the writer may edit it to retain the
decision while removing the match. Preservation is not an exact-text acceptance
gate. Mandatory tests continue to determine what the revision must repair.

## Durable binding and replay

Keep application-only provenance outside the model-facing packet. Record a
versioned `writer_fulfillment_handoff` entry in writer invocation settings with:

- Included/omitted status and bounded reason code.
- Source invocation, Critique, draft and plan identities, shared authority version
  IDs/content hashes, source response hash and source audit digest when available.
- The complete packet actually used, its canonical digest, and handoff policy
  version. For omission, persist an explicit null packet.
- A stable logical writer-task key and the final task fingerprint.

The logical key uses the existing task dependencies, run, operation, unit,
revision, profile, seed and versioned handoff policy. The final fingerprint also
includes the selected handoff snapshot digest. A response hash identifies the
source response; it does not independently prove the saved audit's semantics or
allow reconstruction of an unavailable response body.

On the first attempt, resolve and validate the source, then persist the snapshot
with `_start_invocation` before calling the gateway. On structural retry or
resume, locate the existing snapshot by the same logical key **before rebuilding
evidence from mutable metadata**. Reuse its included/omitted decision, validate its
digest and exact artifact dependencies, and feed the same final fingerprint into
the existing retry/replay machinery. Only the ordinary retry instructions change.

Conflicting snapshots, corruption or a changed source audit must not silently
produce a new task identity, extra retry allowance or duplicate successful writer
call. Surface an integrity error before another call. Source metadata is not an
instruction to rewrite an already pinned packet. Existing invocation failure,
cancellation and worker lease behavior remains in place; test these paths using
real SQLite and a fake gateway.

Use additive versioned JSON metadata, following existing invocation-audit practice;
no persisted table or canonical artifact schema change is proposed. A future
implementation must version the changed writer request explicitly and qualify
its compatibility with frozen-run/replay behavior. Do not silently ship different
writer messages under the old request identity. No version constant changes in
this examination, and no graph-version change is required for the proposed flow.

Keep current call, token and cost budgets. The packet adds input tokens even
though it adds no calls. Existing UTF-8-byte token estimates are diagnostic only,
not exact preflight token accounting. Measure request composition and actual usage;
do not enlarge the budget or trim the source draft/required repairs for this feature.

## Small implementation sequence, if subsequently requested

1. Add a small service-local typed projection/validation helper and tests. Keep
   provider types and database access out of its pure projection logic. Port the
   tested policy; do not import files from ignored diagnostic directories.
2. Connect the exact Critique creator lookup, input checks and snapshot selection
   in `_load_execution`. Carry the selected handoff in `_Execution`, include it in
   fingerprinting, persist it in `_start_invocation`, and render the optional field
   through `_targeted_revision_contract`. Leave critic construction/materialization
   and the failed-clause diagnostic untouched.
3. Verify the durable path locally before spending on new stories. Record an ADR
   for the implemented decision and update the tracker only when the slice passes.
   Implementation and model qualification are separate completion claims.
4. Qualify the handoff with ordinary production-v59 critic semantics in a small
   gated comparison. Include separate overrun, defect inside a cited passage,
   missing decision, and missing date-plus-realization cases. If native reviews
   incorrectly mark a fulfilled event unmet, record that limitation; do not import
   the diagnostic or manufacture a met packet to make the writer test proceed.
   Freeze any new live matrix, payloads and budget before requesting authorization.

Minimum local coverage before promotion:

| Area | Required checks |
| --- | --- |
| Exact binding | Wrong draft version even with identical prose; wrong revision/scene/run/project; changed plan ID or content; changed exit state, Blueprint, Bible or accepted prior scenes; hash mismatch. |
| Source eligibility | Missing creator/audit, failed first attempt followed by validated retry, unsupported audit, adjudication, latest review superseding older met findings, absent anchor, zero met checks, partially fulfilled compound requirement. |
| Evidence/policy | Stale/invented/duplicate handles; malformed second check causes whole-packet omission; exact full compound excerpt; secret guard; byte-cap boundary; no fabricated evidence or extra requirement. |
| Request isolation | Only WRITE revisions receive the addition; all mandatory tests/ledger entries survive; first drafts and critic messages/schema retain their existing behavior; diagnostic fields never enter production. |
| Durability | Real SQLite creator/input resolution and atomic audit visibility; persist before gateway; exact prompt/packet hashes; bounded retries and cancellation/resume; successful replay causes no duplicate call; metadata changes cannot reset retry identity. |
| Repair behavior | Missing decision and complete date-plus-realization still repaired; indirect decision preserved; separate and embedded overruns removed; distinguish valid paraphrase from deletion-only edits and unnecessary restatement. |

For an implementation, run applicable Python Ruff/format, strict mypy, unit,
integration and workflow checks documented in the root README. Confirm public API
schemas are unchanged. Run the production build before handing off the code;
frontend checks apply if their inputs change. No application tests/build are claimed
for this documentation-only examination. Full-story tests are unnecessary for the
reader/provenance checks, but later full runs and human review remain necessary for
Step 19 acceptance and any claim about general story quality.

## Evidence inspected and limits

Read the production execution, graph, persistence, secret-guard and obligation
paths above, the product contract, memory architecture and relevant accepted ADRs
0004, 0005, 0013, 0014, 0033 and 0036. The existing graph already passes the needed
references; the handoff does not need a new workflow stage.

A read-only inspection of the sealed
[preservation-exception experiment](../benchmark_reports/writer-preservation-exception-v59-2026-10-15.md)
checked all twelve validated critic receipts: 22 native met checks and two unmet
checks retain the same status, assessment and evidence handles in the saved audit.
The failed first attempt was excluded. Reconstructing the four evidence-assisted
writer packets from those audits, exact assignment text and catalogs reproduced
all six fulfillment records exactly. Packet sizes were 1,504, 2,171, 1,488 and
2,210 UTF-8 bytes. These measurements support storage/projection feasibility;
they are not a production-database integration test or a universal size bound.

All 288 files in that experiment's closure and its report hash were verified
unchanged. No private prose was copied into this design. Raw captured responses
were used only for this offline comparison, not proposed as a runtime dependency.

The recent OH-V01-002 successes used explicit event wording and the separate
failed-clause critic diagnostic. They demonstrate useful preservation and a working
necessary-edit exception in that matrix; they do not establish ordinary v59 critic
reliability. Both writer arms repaired the embedded defect, and neither was
clause-only. The supported benefit is restraint in some edits, not guaranteed
minimal editing or improved literary quality. Exact source validation establishes
traceability, not semantic correctness.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.** The next proposed action
is the local reader/projection and durable-binding slice, not a critic change or
an immediate full-story campaign.
