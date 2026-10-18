# Review repair and independent revision assessment: diagnosis and proposal

Date: 2026-10-18. **DIAGNOSIS COMPLETE; EXPERIMENT PROPOSED, NOT PREPARED OR RUN.**

The [46-call comparison](../benchmark_reports/fulfillment-reporting-edit-purpose-v61-results-2026-10-17.md)
exposes two different problems. More feedback did not make whole-report regeneration
reliable. Writer-authored purposes did not independently constrain edit selection.
Neither result warrants another production reminder or a canary.

Recommend a **96-call maximum** for two isolated comparisons: full replacement
versus restricted correction of a frozen review, and comparative revision assessment
with writer purposes hidden versus visible. Reuse existing revisions rather than
generate another batch of endings. This task creates no candidate prompt, request
bundle, runtime intervention or live operator. Production stays prompt **61**, graph
**9**, fulfillment policy **1**. **Canary ON HOLD; NOT STARTED.**

## Diagnosis: why expanded feedback added no recoveries

Both policies recovered two of three rejected initials. Only three paired failures
were observed, and the earlier ownership error that masked comparison coverage did
not occur in any new initial. The two duplicate-plus-overrun initials already received
the missing comparison location and the required `boundary` group under ordinary R0.
R1 therefore mostly made an already visible rule more explicit in this sample.

At seed 19603, R0 again omitted that group. R1 supplied it but added a model-written
`boundary` condition, which is forbidden because the application owns that advice.
Both responses retained the correct minor duplication finding. This is a transition
between reporting errors, not evidence that expanded feedback damaged noticing.

The exact requests explain an important limitation of the intervention:

- Both branches require a **complete replacement JSON object**.
- Both send ordinary story context, the complete review schema and selected
  classification metadata. Neither sends the complete rejected review to edit.
- Classification retention constrains category, severity, evidence and reference
  choices. It does not preserve every native judgment, allegation, explanation,
  condition record or score. The model must regenerate those fields.
- R1 diagnoses errors present in the rejected report. It cannot flag the new
  boundary condition that will be introduced by regeneration; that condition was
  absent from the parent. The general ownership prohibition was already present.

This follows the deliberate production policy in
[ADR 0031](../adr/0031-preserve-critic-classification-during-structural-repair.md),
which does not replay rejected allegation or comparison prose. It is not a lost
payload or a new regression. It nevertheless leaves a large amount of valid material
to regenerate during a small structural repair. Error migration is consistent with
that exposure; this run does not establish a unique internal model cause.

The reference names also have different responsibilities. `boundary` is a valid
finding to compare against and repeat, but not a model-authored condition owner.
Independent craft is a distinct defect, yet still must compare itself with current
hard findings. More explanations leave those distinctions for the model to encode
correctly in several fields. The collector improved visibility, not the output
representation or the application of corrections.

**Offline counterfactual:** all five rejected responses from the completed run
validate after editing only the applicable reference, linked recommendation or
forbidden boundary-condition record. Native and boundary judgments, scores, issue
descriptions, severity, evidence and comparison prose remain unchanged. These are
operator-authored copies, not recovered model outputs. Adding a reference alone
does not prove the comparison explanation is substantively adequate.

The earlier masked-error hypothesis remains open. The new evidence argues against
assuming that comprehensive feedback alone is sufficient; it does not show that
the collector is useless on errors that ordinary feedback fails to expose.

## Diagnosis: why purposes justified unnecessary rewrites

The purpose schema worked mechanically: references resolved, patches applied and
all factual repairs succeeded. It did not validate the truth or scope of a claim.
That limitation was explicit in the frozen design, and the results confirm it:

| Observed claim | What the actual change establishes |
| --- | --- |
| The old embedded sentence enters the building | True, but it does not justify adding a poised-at-the-dark image or staring action while removing entry. |
| The adjacent preparation implies forbidden entry | Unsupported: preparation and an anticipated first step are compatible with the explicit outside endpoint. |
| Removing entry necessitates a tonal shift | A stylistic preference is presented as a dependency. Deletion does not itself require a heartbeat or a different condition for proceeding. |
| A duplicate remains unless one copy is removed | Supported; all four craft-control revisions perform that repair while retaining surrounding prose. |

The counterfactual question about keeping the *whole selected old span* was too
coarse to justify every part of a replacement. An embedded span contains a real
defect, so the writer can truthfully identify that defect while adding unrelated
material. For adjacent spans, the writer can assert an implication or flow problem
that the text does not establish. Selection and justification come from the same
generation; neither is an independent test of the other. The output is consistent
with rationalization, but does not reveal whether the explanation preceded the
selection internally.

Four local patch copies remove only entry and validate under the unchanged exact-edit
contract. The separate cases need no adjacent rewrite; the embedded cases can keep
their preparation wording. The patch mechanism can express these repairs. Its role
is to apply the writer's chosen changes accurately, not to decide their necessity.
These copies are factual/preservation controls, not claims of superior literature.

W1 still has limited positive evidence: two primary preservation wins, successful
craft repair and no primary loss. The mixed ending and additions-neutral result
(one win, one loss, four ties) limit that signal. Discarding those gains would be as
misleading as treating the eight valid purpose records as eight supported purposes.

All twelve ordinary posts saw the current revised catalog and repair context, not
the complete original plus revision and diff. They received no writer purposes.
Their unanimous pass and 36 maximum craft scores therefore do not test whether
purposes persuade an independent reviewer, or whether that reviewer can recognize
loss relative to the original. They establish neither comparative preservation nor
literary preference. The next comparison should supply the missing comparison task
and test explanation influence explicitly.

## Proposed A: full replacement versus restricted review correction

Use six fixed source reports, each at two new, predeclared seeds. The following
source IDs identify evidence to freeze during preparation; they are not new live
results. Every source uses attempt 1.

| Source report | Purpose |
| --- | --- |
| `s19603-elara-duplicate-overrun-initial-shared` | Missing independent-craft comparison coverage. |
| `s19601-elara-recurrence-overrun-initial-shared` | Separately authored recommendation on a linked boundary issue. |
| `s19501-elara-duplicate-overrun-initial-P1` from the preceding presentation/temperature run | Ownership error plus concealed comparison error. |
| `s19603-elara-duplicate-overrun-correction-R1` | New ownership error after comparison was corrected. |
| `s19601-elena-missing-decision-initial-shared` | Valid native-condition control; preserve the genuinely missing decision repair. |
| `s19601-elena-compound-outcome-initial-shared` | Valid native-plus-boundary control; preserve the no-match repair and fulfilled decision. |

Supply both arms the exact parent JSON as **untrusted diagnostic data**, the same
full story context, ordinary rules and the same bounded R1 diagnostics:

- **F0:** return a complete corrected report.
- **F1:** return only typed replacements/removals at a bounded list of structurally
  diagnosed locations. Apply them atomically to the exact hashed parent, then run
  the unchanged full validator.

Both arms must preserve all fields outside those diagnosed locations. F1's
application enforces the same scope that F0 must obey while emitting the full object.
Comparison repair may replace its references and assessment; the comparison's
semantic support still requires inspection. A linked recommendation may become
null, and an unauthorized boundary condition may be removed. Native conditions,
issues, evidence, classifications, judgments and scores cannot be discarded or
rewritten to obtain validity. Valid controls require identity/no-op outputs.

Locations must come from a general structural collector, never from expected story
labels or a handpicked successful replacement. No automatic reference insertion,
default explanation, blanking of native conditions, semantic reclassification or
silent repair. Invalid, stale, out-of-scope, overlapping or incomplete patches fail
closed. A model cannot cure an unsupported parent judgment through this format-only
operation; that requires a separately authorized fresh assessment.

This comparison deliberately changes the rejected-prose policy **only inside an
isolated diagnostic adapter**. F0 is not unchanged production R1: adding the parent
to both arms holds that availability constant and isolates full-object emission
versus constrained patching. It will not identify the benefit of parent visibility
alone. Any production adoption would need a separate ADR/security/lineage review;
this proposal makes no such adoption. Treat injected instructions in parent prose
as data and test that boundary locally.

**Budget:** 6 parents × 2 arms × 2 seeds = **24 calls**. Each is the one correction
or identity challenge; no further retry, fresh initial or replacement source.
Failed corrections are scored, not corrected again. Valid controls are diagnostic
challenges, not claims that production should retry passing reviews.

Provisional signal: F1 validates all eight failed-parent cells and preserves all
four valid-control cells; all retained findings/native conditions remain supported;
no collateral field change; at least two additional qualified recoveries over F0
and no paired loss. Invalid output or unsupported comparison text cannot count as
recovery. If both arms recover everything, record no demonstrated relative advantage.
Report success on this fixed error set, never a natural failure-rate estimate or
improved critic noticing. Restricting the output can prevent classes of collateral
changes by construction; that is an adapter property, not evidence of better judgment.

## Proposed B: independent full-prose review, with purposes hidden or visible

Use fixed originals and revisions. Make **no new writer calls**. Each review receives
the full original, full candidate, exact diff/edit alignment, assignment/boundary,
source critique, existing mandatory tests and explicitly requested optional craft
task where applicable. Preserve the distinction between a hard repair and a minor
craft request. No new mandatory literary acceptance test is manufactured.

- **V0:** assess the changes without the writer's purpose claims.
- **V1:** the identical assessment with the purpose claims visible as untrusted
  assertions to check against the actual text and changes.

Use the same assessment task, schema, context and sampling for both. The ordinary
P0 post-results remain historical reference evidence, not a newly paired control.
This comparison tests comparative-review capability and susceptibility to purposes;
it does not isolate before/after visibility from every other difference to P0.
V0 is a separate call to the same model; correlated blind spots remain possible.

The proposed nine-candidate panel is:

1. Actual W1 separate-entry revision, seed 19601: unsupported adjacent rewrite.
2. Actual W1 separate-entry revision, seed 19603: unsupported necessity claim and a
   mixed craft/preservation tradeoff.
3. Actual W1 embedded revision, seed 19601: true entry repair plus additional imagery.
4. Actual W1 optional-craft revision, seed 19601: successful duplicate removal.
5. Operator-authored minimal separate-entry repair from the same frozen original.
6. Operator-authored minimal embedded-entry repair from the same frozen original.
7. Operator-authored optional-craft no-op: the duplicate remains, with the successful
   source's removal claim attached as a deliberately mismatching claim.
8. Operator-authored boundary no-op: the overrun remains, with an entry-removal claim
   attached as a deliberately mismatching claim.
9. A labelled synthetic craft control: accidental phrase duplication **within one
   positively cited fulfillment sentence**, plus a revision removing that duplication
   while retaining its fact. Unlike two separate sentence copies, this task must
   change wording inside the cited passage.

The four actual candidates retain their exact source purposes. Minimal repairs use
the corresponding direct-repair claim; the no-op claims are explicitly operator-
constructed challenge data, never falsely attributed as new model outputs. The
within-sentence control requires a transparently constructed original, candidate,
optional task and claim. Its input versions, reference mappings and factual labels
must be verified during preparation. If that control cannot be made unambiguous,
stop preparation and revise the plan before freezing; do not substitute after calls.
Synthetic provenance and expected labels stay in the operator ledger, not as hints
to the reviewer. Both arms always know that claims may be wrong.

Ask for bounded, source-cited editorial findings on separate axes:

- Was the supplied hard/optional task performed, and were fulfilled facts retained?
- Which changed semantic units are required by the task or by an actual grammatical
  dependency, which are optional craft choices, and which lose existing meaning?
- What concrete gains or losses in voice, tension, agency and naturalness are
  supported by the complete prose? Permit tie, mixed and uncertainty.
- With purposes visible, does each claim cover the **actual alteration**, including
  additions within a span containing a genuine defect? A true defect elsewhere in
  that span is insufficient.

This is an editorial assessment, not hidden reasoning, a new writer prompt or an
automatic accept/reject gate. Assessors cannot rewrite, trim or apply the candidate.
Bind references to original/revision versions and changed-unit IDs; identity checks
do not replace semantic inspection. Keep actual author/arm/seed and expected scores
out of both requests. Counterbalance arm and candidate order without obscuring which
text is the original. Freeze retry retention rules so a structural repair cannot
erase an inconvenient criticism or change a valid judgment unnoticed.

**Budget:** 9 candidates × 2 arms × 2 seeds = **36 primary reviews**, with at most one
structural correction each: **72 calls maximum**. No semantic reconsideration loop,
candidate regeneration or post-review writer call. Score first and final attempts
separately; unchanged invalid opinions cannot be made valid by an operator.

Predeclare V0 as the candidate independent assessment. A useful provisional signal
requires correct task/factual judgments in all 18 cells; both no-op defects detected
at both seeds; all three actual boundary-revision cases identify the concrete extra
changes and distinguish necessity from possible merit; both clean boundary repairs
and both successful craft-control types receive no invented hard failure. The mixed
case must preserve its uncertainty/tradeoff rather than force a literary verdict.
No-op, no-change bias and blanket protection of fulfilled wording fail these controls.

Use V1 as the paired explanation-influence challenge. Report every unsupported
upgrade, factual miss and newly invented objection relative to V0, including cases
where V1 helps. A fluent purpose must not qualify a false repair or erase an observed
loss. Do not select whichever arm happens to score best after seeing results. Passing
V0 would justify proposing a subsequent review-guided revision test, not installing
a reviewer or claiming that its judgments are human quality evidence. If V0 cannot
make these distinctions, do not add a self-approval loop; consider a separately
bounded model crossover or human-calibrated assessment next.

## Budget, preparation and story-quality boundary

| Block | Primary calls | Maximum calls |
| --- | ---: | ---: |
| A: fixed review repair/identity challenges | 24 | 24 |
| B: full-prose assessments | 36 | 72 |
| **Total** | **60** | **96** |

Blocks are nontransferable. A failed primary, refusal, timeout, truncation or unknown
outcome consumes its reserved attempt; no transport reroll or silent case substitution.
Only B's structural validation failures permit its one correction. No budget carries
over from earlier runs. Stop on changed sources/model identity, cancellation, unknown
outcome or a budget inconsistency; retain evidence and do not resume a call blindly.

Propose the existing pinned `gemma4:31b-cloud` identity through Ollama Cloud via the
local daemon, two new fixed seeds (19701/19703), temperature 0.2, top-p 0.95 and
thinking disabled. No discovery has been performed. At the existing per-call caps
of 24,000 input tokens, 8,000 output tokens and 900 active seconds, the maximum
reservations are **2,304,000 input tokens, 768,000 output tokens and 86,400 active
seconds**. Historical October 8 rate estimate at that ceiling: **USD 0.62976**;
actual billed charges remain unknown. Prove full comparison packets fit before
freezing; exceeding the cap requires a revised plan, not silent context trimming.

If preparation is authorized:

1. Freeze the six parent reports and nine candidate comparisons with complete input
   versions, source hashes, honest synthetic provenance and labels kept out of inputs.
2. Implement isolated builders and the atomic review patch adapter. Test immutable
   parent binding, scope, hostile parent text, native-condition retention, comparison
   coverage, malformed output, stale refs and rejection without automatic repair.
3. Freeze exact requests/builders, scoring, conditional retries, settings, schedule,
   accounting, anonymous full-prose exports and stop rules. Verify a fake-gateway
   end-to-end run, cancellation, unknown outcomes, restart/replay and paired deltas.
4. Update the tracker and present the sealed plan **before seeking live approval**.

Retain J1/P1 as diagnostic evidence and E1 as mechanically successful but
preservation-unqualified. Retain W1's limited gains and successful local craft
repair without promoting its purposes into proof. Factual correctness, preservation
and artistic improvement remain separate axes. A changed fulfilled passage can be
better writing; a tiny diff can retain weak prose. These controls deliberately allow
useful craft edits and mixed outcomes.

Blind human review of the already exported pairs can proceed without new model
calls. Broader qualification still requires the accepted
[weighted rubric, hard gates, full intended Cloud corpus and comparable baseline](../../open_hollywood_bible/product_contract_and_benchmarks.md).
This diagnostic review is not a new mandatory human checkpoint or production graph
role. **Step 19 IN PROGRESS; Step 20 NOT STARTED; canary remains ON HOLD.**

## Local evidence

Private diagnosis: `data/diagnostics/fulfillment-repair-surface-review-diagnosis-2026-10-18/`.
The source closure is
`fbc4939b3ce2ddf1c19d74bb011426e15f587c5ca1cc5c71f32bacfffb224e3b`.
Offline verification checks 488 sealed live files, 56 preparation/operator files,
142 dependencies, source report and predecessor seals; replays 46 attempts and
26 skips; and records five annotated review copies plus four minimal writer copies.
Full rejected-response/request inspection and all six W1 edit lists remain private.
Counterfactuals are not new model successes or eligible production sources. Network,
discovery and inference calls during this diagnosis: **zero**. Production prompts,
validators and historical evidence are unchanged.
