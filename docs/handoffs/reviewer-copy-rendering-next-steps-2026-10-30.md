# Proposed next steps after the copy-display and source-alignment audit

Date: **2026-10-30**. **PROPOSAL ONLY.** No new live experiment, requests, model
budget or production integration is frozen or authorized by this document.
Production prompts remain unchanged; inference **PAUSED**, canary **ON HOLD**.

**Do not run another PO/EX comparison now.** The
[local audit](reviewer-copy-rendering-source-alignment-audit-2026-10-30.md) shows
that the application can compute and display explicit text comparisons without
inference. Both reviewer arms already passed the authored semantic contrasts,
and the live control reproduced no definite precision error. Another identical
repeat has no demonstrated production decision to resolve.

The recommended next task is a bounded **local integration-design pass with zero
model calls**, keeping the implementation outside production until its admission
contract is reviewable.

1. **Specify the source record at the saved invocation boundary.** Bind project,
   scene, draft and plan versions, exact field/handle/offset, canonical content,
   catalog-generation version and actual rendered-view hash. Record whether the
   source was shown to the critic, recovered later from canonical storage, or
   unavailable. Reuse existing native-audit and fulfillment provenance where it
   already supplies these identities; do not reconstruct authority from prose.
2. **Specify which comparisons are eligible.** An assignment field and a selected
   current evidence handle can support a literal field-to-span comparison, clearly
   labeled as such. Original-to-revision semantic correspondence remains an
   independently reviewed or unresolved input. Multiple excerpts, multiple
   occurrences and missing historical prose need explicit outcomes; no first-match,
   nearest-wording or equal-text shortcut may imply fulfillment.
3. **Exercise twelve proposed offline fixtures.** Cross six source conditions with
   saved native checks marked met/unmet: a unique handle; duplicate occurrences;
   multiple selected excerpts; compacted older prose recoverable locally;
   unavailable older prose; and stale/conflicting version or field provenance.
   The met/unmet value must not change mechanical equality or source availability.
   Extend existing persisted SQLite/fake-gateway fixtures if persistence/replay is
   part of the proposed implementation. Do not change historical records.
4. **Produce a small reviewable integration proposal.** State where deterministic
   comparison output would appear, how it is labeled as application evidence,
   which original reviewer fields remain visible, and how retry/replay binds the
   same source versions. Keep the no-editor product contract and the single
   Blueprint checkpoint. Identify any required schema, migration or ADR work
   before proposing a production change.

Acceptance requires exact deterministic replay, explicit source/target scope,
rejection of stale or ambiguous location bindings, preservation of unavailable
states, unchanged semantic judgments, and no automatic manuscript repair or
writer dispatch. A correct literal comparison must remain possible alongside an
incorrect or unresolved semantic judgment. Preserve both rather than rewriting
the explanation to manufacture a pass.

After those local checks, decide whether a live question remains. A materially
different question could concern **automatic requirement-to-passage selection or
claim extraction from ordinary production inputs**, where the current experiments
provided authored mappings. First inspect existing saved reviews against source
ground truth to identify a concrete failure class. Only then propose and separately
freeze any necessary small comparison, with unchanged controls, fresh families,
both orders, explicit scoring/stops and a new approved call ceiling. No such live
budget is proposed here without that evidence.

Mechanical comparison work should reduce human searching, not become a new
measure of story quality. Human feel, flow, character and story-breaking review
remains the quality authority. Retain PO as diagnostic evidence, keep EX
unadopted, and leave **Step 19 IN PROGRESS / Step 20 NOT STARTED**.
