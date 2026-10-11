# Fulfilled assignments, optional craft and verdicts v54: 2026-10-11

The focused implementation is **prompt v54 / graph v9 / critic retry policy 17**.
The existing critic now receives an explicit instruction to mark the complete
fulfilled obligation met, keep optional craft preferences outside mandatory
repairs, and return pass when only optional preferences remain. Genuine
independent craft defects can still warrant revision. **Implementation, local
verification and the approved 24-probe comparison are COMPLETE; the remedy is
NOT QUALIFIED**. One clarified review now passes with optional advice, but five
false blockers persist and both explicit-order controls regress to false passes.
Correct native check pairs fall from 19/24 to 17/24. Step 19 remains IN PROGRESS;
Step 20 is NOT STARTED.

## Problem and scope

The [stable-v53 wording comparison](assignment-wording-v53-2026-10-11.md) found
five false assignment blockers in six reviews of a draft containing both required
facts. One critic acknowledged both facts, then rejected the scene for violating
its preferred dramatic purpose. The one correct met/met review still returned
revise for a minor request to make touch trigger or intensify the psychic pull.
Its structural retry preserved classification but dropped the Optional label.
All six missing-fact cases also received excessive consolidated repair advice.

The distinction affects production: the graph sets `critique_requires_revision`
from the verdict, while mandatory repair tests include blocking issues and major
issues in revise reviews. Zero repair targets therefore does not mean zero writer
revisions. This implementation addresses the critic's judgment before that
existing routing, without converting every minor issue into a pass.

## Implementation

`COMPLIANCE_CRAFT_RULE` adds **1,393 characters including its separating space**
to the existing critic system instruction. It applies to initial and revision
reviews, including structural retries, for local and cloud delivery.

- When the complete assigned facts and supported applicable conditions hold,
  choose met with a null repair. A preferred catalyst, stronger connection,
  staging or dramatic purpose cannot invalidate fulfillment.
- Keep real missing facts and violated explicit or canonical relationships
  unmet. Actions and indirect narration remain valid evidence.
- Assess genuine craft defects independently against the rubric, with current
  evidence and the existing assignment comparison. A preferred alternative
  mechanism alone is not proof of a defect.
- If optional advice is retained in issues, explicitly label its recommendation
  Optional and use note/minor severity. Keep it out of native mandatory repairs
  and generic restatements, including during structural retries. Do not invent
  a current finding reference for a met check.
- Before choosing the final verdict, identify the actual unresolved defect that
  warrants revision. Optional preferences, including their effect on scores,
  alone do not justify revise/reject. Pass when only optional preferences remain;
  genuine independent craft defects still qualify for revision. Keep summaries,
  comparisons and advice consistent with that judgment.

The complete-fact rule from v50, comparison clarification from v51, minimum-repair
rule from v52 and source-basis rule from v53 remain unchanged. The new rule makes
compliance symmetric: dramatic similarity cannot replace a missing fact, and a
preferred dramatic mechanism cannot negate a fulfilled fact.

This is **model guidance**, not an application-enforced semantic test. No keyword
gate, automatic verdict promotion, semantic relabeling, schema field, new role,
extra inference call, migration or dependency is added. Writer instructions,
validators, consolidation, historical repair ownership, classification retention,
graph routing, budgets and retry limits remain unchanged. Existing accepted
boundaries in ADR 0010, ADR 0030, ADR 0031 and ADR 0033 continue to apply.

## Local verification

Twelve new cases cover the concrete delivery and routing boundary:

- Four local/cloud initial/revision combinations show that removing only the new
  instruction recovers the prior critic system message. User payloads, immutable
  artifacts and schemas remain unchanged; other roles do not receive the rule.
- Four local/cloud repeated/independent claim cases preserve policy-17 structural
  retry metadata and canonical materialization. Classification is not silently
  changed during format repair.
- Four durable SQLite workflow cases use **simulated** responses. Optional advice
  with pass adds no writer revision. A genuine major craft defect requests a
  revision and retains its repair target. An unmet turning point still forces
  revise even when the simulated model says pass. Optional advice with revise
  remains revise and schedules a writer revision despite having no mandatory
  repair target; this protects the diagnostic from falsely counting zero targets
  as success.

The first **32 focused regressions pass**, including v50/v53 and isolated-probe
controls. Python lint, format and strict mypy across 194 files pass. Frontend
format, lint, type checks, all 11 tests and the production build pass. The full
Python run completed with **965 passing tests and one failure**: the existing
instruction-size test did not yet account for the new addition. It was updated
to preserve the prior guidance ceiling and separately cap the new rule at 1,400
characters. Its targeted rerun passes (**1/1**); there are no unresolved failures.
Thus all **966 cases** have passed across the full run and corrected-test rerun;
this is not reported as a second clean full-suite execution. No production code
changed after that full run began. Final `git diff --check` passes.

Offline replay verifies all **25 saved v53 responses** from the previous 24-probe
comparison: the 24 valid results/audits remain identical and the one rejected
first response retains its exact validation diagnostics. Original request
messages reconstruct after removing only the added system instruction, including
the historical retry. All **159 sealed prior evidence files**, the prior report
and the source database retain their hashes.

These checks establish delivery, compatibility and routing, not that the model
will follow the new instruction or that the stories improve.

## Frozen matched comparison

The comparison uses the exact **24 cases and two seeds (19101, 19103)** from the stable-v53
wording comparison. All first-request user messages, output schemas, drafts,
artifact identities, canon, settings, budgets and call order remain identical.
Only the critic system addition and new invocation/fingerprint metadata differ.
No labels or expected outcomes enter model messages.

The 18 core cases cross original conjunction, separate facts and explicit
relationship clarification with three drafts at both seeds:

| Draft | Expected native checks | Additional observation |
| --- | --- | --- |
| Pull before touch; both facts fulfilled | met / met | Optional causal preferences must not cause mandatory repair or revise/reject; inspect any claimed independent defect rather than assuming all criticism is optional |
| Touch and entry decision missing | unmet / unmet | Both blockers remain; complete repairs add only the missing facts, with no invented cause/order/completed-entry demand |
| Complete baseline with action-based decision | met / met | Indirect fulfillment remains valid and no new defect is invented |

Six controls retain the explicit immediate-cause requirement, explicit noncausal
order requirement and applicable synthetic Bible causality rule, each at both
seeds. Expected checks remain unmet / met. Causal repairs must satisfy first
onset; order-only repairs must not add causation. The clarified plan must not
override applicable canon. Inspect exact source authority as well as verdict.

For every response, retain first and final checks, raw/canonical verdicts, summary,
craft scores, complete native/generic/consolidated advice, repair targets, exact
evidence, classification and any structural retry drift. A successful reference
repair cannot by itself qualify the advice or verdict. In particular, distinguish
**met checks**, **zero mandatory targets**, **optional-only advice** and **pass**.

Genuine independent craft-defect routing is tested locally using simulated
responses. This matched live matrix does not introduce a new controlled craft
defect. Consequently it cannot establish broad sensitivity to craft problems,
writer repair success, full-story reliability or cross-provider transfer.

The private source remains OH-V01-001 scene 1 from formal Cloud v33 repeat 3,
invocation `fdbc1392-549a-4ee6-9398-e1fb593e1c36`; source database SHA-256:

`71618ce4d66ffd3b8ecc46fa4d034105b4e59aa5a80946b5364272b87caeafb2`.

The baseline is merge `2036fa1`. The frozen preparation verifies that the only
production edits are the new critic constant, its insertion into the critic
instruction and the global prompt-version increment to 54. Graph version and
critic retry policy remain 9 and 17.

## Observed results

All **24 probes finish in 25 calls**: 23 first responses validate, and one existing
structural retry produces the 24th valid review. Every response is replayed from
its untouched saved output, with requests reconstructed and hashes checked.
Native check pairs are unchanged in 22/24 matched cases. The two changed pairs
are both regressions on explicit order, reducing correct pairs from **19/24 in
v53 to 17/24 in v54**. These are observations from this one scene/model and two
seeds, not a population accuracy estimate or proof of a general causal effect.

| Cases | Native checks and final verdict | Finding |
| --- | --- | --- |
| Pull before touch, original conjunction, both seeds | unmet / met; revise | Both false blockers remain |
| Pull before touch, separate facts, both seeds | unmet / met; revise | Both false blockers remain |
| Pull before touch, explicit relationship clarification, seed 19101 | unmet / met; revise | Both facts acknowledged, but preferred dramatic function still treated as mandatory |
| Same clarified draft, seed 19103 | met / met; pass | Optional minor advice and no mandatory repair; summary remains inconsistent |
| Both required facts missing, all six wording/seed cases | unmet / unmet; revise | Correct detection; all six full repair sets still add unsupported timing/causation |
| Complete baseline, all six wording/seed cases | met / met; pass | Action-based decision remains accepted; no issues or repairs |
| Explicit immediate causation, both seeds | unmet / met; revise | Correctly enforces the assigned cause |
| Explicit order without required causation, both seeds | met / met; pass | Incorrectly drops the mandatory sequence; both matched v53 reviews correctly blocked it |
| Applicable Bible causation, both seeds | unmet / met; revise | Correctly enforces canon; full repairs require contact-caused onset |

### Optional advice and the final verdict

The clarified seed-19103 review marks both obligations met, leaves both native
repairs null and keeps its generic craft suggestion at minor severity with an
explicit **Optional** label. Its comparison has no assignment-finding reference.
It returns **pass**, despite giving dramatic progress 4 rather than 5, and creates
zero mandatory repair targets. The matched v53 review also had met/met and zero
targets but returned revise. This is a concrete improvement in the verdict that
would control writer revision routing; no writer is actually called here.

However, the same v54 summary still says the turning point is **"only partially
met"**, complaining that touch did not alter the pull. That contradicts its own
correct native assessment, which explicitly recognizes that no order or causal
link is assigned. The improvement therefore does not establish a fully consistent
review. It also required no retry, so it cannot qualify optional-label preservation
through structural retries.

The other five pull-before-touch reviews still promote an unassigned catalyst
or dramatic connection into an obligation. In clarified seed 19101, both the
native and generic assessments acknowledge the two events but reject their
decoupling for its supposed dramatic function. Consolidation avoids duplicate
targets but carries that unsupported repair into the writer-facing instruction.

### Explicit-order regression

The control's assignment says:

> Elara touches the stroller before she feels a psychic pull; contact need not cause the pull.

The draft has the pull before touch. Both v54 assessments acknowledge that actual
sequence, then mark the turning point met with no repair. Seed 19101 reduces the
assignment to touching and feeling the pull without causation, losing **before**.
Seed 19103 reports the reversed chronology without explaining how it could meet
the assignment; its summary nevertheless says the specific sequence is fulfilled.
Both pass verdicts would bypass revision for a real missing condition.

The evidence is present and recognized; the failure is in comparing it with the
whole obligation. Permission for noncausal contact may be getting generalized into
permission for either order. That is a hypothesis to test, not an established
internal explanation. An earlier live progress update prematurely said order was
still enforced; the completed evidence review corrects that statement here.

### Repair scope and consolidation

All six both-missing cases retain the correct two blockers. All six native touch
repairs now add an unassigned order or causal demand, and all six complete repair
sets remain excessive. One native touch repair had stayed minimal in v53 before
its generic restatement added causation; that narrow improvement does not survive
this run. Decision repairs remain requests for a decision or commitment, with
**no unconditional demand for completed entry**.

Explicit-cause repairs correctly require contact to cause the first pull. Both
canon controls quote and attribute the real Bible contact-only onset clause but
omit its artifact-version ID. Their native advice says the pull begins only after
touch; generic consolidated advice adds that touch triggers it. The complete
repair therefore restores contact-caused onset, rather than permitting an earlier
pull merely to intensify. Native advice alone is less specific than that full set.

All **21 final generic comparison objects** validate. Twenty are assignment
restatements consolidated into native findings; one is the independent minor
suggestion. There are **21 mandatory repair targets**, comprising sixteen real
missing/violated obligations and five false blockers, with no extra targets from
duplicate generic reporting. The count falls from v53's 23 because the two real
order violations disappear, **not because false blockers are removed**. A target
for a real omission does not qualify its excessive repair wording.

### Structural retry and limits

Only the seed-19103 canon control retries. Its first response uses incomplete,
unscoped draft-evidence IDs and fails validation. The retry fixes those IDs,
retains unmet/met and retains the raw verdict **reject**. Existing mandatory-check
materialization produces canonical **revise**; that is not a retry verdict change.
The generic complaint remains an assignment restatement, with its category label
changing from Logic/Continuity to Continuity. The invalid evidence in the first
response did not establish a valid classification-preservation record.

All final reviews have aligned viewpoint checks, no boundary overrun and no extra
assignment-violation entries. Those structural results do not correct the semantic
mistakes above. Final verdicts are nine pass and fifteen revise, including the two
incorrect order passes. Relative to v53, one verdict improves and two regress.

The live matrix contains no newly controlled independent craft defect; its
sensitivity remains unqualified by these probes. Local simulated routing tests
remain the evidence that genuine independent defects can request revision. There
are no writer revisions, full-story runs or cross-provider tests. The historical
matched comparison is not a simultaneous replicated experiment.

## Next focused recommendation

Do not treat v54 as accepted stabilization or expand the prompt again on these
results alone. Hold its implementation fixed for a bounded comparison that
separates temporal order from causal permission: order-only wording, the same
order with a no-causation clause, and separately stated relationship conditions.
Cross correct and reversed chronology and retain an unconstrained-facts control.
This can test whether the permissive clause is masking the required order before
we choose another production change. The existing false blockers, excessive
repairs and summary inconsistency remain open. No additional experiment is run
or authorized as part of this completed 24-probe batch.

## Budget, approval and evidence

Destination: existing Ollama Cloud `gemma4:31b-cloud`, via the local daemon with
the recorded model digest checked before inference. **24 probes, at most 48
calls**, allowing one existing structural retry per probe. No reruns of valid
reviews, writer calls, full-story runs or canonical changes.

Each call retains ceilings of 24,000 input and 8,000 output tokens. At recorded
October 8 rates of USD 0.14/M input and USD 0.40/M output, the maximum reference
estimate is **USD 0.31488**. Actual charges remain unknown and separate from this
estimate. No current price claim or zero-cost claim is made.

The user explicitly approved **"Yes, run the 24 v54 probes"**, recorded in
`approval.json` and bound to this frozen plan hash before execution:

`eb01451e664929dc71895fb0dfd4126ba8dde0e850619005f0403df2282a7415`.

The completed batch uses **329,887 input and 30,351 output tokens**, including
the failed first response and retry. Its recorded-rate estimate is
**USD 0.05832458**, below the USD 0.31488 cap. Actual charges remain unknown; the
provider's free/paid accounting is not inferred from that estimate.

Private evidence lives in `data/diagnostics/compliance-craft-v54-2026-10-11/`:
`experiment.py`, `assess.py`, `prepared/*.json`, `offline-verification.json`,
`plan.json`, `approval.json`, `live/`, `assessment.json`, `postcheck.json`,
`record_semantics.py` and `semantic-assessment.json`. `closure.json` seals evidence
and final report hashes. `preparation-checks.json` is the historical preapproval
record of local checks; its zero-call/pending fields are not final run status. A
pre-approval manifest correction changes a code-hash key to its actual source
path; `preapproval-plan-correction.json` records the superseded plan hash. It
does not change any request, instruction, budget or call order. Historical
stories, sealed benchmark results and prior diagnostics are unchanged. Source,
prepared-request and production-code hashes are rechecked after execution. This
implementation is not a qualified remedy or Step 19 acceptance.
