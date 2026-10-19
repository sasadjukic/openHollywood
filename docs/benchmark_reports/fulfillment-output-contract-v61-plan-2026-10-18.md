# Frozen output-contract comparisons, 2026-10-18

**PREPARED, VERIFIED AND FROZEN — no live authorization or calls.** This implements the
[74-call proposal](../handoffs/fulfillment-output-contract-diagnosis-next-experiment-2026-10-18.md).
Production prompt 61 / graph 9 / fulfillment policy 1 stay unchanged.
**Step 19 IN PROGRESS; Step 20 NOT STARTED; full workflow canary ON HOLD.**

Plan SHA-256:
`c8fb871abe6a9e9f4d432dd7a7a47a696dce0547cf671ccd372318a369c426c9`.
All **74 exact requests**, cases, scoring, stop rules, evidence-handle mappings,
schedule, resource limits and helper/source dependencies are frozen locally.

The experiment tests delivery of the existing critic judgments and response
contracts. It cannot establish broader story quality or authorize production
adoption. All cases come from the sealed previous experiment; no new story,
writer output, fallback model or response-dependent case selection is involved.

## Fixed comparisons

| Block | Cases and arms | Seeds | Calls |
| --- | --- | --- | ---: |
| A: restricted critic repairs | F1/F2 on a01, a03, a05, a06; F3 on a01/a03 | 19801, 19803 | 20 |
| B: original/revision assessment | V0/V2/V3 on b01–b09 | 19801, 19803 | 54 |
| **Total, including controls** | **One attempt per slot; zero retries** | | **74** |

A uses the exact previous parent report hashes, full source prose/context,
diagnosed patch locations and resulting-report validator:

- **a01:** `s19603-elara-duplicate-overrun-initial-shared`; comparison meaning failure.
- **a03:** `s19501-elara-duplicate-overrun-initial-P1`; successful comparison control
  with the previously masked application-owned condition error.
- **a05:** `s19601-elena-missing-decision-initial-shared`; valid native missing-decision condition.
- **a06:** `s19601-elena-compound-outcome-initial-shared`; valid compound native condition
  and previous hybrid no-op output. Its inherited warning-acceptance explanation
  caveat stays visible; preserving it is not a new error or certification of its truth.

**F1** retains the previous restricted-edit baseline request text. **F2** moves
the unchanged ordinary rules and schema into explicitly scoped resulting-report
references, then gives one final patch response contract, an answer-free shape
illustration and an explicit empty-edit envelope. **F3** adds only a focus record
derived from the diagnosed issue pointer: its exact description/evidence refs,
reported comparison targets and the minimal-repair comparison question. It supplies
no expected answer, selected reference, classification or new story allegation.

F3 delegates a05/a06 to F2. Four seed-specific observations are shared explicitly;
they buy no calls and are not independent F3 successes. F2 is the primary protocol
candidate. F3 tests the incremental value of issue-local focus. F2 is a delivery
package, so its result cannot isolate the effect of an individual instruction.

B retains all nine full original/revision packets, artifact versions, source
context, tasks, fact checks, diff and change units. Purposes are hidden in every arm:

| Case | Fixed role |
| --- | --- |
| b01 | Actual separate-boundary repair with an extra preparatory-action deletion |
| b02 | Actual separate-boundary repair with mixed ending changes and lost strap-condition detail |
| b03 | Actual embedded-boundary repair with extra ending imagery |
| b04 | Actual successful optional duplicate-removal craft edit |
| b05 / b06 | Operator-authored minimal separate / embedded boundary repairs |
| b07 | Optional-craft no-op: duplicate remains; not a mandatory failure |
| b08 | Mandatory-boundary no-op: entry remains |
| b09 | Labelled synthetic repair of repetition inside a positively cited sentence; fact retained |

**V0** retains the previous purpose-hidden baseline. **V2** separates source
material from one final response contract, retaining the schema and judgments.
It explicitly restates existing requirements for full catalog quotations,
evidence for neutral craft effects and nonblank explanations when mandatory
failure is false. Shape illustrations supply no editorial answers.

**V3**, the predeclared candidate, uses V2's delivery and judgments but asks for
model-selected evidence handles instead of generated citation versions/quotes.
The application supplies the bound original/revision version envelope and expands
each selected handle into the exact catalog version/ref/full quotation. It chooses
no evidence, fills no omission, changes no opinion and edits no prose.

Each handle contains its side-specific catalog ref and a 16-hex fingerprint bound
to the exact trial, side, version and complete catalog record. Both sides' original
catalogs remain in the input, with handles added. This avoids silently accepting a
reused short ref from another case or seed. Unknown, stale or altered handles fail.
The expanded canonical assessment passes the unchanged version, identity and
evidence validator. Wrong/missing/duplicate task, fact and change records fail.
Correct citation identity does not prove that a textual claim is supported; that
remains a separately scored inspection requirement.

## Frozen order and resource limits

Within A, the first seed's case order is **a06, a01, a05, a03**. Within B it is
**b08, b09, b07, b05, b02, b06, b01, b04, b03**. The second seed reverses each
block's case order and each individual case's arm order. First-seed arm rotations
follow the case index; B gives each arm equal first/middle/last positions.
A's semantic results never select, skip or gate B cases. A terminal safety or
integrity failure still stops the whole run.

The model remains `gemma4:31b-cloud`, pinned digest
`c382fbfbc73b6fdd08c8549c23caedc6e62eb09933c65a1fb82dbf3398320a4e`,
through **Ollama Cloud via the local Ollama daemon**. Settings: temperature **0.2**,
top-p **0.95**, thinking **false**. Prompt-text schemas remain in use;
`response_schema=null`. No provider capability change or discovery is inferred.

| Reservation | Per call | Total ceiling |
| --- | ---: | ---: |
| Input tokens | 24,000 | 1,776,000 |
| Output tokens | 8,000 | 592,000 |
| Active seconds | 900 | 66,600 |
| Calls | 1 per slot | 74; A 20 / B 54, nontransferable |

The historical October 8 estimate at USD 0.14/M input and USD 0.40/M output is
**USD 0.48544** at the full reservation. This is not a current quote or confirmed
billed charge. Input-size estimates are checked without trimming; actual provider
usage must remain inside each reservation. No call may consume an unused slot
from the other block. Old approvals and the previous run's unused 55 calls do not
authorize this experiment.

## Scoring and stop rules

- **F2:** require all four qualified comparison corrections and four exact valid
  native-control identities, supported retained judgments and zero collateral
  changes. Report paired improvements and losses against F1. Both reaching the
  ceiling means no demonstrated relative advantage.
- **F3:** require all four comparisons supported, at least two extra qualified
  recoveries over F2 and no losses. If F2 reaches the ceiling, record no demonstrated
  need for F3. A boundary ref without a supported account of the remaining craft
  defect does not qualify.
- **V3:** require all 18 outputs valid, all task/factual judgments correct, both
  no-op defects noticed at both seeds, no invented hard failure on minimal/craft
  controls and all six actual boundary-revision cells to distinguish extra edits
  from repair necessity. Require supported gains/losses or uncertainty in b02 and
  acceptance of the successful within-cited-sentence craft repair in b09.
- Report the 18 paired V2–V0 delivery comparisons and 18 paired V3–V2 metadata
  comparisons separately. Inspect every result, including invalid raw outputs,
  for input copying, output size and errors. Invalid outputs cannot qualify.
  Structural validity and substantive support have separate scores.
- Keep the prior sensitivity analysis treating debatable new imagery/physiology
  as neutral separate from the primary labels. Neither unchanged prose nor the
  smallest diff is a literary oracle. Independent human preference remains pending.

Each slot has **one attempt**. An ordinary structurally invalid `stop` response
fails its cell and the fixed schedule continues. A **fully persisted `length`
response**, with matching provider/model/deployment and known usage inside the
reservation, also fails its cell; its content is **not parsed or retried**. The
next already-frozen cell may then run. This new diagnostic rule does not reopen
the prior terminal run.

**Stop the entire run** on unknown outcome, missing capture or usage, cancellation,
identity/digest drift, transport failure, integrity failure, exceeded budget,
incomplete probe or a finish reason other than `stop`/`length`. Persist requests
and reservations before dispatch; preserve raw captures and usage. Replay
completed cells without new calls; never automatically repeat an incomplete cell.
Show any unobserved cells separately from failed cells if the run stops early.

## Local evidence and approval boundary

Private preparation directory:
`data/diagnostics/fulfillment-output-contract-v61-2026-10-18/`.
It contains the builders, adapter, bounded operator, fixtures, scoring/export,
source packets, exact static requests, schedule, shared controls, stop rules,
verification and preparation closure. The anonymous full-prose review export has
nine original/revision pairs; its reviewer sheet is pending, not model-generated
human evidence. It introduces no production human checkpoint.

Local verification passed:

- **74 valid fixtures, 916 rejection checks, 56 paired request-delta checks and
  18 canonical V3 equivalence checks.** Full source packets are retained; F1/V0
  baseline message text is unchanged. Stale/wrong-side handles, missing/duplicate
  records, partial quotations, blank explanations, unsupported output fields and
  out-of-scope patches are rejected.
- **306 fake dispatches** exercise four complete 74-cell matrices: valid responses,
  invalid responses, known length responses and restart from three completed cells.
  Restart makes exactly 71 new calls; complete replay makes none. Ten terminal
  fault modes, seven approval negatives, four tamper bindings, six budget guards,
  missing captures/unknown outcomes and lock ownership/cancellation pass.
- Final code replays **296 completed attempts**, including all 74 length responses
  with the parser disabled. The fake provider checks durable requests/reservations
  exist before dispatch. These are application checks, not successful model results.
- All 74 request estimates are **13,970–19,592 tokens** using UTF-8 bytes divided
  by four, below the 24,000 allowance. This estimate is not an exact provider count;
  observed usage remains subject to the frozen stop rule. No source text is trimmed.
- **75 focused regressions**, repository Ruff lint/format, strict mypy across
  **201 files**, and lint/format for **eight private helpers** pass. Client/build
  checks are not applicable because client and production code are unchanged.

Preparation corrected a fixture that needed to patch both imported source aliases,
and a replay comparison that needed canonical JSON equivalence after tuples were
serialized as arrays. The successful verification uses the corrected code.
Sandboxed async checks stalled in Windows local socket-pair initialization before
reaching the harness; those processes were stopped. Fake-provider checks and
regressions then passed outside that restriction. The harness blocked external
connections and real gateway construction. **Live inference, real provider
discovery and external-network calls: zero.** Earlier local attempts are retained
separately and are not counted as successful verification.

The sealed predecessor live closure remains
`0b18760f12ac580d7a75ecb26a133d78573c3d717d3a7b2055a277e486de7df4`;
the diagnosis closure remains
`d93b161b0cf8b37d85292da123fb03486564aaa02f0fda13f907b5041c28c8b1`.

Future live execution requires explicit approval bound to this new plan hash,
**74-call ceiling**, **full unpublished fictional prose/critic/context payload**,
and the named Cloud destination, with **canary authorization false**. Approval is
checked before constructing a real gateway or discovering models. There is no
approval record or live output directory in local preparation.

If V3 improves structure but fails substantive controls, do not introduce a
self-approval loop. Consider a separately bounded model crossover or a
human-calibrated judgment experiment. Retain the earlier narrow diagnostic gains
and unqualified preservation candidates without promotion. Broader quality work
still requires the [accepted weighted human rubric, hard gates, full Cloud corpus
and comparable baseline](../../open_hollywood_bible/product_contract_and_benchmarks.md).
