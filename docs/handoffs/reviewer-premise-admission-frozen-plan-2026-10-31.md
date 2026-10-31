# Frozen CW-013 premise-admission diagnostic

Date: **2026-10-31**. **FROZEN AND VERIFIED — 0/24 inference calls used; separate live approval required.**
Production **prompt 61 / graph 9 / fulfillment policy 1** unchanged. Canary **ON HOLD**.

This prepares the [24-call proposal](cw013-admission-preparation-2026-10-31.md).
The question is whether identifying consequential allegations in an ordinary
critic report introduces failures distinct from judging already selected claims.
It is a diagnostic of an upstream dependency, not a new writer intervention or
a production semantic extractor.

## Conditions and exact contrast

**Six families × two conditions × two source orders = 24 calls**, twelve per
condition. One observation per cell, **zero retries, replacements, correction
calls, extra probes or reallocation**.

| Condition | Reviewer task | Calls |
| --- | --- | ---: |
| **SA — self-admission** | Select distinct consequential factual premises from the complete report, then assess their source support | 12 |
| **VA — supplied verbatim admission** | Assess independently selected exact report spans supplied by the application | 12 |

Both receive the same complete source packet, full report, report-field index,
source-reference index, semantic instructions, response contract and sampling.
VA adds exactly one `admitted_spans` message containing field IDs and quotations.
Removing that message reproduces the paired SA wire request. No labels, gold
rationales, protected-target flags or expected source references enter either
request. VA's selection is authored assistance and receives **no model selection
credit**. It cannot qualify automatic admission even if its judgments are perfect.

The historical reports and input artifact contents are unchanged. These are new
requests for a new task, **not byte-identical historical reviewer wire controls**.
The new diagnostic prompt has its own identity, `diagnostic-premise-admission-v1`;
production prompts are untouched. No PO identity/opposition/time map is imposed
on arbitrary claims.

The new reviewer receives full locally saved input bodies, which can exceed the
historical critic's rendered view. That access is not attributed backward to the
critic. The original export retains the actual views and their hashes. The report
under assessment is raw model output; application-added audit advice is not
relabeled as model-authored prose.

The two orders are **PC** (draft prose before assignment/context) and **CP**
(assignment/context before draft prose). The report follows both source blocks.
These are source-presentation controls, not original/revision comparisons or
independent new stories. Arms stay adjacent; there are six SA-first and six
VA-first pairs, and each family's second presentation reverses arm order.

## Cases and authored targets

Each case has **three frozen primary target propositions**. Repeated wording of
one premise in the summary, issue and assessment is not three independent targets.
SA may select any report occurrence that preserves the complete proposition;
coverage of an alternative occurrence requires explicit source inspection.
Additional returned allegations are inspected, not silently discarded because
they are outside the primary target set.

| Family | Source/report origin | Primary distinction and protected criticism |
| --- | --- | --- |
| **H1 — Elena's handwriting match** | Exact October 16 Gemma report `s19103-elena-embedded-initial` and complete saved inputs | The missing-decision premise is unsupported; the independently valid no-match boundary and ten-year realization findings must survive |
| **H2 — Elara's entry** | Exact October 16 Gemma report `s19101-elara-separate-initial` and complete saved inputs | All three selected grounds are supported: actual entry violates the boundary, while the decision and touch/pull events occurred |
| **F1 — watchmaker's recorder** | Fresh authored scene and report | Deciding to compare a ledger does not establish accepting forgery; tearing the paper seal is a real boundary violation; the check decision is fulfilled |
| **F2 — atlas-room letter** | Fresh authored scene and report | A deceased namesake's quoted burn plan does not belong to the protagonist; opening the box violates its independent boundary; seeking help is fulfilled |
| **F3 — bell yard** | Fresh authored scene and report | A conditional promise is not an observed ringing; the warning bell explicitly stays silent; crossing the white line is a real violation and the inspection decision is fulfilled |
| **F4 — station register** | Fresh authored scene and report, with an explicitly unavailable Appendix B | A universal claim about the missing appendix remains uncertain; opening the envelope before the officer arrives is a real assignment violation; completing the request expresses the decision to obtain the appendix |

H1/H2 are synthetic, unapproved diagnostic captures, not durable production runs
or new DeepSeek results. Their raw Gemma reports remain exact, including imperfect
judgments. Four fresh scenes are authored locally; no model generated the scene,
report, selected spans or gold. They retain ordinary-report sections and include
qualified craft opinions. Those opinions are not false factual premises simply
because another reader might disagree.

There are **18 unique target specifications**, yielding **36 target opportunities
per condition**: 26 supported, eight unsupported and two uncertain. Twenty-four
opportunities per condition are in fresh families. All five non-H2 target sets
retain two independently supported grounds. H1's false premise does not justify
clearing its real boundary failure or rewriting all otherwise adequate prose.

The complete local `casebook.md` contains every scene, context artifact, full
report, target span, gold rationale and example witness set. Examples establish
feasibility, not model success or an exhaustive list of acceptable evidence.

## Source and response boundaries

Full artifact contents are supplied with their exact version identities. The
compact citation index maps each S-prefixed reference to an artifact field and,
for prose, its paragraph. The private registry additionally binds content/field
hashes, offsets and exact text. No source text was trimmed to fit the budget.
The field index maps U-prefixed IDs to locations in the complete report. A
report allegation is never promoted into source evidence.

The reviewer returns one bare JSON object with an `assessments` array. Each row
contains `field_id`, an exact contiguous `quote`, `support`, `evidence` and
`reason`. The application locates the quote in its complete field. Missing or
ambiguous occurrences, duplicate rows/keys/refs, extra fields and invalid refs
are rejected without repair. Fenced JSON is rejected explicitly.

SA may return zero to twelve selections. An empty valid SA array is a measurable
admission omission, not a delivery repair opportunity. VA must return all three
supplied field/quote pairs exactly once and no others. The shared schema permits
the same row shape; the supplied-span identity check enforces VA completeness.

Each row permits up to eight source references and 1–1,200 reason characters;
combined reasons are capped at 8,000 characters. Quotes are 1–2,400 characters.
Definite judgments require source evidence; uncertainty may use an empty reference
list only with an adequate scope explanation. Supported, unsupported and uncertain
retain the explicit complete-source versus unavailable-source distinction.

These checks certify bindings and delivery, not truth. A correct-looking label
or exact quote does not establish that the explanation is grounded.

## Frozen inspection and decision rules

Inspect **every returned assertion and reason**, plus **all three targets in
every attempted cell**. Invalid deliveries and unstarted stopped cells remain in
the denominators. Record separately:

1. Delivery and exact span binding.
2. Admission: covered, omitted, meaning changed or unresolved.
3. Correct target label.
4. Usability: faithful meaning, correct support, adequate source evidence and
   grounded reason, with no material error.
5. Preservation of the 26 supported target opportunities, additional material
   errors, and resource use.

An exact target span that was returned cannot be annotated as omitted to turn a
reasoning failure into an admission failure. A selected premise judged wrongly
remains a semantic failure. A correct label with an invented premise receives no
usable credit. Unsupported added explanations remain visible even if all primary
labels are correct. Additional qualified literary readings are distinguished from
unsupported factual assertions.

The conservative **admission-signal** screen requires all 24 valid deliveries,
**36/36 usable VA targets**, no VA material explanation errors, no paired loss of
an SA-usable target, and at least **two actual paired admission recoveries across
two families, including a fresh family**. A recovery requires a valid SA report
that misses or changes the target and a usable VA counterpart. Invalid SA output
does not create an admission opportunity. Selection supplied to VA is never
counted as a learned capability.

Shared failures after both conditions identify the relevant premise are reported
as a semantic bottleneck, without advancement. VA-only semantic gains after
successful SA admission are reported separately, not called admission recoveries.
If both align or admission opportunities are insufficient, retain descriptive
evidence without claiming a recovery. Incomplete execution or delivery limitations
receive their own non-advancement result. No decision promotes a verifier, grants
writer permission, closes CW-013/CW-006 or establishes literary improvement.

The operator export hides arm/order/trial identifiers and excludes thinking from
semantic inspection. Full sources, report, targets and all final assertions remain
available. Seal complete source-bound notes before decoding the key. Familiar
reports and supplied-span behavior may reveal condition: this is **partially
masked assistant factual inspection**, not blind human literary preference.
Terminal exports retain the error chain, raw evidence and unknown usage.

## Model baseline, budget and stops

Metadata-only checks on **2026-10-31** confirm **Ollama 0.40.13**, unchanged selected
DeepSeek metadata and high-thinking capability. Model:
`deepseek-v4.1-flash:cloud`; digest:
`e04da138d31e0c9468e982e1ae9503d06cb7e170caa16a90c17d931c4aa140f8`.
Three successful `/api/version`, `/api/tags`, `/api/show` responses are sealed.
The earlier sandbox socket denial is retained. No prose was transmitted and no
generation was requested. Matching metadata does not attest to an unchanged
hidden provider backend.

Settings: **thinking high**, temperature **0.2**, top-p **0.95**, seed **20261022**,
non-streaming, context **40,000**, no format override. The largest quarter-byte
input estimate is **15,037 tokens**; this is a sizing heuristic, not a tokenizer
guarantee.

| Resource | Per attempt | Total reservation |
| --- | ---: | ---: |
| Calls | 1 | **24**, twelve per condition |
| Input tokens | 24,000 | 576,000 |
| Combined generated tokens, including thinking | 16,000 | 384,000 |
| Active request time | 600 seconds | 14,400 seconds |

Thinking shares the output allowance. Reasoning/final splits are unknown unless
explicitly reported. The archived $0.30/$1.20-per-million reference yields
**$0.63360**, with a **$0.75 planning allowance**; neither is a current tariff
verification or an enforceable billing cap. Actual provider billing remains
unknown. Report measured latency and tokens per attempted and usable report.

The first **eight calls** cover H1/H2, both conditions and both orders, within the
24-call ceiling. Stop after these delivery sentinels if either condition has zero
valid outputs, or the same blocking delivery signature occurs in both historical
families within either condition. A signature confined to one family does not
trigger that repeated-signature stop. No semantic early stopping is allowed.

Non-200/transport/gateway failure, truncation, absent thinking, unknown/excess or
conflicting usage, invalid timing, metadata drift, tampering, ledger gaps,
ambiguous dispatch and cancellation cause a terminal stop. Reserve before
dispatch; preserve raw evidence and unknown usage. Failed attempts consume their
slots. Terminal attempts cannot resume automatically; a clean completed-cell
boundary may continue only through the original unspent schedule. No retry or
replacement allowance is created. Check model metadata before every call and
daemon version before and after every call.

## Verification and approval boundary

Verification records are retained in the private bundle. The checks exercise all
24 synthetic dispatches, exact request replay, source order and condition parity,
source/quote/registry bindings, delivery limits, restart/no-repeat behavior,
sentinels, non-200 and transport terminal export, version drift, unknown usage,
masked inspection binding and admission-versus-semantic scoring. Real HTTP is
blocked during tests. Production code and historical scores are unchanged.

**252 offline tests pass:** 93 current diagnostic checks, 54 prior admission
checks, 83 export/comparison checks and 22 inherited version-evidence checks.
The combined current/export/version run passes 198 tests in 55.70 seconds; the
isolated prior-admission suite passes 54 in 2.55 seconds. Ruff lint/format and
strict mypy pass on all **nine local scripts**. No production/API/frontend or
persistence code changed, so unrelated application/build suites were not rerun.
The freeze binds **397 historical/runtime source fingerprints**, including the
unchanged 212-file production Python baseline and the fourteen issue bodies.

Preparation refinements are recorded before sealing: the initially duplicated
source registry exceeded the input allowance; it was replaced by a compact location
index without removing source text. F4's request completion and the officer's
absence were clarified before freezing. Static formatting/type fixes, historical
test-module name collisions and the inherited parser's fence acceptance were
resolved locally. Prior attempts remain available. No live output informed these
changes.

Private bundle: `data/diagnostics/reviewer-premise-admission-v61-2026-10-31/`:
cases/casebook, targets and admitted spans, source registries, schemas, exact
`prepared/` requests and wire payloads, schedule/budget/scoring/stops, metadata,
inspection contract, runner/exporter, tests, verification records and `plan.json`.
Full mocked responses and annotations are explicitly synthetic.

No approval record or live execution directory exists. Approval must bind the
final plan hash, **24 total calls**, twelve per condition, zero retries, full
unpublished fictional prose/context/reports and admitted spans sent to **Ollama
Cloud through the local daemon**. This preparation authorizes no inference.

Human review retains feel, flow, character and story-breaking judgments. Exact
binding, a smaller edit or a successful premise judgment is not a story-quality
score. The Blueprint checkpoint and nine prior human ties remain unchanged.
All fourteen issue bodies/posted links remain intact; no external issue is edited
or closed. **Step 19 IN PROGRESS; Step 20 NOT STARTED; inference PAUSED; full
workflow canary ON HOLD.**
