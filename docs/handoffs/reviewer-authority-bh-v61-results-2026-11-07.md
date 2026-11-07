# Sol-high B/H authority comparison — results

Date: 2026-11-07. **Completed: 24/24 attempts; all 144 fixed slots inspected.**
Production prompts/profiles unchanged; further live calls **PAUSED**;
full workflow canary **ON HOLD**.

**B and H both achieved 72/72 grounded whole-claim successes.** All supported,
contradicted and uncertain controls passed in both presentation orders and both
repeats. There were **zero paired recoveries and zero regressions**. Under the
prospective decision rule, this is a **ceiling tie**, not evidence that H improves
accuracy. H added **29.6% input tokens**.

This is useful positive evidence for Sol-high assessing clear authority contrasts
with complete sources and explicit work briefs. It does not establish precision
on ambiguous ordinary reviews, necessary editing, preservation or story quality.

## Execution and accounting

The user approved the [frozen local plan](reviewer-authority-bh-frozen-plan-2026-11-07.md),
including full prose/context at OpenAI Responses and its input-count endpoint.
Plan SHA-256 remains:
`53638172ce2ead7f42810934478ce59dac69630eacea0d73f8d6775691d60d90`.

The runner executed **once**, with `gpt-6.1-sol` and reasoning `high`, in the
frozen interleaved order. It used exactly **24 generation POSTs, 24 separate
full-context input-count POSTs and 24 catalog GETs**. Each story-bearing request
matched its frozen body hash. Every returned model identifier matched the selected
alias; this does not establish an immutable backend snapshot.

All 24 outputs passed the native six-claim schema and evidence-location binding;
all 24 read-only work completions are valid. Every count and generation response
was HTTP 200. No empty, truncated, refused, malformed or interrupted delivery
occurred. No stop rule fired, and no retry, repair, continuation, fallback or extra
judge call was made. All attempts are spent; none remain for resampling.

## Fixed-denominator results

| Measure | B: full context + work brief | H: B + provenance/copy receipt |
| --- | ---: | ---: |
| Valid deliveries | 12/12 | 12/12 |
| Bound assessment slots | 72/72 | 72/72 |
| Correct whole-claim labels | 72/72 | 72/72 |
| Complete material coverage | 72/72 | 72/72 |
| Adequate cited evidence | 72/72 | 72/72 |
| Faithful explanations | 72/72 | 72/72 |
| Grounded whole-claim successes | **72/72** | **72/72** |
| Supported controls grounded | 24/24 | 24/24 |
| Contradicted controls grounded | 24/24 | 24/24 |
| Uncertain controls grounded | 24/24 | 24/24 |

Each family scored 24/24 in each condition. All **36 family/claim/condition groups**
passed in all four presentation-order/repeat observations. All **72 B/H slot pairs**
were grounded ties. The H recovery criterion was not met because there was nothing
to recover; no B-pass/H-fail regression appeared either.

The assistant directly inspected all 24 raw finals against all complete source
packets, the eighteen frozen gold judgments and the adequate-evidence criteria.
All 144 annotations bind to the exact request and raw final hashes. This is identified
assistant inspection against prospective assistant-authored controls, **not independent
human adjudication**. Labels were scored mechanically; evidence adequacy, material
coverage and explanation fidelity were inspected rather than inferred from labels.

## What the outputs actually got right

- **Seed-house sluice:** both arms retained the distinction between the reviewer's
  authentic allegation and the earlier assignment's express authorization to open
  the sluice. They explained the real opening without calling it a violation. They
  separately checked all trays inside and closure at the current endpoint, and did
  not turn the reviewer's closed-throughout request into a current obligation.
- **Observatory booking:** both arms established the four-year date relation while
  rejecting current recognition using the prose's explicit denial. They correctly
  accepted the earlier version's requirement and depicted realization, and explained
  why the genuine request to retain realization did not govern the replacement plan.
- **Cinema reel:** both arms rejected the false earlier opening using the full old
  prose's explicit non-opening evidence. They accepted the separate claim about what
  the reviewer alleged and quoted, without treating the scale quotation as proof of
  opening. They distinguished a real projection request from the current prohibition
  and covered every required current action and the non-projection condition.
- **Missing sources:** all 48 uncertain slots cited the actual availability record.
  Neither arm inferred missing memorandum, audit, warrant or continuation contents
  from a similar available instruction, a current endpoint or a deferred action.

Correct reference sets were not required to copy the example lists exactly. For
example, cinema Q1 often cited the contradicted review alongside the decisive old
prose; Q3 also cited the old prose to establish the quotation and explain its limits.
Some warrant judgments cited the earlier assignment to explain why its sealing
instruction did not establish the separate warrant's terms. These added citations
supported the actual explanations and did not earn semantic credit merely by binding.

## Resources and headroom

| Reported resource | B, 12 attempts | H, 12 attempts |
| --- | ---: | ---: |
| Input tokens | 71,560 | 92,752 |
| Cached input tokens, included above | 35,762 | 46,358 |
| Generated tokens, including reasoning | 10,467 | 10,916 |
| Reasoning tokens, included above | 3,351 | 3,725 |
| Mean active seconds | 10.40 | 10.74 |
| Median active seconds | 10.45 | 10.52 |
| Active seconds, total | 124.79 | 128.87 |
| Conservative reference cost | $0.28357 | $0.34104 |

Totals: **164,312 input tokens, 21,383 generated tokens including 7,076 reasoning
tokens, and 253.66 active seconds**. Cached input totaled 82,120 tokens. Counts
from the input-count endpoint matched reported generation input for every attempt.
No usage field is unknown.

H added **21,192 input tokens (+29.6%)**, 449 generated tokens and 374 reasoning
tokens. Its mean active time was 0.34 seconds higher. These latency observations
come from one interleaved run with caching and ordinary provider variation; they
do not establish a reliable causal latency penalty. Active time covers counting
and generation, excluding catalog checks and local bookkeeping.

The largest request used 7,815 input tokens; the largest output used 1,086 tokens
including reasoning, and the longest active attempt took 12.83 seconds. All were
within the frozen 24k input, 32k generated and 600-second per-attempt limits.

The **$0.62461 total reference cost** uses the frozen conservative formula, charging
all reported input at the reviewed input rate with its 1.25 multiplier and output
at the reviewed output rate. It deliberately does not apply a cached-input discount.
It is below the $9.12 reservation bound and $14.40 allowance. **Actual billed cost
was not verified**; this number is not an invoice.

## Interpretation and next step

The result supports a narrow conclusion: **Sol-high can consistently resolve these
explicit, version-specific authority and availability contrasts with B's existing
full-context work brief and native reference interface.** These failure classes
are not inevitable on every input. No delivery problem was reproduced here.

It does not establish that H is generally useless. B already contains the same
source roles, lineage, visibility and assignments; H reorganizes and repeats them.
With B at the ceiling, this comparison cannot demonstrate an accuracy increment.
There is no evidence here to justify routinely adding the receipt to model input
and paying its measured token overhead. Its value as an operator provenance and
copy audit remains a separate application concern.

These deliberately clear authored scenes contain explicit permission, prohibition,
denial and unavailability statements. They are not a natural-review sample. The
previous admission's lack of clear natural-negative controls remains unresolved.
Nor is B an unchanged replay of an older quote-witness or ordinary-review request:
the common native interface and this authored workload limit historical comparisons.
There are three scene families, not 144 independent samples. No writer edited any
prose, and this diagnostic made no craft or edit-necessity judgment.

**Recommended next work is local, not another repeat of this authored comparison:**

1. Preserve representative B/H successes as regression fixtures, especially false
   historical violations, authentic but non-authoritative requests, quotation versus
   event truth, current realization denial and unavailable-source judgments.
2. Audit a bounded read-only assessment/export path using B's complete source and
   work-brief context. Keep the provenance/copy receipt inspectable by the operator;
   do not promote structural binding into semantic truth or a writer permission.
3. Before proposing further inference, identify a materially harder ordinary-review
   authority question with defensible whole-claim gold and complete version-specific
   evidence. Admit clear negative and uncertain controls without rewording away
   ambiguity. If none qualify, record the limitation rather than manufacturing a
   natural-negative precision claim or repeating the same ceiling test.

These are proposed follow-ups, not changes made by this execution. Human review
continues to focus on feel, flow, character and story-breaking details. Better
factual assessment may prevent unjustified edits, but preservation and story quality
still need their own evidence before production promotion.

## Verification and artifacts

The post-run audit revalidated all **48 frozen members, 296 source pins, 24 sealed
capture cells, 24 native completions and 144 raw-final-bound inspections**. It
reconciled the exact endpoint dispatch counts, completion hash and known usage.
The frozen 338-test preparation baseline remains applicable because its verified
source files and harness are unchanged; the broad suite was not unnecessarily rerun.
The new local accounting helper passes Ruff, formatting and strict mypy, and its
analysis is reproducible without provider access.

The first local export invocation used a relative path, which the path guard rejected.
Using the canonical absolute paths completed the export. This involved no provider
request, source amendment, score change or frozen-harness edit.

Private results: [index and provenance](../../data/diagnostics/reviewer-authority-bh-v61-2026-11-07-results/README.md),
[summary](../../data/diagnostics/reviewer-authority-bh-v61-2026-11-07-results/summary.json),
[all 144 slots](../../data/diagnostics/reviewer-authority-bh-v61-2026-11-07-results/inspection-ledger.md),
[semantic inspections](../../data/diagnostics/reviewer-authority-bh-v61-2026-11-07-results/semantic-inspections.json),
[request resources](../../data/diagnostics/reviewer-authority-bh-v61-2026-11-07-results/request-resources.json),
[audited run](../../data/diagnostics/reviewer-authority-bh-v61-2026-11-07-results/audited-run.json).
Full prose and raw captures remain in ignored local data.

CW-007/CW-013 remain open; CW-014 remains unqualified. No issue is closed or
externally edited. **Step 19 IN PROGRESS; Step 20 NOT STARTED; further live calls
PAUSED; production prompts unchanged; full workflow canary ON HOLD.**
