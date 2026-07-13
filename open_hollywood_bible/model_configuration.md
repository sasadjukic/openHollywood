# Model configuration and experiments

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