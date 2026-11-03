# Luna MA/quote-witness comparison: approval plan

Date: **2026-11-03**. **FROZEN AND VERIFIED LOCALLY; LIVE APPROVAL PENDING.**
Maximum **16 attempts**, zero retries. Generation **0**; story-bearing token
counts **0**. One authorized model-catalog check confirmed account visibility.
Production **prompt 61 / graph 9 / fulfillment policy 1** and active profiles
remain unchanged. The full workflow canary remains **ON HOLD**.

This follows the [read-only assessment integration](assessment-result-integration-2026-11-03.md)
and the [scope/citation audit](reviewer-scope-citation-audit-2026-11-03.md).
It asks whether exact source quotations improve evidence selection when Luna
assesses the same full-context, whole-claim workload.

## Approval scope and model amendment

Use **`gpt-6-luna`**, as requested, through OpenAI Responses with explicit
**`reasoning.effort: "high"`** in both arms. The model documentation lists Responses,
structured outputs and high reasoning support. Its documented default is medium;
the comparison retains the previous explicit high setting.
[Official model documentation](https://developers.openai.com/api/docs/models/gpt-6-luna).

Approval would authorize the full unpublished fictional prose, complete planning
context, source-scope records, saved diagnostic critic reports, registry and exact
selected claims to **`https://api.openai.com/v1/responses`**, preceded by
**`https://api.openai.com/v1/responses/input_tokens`**. The count request contains
the same model/input/schema/reasoning material. It also waits for approval.
[Token-count documentation](https://developers.openai.com/api/docs/guides/token-counting).

The four historical MA request bodies match their saved controls except for
`/model`, amended from `gpt-5.6-luna` to `gpt-6-luna`. Their messages, full claims,
gold and schema constraints remain unchanged. This is a comparison **within the
new model**, not a causal test of improvement over the older Luna. The model spec
is injected privately; no production catalog, profile or credential setting is
modified. The existing credential is reused only through the secret store.

One non-generating `GET /v1/models` check confirmed `gpt-6-luna` is visible. That
does not establish generation access, live schema acceptance, billing or quality.
No separately documented immutable snapshot was selected; alias drift remains a
limit. Any unexpected returned model identifier stops the comparison.

## Frozen cases and intervention

| Family | Status | Claims per presentation | Main contrast |
| --- | --- | ---: | --- |
| H1 | Historical full MA control | 7 | Decision versus overrun; general handwriting match versus private flourish; compound date evidence |
| W2 | Historical full MA control | 8 | Decision/touch/vibration, date realization, source scope, plan reference type and attribution |
| F3: The Bell Without a Boat | Fresh authored scene and full planning context | 8 | Specific clapper-isolation test actually performed; next plan opens outside |
| F4: Rain at Platform Nine | Fresh authored scene and full planning context | 8 | Specific hidden-notch calibration not performed; next plan explicitly opens inside |

Every family appears in **PC** (draft before planning/context) and **CP** (context
before draft) presentation order. Four families × two orders × two arms gives
**eight pairs / sixteen calls**, **62 claim judgments per arm / 124 fixed slots**.
The fresh families supply **32 judgments per arm**. Reordered presentations are
paired observations, not independent stories. The fresh scenes deliberately
retain the known semantic classes and therefore provide limited generalization.

**MA:** one response assesses all seven or eight selected claims, citing the
existing S-prefixed registry references.

**WB (quote-witness):** the same full sources, report, registry, selections and
whole-claim instructions; only the existing evidence-output clause and its schema
item change. Each witness supplies immutable source version, field pointer and
an exact quotation of 1–512 characters. At most eight distinct witnesses per
claim and 8,000 quotation characters per response. The evidence clause is exactly
the earlier frozen quote-witness clause. No new active-slot schema or smaller
assessment workload is introduced.

The application locates exact occurrences and displays their containing source
sections. Missing, repeated or cross-entry quotations remain unresolved; no fuzzy
match, ID shifting, repair or inferred support. Validly shaped unresolved witnesses
are binding/citation outcomes and do not trigger the invalid-delivery stop.

The tracked work/scope and evidence-registry components validate local identity,
full context and exact source versions/sections. The historical array response
contract remains on the wire. The private witness adapter is deliberate and
read-only; location binding does not assign semantic support or writer permission.

Frozen pair order, with alternating first arm:
F3-PC (MA/WB), H1-CP (WB/MA), W2-CP (MA/WB), F4-PC (WB/MA),
H1-PC (MA/WB), F3-CP (WB/MA), F4-CP (MA/WB), W2-PC (WB/MA).

## Scoring and interpretation

Freeze the exact claims, expected whole-proposition labels, adequate-evidence
criteria and illustrative references before inference. Examples are not an
exclusive reference whitelist, and no expectations enter the model requests.
Inspect every fixed slot, including unavailable/unstarted deliveries:

- **Grounded:** correct whole-claim judgment and material explanation, with
  adequate resolved cited evidence.
- **Citation-only failure:** correct judgment and material explanation, with
  wrong, missing, insufficient or unresolved evidence.
- **Semantic failure:** wrong judgment or materially unsupported explanation;
  record additional citation problems separately.
- **Unavailable:** failed, missing or unstarted delivery. No partial-final rescue.

For WB, the exact quotation must itself cover the material premise; displaying
its containing paragraph does not automatically supply omitted evidence. Both
arms must cover compound premises and governing obligations. Keep source-plan
entailment separate from observed events, general origin from a particular private
test, speaker attribution from protagonist intent, and unavailable evidence from
disproof. A later overrun does not erase earlier fulfillment. H1 contextual
relations remain a separate inspection, with no automatic whole-relation credit.

The bounded continuation screen requires **all sixteen complete deliveries and
eight pairs**, at least **two distinct family/claim citation-only-to-grounded
recoveries**, **no paired semantic or grounded-judgment loss**, and **all 32 fresh
WB judgments grounded**. The two orders cannot double-count one recovered claim.
Apply the same no-loss check to observed contextual-relation judgments. A clean
result without two recoveries establishes feasibility only; a stop leaves the
comparison incomplete. These are finite diagnostic criteria, not statistical
proof or production qualification.

Shuffle final-response inspection packets and mask arm identity where practical;
output shape can reveal the arm, so do not claim fully blind evaluation. Inspect
final answers and source evidence, never hidden reasoning. Report input/generated/
reasoning/cached tokens, latency, reference cost and binding completeness separately.
Human literary judgment remains about feel, flow, character and story-breaking
details. This test neither rewrites stories nor establishes better story quality.

## Budget, delivery and stops

| Resource | Per attempt | Entire comparison |
| --- | ---: | ---: |
| Attempt/generation ceiling | One, no retry | 16 |
| Input tokens | 24,000 | 384,000 |
| Generated tokens, including reasoning | 16,000 | 256,000 |
| Active count/generation time | 600 seconds | 9,600 seconds |
| Application planning allowance | $0.03 | $0.48 |

Published standard prices are $0.10 input, $0.01 cached input, $0.125 cache-write
input and $0.50 output per million tokens. The conservative reference reservation
uses $0.125 for every input token, giving **$0.176** at both token maxima across
sixteen calls. This is reference accounting, not an observed bill or a guarantee
about actual account charges. [Official pricing on the model page](https://developers.openai.com/api/docs/models/gpt-6-luna).

There are at most sixteen story-bearing count requests and sixteen live model
catalog checks, in addition to the one completed preparation catalog check.
Counting and generation form one reserved attempt; a failed count or interrupted
generation reservation consumes the attempt. Interrupted catalog preflight cannot
be replayed. No separate smoke generation, retry, model substitution, unused-call
transfer or reuse of historical retired allowances is permitted.

Use the existing native strict-schema Responses adapter: `store`, `background`
and `stream` false; truncation disabled; default service tier; no tools or prior
response context. At high reasoning the adapter omits portable temperature, top-p
and seed. This matches the historical effective controls. The local strict-schema
transformation preserves the domain constraints.
[Structured-output documentation](https://developers.openai.com/api/docs/guides/structured-outputs).

Stop both arms at the first empty/invalid/duplicate/missing/extra/changed-claim
delivery, bad evidence shape, refusal, truncation, transport/auth/quota failure,
unknown input/output usage, resource overflow, secret-boundary failure or frozen
source/request/runtime/model drift. Approval and actual outgoing payloads are
checked before dispatch. Retain terminal error chains and unknown usage; retire
unstarted slots. Terminal runs cannot resume. Semantic failures alone do not stop
the run or authorize a repair call. No prompt revision occurs during execution.

## Freeze and verification

Private bundle: `data/diagnostics/reviewer-luna-witness-v61-2026-11-03/`.
Plan SHA-256:
`abd249390095bffd4a2430bbfd8234f69f688b5ca688398146d8d96b6b65931f`.
The freeze binds **32 preparation files and 3,178 source fingerprints**, including
exact native/count requests, full cases/work, claims/gold, inspection template,
scoring, schedule, budget/stops, model amendment, metadata, runtime and verification.
No approval file exists.

**251 offline tests pass:** 89 new harness tests, 123 tracked assessment work/result
tests and 39 provider/routing/execution tests. Tests exercise every exact adapter
wire, strict schemas, both renderers, Unicode/ambiguous/missing/cross-entry quotes,
full-context identity, terminal failures, preserved usage, approval/integrity
checks, interrupted reservations and the sixteen-attempt ceiling. The new paths
block real HTTP transports, external sockets/DNS and SQLite; tracked integration
tests use synthetic responses and temporary test databases.

Repository Ruff/format and strict mypy pass for **224 Python files**, and private
checks pass for **nine scripts**. Deterministic preparation reproduces the exact
artifacts; all 3,178 source pins remain unchanged across verification. A local
schema-order mismatch was caught and corrected before freezing: canonical disk
serialization must precede deriving the adapter's native required-key order.
The initial failed run and correction are recorded in `verification-history.md`.

The installed uv-managed environment ran checks through
`.venv/Scripts/python.exe -X utf8 -m`. Windows async startup required running the
mocked tests outside the sandbox. No tracked code, dependencies, frontend or
production build configuration changed; the prior full 1,363-test integration
result is not claimed as rerun. Native server acceptance and model behavior remain
unverified until the separately approved run.

Next: approve this exact **16-attempt `gpt-6-luna` MA/WB comparison**, including
full prose/context at both stated story-bearing endpoints, then execute once,
inspect all fixed slots and document the outcome. All fourteen issues remain
open; **Step 19 IN PROGRESS, Step 20 NOT STARTED; canary ON HOLD**.
