# Satisfied decision history in writer context, fixed v59 — 2026-10-14

Status: **EXPERIMENT COMPLETE — OMITTING THIS COMPLAINT DID NOT IMPROVE PRESERVATION.**

The [v60 writer clarification](writer-minimal-repair-v60-2026-10-14.md) did not
improve preservation: both writers removed the forbidden entry but rewrote the
accepted indirect ending as an explicit decision. Main retains v59 production
and the v60 documentation. This diagnostic tests whether the already satisfied
historical missing-decision complaint contributes to that unnecessary rewriting.

Source commit: `20280f0bbd2601ced4517443e6667f4535cf960a`.
Diagnostic branch: `codex/writer-history-diagnostic-v59`.
Production remains **prompt v59 / graph v9**, including both writer and critic.
Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.

## Question and isolated change

The writer's projected `revision_contract.critic_acceptance_tests` contains the
historical test `repair_ac584f91-2e0f-5d9c-9c27-534d3cba35ed_1`. Its allegation says
that Elara remains undecided and requests a decision to enter. The saved latest
review of each overrun draft marks that test met, with no linked current finding.
The draft has an accepted indirect decision followed by a separate forbidden-entry
sentence. Historical deletion-only controls already passed.

Compare the complete v59 writer request with the same request omitting this one
test record from the projected checklist. Remove its claim, original evidence,
requested change and associated fields as one unit. Do not remove the underlying
Critique artifact or change its identity, contents or invocation lineage.

Keep all other writer content unchanged: full current prose, the satisfied touch
complaint, the current boundary complaint, assigned decision and outside endpoint,
canon, broader context, next-scene reservation, system instructions, output schema,
model settings and budgets. The compact review projection contains no second copy
of the removed allegation. No v60 writer paragraph is present.

This is an explicit diagnostic allowlist using saved evidence for the exact draft,
not an automatic production classifier or a policy for discarding history. The
application's normal request builder is unchanged; a scoped diagnostic projection
is applied before each request is recorded and sent, including structural retries.

## Frozen matrix

Use private OH-V01-001 scene 1, the exact saved v59 overrun drafts and canonical
feedback, and seeds **19101 / 19103**. Keep the synthetic plan requiring touch and
psychic pull without an assigned relationship, a decision to enter, and remaining
outside at scene end. It remains a diagnostic plan, not a canonical approval.

| Case | Writer context | Seeds | Planned calls |
|---|---|---|---:|
| Overrun, full history | All three repair tests | 19101, 19103 | 2 writers + 2 critics |
| Same overrun, satisfied decision test omitted | Touch and current boundary tests remain | 19101, 19103 | 2 writers + 2 critics |
| Genuinely missing decision | Same omission procedure retains the test because its saved status is unmet | 19101, 19103 | 2 writers + 2 critics |

Total: **12 probes, at most 24 calls**, allowing one existing structural retry per
probe. Each writer produces one revision. The missing-decision cases reuse the
exact saved v60 draft and initial feedback; their writer system instructions are
the unchanged v59 instructions. There are no new first reviews or newly authored
repair recommendations.

Run full history first at seed 19101 and omission first at seed 19103, followed by
the missing-decision control for each seed. This counterbalances condition order;
it does not establish provider determinism. The primary comparison uses fresh
paired calls. Historical v59/v60 outputs provide context, not the paired control.

Every post-revision critic receives the full immutable input history and **all**
original repair tests, including the item omitted from its writer's request.
For an identical candidate, both paired critic requests are identical. The critic
must assess current evidence independently; writer omission does not grant a pass
or erase an obligation. Freeze each dependent request before sending it.

If a writer fails validation after the existing retry, record the failure and skip
its post-review. Do not replace the case. Retain unexpected valid prose and reviews
as evidence. No second prose revision, valid-response reroll, extra initial review,
continuity/adjudication/full-story call, or canonical write is allowed.

## Assessment declared before generation

1. For each preservation seed, compare full history with omission. Primary measure:
   does deleting the entry sentence restore the accepted baseline exactly?
2. Read full prose and diffs independently of the critic. Separate deletion-only
   repair, benign extra edits, explicit decision restatement, lost decision, retained
   overrun and other defects. Check indirect actions, touch/pull, motivation, outside
   position, unrelated prose and non-prose fields.
3. Both missing-decision controls must acquire a decision while remaining outside.
   Direct wording and action-based or indirect fulfillment remain valid. Confirm
   the genuinely unmet historical test stays visible to both roles.
4. Inspect native checks, each historical repair, boundary, mandatory advice and
   citations, consolidation, raw versus normalized verdicts, failures and retry
   drift. A passing critic is not proof of preservation or artistic quality.
5. Reconstruct every sent request, replay raw responses unchanged, record token
   usage and unknown charges, reverify source evidence, and seal the resulting
   bundle before recommending a production change.

A consistent paired improvement would support a contribution from this test packet
in these inputs. It would not establish which part of the packet caused the effect,
nor prove that automatic filtering is safe. Omission also changes prompt length
and token positions; there is no matched-length placebo. Two seeds, one scene and
one provider do not establish a general quality gain. A null result would not rule
out influence from the remaining touch allegation or current boundary wording.

## Local verification

- Verify **902 sealed files** across six predecessor bundles, their reports and the
  frozen source database. Every frozen v59 implementation hash remains unchanged.
- Reconstruct all six writer inputs. Full-history messages match saved v59 requests;
  missing-decision requests match saved v60 requests after removing only its unused
  writer clarification. Schemas, settings and original inputs match. The two omitted
  variants differ only at the declared checklist item.
- Verify complete critic history, identical shared assignment/boundary, and identical
  paired critic requests for the same candidate. Replay eight saved writer/critic
  responses with unchanged results and critic audits.
- Nineteen no-network mock calls cover the twelve stages, an ablated writer's retry
  recovery, both unchanged missing-decision negative fixtures, and permanent writer
  and critic failures. The diagnostic request hook is restored after each probe.
  These fixture results verify execution, not model behavior.
- **45 relevant tests pass in 13.19 seconds**: isolated probes, shared revision tests,
  endpoint validation and v59 conditions. Repository Ruff lint/format and strict
  mypy pass for 198 Python files. All three diagnostic scripts pass formatting and
  syntax/undefined-name checks.
- No application, API/client contract, dependency or UI changes. The full application
  suite and frontend build are not repeated for this diagnostic-only change.

## Provenance, cost and approval

Private bundle: `data/diagnostics/writer-satisfied-history-v59-2026-10-14/`.
Frozen plan SHA-256:
`c92face4c71d8ac2574f10ada9ab3fc2a75234b4691955a85eefe1c2b0053275`.
Source database SHA-256:
`71618ce4d66ffd3b8ecc46fa4d034105b4e59aa5a80946b5364272b87caeafb2`.

- Existing Ollama Cloud `gemma4:31b-cloud` through the local daemon; verify the saved
  model digest before any generation.
- Per call: 24,000 input / 8,000 output tokens; writer temperature 0.85, critic 0.2,
  top-p 0.95, thinking disabled, saved paired seeds.
- Maximum **24 calls / USD 0.15744** using recorded October 8 rates of USD 0.14/M
  input and USD 0.40/M output. These are historical-rate estimates; actual charges
  remain unknown. The source provider's zero placeholders are not billing evidence.

The user explicitly approved this frozen matrix on October 14: “Yes, run the twelve
writer-history probes.” `approval.json` records that authorization and the exact
plan hash. The bounded run completed with twelve calls. Production and main remain
v59, and canonical stories and sealed benchmarks stay unchanged. No production-history
policy is adopted. Every request was reconstructed and each raw response replayed;
full prose, differences and feedback were inspected before recording these results.

## Results

All **12 probes validated on their first calls**: six writer revisions and six
post-revision critics. There were no retries, failures, skipped cases, second prose
revisions or additional model calls.

| Measure | Full history | Satisfied decision complaint omitted |
|---|---:|---:|
| Exact deletion-only repair | **0/2** | **0/2** |
| Unnecessary explicit commitment added or rewritten | 2/2 | 2/2 |
| Complete accepted indirect passage retained verbatim | 1/2 | 0/2 |
| Forbidden entry removed; fulfilled facts and decision retained | 2/2 | 2/2 |
| Full-history post-critic passes | 2/2 | 2/2 |

The two genuinely missing-decision controls retained the unmet test as planned.
Both writers supplied a decision and remained outside; both post-critics passed.
All six writers preserved the earlier paragraphs and other draft fields, apart
from the expected revision-number change. This measures the requested repair and
preservation behavior, not an overall prose-quality ranking.

### Exact paired changes

At **seed 19101, full history**, the writer retained the entire accepted baseline,
including the indirect ending, but replaced the forbidden entry with:

> She took a deep breath, squared her shoulders, and decided she would go inside.

Thus it preserved all 4,128 accepted characters while adding an unnecessary decision
restatement. At the same seed **with the complaint omitted**, the writer instead
extended the bracing action with “her heart hammering against her ribs” and replaced
the accepted final sentence with “She decided she would go inside.” Its first
4,019 characters remain unchanged. Omission did not improve preservation here.

At **seed 19103, full history**, the first-step setup remains, but the final clause
about both boots being outside becomes “she had made her choice. She would go
inside.” The first 4,082 characters remain unchanged. **With the complaint omitted**,
the first 4,021 characters remain, followed by:

> She took a deep breath and committed herself to the dark, though she remained for a final, trembling heartbeat in the daylight, her boots still firmly on the concrete outside the sill.

This is a narrated commitment rather than the word “decided,” but it still rewrites
an already accepted expression of the decision. Both omission cases retain the
preparatory actions and motivation. All four remove the actual crossing and leave
Elara outside, either explicitly at the end or through the unchanged earlier
position with no subsequent crossing.

The **missing-decision controls** replace only the defective final paragraph. Seed
19101 states her decision and leaves her waiting outside for courage; seed 19103
supplies motivation and a decision, then explicitly keeps both boots in daylight.
Neither leaves the original indecision unresolved. Necessary repair remains possible
when the genuinely unmet complaint is retained. These controls do not validate an
automatic classifier for determining which history is safe to omit.

## Critic and advice inspection

All six raw and normalized critic verdicts are pass. Both native checks and every
original repair check are met, with no overrun, current issues, assignment violations
or new mandatory condition records. There are no extra repair links or duplicated
complaints. First and final responses are the same because no retry was needed.

The omission review at seed 19103 credits the retained motivation and preparatory
actions for the decision, demonstrating that the critic can still use that evidence.
Other reviews cite the newly explicit choice. None requires further entry or adds
causal, temporal or direct-narration requirements. Passing these reviews does not
make the writers' unnecessary restatements successful preservation.

`assessment.json` records mechanical comparisons; `inspection/` retains full prose
and input/baseline differences. `semantic-inspection.json` resolves the automated
assessment's pending manual-inspection flag and records the separate judgments.
`postcheck.json` confirms reconstruction, replay and frozen-source verification.
`closure.json` seals the completed private evidence and this report.

## Interpretation and next focused question

**Keep v59 unchanged.** Removing this one satisfied historical decision complaint
did not improve deletion-only preservation in either paired seed. We have no evidence
from this comparison to justify filtering it from production writer context. The
result also does not prove that historical criticism never influences writing: other
history and the current boundary repair remained present throughout.

One remaining candidate is the **current boundary repair recommendation**. The
application asks the writer to “Restore the current scene's planned outcome and exit
state,” even though the native outcome was already met and only the outside endpoint
was violated. The generated finding also carries the `scene_assignment:outcome`
category and quotes the assigned decision. This is an observable property of the
packet, not proof that it caused the restatement. See the boundary materialization
in `apps/api/open_hollywood_api/services/production_model_executor.py`.

The next diagnostic should compare that current recommendation with advice confined
to the unmet outside boundary, explicitly preserving the already fulfilled outcome.
Keep its claim/evidence, all other history, production v59 and the full-history
critic fixed. Include a truly unmet outcome control so narrowing a boundary repair
does not suppress a necessary decision repair. This proposal is not implemented or
authorized for additional model calls by the present experiment.

## Actual usage and closure

The twelve calls used **166,130 input / 14,648 output tokens**, for a recorded-rate
estimate of **USD 0.02911740**. This is within the approved 24-call / USD 0.15744
ceiling. Provider dollar fields remain zero placeholders with unknown cost basis;
**actual charges remain unknown**.

No production code changed. Main still points to `20280f0b`; this branch contains
the diagnostic report and tracking updates. Reverified prior evidence and the source
database are unchanged. Step 19 remains IN PROGRESS and Step 20 NOT STARTED.
