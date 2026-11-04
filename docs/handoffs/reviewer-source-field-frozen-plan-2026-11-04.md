# U/C source-field comparison: approval plan

Date: **2026-11-04**. **FROZEN AND VERIFIED LOCALLY; LIVE APPROVAL PENDING.**
Maximum **16 attempts, zero retries**. No generation, story-bearing token count
or current model-catalog request has been sent. Production **prompt 61 / graph 9 /
fulfillment policy 1**, active profiles and the full workflow canary remain unchanged;
the canary is **ON HOLD**.

This follows the [source/field and quotation-scope audit](reviewer-witness-contract-audit-2026-11-03.md).
The hypothesis is that coupling each field to its actual source in the generation
schema reduces binding errors without losing grounded judgments. The evidence
unit is explicitly the same in both arms: the complete immutable source section
selected by an exact quotation.

## Arms and common baseline amendment

Use **`gpt-6-luna` with `reasoning.effort: "high"`** in both arms, through the
existing OpenAI Responses adapter. The model and reasoning setting are unchanged
from the completed Luna comparison. The private model specification retains the
requested alias; no production catalog or profile changes.
[Official model documentation](https://developers.openai.com/api/docs/models/gpt-6-luna).

- **U — independent fields:** the witness schema separately lists allowed source
  versions and allowed field pointers. An impossible combination can satisfy
  those two lists, then fail the application's location check.
- **C — source-bound fields:** the same witness item uses a nested `anyOf` branch
  per version, with only fields registered for that source. Every legitimate
  source/field pair remains available. This witness-item schema is the sole
  between-arm treatment, represented both in the response-contract message and
  the native strict schema.

Both arms retain the full sources, diagnostic critic report, selected complete
claims, registry and whole-claim workload. There is no active-slot or smaller-batch
treatment. A witness still has `version_id`, `field` and `quote`, with a 1–512
character quote, at most eight distinct witnesses per claim and 8,000 quotation
characters per response. Definite judgments require evidence; uncertainty can
use an empty array with an adequate scope explanation.

Both arms receive the **same explicit section-locator instruction**: a quote
addresses one complete registry field or one prose paragraph. The quote need not
contain every premise if its selected section does. The union of selected sections
must adequately cover the whole claim and material explanation. Adjacent sections
are not silently included. Exact location remains distinct from semantic support.

This is a declared **common baseline amendment** from historical WB's ambiguous
instruction and exact-span scoring. The four historical U wires differ from their
saved WB wires only at `/input/0/content`, where that scope clarification is added.
Sources, selections, schema, model and effective settings remain identical. New
scores cannot be interpreted as improvements over the old exact-span scores;
all historical scores and the previous no-promotion decision remain unchanged.

The documented strict-output subset permits nested `anyOf` subject to its schema
limits. Local checks verify the transformation and finite source/field combinations;
native server acceptance and generated behavior remain unverified. An unsupported
schema response is terminal, with no simplified fallback.
[Structured-output documentation](https://developers.openai.com/api/docs/guides/structured-outputs).

## Cases, claims and presentation

| Family | Status | Claims per block | Main contrasts |
| --- | --- | ---: | --- |
| H1 | Saved historical scene, report and selections | 7 | Wrong source/path pairs; private-flourish inference; decision versus overrun; compound date evidence |
| F3: The Bell Without a Boat | Saved prior fresh-family control | 8 | Blueprint versus separate plan fields; performed private test; motive omitted by a short quote; next plan opens outside |
| F5: The Last Steam Ticket | Fresh authored scene, 520 words | 8 | Private tooth-spacing test performed; next plan opens inside; accurate speaker/rejection claim; repeated dialogue |
| F6: Counterweight at Dawn | Fresh authored scene, 490 words | 8 | General origin versus unperformed concealed-pin test; next plan opens outside; false protagonist attribution; repeated dialogue |

Every family has **PC** (draft before planning/context) and **CP** (context before
draft) blocks. Four families × two blocks × two arms give **eight pairs / sixteen
attempts**, **62 claims per arm / 124 fixed slots**, including **32 fresh claims per
arm**. Reordered presentations are not independent stories.

H1's historical PC/CP selections differ. Preserve them within each matched U/C
pair; do not interpret their cross-block differences as source-order effects.
F3/F5/F6 have identical selections across orders. Each fresh family includes a
complete five-scene blueprint, separate current assignment, whole draft and
unavailable-source scope record. Fresh gold has both positive and negative
contrasts across families, including unavailable evidence that requires uncertainty.

Frozen pair order, alternating the first arm:
**F5-PC U/C; H1-CP C/U; F3-CP U/C; F6-PC C/U; H1-PC U/C;
F5-CP C/U; F6-CP U/C; F3-PC C/U.**

Exact source versions, messages, domain/native schemas, count bodies, claims,
expectations, adequate-section criteria, illustrative witnesses, work fingerprints
and inspection slots are stored in the private bundle. Gold and authored probe
answers never enter the model messages. Examples are not an exclusive evidence
whitelist and are not live model results.

## Frozen scoring

Inspect all 124 fixed slots, including unavailable/unstarted deliveries, against
the complete sources and whole propositions. Record delivery, source/field and
literal location, label, material explanation and adequate selected-section
coverage separately. Use these categories in order:

1. **Unavailable:** missing, invalid or unstarted delivery; no partial-final rescue.
2. **Semantic:** wrong whole-claim label or materially unsupported explanation.
   Record citation problems as additional observations.
3. **Citation-only:** correct label and material explanation but wrong, missing,
   unresolved or insufficient selected evidence.
4. **Grounded:** correct label and explanation with adequate resolved evidence.

Missing, repeated, altered and cross-entry quotations remain unresolved without
repair. U's globally allowed but wrongly paired version/field is a validly shaped
unresolved witness. C's same impossible pair violates its schema and invalidates
the response. Report both delivery and fixed-slot outcomes so this distinction
cannot disappear from denominators. Schema-valid unresolved witnesses alone do
not trigger the invalid-delivery stop.

Full source context informs the judgment; only precisely selected sections supply
cited coverage. Compound premises and governing obligations must all be covered.
Purposeful action can establish a decision; later overrun does not erase earlier
fulfillment. A plan's opening can be judged from the plan without an observed
future scene. General origin does not establish a particular private test. Preserve
speaker attribution, negation and unavailable-source uncertainty. H1's contextual
relation remains separately inspected; component labels do not imply whole-relation
support. The schema cannot settle whether a pacing criticism is editorially useful.

The bounded continuation screen requires:

- All sixteen complete deliveries and all eight matched pairs.
- At least **two distinct family/full-claim U citation-only → C grounded recoveries**.
  A reversed presentation of the same claim cannot count twice. Full claim identity
  avoids confusing H1's differing per-block unit numbers.
- **No grounded-to-failure loss, no new semantic loss and no contextual-relation
  loss.** Semantic loss includes a U citation-only judgment becoming C semantic.
- **All 32 fresh C judgments grounded.**

A clean result without two recoveries establishes feasibility/repeatability only.
A terminal stop leaves the comparison incomplete. These are finite diagnostic
screens, not statistical proof or production qualification. The local scorer
aggregates explicit source-inspection decisions; it does not automate semantic
judgment or grant writer authority.

Inspect final-response packets in a reproducible shuffled order, masking arm
identity where practical, and save notes before decoding/aggregation. Evidence
shape and remembered cases can reveal the arm; this is assistant source inspection,
not a fully blind human study. Do not inspect hidden reasoning. Report tokens,
active latency, reference cost, delivery and binding completeness independently.

Human review remains focused on feel, flow, character and story-breaking details.
This diagnostic rewrites no story and cannot demonstrate better literary quality.

## Budget, endpoints and terminal stops

| Resource | Per attempt | Entire comparison |
| --- | ---: | ---: |
| Reserved attempts / maximum generation dispatches | 1, no retry | **16** |
| Input tokens | 24,000 | 384,000 |
| Generated tokens, including reasoning | 16,000 | 256,000 |
| Active count/generation time | 600 seconds | 9,600 seconds |
| Application planning allowance | $0.03 | **$0.48** |

The conservative token-max reference reservation is **$0.176**, using $0.125 for
every input token and $0.50 per million generated tokens. Published standard rates
are $0.10 input, $0.01 cached input and $0.125 cache-write input per million tokens.
Reference accounting is not an invoice or a guarantee of actual charges.
[Official pricing](https://developers.openai.com/api/docs/models/gpt-6-luna).

Approval must cover full unpublished fictional prose, complete planning/context,
critic reports, registry and exact admitted claims at **both** story-bearing
destinations: `https://api.openai.com/v1/responses` and the preceding
`https://api.openai.com/v1/responses/input_tokens`. The count body contains the
same model/input/schema/reasoning material. There are at most **16 count requests**
and **16 model-catalog preflights**, with no extra smoke generation.
[Token-count documentation](https://developers.openai.com/api/docs/guides/token-counting).

Preparation uses the saved account-visibility observation from 2026-11-03 and
current official documentation, with **zero new catalog calls**. Current account
access is unverified. After approval, catalog availability is checked before each
reserved count/generation attempt. Unexpected returned model identity stops the
run. No immutable snapshot is selected; alias drift remains a limitation.

The adapter uses native strict schema, default service tier, disabled truncation,
and `store`, `background`, `stream` false. No tools or prior-response state.
At high reasoning it omits portable temperature/top-p/seed, matching the previous
effective controls. Outgoing request bodies and destinations are checked against
the freeze before dispatch. The existing credential is accessed through the
secret store and excluded from captures; no credential setting is changed.

Counting and generation share a reservation. Failed counts and interrupted
reservations consume their attempt. Stop both arms on the first empty/invalid/
duplicate/missing/extra/changed-claim delivery, bad witness shape, unsupported
schema, refusal, truncation, transport/auth/quota failure, unknown input/output
usage, resource overflow, secret-boundary failure or frozen identity drift.
Preserve error chains, partial final data and unknown usage without crediting a
failed result. Retire unstarted slots; terminal runs cannot resume. Interrupted
catalog preflight cannot be replayed. Semantic failures alone do not stop the run.

No retry, model substitution, prompt revision, replacement generation, unused-call
transfer or reuse of historical retired allowances is permitted.

## Freeze and verification

Private bundle: `data/diagnostics/reviewer-source-field-v61-2026-11-04/`.
Plan SHA-256:
`b60e255769d5496b8a5632b116ff61b582d26b29df593688e18dea6026dec2c8`.
The freeze binds **34 preparation files and 3,521 source fingerprints**, including
exact native/count requests, complete cases/work, gold, scoring, inspection slots,
schedule, budget/stops, metadata baseline, runtime and verification. No approval
file or live directory exists.

**378 offline tests pass:** 216 diagnostic tests, 123 tracked assessment-work/result
tests and 39 provider/routing/execution tests. These cover every actual adapter
wire, 103 saved witness regressions, all 1,824 source/field combinations, both
evidence views, full-context identity, malformed output, unsupported native schema,
transport/usage failures, reservations, the sixteen-attempt ceiling, no retries,
scoring coverage, distinct-recovery counting and loss screens. No test is deselected.
The schema matrix retains **464 valid pairs** and excludes **1,360 impossible
combinations**. This establishes local constraints, not model recoveries.

Repository Ruff/format and strict mypy pass for **224 Python files**; all **eleven
private scripts** pass their corresponding checks. Deterministic preparation,
inspection-slot generation and the local audit reproduce their exact artifacts.
All source pins remain unchanged across verification. Development formatting and
test-helper lint findings were corrected before the final run; the development
unit suite passed on its first execution. Details are in `verification-history.md`.

The harness uses mock HTTP and a synthetic credential, blocking real HTTP
transports/external sockets/DNS/SQLite. Tracked integration tests use temporary
test databases. The installed uv-managed `.venv/Scripts/python.exe -X utf8 -m`
commands used the established outside-sandbox workaround for Windows async startup.
No current access or live schema-acceptance claim follows from those tests.
No production application, frontend, dependency or database schema changed;
the earlier full repository suite is not claimed as rerun. Original issue bodies
and posted GitHub URLs remain intact; no external issue was edited.

Next: approve this exact sixteen-attempt U/C comparison, including full prose/context
at both stated story-bearing endpoints; then execute once, inspect every fixed
slot and document the outcome. All fourteen issues remain open:
**Step 19 IN PROGRESS; Step 20 NOT STARTED; live calls PAUSED; canary ON HOLD.**
