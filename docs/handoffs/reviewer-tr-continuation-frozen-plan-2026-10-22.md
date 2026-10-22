# Frozen T/R reviewer continuation, 2026-10-22

**Prepared locally; live execution awaits approval of this continuation.**
This plan permits at most **31 new attempts, 41 combined attempts**, within the
original **48-call ceiling**. All ten previous attempts remain counted, including
the HTTP 500. D remains stopped. No live inference or daemon discovery occurred
during preparation. Production prompts are unchanged; the canary is **ON HOLD**.

The user explicitly selected: “One exact recovery attempt: up to 31 new calls,
41 total; no further retries (recommended).” That selects the preparation policy;
it is not approval to execute the newly sealed harness.

## 1. Preserve the interrupted experiment

The [original frozen plan](reviewer-isolated-pilots-frozen-plan-2026-10-22.md),
[interrupted results](../benchmark_reports/reviewer-isolated-pilots-v61-results-2026-10-22.md)
and [terminal-evidence support](reviewer-terminal-evidence-support-2026-10-22.md)
remain immutable. The continuation uses a separate preparation and future live
ledger. It never clears the previous terminal marker or completes its unresolved
reservation in place.

| Pilot | Previously charged | New maximum | Combined maximum | Treatment |
| --- | ---: | ---: | ---: | --- |
| D: Gemma C2/D1 delivery | 8 | 0 | 8 | Retain sentinel stop and limited D1 evidence |
| T: DeepSeek C2/T1 temporal scope | 2 | 15 | 17 | Carry completed T1; recover failed C2 once; then 14 untouched cells |
| R: DeepSeek C2/R1 fulfillment vocabulary | 0 | 16 | 16 | Original frozen schedule |
| **Total** | **10** | **31** | **41** | **Seven original slots remain unallocated and unavailable** |

**Explicit subcap amendment:** T's attempt allowance changes from 16 to 17 and
DeepSeek's aggregate allowance from 32 to 33. This named recovery is the sole
exception to the original per-pilot/no-transfer limits. D is not reopened and
there is no additional reallocation, retry, repair or replacement capacity.

The first new request is **T-h04-C2-RO, attempt 2**. Its prepared file and Ollama
wire payload are exactly the original request, including prose, context, artifact
versions, messages, settings and seed. Its original HTTP-500 attempt remains a
separate failed delivery with unknown usage. A recovery outcome cannot erase it.

**T-h04-T1-RO is never sent again.** Carry its original response and inspection:
correct event/endpoint labels, but an unsupported contradiction claim and false
temporal target, making it unusable. It is already unmasked and is not a new
replicate. No response is selected by comparing multiple successful attempts.

## 2. Keep the cases, requests and scoring fixed

Only `deepseek-v4.1-flash:cloud` is dispatched, through the local daemon at
`http://127.0.0.1:11434` to Ollama Cloud. The payload includes full unpublished
fictional prose, critique/assignment context and exact source-version bindings.
No expected answers or inspection judgments are added to requests.

| Comparison | Frozen families | Contrast to inspect |
| --- | --- | --- |
| T: C2 versus T1 | h04 safehouse; F02 tram; h03 journal; F01 observatory | Earlier events versus final state; sequential transition versus simultaneous contradiction; lost fact with satisfied endpoint; permitted departure |
| R: C2 versus R1 | n03 seed store; F05 bakery; h03 journal; F06 ferry | Fulfillment versus relevance; legitimate duplicate repair; unsupported parent and dependent callback; required retention failure alongside a successful optional repair |

Both original/revision presentation orders remain scheduled for every arm/family.
Keep original schedule order, omitting D and the carried T1 response only. T's
recovery occupies the failed control's original logical position. The 31 prepared
requests are byte-identical copies from the original bundle. No fresh scenes or
prompt changes are introduced into this continuation. Historical/fresh family
labels refer to the original preparation, not a new independent sample set.

Unchanged settings: temperature **0.2**, top-p **0.95**, seed **20261022**,
`think:false`, non-streaming, context **32,000**, output limit **8,000**.
Input reservation is **24,000 tokens** and active inference timeout **300 seconds**
per attempt. No fallback model, schema repair, writer call or warm-up inference.

The original `scoring.json`, inspection anchors, strict validators and
`analysis.decide` are retained. Count logical comparison cells separately from
delivery attempts. A completed T comparison has 16 logical cells and 17 charged
attempts; R has 16 of each. The original HTTP failure has no semantic answer.

Advancement still requires all of:

- Candidate delivery **8/8**, with no lost paired usable control success.
- Every designated permissible candidate control usable in both orders.
- Target improvement in **both orders of at least one family**.
- Correct declared labels and supported task/fact/endpoint, group/support/dependency
  and comparative explanations; uncertainty does not count as success.

T additionally requires the frozen temporal distinction to be supported. R
requires each mapped fulfillment/support/dependency assessment to be supported.
In F02, identify the real same-time contradiction without inventing an assignment
or endpoint failure. In F06, evaluate the legitimate duplicate repair separately
from the unsupported fact change and its dependent callback.

Incomplete or sentinel-stopped pilots cannot advance on a smaller denominator.
D's decision stays incomplete. The best possible T/R result is permission to
**prepare a broader diagnostic**, never production qualification.

## 3. Stop rules and budget

The existing eight-logical-cell sentinel remains mandatory for each pilot. Stop
that pilot if either arm has zero valid answers out of four, or if one blocking
structural signature appears in at least three of its four answers across both
families. T's checkpoint includes the carried T1 and recovery outcome plus the
next six cells: **seven new attempts**, or 17 combined attempts if reached.
R's checkpoint is its first eight cells. It occurs at 33 combined attempts if T
finishes, or 25 if T stops at its sentinel. Stopped tails are not failures and
cannot fund replacement calls.

Any new transport, HTTP, timeout, cancellation, unknown outcome, missing/invalid
usage, budget, integrity, model or daemon-version failure stops **all dispatch**.
The provider's retryable flag is evidence, not permission to retry. No terminal
run resumes automatically. An incomplete reservation or operator lock blocks
restart before discovery. A clean, sealed completed-cell boundary may continue
only after the full ledger and preflight checks pass.

Strictly captured, identified, in-budget HTTP-200 length finishes count as declared
failures without parsing their answer. Invalid complete stop responses remain
invalid. Both count toward sentinels and receive no repair. Non-200 bodies never
enter answer or length evaluation, including error envelopes that resemble a
successful length response.

| Reservation | New maximum | Combined maximum including prior ten |
| --- | ---: | ---: |
| Attempts | 31 | 41 |
| Input tokens | 744,000 | 984,000 |
| Output tokens | 248,000 | 328,000 |
| Active inference seconds | 9,300 | 12,300 |
| Estimate using archived October 22 reference rates | $0.52080 | $0.60688 |

These are reservations, not measured usage or an enforceable provider billing
cap. The original $0.80 planning allowance and 48-call ceiling are retained.
Known prior usage is **87,201 input / 7,737 output tokens** over nine complete
responses; failed-attempt usage and actual billed cost stay unknown. A successful
recovery will not make aggregate actual usage known.

## 4. Approved preflight and terminal evidence

After new live approval, verify all preparation/source seals before constructing
a live transport. Record a nonempty daemon `/api/version` response and require
that same version before/after each inference and across completed-boundary
restarts. Check the original DeepSeek digest, capability and thinking metadata at
preflight and before every request. Gemma is not checked or dispatched.

Expected DeepSeek digest:
`e04da138d31e0c9468e982e1ae9503d06cb7e170caa16a90c17d931c4aa140f8`.

The user's screenshot shows an update followed by successful CLI commands and a
cloud-session prompt. It does not establish the cause of the earlier HTTP 500 or
prove future inference availability. No version from the screenshot is imposed
as the expected server version. The harness does not install updates or restart
Ollama. Version checks can detect observed changes; they cannot prove that no
same-version restart occurred between checks. The carried T1 predates this
preflight, so disclose the interrupted-run/environment boundary when interpreting
the recovered pair, even if the model digest matches.

New terminal evidence binds the continuation seal, original evidence manifest,
reservation, captured body and original gateway exception chain. Unknown usage
remains null, separately from known completed usage. The terminal audit/export
path verifies completed cells and the unfinished terminal attempt independently;
it does not invent a receipt or make the run resumable.

New completed reports are shuffled for source-grounded operator inspection, with
model/arm/order/seed hidden and R1 labels normalized only after strict validation.
Wording may reveal the condition. Carried notes and failed attempts are exported
separately. This is not new blind human literary-preference evidence.

## 5. Verification and local artifacts

The private bundle is
`data/diagnostics/reviewer-tr-continuation-v61-2026-10-22/`.
It contains the 31 requests, seven source packets, schedule, budget, continuation
policy, unchanged scoring/anchors, carried receipts, archived model metadata,
four Python scripts, verification records and a final `plan.json` seal.
The seal binds this public document as well as executable files. Its digest is
recorded in `closure.json` and the authoritative tracker, avoiding a self-hash.

**93 tests pass: 71 continuation checks and 22 existing gateway/contract tests.**
Ruff lint/format and strict mypy pass on all four new Python files.
Verification covers the full 31-request mock path, exact recovery payload,
carried unsupported T1, both sentinel stops, completed-boundary restart, terminal
HTTP fixtures, unknown usage, version drift, strict usage/model guards, corrupted
evidence, authorization bindings, source-safe exports and unchanged scoring.
Final test counts and command results are recorded in `verification.json`.
The first run passed 78 tests and found one test-fixture error: its note builder
tried to score invalid historical D reports as valid semantic samples. That
fixture was corrected; the final run also includes fourteen added approval and
sentinel guard checks. Both verification XML records are retained. All provider
HTTP was simulated, with real HTTP transport blocked in the continuation tests.
No application source or dependency changed; application-wide build checks are
not substituted for these targeted diagnostic/gateway checks.

Verify the freeze locally, without network access:

```powershell
.venv/Scripts/python.exe -X utf8 data/diagnostics/reviewer-tr-continuation-v61-2026-10-22/continuation.py verify
```

Only after explicit approval of this plan, record an `approval.json` binding the
seal, 10 prior / 31 new / 41 combined / 48 original counts, the single named
recovery, DeepSeek, full prose/context and destination. No approval file is
created by preparation. The original 48-call approval cannot unlock this runner.
The future execution command is:

```powershell
.venv/Scripts/python.exe -X utf8 data/diagnostics/reviewer-tr-continuation-v61-2026-10-22/run_continuation.py run
```

The same script supports offline `audit` and `export --output <new-directory>`
against its canonical future live ledger. Export rejects overwrites and paths
inside its source. Raw requests, unpublished prose and detailed captures remain
in ignored local storage; this document does not publish them.

## Interpretation and status

This continuation tests reviewer discrimination and delivery. It does not measure
writer improvement or establish that extra edits harm stories. Preserve the nine
human ties. Future human review should concentrate on feel/emotion, flow,
character and story-breaking details, with mechanics and source evidence prepared
by machines. No gold literary winner or smallest-diff reward is introduced.

All critic/writer issues remain open. No external GitHub issue is edited or closed.
Production remains **prompt 61 / graph 9 / fulfillment policy 1**; the canary is
**ON HOLD**, Step 19 **IN PROGRESS**, Step 20 **NOT STARTED**.
