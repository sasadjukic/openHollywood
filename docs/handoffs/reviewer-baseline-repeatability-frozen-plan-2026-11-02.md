# Frozen baseline-only MA repeatability diagnostic — 2026-11-02

**Prepared locally; awaiting separate live approval. 0/12 inference calls used.**
Production remains **prompt61 / graph9 / fulfillment policy1**. Live inference
is **PAUSED** and the full workflow canary remains **ON HOLD**.

This implements the [local repeatability audit's proposal](reviewer-delivery-repeatability-audit-2026-11-01.md).
Four byte-identical historical MA requests previously moved from 13/24 to 24/24
grounded judgments. The question is whether the saved citation and semantic
failures recur across deliberate repetitions of those same requests at the same
limits. This is a baseline diagnostic, not another PE treatment comparison or a
production qualification test.

## Frozen requests and allocation

**Four unique MA wires × three repetitions = twelve calls maximum.** Each wire
retains its complete prose, blueprint/context, current assignment, saved report,
actual saved SO selections, original instructions and response contract. Historical
PC and CP selections differ and remain unchanged. PC presents prose before
context; CP presents context before prose. No selector or writer is rerun.

Every model-facing payload exactly matches its archived MA/PE MA control and the
corresponding original VA/MA MA wire. Local repeat IDs, block numbers, provenance
and budget accounting are not added to model messages. No paragraph excerpts,
gold judgments, relevance hints or expected citations are added. Prompts, source
versions, sampling requests and per-call limits remain unchanged.

| Wire | Source family and diagnostic coverage | Judgments per call | Calls |
| --- | --- | ---: | ---: |
| H1/PC | Elena: dates, decision/match evidence, valid no-match boundary violation, unsupported specific-flourish inference | 7 | 3 |
| H2/CP | Elara: contact/pull, preparation/entry, outside obligation, unsupported starting-after-entry inference | 5 | 3 |
| H1/CP | Same H1 source family, original CP selections and endpoint-relation flag | 7 | 3 |
| H2/PC | Same H2 source family, original PC selections | 5 | 3 |

The fixed interleaving is:

| Block | Calls, in order |
| --- | --- |
| R1 | H1/PC → H2/CP → H1/CP → H2/PC |
| R2 | H2/PC → H1/CP → H2/CP → H1/PC |
| R3 | H1/CP → H2/PC → H1/PC → H2/CP |

This varies positions across blocks; it is not complete positional counterbalancing
with only three repeats. No output-dependent scheduling, seed change, cache
clearing, treatment arm, additional family or replacement is allowed. Repeated
orders/claims are not independent stories: there are **two family clusters**.
Fresh C5/D6 positives remain local regressions outside this live matrix.

The [private casebook](../../data/diagnostics/reviewer-baseline-repeatability-v61-2026-11-02/casebook.md),
`cases.json`, `assessment-units.json`, `wire-requests.json` and twelve `prepared/`
records bind every exact request and selected proposition. Per-claim judgments
and adequate-evidence criteria remain source-bound and are never sent to the model.

## Frozen scoring and inspection

There are **72 fixed judgment slots**: 24 per block, with **54 supported and
18 unsupported** labels overall. These unchanged historical selections have no
uncertain-label case; uncertainty controls remain in the preserved local suite.
Coverage comprises:

- **21 occurrences of seven historical citation targets:** H1/CP Q002, Q003,
  Q005 and Q006; H2/CP Q004; H2/PC Q001 and Q002, each repeated three times.
- **Twelve occurrences of four historical semantic targets:** H1/PC Q006,
  H1/CP Q007, H2/PC Q005 and H2/CP Q005, each repeated three times.
- **39 occurrences of thirteen previously grounded successes**, plus separate
  protection of **60 occurrences of twenty previously semantically correct
  judgments**. Every other observed failure is also reported, including new
  errors on the most recently successful MA claims.
- **Six contextual flags:** the complete current endpoint relation in each
  H1/CP and H2/CP report. Correct component labels do not establish that relation.

Every valid returned judgment receives separate source-bound assessment of label
accuracy, faithful selected meaning, substantive explanation grounding, adequate
citations, material error and opinion factualization. Adequacy means content
coverage, not an exact reference whitelist. A compound observation needs evidence
for every relevant component; a claimed violation needs the observed event and its
governing obligation. General matching does not establish the specified private
verification test; an interior location does not prove a scene begins after entry.
Extra irrelevant references alone do not fail an otherwise adequately cited claim.

The application verifies structure, exact selections, references and source/result
bindings. It does not automatically judge entailment or repair an answer. The
unchanged boundary rejects duplicate keys, duplicate/missing/extra selections,
unknown or duplicate references, forbidden fields and altered quotations. Each
reason is 1–1,200 characters; combined reasons are capped at 8,000, and selected
quotes at 2,400 characters.

Inspection exports withhold the trial/block key and resources until notes are
sealed. This is **partial assistant masking, not blind human literary review**:
the familiar cases and selections can reveal provenance. Thinking content is
excluded from semantic evidence. Notes bind exact source versions, returned
reasons, selections, unit IDs and result hashes.

Scoring distinguishes:

1. **Citation-only recurrence:** a historical citation target remains semantically
   correct but lacks adequate citations. A semantic error on that target is
   reported separately, not counted as a citation-only recurrence.
2. **Semantic-label recurrence:** an incorrect frozen support label on one of the
   four exact historical semantic targets. Reason-only errors with a correct
   label remain visible as semantic errors, without automatically claiming the
   same historical failure pattern.
3. **Other errors and unavailable results:** all observed errors are retained.
   Invalid, length-stopped and unstarted reports remain in the fixed denominators
   but are not described as observed semantic mistakes. Partial finals receive
   no salvaged judgment credit.

Report results per wire and per repeat: valid delivery, grounded judgments,
recurrence counts, distinct labels/reasons/citation lists and citation sets,
tokens, cache counters and active latency. Preserve historical observations
separately from the new-run counts; do not pool them into a reliability estimate.
Protection failures are split into observed failures and unavailable slots.

The overall status is **incomplete delivery** unless all twelve reports are valid.
With twelve valid reports, report **known failure recurrence observed** if either
defined target recurrence occurs; otherwise report **bounded nonreproduction**.
Any recurrence observed before a delivery stop remains recorded. Other errors
and whole-relation coverage are reported regardless of that status. No outcome
grants production readiness, stable reliability, writer dispatch or story-quality
qualification. If target failures do not reproduce, defer another citation
intervention rather than attributing a benefit to an untested treatment.

## Model, metadata and budget

Metadata-only capture on **2026-11-02** confirms **Ollama 0.40.13** and unchanged
`deepseek-v4.1-flash:cloud` information. The selected digest remains:

`e04da138d31e0c9468e982e1ae9503d06cb7e170caa16a90c17d931c4aa140f8`.

Only `/api/version`, `/api/tags` and `/api/show` were requested from the local
daemon; **zero inference**. Raw response bytes, hashes, request metadata and seals
are preserved. Model information and daemon baseline match the prior capture,
so no baseline amendment is needed. Preflight and per-call checks enforce the
freeze; metadata drift stops the run rather than silently adopting an update.

| Setting | Frozen value |
| --- | --- |
| Destination, if separately approved | Ollama Cloud through `http://127.0.0.1:11434` |
| Thinking | `"high"`; require a nonempty returned thinking field |
| Temperature / top-p / seed | 0.2 / 0.95 / 20261022 on every call |
| Requested context / generated cap | 40,000 / 16,000 tokens |
| Streaming / provider format schema | Off / none |
| Input reservation per call | 24,000 tokens |
| Active inference time per call | 600 seconds |
| Attempts | **12 total; three per wire; zero retries** |
| Aggregate reservations | **288,000 input / 192,000 generated / 7,200 active seconds** |
| Archived-rate reference / planning allowance | **$0.31680 / $0.35** |

The archived reference uses the previous $0.30 input / $1.20 output per million
rates without cache discounts. It is not a current-price claim or an actual bill;
billing is unknown and no enforceable billed-dollar cap is asserted. All generated
tokens, including thinking and final output, share the 16,000 limit. Their split
remains unknown unless explicitly reported; do not estimate it from characters.
Metadata checks and inspection time are outside the active inference seconds.

The largest wire is **60,612 UTF-8 bytes**. A conservative bytes/3 estimate is
**20,204 input tokens**, below the reservation; this is not model tokenization.
Actual usage must obey the frozen limits. Captured settings describe what was
requested; they do not attest effective sampling or seed determinism. Cache
counters are observations, not randomized experimental conditions.

This is a separate twelve-call budget. The six retired PE slots and every earlier
experiment's stopped allowance stay closed and are not reused.

## Stops and authorization

Continue through semantic or citation errors to measure recurrence. **Stop the
entire diagnostic at the first delivery failure**, including an invalid structured
final, empty final or verified length termination. Also stop on non-200/transport
failure, unknown or conflicting usage, exceeded resources, missing required
thinking, invalid timing, metadata drift, integrity mismatch, ambiguous dispatch,
unexpected gateway failure or cancellation. No retry, repair, replacement, budget
transfer or larger generation cap follows a stop.

Reserve each attempt before dispatch. Preserve raw responses, gateway error chains,
version observations and known/unknown usage, including failed calls. Known counters
on a length-stopped response do not create a valid report. A terminal run cannot
resume. Only a clean boundary after a complete, sealed, valid cell may resume the
original remaining schedule without repeating a request. The runner verifies the
ledger, frozen wires, source pins and approval before further dispatch.

Live operation requires a new approval file bound to the final plan hash,
**full unpublished prose/context/report/selections**, the stated destination,
high thinking, twelve calls, first-failure stop and zero retries. No such approval
file or live-run directory is created during preparation. Earlier approvals do
not authorize this diagnostic.

## Local verification and freeze

The isolated bundle is
`data/diagnostics/reviewer-baseline-repeatability-v61-2026-11-02/`. It contains
cases, exact selections/gold, twelve requests, source identities, renderer checks,
metadata, scoring, budget, stops, runner, inspection/sealing tools and mock tests.
The final `plan.json` binds the public plan, bundle assets and runtime/historical
source fingerprints. The tracker records its final hash and verification results.

Verification exercises all twelve requests and clean restarts, the immediate
delivery stop, malformed/empty/length responses, non-200 and unknown usage,
metadata drift, approval scope, tampering, semantic continuation, masked export,
sealed notes, protected judgments and separate recurrence categories. Real HTTP
transports and database access are blocked in tests; provider responses are
in-memory fixtures. The previously captured PE length response is replayed only
as a local terminal fixture, with no new model call or partial-answer scoring.

The initial sandboxed asynchronous test stalled and was stopped; its verification
record also retains corrected typing findings. A later run identified an overly
broad leakage assertion matching the historical phrase “non-repeatable event.”
The check was corrected while exact historical wire equality remained required.
No request, prompt, source or gold judgment was changed to make that check pass.

**253 offline tests pass:** 80 comparison tests, 22 gateway/contract tests,
67 delivery/repeatability regressions and 84 usage regressions. Ruff lint/format
and strict mypy pass on ten scripts. Historical MA/PE score replay passes
unchanged. The freeze binds **2,283 historical/runtime source fingerprints**.
The successful checks are in `verification-final.json`; earlier failed checks
remain separately preserved. No live approval file or live-run directory exists.

```powershell
$env:PYTHONPATH = 'engine;apps/api;apps/worker'
.venv/Scripts/python.exe -X utf8 data/diagnostics/reviewer-baseline-repeatability-v61-2026-11-02/freeze.py verify
```

Human review remains focused on feel, flow, character and story-breaking details.
Mechanical evidence belongs in the diagnostic appendix; factual accuracy alone
does not establish edit necessity, preservation or emotional effectiveness.
No production code, prompt, graph, schema, canonical prose, writer route, issue
body or mandatory Blueprint checkpoint changes. No issue is closed or edited
externally. **Step 19 IN PROGRESS; Step 20 NOT STARTED; inference PAUSED pending
separate approval; full workflow canary ON HOLD.**
