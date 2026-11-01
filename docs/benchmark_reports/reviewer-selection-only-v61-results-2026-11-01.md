# SA/SO premise-selection comparison results

Date: **2026-11-01**. **10/16 calls attempted; nine valid outputs; one length
failure; six SA cells retired without dispatch; zero retries.** Production
**prompt61 / graph9 / fulfillment policy1** unchanged. Further inference
**PAUSED**; full workflow canary **ON HOLD**.

**SO passes the frozen selection-feasibility screen, under its complete-report-field
context contract. It does not establish an efficiency benefit or qualify a production
change.** SO delivered 8/8 valid outputs and faithfully retained all **24/24 primary
targets**, including **12/12 fresh-family opportunities**. SA delivered one valid
report, then reached the 16,000-generated-token limit with an empty final response.
The approved rule retired SA while allowing SO to finish its unchanged schedule.

Only **one complete valid pair** survived. In that pair, SO used **14,262 generated
tokens / 48.64 seconds**, versus SA's **13,011 / 36.15 seconds**. The required
eight-pair resource screen is **not evaluable**. The observed pair favors SA on
these resource measures; it cannot establish a general cost or latency difference.

Retain SO as a **bounded premise-selection candidate for local staged design**.
It has not demonstrated correct support judgments, citation adequacy, whole-report
completeness, writer preservation, end-to-end savings or improved story quality.

The [frozen plan](../handoffs/reviewer-selection-only-frozen-plan-2026-11-01.md)
and [preceding audit](../handoffs/reviewer-admission-delivery-audit-2026-11-01.md)
remain unchanged. Plan SHA-256:
`4ab67cbefa480bfec751e58d7a5c66d5b03be05278773027471c6a9a822f9a99`.

## Execution and the condition stop

The user explicitly approved the sixteen-call ceiling and sending full unpublished
fiction/context and saved reports to Ollama Cloud through the local daemon.
All dispatched wires match the frozen requests. Source packets, sampling settings,
budgets, scoring and stops were unchanged; there were no repairs, replacements or
reallocations. The prior SA/VA run's six calls and global terminal stop remain separate.

| Actual attempt | Frozen cell | Result | Generated tokens | Active seconds |
| ---: | --- | --- | ---: | ---: |
| 1 | S-SA-H1-PC | Valid | 13,011 | 36.15 |
| 2 | S-SO-H1-PC | Valid | 14,262 | 48.64 |
| 3 | S-SA-H2-CP | Length; empty final; SA retired | 16,000 | 46.37 |
| 4 | S-SO-H2-CP | Valid | 13,667 | 40.17 |
| 5 | S-SO-H1-CP | Valid | 13,290 | 41.03 |
| 6 | S-SO-H2-PC | Valid | 9,244 | 27.74 |
| 7 | S-SO-F2-PC | Valid | 7,565 | 23.58 |
| 8 | S-SO-F4-PC | Valid | 7,613 | 23.93 |
| 9 | S-SO-F2-CP | Valid | 6,031 | 17.73 |
| 10 | S-SO-F4-CP | Valid | 8,328 | 22.51 |

Actual attempt numbers differ from original schedule ordinals after SA retires;
SO's original relative order remains intact. Its four historical cells all
validated, so the historical delivery checkpoint permitted its four fresh cells.
The six remaining SA cells cannot be retried or restarted under this plan.

The SA failure returned **HTTP 200**, `done: true`, `done_reason: length`, **15,265
input / 16,000 generated tokens**, and **zero final characters**. A nonempty thinking
field was observed and hashed, but its text was not used as semantic evidence.
The gateway error chain was preserved:

1. `ModelGatewayError`, `invalid_response`: “Ollama response metadata is invalid”.
2. Caused by `ValueError`: “response content must not be empty”.

The new, previously tested handler recognized only this integrity-bound length
response and known empty-content rejection. It captured the post-call daemon
version, retained the full consumed reservation, recorded an **unusable terminal
attempt**, and retired SA. It did not create a successful gateway response, score
partial output or retry. There was no global transport/unknown-usage stop.

All **21 version observations** matched **Ollama 0.40.13**, including before and
after the failed attempt; **eleven model checks** matched the frozen digest and
capabilities. Every call requested DeepSeek high thinking, temperature 0.2,
top-p 0.95, seed 20261022, context 40,000, non-streaming and no format override.
These observations do not prove effective sampling or an unchanged remote backend.
All ten raw responses were HTTP 200; there is no observed service-unavailability
response in this run.

## Inspection and results

The supported exporter shuffled ten attempt records. All **49 selections** in the
nine valid outputs and all **27 corresponding primary target opportunities** were
inspected against the complete report fields, supplied drafts, assignments, scope
metadata and relevant next-scene context. Notes were source/result-bound, validated
and sealed before decoding the trial key. Thinking text was excluded from the export.

This was a **partially masked assistant source audit**, not independent blind human
review. Output shapes and familiar cases reveal the task; execution monitoring also
exposes delivery/resource information. The review export itself withheld trial/arm/order
labels and token/timing measures. The exact whole-field notes remain local.

| Measure | SA | SO |
| --- | ---: | ---: |
| Planned calls | 8 | 8 |
| Attempted calls | 2 | 8 |
| Valid outputs | 1 | 8 |
| Length failures | 1 | 0 |
| Unstarted calls | 6 | 0 |
| Selections inspected | 8 | 41 |
| Faithful primary admissions, completed outputs | 3/3 | 24/24 |
| Faithful primary admissions, fixed denominator | 3/24 | 24/24 |
| Fresh primary admissions | 0/12, unstarted | 12/12 |
| Faithful targets per attempted call | 1.5 | 3.0 |
| Faithful targets per planned call | 0.375 | 3.0 |
| Grounded usable primary assessments | 3/3 completed | Not requested |
| Material selection distortion / opinion factualization observed | 0 / 0 | 0 / 0 |
| Overlapping/repeated premise selections counted once | 1 | 1 |

Unstarted and truncated cells remain in the frozen denominators, without being
called observed semantic errors. No primary loss appears in the single complete
pair. H2/CP supplies a delivery contrast, not a demonstrated recovery from an SA
semantic mistake: SA supplied no final assessment there.

H1 concerns **Elena's handwriting verification**; H2 concerns **Elara's building
entry**. SO admits H1's unsupported missing-decision allegation while also retaining
the valid no-match endpoint violation and ten-year date realization. In H2 it
retains the fulfilled decision, both touch/pull events, and the genuine entry violation.
The observed event and independent endpoint error remain separate.

Both F2 orders preserve the false allegation that the living Mira plans to burn
the atlas, alongside the valid closed-box violation and decision to seek help.
Both F4 orders preserve the universal allegation about unavailable Appendix B,
alongside the valid envelope-opening violation and decision to request the appendix.
**Selecting these allegations does not mean SO correctly rejects or qualifies them.**
No support labels, citation arrays or reasons were requested from SO.

### Why full field context matters

The frozen contract explicitly retains each selected quote's complete report field
and permits multiple selected rows to cover a target. Coverage was adjudicated from
that complete proposition, not awarded for word overlap. Three cases deserve attention:

- **S-SO-H1-CP** selects the observed match from U007 and the no-match-by-end
  obligation from U005 separately. The original full U007 field explicitly compares
  them. Together the selected components and retained field preserve the endpoint
  target; neither isolated clause alone expresses the whole comparison.
- **S-SO-H2-CP** selects the outside requirement from U003 and actual entry from
  U005. The complete U003 field expressly states the violation. The joint selections
  retain the target under this contract, rather than asserting that a requirement
  proves the event occurred.
- **S-SO-F4-CP** selects opening before officer attendance but stops the quote before
  “violating the assigned boundary”. Its bound full U005 field retains that relation,
  and the separately supplied assignment and prose support it.

The notes document these coverage decisions explicitly. **The 24/24 result does
not qualify a bare-quote handoff** that strips away full fields or reconstructs
relations from unlinked snippets. That is an integration risk to test locally.

Extras were inspected rather than penalized merely for falling outside the three
targets. They include discovery facts, explicit obligations, scope availability and
next-scene allegations. No qualified literary opinion was promoted to a factual
defect. One SO current-scene verification statement overlaps an earlier selected
match premise; SA repeats its boundary comparison. Neither inflates target credit.

The one completed SA report gives correct, grounded assessments for all eight
selected assertions, including all three primary targets. It distinguishes the
general handwriting match from the specifically named next-scene flourish. That
literal distinction still does not decide whether early matching weakens the story's
pacing. SO makes no corresponding source-judgment or craft-quality claim.

## Resources and limits

| Resource | SA: two attempts | SO: eight attempts | Total |
| --- | ---: | ---: | ---: |
| Reported input tokens | 29,521 | 63,000 | 92,521 |
| Reported total generated tokens | 29,011 | 80,000 | 109,011 |
| Active generation seconds | 82.51 | 245.31 | 327.83 |

All reported counters passed the frozen consistency checks, including the consumed
length attempt. Total generated tokens are counted once; reasoning/final token
splits and actual billing remain unknown. The archived-rate reference is
**$0.1585695**, not actual billing or a verified current tariff. All per-call and
aggregate reservations were respected; SA reached the per-call output limit.

The only complete pair, H1/PC, has a generated SO/SA ratio of **1.096**, about **9.6%
more** for SO, with about **34.6% longer** active time. Its smaller final response
contract did not yield lower generation or latency in that observation. Seven
other complete control pairs are missing, so there is no eight-pair median and
the predeclared resource screen remains **not evaluable**, rather than passed.
Historical and fresh source packets differ substantially in size; comparing their
unpaired totals is not an isolated workload or efficiency experiment.

This run demonstrates feasible selection on this bounded case set and another
combined-task truncation. It does not establish why either condition used its
generation budget, whether a staged pipeline is cheaper, or whether this effect
generalizes to long stories, other models or production reports.

## Verification and next work

The separate read-only verifier replays the ledger, retirement decisions, every
wire/raw response, version/model checks, raw usage, sealed export, annotations and
frozen scores. All **54 frozen files and 671 historical/source fingerprints** are
checked without altering the prepared bundle or prior experiment. **266 offline
tests pass**: 89 current/gateway/contract checks, 84 prior audit checks and 93 prior
SA/VA checks. The one preparation-only test asserting that no live approval exists
is deselected because approval now exists; the real approval binding and completed
live ledger are verified separately without inference. Ruff lint/format and strict
mypy pass on ten frozen scripts and three new analysis scripts. An initial mypy
module-name collision between the two `verify_local.py` files was corrected by
checking the directories separately; the passing test results were retained without
rerunning unchanged suites. The new summary reader also excludes version request
records when counting completed version observations. Frozen code is unchanged.
Post-run records and the publication closure retain these corrections and final
checks. No production/API/frontend code changed, so unrelated build suites are
outside this change.

Before any more inference, I recommend a bounded **local staged-handoff audit**:

1. Preserve the new SA empty-final capture and SO split-selection/full-field pairs
   as regression fixtures, including both fresh attribution and unavailable-source
   contrasts. Keep delivery failure, known raw usage and successful response distinct.
2. Use the eight existing SO outputs to design a read-only admission handoff that
   carries exact source/report versions, field pointers and complete field context,
   and retains explicit links between selected components. Test truncating that
   context, changing attribution/negation or dropping the obligation as negative
   controls. Do not convert selected allegations directly into repair instructions.
3. Audit assessment workload using these **model-selected sets**, including extras
   and duplicates, rather than substituting the old authored three-target answer
   set. Then decide whether a separately frozen staged-assessment comparison is
   warranted. Any future budget must include selection plus assessment and retain
   failure costs. No next live budget or requests are approved by this report.

Retain human authority over feel, flow, character and story-breaking judgments.
Mechanical binding and counting remain application work; factual premise admission
does not license prose rewrites. No issue is closed, and no production prompt,
writer route or mandatory human checkpoint changes. **Step 19 IN PROGRESS;
Step 20 NOT STARTED; inference PAUSED; full workflow canary ON HOLD.**

Local evidence directories: `data/diagnostics/reviewer-selection-only-v61-2026-11-01/`
and its `-live`, `-inspection`, and `-analysis` siblings. The frozen plan, exact
requests, raw responses, authored notes and decoded results remain available there.
