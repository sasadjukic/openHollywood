# C2/M1 requirement-ownership comparison results

Date: **2026-10-23**. **COMPLETE: 48/48 calls, no retries.** Frozen decision:
**`retain_limited_evidence_no_advancement`**. Production remains **prompt 61 /
graph 9 / fulfillment policy 1**; the full workflow canary remains **ON HOLD**.

M1 recovered one mandatory-scope contrast in both presentation orders while still
identifying the real prose contradiction. It did not pass the frozen screen:
delivery was below threshold, successful controls were lost, and there was no
event/endpoint recovery. Retain the narrow scope result as diagnostic evidence;
do not promote M1 or claim improved story quality.

## Approved scope and execution

The user approved the [frozen C2/M1 plan](../handoffs/reviewer-ownership-frozen-plan-2026-10-23.md),
including full unpublished prose/context sent to **Ollama Cloud through the local
daemon**, at most **48 attempts, 24 per arm**, with zero retries. Approval was
recorded against plan SHA-256
`d5d71fb62ccbe39ec1dad871fbfc9b44f9a3ade09e63d87521d33769105b091d`
before preflight or inference.

The model was `deepseek-v4.1-flash:cloud`. Preflight and per-call checks matched
daemon **0.40.8**, the frozen capabilities and model digest
`e04da138d31e0c9468e982e1ae9503d06cb7e170caa16a90c17d931c4aa140f8`.
All 48 dispatched requests matched their frozen wire representations. Settings,
source versions, cards, cases, scoring and stop rules stayed unchanged.

Both arms passed the eight-call A01/CN sentinel with **4/4 valid** each. Later
normal-stop invalid responses remained failed cells, as the plan requires; no
terminal stop, retry, replacement, structural repair or extra judge was used.
Every response was **HTTP 200, done=true, normal stop**, with no thinking output
or length finish. All token and time limits held. The earlier three-pilot budget
remains separate: **41 attempts, D stopped, seven unused slots unavailable**.

| Accounting | Recorded result |
| --- | ---: |
| Calls / retries | 48 / 0 |
| C2 / M1 attempts | 24 / 24 |
| Reported input tokens | 265,282 |
| Reported output tokens | 49,109 |
| Active inference time | 208.036 seconds |
| Largest input / output | 6,390 / 1,391 tokens |
| Longest attempt | 14.461 seconds |
| Estimate at archived reference rates | **$0.13851540** |
| Actual billed charge | **Unknown** |

The estimate uses the frozen October 22 rates of $0.30 input and $1.20 output per
million tokens, without cache/off-peak discounts. It is not a new price check or
a bill. The frozen reservation was $0.80640, with a $1.00 planning allowance.

## Results under unchanged scoring

“Target correct” requires correct fact, endpoint, task and mandatory-aggregate
labels with supported explanations. “Usable” additionally requires correct group
labels, supported group/comparative premises and explicit detection of the real
C/D contradictions. Invalid reports receive no semantic credit.

| Outcome | C2 control | M1 ownership card |
| --- | ---: | ---: |
| Scheduled attempts | 24 | 24 |
| Valid reports | **16/24** | **19/24** |
| All scored labels correct | 14/24 | 19/24 |
| Supported target judgment | **14/24** | **19/24** |
| Complete usable report | **12/24** | **15/24** |
| C/D contradiction identified with both assertions | 7/8 | 8/8 |
| OR: valid / target / usable, out of 12 | 9 / 8 / 6 | 10 / 10 / 8 |
| RO: valid / target / usable, out of 12 | 7 / 6 / 6 | 9 / 9 / 7 |

Counts below are **valid / target / usable**, each out of two display orders.
A/B digits mean earlier event retained (1) or lost (0), then endpoint satisfied
(1) or violated (0). N/B mean narrow/broader mandatory scope.

| Case | C2 | M1 | Interpretation |
| --- | --- | --- | --- |
| A11: recognition and unbroadcast endpoint retained | 2 / 2 / 2 | 2 / 2 / 2 | Permitted departure remains supported |
| A10: recognition retained, broadcast violates endpoint | 0 / 0 / 0 | 2 / 2 / 1 | Delivery gain; one unsupported comparative premise |
| A01: recognition lost, unbroadcast endpoint retained | 2 / 2 / 2 | 2 / 2 / 1 | Both arms separate event from endpoint; one uncertain M1 premise |
| A00: recognition lost and broadcast occurs | 0 / 0 / 0 | 0 / 0 / 0 | Entire contrast remains unmeasured semantically |
| B11: discovery and unaltered costume retained | 2 / 2 / 2 | 2 / 2 / 2 | Optional duplicate cleanup succeeds |
| B10: discovery retained, seam unpicked | 1 / 1 / 0 | 2 / 2 / 0 | Correct targets; all three valid reports add false sequencing premises |
| B01: discovery lost, costume unaltered | 2 / 2 / 2 | 0 / 0 / 0 | M1 loses both successful controls through invalid delivery |
| B00: discovery lost and seam unpicked | 0 / 0 / 0 | 1 / 1 / 1 | One-order delivery gain, not a semantic recovery |
| CN: glass contradiction outside mandatory task | 2 / 0 / 0 | **2 / 2 / 2** | **Both-order scope recovery** |
| CB: same glass contradiction explicitly mandatory | 2 / 2 / 2 | 2 / 2 / 2 | Both arms detect and correctly block it |
| DN: loudspeaker contradiction outside mandatory task | 2 / 2 / 2 | 2 / 2 / 2 | Control already succeeds |
| DB: same loudspeaker contradiction explicitly mandatory | 1 / 1 / 0 | 2 / 2 / 2 | C2 has one delivery failure and one unsupported group premise |

The screen requires at least **22/24 valid M1 reports**, no lost usable or correct
target control, no lost contradiction detection, and both-order semantic
recoveries spanning an A/B and a C/D family. M1 delivered **19/24**; the only
eligible recovered case is **CN**. It loses usable controls at **A01/RO** and
**B01/OR, B01/RO**. The two B01 losses also lose correct target judgments. No
previously detected C/D contradiction is lost. The required two-family,
two-class recovery is absent.

The A01/RO comparative judgment is explicitly **uncertain**, not proven false.
Even granting that report usability would leave M1 at 16/24 usable and would not
change the failed delivery threshold, B01 losses or absent A/B recovery. This
sensitivity observation does not alter the sealed primary scores.

## What the source inspection establishes

**The ownership card helps one narrow aggregate decision.** In CN, both C2
reports find the retained discovery, decision and endpoint and mark the sole
mandatory retention task met. They also correctly find that the same glass panel
is asserted intact and shattered at the same instant. Their explanations then
explicitly make that separate defect justify `mandatory_failure=true`, despite
acknowledging the narrow test has passed. M1 keeps the contradiction visible in
its group and craft discussion but reports `mandatory_failure=false` in both
orders. Both arms correctly set the flag true when consistency is explicitly
mandatory in CB.

This supports a limited improvement in assigning a defect to the correct
reporting scope. It is not evidence that the defect should be ignored. DN already
works under C2, and no second scope recovery is available. The card adds length
and salience together, so this run does not isolate a particular causal phrase.

**No valid report in these fresh A/B families confuses the earlier event with
the endpoint.** All **20 valid A/B reports** have correct target judgments:
nine C2 and eleven M1. Discovery loss can coexist with a satisfied final state;
the discovery/decision can survive a later prohibited action. The optional
departure or duplicate cleanup is correctly recognized independently in all
twenty. These are useful successful controls, but twelve A/B cells are invalid,
including all four A00 cells. Historical h03 failures were not repeated here;
this fresh matrix does not establish their resolution or a treatment benefit.

**Correct target labels still coexist with unsupported narrative explanations.**
Every valid B10 report—C2/OR and both M1 orders—treats unpicking the seam as
contradicting an invented consultation-before-action or before-decision rule.
The prose actually says Tomas wants another pair of eyes **before explaining**
what he thinks should happen to the coat. It also already supplies a shoulder-
narrowing assignment. Unpicking genuinely violates the assigned endpoint, but
that does not establish the extra claimed narrative contradiction. Two of those
reports repeat the false premise in the group rationale as well.

M1 A10/OR similarly says broadcasting contradicts Lea's choice to defer the
conversation and arrive with a question. The endpoint prohibits broadcasting;
the deferred conversation does not independently prohibit every intervening
action. M1 A01/RO's claim that the changed recording gives **no reason** to ask
the brother is marked uncertain after reading the retained recording discovery,
town/brother reflection and deliberate question. A weaker emotional connection
is a legitimate interpretation; categorical absence of motivation is not
established by those passages.

C2 DB/OR has correct task and endpoint conclusions but says the added sound
assertion makes a pre-existing inconsistency explicit and **“compounds it.”**
The original supplies only the silent-second assertion; the revision creates
the contradiction. Its group rationale therefore fails support even though its
group labels are correct. These defects concern explanatory premises, not a
mandatory literary preference or a reward for smaller edits.

**The deterministic projection isolates the aggregate inconsistency.** On the
35 valid reports, projection from mandatory task verdicts matches the withheld
aggregate in all 35. It differs from the model's flag only in the two CN C2
reports. This is a conditional local consistency result: it relies on the task
verdicts and their declared membership. It neither validates those verdicts in
general nor repairs false explanations, invalid delivery or story quality. No
model answer was overwritten or credited as a repaired success.

## Delivery failures

The **13 invalid reports** are retained and independently audited. All are
normal-stop outputs, not transport errors or truncation.

| Failure | C2 | M1 | Captured evidence |
| --- | ---: | ---: | --- |
| Duplicate `group_id` keys inside group objects | 6 | 5 | Eleven reports, **27 repeated keys**, each with two identical values |
| Invalid JSON: premature root closure, then trailing fields | 1 | 0 | A00/RO; parser stops at character **3,857** of **6,244**, with misplaced root `evidence` |
| Unknown evidence reference | 1 | 0 | B10/RO cites revision `R020`; that revision catalog ends at `R019` |

The duplicated IDs appear once at the beginning of their group object and again
after `preservation`, before the remaining relation/support/dependency fields.
Identical values do not make duplicate-key JSON acceptable. The pair-preserving
audit retains both occurrences and never chooses a first or last value. The
unknown-reference report has seven references in the affected field, within the
eight-reference limit: its failure is identity, not cardinality.

The initial sentinel passed before these failures appeared. Several occur in
compound A00/B00 cases, but B01 and DB also fail; this small fixed schedule does
not establish complexity or order as the cause. The ownership card was not a
delivery intervention. DeepSeek's earlier 32/32 valid C2 repeat cannot be treated
as a general delivery guarantee, and these failures are not evidence of a new
Ollama outage. They remain separate from the earlier stopped Gemma D pilot.

## Inspection, local verification and artifacts

All 48 receipts and source/request bindings were replayed. A shuffled export hid
arm and presentation order; all **35 valid reports** were read against complete
source/context and every assessment field. **425 exact field-bound claims** are
recorded with source/version/offset evidence, explicit support or uncertainty,
and exact mandatory contracts. Notes were sealed **before decoding the key**.
All thirteen rejected captures received a separate structural audit and no
semantic rescue. Wording can reveal condition; this is operator factual
inspection, not independent blind human literary preference.

**23 post-run offline tests pass**, including replay of every invalid capture,
unchanged request/budget/runtime checks, source-bound notes, full assessment-field
coverage, raw/inspection tamper rejection, scope/contradiction controls and exact
decision replay. HTTP is blocked during these tests. Ruff lint/format and strict
mypy pass on four new analysis scripts. An initial test run correctly rejected
both tampered copies but expected `AssertionError` instead of the harness's
`ValueError`; those two test expectations were corrected. Initial and final
verification records remain available. No sealed harness or scoring rule changed.

The sealed **119-test preparation** record remains intact. Application source,
production prompts and frontend files did not change, so unrelated application
suites and the frontend build were not repeated for this evidence/documentation
change. The tracker and local issue index are updated; all fourteen GitHub links
and original issue bodies are preserved. No external issue was edited or closed.

- [Frozen preparation](../../data/diagnostics/reviewer-ownership-v61-2026-10-23/):
  plan, exact requests, source packets, cards, gold labels and approval record.
- [Raw execution](../../data/diagnostics/reviewer-ownership-v61-2026-10-23-live/):
  48 reservations, wire requests, model/version checks, raw captures, receipts and
  per-cell seals; the sentinel and preflight are preserved.
- [Inspection and analysis](../../data/diagnostics/reviewer-ownership-v61-2026-10-23-analysis/):
  `inspection/` export, notes and seals; `decision.json`, `results.json`,
  `invalid-response-audit.json`, `execution-manifest.json`, verification and
  analysis manifest. Detailed prose and captures remain local and ignored by Git.

Offline replay from the repository root:

```powershell
.venv/Scripts/python.exe -X utf8 data/diagnostics/reviewer-ownership-v61-2026-10-23/ownership.py verify
.venv/Scripts/python.exe -X utf8 -m pytest data/diagnostics/reviewer-ownership-v61-2026-10-23-analysis/test_execution.py -q
```

## Recommended next decisions

1. Retain **CN's both-order scope recovery** as limited diagnostic evidence.
   Keep C2 controls and the 13 invalid captures; do not adopt the M1 package.
2. Investigate delivery locally before another inference run: compare these
   DeepSeek group-ID repetitions with the already audited schema property/required
   ordering and the isolated D presentation candidate. Preserve strict validation;
   do not silently deduplicate, splice braces or remap evidence references. This
   run's exact invalid captures are already covered by offline regression checks.
3. Consider an application-owned mandatory aggregate as a separate local design,
   using validated declared task membership and preserving uncertainty. Display
   genuine out-of-scope craft defects independently. Do not turn the successful
   projection into an automatic writer instruction or treat it as semantic truth.
4. Only after those checks, propose a delivery-focused bounded comparison with
   unchanged controls, fresh families and both orders. Keep ownership/semantic
   changes isolated, retain compound-loss and successful controls, and require
   source-grounded complete reports before testing reviewer-driven writer edits.
   No next experiment, budget or live call is authorized by this recommendation.

The nine earlier human ties remain unchanged. Humans should assess feel/emotion,
flow, character and story-breaking details, with machine-prepared mechanical
evidence. Neither more accurate diagnostic labels nor exact preservation alone
demonstrates a better story. Four family clusters at one seed are a small
diagnostic sample, not 48 independent stories. **Step 19 remains IN PROGRESS;
Step 20 remains NOT STARTED; the canary remains ON HOLD.**
