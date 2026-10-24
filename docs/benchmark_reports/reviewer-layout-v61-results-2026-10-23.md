# DeepSeek C2/D1/D2 delivery comparison results

Date: **2026-10-23**. **COMPLETE: 48/48 calls, zero retries.** Frozen decision:
**`retain_limited_evidence_no_advancement`** for both D1 and D2. Production remains
**prompt 61 / graph 9 / fulfillment policy 1**; the full workflow canary remains
**ON HOLD**.

D1 did not improve delivery. D2 delivered more valid reports and avoided the
observed group-ID duplication pattern, but lost successful C2 controls and did
not meet the required paired recovery rule. Retain that limited D2 observation
and all failure captures; neither candidate is qualified for adoption or a
reviewer-driven writer experiment.

## Approved scope and execution

The user approved the [frozen plan](../handoffs/reviewer-layout-frozen-plan-2026-10-23.md),
including full unpublished fictional prose/context sent to **Ollama Cloud through
the local daemon**, within **48 attempts, sixteen per arm**, with no retries.
The approval record binds plan SHA-256
`4afe9850924396075a722056bafabaaaf089615377b3f2264fdee5f6724dd3f0`.
The public plan retains its historical preparation status; this report records
the subsequent approval and execution.

Preflight and every before/after check matched **Ollama 0.40.9**, the frozen
capabilities, and model `deepseek-v4.1-flash:cloud`, digest
`e04da138d31e0c9468e982e1ae9503d06cb7e170caa16a90c17d931c4aa140f8`.
All 48 requests matched their frozen wire representations. Temperature 0.2,
top-p 0.95, seed 20261022, thinking disabled and streaming disabled remained fixed.
C2 was unchanged; D1 aligned schema property/required presentation; D2 additionally
placed group identity first. No ownership card, semantic prompt change, report
repair or extra judge was introduced.

The twelve-call A00/E-clean sentinel passed with **3/4 valid per arm** and no
blocking repeated signature. Every response completed with **HTTP 200,
done=true, normal stop**; none had a length finish or thinking output. There was
no terminal error, unknown usage, version change, retry or budget transfer.
Normal-stop invalid reports remained failed cells as frozen. Earlier budgets
remain closed, including Gemma D's stop and the three-pilot total of 41 attempts
with seven unavailable slots.

| Accounting | Recorded result |
| --- | ---: |
| Calls / retries | **48 / 0** |
| C2 / D1 / D2 attempts | 16 / 16 / 16 |
| Reported input / output tokens | 263,746 / 43,807 |
| Active inference time | 184.664 seconds |
| Largest input / output | 6,064 / 1,456 tokens |
| Longest attempt | 6.604 seconds |
| Estimate at archived reference rates | **$0.13169220** |
| Actual billed charge | **Unknown** |

All frozen token/time limits held. The cost estimate uses the archived $0.30
input/$1.20 output per million tokens, without discounts; it is not a fresh price
check or a bill. Reservation was $0.80640 against a $1.00 planning allowance.

## Results under unchanged scoring

“Supported target” requires correct task, fact, endpoint and mandatory-aggregate
labels with supported explanations. “Usable” additionally requires correct group
labels, supported premises in every assessment field, and actual contradiction
detection where applicable. Invalid reports receive no semantic credit. Literary
preference is not a prescribed answer.

| Outcome | C2 | D1 | D2 |
| --- | ---: | ---: | ---: |
| Valid reports | **14/16** | **11/16** | **15/16** |
| Fresh valid reports | 7/8 | 6/8 | 8/8 |
| All scored labels correct | 14/16 | 10/16 | 15/16 |
| Supported target judgments | **14/16** | **10/16** | **15/16** |
| Complete usable reports | **11/16** | **7/16** | **12/16** |
| Genuine contradiction detected | 8/8 | 6/8 | 8/8 |
| Supported optional edit recognized | 6/8 | 5/8 | 7/8 |
| OR: valid / target / usable, out of 8 | 8 / 8 / 5 | 5 / 5 / 3 | 7 / 7 / 6 |
| RO: valid / target / usable, out of 8 | 6 / 6 / 6 | 6 / 5 / 4 | 8 / 8 / 6 |

Counts below are **valid / supported target / usable**, out of two orders per arm.

| Case | C2 | D1 | D2 |
| --- | --- | --- | --- |
| A00: lost recognition, forbidden broadcast, permitted departure | 1 / 1 / 0 | 1 / 0 / 0 | 1 / 1 / 1 |
| B10: retained discovery/decision, seam unpicked, duplicate removed | 2 / 2 / 2 | 1 / 1 / 1 | 2 / 2 / 0 |
| CN: panel contradiction outside mandatory retention | 2 / 2 / 2 | 2 / 2 / 2 | 2 / 2 / 2 |
| DB: speaker contradiction explicitly mandatory | 2 / 2 / 2 | 1 / 1 / 1 | 2 / 2 / 2 |
| E-clean: footbridge duplicate cleanup, all required facts retained | 2 / 2 / 2 | 2 / 2 / 2 | 2 / 2 / 2 |
| E-compound: split lost, bridge opened, appointment/cleanup retained | 1 / 1 / 0 | 1 / 1 / 0 | 2 / 2 / 1 |
| F-narrow: crate contradiction outside mandatory retention | 2 / 2 / 1 | 2 / 2 / 1 | 2 / 2 / 2 |
| F-broad: identical prose, consistency explicitly mandatory | 2 / 2 / 2 | 1 / 1 / 0 | 2 / 2 / 2 |

D1 fails both delivery thresholds: **11/16** overall against 15/16, **6/8** fresh
against 7/8. It has **zero** qualifying C2-invalid-to-usable recoveries. It loses
valid C2 reports at A00/OR, B10/RO, DB/OR, E-compound/OR and F-broad/RO, with
additional complete-usability loss at F-broad/OR due to its group-relation label.

D2 meets the delivery thresholds, but has only **one** qualifying recovery,
**A00/RO**, in one family and one order. Its other valid replacement for an
invalid C2 cell, E-compound/RO, has an unsupported comparative premise. D2 loses
the valid, supported-target and optional-success C2 control at **A00/OR** through
invalid delivery, and loses **both usable B10 controls** through unsupported
explanations. Its three total usability gains over C2 do not erase those losses;
only one meets the main recovery definition. The D1/D2 preference rule does not
override a failed primary screen.

Concurrent C2 has only **two invalid cells**, so four qualifying delivery
recoveries were impossible in this run even with a perfect candidate. That is a
frozen-design sensitivity limit, not permission to expand the run or lower its
threshold. The independent control losses also block advancement. Even crediting
every valid report as usable would leave both candidates with valid-C2 losses
and too few eligible recovery cells. The decision therefore does not depend on
the most debatable comparative-language adjudications below.

## Delivery inspection

All **eight invalid captures** were independently inspected and retained without
deduplication, syntax repair, field removal or semantic rescue.

| Failure | C2 | D1 | D2 | Evidence |
| --- | ---: | ---: | ---: | --- |
| Duplicate `group_id` | 2 | 3 | 0 | Five reports; twelve group objects, each with two identical ID values |
| JSON syntax error | 0 | 2 | 0 | Missing opening quote before `evidence`; extra closing array bracket after `endpoint_check` |
| Extra schema fields | 0 | 0 | 1 | Empty `effect_note` in both `craft.voice` and `craft.naturalness` |

The duplicated group objects repeat the previous pattern: `group_id` first, then
assessment/evidence/preservation, then `group_id` again, followed by relation,
support and dependency. D1's aligned lists still place group identity fourth;
merely aligning the lists did not eliminate the model's apparent identity-first
prefix followed by schema-order continuation. D2 is consistent with the narrower
hypothesis that identity-first presentation can avoid that pattern. These small
counts do not prove the internal generation mechanism or universal reliability.

D1 F-broad/RO fails parsing at character **363** of 4,052; E-compound/OR at
**1,883** of 5,474. Both continue to a closing overall assessment and have normal
stop metadata. D2 A00/OR is syntactically parseable but violates the closed object
schema twice. An empty extra field is still invalid. None of these failures
supports an outage, exhausted output allowance or truncation diagnosis.

The earlier stopped Gemma D pilot's four valid D1 reports did not establish that
D1 would solve DeepSeek delivery. Historical comparisons also cross daemon
versions; this run's concurrent C2/D1/D2 cells all used 0.40.9.

## Semantic findings and limits

**Scope works on these valid reports.** All **40/40** valid model mandatory flags
match the frozen cases and the separate application-owned aggregate. All **22/22**
valid contradiction reports identify both mutually exclusive assertions. Narrow
CN/F reports keep those defects outside mandatory retention; broad DB/F reports
include consistency explicitly. All **18/18** valid optional-edit cases recognize
the independent cleanup or permitted departure. Invalid cells remain failures
in the scheduled denominators.

The prior C2/M1 CN control failures therefore did not recur here, even without
the ownership card. Preserve the historical both-order M1 result, but do not
treat it as proof that the card is necessary or that scope is now solved. The
application aggregate corrects no flag in this run and does not establish the
truth of task explanations, group judgments or craft premises.

**Nine valid reports fail factual-support inspection; a tenth fails a group
label.** These are distinct from delivery and from disagreements about taste:

- **C2 A00/OR:** naturalness says broadcasting contradicts the decision to ask
  the brother tomorrow. The explicit endpoint prohibits broadcast; a deferred
  conversation does not independently prohibit intervening action.
- **D1 A00/RO:** the task explanation invents an unidentified voice replacing
  the mother's humming. The revision supplies tape hiss and no identifying
  information, not an asserted unidentified voice. Its labels are correct but
  its target explanation is not fully supported.
- **D2 B10, both orders:** craft explanations invent consultation before deciding
  or acting. The prose says before **explaining** what Tomas thinks should happen.
  RO additionally describes him as destroying the garment; the captured action
  establishes shoulder-seam unpicking, not destruction of the whole coat. The
  actual unaltered-endpoint violation remains correctly identified.
- **E-compound: C2/OR, D1/RO, D2/RO:** comparative explanations treat a smooth plank
  or crossing as inconsistent with the carpenter appointment or inspection
  rationale. The complete source explicitly retains routine post-flood inspection
  as due anyway, with the carpenter's knowledge of older timber. Losing a hazard
  can weaken tension; it does not remove that independent rationale or make an
  appointment prohibit earlier crossing. D2/OR acknowledges that surviving reason
  and receives support credit under the sealed inspection.
- **F-narrow: C2/OR and D1/OR:** both correctly detect the two/three contradiction
  but call the earlier sentence or claim **identical** to the added one in their
  naturalness explanation. The claims are incompatible, not identical. These
  narrow wording failures do not mean the story feels different to a reader or
  that the contradiction went unnoticed.
- **D1 F-broad/OR:** the group rationale correctly describes a newly introduced
  contradiction, but `request_relation=direct` fails the frozen `unrelated` label.
  Adding the defect is not performing the requested consistency repair. Every
  assessment field is supported; the separate label still prevents full usability.

The masked notes distinguish categorical invented facts from literary readings.
Reduced tension, a less grounded decision, an abrupt action, or a harsher tone
are not automatically false. Disjunctive “creates or compounds” wording in two
DB reports is not treated as a categorical assertion of a pre-existing defect:
the edit does create it, and the surrounding explanation identifies the addition.
The original unchanged DB historical failure remains scored as before.

These are assistant source audits, not independent human judgments. Complete
usability is deliberately stricter than a correct verdict or a satisfactory
reading experience. The nine earlier human ties remain untouched; none of the
results establishes improved story quality or harm from a small textual change.

## Verification and evidence

All 48 receipts, exact requests, source identities and runtime checks replay.
The shuffled export hid arm and display order. All **40 valid reports**, covering
**487 exact assessment-field claims**, were inspected against complete prose and
context. **Eleven claims in nine reports** are marked unsupported; none uncertain.
Every claim has source/version/offset evidence. Notes were sealed before decoding
the arm/order key; wording could still reveal condition. Invalid reports received
a separate structural audit with no semantic credit.

**20 post-run offline tests pass**, with HTTP blocked: exact schedule/ceilings,
runtime and wire identity, sentinel, all eight invalid replays, full claim
coverage, inspection/raw-capture tamper rejection, independent structural details,
scope/optional controls, conditional aggregation and exact decision replay.
Ruff lint/format and strict mypy pass on all three analysis scripts.

The first pytest run had fifteen passes and two setup errors because the Windows
sandbox's default temporary directory could not create a numbered directory.
The completed run used a new explicit repository-local temporary directory.
Strict mypy initially required a local list annotation; that annotation was added.
Initial and final verification records are preserved. No frozen harness, scoring,
capture or sealed note changed. The prior **138-test preparation** record remains
intact. Production/frontend source did not change, so unrelated application
suites and the frontend build were not repeated.

- [Frozen preparation](../../data/diagnostics/reviewer-layout-v61-2026-10-23/):
  plan, exact cases/requests, labels, source/runtime fingerprints and approval.
- [Raw execution](../../data/diagnostics/reviewer-layout-v61-2026-10-23-live/):
  48 reservations, wire requests, raw responses, receipts, version checks and
  per-cell seals, plus preflight and sentinel.
- [Inspection and analysis](../../data/diagnostics/reviewer-layout-v61-2026-10-23-analysis/):
  masked export, operator observations, 487-claim notes and seals, inspection
  timeline, decision/results, invalid audit, capture details, execution manifest,
  tests, verification and analysis manifest. Full prose/captures remain ignored
  local data, outside tracked documentation.

Execution manifest SHA-256 (435 files):
`9354d23ca73b7a45230b616cb93d6011c19d69cf6ef28f43fdae9449121a8a55`.
Inspection notes SHA-256:
`66970110349bdcef6f15d254c9050ad52a5c713540a14946b73a6256b34cd72e`.
The tracker records the final analysis seal. All fourteen user-posted GitHub
links and original issue bodies remain intact; no external issue was changed.

Offline replay from the repository root:

```powershell
.venv/Scripts/python.exe -X utf8 data/diagnostics/reviewer-layout-v61-2026-10-23/layout_experiment.py verify
.venv/Scripts/python.exe -X utf8 -m pytest data/diagnostics/reviewer-layout-v61-2026-10-23-analysis/test_execution.py -q
```

If the default Windows test temporary directory is unavailable, use a fresh
repository-local `--basetemp` path; never point it at an evidence directory.

## Recommended next decisions

1. Retain D2's absence of observed ID duplication as **limited component evidence**,
   not a qualified candidate. Keep the failed D1 and extra-field/syntax captures;
   all eight now have local replay coverage. Keep strict validation unchanged.
2. Before more inference, separate local delivery work from explanation quality.
   Inspect why a closed craft object acquires `effect_note`; retain the explicit
   syntax and duplicated-ID fixtures. Do not silently accept extra fields or
   deduplicate keys to manufacture a delivery gain.
3. Extend the local semantic contrast set around actual versus invented timing,
   retained independent motivations, absent sensory events, and identical versus
   incompatible assertions. Preserve correct endpoint labels and successful
   optional cleanup as controls. Distinguish an unsupported premise from a
   reasonable opinion about emotional force; a correct aggregate cannot do that.
4. Propose any further live test only after those local checks, with a stated
   question and a design that acknowledges the limited number of failing C2
   controls. Do not recycle the 48-call budget or relax this completed screen.
   No additional inference or writer experiment is authorized by this report.

Eight cases in **six family clusters**, at one seed and short scene length, are
not 48 independent stories. Future human assessment should continue to emphasize
feel/emotion, flow, character and story-breaking details, with mechanical evidence
prepared by machines. **Step 19 remains IN PROGRESS; Step 20 NOT STARTED; the
canary remains ON HOLD.**
