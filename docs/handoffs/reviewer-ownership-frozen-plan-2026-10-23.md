# Frozen C2/M1 requirement-ownership comparison

Date: **2026-10-23**. Status: **PREPARED AND VERIFIED LOCALLY; AWAITING LIVE APPROVAL**.

This freezes the [48-call proposal](reviewer-requirement-ownership-proposal-2026-10-23.md)
after the [scope regressions](reviewer-scope-regressions-2026-10-23.md). **Zero live
inference and zero daemon discovery calls** occurred during preparation.
Production remains **prompt 61 / graph 9 / fulfillment policy 1**; the full
workflow canary remains **ON HOLD**. This preparation supplies no new model or
human preference evidence.

## Question and intervention

Does a case-specific, application-authored requirement ownership card help a
reviewer attach correctly found evidence to the right requirement, without
hiding genuine craft defects?

- **C2 control:** the archived C2 system text, message construction, output
  schema and field order, eight-reference evidence policy, group alignment,
  vocabulary and validator are unchanged. Fresh source material is the only
  case-dependent content change.
- **M1 candidate:** the exact C2 request plus one user message immediately before
  the final response contract. Its ownership card maps supplied discoveries and
  decisions to fact checks, the supplied final state to the endpoint check,
  exact mandatory tests to their task checks and aggregate, and optional work
  and other craft concerns to their existing destinations.

Cards contain only assignment-derived requirements and reporting instructions.
They contain no expected verdicts, selected evidence, revision critique or claim
that an edit succeeded. Card generation cannot read either prose version or
withheld labels. Cards are identical across the four variants of each A/B
family; C/D cards change only with their explicit scope contract. Card content
hashes and version IDs are included in the frozen input-artifact bindings.

M1 does not incorporate T1 temporal instructions, R1 category renaming or D1
schema ordering. Both arms use the same C2 schema and strict validator. The
intervention changes input length and salience, so any benefit belongs to the
card as a package, not to a proven individual phrase or mechanism.

## Frozen cases and schedule

All four families are newly authored diagnostic fiction, with reliable narration
and **268–296 words per version**. They are not renamed historical samples.
Full prose, context, cases, source catalogs, exact diffs, group boundaries,
withheld labels and reading copies remain in the ignored private bundle.

| Family | Scene | Cases | Controlled distinction | Calls |
| --- | --- | --- | --- | ---: |
| A | Community radio closing; Lea and an old recording | A11, A10, A01, A00 | Earlier recognition retained/lost × unbroadcast endpoint satisfied/violated; physical departure is permitted and independently requested | 16 |
| B | Theatre costume workroom; Tomas and an old coat | B11, B10, B01, B00 | Earlier discovery retained/lost × unaltered-costume endpoint satisfied/violated; the same optional duplicate cleanup succeeds in all four | 16 |
| C | Conservatory after a bereavement; Nadia and a lemon tree | CN, CB | Identical prose pair with incompatible same-time glass-panel assertions; narrow assignment versus explicit consistency requirement | 8 |
| D | Sound archive; Ivo and a donated recording | DN, DB | Identical prose pair with incompatible same-interval loudspeaker assertions; narrow assignment versus explicit consistency requirement | 8 |
| **Total** | **Four families, twelve cases** | | **C2/M1 × OR/RO** | **48** |

For A/B, the first digit denotes event retention and the second denotes endpoint
compliance. N/B denote narrow/broader mandatory scope in C/D. These identifiers
and withheld labels are operator metadata; trial IDs and expected labels are not
sent in model messages. A/B original prose and context stay constant within each
family. C/D original and revision prose, source versions and mechanical edits are
identical within each scope pair; the explicit task contract changes. Optional
cleanup groups remain separate from substantive edits under unchanged C2 grouping.

The fixed case-block order is:

`A01, CN, B11, DB, A11, B00, CB, A10, DN, B01, A00, B10`.

Each block has four calls, covering both arms and both display orders. The first
display order alternates by block; the first arm alternates within matched
blocks. **A01 and CN form the initial eight-call delivery sentinel.** No adaptive
selection, replacement case, extra seed or follow-up judge is permitted.

The machine-prepared local audit binds exact source quotations, version IDs,
offsets and changed paragraph groups. The case design was inspected for the
intended semantic contrast; mechanical checks establish exact identity and
coverage, not literary quality or a general prose-understanding capability.

## Budget, route and settings

| Item | Frozen value |
| --- | --- |
| Model | `deepseek-v4.1-flash:cloud` |
| Destination, only after approval | Ollama Cloud through local daemon at `http://127.0.0.1:11434` |
| Expected daemon version | Archived **0.40.8**; not rediscovered during preparation |
| Model identity | Archived tag digest and capabilities; must match at preflight and before each call |
| Calls | **48 maximum; 24 per arm; one attempt per cell** |
| Temperature / top-p / seed | **0.2 / 0.95 / 20261022** |
| Thinking / streaming | **false / false** |
| Context / input reservation / output ceiling | **32,000 / 24,000 / 8,000 tokens per call** |
| Aggregate token reservation | **1,152,000 input + 384,000 output** |
| Active inference limit | **300 seconds per attempt; 14,400 seconds aggregate** |
| Reference-rate reservation | **$0.01680 per call; $0.80640 total** |
| Planning allowance | **$1.00**, not an enforceable billing cap |

Model digest:
`e04da138d31e0c9468e982e1ae9503d06cb7e170caa16a90c17d931c4aa140f8`.

The cost reservation uses the archived 2026-10-22 reference rates of $0.30 input
and $1.20 output per million tokens, without cache/off-peak discounts. It is not a
new price check or actual bill. Unknown billing remains unknown; missing required
token usage stops the run. Request-size estimates range from **5,027 to 6,511
tokens** using UTF-8 bytes divided by four, not a provider tokenizer. Exact reported
usage is checked against the reservation after each response.

This is a separate 48-attempt budget, starting at zero. The earlier run remains
41 combined attempts with D stopped; its seven unused slots cannot transfer.
Every attempted dispatch counts, including invalid output, HTTP errors,
cancellation and unknown outcomes. Reservations are durable before dispatch and
remain charged when a terminal attempt has no accepted usage. There are **no
retries, structural repairs, replacement calls or hidden follow-up calls**.

## Frozen scoring and inspection

Delivery, evidence finding, requirement attribution, mandatory aggregation and
complete-report usability are separate outcomes. Invalid output remains a failed
scheduled cell and receives no semantic rescue.

1. **Delivery:** strict JSON with no duplicate keys, exact C2 schema/IDs,
   source-bound evidence, permitted cardinality and normal complete stop. Neither
   syntax repair nor normalization into a different interface is allowed.
2. **Target correctness:** original withheld fact, task, endpoint and mandatory
   labels must be correct, with supported explanations. Record whether a source
   fact was missed, found but assigned to the wrong requirement, or correctly
   assigned but aggregated incorrectly.
3. **Real craft defects:** both C/D contracts require the reviewer to identify
   the same-referent, same-time contradiction with evidence for both assertions.
   A worse preference label alone does not demonstrate detection. Narrow scope
   does not make the prose defect disappear; broad scope makes consistency an
   explicit mandatory test.
4. **Complete report:** retain the unchanged C2 group-label checks and inspect
   consequential comparative premises. Correct target labels do not excuse
   unsupported group reasoning, false contradictions or invented motivations.

The deterministic mandatory-task projection runs on both arms after capture. It
only checks consistency with their own mandatory task verdicts. It preserves
uncertainty and cannot validate false premises. It never overwrites the model
answer or creates an accepted recovery.

Export shuffles reports and hides arm/order/model identifiers. Operator notes
must bind the exact assessment and source packet, identify exact report fields
and claim text, and attach source/version/offset evidence and uncertainty.
Unsupported target claims are classified as `event_endpoint` or
`mandatory_scope`. Contradiction detection requires both source assertions.
Seal notes before decoding the key. Wording may reveal a condition: this remains
masked operator factual inspection, not independent blind human preference.

**M1 passes this diagnostic screen only if all conditions hold:**

- All **48** scheduled responses complete; M1 delivers at least **22/24** valid
  reports. A terminal or sentinel-stopped run is incomplete.
- No paired usable C2 report becomes unusable under M1. No correct C2 target
  judgment or detected real contradiction is lost under M1.
- There are complete, grounded recoveries in **both orders** of a case in at
  least two distinct families: at least one A/B event/endpoint recovery and at
  least one C/D mandatory-scope recovery.
- For each counted recovery, both C2 orders must have a **valid report with the
  relevant target failure**, and both M1 orders must be usable and correct.
  Delivery-only improvements, a different failure class, one-order gains and
  aggregate-only counterfactual repairs cannot satisfy that recovery requirement.

This makes the proposal's target-specific recovery rule explicit before any live
output. If controls already succeed or gains do not span the required contrasts,
report no demonstrated advancement; do not expand the budget. Even a passing
screen yields only `retain_promising_diagnostic_only`, never production adoption.

There is no gold literary winner for changed prose and no reward for fewer edits.
Human review stays focused on feel/emotion, flow, character and story-breaking
details. The nine earlier human ties remain unchanged. Four family clusters,
one seed and repeated within-family variants limit generalization; 48 calls are
not 48 independent stories or a demonstration of improved fiction.

## Stops and execution safeguards

- Before any live discovery or inference, require a new approval record binding
  this plan hash, full prose/context payload, model, destination, 48-call ceiling,
  24-per-arm limits, zero retries and no canary authorization. Earlier approvals
  are rejected. No approval record or live execution directory exists now.
- Check frozen sources, requests, runtime code and production fingerprints.
  Require the archived model digest/capabilities and daemon version. Check daemon
  version before and after every call. A changed baseline or runtime stops
  execution and requires a documented decision; no silent rebaseline occurs.
- Any non-200 response, transport error, timeout, cancellation, length finish,
  incomplete/unexpected finish, unexpected thinking, model mismatch, missing or
  excessive required token usage or elapsed-time overrun stops **all** dispatch.
  Preserve raw response when available, gateway exception chain, reservation and
  unknown usage. Terminal-aware audit/export does not reopen the run.
- At eight responses, stop if either arm has zero valid reports, or one structural
  signature appears in at least three of its four reports across both sentinel
  families. Below that threshold, invalid normal-stop reports stay failed while
  the remaining frozen schedule continues. No semantic-result-based adaptation.
- Reject concurrent operators, unplanned/skipped/duplicate cells, source or
  request tampering and unresolved reservations. Clean cell-boundary restarts
  replay receipts and sentinel state; terminal stops cannot resume or retry.
- Unused calls stay unused. Production prompts, writer selection and workflow
  routing remain unchanged; the full workflow canary stays **ON HOLD**.

## Verification, artifacts and next action

**119 tests pass: 97 preparation/harness checks plus 22 gateway/contract checks.**
Ruff lint/format and strict mypy pass on five new private scripts. Verification
includes every frozen wire request through the actual production Ollama adapter
using in-memory HTTP, a full 48-call mock run and restart, both sentinel outcomes,
all sixteen non-200 fixtures, normal-stop malformed output, cancellation,
truncation, usage/version/model failures, terminal audit/export, source-bound
inspection, scoring regressions and tamper rejection. Real HTTP is blocked.

Windows event-loop IPC required running mocked tests outside the restricted
process sandbox. An initial mocked run caught a missing timestamp in the fake
provider envelope and an overly strict comparison against model metadata that
also includes a check timestamp. Both were corrected locally; initial results
are retained. No real server was contacted. The final preparation also adds
target-class checks so delivery-only or wrong-class gains cannot pass the screen.

No application source changed. Relevant gateway tests were rerun because the
new harness uses that adapter; the frontend build and unrelated application
suites were not repeated.

Private preparation:
[`data/diagnostics/reviewer-ownership-v61-2026-10-23/`](../../data/diagnostics/reviewer-ownership-v61-2026-10-23/).
Key files are `plan.json`, `cases.json`, `casebook.md`, `local-case-audit.json`,
`ownership-cards.json`, `card-artifacts.json`, `prepared/`, `schedule.json`,
`scoring.json`, `budget.json`, `stop-rules.json`, `pricing.json` and
`verification.json`. The plan binds these files, scripts, archived dependencies,
production fingerprints and this public document. Its digest is in the tracker.
Detailed prose remains local and ignored by Git.

Offline verification from the repository root:

```powershell
.venv/Scripts/python.exe -X utf8 data/diagnostics/reviewer-ownership-v61-2026-10-23/ownership.py verify
.venv/Scripts/python.exe -X utf8 -m pytest data/diagnostics/reviewer-ownership-v61-2026-10-23/test_ownership.py tests/models/test_ollama_gateway.py tests/models/test_contracts.py -q
```

The next action is approval of this frozen live comparison. Until then, **live
calls remain paused**, the previous evidence stays sealed, all critic/writer
issues remain open, Step 19 remains **IN PROGRESS**, and Step 20 is **NOT STARTED**.
