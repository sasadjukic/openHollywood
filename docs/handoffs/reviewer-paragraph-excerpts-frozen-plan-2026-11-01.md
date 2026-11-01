# Frozen MA/PE paragraph-excerpt comparison — 2026-11-01

**Prepared locally; awaiting separate live approval. 0/16 inference calls used.**
Production remains **prompt61 / graph9 / fulfillment policy1**. Live inference
is **PAUSED**, and the full workflow canary remains **ON HOLD**.

This implements the [citation-mapping audit's proposal](reviewer-citation-mapping-audit-2026-11-01.md).
That audit found no application reference-map error, but seven correct-label
citation gaps and four separate semantic failures. The question here is narrow:
does putting exact paragraph text beside each prose reference improve citation
placement while preserving assessment scope and semantic accuracy?

## Frozen arms and allocation

| Arm | Treatment | Calls |
| --- | --- | ---: |
| MA | Existing full-context selected-premise assessment | 8 |
| PE | MA plus `exact_paragraph_text` on every `/prose` registry entry | 8 |

**Four families × two presentation orders × two arms = sixteen calls maximum.**
PC presents prose before context; CP reverses those source messages. Case and
artifact identities do not change. Each pair has identical selected propositions,
complete sources/report/fields, system instructions, response contract, sampling
and limits. All paragraphs receive the PE treatment, including short standalone
paragraphs and paragraphs irrelevant to a particular claim. No gold witnesses,
relevance labels, source filtering, semantic hints or model quote-copying task
are added. Production prompts are not edited.

The only wire change in PE is the exact-text field inside the existing registry
message. Removing those fields restores the paired MA wire exactly. The four
historical MA controls match their archived wire payloads exactly. PE retains
the original complete source artifacts as well as the added excerpts; extra
input and duplication are part of the intervention, not a token-neutral contrast.

## Frozen cases and selected propositions

| Family | Source and purpose | Draft words / paragraphs | References | Units per order, per arm |
| --- | --- | ---: | ---: | ---: |
| H1, Elena | Unchanged handwriting/date case; short realization, decision/match citations and unsupported specific-flourish inference | 478 / 11 | 312 | 7 |
| H2, Elara | Unchanged contact/pull and preparation/entry case; unsupported starting-inside inference | 729 / 13 | 342 | 5 |
| C5, The Silent Casting | Fresh harbor foundry; split contact/vibration, seven-day realization, actual private-gauge verification and explicit next-scene start after entry | 800 / 13 | 223 | 8 |
| D6, The Tide Catalogue | Fresh seed house; split contact/vibration, nine-day realization, general weight comparison without private watermark verification, next-scene summary includes entry | 753 / 14 | 224 | 8 |

Both fresh families include adjacent preparation and crossing, an independently
valid outside-at-end violation, a quoted intention attributed to someone else
and explicitly rejected by the protagonist, and an unavailable annex whose
contents remain uncertain. Their full packets include an eight-scene blueprint,
characters, locations, current assignment and source-scope declarations. They
are long-context diagnostic fiction, not production canon or human-quality evidence.
Their lengths are disclosed above; they are not exact length matches for H1/H2.

The historical selections are the actual saved SO selections assessed in VA/MA,
including partial-field selections and the overlapping H1 claims. PC/CP-specific
historical selections remain unchanged. Fresh selections are authored, eight
per report, and identical across both presentation orders. No selector is rerun.
This design tests assessment and citation presentation, not admission completeness.

Each arm has **56 fixed assessment slots**: 24 historical and 32 fresh. The frozen
labels are **38 supported / 14 unsupported / four uncertain per arm**. There are
**112 total judgments and 56 exact paired units**. Repeated orders are not
independent stories; the design has four family clusters. F2/F4 remain preserved
local positive regressions outside this live matrix.

The [private casebook](../../data/diagnostics/reviewer-paragraph-excerpts-v61-2026-11-01/casebook.md),
`cases.json`, `assessment-units.json` and `adequate-evidence.json` contain full
source/selection bindings, per-claim labels, rationales and evidence criteria.
Gold and inspection criteria are never included in requests.

The pair sequence is **H1/PC, H2/CP, H1/CP, H2/PC, C5/PC, D6/PC, C5/CP,
D6/CP**. The existing balanced arm-order pattern is retained: each arm goes first
in four pairs. The first eight calls cover the two historical sentinel families.
`schedule.json` fixes the exact sixteen-cell sequence; no output-dependent selection.

## Renderer and evidence criteria

An independent paragraph scanner verifies the original source version, field,
code-point range, exact text, source/field hashes and one-based nonempty paragraph
mapping. PE copies the verified paragraph bytes as decoded text, without trimming,
normalizing Unicode or changing punctuation. The registry retains version and
field identity. A separate diagnostic-view version binds the added presentation.

| Family | Added UTF-8 bytes per PE request | Maximum PE input estimate, bytes/4 |
| --- | ---: | ---: |
| H1 | 3,071 | 15,189 |
| H2 | 4,565 | 16,295 |
| C5 | 4,931 | 10,977 |
| D6 | 4,667 | 10,861 |

The largest exact wire is **65,177 UTF-8 bytes**. The stricter bytes/3 estimate
is **21,726**, below the 24,000 input reservation. These estimates are not model
tokenization measurements or guarantees. Actual reported usage must satisfy the
limits; a violation stops the run. Added input, generation and latency are measured.

Adequate evidence is judged by **content coverage**, not an exact reference
whitelist. Illustrative references remain available to the inspector. Examples:

- Dates and an explicit realization require evidence for all three components.
- Contact plus a persistent sensation requires both components; an obligation
  or later entry cannot substitute for either event.
- A selected decision explanation requires its reasoning/preparation; entry
  alone does not establish that particular explanation.
- A claimed violation requires the observed event and its governing obligation.
- General similarity does not establish a specified private verification test.
  Interior location alone does not establish a scene starting after entry.
- Correct attribution and negation matter. An unavailable source is not silently
  treated as a complete source whose silence refutes a claim.

Extra irrelevant references alone do not fail a judgment if adequate evidence
remains. Literal plan wording is unnecessary for an expressed decision. Located
text does not automatically establish entailment. Correct selected components
do not automatically establish their whole relation.

The unchanged output boundary rejects duplicate keys, unknown fields/references,
duplicate references or selections, missing/extra admitted propositions, changed
quotes and length violations. Each reason is 1–1,200 characters, combined reasons
at most 8,000; exact selected quotes are 1–2,400 characters. No structural repair,
quote replacement, salvaged-claim credit or writer instructions are permitted.

## Frozen scoring and interpretation

Every completed valid judgment receives source-bound inspection on separate axes:
label accuracy, faithful selected meaning, substantive explanation grounding,
citation adequacy, material error and opinion factualization. All axes are retained
even when the combined grounded judgment fails. Invalid/unstarted units remain in
the fixed denominators. The application checks structure and bindings; it does not
automatically judge semantic support.

The two historical contextual flags, H1/CP and H2/CP, are inspected for each arm:
**four flags total**. Whole-relation credit requires an explicit explanation with
adequate evidence, not aggregation of supported components. Fresh violation claims
are assessed as complete selected propositions within their regular eight units.

The seven historical citation targets are H1/CP **Q002/Q003/Q005/Q006**,
H2/CP **Q004**, and H2/PC **Q001/Q002**. A paired recovery counts only when the
new MA response is semantically correct but inadequately cited and PE grounds
the identical unit. Recovery in both arms does not count as treatment evidence;
a corrected semantic error is not counted as a citation-only recovery.

**Promising citation-presentation evidence requires all of the following:**

1. All sixteen outputs structurally valid and all 56 pairs evaluable.
2. At least two of the seven historical targets reproduce a citation-only failure
   in the new MA control, and at least two receive paired grounded PE recoveries.
3. Zero MA-to-PE grounded or semantic pass-to-fail losses, and zero losses of a
   grounded contextual-relation explanation.
4. PE preserves all **13 historically grounded H units** and all **20 historically
   semantically correct H units**, including the seven former citation-only gaps.
   A shared new failure in both arms cannot evade this protection.
5. All **32 fresh PE units** are grounded, including the positive/negative semantic
   contrasts, attribution and unavailable-source controls.

If validity or preservation/fresh-case criteria fail, the gate is not met. If
those criteria pass but fewer than two control citation failures reproduce,
the citation hypothesis is **inconclusive**. Otherwise fewer than two recoveries
also fails the gate. These rules are fixed before inference and implemented in
the scorer. The earlier four semantic failures may remain failures; every such
failure is still reported, and `all_PE_units_grounded` is reported separately.
Promising citation presentation does not qualify the reviewer-to-writer route.

Inspection exports shuffle reports, withhold arm/resource data and the decode key,
exclude thinking from semantic evidence, and seal annotations before decoding.
This is partial assistant masking, not blind human review: familiar cases and
selections can reveal provenance. Every reason is inspected, including successful
labels and incidental factual assertions.

Report input tokens, combined generated tokens, known timing and paired ratios.
Aggregate paired ratios require all eight valid pairs. There is **no efficiency
promotion threshold**. No reasoning/final split is invented; actual billing remains
unknown unless supplied. Historical selection calls are not new calls, and authored
fresh selections do not establish end-to-end savings.

## Budget, metadata and destination

| Limit | Frozen value |
| --- | --- |
| Model | `deepseek-v4.1-flash:cloud` |
| Daemon baseline | **Ollama 0.40.13**, captured locally during preparation |
| Attempts | **16 new total, eight per arm, one per cell** |
| Retries / repairs / extra judges / warm-ups | **0** |
| Input / combined generated / context per call | **24,000 / 16,000 / 40,000 tokens** |
| Active time per call | **600 seconds** |
| Aggregate input / generated / active reservations | **384,000 / 256,000 / 9,600 seconds** |
| Thinking / sampling | `high`; temperature 0.2, top-p 0.95, seed 20261022 |
| Streaming / provider format enforcement | false / none |
| Archived-rate reference reservation / planning allowance | **$0.42240 / $0.50** |

The dollar figures use archived $0.30 input / $1.20 output per million tokens,
without discounts. They are planning references, not current-price verification,
actual billing or an enforceable billed-cost cap. Thinking and final generation
share the single 16,000-token output allowance.

The model digest remains
`e04da138d31e0c9468e982e1ae9503d06cb7e170caa16a90c17d931c4aa140f8`.
Three successful metadata responses—version, tags and show—match the prior model
snapshot and support `high` thinking. The first sandboxed loopback attempt was
denied locally; that failed capture and the successful retry are retained. No
inference or story payload was sent during metadata discovery.

Approved execution would send **full unpublished prose, blueprint/context,
critique, selected propositions and the PE paragraph view to Ollama Cloud through
the local Ollama daemon**. Approval must bind the frozen plan hash, payload,
destination and sixteen-call ceiling. No earlier unused allowance is reused.

## Stops and replay

- A trustworthy HTTP-200 `length` finish immediately retires the affected arm,
  including empty final text with verified usage. Preserve raw counters, gateway
  error chain and version evidence; grant no usable-output credit.
- After an arm's four historical H1/H2 attempts, retire it for zero valid outputs
  or the same blocking validation signature in both historical families.
- Non-200/transport, unknown or conflicting usage, excessive resources, missing
  thinking, invalid timing, metadata drift, tampering, ambiguous dispatch,
  cancellation or an unexpected gateway failure cause a **global terminal stop**.
- No global-stop resumption, semantic early stop, retries, replacements or
  reallocation. Clean pauses at sealed cell boundaries may resume only the exact
  remaining schedule. Used reservations are never released.

Preflight and per-call checks must match the frozen daemon/model metadata.
Version observations are saved before validation, including non-200 evidence.
Raw captures and the supported terminal audit/export preserve unknown usage.
Ledger replay, operator locking and sealed stop decisions prevent repeat dispatch.

## Local verification and freeze

Bundle: `data/diagnostics/reviewer-paragraph-excerpts-v61-2026-11-01/`.
It contains cases, source/version bindings, exact selections and judgments,
adequate-evidence criteria, sixteen prepared/wire requests, response schemas,
renderer checks, scoring, budget/stops, metadata, tests and inspection tools.
`plan.json` seals the public plan, these assets, runtime sources and verification.

Verification covers exact historical controls, reversible PE additions, source
and paragraph parity, no gold leakage, full schedules/restarts, structured-output
failures, terminal usage, metadata failures, tampering, masked export/sealing and
scoring. The local audit and original VA/MA results are replayed unchanged. No
live approval file or live-run directory exists during preparation.

The initial sandboxed asynchronous test stalled before its first mocked call
completed and was interrupted. The retained preparation record also lists its
lint/type findings. The successful verification uses only in-memory provider
responses, with real HTTP transports and database access blocked. A subsequent
local scoring amendment explicitly protects all twenty historical semantic
successes, preventing shared new failures from hiding behind citation gains.
It changes no cases, requests, limits or production prompts.

**284 offline tests pass:** 104 comparison tests, 22 gateway/contract tests,
74 citation-mapping regressions and 84 delivery/usage regressions. Ruff lint/format
and strict mypy pass on eleven local scripts. Historical VA/MA result replay also
passes unchanged. Final checks and the freeze fingerprint are recorded in
`verification-final.json`, the preparation closure and the authoritative tracker.
The bundle binds **1,751
historical/runtime source fingerprints**; all fourteen issue bodies and posted
links remain preserved.

```powershell
$env:PYTHONPATH = 'engine;apps/api;apps/worker'
.venv/Scripts/python.exe -X utf8 data/diagnostics/reviewer-paragraph-excerpts-v61-2026-11-01/freeze.py verify
```

Human literary review remains focused on feel, flow, character and story-breaking
details. Mechanical evidence belongs in the prepared appendix. Neither citation
accuracy nor factual support establishes edit necessity, prose preservation or
story quality. No writer, canonical artifact, production graph/schema or mandatory
Blueprint checkpoint changes. No issue is closed or edited externally.
**Step 19 IN PROGRESS; Step 20 NOT STARTED; inference PAUSED pending approval;
full workflow canary ON HOLD.**
