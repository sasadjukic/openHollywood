# What the evidence says about DeepSeek as a cause

Date: 2026-10-26. Evidence assessment only; no new model or daemon calls.

**Yes: the records demonstrate failures in answers returned by
`deepseek-v4.1-flash:cloud` under our tested configuration. They support treating
this deployment/configuration as an unreliable reviewer for these tasks. They do
not isolate the base model's weights as the sole cause of our difficulties, or
establish that another model would solve them.**

The distinction is between observed model-output failures and a controlled causal
comparison of models or operating modes. We have substantial evidence of the first
and limited evidence of the second.

## Direct evidence of limitations

In the [latest NC/ES comparison](../benchmark_reports/reviewer-evidence-status-v61-results-2026-10-26.md),
all 28 responses returned HTTP 200 and finished normally. Eight H/U target
judgments—two scene families, two interfaces and two presentation orders—falsely
accepted factual contradictions. ES recovered **none of four contemporary NC
failures**. These are repeated observations on two families, not eight independent
stories or a population-level failure rate.

The erroneous judgments are in the raw content, before application aggregation
or label projection. For example, the model reasons that not yet consulting
someone contradicts acting before consultation. Those facts are compatible;
the surrounding text establishes a different, genuine conflict with a prior
intention and an assignment rule. Merely restating the two true facts does not
support the asserted contradiction. The [local relation audit](reviewer-relation-object-audit-2026-10-26.md)
records exactly which pair each reason addresses.

Other direct output failures include two NC labels that disagree with their
accurate endpoint explanations, and one normally finished report containing three
duplicate JSON member names. These did not originate in the application computing
the wrong aggregate. The strict parser exposed the duplicate-member output; it
did not generate it. Transport success does not prove every aspect of serving is
irrelevant, but a recorded HTTP error or truncation does not explain these cells.

The same model also succeeds on meaningful controls. ES correctly handles all ten
required genuine-conflict, compatible-sequence and explicit-uncertainty targets,
and improves usable whole claims from NC's 30/42 to 35/42. It still loses protected
craft/citation cases and fails the recovery screen. The evidence is selective
unreliability, not inability to perform every relevant judgment.

## Why this is not a DeepSeek-only explanation

The writer-preservation and ordinary-critic problems were already documented using
`gemma4:31b-cloud` in the [October 16 production comparison](../benchmark_reports/production-fulfillment-v61-results-2026-10-16.md)
and [October 17 replication](../benchmark_reports/fulfillment-contrasts-v61-results-2026-10-17.md).
Those failures cannot be attributed to a DeepSeek reviewer that was not used in
those runs. This does not rule out additional weaknesses specific to DeepSeek.

Our matched reviewer comparisons show interaction with the interface:

| Recorded comparison | Gemma | DeepSeek | Supported conclusion |
| --- | --- | --- | --- |
| October 20, V2/C1, 24 attempts per model | 11/24 usable overall; C1 improves 4/12 to 7/12 | 11/24 usable overall; C1 changes 6/12 to 5/12 | No overall winner on this small matrix; the interface affects the models differently. |
| October 21, C2, 32 attempts per model | 0/32 structurally valid; repeated endpoint_check keys | 32/32 valid, 24/32 correct labels, 22/32 usable | DeepSeek delivers much more usable evidence on this interface, but still fails qualification. |

Sources: [October 20 results](../benchmark_reports/reviewer-gemma-deepseek-v61-results-2026-10-20.md)
and [October 21 results](../benchmark_reports/reviewer-interface-repeat-v61-results-2026-10-21.md).
These are different matrices; the table is not a pooled model ranking. Invalid
Gemma reports do not receive primary semantic credit. No matched alternative-model
run on the latest H/U/ES matrix establishes whether those specific failures are
unique to DeepSeek.

## An important untested variable: thinking mode

All 28 latest saved wire requests explicitly set **`think: false`**. The earlier
October 20 comparison also did so. The latest captured `/api/show` metadata lists
supported values `[false, "low", "high", "max"]`, with default `high`. An explicit
false request does not use that default. This was part of the frozen controls,
not a newly discovered execution deviation.

Ollama documents using `/api/show` to discover supported levels and the `think`
field to select them. DeepSeek's own API documentation also describes enabled
thinking with high effort as its default. Those documents establish an available
configuration distinction; they do **not** demonstrate an improvement on our
cases. [Ollama thinking controls](https://docs.ollama.com/capabilities/thinking),
[DeepSeek thinking-mode documentation](https://api-docs.deepseek.com/guides/thinking_mode/).

Thus we have not established that DeepSeek at high thinking would fail in the same
way, nor that it would fix the problem. The direct DeepSeek API documents different
effective sampling behavior between modes; we have not independently established
every corresponding Ollama routing detail. A future test must distinguish requested
parameters from verified effective settings and preserve reasoning/output budgets.
[DeepSeek parameter behavior](https://api-docs.deepseek.com/guides/thinking_mode/).

Captured metadata reports FP8 and the selected tag digest
`e04da138d31e0c9468e982e1ae9503d06cb7e170caa16a90c17d931c4aa140f8`.
We have no matched precision comparison, so we cannot attribute these failures to
quantization. A local cloud-tag digest is not an independently verified checksum
of remotely served weights. We have not isolated base weights, serving behavior,
operating mode, prompt/context burden and task design from one another.

## Recommendation

Treat the observed non-thinking DeepSeek reviewer as a current bottleneck for
these gates. Do not assume that additional schema wording will make it reliable,
or conclude that replacing it will necessarily fix the workflow.

The next materially different hypothesis worth preparing is a **matched operating-
mode comparison**, retaining full scenes, unchanged NC controls and diagnostic
contract, known failures, fresh families, both orders and protected craft/uncertainty
controls. A separate later isolated-pair/full-scene probe could test context
sensitivity. The [local audit](reviewer-relation-object-audit-2026-10-26.md) specifies
the contrasting predictions and preparation requirements. Neither is frozen or
approved here, and there is no new live budget.

Provider attribution remains deferred as requested. Production prompts are
unchanged, live calls are paused and the canary is on hold. Reliable mechanical
review remains distinct from emotionally effective storytelling; the nine prior
human ties and the human review criteria remain unchanged.
