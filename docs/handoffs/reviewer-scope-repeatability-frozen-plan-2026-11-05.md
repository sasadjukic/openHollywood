# Sol-high scope-separated repeatability — frozen plan, 2026-11-05

**Prepared and verified locally; awaiting separate live approval.**

This follows the [claim-scope and whole-claim gold audit](reviewer-claim-scope-gold-audit-2026-11-05.md).
It asks whether explicitly scoped factual judgments and adequate evidence remain
stable when assignment requirements and observed action vary independently.
It does not reinterpret the previous diagnostic's scores or measure literary effect.

**No generation, input-count, catalog or daemon calls occurred during preparation.**
Production prompts/profiles remain unchanged; the full workflow canary is ON HOLD.

## Frozen design

- Model: **`gpt-6.1-sol`, high reasoning**, same reviewed adapter specification and
  U section-locator instructions as the prior Sol diagnostic. Current official
  documentation supports high reasoning and structured output; account access and
  acceptance of these actual requests remain untested. [Official Sol model documentation](https://developers.openai.com/api/docs/models/gpt-6.1-sol).
- **Four fresh complete fiction families × two source orders × two repeats =
  16 attempts.** Each request has seven complete selected claims: **112 fixed slots**,
  representing 28 case-bound claims. PC presents prose before context; CP reverses
  those source blocks. All sources, report fields and selections remain present.
- Within each family/order, the second attempt has **identical generation and
  input-count bodies and the same work fingerprint**. Attempt/request identities
  differ. Across orders, only the source-block presentation changes.
- No prompt treatment, model substitution, evidence-contract change, larger output
  allowance or new production routing. These are new source/claim fixtures, not
  exact historical control requests or a same-claim wording-recovery comparison.

| Family | Complete scene | Investigation required? | Choice and specified check depicted? | Asserted means relation |
| --- | --- | --- | --- | --- |
| S1 | Mira's final theatre rehearsal; amended cue sheet | Yes | Yes: purposeful investigation and lamp check | Supported: turning the key opens the cupboard |
| S2 | Jonah and Eda at a ferry landing | Yes | No: explicit refusal and nonperformance | Unsupported: gate is already raised before Jonah pulls the bell cord |
| S3 | Rina and Ivo in their bakery | Explicitly optional | Yes: investigation and full arithmetic check | Unsupported: the key opens the drawer before the arithmetic |
| S4 | Toma and Vesna packing the household archive | Explicitly optional | No: investigation declined; weighing procedure absent from the complete draft | Supported: damp fingers extinguish the candle |

The means claims include two supported and two unsupported relations, distinct
from whether the investigative procedure occurs. Every scene also contains a genuine
current endpoint violation, a misattributed assertion, and a declared unavailable
continuation. S2's explicit nonperformance and S4's absence of depiction remain
different evidence situations.

The four matrix cells use different scene families. This is a bounded scope and
repeatability screen, **not a causal estimate of assignment wording**, a population
model ranking or evidence of better storytelling.

## Whole claims and gold

Each request asks the same seven kinds of question, separately:

| Unit | Assessed proposition | Required evidence scope |
| --- | --- | --- |
| Q001 | Current assignment requires the investigative decision | Current assignment authority, including explicit optionality where present |
| Q002 | Current draft depicts that decision | Observed action/intent or refusal; an obligation cannot prove occurrence |
| Q003 | Current draft completes every defining step of the specific check | Definition plus draft evidence for all steps/result, or adequate nonperformance/absence evidence |
| Q004 | The named action is the means of the named resulting event | Whole means relation, preserving actor and timing; two occurring events alone are insufficient |
| Q005 | The draft violates the specified current endpoint | Authoritative endpoint plus violating event and boundary state |
| Q006 | The protagonist makes the alleged assertion | Complete attributed exchange, including denial or epistemic qualification |
| Q007 | The unavailable continuation resolves the conflict | Scoped uncertainty; no invented evidence from an outline |

Frozen expected labels, in Q001–Q007 order:

| Family | Q001 | Q002 | Q003 | Q004 | Q005 | Q006 | Q007 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| S1 | Supported | Supported | Supported | Supported | Supported | Unsupported | Uncertain |
| S2 | Supported | Unsupported | Unsupported | Unsupported | Supported | Unsupported | Uncertain |
| S3 | Unsupported | Supported | Supported | Unsupported | Supported | Unsupported | Uncertain |
| S4 | Unsupported | Unsupported | Unsupported | Supported | Supported | Unsupported | Uncertain |

All labels are authored before responses. The private [case and scoring packet](../../data/diagnostics/reviewer-scope-repeatability-v61-2026-11-05/cases-and-scoring.md)
contains every exact claim, rationale, adequate-evidence criterion and illustrative
source reference. [Cases](../../data/diagnostics/reviewer-scope-repeatability-v61-2026-11-05/cases.json)
retain the full prose and context; [requests](../../data/diagnostics/reviewer-scope-repeatability-v61-2026-11-05/requests.json)
contain every exact body. Those links refer to local private artifacts, not published
GitHub attachments.

The local design audit binds whole selections, fields, source versions and component
inventories. It rejects event evidence substituted for authority, omitted means
components, unresolved qualifiers and incomplete absence review. These are checks
of authored declarations; they do not mechanically prove the author's semantic gold.
Gold and audit annotations are excluded from model input.

## Fixed schedule

The two occurrences of each family/order are five to eight attempts apart.
Second repeats are interleaved with remaining first occurrences.

| Attempt | Trial | Attempt | Trial |
| --- | --- | --- | --- |
| 1 | SR-1-S1-PC | 9 | SR-1-S4-PC |
| 2 | SR-1-S2-CP | 10 | SR-2-S3-PC |
| 3 | SR-1-S3-PC | 11 | SR-1-S3-CP |
| 4 | SR-1-S4-CP | 12 | SR-2-S4-CP |
| 5 | SR-1-S2-PC | 13 | SR-2-S2-PC |
| 6 | SR-2-S1-PC | 14 | SR-2-S1-CP |
| 7 | SR-1-S1-CP | 15 | SR-2-S4-PC |
| 8 | SR-2-S2-CP | 16 | SR-2-S3-CP |

## Scoring and success condition

Inspect every final reason against complete primary sources. Record delivery,
binding, whole-claim interpretation, material explanation correctness and adequate
evidence separately. Classify every fixed slot as unavailable, semantic failure,
citation-only failure or grounded. A correct label for a substituted question,
unsupported material explanation or true subset of a claim does not pass.

An exact quotation locates its entire immutable registry field or single prose
paragraph. It is not itself the whole evidentiary span. Credit no uncited neighbors;
accept alternative sections when their contents provide genuinely adequate coverage.
Correct location does not establish support. Preserve reason materiality explicitly;
ancillary concessions cannot silently change the frozen evidence requirement.

Inspect Q004's means relation and Q005's endpoint relation in full. No automatic
truth follows from component labels, shared evidence or co-occurrence. Q007 may
validly return uncertain with no evidence because the continuation is unavailable.

The bounded screen requires **all 112 slots grounded**: Q001–Q005 in both orders
and repeats, with no remaining Q006/Q007 control failures. Failed and undispatched
slots remain in the denominator. No gold repair, replacement request or corrected
aggregate after responses.

Publish 56 same-family/order repeat pairs and 56 cross-order pairs, including label
agreement, categories, recoveries/losses and both-grounded status. Stable wrong
answers are failures. Exact wording of reasons or exact equality of adequate
citation sets is not required. Two repeats do not estimate a population success rate
or establish an identical provider backend snapshot.

Passing would support only a next bounded **read-only claim-scope integration check**.
It would not promote a model, authorize rewrites or qualify craft. Future human
review remains focused on overall feel, flow, character and story-breaking details.

## Budget, endpoints and stops

The **16-call ceiling means sixteen generation attempts**, with separately bounded
supporting requests:

| Resource | Maximum |
| --- | ---: |
| Generation attempts | 16 |
| Full-context input-count requests | 16 |
| Catalog preflight reads | 16 |
| Input tokens per attempt | 24,000 |
| Generated tokens per attempt, including reasoning | 32,000 |
| Active count/generation time per attempt | 600 seconds |
| Additional catalog timeout per attempt | 25 seconds |
| Total input / generated reservation | 384,000 / 512,000 tokens |
| Total active time / additional catalog timeout reservation | 9,600 / 400 seconds |
| Conservative reference cost reservation | **$6.08** |
| Planning allowance | **$9.60** |

The reference retains $2.50 per million input tokens as the input/cache-write bound
and $10 per million generated tokens, without cache discounts: $0.38 per attempt
against a $0.60 planning allowance. These are reference reservations, not an actual
billing guarantee. Reasoning tokens are already included in output. [Official Sol pricing](https://developers.openai.com/api/docs/models/gpt-6.1-sol).

After separate approval, **full unpublished fictional prose/context, report and
selected claims will be sent to both**:

- `POST https://api.openai.com/v1/responses/input_tokens`
- `POST https://api.openai.com/v1/responses`

Catalog access is limited to `GET https://api.openai.com/v1/models` through the
existing adapter. The existing approved application credential route is retained;
no key is written into this bundle. Catalog availability alone cannot establish
backend weight identity. Account access and server schema acceptance await the
approved run. No Ollama calls are involved.

Keep store/background/stream false, truncation disabled, standard service tier and
native strict output. Portable temperature/top-p/seed are omitted by the unchanged
adapter. No tools, previous-response chain, fallback or abbreviated context.

Stop the entire comparison on the first terminal preflight, identity, delivery or
resource failure: source/request/runtime/model/spec drift, unavailable model,
authentication/quota error, count error/overflow, invalid/empty/duplicate/missing
output, refusal, truncation, transport/cancellation, unknown or inconsistent reported
input/output/reasoning usage,
over-budget output/time, or a secret-boundary failure. Preserve gateway error chains
and unknown usage. A failed input count or interrupted attempt reservation remains
consumed; an interrupted catalog reservation stops without replay.

**No retries, extra probes, fallback, allowance transfer or terminal resume.**
Semantic errors and unresolved evidence locations are scored, not silently repaired
or treated as an early semantic stop. No previous unused budget is reused.

## Verification and freeze

**322 offline tests pass**, with nothing deselected: 160 local harness/metadata/
scope/repeatability tests, 123 tracked assessment tests and 39 provider/routing/
execution tests. Mocked transport checks exercise the actual adapter's exact count
and generation bodies, strict schema, terminal usage/error capture, cancellation,
budget/approval boundaries, full-context rendering and whole-claim scoring.

Repository Ruff, formatting and strict mypy pass for **224 files**. The same checks
pass separately for all **14 diagnostic scripts**. Cases, requests, gold, fixed
slots and the design audit reproduce deterministically. Frontend checks are
inapplicable; a full repository test run is not claimed.

Manual review corrected one **unfrozen** S2 ambiguity: the gate lift now finishes
before the bell cord is touched, excluding an indirect-trigger interpretation.
The initial local build is preserved as inert preparation history; every derived
request was regenerated and final verification rerun. No model response informed
that clarification and no frozen artifact was amended.

Private root: `data/diagnostics/reviewer-scope-repeatability-v61-2026-11-05/`.

**89 frozen files; 5,307 source fingerprints.** Plan SHA-256:

```text
36c22411309c27d1a5a59e75ed135df3b9a4db9aebbaf25754a9934e2e345a6b
```

Approval is absent. The next action, only after separate approval of this plan and
both full-context endpoints, is one bounded execution followed by inspection of all
fixed slots, documentation of results and a tracker update.

All fourteen issues remain open; issue bodies and posted URLs remain unchanged.
**Step 19 IN PROGRESS; Step 20 NOT STARTED; live calls PAUSED; production prompts
unchanged; full workflow canary ON HOLD.**
