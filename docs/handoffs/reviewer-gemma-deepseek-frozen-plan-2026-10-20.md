# Gemma and DeepSeek reviewer diagnostic plan

Date: 2026-10-20. Status: **FROZEN, LOCALLY VERIFIED, NOT RUN**.
Live inference is not authorized. The full workflow canary remains **ON HOLD**.

This diagnostic tests whether a simpler response interface improves usable editorial
assessments, and whether the same failures recur with a second model family. It uses
12 fixed original/revision pairs, two interfaces, and two models: **48 calls maximum,
one attempt per cell**. There are no writer calls, repair retries, fallback models,
or production changes.

The [human review](critic-writer-human-review-results-2026-10-20.md) found the earlier
Elara variants broadly equivalent and promising as a story foundation. Accordingly,
this test separates factual correctness, necessary versus optional editing, and
supported comparative claims from literary preference. It does not award quality
points for smaller diffs or agreement with the coordinator's preferred wording.

## Questions and comparison

1. Does application-owned source binding reduce malformed reports without weakening
   factual or editorial judgment?
2. Does DeepSeek behave differently from Gemma on the same sources and contracts?
3. Can a reviewer distinguish a genuine assignment failure from permissible variation,
   and avoid inventing a comparative gain or loss when prose is identical?

| Interface | Frozen behavior |
| --- | --- |
| V2 | Existing comparative-review judgment instructions and final response contract. The model returns version IDs, catalog references, and complete exact quotations. Its schema is instantiated with each case's task IDs. |
| C1 | The same complete source packet and the same system judgment instructions. The final delivery contract accepts short references such as `O001` or `R001`; the application supplies source versions and exact quotes from the request's immutable catalog. |

C1 retains every task, fact, changed-unit, craft, mandatory-failure, and literary
comparison field. It removes copying of version IDs and quotations and does not
require fingerprinted handles. The application cannot choose evidence or alter
judgments. An unknown reference fails validation. A known but irrelevant reference
can pass structure and still fail semantic inspection.

The entire system message and source-data message are identical across interfaces
for each case. Only the final response-delivery message differs. Both models receive
identical messages for each case/interface. Production prompt **61**, graph **9**,
and fulfillment policy **1** remain unchanged.

## Models and fixed settings

| Model through local Ollama | Frozen local manifest digest |
| --- | --- |
| `gemma4:31b-cloud` | `c382fbfbc73b6fdd08c8549c23caedc6e62eb09933c65a1fb82dbf3398320a4e` |
| `deepseek-v4.1-flash:cloud` | `e04da138d31e0c9468e982e1ae9503d06cb7e170caa16a90c17d931c4aa140f8` |

Both use temperature **0.2**, top-p **0.95**, seed **20261020**, and explicit
`think: false`. Metadata captured locally confirms that both advertise this setting.
DeepSeek's advertised default is high thinking, so omission of the explicit setting
would change the experiment. The seed is a reproducibility setting, not a guarantee
of identical randomness across model families or remote deployments.

Model tags, digests, and capability/thinking metadata are checked again before each
dispatch. Local manifest pinning detects local catalog changes; it cannot prove that
the cloud backend never changes behind a tag. The experiment describes these
deployments under these settings, not model-family quality at every reasoning level.

There are 24 calls per model and 12 per model/interface. The four model/interface
combinations rotate within each case; each occupies each order position three times.
There is one fixed presentation direction, original then revision, and one draw per
cell. This pilot does not estimate order sensitivity or run-to-run variance.

## Frozen cases

The full text, exact source identities, construction provenance, diffs, catalogs,
and expectations are in the private
[casebook](../../data/diagnostics/reviewer-crossover-v61-2026-10-20/casebook.md).
The eight new pairs are constructed offline from saved scene material, not newly
generated writer results. New negative revisions deliberately create errors.

| Case | Context and comparison | Frozen factual expectation |
| --- | --- | --- |
| r01 | Elara: unchanged optional duplicate, historical b07 | Optional request remains unmet; required facts survive; no mandatory failure or invented comparative effect. |
| r02 | Elara: unchanged completed entry, historical b08 | Mandatory outside endpoint remains violated; the earlier decision and touch/pull remain fulfilled; prose is identical. |
| r03 | Elara: minimal entry deletion, historical b05 | Entry violation is repaired; preparation still expresses commitment to enter; touch/pull survive. |
| r04 | Elara: actual saved optional duplicate repair, historical b04 | One duplicate is removed and one survives; optional request is addressed; required facts survive. |
| r05 | Elena: future dates and realization removed | Required ten-years-ahead realization is lost; verification preparation survives; mandatory failure. |
| r06 | Elena: definitive handwriting match appended | Decision to verify and date realization survive; establishing the match violates the no-match endpoint. |
| r07 | Safehouse: truce replaced with mutual refusal | Discovery of the handlers' omission survives; the required truce is lost; mandatory failure. |
| r08 | Safehouse: all three leave for the woods | Discovery and truce survive; the assigned locked-room exit state is violated. |
| r09 | Elena: small opening wording variation | Required facts and endpoint survive; no invented mandatory defect; literary preference is open. |
| r10 | Elena: optional adjacent sentence duplicate removed | One occurrence survives; requested optional edit is addressed without loss of required facts. |
| r11 | Safehouse: requested explanatory phrase removed | Action, discovery, and truce survive. Explicit characterization changes, but reader benefit or harm is not predetermined. |
| r12 | Safehouse: unchanged prose with no-change permitted | Optional task permits leaving text alone; required facts survive; no invented comparative effects. |

There are four cases in each group: existing controls, clear failures, and permissible
variation/craft controls. They come from **three scene families**, not twelve
independent stories. The safehouse source is a saved v33 benchmark scene; Elena uses
the existing diagnostic scene/context; Elara uses the sealed completed comparison.
These sources do not constitute a new full-workflow benchmark.

The new failure cases ask whether proposed line edits retain the assignment. Their
editing conditions are explicitly coordinator-constructed, not fabricated prior
critic reports. Original and revision prose have separate identities even on no-op
controls. No supplied text is treated as an instruction to execute.

## Scoring and interpretation

The frozen [scoring rules](../../data/diagnostics/reviewer-crossover-v61-2026-10-20/scoring.json)
separate the following dimensions:

- **Delivery:** complete response, valid schema, exact record coverage/order, and
  request-bound citations. Invalid reports remain invalid.
- **Task and fact judgment:** whether the requested edit is addressed, the native
  turning point and outcome survive, and a mandatory failure remains. A later
  boundary overrun must not erase an earlier fulfilled event.
- **Necessity:** whether a change addresses the requested task, is actually needed
  next to it, or is optional, unsupported, benign, or uncertain. A true old defect
  does not justify every part of a replacement.
- **Comparative support:** whether claimed gains/losses follow from the actual
  source and diff. No-op comparisons cannot acquire new losses merely because the
  same prose has a different version ID.
- **Literary preference:** recorded descriptively. There is no prescribed winner
  for changed prose. Supported ties, mixed effects, and uncertainty are acceptable.

Mechanical label checks run locally. Their success is insufficient for a usable
assessment: each textual claim still needs inspection against the complete prose,
assignment, and diff. The operator export shuffles normalized assessments and hides
model/interface labels before this inspection. Invalid raw outputs may be inspected
separately to diagnose delivery failures; they cannot become usable passes.

A **usable supported assessment** requires valid delivery, correct frozen labels,
and supported task/fact/mandatory, necessity, and comparative claims. Unresolved
semantic support remains pending. This support review is coordinator analysis,
not independent human story-quality certification. A plausible artistic judgment
may differ from the coordinator's preference without being erroneous.

Report every cell and each dimension separately, with denominators of 12 per
model/interface and four per group. Consider C1 promising for a model only when it
increases usable supported assessments, has no paired loss in mandatory/fact
accuracy, and introduces no new unsupported mandatory flags on permissible controls.
Delivery-only gains are reported as delivery gains. Cross-model differences and
remaining failures guide a later proposal; neither automatically promotes a model
or interface into production.

The prior human ties remain calibration evidence, not a universal answer key.
Exact repetition counts and lost words are mechanical observations, not proof of
reader harm. No new human review of these similar variants is required for this
diagnostic. Later quality work still needs meaningful whole-story comparisons,
overall feel/emotion, flow, character, and story-breaking concerns under the accepted
benchmark contract.

## Budget and stop rules

| Limit | Frozen allowance |
| --- | ---: |
| Inference calls | 48 total; 24 per model; 12 per model/interface |
| Attempts | One per cell; zero retries or replacement samples |
| Input allowance per call | 24,000 tokens |
| Output allowance per call | 8,000 tokens |
| Requested context per call | 32,000 tokens |
| Active request timeout | 300 seconds |
| Aggregate input reservation | 1,152,000 tokens |
| Aggregate output reservation | 384,000 tokens |
| Aggregate active request time | 14,400 seconds, at most four hours |

Frozen requests measure 12,066–16,230 tokens using UTF-8 bytes divided by four,
rounded up. That is an estimate, not a tokenizer guarantee. No input is silently
trimmed. Returned provider token counts must remain within the frozen allowances;
missing or excessive usage stops the run. Cloud enforcement of context/output
options is not assumed to prove a billed-spend cap.

At the rates checked on 2026-10-20, the maximum reserved-token estimate is
**$0.56064**: $0.15744 for Gemma and $0.40320 for DeepSeek at peak rates. Use a **$0.60
planning allowance**, without assuming cache discounts or off-peak pricing.
[Ollama's pricing table](https://ollama.com/pricing) lists Gemma at $0.14 input /
$0.40 output and DeepSeek at $0.30 input / $1.20 output per million tokens.
These are usage estimates; the current gateway does not supply actual per-call
charges, so actual cost remains unknown under ADR 0017.

Continue to the next fixed cell after a valid report, a captured invalid report,
or a captured, identified, in-budget `length` completion. A length completion fails
the cell and is never parsed, salvaged, or retried.

Stop all further dispatch on transport/auth/rate-limit failures, timeout,
cancellation, unknown outcome, missing capture or usage, excessive usage/time,
model/digest/capability drift, unexpected thinking output, another finish reason,
source/request/code mismatch, incomplete previous cell, concurrent execution, or
approval mismatch. An invalid provider envelope or other unclassified runtime error
also stops dispatch. No automatic fallback or prompt adjustment is permitted.
Reservations are persisted before submission and consume the cell even when its
outcome is unknown. Completed cells replay without another call. Interrupted or
terminal cells require inspection and cannot silently become retries.

## Local evidence and execution boundary

Local verification passed **70 tests**: 48 diagnostic harness tests and 22 existing
model-gateway/contract tests. The harness exercises all 48 cells through the actual
Ollama adapter with an in-memory HTTP transport, partial-run resume and completed-run
replay, invalid and empty truncated outputs, cancellation/transport failures, model
drift, usage limits, citation/schema failures, evidence tampering, concurrent locks,
and the approval gate. Archived V2 responses reproduce **15/18 valid** reports.
Ruff lint/format and strict mypy pass on all five diagnostic scripts.

The existing b05/V2 request's three messages remain byte-for-byte identical in r03/V2.
All paired interface source messages are identical, and all 48 requests reconstruct
from the frozen cases. Full prose exports and catalog spans match their sources.
The offline mocks establish harness behavior, not model judgment or literary quality.
Production application and frontend code were not changed; no frontend build was
needed for this private diagnostic harness and documentation change.

Private preparation directory:
`data/diagnostics/reviewer-crossover-v61-2026-10-20/`.

- [Frozen source snapshots](../../data/diagnostics/reviewer-crossover-v61-2026-10-20/sources.json)
- [Cases and exact expectations](../../data/diagnostics/reviewer-crossover-v61-2026-10-20/cases.json)
- [Ordered 48-cell schedule](../../data/diagnostics/reviewer-crossover-v61-2026-10-20/schedule.json)
- [Stop rules](../../data/diagnostics/reviewer-crossover-v61-2026-10-20/stop-rules.json)
- [Local verification](../../data/diagnostics/reviewer-crossover-v61-2026-10-20/verification.json)
- [Preparation seal](../../data/diagnostics/reviewer-crossover-v61-2026-10-20/plan.json)

The preparation seal binds all requests, code, cases, scoring, metadata, verification,
source hashes, runtime dependencies, and this plan. Full unpublished prose remains
under ignored `data/`; the repository handoff records the plan and provenance.

Any future live approval must bind the seal, the **48-call ceiling**, these exact
models, and transmission of full unpublished scene prose, source critique where
present, and blueprint/bible/assignment context to **Ollama Cloud through the local
daemon**. The runner refuses to construct a live transport without that approval.
The preparation task does not grant it.

Step 19 remains **IN PROGRESS**. Step 20 is **NOT STARTED**. The full workflow canary
remains **ON HOLD**, and no production prompt, graph, schema, or human checkpoint
changes.
