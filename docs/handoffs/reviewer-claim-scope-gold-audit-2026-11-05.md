# Claim-scope and whole-claim gold audit — 2026-11-05

**Complete locally. No inference, input-count, catalog or daemon calls.**

The [Sol-high interpretation results](../benchmark_reports/reviewer-interpretation-v61-results-2026-11-05.md)
remain **M 48/56 grounded, E 50/56**, with eleven citation-only and three
semantic-category mismatches overall. The frozen screen still fails. This audit
preserves the original gold, responses, inspections and scores; it does not publish
a corrected accuracy score.

The main finding is an evaluation-design limitation: **the selected claim, the
gold proposition and the required evidence must ask the same question**. Several
remaining disagreements do not satisfy that condition. The stronger model's final
reasons exposed distinctions our authored tests had collapsed. That is evidence
about this diagnostic, not proof that the model or production workflow is reliable.

## What the local review found

| Audit finding | Affected slots | Consequence |
| --- | ---: | --- |
| Bare event wording, assignment-authority evidence criterion | 12 fresh Q001 controls | Separate observed choice from the requirement to choose |
| Mixed event, means and editorial-effect claim | All 8 mixed targets | Do not reuse these as clean factual controls, including the targets whose labels passed |
| Procedure-occurrence gold omits the asserted by-identifying mechanism | 2 I1 mixed targets, included in the eight above | Whole-claim gold must account for the causal qualifier |
| No newly identified conflict under the recorded contextual scope | 92 other slots | Preserve the specific scope and evidence limits; this is not a new accuracy denominator |

These are slot counts across repeated presentations and formulations, not counts
of independent stories. Twenty slots need redesign before reuse as clean factual
tests. The scope review covers all 112 slots, including successful controls.

### 1. Observing a choice does not prove an assignment requires it

The fresh Q001 report fields are bare statements such as “Mara chooses to
investigate the disputed tune's attribution.” Their location is a generic
`/claims/*/assessment` field. They do not say “the assignment requires.” Yet their
frozen evidence criterion asks for the current assignment's choice obligation.

The same sentence also appears in an authoritative plan outcome. That source
location makes it an assignment; copying its words into a report does not preserve
the normative operator automatically. The report summary, which mentions an
alleged assignment breach, does not uniquely resolve the selected field's meaning.

All twelve final reasons support the observed choice with genuine draft action.
Eleven omit assignment authority; I2 mixed/CP also cites it. The **eleven original
citation failures and the I2-CP paired control loss remain recorded**. They are not
eleven false judgments that a choice occurred, or eleven failed quote locations.

For future gold, distinguish:

- **Requirement:** what the current assignment explicitly demands, with its exact
  version/field and applicable conditions.
- **Occurrence:** what the supplied complete draft depicts, including purposeful
  action that establishes a decision without a literal declaration.
- **Compliance:** the relation between that requirement and that occurrence,
  including the whole endpoint. This needs both sides.

A requirement can exist without fulfillment. An event can occur without being
required. A later endpoint breach does not erase an earlier fulfilled decision.

### 2. I1's true event does not establish the stated means

I1's mixed allegation says that the later private-signature turning point is
consumed **“by identifying the tune.”** Its supported gold followed the private
procedure's occurrence but did not separately adjudicate that qualifier.

The complete sources distinguish general tune identification through score
comparison from private verification through half-speed playback, four taps and
recognition of the doubled fourth tap. Both mixed final reasons acknowledge the
verification, then reject the stated means. Both explicit-procedure targets are
supported with adequate evidence.

Those two original label mismatches remain in the semantic category. They are
**not unambiguous failures to recognize the performed procedure**. The audit does
not flip their gold to unsupported: the mixed sentence also retains an editorial
reading, so replacing one collapsed interpretation with another would repeat the
design problem. Causal or means relations need their own whole proposition and
evidence criterion. Co-occurrence, narrative order and a shared subject do not
establish the asserted mechanism.

### 3. Passing mixed targets still contain the scope ambiguity

All four families' mixed targets combine a specific planned procedure, an earlier
general identification and the editorial word “consumes.” H1's current PC response
explicitly treats consumption as a sequencing criticism; its CP response answers
whether the specific event occurred. The saved historical H1 responses took the
editorial reading in both orders despite identical count/generation bodies and
work fingerprints.

The local replay confirms that history. It does not establish why the interpretation
varied or prove an identical provider backend snapshot. It provides no new evidence
of a provider fault.

I2 and I3's mixed labels passed, but a favorable label does not make the mixed
sentence a clean factual test. Their explicit controls preserve a useful contrast:
I2's complete draft does not depict the planned arithmetic, while I3 explicitly
negates and postpones the private exchange. Neither establishes an artistic judgment
about how much later payoff remains.

The eight explicit targets are promising feasibility evidence. They are different
propositions from the mixed targets, so they do not demonstrate eight same-claim
repairs or qualify production routing.

## Whole-claim and evidence contract

The local prototype binds each authored scope review to the exact whole selection,
containing report field, request, case and source sections. It checks that declared
claim predicates, gold predicates and evidence predicates agree, and retains an
explicit inventory of unresolved material qualifiers. An editorial-effect predicate
cannot pass through this prototype as a clean factual control.

The review retains these distinctions in the other controls:

- Compound events require every material conjunct, such as both dates and their
  comparison, or tune identification and audible signature recognition.
- Attribution, negation and modality belong to the proposition. Someone else's
  accusation or belief is not the protagonist's assertion.
- A complete draft with no depicted procedure differs from an explicit refusal,
  and both differ from an unavailable continuation. The last can warrant uncertainty
  with no invented evidence.
- H1's “immediately” control retains its declared **present-scene resolution**
  reading. It does not certify measured elapsed time, opening position or pacing
  quality, and should not become an unqualified temporal control in a new test.
- Both original H1-CP endpoint-relation inspections remain intact. Component
  labels and shared quotations do not automatically establish a whole relation.

The quotation contract also remains unchanged: an exact quotation locates a whole
immutable section. Location is not entailment. Complete context is available for
inspection, but uncited neighboring sections do not supply credited evidence.
The prior explicit materiality decisions remain intact, including ancillary endpoint
concessions in H1 E/PC Q003 and I1 E/CP Q002. This audit neither adds a new citation
requirement to those judgments nor retroactively supplies their missing citations.

**The prototype checks authored declarations, not natural-language truth.** It can
reject an identity mismatch, missing authority or declared qualifier omission. It
cannot prove that the author noticed every qualifier, selected the only possible
reading, or authored the correct gold. These are identified assistant source
reviews, not independent blind human judgments or model-generated grades.

## Application implications

The production audit confirms existing protections rather than a missing instruction:

1. `assessment_work.SelectedStatement` preserves exact selections, and
   `assessment_result.AssessmentScope` binds work, request and active units. Those
   are identity boundaries; they do not specify an event/obligation/means predicate.
   Successful binding deliberately leaves support, craft and edit necessity unassessed.
2. `_scene_assignment_contract` projects the current plan, and
   `_scene_boundary_contract` already separates decision, attempt and established
   result. A later stronger proof does not license an earlier forbidden result.
3. `REQUIREMENT_BASIS_RULE` already distinguishes facts, order/immediacy and causation.
   `COMPLIANCE_CRAFT_RULE` preserves genuine independent craft defects while keeping
   preferences outside mandatory repairs. `comparison_error` checks structure and
   finding coverage, not semantic truth.

The next improvement should therefore make the **assessed proposition and its
evidence obligation reviewable before inference**, rather than add another general
prompt reminder. The local scope representation is not integrated into production
and does not change the accepted engine contracts or public schemas.

Machine checks can certify exact source/field binding, selected scope, delivery and
declared design consistency. They cannot turn a plausible effect on pacing into a
verified event, a required repair or proof of better writing. Genuine craft problems
remain eligible for separate assessment. Future human evaluation should focus on
overall feel, flow, character and story-breaking details, supported by prepared
mechanical evidence; no new routine human checkpoint is introduced.

## Preserved artifacts and verification

Private bundle: `data/diagnostics/reviewer-claim-scope-gold-audit-2026-11-05/`.

- **368 exact captured files**, with **4,929 historical fingerprints** verified.
- All **112 original judgments**, **56 mixed/explicit unit pairs** and **two H1
  same-request histories**, retaining all seven historical/current assessments
  for each order. All controls and the paired control loss remain visible.
- All **196 evidence quotations** replay to their original section views.
- **112 authored scope records** and **28 literal full-work renders** covering
  every target and fresh Q001 control; original reasons, gold and full sources remain.

**284 offline tests pass**: 145 local scope/provenance/rendering regressions,
16 prior result-authentication tests and 123 tracked assessment tests. Nothing is
deselected. Mutation checks cover altered whole claims, source authority, requests,
fields, offsets, assessment reasons, unsupported authority promotion and missing
scope. Unavailable-source uncertainty remains valid without fabricated citations.

Repository Ruff, formatting and strict mypy pass for **224 files**; the same checks
pass separately for **five audit scripts**. Deterministic replay reproduces the
original scores and new design findings. The verification logs retain exact commands
and outputs. Archived Python remains inert. No provider credentials were loaded.
No frontend or production application code changed; frontend checks are inapplicable
and a full repository test run is not claimed.

## Proposed next step

Prepare a **16-attempt, scope-separated repeatability diagnostic**, using the same
Sol-high model, U evidence contract, complete-context presentation and seven-claim
workload. This is a materially different question: **are unambiguously scoped
factual judgments and their evidence stable when requirement and occurrence vary
independently?** It is not another wording arm scored as a repair of the old claims.

Proposed design, subject to local preparation and separate approval:

1. Author four fresh complete scene families crossing **required/not required** with
   **performed/not performed**. State optionality explicitly where applicable;
   do not infer it merely from silence. Counterbalance supported and unsupported
   means relations, with evidence that distinguishes an actual means from a separate
   event. Retain genuine endpoint violations as independent controls.
2. Use seven separate, fully specified claims per family: current requirement,
   observed choice, specific procedure, asserted means, endpoint compliance,
   speaker attribution and unavailable-continuation content. Keep literary
   consumption outside factual gold. Determine every material clause, expected
   label, full-source authority and adequate-evidence criterion **before responses**.
3. Run each family in both source orders, twice: **4 × 2 × 2 = 16 attempts**, with
   **112 slots**. Preserve the same semantic workload and exact request bodies within
   each repeated family/order; record separate attempt identities. Interleave the
   second repeats. Count and generation payloads retain full prose/context.
4. Freeze original-style delivery/binding/whole-claim/evidence scores plus a separate
   repeatability table. A correct support label without authority coverage fails the
   grounded judgment. Predeclare a feasibility gate requiring grounded results on
   every obligation/event/means/endpoint slot in both orders and repeats, without
   losses on the remaining controls. Any mismatch remains visible; no post-hoc
   gold repair or corrected aggregate. Passing would justify only the next bounded
   read-only integration check, not writer authority or production promotion.
5. Preserve the previous per-attempt resource ceilings during preparation unless
   explicitly amended; cap generation attempts at sixteen, story-bearing input
   counts at sixteen and catalog reads at sixteen. No retry, fallback or extra probe;
   stop on the first terminal delivery/resource/identity failure and retain unknown
   usage. Semantic failures remain scored through the fixed schedule.

First apply the local claim/gold design check to these newly authored cases and
inspect their complete sources. If their intended scope cannot be made explicit
without losing the claim's meaning, keep them out of this factual diagnostic rather
than spend calls. No new cases, requests or live approval are frozen by this audit.

If this test is stable, the production-facing next step is a small, tracked **read-only
claim-scope declaration and audit display** beside the existing assessment component.
Keep unresolved editorial or causal scope visible. Any later use to authorize edits
needs its own evidence and story-quality evaluation. If the test is unstable, retain
the failures and limit automatic factual reliance instead of repeating equivalent
rephrasings or increasing reasoning without a new hypothesis.

All fourteen issues remain open; issue bodies and posted GitHub URLs are unchanged.
**Step 19 IN PROGRESS; Step 20 NOT STARTED; production prompts/profiles unchanged;
live calls PAUSED; full workflow canary ON HOLD.**
