# Remaining critic failures and ending rewrites

Date: 2026-10-17. **DIAGNOSIS COMPLETE; NEXT EXPERIMENT PROPOSED, NOT PREPARED OR RUN.**

The critic needs a clearer connection between its judgment and the legal reporting
route. The writer still receives a real boundary defect framed as an outcome
repair, even when positive evidence certifies that outcome. These are concrete
properties of the requests worth testing separately. They are not proven causes
of the model's choices.

Recommend two independent comparisons in one proposed **40-probe / 80-call**
envelope: an explicit critic route index, and a writer view that presents a
boundary-only complaint as a boundary repair. Neither candidate is implemented.
Production stays prompt 61 / graph 9 / policy 1. The full workflow canary remains
**ON HOLD; NOT STARTED**. No new inference or provider discovery was performed.

## Evidence and scope

This follows the [completed 35-call comparison](../benchmark_reports/fulfillment-contrasts-v61-results-2026-10-17.md)
and [previous diagnosis](fulfillment-failure-diagnosis-next-experiment-2026-10-16.md).
The completed experiment and its unused 29 slots are closed; they do not authorize
this proposal. Its immutable plan, scoring, failed attempts and results are preserved.

At checkout `18ca05abba476524d7af38a1266f1b8a6ba57f97`, offline inspection reverified
all **337 live files**, **44 preparation/operator files**, the report hash, the
115 frozen code/dependency hashes and predecessor seals. All 32 receipts were
replayed, including the 35 attempts and both terminal failures. Network connections
and gateway construction were blocked during that verification. The private record
is `data/diagnostics/fulfillment-routing-ending-diagnosis-2026-10-17/inspection.json`.

This is analysis and a proposed design. It does not create candidate request
bundles, change a prompt, relax a validator, amend an ADR or start Step 20.

## 1. The remaining critic failures

### A real endpoint defect is attached to the wrong obligation

Both final Elena separate-match reviews acknowledge that she starts checking the
handwriting, yet call the decision unmet because a match is established afterward.
Their citations include the purposeful action and the subsequent result as separate
excerpts. The model found the evidence; it assigned the defect incorrectly.

The clean versions pass, the genuinely undecided versions fail correctly, and the
compound outcomes correctly fail their own explicit no-match clause. Elara passes
the distinction in both separate and embedded forms. This rules out missing evidence,
normalization reversing the judgment, and sentence grouping as a sufficient
explanation. It does not establish reliable general event-versus-endpoint reasoning.

The request still presents overlapping concepts:

- The system says to assess each exact obligation independently and accepts an
  intentional attempt as a decision.
- `scene_boundary.current_endpoint` references outcome and exit state together.
- `critic_requirement_scope` lists exit state as an outcome companion, labels it
  advisory, and says advisory entries cannot become blocking omissions.
- The separate boundary policy makes an actual endpoint overrun blocking.

Those representations serve different purposes, but the reader must reconcile
them. The observed attribution error fits treating the whole endpoint as the
native outcome. It remains a hypothesis about influence, not proof that one field
caused it. The failed scope-clarification trial and imperfect failed-clause trial
remain counterevidence against simply adding more semantic instructions.

### Correct raw judgments still fail the reporting contract

Both embedded Elena probes say outcome **met** and boundary **overrun** in both
raw attempts. Their failures concern conditions, anchors and links, not an absent
decision. The five invalid attempts show these routes:

| Probe/attempt | Failure |
| --- | --- |
| Embedded Elena 19201/1 | Creates `assignment:outcome` conditions and a linked issue although that check is met |
| Embedded Elena 19201/2 | Invents `assignment_violations.anchor=exit_state` and its repair identity |
| Separate Elena 19203/1 | Reports `outcome` in the generic violation array as well as the native check |
| Embedded Elena 19203/1 | Authors a separate recommendation on a linked issue; also includes incompatible outcome routes |
| Embedded Elena 19203/2 | Removes conditions/violations but still links the issue to `outcome` / `assignment:outcome`, rather than the available `boundary` finding |

The generic violation schema permits only `assigned_character_ids`, `location_id`
and `scene_id` for these requests. A populated `exit_state` in the input is therefore
not a legal generic violation anchor. `repair_ref` is a bounded string with legal
ownership enforced by application validation. Boundary-only advice is supplied by
the application; the model must not create a boundary condition record. Linked
generic issues reuse their native finding's advice and keep `recommendation=null`.

These rules are already present, but spread across long instructions, schemas and
conditional ownership requirements. The saved requests have `response_schema=null`;
the schema is delivered in message content. The observed transport does not prevent
the model from generating these invalid combinations before application validation.

Validation correctly refuses them. Do not convert their raw met judgments into
writer evidence, silently reroute complaints, accept unsupported anchors or add retries.

### Structural retry does not ensure semantic stability

The separate Elena 19203 review changes from raw met to valid-but-wrong unmet on
retry. That makes its outcome repair route structurally legal while degrading the
judgment. Structural recovery and semantic recovery must be measured separately.

All three retry requests contain only system and user messages, with no rejected
assistant response and no `preserved_classifications`. The separate case's focused
directive is only “repair this review-response field only.” The embedded retries
repeat the condition rule and required shape. They regenerate a full review from
the original inputs rather than editing an attached prior response.

The code deliberately excludes rejected prose. Its existing retention protects
generic issue classification metadata (category, severity, evidence and finding
link), not a snapshot of native `assignment_checks` statuses. It permits that
retention only when the underlying findings/conditions validate; malformed advice
can prevent it. See
[production_critic_classification.py](../../apps/api/open_hollywood_api/services/production_critic_classification.py),
`_schema_repair_guidance`, `_critic_link_failure_details` and
`_critic_retained_classifications` in
[production_model_executor.py](../../apps/api/open_hollywood_api/services/production_model_executor.py),
and [ADR 0035](../adr/0035-rendered-assignment-repair-advice.md).
There was no retained generic-classification contract in these three requests,
and no mechanism directly pinning their native statuses. This explains why the
retry path did not prevent drift, not why the model chose that particular new
judgment. Feeding back rejected prose or freezing unvalidated
statuses would be a separate intervention with different risks; neither is proposed
for the first comparison below.

### Advice support remains another axis

Keep the reported **16/20 classification matches** separate from the conservative
**15/20 sound-review assessment**. The compound Elena condition requiring an
“inconclusive or negative” comparison is narrower than simply establishing no match.
The original report already records the permissive alternative interpretation.
It is a reviewable advice-support caution, not another unequivocal routing failure.
The next scoring sheet must predeclare how pending comparison, optional alternatives
and mandatory new results are judged; source-valid quotations alone prove no entailment.

## 2. Why both writer arms rewrite the ending

The latest results do not support blaming the positive packet for the shared edits.
Evidence avoids new decision assertions in 3/3 pairs; current context adds them in
3/3. Both arms nevertheless remove the imminent-first-step sentence and replace the
ending. The earlier evidence-only restatement at seed 19101 remains real, but did
not recur at the three new seeds.

The shared request gives the writer one current repair test with:

- category `scene_assignment:outcome`;
- a claim beginning `Assigned outcome: "Elara decides to enter the windowless building."`;
- advice beginning `Restore the current scene's planned outcome and exit state`;
- evidence consisting of the actual forbidden entry sentence.

The native outcome was met; only the outside boundary failed. The positive packet
and negative test consequently frame the same outcome differently. The compact
Critique input contains only its target and verdict, so this test is the substantive
negative-feedback channel, not one copy among several full critique bodies.

The packet cites bridge reasoning and bracing against the jamb, not the subsequent
imminent-step sentence. That sentence is adjacent to the defect and predicts the
very action being removed. Those facts make both broader endpoint framing and
local sentence interpretation plausible contributors. Neither proves causation.
Earlier successful deletion-only responses demonstrate that changing it is not
necessary for the supplied boundary repair. Conversely, its strap timing and
prospective action could invite a stylistic clarification; the model supplied no
independent craft rationale establishing one.

“Unnecessary” here means unsupported by the supplied repair, not automatically bad
writing. The source is not a literary gold standard. A human might prefer a changed
ending. The unchanged post-critics accept both explicit and indirect decisions and
report no craft issues; their passes cannot resolve that preference.

Do not repeat already unsuccessful interventions without a distinct hypothesis:

- The [v60 deletion/preservation reminder](../benchmark_reports/writer-minimal-repair-v60-2026-10-14.md)
  yielded 0/2 exact restorations.
- [Omitting a satisfied historical complaint](../benchmark_reports/writer-satisfied-history-v59-2026-10-14.md)
  yielded 0/2 in both arms. The latest source has no such historical ledger anyway.
- [Changing only the boundary advice prefix](../benchmark_reports/writer-boundary-advice-v59-2026-10-15.md)
  yielded 0/2 in both arms; its category and outcome-framed claim remained.

The next writer comparison should test the remaining negative-feedback framing
as a whole, with fulfillment evidence held constant. Adding a citation to protect
the ending would instead test evidence coverage, and copying more favorable critic
claims into a saved packet would falsify its ordinary-review provenance. Neither
belongs in the proposed comparison.

## 3. Proposed next experiment

Prepare and present the complete frozen plan locally first. Only a later explicit
approval of that plan permits live work. The following candidates are descriptions
for review, not changes to current production prompts or requests.

### A. Critic route index: 24 probes, at most 48 calls

Compare fresh ordinary v61 requests (**C0**) with the same requests plus one compact,
schema-derived `critic_route_index` in the user payload (**C1**). Include the same
index on its structural retry. Leave system instructions, output schema, condition
semantics, source catalog, validator, normalization and retry construction unchanged.
Do not add the failed-clause diagnostic or a semantic answer key.

The proposed index states the existing legal destinations:

| Finding | Legal destination and advice ownership |
| --- | --- |
| Turning point / outcome | `assignment_checks` only; only an unmet check owns `assignment:<anchor>` conditions |
| Other assignment mismatch | `assignment_violations`, limited to the exact anchor enum in this request |
| Endpoint overrun | `scene_boundary_check`; when overrun, `boundary` is available to a linked repetition; no model-authored boundary condition record |
| Viewpoint violation | `point_of_view_check` and its existing condition owner |
| Generic repetition | An actually reported blocking finding; null recommendation; reuse its conditions/application policy |
| Independent craft | Ordinary `issues` route with null assignment link and its own supported recommendation/comparison |

The map must be conditional on the model's own findings, not populate met/unmet
answers or declare an overrun in advance. It must preserve compound obligations,
legitimate native/boundary consolidation and independent craft. A met obligation
cannot be made unmet merely to create a repair reference. Exact text and insertion
position will be frozen during preparation; only that payload field may differ.

Use six existing complete cases at **19301 and 19303**, in this order: Elena clean,
separate match, embedded match, missing decision, compound outcome; then Elara
embedded entry as a cross-story control. Run both arms for each case. At 19301 use
C0 then C1; reverse at 19303. Preserve exact prose, assignment, constraints and
artifact lineage from the sealed contrast bundle. All 24 probes run irrespective
of semantic results, subject to global integrity/transport/budget stop rules.

Expected tuples remain those already frozen: met decisions in clean/event-overrun
cases, unmet decisions when genuinely missing, unmet complete compound outcomes,
appropriate boundary status, and met turning points throughout. No positive status
is a substitute for supported advice or a correct raw verdict.

Measure first/final validity, every routing error, native checks, raw versus
normalized verdict, source support and retry drift. A promising result requires
fewer routing failures than the concurrent control, correct supported judgments
on all twelve candidate cases, and no lost clean/missing/compound control. If the
control has no failures, report non-reproduction rather than crediting an improvement.
If routing improves but wrong attribution survives, propose a separate scope
intervention afterward; do not tune it into this run.

### B. Writer boundary framing: 8 writers + 8 post-critics, at most 32 calls

Use two fixed, successful **ordinary** critic sources, selected before any new calls:

1. Separate entry: the same `s19101-elara-separate-initial`, attempt 2, used by the
   completed replication, from the October 16 production comparison.
2. Embedded entry: `s19201-elara-embedded-initial`, attempt 1, from the October 17
   contrast comparison. Its met outcome cites the composite passage containing
   the forbidden entry, providing an actual necessary-edit-inside-evidence control.

Both sources certify the native facts and report only a boundary repair. Reconstruct
their exact drafts, feedback and fulfillment packets through the existing projection;
never salvage a failed review or change what the source critic cited. Compare arms
within each source, not differences between the two sources as a treatment effect.

**W0:** ordinary v61 writer with its exact fulfillment packet and original repair test.

**W1:** the same request and packet, with only three fields of the boundary-only
writer acceptance-test view projected differently:

- `category`: `scene_boundary:exit_state` instead of `scene_assignment:outcome`.
- `claim`: replace the opening `Assigned outcome: "<exact outcome>".` with
  `Assigned exit state: "<exact exit state>".` Keep achieved state, endpoint
  comparison, next-scene comparison and any restatement verbatim.
- `requested_change`: replace its first sentence with `Repair the violated current
  exit state: remove unassigned material advancement, not merely a later detail of
  an already established result.` Preserve the remaining setup/overlap policy and
  next-scene reservation verbatim.

This is a diagnostic presentation of the real complaint, not an edit to its immutable
Critique. Keep IDs, severity, original evidence, acceptance condition, all other
tests, full prose, assignment and positive packet identical. Preserve the ordinary
writer system message and output schema. Record the three exact JSON-path differences
and diagnostic provenance rather than representing W1 as an ordinary production
request. This tests the bundled boundary framing; it cannot identify which of the
three fields mattered, and there is no matched-length placebo.

The projector applies only to these allowlisted boundary-only source tests. A native
unmet condition, mixed consolidated repair, unknown provenance or extra issue must
stop preparation of that source, not be discarded to fit the treatment. Offline
negative fixtures must show that genuinely unmet/native/craft repairs cannot be
hidden or relabelled by it. Both complete input sources must qualify before freezing.

Use **19301 and 19303** for both cases. At 19301 run W0 then W1; reverse at 19303.
One prose revision per writer, followed immediately by one ordinary post-critic
on valid output. Post-critics get all **original** feedback/tests, no W1 projection,
no route index and no fulfillment packet. Identical paired drafts must yield
identical post-critic requests. New critic results in A never gate or supply B.

Judge full prose and diffs after both arms validate, repair the defect and retain
fulfilled facts. Record new restatement, changed uncited prose, necessary changes
inside cited prose, unrelated ending edits, benign edits and genuine craft tradeoffs.
Exact deletion/clause removal and quote retention are descriptive, never quality
gates. Keep invalid/factual failures outside preservation wins and in total coverage.

Report four pairs as wins/ties/losses/mixed. A promising framing signal would be
at least three preservation wins, including a win in each case, without factual
regression or failure to edit the embedded defect. Shared rewrites or ties provide
no preservation-benefit claim. Any result is diagnostic, not grounds for promotion.
Archive full anonymous pairs for human preference; assistant inspection is not blind
human review. No additional revision is allowed in response to a post-critic.

### Budget and stop rules

| Proposed block | Primary probes | Maximum calls including one structural retry |
| --- | ---: | ---: |
| Six critic cases × two arms × two seeds | 24 | 48 |
| Two writer cases × two arms × two seeds | 8 | 16 |
| Their ordinary post-critics | 8 | 16 |
| **Total** | **40** | **80** |

The increase from the previous 64-call ceiling funds the embedded writer control
and fresh matched critic arms; it is a new proposed allowance. No unused slots from
any completed comparison transfer here. Keep separate 48-call and 32-call block
ceilings with no reassignment.

Use the same recorded `gemma4:31b-cloud` deployment and digest, verified only after
live approval. Keep temperatures 0.2 critic / 0.85 writer, top-p 0.95, thinking off,
24,000 input / 8,000 output tokens and 900 seconds per attempt. Maximum reservation:
**1,920,000 input / 640,000 output tokens**, **72,000 active seconds**. At the frozen
October 8 rates only, the estimate ceiling is **USD 0.52480**; actual billed charges
remain unknown, and this is not a current pricing or dollar-budget guarantee.

The frozen plan must explicitly disclose complete fictional prose/context sent
through the local Ollama daemon to Ollama Cloud. Record later approval against its
exact hash. Persist exact requests and reserve each attempt before dispatch. Terminal
structural failures remain results; a failed writer skips only its post-review.
Transport/authentication, model identity, integrity, budget, cancellation or unknown
outcome stops further dispatch. No transport retries, semantic rerolls, replacement
cases, additional roles, full stories, canonical writes or canary work.

## 4. Preparation and future quality work

1. Review this proposal. If preparation is authorized, implement both projections
   only in a new private diagnostic harness, leaving production fixed.
2. Freeze full inputs, source-response/audit hashes, candidate text, exact request
   differences, seeds, order, scoring examples and the 80-call budget. Freeze the
   conditional post-review and retry builders; save each actual body before dispatch.
3. Verify offline schema/route ownership, ordinary versus candidate request isolation,
   missing/compound controls, necessary embedded repair, independent craft transmission,
   source/packet provenance, ceilings, known outcomes, skips and zero-call replay.
   Retain the ordinary full-history post-critic. Present the frozen plan before any calls.
4. Only after separate plan-bound live approval, execute once, inspect all attempts
   and revisions, report failures and limits, update tracking and seal the evidence.

The embedded case tests permission to repair a defect within a cited passage. It
does **not** exercise a real craft-driven improvement in a met passage. Offline craft
fixtures prove transmission, not literary judgment. That remaining live qualification
and human review must stay explicit even if both proposed candidates perform perfectly.

Use the already exported three anonymous pairs for pending human review and preserve
the original prose alongside each revision. Do not elevate preservation into the
product's creative objective: meaningful improvements to voice, character, tension
or dialogue must remain possible in fulfilled passages. Avoid locked spans and extra
explicit-decision requirements. Do not treat all rewrites as losses or critic praise
as a human preference signal.

Complete-story quality still needs the accepted rubric, hard gates, full Cloud corpus
and comparable single-model baseline. Constraint adherence has 5% of the weighted
rubric plus applicable hard gates; local wording retention is not a new dimension.
This proposal adds no normal-workflow human checkpoint beyond Blueprint approval.
**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED; the canary stays on hold.**
