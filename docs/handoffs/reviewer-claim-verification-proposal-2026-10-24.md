# Proposed isolated claim-verification diagnostic — 2026-10-24

Status: **proposal only; not prepared, frozen or approved for inference**.
Basis: the completed [reference, explanation and group-relation audit](reviewer-reference-relation-audit-2026-10-24.md).
Production prompts stay unchanged; live calls are paused and the canary is on hold.

## Question and reason to test it

Can the same DeepSeek model distinguish supported from unsupported explanations
when it evaluates fixed claims against complete sources, instead of composing a
full comparative review at the same time?

The preceding D2/PC run often got task and endpoint verdicts right while adding
false explanations. The local audit shows that removing group-label failures
would recover only two PC reports. A general premise reminder was already
tested, and a fulfillment-field rename was already tested. Neither established
overall reviewer reliability. The new question isolates recognition of a supplied
claim from spontaneous explanation generation. It does not test a new writer,
provider, production reviewer role or story-quality preference.

Recommend this diagnostic before spending another full reviewer comparison on
the enum or a taxonomy change. The enum has useful local coverage but only one
observed reference-type failure in 32 responses. It cannot prevent a false claim
that cites real sentences. Keep its prototype out of this experiment so a schema
presentation change is not bundled with the new task.

## Proposed matrix: 24 attempts

| Dimension | Proposed scope |
| --- | --- |
| Model and route | Same `deepseek-v4.1-flash:cloud` through the local Ollama daemon to Ollama Cloud |
| Historical families | Three exact source packets: consultation/action (H), explanation/action (B), original/revision ownership (G) |
| Fresh families | Three genuinely new scenes, one testing each distinction with new actions, motives and explicit conditions |
| Presentation | Original then revision and revision then original, with explicit version ownership in both |
| Repetition | Two exact request repetitions per family/order, retaining the same settings and seed |
| Total | **6 families × 2 orders × 2 repetitions = 24 attempts**, including invalid or interrupted dispatches |

Each request contains the full original/revision, assignment, binding constraints
and the same source catalog, plus three fixed claims to assess. Freeze **18
distinct claim texts** before inference. Repeated requests yield **72 claim
judgments**, not 72 independent examples. Use a mix of supported and unsupported
claims with qualified literary interpretations among the supported controls;
vary the mix across families so no fixed per-request answer count is implied.
Do not provide expected labels, prior model verdicts, adjudication notes or an
instruction that every packet contains a particular kind of mistake.

Historical claims include unchanged captured failures and supported controls from
the local register. Fresh claims include authored false premises and supported
controls, explicitly identified as authored in the private key. Counterbalance
claim positions across families, retain those positions across source-order
swaps, and freeze an interleaved schedule. This isolates source order; claim-order
sensitivity would remain untested. Exact repeats measure observed repeatability,
not independent coverage or a guaranteed deterministic model.

The control claims must retain genuine consultation/endpoint violations and
reasonable intention/action or continuity readings. Fresh cases must distinguish
an explicit prerequisite from a desired explanation, and a replaced original
event from an event that actually remains in the revision. Do not manufacture a
mechanical gold winner for a subjective prose preference.

## Output and scoring to freeze during preparation

Use a small diagnostic output: claim ID, `supported` / `unsupported` / `uncertain`,
bounded O/R evidence refs and a short source-grounded reason. Retain the existing
strict JSON, duplicate-key, namespace, citation-cardinality and source-binding
checks. The compact schema is necessarily a new diagnostic task interface; it
is not an unchanged D2 request or a directly comparable treatment arm. No new
catalog enum, group taxonomy, premise card, retry or automatic output repair is
added. Retain complete sources rather than supplying answer-selected excerpts.

Before dispatch, freeze claim-level judgments and source-bound rationales, and
define supported literary readings as defensible interpretations rather than
the uniquely correct emotional response. Allow `uncertain` in output; for a
fixture with a definite supported/unsupported oracle it is an abstention, not a
correct recovery. Ambiguous authored cases should be revised or excluded before
freezing, never given a convenient oracle after results arrive.

Score these dimensions separately:

1. Valid complete delivery, including evidence membership and provenance.
2. Correct judgment of each fixed claim, counting uncertainty and failures in
   the attempted-call denominator; report supported-control false rejections
   separately from false-premise acceptance.
3. Whether the evidence and **entire** reason support that judgment. A correct
   label with an invented prerequisite, event or contradiction is not usable.
4. Whole-request usability: all three claims correct and all reasons grounded.
5. Results by family, historical/fresh status, source order and repetition;
   disclose repeat disagreement and any persistent mistake in both orders.

Shuffle/mask returned answers for source inspection before decoding order and
repeat identifiers. Adjudication remains assistant source inspection, with its
limits stated. It is not a new human preference test. Preserve raw invalid
answers and independently audit them; do not filter away failed deliveries.

This is a **descriptive diagnostic**, with no production advancement threshold or
paired D2-versus-candidate improvement claim. Historical D2/PC results supply the
question and frozen controls, not a contemporaneous comparison arm. If a claim
check looks useful, a later paired experiment must test whether it can improve
full reports without losing supported criticism. Do not treat that benefit as
already demonstrated here.

## Budget, stopping and interpretation

Proposed hard ceiling: **24 new attempts, zero retries**, no warm-up or automatic
completion calls. Retain the prior per-call limits of 24,000 input tokens, 8,000
output tokens, 32,000 context and 300 active generation seconds, giving maximum
aggregate reservations of **576,000 input / 192,000 output tokens and 7,200 active
seconds**. These are planning bounds, not an instruction to use that much output.
At the previously archived reference rates, the arithmetic token reservation is
**$0.40320**, within a proposed **$0.50 planning allowance**. This is not current
price verification, actual billing or a provider-enforced spend cap. None of
these proposed resources is approved yet.

Preparation must bind exact model metadata and runtime fingerprints and verify
the full harness offline. The latest verified baseline is Ollama **0.40.10**;
this audit did not recheck it. Later authorized preflight must stop on baseline
drift rather than silently refresh it. Preserve the established durable version
capture and terminal audit/export paths.

Proposed delivery sentinel: the first eight scheduled attempts cover one
historical and one fresh family in both orders and both repetitions. Stop if
none is valid, or if at least three responses share the same structural failure
signature spanning both families. Semantic failures remain measured outcomes;
they do not authorize resampling or an early claim of success.

Stop the whole run on non-200/transport failure, timeout/cancellation, truncation,
missing or irreconcilable usage, ceiling exhaustion, version/model drift,
request/source tampering or an incomplete durable capture. Preserve the complete
gateway chain and unknown usage where applicable. Every dispatched reservation
counts; an interrupted dispatch is not a free retry. There is no continuation
allowance without a separately frozen and approved policy.

Interpret the outcomes narrowly:

- Correct fixed-claim judgments with grounded reasons across fresh cases, both
  orders and repeats would support investigating task separation. They would not
  establish a reliable production verifier or explain the model's internals.
- Repeated acceptance of the same false premises would show that supplying the
  claim is insufficient in this setting. It would weaken the case for adding a
  same-model verifier at this stage, without proving a provider or model-wide cause.
- Frequent uncertainty, invalid output or rejection of supported controls would
  leave usefulness unresolved or demonstrate a new tradeoff. Report it without
  treating abstention or blanket skepticism as success.

No writer receives these judgments. No story is revised, no production gate
changes, and there is no provider comparison. Preserve the nine human ties and
the future division of work: machines prepare mechanics and grounded evidence;
humans judge feel/emotion, flow, character and story-breaking details on
sufficiently distinct stories. A later quality study must allow legitimate
creative change rather than reward minimal edits alone.

Next authorization, if desired, is **local preparation and freezing**, followed
by review of the concrete plan. Live execution would need separate explicit
approval of the frozen payload, destination and 24-call ceiling.
