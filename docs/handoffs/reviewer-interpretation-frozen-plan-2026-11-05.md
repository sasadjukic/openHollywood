# Sol-high interpretation diagnostic — frozen plan

Date: 2026-11-05. **Local preparation; live execution requires separate approval.**
Production prompts, model profiles, routing and writer behavior remain unchanged.
Step 19 remains IN PROGRESS; Step 20 remains NOT STARTED; canary ON HOLD.

## Question and scope

Does separating a factual claim about a **depicted specific procedure** from a
mixed claim about **spending a future dramatic payoff** resolve Sol's assessment
disagreement while preserving its judgments on surrounding facts?

The [model-scope audit](reviewer-model-scope-audit-2026-11-05.md) found that Sol
and Astra explicitly read H1's mixed allegation as an editorial judgment while
locating adequate source evidence. Their original specific-event scores remain
failures under that frozen factual contract. Terra distinguished the specific
event correctly; its saved responses remain a historical contrast, not an arm
here. This test uses Sol because it reproduced the interpretation in both orders,
not because this preparation establishes that Sol is the best production model.

The two formulations are **different propositions**, not a same-claim citation
recovery. No output will prove that a scene feels better or that a rewrite is
necessary. A plausible editorial concern is not automatically a factual error,
and correct event verification does not settle a concern about dramatic effect.

## Frozen design

**4 complete families × 2 target formulations × 2 source orders = 16 attempts.**
One model: **`gpt-6.1-sol`, reasoning `high`**, unchanged U section-locator contract.
Each request assesses seven fixed, complete selected propositions in its full
report and primary-source context. There are **112 claim slots: 16 target slots
and 96 surrounding-control slots**, plus two H1-CP contextual relation inspections.

| Family | Full scene situation | Specific procedure in current draft | Explicit-event gold |
| --- | --- | --- | --- |
| H1 | Historical Elena card, journal and handwriting scene | General match; private flourish verification is not depicted | Unsupported, absence of depiction |
| I1 | Mara challenges musical attribution during a rehearsal | Reel played at half speed; four taps counted; doubled fourth recognized, through paraphrase | Supported |
| I2 | Nadi challenges a missing village account at a public hearing | Ledger identified from its number and repaired cover; private subtraction check is not depicted | Unsupported, absence of depiction |
| I3 | Suri hears a recording during a call after family estrangement | Familiar voice recognized; later private exchange is explicitly left unheard and unchecked | Unsupported, explicit nonperformance |

I1–I3 are newly authored complete local scene families. They vary narrative purpose,
structure, point of view and relationships, rather than merely replacing names and
props. They are controlled diagnostic fiction, not approved canonical story material
or a representative sample of all future stories.

- **M — mixed:** a claim that general identification consumes the specifically
  named future turning point. H1 keeps the original wording and original factual
  gold. Fresh mixed targets retain the named-procedure factual criterion separately
  from any editorial reading; reader effect has no factual gold.
- **E — explicit event:** a claim that the current draft depicts the specified
  private procedure. H1 says: “The current draft depicts Elena verifying an
  idiosyncratic flourish only she knows, the specific procedure named in Scene 2's
  turning point.” Fresh targets specify the procedure's concrete operations.
- **PC / CP:** prose before surrounding context / surrounding context before prose.
  Full documents and report stay available in both. These are presentation controls,
  not independent story samples.

The fresh surrounding claims cover current assignment authority, a fulfilled
investigative decision falsely alleged absent, observed identification, a genuine
endpoint breach, misattributed accusation/belief, and an unavailable continuation.
H1 retains its existing six controls for each order, including the independent
no-match endpoint breach and the fulfilled decision. Historical PC and CP have
different selected control sets; that existing difference is retained, not hidden.

## What changes and what stays fixed

Within every M/E pair, the audit verifies identical primary sources and versions,
source order, registry, system instructions, response schema, model, settings and
surrounding claims. Only the target report field and its admitted quotation change
in the actual generation/count bodies. Report, selection, case, context, work and
request fingerprints change accordingly and are explicitly recorded.

The two H1 M generation/count JSON bodies are byte-identical under the frozen
canonical serialization to the saved Sol controls; their work fingerprints also
match. Their new scheduling/envelope IDs are local bookkeeping. No prior receipt
is presented as a new result. Source/field coupling, workload narrowing, excerpt
replacement and new receipt aliases are not treatments in this comparison.

The renderer remains read-only: a unique exact source-version/field quotation
locates **one whole registry field or one prose paragraph**. It does not certify
support. Neighboring uncited sections do not count as cited evidence. Full source
context remains available for interpretation, including inspection for absence.
No locator repair, semantic normalization or automatic writer dispatch is added.

## Fixed execution order

Run once, serially, in the following pair order. The first formulation alternates;
each family has M first in one presentation and E first in the other.

| Attempts | Family/order | Formulations |
| --- | --- | --- |
| 1–2 | I2-PC | M, E |
| 3–4 | H1-CP | E, M |
| 5–6 | I1-CP | M, E |
| 7–8 | I3-PC | E, M |
| 9–10 | H1-PC | M, E |
| 11–12 | I2-CP | E, M |
| 13–14 | I3-CP | M, E |
| 15–16 | I1-PC | E, M |

No smoke generation, retries, fallback model, adaptive replacement or extra repeat.
The experiment is descriptive and bounded; it does not estimate a population effect
or isolate backend nondeterminism. Published alias identity does not reveal the
provider's internal backend fingerprint.

## Adapter, destinations and budget

Preparation exercises the application's actual `OpenAIGateway` through mocked HTTP,
using a diagnostic-only explicit Sol specification. The wire requests high reasoning,
strict structured output, `max_output_tokens=32000`, `service_tier=default`, and
disabled truncation, storage, background execution and streaming. Portable temperature,
top-p and seed settings are omitted by this adapter; they are not effective controls.
No tools, previous-response state or production model-profile changes are requested.

The [official Sol documentation](https://developers.openai.com/api/docs/models/gpt-6.1-sol)
was searched and opened on 2026-11-05. It documents high reasoning, Responses,
structured output, a 1,050,000-token context and 128,000 maximum output tokens.
Published standard rates remain $2 input and $10 output per million tokens, with
$2.50 cache writes. The prior restricted diagnostic specification is retained after
that review; its 24,000-input/32,000-output limits are experiment limits.

**No provider catalog, input-count or generation request was made during preparation.**
Current account access and server acceptance therefore remain unverified. After
approval, catalog availability is checked once before each fixed attempt, and exact
response model identity is enforced. A failed check terminates the comparison.

| Resource | Per attempt | Maximum for this comparison |
| --- | --- | --- |
| Generation attempts | 1 | **16** |
| Story-bearing input-count requests | At most 1 | **16** |
| Non-generating catalog reads | At most 1 | **16** |
| Input tokens | 24,000 | 384,000 reserved generation-input tokens |
| Generated tokens, including reasoning | 32,000 | 512,000 |
| Active count/generation time | 600 seconds | 9,600 seconds / 160 minutes |
| Catalog timeout | 25 seconds | Up to 400 additional seconds |
| Conservative published-rate reference | $0.38 | **$6.08** |
| Planning allowance | $0.60 | **$9.60** |

The reference uses the $2.50 input/cache-write bound without cached-input discounts;
reasoning is included in generated tokens, not charged a second time. Actual billed
cost remains unknown. These are reservations, not predicted latency or a billing
guarantee. Local verification, logging and integrity checks add elapsed time.

There can be at most **32 story-bearing POST requests**, because each generation has
one separate count request. Full unpublished prose, plans, context, report and selected
claims go to both:

- `https://api.openai.com/v1/responses/input_tokens`
- `https://api.openai.com/v1/responses`

Catalog reads use `https://api.openai.com/v1/models` without story content. The existing
key-reuse authorization persists; no key is printed, copied into artifacts or changed.
New live transmission still requires approval of this frozen plan and both endpoints.

## Scoring and inspection

Every fixed slot remains in the denominator, including failed or unattempted slots.
The inspector must bind observations to sealed request/receipt/assessment hashes,
then review complete primary sources. No model grader or hidden reasoning is used.

Inspect independently:

1. Complete valid delivery and exact claim identity.
2. Explicit event truth or the original mixed factual-contract judgment, retaining
   the distinction between absence of depiction, explicit nonperformance and missing
   source scope.
3. Target interpretation expressed in the final reason: specific event, editorial
   effect, both, or unclear. A mixed editorial reading does not retroactively change
   the original H1 gold.
4. Exact witness location and adequate coverage of all material factual premises in
   the claim and reason. Frozen example references are sufficient examples, not an
   exhaustive whitelist. A negative depiction claim does not need an invented denial
   sentence, but does require full-draft inspection and cited relevant contrasts.
5. Unsupported factual or editorial premises in the explanation. Actual reader
   effect, edit necessity and story quality remain unassessed.

Classify each slot as grounded, citation-only failure, semantic failure, or unavailable.
H1-CP's T2 whole-field endpoint relation has its own inspection in each formulation;
two supported component labels alone do not establish that relation.

The bounded screen requires **all 16 valid deliveries**, all eight explicit target
slots grounded without unsupported editorial premises, all 48 explicit-arm controls
grounded with no losses against the paired mixed controls, and adequate explicit-arm
H1-CP endpoint-relation coverage. No average can conceal a lost control.

Both H1 mixed controls must also reproduce the prior supported/editorial reading with
adequate located evidence before describing a demonstrated interpretation contrast.
If they do not, favorable explicit results establish feasibility only. Even a favorable
result is not a same-claim recovery, causal proof, production promotion or evidence of
better stories. If explicit wording still fails with adequate evidence, require a
materially new hypothesis before more inference; do not continue synonymous rewrites.

## Terminal stops

Stop the entire comparison at the first terminal delivery, resource, identity or
preflight failure: drift in frozen sources/requests/runtime/specs; missing/mismatched
approval; unavailable/wrong model; auth/quota/count errors; count over 24,000; empty
final; malformed/duplicate-key JSON; missing/extra/changed claims; invalid evidence
shape; refusal; truncation; transport/cancellation/time failure; unknown or inconsistent
reported usage; input/output cap breach; or secret-boundary failure.

A count failure consumes its reserved attempt. Interrupted dispatch reservations
remain consumed, with unknown usage preserved. Catalog interruption is terminal,
without another preflight. No terminal resume, allowance transfer or replacement.
A validly shaped but unresolved quotation is a recorded binding outcome, not a reason
to repair output or retry. Semantic disagreement does not trigger adaptive early
stopping: complete the remaining frozen schedule unless a terminal stop applies.

## Artifacts and verification

Private, ignored bundle:
`data/diagnostics/reviewer-interpretation-v61-2026-11-05/`.

`cases-and-scoring.md` provides the complete local source packets and frozen judgments.
`requests.json` has both exact endpoint bodies; `works.json` binds full context and
active statements. `gold.json`, `scoring.json`, `inspection-template.json` and
`relation-inspection-template.json` freeze the evaluation. Budget, stops, model specs,
schedule, source pins, history, local tests and read-only renderer examples are included.
`plan.json` is the approval-bound manifest. Public documentation contains no API keys
or full unpublished source packets.

**294 offline tests pass**: 132 diagnostic tests, 123 tracked assessment tests and
39 provider/routing/execution tests. Repository Ruff, formatting and strict mypy pass
for 224 files; the same checks pass for all 14 private scripts. Deterministic
preparation, fixed-slot generation and the paired-input audit reproduce their outputs.
Mock tests exercise all 16 adapter wires, native schema, count-before-generation,
terminal stops, unknown usage, cancellation, the attempt ceiling, approval/runtime
guards, exact binding, literal rendering and scoring without inferred edit authority.

The first unfrozen build is retained locally with hashes. Preparation corrected the
historical H1 inventory's selective field IDs and normalized schema property ordering
before native serialization. A ported test's report mutation was adjusted for the
fresh report shape. The final suite includes that test; nothing is deselected.

The freeze binds **70 files and 4,929 source fingerprints**. Plan SHA-256:
`de3c4e83943b40bcff58481581e0d3cd1fabc7ca411bf495051423e834e3c5f0`.

No frontend or runtime application change is included; frontend build/testing is not
applicable. The complete repository test suite is not claimed as rerun.

After approval, execute the frozen schedule once, inspect every fixed slot and both
relations, document latency/token/reference-cost observations and update the tracker.
Keep future human review focused on feel, flow, character and story-breaking details,
using machine-prepared factual evidence. No new routine human checkpoint is introduced.
