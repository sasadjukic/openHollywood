# MA/quote-witness binding comparison: frozen local plan

Date: **2026-11-02**. **PREPARED AND VERIFIED LOCALLY; 0/24 inference calls used.**
Separate live approval is pending. Production prompts remain unchanged and the
full workflow canary is **ON HOLD**.

This follows the [repeated-control audit](reviewer-binding-semantics-audit-2026-11-02.md).
It tests whether asking the model to copy a source witness, then having the
application locate its registry entry, improves citation binding over asking the
model to emit registry IDs. It does not assume that exact copying establishes
truth, necessary edits or story quality.

## Arms and isolated change

Both arms use `deepseek-v4.1-flash:cloud`, **high thinking**, the same full source
versions, source registry, report, saved assertion selections and substantive
judging instructions. There is no selector or writer call. Gold labels, adequate-
evidence criteria, example answers and trial/repeat identifiers are withheld from
model messages.

| Arm | Evidence output | Application responsibility |
| --- | --- | --- |
| MA: unchanged control | One to eight distinct `S` registry references | Validate the references and preserve their exact source entries. |
| WB: quote-witness binding | One to eight distinct `{version_id, field, quote}` objects | Locate each exact quotation in its named source field, then resolve its containing registry entry. |

WB changes only the evidence-output instruction block and corresponding response
schema. Removing those two changes reconstructs the MA wire exactly. All eight
historical MA requests are byte-equivalent at the model-facing wire level to their
respective saved baseline controls. No source-excerpt duplication, additional
semantic advice, changed sampling or increased output allowance is introduced.

Each witness quote must contain **1–512 characters**, with at most **8,000 witness
characters per report**. Its version and JSON-pointer field must exist together.
The model supplies no offsets, hashes, occurrence index or registry reference in
the witness. A repeated phrase requires enough surrounding copied text to locate
one occurrence within one registry entry. No fuzzy matching or automatic repair
is allowed. Different witnesses in one paragraph remain visible; resolved registry
references are deduplicated without discarding the original witnesses.

The existing assertion identity and support/reason contract remains intact:
every frozen selection exactly once; `supported`, `unsupported` or `uncertain`;
reason 1–1,200 characters, at most 8,000 in total. Empty evidence is allowed only
for `uncertain` with an adequate scope explanation. WB also rejects raw responses
over 64,000 characters. Unknown fields, duplicate keys, duplicate selections or
witnesses, extra/missing assertions, invalid types and cardinality violations are
delivery failures.

A structurally valid witness with a missing, ambiguous or cross-entry quotation
is retained as an **unresolved binding**, not repaired or treated as invalid JSON.
That judgment cannot receive citation/grounding credit; its label and substantive
semantic correctness are still inspected independently. Such failures do not
stop inference. This distinction is frozen before observing model results.

The local renderer recomputes all locations from the original submitted response,
rejects altered projections, and displays exact source entries and hashes with
unverified model judgments. Text is rendered literally, including markup. It
grants no entailment, review acceptance or writer authority.

## Cases, order and denominators

| Case block | Allocation | Calls | Judgments across both arms |
| --- | --- | ---: | ---: |
| Historical H1/H2 | Four family/order wires × two repeats × two arms | 16 | 96 |
| Fresh W1/W2 | Two families × two source orders × two arms | 8 | 64 |
| Total | Twelve paired positions; twelve calls per arm | **24** | **160** |

Each arm has **80 judgments: 56 supported, 20 unsupported and four uncertain**.
PC/CP are the two previously used presentation orders. The two historical blocks
are H1/PC–H2/CP–H1/CP–H2/PC and H2/PC–H1/CP–H2/CP–H1/PC. The fresh block is
W1/PC–W2/CP–W1/CP–W2/PC. Paired arms are adjacent and their first position
alternates. The exact 24-row schedule is frozen locally; this is limited
counterbalancing, not an independence or population-reliability design.

H1 retains decision/handwriting, explicit future-date realization, current endpoint
and specific private-flourish claims. H2 retains reasoned decision/preparation,
touch/effect, current outside endpoint and next-scene plan claims. Every historical
label, selection and source remains unchanged. In particular, a frozen factual
failure on “consumes/preempts” does not establish that an editorial concern about
suspense is worthless. Binding success cannot resolve that interpretive limitation.

The two fresh scenes preserve those contrasts with explicit event/plan wording:

- **W1, The Unfired Plate:** Iris's conservation-annex scene actually performs a
  planned private verification through paraphrase. The next-scene plan starts
  outside and includes entering; it does not start after entry.
- **W2, The Last Cable Ledger:** Dara's funicular-station scene establishes general
  origin while explicitly leaving the private verification undone. Its next-scene
  plan explicitly starts inside after crossing.

Both fresh families also test reasoned decision without a literal declaration,
touch plus a persistent effect across paragraphs, two dates plus an explicit
realization, an independent current endpoint violation, attributed intent with
negation, and uncertainty when a required annex is unavailable. Positive and
negative controls prevent blanket rejection from looking successful. Each fresh
family supplies eight complete claims in both orders. Full fiction, blueprint,
assignment, report, scope, exact selections and held-out criteria are frozen in
the [local casebook](../../data/diagnostics/reviewer-quote-witness-v61-2026-11-02/casebook.md)
and accompanying case/request files. These are diagnostic scenes, not a new
human preference study or production story artifacts.

## Scoring and decision rule

After execution, inspect every valid judgment against the complete sources.
Seal source-bound inspection notes before decoding the trial/repeat key and
resources. Masking is partial: output shape and known cases can reveal provenance.
This is an assistant factual audit, not blind human review. Model thinking is
preserved opaquely and excluded from semantic evidence.

Score label accuracy, faithful meaning, grounded explanation, material error,
opinion factualization and adequate citations separately. Evidence adequacy uses
the **same complete containing registry field/paragraph and full context in both
arms**. A small locating quote alone does not prove a compound claim. A reference
whitelist is not the scoring rule: evidence must cover each required fact and
relation. For unsupported claims it must ground the rejection; for uncertainty it
must accurately explain the unavailable scope. Frozen per-claim criteria specify
these requirements.

A citation-only failure means the label and substantive reasoning are correct,
but the submitted evidence is inadequate. A recovery requires a fully grounded
WB judgment at that paired position. A semantic recovery cannot be counted as a
citation recovery. Distinct positions are keyed by **family, presentation order
and claim**, so recovering the same historical position twice counts once.

The diagnostic is promising only if all of these hold:

1. **24 valid reports**, with all 160 judgment slots available.
2. At least **two distinct paired citation-only recoveries** from MA to WB.
3. **Zero paired semantic or grounding losses**, including fresh controls.
4. All **32 fresh WB judgments grounded**, with no blanket rejection shortcut.
5. Retain **26 historical grounded and 40 historical semantic protection
   occurrences** in WB. These are repeated occurrences, not independent stories.
6. No loss of a grounded whole contextual relation assessed in the paired MA
   report. Inspect **eight separate contextual relation flags**; component labels
   never silently become a whole-relation judgment.

Any unavailable report yields `incomplete_delivery`. With complete delivery, a
regression or failed protection/fresh gate yields `gate_not_met`. If those gates
pass but fewer than two distinct eligible MA citation failures recur, report
`insufficient_control_reproduction`, not treatment success. Otherwise two distinct
recoveries yield `promising_binding_diagnostic`; fewer yield `gate_not_met`.
Report repeat-specific outcomes as well as totals. Do not pool historical runs or
turn this small targeted sample into a reliability estimate.

All unstarted/invalid slots remain in the fixed denominators and are reported as
unavailable, not observed semantic errors. Report per-request latency and input /
combined generated counters, including cache information when supplied. Reasoning
versus final token counts remain unknown unless explicitly reported. A complete
paired resource comparison requires all 24 valid reports. No resource-saving
gate or billed-cost claim is imposed after looking at results.

## Budget, metadata and stops

| Limit | Frozen allowance |
| --- | --- |
| Inference | **24 total, 12 per arm; one attempt per cell; zero retries** |
| Each call | 24,000 input tokens; 16,000 combined thinking + final tokens; 600 active seconds |
| Requested context | 40,000 tokens |
| Aggregate reservations | 576,000 input; 384,000 combined generated; 14,400 active seconds |
| Sampling | Temperature 0.2; top-p 0.95; seed 20261022; high thinking; non-streaming; no `format` option |
| Archived-rate reference | **$0.63360**, with $0.70 planning allowance; actual billing unknown and no enforceable billed cap |

The cost reference retains the archived October 22 rates, not a new pricing claim.
No unused historical budget is reused. Largest wire: **67,546 UTF-8 bytes**;
bytes/3 estimate **22,516**, below the input allowance. This is not a tokenizer
measurement; actual counters govern enforcement.

Three metadata-only responses on November 2 confirm **Ollama 0.40.13**, high-
thinking support and unchanged model digest
`e04da138d31e0c9468e982e1ae9503d06cb7e170caa16a90c17d931c4aa140f8`.
The initial sandbox-blocked metadata attempt and successful second capture are
both retained. No inference occurred. Recheck daemon/version/model capabilities
before dispatch; capture version evidence around each call. Drift stops the run
rather than silently amending the baseline. Requested sampling is recorded;
provider-internal effective sampling is not asserted.

**Stop both arms on the first invalid, empty or length-limited final**, non-200 or
transport failure, timeout, unknown/conflicting usage, missing thinking, invalid
timing, resource excess, metadata drift, source/request/ledger integrity failure,
ambiguous dispatch or cancellation. Preserve raw errors and their chain; unknown
usage stays unknown. A partial or complete-looking length final earns no semantic
credit. Never retry, replace, reallocate, release spent reservations or increase
limits to rescue delivery. Continue across valid semantic and unresolved-witness
failures only. A clean pause can resume at a sealed valid cell boundary; a terminal
or delivery stop cannot resume under this approval.

## Verification, artifacts and approval boundary

The local bundle is
`data/diagnostics/reviewer-quote-witness-v61-2026-11-02/`. It contains the exact
cases, admitted selections, held-out judgments, evidence criteria, 24 prepared
requests and wires, schemas, schedule, historical protections, scoring/stops,
metadata, source pins, literal renderer samples, runner and inspection harness.
`plan.json` seals these files and this public plan. The tracker records its final
hash; subsequent publication checks seal the tracker/index without changing the
frozen requests.

Verification covers schema and quote-location failures, source/hash and literal-
rendering fidelity, 24 exact request reconstructions, gold exclusion, fixed
denominators and distinct-recovery rules, paired losses, whole-relation separation,
terminal usage/error preservation, tampering, approval binding, clean pause/resume
and first-failure stop. **263 offline tests pass**: 99 comparison tests, 22 gateway /
contract tests, 58 prior binding-audit tests and 84 usage tests. Ruff lint/format
and strict mypy pass on twelve scripts. Historical score replay remains unchanged.
Real HTTP/model and database access are blocked during the diagnostic tests.
Preparation failures and their corrected verification are preserved locally.

**Separate approval is required before inference**, for the frozen plan and
full unpublished fictional prose/context, reports and admitted assertions sent to
**Ollama Cloud through the local Ollama daemon**, within 24 calls and these stops.
At preparation there is no live approval file or live-run directory.

Production **prompt 61 / graph 9 / fulfillment policy 1**, canonical story prose,
writer routes, source exporters and the mandatory Blueprint checkpoint remain
unchanged. Step 19 stays **IN PROGRESS**, Step 20 **NOT STARTED**, all issues remain
open and the canary stays **ON HOLD**. A favorable result would justify further
evidence-handling work only. Literary feel, flow, character, story-breaking detail,
edit necessity and preservation remain separate questions.
