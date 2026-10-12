# Separate facts, order and causation in critic guidance v55: 2026-10-12

**Implementation, local verification and the approved twenty-probe comparison
are COMPLETE; the remedy is NOT QUALIFIED.** Final assignment-check pairs improve
from 16/20 to 19/20 in this matched sample, with both causal-waiver false passes
corrected on first review. One improvement occurs only during a structural retry;
first-review pairs are 18/20. Repair advice still adds unsupported requirements,
and one false blocker remains. All twenty reviews validate in twenty-one calls.
Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.

## Problem and focused change

The [v54 order/causation diagnostic](order-causation-v54-2026-10-12.md) found that,
at both seeds, the same reversed chronology was blocked when order alone was
required, passed incorrectly after a causal waiver was added, and blocked again
when order and causation were stated separately. Correct blockers could also
produce repairs that invented causation or weakened a required onset time.
Both unconstrained-fact cases were incorrectly blocked. Overall, 16/20 native
check pairs were correct; all twenty action-based outcome decisions were judged
correctly. An identical historical request had changed judgment, so repeated
observations must be treated as descriptive evidence, not guaranteed behavior.

v55 replaces `REQUIREMENT_BASIS_RULE` and `MINIMUM_REPAIR_RULE` in the existing
critic. It adds no instruction block. Together the two constants shrink from
1,446 to 1,345 characters including the separating space. The replacement asks
the critic to:

1. Assess required facts, temporal order/immediacy and causation separately.
2. Cite the assignment field or applicable canonical version/field and the words
   requiring each relationship, then compare them with draft evidence.
3. Apply permissions only to the named relationship. Optional causation leaves
   required order intact; order alone does not require causation. An exemption
   cannot satisfy a different missing obligation.
4. Carry those distinctions into every native and restated repair. Repair the
   missing fact or violated relationship while preserving fulfilled facts and
   the scene endpoint. Do not invent triggers for order-only repairs or weaken
   required immediate onset to later onset.
5. Require completed action only when supported by the assignment or applicable
   canon. Keep unassigned staging, motivation and craft preferences optional.

The exact complete-fact definition of `met`, independent mandatory checks, valid
actions/indirect narration, applicable canon and v54 optional-craft/verdict rule
are preserved. Schemas, validation, consolidation, writer instructions, graph
routing, budgets and critic retry policy are unchanged. Prompt version advances
to **55** for provenance; graph remains **9**, retry policy **17**. Three existing
tests update their current-version expectations only.

Both rule constants already reach initial and revision reviews, structural
retries, and local/cloud request paths through the existing critic instruction
assembly. This is model guidance: no deterministic code infers whether a story
fact, chronology or causal relationship is actually fulfilled.

## Frozen comparison

Repeat the exact twenty cases from the completed v54 diagnostic, using the same
private OH-V01-001 scene 1 context, drafts, synthetic plans, artifact identities,
seeds **19101/19103**, and case order. The second seed retains reversed case order.
Only the two system-guidance constants differ in the model-visible request.
Production stays fixed at v55 throughout execution.

The core matrix remains four wordings by two drafts by two seeds: sixteen probes.
Each cell below gives the expected turning-point/outcome pair.

| Assignment relationship | Pull before touch | Touch before delayed pull |
| --- | --- | --- |
| Order alone | unmet / met | met / met |
| Same order plus the original causal waiver | unmet / met | met / met |
| Separately stated facts, required order and optional causation | unmet / met | met / met |
| Both facts required; neither order nor causation required | met / met | met / met |

Four controls complete the matrix:

- The delayed draft with explicitly required immediate causation, at both seeds:
  unmet / met. Its full minute without pull violates the required immediate onset.
- The saved draft missing touch and leaving entry undecided, under unconstrained
  facts at both seeds: unmet / unmet. Relationship permissions cannot excuse
  missing facts or a missing decision.

All core drafts retain the same action-based entry decision at the threshold.
The delayed draft excludes immediate onset; it does not disprove every possible
delayed causal link. No case, expected label or seed was selected after seeing
v55 output. Expected labels remain private evaluation metadata outside requests.

## Evaluation rules before execution

Compare each v55 case with its v54 counterpart, and compare wordings within
each unchanged draft/seed. Report mixed seeds and regressions directly.

- Required order must survive the causal waiver. Unconstrained facts must remain
  met without demanding an unassigned dramatic or causal connection.
- All eight ordered core cases should remain met/met, preserving the indirect
  entry decision. The explicit immediate-cause and both-missing controls must
  remain blockers for their actual unmet obligations.
- Read complete native, generic and consolidated repairs. An order-only repair
  must permit noncausal order; a missing fact must not acquire invented timing
  or motivation; immediate onset must not become onset after release or delay.
  A correct native status alone does not qualify its repair advice.
- Inspect evidence references, source authority, summaries, scores, raw and
  canonical verdicts, optional scope, and duplicate handling. A false unmet is
  still an application blocker; an optional-only revise is still problematic
  even if it creates no mandatory repair targets.
- Record first/final validity, exact structural failures, retries and semantic
  drift independently. Do not rerun a valid review to obtain a preferred judgment.

Both rule constants change together, so the test cannot attribute any effect to
an individual sentence. This is one scene and model at two seeds, compared with
a historical baseline rather than a contemporaneous randomized arm. It is not
writer-repair, full-story, cross-provider, preference or cost acceptance. There
is no new live independent-craft defect or synthetic applicable-canon control in
this matrix; existing local coverage does not establish those live sensitivities.

## Preparation and local verification

- All **133** sealed v54 evidence files, the prior report and source database
  retain their recorded hashes. The historical plan and sealed outputs are intact.
- All **20** saved v54 responses replay under current materialization to identical
  canonical results and boundary audits. Substituting the two old constants back
  into each request reconstructs its exact saved v54 messages and response schema.
- All twenty new snapshots preserve inputs, user payloads, schemas, settings,
  budgets and seeds. Runtime source comparison permits only the two constant
  replacements and prompt-version increment; complete-fact, optional-craft,
  validator and graph code remain byte-for-byte unchanged from merge `9600709`.
- **41 focused regressions pass**. The full Python suite passes **966 tests** in
  188.84 seconds. Ruff check/format and strict mypy pass across 194 source files.
- Frontend format, lint and type checks pass; all **11** frontend tests and the
  production build pass. These are local application checks, not live-model proof.

Private material stays in ignored local storage:

`data/diagnostics/relationship-scope-v55-2026-10-12/`

It contains the experiment and assessor, twenty prepared snapshots, the frozen
plan, offline replays, preparation checks, explicit approval, all request/response
receipts, result/audit replays, inspected semantic findings and a closure record.
The approval and execution are bound to this plan hash:

`b069a94f109e1ee9bb9ebce3f59b49ddc006548f9307798387d51f088f6f51ce`

Source database:

`data/benchmarks/v0.1/formal-cloud-v33-repeat-3-2026-10-02/private/completed-snapshot.db`

Source SHA-256:

`71618ce4d66ffd3b8ecc46fa4d034105b4e59aa5a80946b5364272b87caeafb2`

## Approved execution and cost

Use the existing local Ollama daemon forwarding to Ollama Cloud
`gemma4:31b-cloud`, with the same recorded model digest checked before execution.
Twenty fixed critic probes permit at most one existing structural retry each:
**forty calls maximum**. Each call retains a 24,000-input/8,000-output token budget.
The recorded October 8 rates of USD 0.14/M input and USD 0.40/M output give a
maximum reference estimate of **USD 0.26240**. This is separate from actual
charges, which remain unknown.

The user explicitly approved the twenty v55 probes. Execution used **21 calls**:
nineteen first reviews validated, and one needed the existing structural retry.
All twenty final reviews validated. Usage was **279,680 input / 26,322 output
tokens**, or **USD 0.049684** at the recorded rates, below the USD 0.26240 ceiling.
Actual charges remain unknown. There were no writer calls, full-story runs or
canonical artifact writes. Production and all frozen inputs remained unchanged
throughout execution.

## Matched results

| Case, across both seeds unless noted | v54 final checks | v55 result |
| --- | --- | --- |
| Reversed order, order alone | Both correctly unmet/met | Both still unmet/met; both full repairs still demand a causal trigger |
| Reversed order, original causal waiver | Both falsely met/met | Both correctly unmet/met on first review |
| Reversed order, separate relationships | Both correctly unmet/met | Both still unmet/met; seed 19101 now adds unassigned immediacy in the generic repair |
| Reversed order, unconstrained facts | Both falsely unmet/met | Both first reviews still falsely unmet/met; only seed 19101's structural retry becomes met/met |
| Ordered delayed draft, four ordinary wordings | All eight correctly met/met | All eight still met/met and pass, with no issues or repairs |
| Ordered delayed draft, required immediate cause | Both correctly unmet/met | Both still unmet/met; both repairs now retain onset at contact |
| Missing touch and decision, unconstrained facts | Both correctly unmet/unmet | Both still unmet/unmet; both touch repairs still add unassigned order |

Seventeen final native pairs remain unchanged; three improve and none regress.
The two causal-waiver improvements are first-review results. The third is
retry-dependent. These counts measure only the mandatory check pair, not the
correctness of the entire review. All twenty outcome checks remain correct,
preserving action-based decision evidence and rejecting actual indecision.

The lone retry is `s19101-reversed-unconstrained_facts`. Its first turning-point
assessment is **631 characters**, exceeding the existing 600-character limit.
That review acknowledges both facts but demands a dramatic or causal link. The
structural retry changes the turning point from unmet to met, changes revise to
pass, removes its issue and validates. It is not an application-side semantic
correction, and it does not establish reliable first-review interpretation. The
other seed validates its false unmet on the first attempt and retains the false
blocker.

## Repair scope, summaries and consolidation

The full responses show several distinct remaining failures:

- **Order-only repairs still invent causation at both seeds.** At seed 19101 the
  native repair asks for reordering, but the blocking generic restatement demands
  a trigger. At seed 19103 the native assessment, repair, generic issue and summary
  all add causal meaning to the temporal requirement. The broad stroller-as-lure
  world rule does not specify a physical-touch trigger.
- **One separated-relationship repair adds immediacy.** Seed 19101's native advice
  permits temporal precedence, but its generic advice requires the pull to occur
  immediately after contact. Consolidation carries that extra condition into the
  mandatory target. This is an advice regression even though its native status is
  unchanged. Seed 19103 permits a catalyst **or at least** temporal precedence;
  that alternative leaves noncausal ordering sufficient and is not counted as a
  mandatory-causation failure.
- **Both missing-touch repairs add chronology.** One requires touch before or
  during the pull; the other requires it before the pull. Neither follows from
  the unconstrained-facts assignment. Their separate outcome repairs ask for a
  decision and do not unconditionally demand completed entry.
- **A craft preference enters a real blocker.** At seed 19101 with the causal
  waiver, the native order repair is adequate. A minor linked issue says to
  consider hesitation or failed resistance to make contact more meaningful. It
  lacks the prescribed Optional label and is appended as a restatement repair
  to the blocking issue and its `requested_change`. The tentative wording means
  this is ambiguous scope, not proof that a writer would obey it as mandatory.
- **One false obligation survives.** Seed 19103 with unconstrained facts explicitly
  acknowledges both events but labels touch redundant without a meaningful
  connection. Its repair requires triggering or intensifying the pull. This is
  an unsupported mandatory relationship, not an unfulfilled assigned fact.

Thus **five final reviews with real defects add unsupported mandatory conditions**,
one further review mixes a tentative craft preference into a blocker, and one
creates an unnecessary repair from a false blocker. The two immediate-cause
repairs keep onset at the moment of contact; the previous alternative allowing
onset upon release is absent. Their correct timing does not establish writer
success. At seed 19103, the generic rationale overattributes that timing to the
world rule even though the explicit scene assignment supplies it.

All **eleven** final generic complaints link to existing assignment findings.
Consolidation produces **thirteen** mandatory targets: twelve for real missing
or violated obligations and one false target, with **zero duplicate targets**.
This confirms that correct finding identity and deduplication do not ensure
that the appended advice stays within the requirement. The computed next-review
repair tests retain the same excessive or ambiguous `requested_change` text.
No writer was invoked.

Final canonical verdicts are nine pass and eleven revise. Three raw rejects
(both missing-fact controls and seed 19103 order-only) become revise through the
existing mandatory-assignment route, not through a new v55 verdict rule. All
final POV checks are aligned, boundary checks are no-overrun, and the separate
assignment-violations lists are empty.

Correct status also does not guarantee precise explanation. The seed-19101
causal-waiver summary says structural requirements are satisfied while noting
the inverted required order. Some scores and assessments still describe a causal
sequence when only chronology is required. These do not create extra targets by
themselves, but they prevent a claim that the distinctions are consistently
preserved throughout the response.

## Conclusion and next focused step

The shorter replacement provides useful, bounded evidence of better order
judgment: both cases that previously mistook causal permission for temporal
permission now detect the violation. The complete remedy remains unqualified
because unassigned relationships still enter repairs, an unconstrained-fact
false blocker remains, and one improvement depends on retry drift.

Keep the v55 fact checks stable for the next focused change. Require each
mandatory repair, including a linked restatement, to be compared with the exact
supported requirement it repairs before it becomes writer feedback. A correct
order finding must not acquire a causal trigger or immediate timing through a
second recommendation; optional craft suggestions must retain separate optional
scope. Use the saved responses and controlled local cases first, then a bounded
matched critic comparison. Do not use word matching to infer story semantics or
blanket-drop minor craft findings. Track the remaining false blocker and retry
drift independently rather than marking them resolved by this repair change.

This recommendation is not implemented in this batch. No additional calls or
broader story tests were run. The frozen plan, all twenty-one response replays,
prior evidence and source database were verified after execution and the final
evidence is sealed locally.
