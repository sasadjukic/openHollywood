# Sol-high ordinary-review U/B results

Date: 2026-11-07. **Completed: 32/32 attempts, no retries.**

The explicit brief condition **B improves the frozen grounded score to 63/64**, from
**52/64 for U**, with **11 matched recoveries and no regressions**. It **does not
pass the frozen improvement screen**, which requires all 64 B slots grounded.
The remaining B failure is an omitted realization citation under the predeclared
criterion. That criterion itself needs a local materiality audit: the selected
correction claim expressly describes corrected dates and a required gap, while
the rubric additionally requires the character's realization. These scores remain
unchanged; the protocol failure is not proof that the model invented a date or
that the story needs another edit.

All **32 responses were valid**, and all **128 fixed slots were inspected**. The
[frozen plan](../handoffs/reviewer-ordinary-brief-frozen-plan-2026-11-06.md) was
executed once under explicit approval, sending full prose/context to OpenAI
Responses and its input-count endpoint. Production prompts, profiles, graph and
routing remain unchanged. **Further live calls are PAUSED; canary ON HOLD.**

## Fixed-slot outcome

Both conditions used `gpt-6.1-sol` at `high`, unchanged controls and full context.
B added only the frozen authored assessment brief. Four saved report packets
cover two closely related scene families, with both orders and two exact-body
repeats. Each request assessed four unchanged whole fields: 16 unique claims and
128 fixed slots. All sixteen gold labels are supported; this is not a test of
natural false-positive precision or uncertainty calibration.

| Packet | U grounded | B grounded | Remaining failures under frozen scoring |
| --- | ---: | ---: | --- |
| R1 — Elara post-review | 12/16 | 16/16 | Four U historical-scope/uncertainty failures |
| R2 — Elena initial date review | 16/16 | 16/16 | None |
| R3 — Elena date post-review | 12/16 | 15/16 | Four U and one B citation-only failures |
| R4 — Elena decision post-review | 12/16 | 16/16 | Four U historical-attribution citation failures |
| **Total** | **52/64** | **63/64** | **Four semantic / nine citation-only / zero unavailable** |

The 32 initial-review slots are all grounded. Post-review results are **U 36/48,
B 47/48**. All failures occur in three historical correction fields; the other
**104 slots, covering thirteen unique fields, are grounded in both arms**. These
include purposeful decisions, conditional thoughts, current dates and realization,
turn definitions, and achieved states. This does not qualify those capabilities
outside these admitted examples.

Labels match gold in **124/128 slots**: U 60/64, B 64/64. All **386 exact witnesses**
resolve, and all 128 slots have complete mechanical binding. Location alone does
not establish material evidence coverage. All native work completions are delivery
complete; their read-only status does not grant semantic approval or writer access.

Of the 64 U/B pairs, **52 are grounded in both arms, 11 recover a U failure, and one
fails in both**. There are no U-grounded/B-failing pairs. B passes fifteen of sixteen
four-slot claim gates; U passes thirteen. The failed B claim is R3 Q003, with three
grounded assessments and one citation-only failure.

Both the 64 repeat pairs and the 64 presentation-order pairs have **64/64 label
agreement**, but only **57/64 both-grounded pairs**. Within each comparison, U has
26/32 both-grounded pairs and B 31/32. U's failed categories are stable; B's final
R3 Q003 differs from its passing identical first CP repeat and passing second PC
response. Stable labels are not sufficient evidence of grounded repeatability.

## What failed and what the briefs changed

### R1: preserved excerpt versus complete historical verification

The selected correction field says the previous sill-crossing violation was
corrected and the current scene ends outside. The visible historical repair record
contains an `original_evidence` excerpt explicitly depicting crossing. Complete
older prose is unavailable. The frozen admission accepts comparison with that
recorded evidence; it does not authorize reconstructing the whole older draft.

All four U responses return `uncertain`. They correctly describe current outside
compliance but treat the historical clause as requiring the unavailable older draft,
describe its support as a critic allegation, and cite only the current boundary and
prose. All four B responses cite the preserved original excerpt plus the current
boundary and prose, return `supported`, and expressly limit the result to correction
of the recorded target.

This is **four recoveries under the admitted scope**, not evidence that arbitrary
critic allegations prove story events. The outputs do not reveal whether U overlooked
or deliberately discounted the excerpt. Nor does B independently verify complete
older-draft truth. The distinction between a previous event, an attributed claim
and an application-verified excerpt still needs an explicit production contract.

- [First U PC failure](../../data/diagnostics/reviewer-ordinary-brief-v61-2026-11-07-analysis/views/OB-1-R1-U-PC.md), Q003
- [Matched B PC recovery](../../data/diagnostics/reviewer-ordinary-brief-v61-2026-11-07-analysis/views/OB-1-R1-B-PC.md), Q003
- [U identical second PC repeat](../../data/diagnostics/reviewer-ordinary-brief-v61-2026-11-07-analysis/views/OB-2-R1-U-PC.md), Q003

### R3: current requirement, realization and the remaining B failure

All eight labels for the date-correction field are `supported`; the date facts and
historical attribution are correct. Under the frozen criterion, all four U citation
sets are incomplete. The first U PC response cites the old allegation and current
dates but no actual current assignment or realization. The other three cite the
recorded `requested_change` rather than the actual assignment authority; two also
omit the current realization. A requested repair establishes what was requested,
not independently what the canonical assignment requires.

Three matched B responses cite the historical claim, actual assignment, both dates
and realization. The final **`OB-2-R3-B-CP`, Q003** cites the historical claim, actual
assignment and both dates, but omits the realization. It cites that very realization
for Q002 and Q004 in the same response. The frozen per-claim rule does not allow
borrowing those citations. Its identical first CP body passed.

The selected field includes:

> The current draft corrects this: the card is now dated October 14th, 2034, while the current date is October 14th, 2024, establishing the required ten-year gap.

The **pre-response rubric additionally requires realization evidence**. That is a
material evaluation-design question: does this whole claim assert realization,
or only the corrected date relation? Does “required” refer to the canonical turn
or to the recorded repair request? This report applies the frozen rule and records
**one B citation-only failure**, but does not resolve those questions by changing
the gold after seeing the response. The result does not show that the model failed
to notice the realization; its other two assessments cite it.

- [U missing assignment/realization evidence](../../data/diagnostics/reviewer-ordinary-brief-v61-2026-11-07-analysis/views/OB-1-R3-U-PC.md), Q003
- [U citing the requested repair](../../data/diagnostics/reviewer-ordinary-brief-v61-2026-11-07-analysis/views/OB-1-R3-U-CP.md), Q003
- [B final omission](../../data/diagnostics/reviewer-ordinary-brief-v61-2026-11-07-analysis/views/OB-2-R3-B-CP.md), Q003
- [B passing identical first CP body](../../data/diagnostics/reviewer-ordinary-brief-v61-2026-11-07-analysis/views/OB-1-R3-B-CP.md), Q003

### R4: correct current repair without cited historical attribution

All four U responses correctly describe the current decision and return `supported`.
They cite the ending and actual requirement, but omit the specific historical
unresolved-choice claim/evidence. One additionally cites a generic `accept_when`
field; its entire contents still do not identify that earlier allegation. The
neighboring historical `claim` field cannot be credited automatically.

All four B responses cite that historical attribution, the actual current
requirement and the complete current ending. They preserve conditional thinking,
purposeful reaching and intent without inventing completed journal retrieval,
comparison or a handwriting match. These are **four matched citation recoveries**.

- [U current-only comparison](../../data/diagnostics/reviewer-ordinary-brief-v61-2026-11-07-analysis/views/OB-1-R4-U-PC.md), Q003
- [Matched B historical attribution](../../data/diagnostics/reviewer-ordinary-brief-v61-2026-11-07-analysis/views/OB-1-R4-B-PC.md), Q003

## Inspection limits and alternatives

This is assistant primary-source adjudication, not blind human review. All 128
slots retain their frozen fields, gold, criteria and receipt/result hashes. No
claim, threshold, denominator or source was changed after inference. One inspection
note was clarified before scoring to avoid treating duplicate historical excerpt
references as a whitelist; its original and clarification are archived, with no
flag or category change.

The full historical claim can establish what was alleged, including the historical
dates it quotes. It cannot independently prove the whole older draft or the current
assignment. A short witness locating the final prose paragraph can cover its
conditional thought, journal location, action and purpose. Alternative adequate
sections were accepted: later explicit future-date recognition and purposeful
handling/reading can establish the corresponding achieved-state events. No
uncited adjacent section or cross-claim citation was credited.

The cases remain synthetic, unapproved diagnostic contexts from saved ordinary-v61
probes, not a representative sample of durable production reviews. All gold is
supported. An always-supported labeler passes label-only scoring, so B's 64 correct
labels cannot establish that it rejects naturally false criticism. The four-field
workload also differs from the preceding six-field experiment. This run does not
establish automatic brief neutrality, story-quality improvement, repair necessity,
prose preservation, provider superiority or full-workflow readiness.

## Budget and observed resources

Exactly **32 generation dispatches, 32 separate story-bearing input counts and
32 catalog checks** occurred. No retries, fallback, extra warm-up, continuation or
unbudgeted inference was used. All reported models are `gpt-6.1-sol`; all frozen
requests use `high`. Counts, usage and captures are known for every attempt.

| Measure | U — 16 attempts | B — 16 attempts | Total |
| --- | ---: | ---: | ---: |
| Input tokens | 366,608 | 370,452 | **737,060** |
| Generated tokens, including reasoning | 39,671 | 39,221 | **78,892** |
| Reasoning tokens, included above | 18,172 | 16,358 | **34,530** |
| Reported cached input tokens | 200,682 | 202,417 | **403,099** |
| Active count + generation seconds | 489.30 | 450.72 | **940.02** |
| Median active seconds per attempt | 29.67 | 28.04 | **28.43 overall** |
| Frozen-rate reference cost | $1.313230 | $1.318340 | **$2.631570** |

B adds 3,844 input tokens across the matched requests, with 450 fewer generated
tokens and 1,814 fewer reasoning tokens observed. These are descriptive results,
not a guaranteed latency/token effect; cache state and output variability differ.
Active time excludes catalog checks, local ledger work and human/assistant inspection.
Actual billing is **unknown**; the reference cost uses the frozen conservative
uncached rates, not an invoice or claimed cache discount. It remains below the
$12.16 reservation and $19.20 planning ceiling.

The largest input count is **23,568/24,000**, leaving only 432 tokens of input
headroom. Maximum generation is **3,695/32,000** tokens, maximum final text is
6,299/64,000 characters, and the longest active attempt is **51.06/600 seconds**.
No truncation or delivery/resource stop occurred. This does not qualify larger
ordinary packets or longer stories within the same input limit.

## Verification and artifacts

**16 new offline result tests pass.** Repository Ruff, formatting and strict mypy
pass for **228 Python files**; private checks pass for **24 scripts** (19 frozen
preparation scripts and five result helpers). All nine final recorded checks pass,
including deterministic result/table replay, actual endpoint-body hashes, the
completed budget ledger, all slot/receipt bindings, every literal full-context
view, native result revalidation and mutation rejection. The **370 frozen
preparation tests remain unchanged and were not counted as newly rerun**.

The initial result test assumed a fixed Markdown fence length; the renderer uses
a content-dependent fence. That test helper was corrected and all sixteen tests
rerun. The initial failed check and successful replacement remain recorded. No
model output, gold, scoring rule or observation flag changed. No additional model
call was made for verification. Frontend/build checks are inapplicable to this
documentation/private-analysis change; production Python sources are unchanged.

All **68 frozen files and 1,753 source fingerprints** still match. The completed
ledger, 32 literal views, 128 inspections, pair/resource tables and verification
logs are retained in the private archive and final evidence seal.

Private artifacts:

- Frozen plan: `data/diagnostics/reviewer-ordinary-brief-v61-2026-11-06/`
- Live captures: `data/diagnostics/reviewer-ordinary-brief-v61-2026-11-06-M-live/`
- [Inspection archive](../../data/diagnostics/reviewer-ordinary-brief-v61-2026-11-07-analysis/README.md)
- [All fixed-slot judgments](../../data/diagnostics/reviewer-ordinary-brief-v61-2026-11-07-analysis/inspection.json)
- [Inspection method and materiality decisions](../../data/diagnostics/reviewer-ordinary-brief-v61-2026-11-07-analysis/inspection-method.md)

The exact plan SHA-256 remains
`b6bec287634f81bcba4464eeb9326817144c639ccfbef976a28bfab98dfa1ab1`.
No API key, authorization header or OpenAI reasoning content is retained in these
artifacts; reasoning token counts are retained.

## Recommended next step

Retain B as promising diagnostic evidence, **not a qualified production gate**.
Do local work before considering more inference:

1. Preserve the historical-scope and attribution failure/recovery pairs, and the
   final B omission with its passing identical control, as regression fixtures.
2. Audit historical event truth versus attributed claims and verified excerpts,
   including whether an authored brief changes the asserted proposition. Separately
   audit R3 Q003's minimum material evidence, realization requirement and the
   authority of a requested repair versus a canonical assignment. Keep this run's
   original scoring intact; document any later gold correction separately.
3. Check how those distinctions can be represented in the existing read-only
   work/brief component without granting writer authority. Require defensible
   false-claim controls and a materially justified hypothesis before another live
   comparison; repeating this all-supported workload cannot establish precision.

No new experiment is frozen or authorized here. Human judgments of feel, flow,
character and story-breaking effects remain separate from factual evidence checks.
CW-007/CW-013 remain open; CW-014 remains unqualified. All fourteen issue bodies
and posted URLs remain unchanged. **Step 19 IN PROGRESS; Step 20 NOT STARTED;
production prompts unchanged; live calls PAUSED; full workflow canary ON HOLD.**
