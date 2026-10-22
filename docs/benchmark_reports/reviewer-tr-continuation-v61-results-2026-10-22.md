# T/R reviewer continuation results, 2026-10-22

**The approved continuation completed 31 new calls, reaching 41 combined attempts
within the original 48-call ceiling. Neither comparison advances under its frozen
rule.** D remains stopped. There were no new HTTP failures or length finishes;
30 new reports were strictly valid and one was invalid JSON.

T1 produced **4/8 usable reports versus C2's 3/8**, but lost successful controls
and did not improve both presentation orders of any family. R1 corrected the
fulfillment vocabulary on the journal case in both orders, but failed the same
endpoint distinction as its controls. R1 and C2 each produced **5/8 usable reports**.
Retain R1's narrower classification gain as diagnostic evidence; neither candidate
is qualified for production or broader diagnostic advancement by this run.

Production remains **prompt 61 / graph 9 / fulfillment policy 1**. Production
prompts, schemas, routing and human checkpoints are unchanged. The full workflow
canary is **ON HOLD**; Step 19 remains **IN PROGRESS**, Step 20 **NOT STARTED**.

## Authorization, accounting and execution

The user approved the [frozen continuation](../handoffs/reviewer-tr-continuation-frozen-plan-2026-10-22.md),
including full unpublished prose/context to Ollama Cloud through the local daemon,
against preparation seal:

`1372bb40e4ccb75fb746ca4e888d007b68bdc8d4d49095a3fd138ba2fe9ac201`.

All ten [previous attempts](reviewer-isolated-pilots-v61-results-2026-10-22.md)
remain charged. The first new call was the one authorized exact recovery of
`T-h04-C2-RO`. It succeeded. Its first HTTP-500 attempt remains a separate failed
delivery with unknown usage; its original reservation and terminal evidence were
not rewritten. The completed `T-h04-T1-RO` response and its unsupported inspection
were carried unchanged and were never rerun.

| Pilot | Prior attempts | New attempts | Combined attempts | Completed logical cells |
| --- | ---: | ---: | ---: | ---: |
| D: Gemma C2/D1 | 8 | 0 | 8 | 8/16; stopped |
| T: DeepSeek C2/T1 | 2 | 15 | 17 | 16/16 |
| R: DeepSeek C2/R1 | 0 | 16 | 16 | 16/16 |
| **Total** | **10** | **31** | **41** | **40 completed responses, plus one historical HTTP failure** |

T's explicit 17-attempt subcap includes nine C2 attempts yielding eight responses
and eight T1 attempts yielding eight responses. This was the sole authorized
exception to the original per-pilot allocation. No further retry, repair,
replacement, fallback, writer call or warm-up inference occurred. D's eight
unstarted cells remain unstarted; the seven unallocated original slots are not
permission for further calls.

Preflight observed daemon **0.40.8** and matched the original DeepSeek digest and
capability/thinking metadata. Version checks before and after all 31 calls
matched, as did per-call model checks. All sent requests exactly match the frozen
payloads. Settings stayed at temperature 0.2, top-p 0.95, seed 20261022,
`think:false`, 32,000 context, 24,000 input reservation, 8,000 output limit and
300 active inference seconds per attempt.

Both eight-cell sentinels continued: T had C2 **4/4** and T1 **4/4** valid reports;
R had C2 **4/4** and R1 **4/4**. The later invalid T control did not retrospectively
change its checkpoint or trigger an unplanned retry. No new terminal condition
occurred. Successful execution now does not identify the cause of the earlier
HTTP 500; update interference, remote availability and other explanations remain
unconfirmed for that historical failure.

## Delivery, labels and supported usability

Denominators below are the eight planned logical responses per arm. T includes
the carried T1 and recovered C2 response; the additional failed C2 attempt has no
semantic score. Usability requires strict delivery, every frozen label correct
and support for every consequential task/group/comparative explanation.

| Pilot / arm | Strictly valid | All frozen labels correct | Supported usable |
| --- | ---: | ---: | ---: |
| T / C2 | 7/8 | 3/8 | 3/8 |
| T / T1 | 8/8 | 5/8 | 4/8 |
| R / C2 | 8/8 | 6/8 | 5/8 |
| R / R1 | 8/8 | 6/8 | 5/8 |

D's historical result remains C2 **0/4 valid** versus D1 **4/4 valid, correct and
supported**, on only half the planned cells. It remains incomplete and unqualified.

### T: gains and losses depend on order

| Family | OR: C2 / T1 usable | RO: C2 / T1 usable | Finding |
| --- | --- | --- | --- |
| h04 safehouse | No / Yes | Yes / No | T1 fixes event retention in OR; carried RO T1 keeps a false contradiction premise |
| F02 tram | Yes / No | No / Yes | Both recognize the real simultaneous contradiction; mandatory-scope mistakes switch arms with order |
| h03 journal | No / No | No / No | All four reports wrongly fail the retained endpoint because the earlier date event was removed |
| F01 observatory | No / Yes | Yes / Yes | OR control is invalid JSON; the three valid reports accept the permitted departure |

On h04/OR, C2 says the later exit dissolves the previously formed truce, marking
the outcome lost. T1 correctly retains that event while rejecting the final
departure against the locked-room endpoint. On h04/RO, the recovered C2 makes
the correct distinction, while the carried T1 still incorrectly calls earlier
staying and subsequent leaving a contradiction. The source explicitly sequences
remaining, unlocking and leaving. The wrong endpoint and an unsupported logical
contradiction are different claims.

On F02, **all four** reports identify the same tram as both motionless and moving
at the same instant. All retain the discovery, decision to ask dispatch and
pre-contact endpoint. Nevertheless, C2/RO and T1/OR mark `mandatory_failure:true`,
even while explaining that the assigned retention task is met. The frozen task
expressly excludes the separate motion defect from its acceptance criteria.
The failure is in assigning severity/scope, not in noticing the contradiction.

On h03, both arms correctly find that the future-date realization is deleted and
the handwriting-check decision remains. They also acknowledge the unsettled,
no-match ending. Yet all four broaden the endpoint to include the earlier
turning point and mark it violated. T1's explicit temporal instruction does not
prevent this attribution error. T1/RO additionally calls the dependent callback's
edit support uncertain; recognizing its unsupported parent does not make that
uncertainty a successful authorization judgment.

Thus T1 meets delivery and permissible-control requirements, but loses two paired
usable controls and has no family with target improvement in both orders.
The frozen decision is **`retain_limited_evidence_no_advancement`**.

### R: a useful vocabulary result, with no complete-report recovery

| Family | C2 usable | R1 usable | Finding |
| --- | ---: | ---: | --- |
| n03 seed store | 1/2 | 1/2 | Correct labels in both orders; each RO report adds a different unsupported comparative premise |
| F05 bakery | 2/2 | 2/2 | Both accept the legitimate duplicate cleanup and preserve facts/endpoint |
| h03 journal | 0/2 | 0/2 | R1 fixes fulfillment labels in both orders, but both arms retain the wrong endpoint verdict |
| F06 ferry | 2/2 | 2/2 | Both separate optional duplicate repair, required fact loss and unsupported dependent callback |

On h03, C2 labels the deletion of the required date realization `direct`, while
also correctly calling the edit unsupported. That mixes relevance to the task
with fulfillment of it. R1 labels it `does_not_fulfill` in both orders, which
normalizes to the frozen `unrelated` category only after strict validation. The
dependent callback remains `supports_other_edit` / `on_unsupported_change` and
unsupported. **Group labels are correct in 8/8 R1 reports versus 6/8 C2 reports.**
This is a specific classification improvement, not a gain in overall usability:
both R1 h03 reports still misclassify the separately satisfied endpoint.

Across T and R together, **all eight h03 reports** make that endpoint error.
Correctly noticing a required-event loss is not sufficient if the report assigns
the failure to every adjacent requirement.

On n03, all four reports correctly identify the lost cooperation agreement while
preserving the discovery and closed-case, in-store ending. The RO C2 report then
calls refusal unmotivated by anything earlier, despite the conflicting custody
promises and explicit memory of past blame. RO R1 says the refusal conflicts with
the planned endpoint in its naturalness assessment, despite its correct endpoint
field and the intact physical ending. These are source/scope errors, not a demand
that every reader share one aesthetic preference.

F05 and F06 supply useful positive controls. Both interfaces handle duplicate
removal; in F06 they independently credit that cleanup while rejecting the
expired-to-valid permit change and its dependent callback. They do not erase
Oren's retained decision or falsely fail his counter/pre-boarding endpoint.
The h03 difficulty therefore does not demonstrate a universal inability to
separate event and endpoint. Context, familiarity and report aggregation remain
plausible factors requiring isolation.

R1 meets delivery, paired-control preservation and permissible-control checks,
but has no family with complete usable target improvement in both orders.
The frozen decision is **`retain_limited_evidence_no_advancement`**.

## The one invalid response

`T-F01-C2-OR` returned HTTP 200, `done:true`, `done_reason:stop`, no thinking
content, **3,233 input / 860 output tokens**. Its 4,165-character answer fails JSON
parsing at the end. The root is unclosed, and six required root fields follow
`naturalness` inside the `craft` object instead of at the root.

An offline diagnostic temporarily appended one closing brace in memory solely to
inspect key/value pairs. That inspection exposed root keys `task_checks`,
`fact_checks`, `craft`, with six misplaced fields inside `craft`. It did not
produce a scored or accepted repair; the capture, receipt and invalid status are
unchanged. This is neither a duplicate-key capture nor a provider-reported
length finish. It is further evidence that C2 delivery can fail through distinct
structural mechanisms. No inference repair was attempted.

## Inspection, usage and verification

All 31 new exports were read; all 30 valid assessments were checked against the
complete source passages and supplied context. Notes contain exact claim fields,
source references, offsets, version IDs, counterevidence and uncertainty. The notes
were sealed before opening the new arm/order key. Interface wording can reveal
conditions, and the carried T1 was already unmasked: this is masked operator
inspection, not independent human blind preference evidence. Invalid output was
not rescued or given semantic success credit.

Debatable craft judgments were not rejected merely for differing from a preferred
reading. For example, removal of a numerical discovery can support a local
tension/voice concern while other motives for dread remain; a valid permit can
still require attention even if the revision weakens its explicit motivation.
The notes distinguish those readings from categorical errors such as equating an
undated card with a blank reverse or calling a future warning incoherent merely
because it lacks an inscribed date. None of these judgments substitutes for human
feel/emotion, flow, character or story-breaking review.

| Usage | New continuation | Combined known usage across 40 completed responses |
| --- | ---: | ---: |
| Input tokens | 208,787 | 295,988 |
| Output tokens | 29,417 | 37,154 |
| Active inference seconds | 140.616 | 175.716 |
| Estimate using archived reference rates | $0.09793650 | $0.11631656 |

These are observed token/time totals and reference-rate estimates, not actual
billing. Aggregate actual usage and cost remain unknown because the original
HTTP-500 attempt has no accepted usage record. Its full reservation remains
charged. The continuation's $0.52080 reference-rate reservation and combined
$0.60688 reservation were not exceeded by known usage; neither is an enforceable
provider billing cap.

**Nine post-run offline tests pass**, along with Ruff lint/format and strict mypy
on four analysis scripts. They verify source and approval seals, all exact wire
requests, the single recovery, 41-attempt accounting, model/version/usage checks,
both sentinels, source-bound notes, tamper rejection, invalid-report preservation
and reproducible frozen decisions. The preparation's **93 passing checks** remain
sealed; no preparation or production code changed. Application-wide build checks
were not repeated for this diagnostic execution/documentation work.

Private evidence:

- [Execution ledger](../../data/diagnostics/reviewer-tr-continuation-v61-2026-10-22-live/),
  including raw captures, immutable reservations, receipts and sentinel decisions.
- [Results](../../data/diagnostics/reviewer-tr-continuation-v61-2026-10-22-analysis/results.json),
  [inspection notes](../../data/diagnostics/reviewer-tr-continuation-v61-2026-10-22-analysis/inspection/notes.json),
  [invalid-response audit](../../data/diagnostics/reviewer-tr-continuation-v61-2026-10-22-analysis/invalid-response-audit.json)
  and [verification](../../data/diagnostics/reviewer-tr-continuation-v61-2026-10-22-analysis/verification.json).

Execution manifest SHA-256:
`0f1dd72cda2767af82ec1814de1ff89dc8a6d6eece1ae83acf9be3855451d546`.
Inspection seal SHA-256:
`1f8004b1e861b7ce34fe6d9fab806acda39b6efb9d1ebd72c53bca920d3d4c66`.
The final analysis manifest binds this report and all analysis artifacts; its
digest is recorded in the tracker. Detailed prose and captures remain local and
ignored by Git.

## What to retain and what to investigate next

Retain **R1's h03 fulfillment-label correction** as promising diagnostic evidence,
and retain **T1's mixed, order-dependent behavior** without treating the 4/8 versus
3/8 total as reliable superiority. D1's earlier limited delivery evidence and
all original failures remain available. No critic/writer issue is closed.

Before proposing more inference, the useful local work is to make this run's
attribution failures and malformed C2 capture regression fixtures. In particular,
separate the model's evidence finding from its assignment to an earlier event,
final state, mandatory test or optional craft concern, then inspect how those
findings become an aggregate failure. A later bounded proposal should isolate
that mapping/aggregation problem with unchanged controls, genuinely new families
and both orders, rather than combining further vocabulary and temporal changes
and assuming their individual gains will compose. No such prompt change or new
experiment is implemented or authorized here.

The comparison has one seed, small family counts and shared historical material.
The h03 C2 requests recur across the two pilots; these are repeated observations
of the same case, not independent stories. The recovered h04/RO pair spans the
interruption and carries an earlier T1 response; the daemon version is only
verified for the continuation phase. Tags, digests and seeds do not prove
immutable remote weights or independence. These limits constrain causal and
generalization claims.

Preserve the nine human ties. Better report labels, fewer edits or a valid JSON
object do not establish a better story. The next story-quality phase still needs
meaningfully varied material and human judgments of the overall reading
experience, with mechanical evidence prepared by machines. The canary remains
**ON HOLD**.
