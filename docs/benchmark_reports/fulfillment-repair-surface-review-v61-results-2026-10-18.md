# Review correction and comparative assessment: bounded results

Date: 2026-10-18. **STOPPED AT 41/96 CALLS: A COMPLETE; B PARTIAL.**

Restricted critic edits improved qualified recovery on the fixed failed reports,
but failed the complete preservation/control requirement. The comparative assessor
produced no valid report in the eight completed review slots. Its next call copied
input material until it reached the output limit, triggering the frozen terminal
stop. Neither candidate is qualified for production. Unreached controls remain
unanswered; they are not scored as model failures or successes.

Production remains prompt **61**, graph **9**, fulfillment policy **1**.
**Full workflow canary: ON HOLD; NOT STARTED.**

## Scope and terminal accounting

The user approved the [frozen 96-call plan](fulfillment-repair-surface-review-v61-plan-2026-10-18.md),
including full unpublished prose/context sent to Ollama Cloud through the local
daemon. The exact approval is recorded against the plan hash. The plan document
retains its historical preparation status; this report records the subsequent run.

- Plan SHA-256:
  `9793f119f39c64ba2cd92f869f1d356240dfc8da7c8cf7b2a4184e79c12d9c86`.
- Preparation closure SHA-256:
  `6be9189492c415c56e741e2de7b55f2f48845ec3bdd745972cc497a1d6e967ba`.
- Model: `gemma4:31b-cloud`; preflight and both phase checks confirmed Cloud
  deployment and digest
  `c382fbfbc73b6fdd08c8549c23caedc6e62eb09933c65a1fb82dbf3398320a4e`.

Both arms used temperature 0.2, top-p 0.95 and thinking disabled. A completed both
seeds, 19701/19703, with the frozen reversed ordering. B reached only the beginning
of seed 19701. Cases, requests, validators, scoring and budgets were unchanged.
There were no new writer calls, semantic rerolls, transport retries or replacements.

| Block | Primary slots completed | Other primary slots | Calls | Valid final reports |
| --- | ---: | --- | ---: | ---: |
| A: full report F0 / restricted edits F1 | 24 / 24 | None | 24 / 24 | 17 / 24 |
| B: purposes hidden V0 / visible V1 | 8 / 36 | 1 truncated; 27 unstarted | 17 / 72 | 0 / 8 completed |
| **Total** | **32 / 60** | **1 truncated; 27 unstarted** | **41 / 96** | **17 / 32 completed** |

B completed b01-b04 in both arms at seed 19701. All eight required their one
structural correction and remained invalid. Call 41 was
`s19701-b05-review-V0-attempt-1`, the minimal separate-entry repair control. It
returned `finish_reason=length` at **8,000 output tokens**, after emitting copied
input fields, prose and catalogs instead of a completed assessment. The frozen
operator stopped before validation or retry. Its raw capture and incomplete probe
remain intact; no successful receipt or phase-complete marker was manufactured.

The **55 unused calls** do not permit continuation after this terminal stop.
The 27 unstarted primaries are b05/V1 and b06-b09/both arms at 19701, plus all 18
reviews at 19703. These are not conditional skips and no skip records were invented.
B's no-op tests, embedded minimal repair and synthetic within-cited-sentence control
were not reached. The truncated minimal control has no scorable assessment.

Observed usage was **780,033 input tokens, 64,892 output tokens and 235.33 active
seconds**, including the truncated call. Maximum observed per attempt was 22,654
input tokens, 8,000 output tokens and 37.60 active seconds. No allowance was exceeded
or transferred; reaching the output cap with a non-stop completion nevertheless
requires stopping. Historical October 8 rate estimate: **USD 0.13516142**. Actual
billed charges are unknown. Three model-discovery checks are separate from inference.

The terminal outcome record has null token fields because the integrity exception
does not carry usage. Its already-persisted model capture contains **15,183 input /
8,000 output tokens**. Offline reconciliation counts those exactly once and binds
the capture and outcome hashes. The original outcome is unchanged; null is not
interpreted as zero or an unknown invocation.

## A: better recovery, but neither complete coverage nor control preservation

Both arms received the same exact parent, full original context, ordinary review
semantics and diagnosed scope. F0 emitted a complete report; F1 emitted restricted
operations applied atomically to that parent. Parent visibility is common to both,
so these results do not isolate its effect or compare against unchanged production R1.

| Measurement | F0 | F1 |
| --- | ---: | ---: |
| Structurally valid failed-parent corrections | 4 / 8 | 8 / 8 |
| **Qualified failed-parent recoveries** | **4 / 8** | **6 / 8** |
| Valid, preserved native controls | 3 / 4 | 2 / 4 |
| Structurally valid total | 7 / 12 | 10 / 12 |
| Qualified total, including controls | 7 / 12 | 8 / 12 |

F1 adds two qualified failed-parent recoveries and no failed-parent loss, but loses
both compound controls. Across all 12 pairs it has **3 qualified wins, 2 losses and
7 ties**: two repair wins, one identity-control win, and two identity-control losses.
The frozen criterion requires all eight repairs, all four controls and no paired
loss. **F1 fails it.** A structural gain must not be counted as a supported explanation.

| Case | F0, across both seeds | F1, across both seeds |
| --- | --- | --- |
| a01: missing comparison coverage | Leaves the comparison reference empty; both invalid | Adds the boundary reference, but replaces the craft comparison with an explanation solely about entry; both valid but unqualified |
| a02: linked recommendation | Nulls only the diagnosed recommendation; both qualified | Same narrow repair; both qualified |
| a03: ownership plus masked comparison | Removes the condition but miscopies the parent hash and still omits comparison coverage; both invalid | Removes the application-owned condition and explains the distinct duplicate; both qualified |
| a04: ownership after correct comparison | Removes only the forbidden condition; both qualified | Same narrow repair; both qualified |
| a05: valid missing-decision control | One exact identity; one changes an assessment outside scope | Both empty edit lists; exact parent preserved |
| a06: valid compound control | Both exact identities | Both emit empty edits plus ordinary report fields at top level; invalid |

In a01, F1's replacement accurately describes the boundary breach but never explains
the repeated sentence that survives removing entry. The duplicate finding itself
remains present and minor; its comparison is inadequate. This is a semantic loss
inside an allowed correction location, despite preserved surrounding fields.

In a03, the seed-19701 explanation states the converse counterfactual—removing the
duplicate does not fix entry—while explicitly identifying the independent mechanical
repetition. The full text supports that distinction. The other seed explicitly
says repetition remains whether the scene stops at the threshold or enters.

F0's a05 change merely substitutes “The assigned outcome requires” for “The outcome
requires.” It does not reverse the judgment, but violates the frozen identity task.
F1's a06 failures likewise do not show loss of the native repair: they copy the parent
into forbidden extra fields. These are output-contract failures, not evidence that
the model newly misunderstood the underlying story.

All accepted corrections preserve out-of-scope values exactly. Narrow native
conditions remain supported. The compound parent's known warning-acceptance
overclaim remains a documented inherited caveat, neither a newly introduced error
nor certified truth. No invalid response was silently stripped, reclassified or
repaired by the operator. These fixed challenges estimate neither natural error
rates nor improved critic noticing.

## B: no usable assessments; limited raw comparative evidence

The eight completed slots comprise **16 invalid responses**: eight initial attempts
and eight structural corrections, with **zero recoveries**. At both attempts, four
slots fail first on duplicate JSON keys and four fail on missing required fields.
The latter use input-style `changed_units` instead of output `change_assessments`.

Full raw inspection also finds overlapping defects hidden behind those first errors:

- **14/16** responses contain at least one quote/ref/version mismatch, often a
  sentence fragment where the contract requires the exact complete catalog entry.
  Some combine text from multiple entries. These are binding errors, not all
  fabricated story facts.
- **13/16** leave the mandatory-failure explanation null or empty.
- Three hidden-purpose responses invent purpose records despite receiving no claims.
- One initial response repeats `fact_checks` with conflicting values: substantive
  records first, then an empty array. It has no unambiguous structured fact result.

Operator-only inspection exposes duplicate values rather than accepting permissive
JSON decoding as a repair. Every original response remains invalid. The four
parseable parents retain **95 valid semantic leaves** across their corrections,
with zero drift. The four duplicate-key parents are unparseable under the frozen
decoder and retain none. Change judgments under the wrong field name also cannot
be retained by the frozen identity map. For example, b03/V1's punctuation label
changes from optional to required-adjacent. This is a limitation of the planned
retention surface, not a reason to accept the output or alter it during execution.

The following observations concern raw text only, at the one reached seed:

| Pair | Purposes hidden, V0 | Purposes visible, V1 |
| --- | --- | --- |
| b01: adjacent preparation deletion | Identifies the deletion as optional craft | Calls it required and endorses the unsupported claim that preparation implies entry already in progress |
| b02: mixed ending rewrite | Recognizes optional physiological/metaphorical changes, but treats preservation as neutral and declares improvement | Also misses the concrete tradeoff; supports the necessity claim by praising tension rather than establishing necessity |
| b03: embedded repair plus image | Labels pieces of the optional threshold image as direct repair | Same conflation; supports the whole purpose without qualifying added imagery |
| b04: duplicate removal | Correctly recognizes repair and retained facts | Agrees; the direct repair purpose is supported |

All eight final raw texts correctly describe task completion and retention of the
assigned turning point/outcome, and invent no mandatory failure on these repaired
cases. They nevertheless are invalid reports. Those observations cannot establish
that the reviewer detects an unrepaired defect: neither no-op was reached.

The b01 pair contains **one observed unsupported necessity upgrade** with visible
purposes. b02 and b03 add unsupported purpose endorsements without a demonstrated
relative preservation benefit. No supported improvement over V0, new factual miss
or invented hard failure was found in these four reached raw pairs. The other 14
planned pairs are unavailable, including the reverse-order seed. This is limited
diagnostic evidence, not a full estimate of explanation influence.

Both arms call every reached revision better. In b02 they notice the move from
equipment preparation to heartbeat/daylight imagery, but do not acknowledge the
loss of the explicit strap contingency and terminal outside state as a tradeoff.
Possible emotional or agency gains remain plausible; they do not prove preservation.
In b03, deleting entry does not require the chosen threshold image. Treating the new
imagery and physiology as neutral leaves these necessity/meaning distinctions and
all validity failures unchanged. It does not settle human literary preference.

**V0's success criterion is not demonstrated.** Its reached cells already fail
validity, its mixed-case and necessity distinctions are inadequate, and the crucial
negative and within-cited-sentence controls are unrun. V1 is not substituted as the
primary candidate. No comparative reviewer or self-approval loop is installed.

## Decisions, verification and remaining work

Retain F1's two additional qualified failed-parent recoveries as narrow diagnostic
evidence, alongside its two unsupported comparisons and two control failures.
Retain the raw b01 purpose-influence observation and b04 craft recognition with their
invalid-output and single-seed limitations. Do not promote either experiment into
production. J1/P1 remain diagnostic evidence, E1 remains preservation-unqualified,
and W1's earlier limited gains remain separate historical findings.

Full original/revision prose for all nine frozen pairs was inspected: their common
3,900-character body is identical, and every differing tail, exact alignment, claim
and source was checked. The nine anonymous pairs remain exported with an empty,
**PENDING** human review sheet. Exporting or inspecting an unreached case is not a
new model result. Future story-quality qualification still requires independent
human review, the accepted weighted rubric/hard gates, the full intended Cloud
corpus and a comparable baseline. This run adds no mandatory human checkpoint.

Private evidence is under
`data/diagnostics/fulfillment-repair-surface-review-v61-2026-10-18-live/`:
all requests/reservations/outcomes/captures, 40 completed-attempt replays, the retained
terminal capture, 60-slot partial reconciliation, per-attempt raw inspection,
operator A/B judgments, full-prose exports, verification and closure. The terminal
probe remains incomplete and the remaining 27 slots explicitly unrun.

Offline verification rechecks the frozen plan, preparation/source seals and all
151 code dependencies; reconstructs every dispatched request; reconciles all 41
calls and usage; reproduces operator summaries; and checks the report, tracker,
exports and private helpers. It makes no new discovery or inference calls. The
preparation's 75 focused regressions and strict mypy remain applicable to unchanged
production code; no production/client changes require rerunning their suites.

Further execution requires a separately reviewed plan addressing the observed
terminal/output-contract failures; this report authorizes no changes or calls.
**Step 19 IN PROGRESS; Step 20 NOT STARTED; canary ON HOLD.**
