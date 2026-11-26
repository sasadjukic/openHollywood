# Wading Path measured-stop repeat for approval

**This plan is ready for approval.** One run would send full unpublished prose, saved critique and story context to both OpenAI endpoints for 24 serial input counts followed by up to 24 serial generations. The journal is unused. Approval SHA-256 is `91d46c7d2e445a47d72ede07919e5a44c666aa987a3705cb4bdf9bb8013698c8`. [Frozen manifest and per-slot request hashes](../../data/diagnostics/wading-path-se-repeat-2026-11-26/plan.json)

In the first Wading Path comparison, Astra X alone correctly left an earlier visit open on SE. The independent reader also found its explanation sufficient. This repeat asks how often that combination recurs on identical input and whether the same arm still recognizes a visit or an exclusion when the draft actually supplies one. Only fresh observations enter the totals. B is the production default throughout. [Prior comparison](wading-path-sol-astra-scope-results-2026-11-25.md) · [Independent reading](sol-astra-independent-reading-2026-11-26.md) · [Four-boundary rehearsal](sol-astra-scope-boundary-rehearsal-2026-11-26.md)

## Cases and requests

All three drafts contain the same closing observation. When the light steadies, Elias and Maya stop three full strides short of the panel housing and stay there. A001 asks whether **Elias and Maya reached the master breaker panel housing at some time during scene four**. E1420 points to the complete selected draft in each request.

| Case | What the complete draft establishes | Exact draft version | Frozen label | Fresh observations per arm |
| --- | --- | --- | --- | ---: |
| SE · measured stop | The entry, sightline and closing position leave an earlier joint visit open. | `2f9e80a0-29b4-579f-8075-b6e064788b24` | `uncertain` | 4 |
| VE · confirmed visit | After entering and before the light steadies, both reached the housing and walked back up the passage. | `58a48fd1-3acd-5e69-9f1b-a89c67170c20` | `supported` | 1 |
| XE · whole-scene exclusion | From the opening huddle to the last moment in the plenum, neither person ever came closer than three strides. | `4da86d35-9337-54d8-896b-c212ba05516c` | `unsupported` | 1 |

The four arms are Sol B, Sol X, Astra B and Astra X, using `gpt-6.2-sol` and `gpt-6.2-astra` at high reasoning. B uses the ordinary work brief. X adds one instruction in the claim scope. Its exact wording is “Assess whether the event occurred at any time during scene four. Identify the interval covered by the cited observation and explain its bearing on that claim.”

All 48 request files match their corresponding November 25 archived bytes. Within each arm, the four SE counts are byte-identical and the four SE generations are byte-identical. Repeat numbers and order appear only in the journal. Both presentations use the same original critique, plan, blueprint, bible, earlier scenes and selected prose. Gold, scoring criteria and prior results stay local. [Frozen requests](../../data/diagnostics/wading-path-se-repeat-2026-11-26/requests) · [Source bindings and gold](../../data/diagnostics/wading-path-se-repeat-2026-11-26/gold.json)

## Dispatch order and budget

Read the table top to bottom for counts, then repeat the table for generations. Each arm occupies each position once across the four SE blocks. Each pair of arms occurs in either relative order twice on SE. The two control blocks have opposite orders.

| Block | First | Second | Third | Fourth |
| --- | --- | --- | --- | --- |
| SE repeat 1 | Sol B | Sol X | Astra X | Astra B |
| VE control | Astra X | Astra B | Sol X | Sol B |
| SE repeat 2 | Sol X | Astra B | Sol B | Astra X |
| SE repeat 3 | Astra B | Astra X | Sol X | Sol B |
| XE control | Sol B | Sol X | Astra B | Astra X |
| SE repeat 4 | Astra X | Sol B | Astra B | Sol X |

The destinations are `https://api.openai.com/v1/responses/input_tokens` and `https://api.openai.com/v1/responses`. All counts must be positive and pass the model, context and cost checks before the first generation. Each generation allows 160,000 input and 4,096 output tokens including reasoning. The aggregate generation ceilings are 3,840,000 input and 98,304 output tokens. Under the frozen cost assumptions the estimated generation ceiling is **$26.45760** ($5.29152 for Sol and $21.16608 for Astra). Both arms of each model use the standard service tier with storage disabled. Time limits are 120 seconds per count, 300 seconds per generation and 168 minutes overall.

The first transport, timeout, HTTP, malformed response, model identity, refusal, truncation, claim/citation binding, required usage or budget failure stops dispatch globally. An eligible semantic miss is scored and dispatch continues. Intent is recorded before send. An interruption consumes the registration. Untouched slots and unknown usage remain explicit. The runner allows zero retries, replacements, redirects or fallbacks. [Single-use runner](../../scripts/wading_path_se_repeat/run.py)

## Scores and decision

1. **Label correctness.** One point when the returned label exactly matches the case gold.
2. **Factual sufficiency.** One point when the explanation and cited draft establish the answer for both people over the claimed interval. On SE, the final distance has to leave the earlier visit unresolved. VE and XE each supply a distinct retrospective witness.
3. **Diagnostic completeness.** One point for a factually sufficient explanation that also locates the decisive passages. On SE those include entry, sightline and the joint stop and stay. VE calls for the earlier visit, its timing and the return before the closing stop. XE calls for the whole-scene minimum distance and the interval it covers. Equivalent passage descriptions count.

Grade the explanations with model, presentation, repeat, order and returned label masked. Record the answer excerpt, selected-draft excerpt and basis for each reading. Separately quote any unwarranted assertion that the pair never visited the housing. A wrong label alone does not establish a false denial. Seal all eligible readings before joining the labels. Identical returned text in separate attempts gets a distinct local grading ID. [Frozen grading rules](../../data/diagnostics/wading-path-se-repeat-2026-11-26/scoring.json) · [Grader and decision rule](../../scripts/wading_path_se_repeat/scoring.py)

Report all 48 slot states and available usage, reasoning tokens and latency. Report the three scores and false-denial annotation per eligible observation, SE counts by arm and the two controls separately. Show gains, losses and ties within each model and within each presentation. On SE, a grounded pass requires both the correct label and factual sufficiency.

**Consider a held-out production-length family only if** Astra X records at least **3/4 grounded SE passes**, leads **each** competing arm by at least **two** grounded passes, and earns all three points on **both** its determinate controls. Any missing eligible generation makes the comparison inconclusive. A complete run below threshold holds advancement. Repeated judgments on this one scene can establish within-request repeatability only. Production routing and the workflow canary would require a separate decision.

## Local verification

All **125 local tests passed**. Fourteen covered the new registration, grading and prior boundary rehearsal. Four injected-transport tests exercised the full schedule with identical answers, a rejected 24th count, a wrong generation model and an interrupted dispatch. They checked blocked reuse and the untouched tail. Another 107 exercised the shared mapping and archived regressions. Repository-wide Ruff lint and formatting passed. Strict mypy passed across 492 Python files. [Request and scoring checks](../../data/diagnostics/wading-path-se-repeat-verification-2026-11-26/offline.xml) · [Injected transport](../../data/diagnostics/wading-path-se-repeat-verification-2026-11-26/injected.xml) · [Mapping and archive](../../data/diagnostics/wading-path-se-repeat-verification-2026-11-26/mapping-and-archive.xml)

Disk readback verified the approval digest, all 52 frozen members, 63 implementation and prerequisite hashes, and all 48 wire matches. The registered ledger is ready with 0/24 counts and 0/24 generations attempted. Live calls await approval. [Unused journal readback](../../data/diagnostics/wading-path-se-repeat-verification-2026-11-26/unused-journal.json)
