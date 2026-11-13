# Four-work OpenAI assessment smoke results

Date: 2026-11-13

Status: approved execution and terminal inspection **COMPLETE**; run **HALTED at
the first input-count gate**. Generation delivery remains **NOT QUALIFIED**.
Production prompts unchanged; further live calls **PAUSED**; canary **ON HOLD**.

## Outcome

The [frozen plan](assessment-openai-four-work-smoke-plan-2026-11-13.md) was executed
once. OpenAI returned HTTP **200** for N06's full-context input-count request and
counted **350,749 input tokens**. That exceeds the frozen **272,000-token application
reservation** by **78,749 tokens (28.95%)**. The response mapped cleanly, with no
error codes or mapping issues. The application correctly stopped the entire
remainder before any generation.

**One of four input counts, zero of four generation attempts, zero retries.**
The other seven fixed slots were not dispatched. All six active claims remain
unassessed: there are no new model judgments, citations, explanations, native
completion receipts or successful whole works to score. This is a resource-fit
result, not a failed model assessment or evidence of a provider outage.

The approved model setting was `gpt-6.1-sol`, explicit `high`. The count response
does not establish that model's generation access or behavior. The 272,000-input
limit is the application's reviewed pricing boundary, not the model's full context
limit. The other three works' actual token counts remain unknown.

## Authorization, payload and fixed slots

User approval covered full unpublished prose/context at both OpenAI endpoints,
four counts and four generation attempts with no retries, subject to frozen stops.
Only `POST https://api.openai.com/v1/responses/input_tokens` was actually called,
once for N06. No request was sent to `https://api.openai.com/v1/responses`. No
metadata, model-list, recovery, polling or substitute request was made.

Exact approved plan bytes SHA-256:
`97f479ce20069c57649bf981a92c3b2724a9cd9a9ba811b2e9b419f0b7ae9eed`.

The full source prose, original messages, whole reviews, registry, provenance,
declarations and work briefs were unchanged. The four preparations still retain
all **six active claims, 51 fields, four holds and 41 unselected fields**. The eight
frozen endpoint bodies, diagnostic presentation, response schema and resource
settings were not edited. The existing approved credential was used only in memory.

| Fixed slot | Work | Result | Attempt consumed |
| --- | --- | --- | --- |
| Input count 1 | N06 | HTTP 200; 350,749 tokens; rejected by 272,000 cap | Yes |
| Input count 2 | N07 | Not dispatched after N06 stop | No |
| Input count 3 | N10 | Not dispatched after N06 stop | No |
| Input count 4 | N11 | Not dispatched after N06 stop | No |
| Generation 1 | N06 | Not dispatched | No |
| Generation 2 | N07 | Not dispatched | No |
| Generation 3 | N10 | Not dispatched | No |
| Generation 4 | N11 | Not dispatched | No |

All four counts had to pass before any generation. Unused slots are not permission
to resume this closed one-shot plan, create another journal, raise the cap or trim
context. No follow-up inference was attempted.

## Inspection and accounting

| Work | Active original claims | Assessment outcome |
| --- | --- | --- |
| N06 | Q001 | Not assessed; generation not started |
| N07 | Q004, Q005 | Not assessed; generation not started |
| N10 | Q003, Q007 | Not assessed; generation not started |
| N11 | Q003 | Not assessed; generation not started |

The frozen inspection form was copied to the results directory and completed for
all eight slots and six absent judgments. Whole-claim support, source/version
binding, material evidence coverage, explanation materiality and interpretation
are all explicitly unassessed. Earlier authored finals remain fixtures; they were
not substituted for live results or used to invent a semantic score.

The count exchange took **2.325185 seconds**. The recorded run dispatch window was
**5.339304 seconds**, excluding initial local source authentication and final audit.
These are count/dispatch measurements, not generation latency measurements.

The count response supplies no generation input/output/cached/reasoning usage
counters. They remain null. Known generation subtotals are zero because there
were **zero generation intents**, with zero unknown-usage generation attempts.
The count is not generation usage. **Actual billed cost remains unknown**; no claim
is made that this request was free. The $4 reservation was an upper estimate for
authorized generation, not a measured charge.

The journal contains one flushed intent, one observed outcome and a final stop.
It closed normally with state `halted`; process exit zero denotes successful
execution of that stop, not successful assessment delivery. No work is completion
eligible and writer dispatch remains unauthorized.

## Evidence and verification

Private preparation: `data/diagnostics/assessment-openai-smoke-2026-11-13/`.
Its fixed `live-journal/` is retained unchanged. Private results:
`data/diagnostics/assessment-openai-smoke-results-2026-11-13/`.

- `authorization.json` records this approval and endpoint ceilings.
- `capture/` is a byte-identical copy of the five live-journal files.
- `audit/` contains the supported read-only three-file terminal export. Its origin
  is `observed_openai_transport`, with transport observation true and model
  observation false. Local journal integrity is not provider-signed attestation.
- `inspection.json` and `summary.json` record every fixed slot and absent judgment;
  `inspect_run.py` independently checks the count guard, exact body/intent linkage,
  usage nullability, stop, undispatched slots and missing native completions.
- The observed response-body SHA-256 is
  `0228c230e4266be2e2343c3695f44fdaf57b0490aa9bd52b49b9fcb2ac8368ab`.
  Raw HTTP response bytes were not retained; the safe mapped response and digest
  were. The request ID is retained privately for correlation, not as an attestation.

Before execution, all **101 sealed preparation members** and **11 implementation/
documentation snapshots** matched; local source validation passed for all four
works and the fixed live journal was absent. After execution, the supported audit
reconstructs the same closed terminal state. Its exact repeat reuses the export
without changing bytes or mtimes. The private inspection assertions, Ruff,
formatting and strict mypy pass (**268 Python files**, including the inspection
helper). The prior preparation's 420-test combined suite and 38-test final smoke
suite are historical qualification evidence; they are not claimed as rerun here.
No runtime implementation or test code changed during this execution task.

Final preservation checks retain **1,318 earlier sealed members** (1,217 preceding
this preparation plus its 101), **636 selected archive source pins**, **763 of 766
baseline files** outside the three declared documentation updates, all fourteen
issue bodies and posted URLs, and the original live journal. Only the root README,
issue index and tracker are updated, alongside this new report and private results.
The frozen approval document remains a historical preparation record. Final private
snapshots, verification records and a results seal preserve this handoff.

## What this establishes and next step

This run establishes a successful authenticated count exchange for N06 and an
effective application reservation stop with durable terminal evidence. It does
not qualify generation transport, native completion, semantic judgment, factual
coverage, editorial judgment, writer edits or story quality. It supplies no basis
for blaming Sol or OpenAI for the existing critic/writer problems.

Before more inference, do a **bounded local payload/resource composition audit**
of these same four exact requests. Measure the representations of story evidence,
scope, citation registry and operator provenance, including repeated serialization.
Determine what the model needs to see and what the application only needs to retain
for audit. Explore a lossless representation with stable reference mapping, and
prove source/authority/scope/citation equivalence locally before proposing a renderer
change. The present count does not quantify which payload sections caused the excess;
do not turn that hypothesis into a finding without the audit.

Do not shorten the story, summarize away evidence or raise the cap automatically.
Any revised request or resource policy needs a new locally verified freeze and
separate approval before live calls. This protects the context needed for future
story-quality work while addressing a concrete delivery prerequisite.

CW-007/CW-013 remain open; CW-014 unqualified. Step 19 **IN PROGRESS**; Step 20
**NOT STARTED**. Production prompts unchanged; live calls **PAUSED**; full workflow
canary **ON HOLD**. No user database write, new human checkpoint or issue closure.
