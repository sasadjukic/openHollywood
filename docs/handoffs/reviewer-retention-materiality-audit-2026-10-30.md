# Recovered pairs, exact copying and explanation materiality

Date: **2026-10-30**. **COMPLETE — local audit and verification only.**
Inference and daemon calls: **zero**. Production **prompt 61 / graph 9 /
fulfillment policy 1** unchanged; live calls **PAUSED**, canary **ON HOLD**.

The three BS/PO recoveries and all seven precision annotations are preserved as
regressions. The principal new finding is a coverage gap: **all 80 discovery and
decision assessments used sentences copied exactly from original to revision**.
Those are **20 unique passages in ten families**, repeated across two arms and
two presentation orders. All 80 corresponding canonical-assignment-to-revision
comparisons differ literally. Neither fact invalidates their correct semantic
retention judgments, but the run does not establish discrimination between
meaning-preserving paraphrases and copied sentences whose context changes their
meaning.

Keep semantic retention, literal identity and explanation reliability as separate
measurements. A false literal-comparison assertion is a critic-report defect;
it does not automatically establish a missing story event or justify rewriting
the prose. A correct literal match does not establish the event either.

## Preserved evidence and unchanged results

Source: [BS/PO source-provenance results](../benchmark_reports/reviewer-provenance-v61-results-2026-10-29.md).
Private local bundle: `data/diagnostics/reviewer-retention-materiality-audit-v61-2026-10-30/`.
As with the preceding diagnostics, `data/` is Git-ignored; the public handoff
documents describe evidence retained in the local workspace.

| Material | Count / bundle file |
| --- | --- |
| Byte-identical raw responses, with original envelope and opaque thinking retained | 40; `captures/<trial>/raw-response.json` |
| Source-bound component regressions with raw and bound assessments, sealed inspection and historical metrics | 280; `captured-regressions.json` |
| All matched BS/PO pairs and their conditional controls | 20; `bs-po-pairs.json` |
| Recovered pairs | 3; `label-recovery-pairs.json` |
| Raw PO premise judgments, bound witnesses and original inspection | 60; `po-primitive-regressions.json` |
| Definite and qualified precision annotations with both explicit text comparisons | 7; `precision-regressions.json` |
| Historical primary and sensitivity distinction | `precision-sensitivity-preserved.json` |
| Discovery/decision text-identity census | 80 observations; `retention-copy-audit.json` |
| Authored semantic, copying and materiality contrasts | 21; `authored-retention-fixtures.json` |
| Replayed actual production-rendering probes | 3; `production-rendering-probes.json` |

Recovered targets remain **K2-RO, N5-OR and N5-RO**, component **C02.A01**.
K2 changes from BS *uncertain* to PO *unsupported* for complete-source
insufficiency, while the event remains uncertain. Both N5 presentations change
from BS *unsupported* to PO *uncertain* for unresolved equal-authority clock
conflict. Their BS reasons already identify the relevant source facts: these are
label recoveries, not newly recovered evidence noticing. PO's target verdict
remains explicitly application-derived from inspected premises.

The original **BS 17/20 versus PO 20/20** usable targets, **60/60 PO premises**,
**193/200** conservative assignment/craft usability and **three protected
PO-loss pairs** remain unchanged. The two existing sensitivities remain
**198/200** and **200/200**, not replacements for the frozen primary result.
The outcome remains **retain limited evidence, no advancement**.

The seven precision records are:

- **C-PO-N8-OR, C01.A01/A02:** two definite false word-for-word comparisons with
  explicitly named assignment references C002/C003.
- **C-BS-N5-OR, C01.A01/A02; C-PO-N2-OR, C01.A01;
  C-PO-N4-OR, C01.A01/A02:** five ambiguous “verbatim” comparison referents.
  Original-to-revision equality is true; assignment-to-revision equality is false.

The application can settle those two explicit text comparisons without inference.
It cannot establish which comparison an ambiguous explanation intended from
string equality alone. Preserve that uncertainty rather than treating all five
as definite falsehoods or automatically accepting them.

Source analysis seal:
`521af5ae096cb44ae20532bdc24cef01da13aa98f05e0d978ee84548577af410`.
The new bundle binds exact requests, full scenes/context, claims, source versions,
offsets, raw captures and old inspection through `sources.json`. Raw thinking is
not used as semantic evidence. No historical gold, notes, score or report is edited.

## Prospective contract

| Question | Required evidence | What it cannot establish |
| --- | --- | --- |
| Is the assigned meaning retained? | Independently inspected complete requirement: actor, event, polarity, modality, attribution, time and endpoint scope | Literal overlap, similar wording or a valid citation alone cannot prove fulfillment |
| Are the selected spans identical? | Explicit original-to-revision or assignment-to-revision pair, exact artifact versions, field pointers, text hashes, offsets and quotes | Equality says nothing about truth, actor identity, surrounding quotation, event realization or literary quality |
| Is an explanation error material? | Source inspection plus its effect on the inspected conclusion, evidence basis or repair recommendation | A keyword such as “verbatim,” a correct label or a small prose difference is insufficient |

The offline `retention_contract.py` prototype compares exact Unicode code points,
without whitespace, case, punctuation, Unicode-form or tense normalization.
Unavailable text produces **unavailable**, never equal or unequal. Stale versions,
wrong source roles, changed fields, invalid offsets, invented quotes and duplicate
source identities are rejected. A receipt is tied to a selected span and pair;
it is not a whole-scene preservation certificate. The inventory and span alignment
are authored/inspected inputs, not an implemented automatic semantic aligner.

The materiality prototype consumes **already inspected** semantic and explanation
judgments. It neither extracts claims nor decides truth from prose or model
reasons. Its prospective outcomes are:

- **Incidental report-precision error:** a false exactness assertion accompanies
  independently established complete semantic fulfillment, and correcting that
  assertion changes neither the inspected conclusion nor repair advice. Keep
  the report error visible; do not manufacture a manuscript defect.
- **Material review error:** an erroneous fact, source scope or literal claim
  affects the conclusion, invalidates its evidence basis or drives a repair.
  Exactness is material when exact copying is itself explicitly required.
  Correct the review before relying on it; this is still not automatic writer
  authorization.
- **Unresolved referent or unreviewed input:** retain adjudication status. Do not
  silently turn an ambiguous assertion into a pass or a definite factual error.

This limited prototype permits incidental treatment only for independently
checked text-equality overclaims. It conservatively routes other explanation
errors to review; it is not a general classifier of literary severity.

Applied only as a **prospective shadow policy**, the two definite N8 assertions
are incidental to independently inspected semantic fulfillment; the five
ambiguous assertions remain unresolved. This does not assert how the model
internally reached its answers and does not rescore the historical run. These
diagnostic reports contain no writer repair instruction; that does not prove
the same errors would be harmless in a production repair route.

The authored contrasts include paraphrase and intentional action that retain a
decision; an exact sentence in a fictional quotation or about another actor;
negation; conditional-only evidence; unavailable text; and an actual earlier
decision followed by reversal. The latter retains the **decision event**, while
the same passage violates a separately specified **unsold-at-end condition**.
This avoids repeating the original event-versus-endpoint conflation. Explicit
copy requirements, unnecessary-repair advice, invalid source scope, ambiguous
referents and missing inspection have separate controls. An intentionally false
but well-formed semantic input demonstrates that the policy is not a truth
detector. No authored fixture is counted as a model recovery.

## Production applicability and story quality

Current [assignment guidance](../../apps/api/open_hollywood_api/services/production_critic_obligations.py)
already accepts actions and indirect narration when they establish the complete
assigned fact; literal plan wording is unnecessary. Independent craft defects
remain possible even when obligations are fulfilled. The audit therefore does
not justify making literal copying a general prose-preservation requirement.

The three production-rendering probes reproduce the
[previous scope audit](reviewer-production-scope-audit-2026-10-28.md) exactly.
They still show that the same artifact version can have a filtered or compacted
reviewer view. Exact evidence references establish identity and quotation,
not entailment or source completeness. The new receipts cannot fill omitted
context, identify an authoritative observation pair or create PO's semantic
premises automatically. An assignment is an obligation, not an observation.
These applicability limits are not evidence that production filtering caused
the historical diagnostic failures.

Human review remains focused on feel, flow, character and story-breaking details.
Machines should prepare exact-comparison receipts and source locations. Neither
literal preservation nor a correct semantic label establishes enjoyable fiction.
Necessary craft revisions may change wording substantially; rote restatement
should not earn credit merely for resembling an assignment. No writer, quality
preference or full-workflow outcome is tested by this audit.

## Verification and next decision

**217 offline tests pass: 141 audit tests plus all 76 preceding execution tests.**
Ruff lint/format and strict mypy pass on six local scripts. Tests block real HTTP
and replay historical scoring, all three recoveries, every PO premise, precision
bindings, both text comparisons, unsafe context shortcuts and production probes.
**8,227 historical/production fingerprints** verify. The first verification passed
all 217 tests but found two strict-typing references to an unexported imported
module; direct test imports fixed them. Both verification records are retained.
No application code changed; unrelated frontend and application build suites
were not rerun. The preceding preparation's 455-test record remains intact.

The materially new question is whether explicit application-owned text-comparison
receipts help a reviewer keep literal identity separate from semantic fulfillment
when the two deliberately diverge. The separate
[32-call PO/EX proposal](reviewer-retention-materiality-proposal-2026-10-30.md)
uses unchanged PO controls, known precision anchors and six fresh full-scene
families in both orders. It is **proposed only: not prepared, frozen or approved**.
No inference is needed merely to confirm the existing wording mismatches or to
decide this local policy.

All fourteen issue bodies and user-posted GitHub links remain intact; no external
issue is edited or closed. **Step 19 IN PROGRESS; Step 20 NOT STARTED.** Production
prompts, Blueprint approval and the earlier nine human ties are unchanged.
