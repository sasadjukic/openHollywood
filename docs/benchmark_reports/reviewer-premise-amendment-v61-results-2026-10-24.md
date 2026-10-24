# Amended DeepSeek D2 / premise-check comparison — 2026-10-24

**Completed: 32/32 model calls, sixteen per arm, zero retries.** The frozen
decision is **`retain_limited_evidence_no_advancement`**. The premise-check card
produced one qualifying semantic recovery, but lost four usable paired controls
and one valid delivery. It does not qualify for advancement.

Production remains **prompt 61 / graph 9 / fulfillment policy 1**. The full
workflow canary remains **ON HOLD**. No writer run, production prompt change,
new human preference judgment or further inference is authorized by this report.

## Authority and execution

The user approved the [amended plan](../handoffs/reviewer-premise-baseline-amendment-2026-10-24.md),
including full unpublished prose/context to Ollama Cloud through the local daemon.
The amended plan SHA-256 is
`9f3421d30db0e361736146d9adecdb7bf81fd41dd81a46ad422beb63c6d37810`.
The original [32-call design](../handoffs/reviewer-premise-frozen-plan-2026-10-24.md)
and its scoring remain unchanged. Its [earlier execution attempt](reviewer-premise-v61-results-2026-10-24.md)
stopped before inference: **zero earlier calls + 32 amended calls = 32 total**.
The old terminal ledger and its missing observed-version value remain intact.

This execution verified **Ollama 0.40.10** and
`deepseek-v4.1-flash:cloud`, digest
`e04da138d31e0c9468e982e1ae9503d06cb7e170caa16a90c17d931c4aa140f8`.
All **65 initial/before/after version observations** were captured and sealed,
with matching expected/observed versions and exact response bytes. Selected-model
checks matched the frozen metadata. Model metadata does not establish the
immutability of an upstream cloud service; this report claims the identities
actually observable through the daemon.

All 32 prepared requests and wire payloads matched the freeze. Temperature 0.2,
top-p 0.95, seed 20261022, thinking disabled, nonstreaming delivery, schemas,
cases, source artifact versions and stop rules were unchanged. The first-eight
sentinel continued with **D2 4/4 valid, PC 3/4 valid** and no blocking signature
threshold. Every generation returned HTTP 200 with a normal `stop`, recorded
usage and no thinking output. There was no transport stop, truncation or retry.

## Results under the frozen rules

“Fully usable” requires the scored labels, supported target judgments, every
explanatory field supported, and any required contradiction detected. It is
deliberately stricter than delivery validity or a correct main verdict. It is
not a measure of literary preference or whole-story quality.

| Measure | Unchanged D2 | D2 + premise-check card (PC) |
| --- | ---: | ---: |
| Completed calls | 16/16 | 16/16 |
| Structurally valid reports | 16/16 | 15/16 |
| Fresh-case valid reports | 8/8 | 8/8 |
| All scored labels correct | 11/16 | 11/16 |
| Supported target judgments | 14/16 | 14/16 |
| Fully usable reports | 9/16 | 6/16 |
| Actual crate contradiction detected | 2/2 | 2/2 |
| Optional requests correctly recognized, with support | 10/10 | 9/10 |
| Valid reports containing an unsupported explanation | 7/16 | 7/15 |
| Unsupported explanatory fields | 12 | 13 |
| Uncertain explanatory fields | 0 | 2 |

All **31 valid reports / 387 assessment fields** received an operator factual
audit against the complete source pairs. The export hid arm/order identities;
notes with exact source versions, offsets and claims were sealed **before** the
key was decoded. Wording can reveal a condition, so this is a masked operator
audit, not an independent blind human preference study. The rejected report was
inspected separately without repair or semantic credit.

The candidate met the absolute delivery floors of 15/16 and 7/8 fresh. It failed
the required three semantic recoveries across two families, a historical case
recovered in both orders, and the protected no-loss conditions:

- **One semantic recovery:** A00, revision-first (RO). D2's unsupported claim
  that broadcasting invalidates the retained brother-question decision becomes
  a fully usable PC report. There is no both-order historical recovery and no
  delivery-only recovery.
- **Four paired usable losses:** B10 original-first (OR), E-compound RO,
  F-narrow OR, and I-cause RO.
- **One valid-delivery loss:** B10 OR; it also loses a supported target and
  optional-request result because the whole report is rejected.
- **An additional target loss:** A00 OR, where PC invents an unidentified
  audible voice in a revision that establishes only hiss and an unidentified
  recording maker.
- No lost crate-contradiction detection and no newly observed blanket rejection
  of a legitimate fresh contrast.

There were **seven eligible D2 premise-failure pairs across four families**:
A00 in both orders, B10 RO, G-voice in both orders, and H-before in both orders.
The frozen opportunity screen was therefore sufficient. Independent delivery
and regression failures also prevent advancement; they cannot be hidden by
reclassifying the opportunity denominator.

### Complete-report outcome by case

Each cell below summarizes full usability, not just its main task verdict.
OR means original displayed first; RO means revision displayed first.

| Case | D2 OR | D2 RO | PC OR | PC RO |
| --- | --- | --- | --- | --- |
| A00: radio | Unsupported deferred-question premise | Unsupported premise; wrong outcome label | Invented voice | **Usable** |
| B10: costume | **Usable** | Invented dependency; wrong group label | Invalid evidence refs | Invented consultation condition |
| E-compound: footbridge | **Usable** | **Usable** | **Usable** | Unsupported inspection premise and added-detail claim |
| F-narrow: bakery | **Usable** | **Usable** | Inaccurate “identical clause” claim | **Usable** |
| G-voice: ferry | Invented wait-for-dispatcher condition | Wrong group label; unsupported corroboration | Imported prior action/condition | Wrong group label |
| H-before: observatory | Wrong group label; false contradiction premise | Wrong group label; false contradiction premise | Wrong group label; false contradiction premise | Wrong group label; false contradiction premise |
| I-cause: nursery | **Usable** | **Usable** | **Usable** | Wrong group label |
| J-duplicate: archive | **Usable** | **Usable** | **Usable** | **Usable** |

## What failed, and what worked

**The delivery failure is reference-type confusion.** `P-B10-PC-OR` supplies
`[O016, R015, U02, U03]` as G02 evidence. U02/U03 are real changed-unit IDs in
the input, but they are not prose catalog refs. The rule accepts distinct O/R
catalog references only. The raw answer is complete JSON, with 1,026 output
tokens and a normal stop; this is neither truncation nor an eight-reference
overflow. It contains no duplicate keys or extra craft fields. No ID was
translated, dropped or silently accepted. The explanation also repeats a
consultation-before-decision premise, but the rejected report earns no semantic
score even where individual statements look useful.

**The card did not consistently separate factual relations from plausible story
logic.** Both arms still build extra conditions around retained facts. In
`P-B10-PC-RO`, agency says Tomas plans to consult before **deciding** what should
happen; the source says before **explaining** what he thinks should happen.
`P-G-voice-D2-OR` treats leaving an identity question for the dispatcher as a
constraint on admitting a passenger. `P-G-voice-PC-OR` additionally imports the
original's replaced locked-gate action as an earlier choice within the revision.
The independent no-unpicking/locked-gate endpoints really are violated, but that
does not make the additional explanations true.

**A real violation can attract a second, false contradiction.** All four
H-before reports correctly accept the retained discovery/decision/closed roof
and reject rotation before consultation. All four also contain at least one
claim that rotation *before consultation* contradicts the statement that
consultation *has not happened yet*. Those facts agree. The actual conflict is
with the separate promise/prohibition not to rotate until consultation. This
distinction was applied consistently across both arms; reasonable criticism of
the real intention/action conflict was retained. It does not establish that a
character acting against an intention is inherently bad writing.

**Correct labels do not guarantee supported explanatory premises.** In
`P-E-compound-PC-RO`, the fact assessment recognizes the independent post-flood
inspection rationale, while naturalness says that rationale presupposes a split.
The source explicitly says the inspection was due anyway. The same report calls
unchanged sensory/domestic details “added.” Conversely, all four I-cause reports
properly recognize the real causal gap: the original makes the crack the sole
reason for a glazier visit, and the revision removes it without supplying another
reason. Losing specific urgency is a permissible reading of E-compound; saying
its independent reason presupposes the removed defect is not.

**Relation labels remain a separate failure.** Eight valid reports miss at least
one frozen group label: D2 B10 RO; both arms/orders of H-before; both arms G-voice
RO; and PC I-cause RO. Seven use `direct` where the contract expects `unrelated`;
D2 B10 RO invents a dependency on an unsupported change within one complete edit
group. The frozen definition of direct is “does what the requested task asks,”
not merely “touches or violates a requirement.” In particular, the H-before
reports describe the prohibited action correctly while assigning the wrong
relation label. This should not be reported as failure to notice the action or
as a newly solved event-attribution issue.

**Some primary failures are narrow wording errors.** The 25 unsupported fields
comprise **22 decision-relevant invented constraints/events/causal or factual
relations** and **three narrow wording inaccuracies**. The latter are PC's
“identical clause” description of differently worded crate assertions, PC's
claim that unchanged sensory details were added, and D2's claim that turning
away from a departure board confirms admission when the same movement occurs
in the original without admission. Those three still fail the frozen complete
support rule, but are not equivalent to losing the main story fact. Two PC
craft premises were recorded as uncertain, not forced into true/false: whether
“withheld ferry” is figurative shorthand and whether unpicking one seam resolves
the coat's fate. Neither uncertainty creates an eligible semantic recovery.

The main successes remain useful diagnostic evidence. All 31 valid reports have
correct task, endpoint and mandatory-flag labels. One D2 A00 report mislabels the
retained decision as uncertain; all other fact labels are correct. The separate
application mandatory aggregate matches the model flag and frozen scope on
**31/31 valid reports**, without repairing a primary report or authorizing a
writer. All four F-narrow reports detect both incompatible crate counts while
keeping them outside the narrow assignment test. All four J-duplicate reports
accept the real optional cleanup and preserve its facts/endpoint. These are
bounded diagnostic results, not general reliability estimates.

## Budget and observability

| Resource | Observed | Frozen ceiling |
| --- | ---: | ---: |
| Model attempts, including invalid delivery | 32 | 32 |
| Input tokens | 179,932 | 768,000 aggregate / 24,000 per call |
| Output tokens | 31,662 | 256,000 aggregate / 8,000 per call |
| Active generation seconds | 131.545 | 9,600 aggregate / 300 per call |
| Largest input / output | 6,268 / 1,325 | 24,000 / 8,000 |
| Longest active call | 5.541 seconds | 300 seconds |

Usage is complete. At the archived reference rates of $0.30/M input and $1.20/M
output, the arithmetic estimate is **$0.091974**, below the frozen $0.53760 token
reservation and $0.75 planning allowance. This is not actual billing or a
provider-enforced spend cap. Verification/metadata time is separate from active
generation time. Analysis and verification made **zero inference calls**.

## Recommended next local work

Keep D2 and PC as diagnostic evidence; do not promote the card. The observed
recovery is one paired example, not a stable causal effect or a production gain.
The comparison is small, uses one fixed seed, and does not measure writer
behavior or story quality.

Before any new live proposal:

1. Bind the U02/U03 reference-type error as a local regression alongside valid
   O/R controls. Audit whether a future diagnostic schema can enumerate valid
   catalog refs without changing the semantic task. Preserve strict rejection;
   do not repair this capture.
2. Add source-bound contrasts for the new false contradiction: pre-consultation
   action agrees with “not consulted yet” but violates “must consult first.”
   Include before-explaining versus before-deciding and original-versus-revision
   action ownership. Preserve reasonable intention/action literary criticism.
3. Audit group-relation wording locally against these exact failures. Separate
   carrying out a requested change, violating a protected condition, and being
   related to its subject. Keep current gold labels and primary results frozen.
   Any future alternative taxonomy needs its own explicit design and controls.

If those checks justify more inference, propose a small isolated comparison of
one mechanism at a time, with unchanged controls, fresh scene families and both
orders. Do not simply extend this run or bundle another general reminder with a
schema/taxonomy change. No new live budget is proposed or approved here.

For future story-quality work, retain the human review's **nine overall ties**.
Machines should prepare mechanics and requirement evidence; humans should judge
feel/emotion, flow, characterization and story-breaking concerns on sufficiently
different stories. Exact wording preservation and this strict report-usability
screen are not proxies for reader experience. No new human checkpoint is added.

## Verification and evidence

The frozen preparation had **177 passing offline tests**. **Fourteen post-run
offline tests pass**, covering exact request/ledger replay,
masked-note/source binding, tamper rejection, complete version observations,
rejected evidence-type contamination, independent loss accounting and separation
of group-label failures from correct event verdicts. Real HTTP is blocked during
these tests. Ruff lint/format and strict mypy pass on the three post-run scripts.
The initial static checks exposed a test import/export typing issue; direct
import fixed it without touching the frozen runner or production code. Initial
and final verification records are both retained. No frontend/API/worker code
changed, so unrelated application builds and broad product suites were not rerun.

Local private evidence (ignored by Git; full unpublished prose is not uploaded):

- [Amended preparation](../../data/diagnostics/reviewer-premise-amendment-v61-2026-10-24/)
  — frozen plan, requests, metadata and current plan-bound approval.
- [Live run](../../data/diagnostics/reviewer-premise-amendment-v61-2026-10-24-live/)
  — 32 reservations/captures/receipts, sentinel, 65 version observations and seals.
- [Analysis](../../data/diagnostics/reviewer-premise-amendment-v61-2026-10-24-analysis/)
  — masked reviews, sealed notes/key, decision/results, raw rejection audit,
  unsupported-claim index, tests, verification and closure manifests.
- [Exact results](../../data/diagnostics/reviewer-premise-amendment-v61-2026-10-24-analysis/results.json)
  and [frozen decision](../../data/diagnostics/reviewer-premise-amendment-v61-2026-10-24-analysis/decision.json).

The execution manifest binds **486 live JSON files** and approval. The analysis
seal binds the report and local inspection/verification artifacts; a separate
documentation closure binds the tracker and issue index without a hash cycle.
All fourteen issue bodies and user-posted GitHub links remain unchanged. No
external issue was edited or closed. **Step 19 remains IN PROGRESS; Step 20 NOT
STARTED; further live calls PAUSED; full workflow canary ON HOLD.**
