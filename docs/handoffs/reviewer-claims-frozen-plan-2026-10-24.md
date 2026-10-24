# Frozen claim-verification diagnostic — 2026-10-24

Status: **PREPARED LOCALLY; AWAITING PLAN-BOUND LIVE APPROVAL**.
This freezes the [24-call proposal](reviewer-claim-verification-proposal-2026-10-24.md)
following the [reference and group-relation audit](reviewer-reference-relation-audit-2026-10-24.md).
Preparation makes **zero inference and zero daemon-discovery calls**.
Production prompts remain unchanged and the full workflow canary stays **ON HOLD**.

## Question and limits

Can DeepSeek distinguish supported from unsupported explanations when assessing
fixed claims against complete sources, separately from composing a full review?

This is a descriptive diagnostic with one task interface, not a candidate-versus-
D2 efficacy comparison. Historical scores are unchanged. The fixed claims and
compact response interface differ from a full comparative review; a successful
run would justify investigating task separation, not claim that it has already
improved production reviews, writing or reader experience. No writer receives
these judgments, and no production role or human checkpoint is added.

## Frozen cases, claims and schedule

| Family | Source status | Scene and contrast | Attempts |
| --- | --- | --- | ---: |
| H | Historical | Observatory: consultation-first violation versus a false contradiction about not having consulted | 4 |
| B | Historical | Coat workshop: before explaining versus an invented before-deciding condition | 4 |
| G | Historical | Ferry terminal: original/revision action ownership, with qualified continuity criticism | 4 |
| K | Fresh | Concert hall: approval-before-pit-descent violation versus approval-status consistency | 4 |
| L | Fresh | Pottery workshop: a desired explanation versus a claimed prohibition on earlier action | 4 |
| M | Fresh | Railway shed: a replaced cabinet action versus an invented retrieval within the revision | 4 |

The three historical packets and nine historical claim texts are unchanged from
the preceding sealed audit. The three fresh scenes and nine fresh claims were
authored locally before inference. Each version is **224–294 words** across this
matrix. The private casebook includes complete sources, exact claims, expected
judgments, rationales and version/offset-bound evidence.

There are **18 distinct claims**, three per family. They include **ten supported
and eight unsupported** judgments; the per-family mix and claim positions vary.
Qualified voice, urgency, naturalness and continuity readings remain supported
controls. Their gold means a defensible reading grounded in the text, not the
uniquely correct emotional response or a gold literary winner. A mixed claim
with an unsupported factual premise is unsupported as a whole, even when other
parts are correct. No ambiguous authored claim is assigned an uncertainty gold.

Each family runs in original/revision and revision/original source order, with
**two exact repetitions** of each request: **6 × 2 × 2 = 24 attempts**. This yields
72 returned claim judgments if completed, not 72 independent examples. The
expected-label denominators are 40 supported and 32 unsupported judgments. Claim
positions stay fixed across source orders and repeats; claim-order sensitivity
is not measured. Exact repeats measure observed repeatability, not guaranteed
determinism.

The schedule interleaves H/K for the first eight calls, then B/L, then G/M. Within
each pair it alternates family order across the two source orders and repeats.
All 24 request files and wire payloads are frozen. The twelve repeat pairs have
identical model-facing wire payloads; execution IDs distinguish their records.

Private local inputs, ignored by Git:

- [Casebook with full prose and withheld gold](../../data/diagnostics/reviewer-claims-v61-2026-10-24/casebook.md)
- [Exact claims](../../data/diagnostics/reviewer-claims-v61-2026-10-24/claims.json)
  and [source-bound cases](../../data/diagnostics/reviewer-claims-v61-2026-10-24/cases.json)
- [Schedule](../../data/diagnostics/reviewer-claims-v61-2026-10-24/schedule.json),
  [prepared requests](../../data/diagnostics/reviewer-claims-v61-2026-10-24/prepared/)
  and [wire payloads](../../data/diagnostics/reviewer-claims-v61-2026-10-24/wire-requests.json)

## Request interface and settings

Model: **`deepseek-v4.1-flash:cloud`**, through
**`http://127.0.0.1:11434` to Ollama Cloud**. Selected digest:
`e04da138d31e0c9468e982e1ae9503d06cb7e170caa16a90c17d931c4aa140f8`.

The baseline is the last verified **Ollama 0.40.10** snapshot. Preparation does
not claim to have discovered the current daemon. Authorized live preflight must
match the pinned version, selected-model digest, capabilities and thinking
metadata; drift stops the run without silently amending the plan. Provider
investigation remains deferred at the user's request.

Settings remain temperature **0.2**, top-p **0.95**, seed **20261022**, thinking
**false**, nonstreaming, context **32,000** and maximum output **8,000** tokens.
There is no warm-up, feedback, resampling or automatic repair. The new prompt is
private diagnostic material; no production prompt is edited.

Each request includes complete context and assignment, both complete prose
versions with their catalogs, the unchanged mechanical appendix, three claims
and the compact output contract. Expected labels, claim provenance, prior
adjudication notes and selected gold evidence are withheld. No answer distribution
is disclosed to the model. Source text and supplied claims are data to examine,
not instructions to execute.

Output contains exactly three claim records in input order: claim ID,
`supported` / `unsupported` / `uncertain`, evidence refs and a nonblank reason
of at most 2,000 characters. Strict parsing rejects duplicate keys, extra fields,
missing/reordered/duplicate claims and invalid types. Evidence permits at most
eight distinct refs from this packet. Supported/unsupported judgments need at
least one ref; uncertain may use an empty list with a reason. The application
binds quotes to exact source versions and offsets. No array is trimmed and no
answer is repaired. The proposed catalog enum is **not** added, and the wire has
no `format` parameter. Membership alone still does not prove a claim or reason.

## Frozen scoring and inspection

The [scoring contract](../../data/diagnostics/reviewer-claims-v61-2026-10-24/scoring.json)
has no production advancement threshold. Report:

1. Complete valid deliveries per attempted call.
2. Correct fixed-claim labels per attempted claim judgment. An `uncertain`
   answer against definite gold is an abstention, not a recovery. Report false
   rejection of supported controls and acceptance of unsupported premises
   separately, with their corresponding denominators.
3. Grounding of the **entire reason** and whether the cited evidence supports
   that reason/judgment. A correct label with a false explanation or irrelevant
   citations is not a usable claim.
4. Whole-request usability: valid delivery and all three claims correct with
   grounded reasons and evidence.
5. Results by family, historical/fresh origin, source order and repeat, including
   disagreement between repeats and false premises accepted in both orders and
   both repetitions.

An invalid completed delivery contributes three failed claim judgments. A
dispatched terminal failure also stays in the attempted denominator with three
failed judgments; unknown usage remains unknown. Unstarted calls are reported
separately and are not called model failures. Budget reservations are separately
counted, including any reservation that stopped before dispatch.

Export shuffles answers and hides trial, order and repeat IDs. Complete sources
and claims remain available to the inspector; recognizable families and wording
limit masking. Inspect every returned reason and cited evidence, preserve
unsupported versus uncertain judgments, and bind exact reason text, source
hashes, versions, offsets and quotes. Seal the notes before decoding the key.
This is assistant source inspection, not a new blind human preference result.
Invalid captures remain available for separate diagnosis without repair.

Completion returns `complete_descriptive_only`; any short run returns
`incomplete_no_conclusion`. Neither authorizes production or writer dispatch.
A useful pattern would support designing a later paired full-review experiment.
Persistent false-premise acceptance, uncertainty or rejection of supported
criticism will be recorded without redefining success after the fact.

## Budget and stops

| Resource | Per call | Whole run |
| --- | ---: | ---: |
| Attempts | 1, no retry | **24 maximum** |
| Input tokens | 24,000 | 576,000 |
| Output tokens | 8,000 | 192,000 |
| Active generation seconds | 300 | 7,200 |
| Archived-rate token reservation | $0.01680 | $0.40320 |

Planning allowance: **$0.50**. These arithmetic figures use the previously
archived $0.30/M input and $1.20/M output rates, without discounts. They are not
current price verification, actual billing or a provider-enforced spending cap.
Metadata/verification time is separate from active generation time. Prompt-size
estimates are **3,500–4,443 tokens by UTF-8 bytes divided by four**, not tokenizer
measurements; actual usage is checked after every call.

The first-eight delivery sentinel covers H and K in both orders and repeats.
Stop if zero answers are valid, or if at least three answers share a structural
failure signature spanning both families. Semantic mistakes are measured
outcomes; they do not trigger resampling or a success stop.

Stop the whole run on non-200/transport error, timeout/cancellation, truncation
or another non-stop finish, missing/invalid/excess usage, unexpected thinking,
version/model drift, budget exhaustion, source/request tampering or an incomplete
durable capture. The runner reserves each attempt before dispatch and preserves
exact requests, raw responses, usage, version observations and validation results.
The version response is durably captured before validation at initial preflight
and before/after each generation. Terminal audit/export preserves the gateway
error chain and unknown usage.

There are **zero retries and no terminal continuation allowance**. A clean stop
between completed cells may resume only the untouched remainder of the same
24-cell ledger. Missing captures, a terminal marker or a stopped sentinel cannot
be bypassed by restarting. No other run's unused allowance is transferred here.

## Verification and authorization boundary

**125 offline tests pass; Ruff lint/format and strict mypy pass on seven private
scripts.** The private harness tests all exact requests through the
production Ollama adapter using an in-memory transport, restart/ceilings,
sentinels, terminal export, version capture, structured-output rejection,
source/oracle binding, masking and descriptive scoring. Real HTTP is blocked in
tests. Static lint, formatting, strict typing and focused test results are kept
in the [verification record](../../data/diagnostics/reviewer-claims-v61-2026-10-24/verification-final.json).
No frontend, API, worker or production prompt code changes, so unrelated
application builds are not rerun.

The restricted Windows process reproduced the previously documented asyncio
socket-pair stall before the first mocked run created its ledger. A five-second
empty-event-loop reproducer isolated that environment failure. The completed
tests ran outside that restriction with real HTTP still blocked. Initial static
format/type adjustments and the restricted-run evidence are retained; they do
not represent model calls or provider findings.

The [plan seal](../../data/diagnostics/reviewer-claims-v61-2026-10-24/plan.json)
binds the public plan, private scripts/fixtures/requests and **733 historical
source fingerprints**, including the prior audit seal. It retains all original
results and issue bodies. The tracker and issue index are updated under a
separate documentation closure to avoid a hash cycle.

No live approval file or live-run directory exists at preparation closure.
Further approval must bind this plan hash, the **24-attempt ceiling**, full
unpublished prose/context/claims, and **Ollama Cloud through the local daemon**.
The runner rejects an earlier comparison's approval. Preparation itself grants
no inference authorization.

Production stays **prompt 61 / graph 9 / fulfillment policy 1**. Preserve the
**nine prior human ties** and future story-quality focus on feel/emotion, flow,
character and story-breaking details; mechanical evidence is prepared by machines.
Minimal edits and report usability are not measures of reader preference.
**Step 19 IN PROGRESS; Step 20 NOT STARTED; live calls PAUSED; canary ON HOLD.**
