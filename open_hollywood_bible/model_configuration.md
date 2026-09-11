# Model configuration and experiments

## Current testing policy — 2026-09-11

The designated testing model is `gemma4:31b`, requested as
`gemma4:31b-cloud` for Cloud inference. E4B-driven development tuning is retired
for this phase. Prioritize complete production runs, bounded failure recovery,
revision preservation, human story quality and blind baseline comparison.
Further focused proofreading experiments are deferred, not silently promoted.

Retain all three UI presets and provider-neutral routing. Test 31B only in Cloud
for now; do not make Local depend on Cloud or silently fall back to E4B. This is
an evaluation decision, not an edit to persisted profiles or runtime defaults.
Hybrid evaluation follows only after 31B completes the intended Cloud workflows
and the explicitly scoped Cloud-first Step 19 phase meets its completion criteria.
Local/Hybrid qualification remains deferred, never inferred from Cloud success.

The [testing decision](../docs/benchmark_reports/model-testing-direction-2026-09-11.md)
defines scope, evidence requirements and the operator-reported request allowance;
the [evaluation register](../docs/benchmark_reports/gemma4-31b-evaluation-register-2026-09-11.md)
records observed capabilities and limitations. The original profile descriptions
below remain product capabilities and future experiment options, not a requirement
to run all three concurrently during this phase.

## Settings experience

Do not begin with a giant provider form. Offer three presets:

- Local: every role uses Ollama.
- Cloud: every role uses selected cloud providers.
- Hybrid: expensive creative/reasoning roles use cloud models; summarization, extraction, and selected evaluations run locally.

An Advanced view exposes a role matrix:

| Role | Primary | Fallback | Temperature | Context budget | Output budget | Max attempts |
|---|---|---|---:|---:|---:|---:|
| Orchestrator | Model A | Model B | 0.3 | 20k | 3k | 2 |
| Brainstormer | Model C | Model A | 1.0 | 12k | 5k | 2 |
| Writer | Model D | Model C | 0.8 | 24k | 8k | 2 |
| Continuity | Local model | Model A | 0.2 | 16k | 2k | 2 |

The application should discover Ollama models through its API and query provider model catalogs where available. Context limits and supported capabilities must be recorded per model rather than assumed. Ollama exposes response timing, prompt token counts, generated token counts, tool calls, and other execution metadata through its chat API. [Ollama chat API](https://docs.ollama.com/api/chat).

### Initial v0.1 provider boundary

Start with one Ollama adapter in two deployment modes:

- **Ollama Local:** requests go to the user's local Ollama server without API-key authentication.
- **Ollama Cloud:** requests go directly to `ollama.com` with an API key, or use a `-cloud` model through a signed-in local Ollama server.

This is sufficient for the first short-fiction vertical slice. Do not add Google,
OpenAI, or LiteLLM until experiments show a concrete capability or quality gap.
Keep local/cloud/hybrid profiles provider-neutral so another adapter can be added
without changing workflow contracts.

Discover cloud models dynamically rather than maintaining a hard-coded list of
free models. As of 2026-07-22, Ollama's cloud catalog includes `gpt-oss`,
`gemma4:31b-cloud`, and `nemotron-3-super:120b-cloud`, while the Free plan grants
limited cloud access with one concurrent cloud model. Availability and plan access
can change independently. [Ollama cloud models](https://ollama.com/search?c=cloud),
[Ollama pricing](https://ollama.com/pricing).

Capability routing must account for inference placement, not only the model name.
In particular, Ollama currently documents schema-enforced structured outputs for
local inference but not Ollama Cloud. A cloud-offloaded model must therefore report
`supports_structured_output = false` even when accessed through the local Ollama
endpoint. [Ollama structured outputs](https://docs.ollama.com/capabilities/structured-outputs),
[Ollama Cloud authentication](https://docs.ollama.com/api/authentication).

## Experiment framework

Every invocation should record:

- Provider and exact model identifier
- Model/profile version
- Prompt template version
- Input artifact versions
- Temperature, top-p, seed when supported
- Context and output tokens
- Latency
- Cost or estimated cost
- Retry/fallback history
- Output schema validity
- Critic scores
- Human preference

Implement blind comparison runs:

- Local versus cloud
- Cloud versus hybrid
- Single-writer versus character-agent dialogue
- One critique pass versus two
- Different story architectures
- Different context strategies

Evaluation dimensions should include:

- Originality
- Causal coherence
- Character consistency
- Dialogue distinctiveness
- Emotional credibility
- Pacing
- Voice consistency
- Setup/payoff quality
- Continuity
- Format compliance

LLM critics are useful filters, but human blind preference should remain the highest-weight measure. Otherwise the system risks optimizing writing for the tastes of its evaluator model.
