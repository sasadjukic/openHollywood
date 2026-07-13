Starting point is a deliberately narrow Open Hollywood v0.1: local-first, one short-fiction format, one required human approval, three model profiles, and a 12-prompt benchmark set. That is large enough to test the agentic thesis without prematurely building the final product.

# Recommended Phase 0 contract

## 1. Supported format for v0.1

Start with one format:

> Short prose fiction: 2,500–5,000 words, 3–8 scenes, and roughly 2–5 significant characters.

This is the best first test because it exercises the entire creative chain:

- Interpreting a sparse premise
- Developing characters and a world
- Constructing a complete dramatic arc
- Writing dialogue and action
- Maintaining continuity
- Reaching a satisfying ending
- Editing the complete work

A novel would introduce long-context and continuity problems before the basic workflow is proven. A screenplay would add page formatting and screenplay-specific structural questions that could obscure whether the underlying storytelling works.

I would sequence formats like this:

1. v0.1: short prose fiction
2. v0.2: short screenplay or TV cold open, approximately 5–12 pages
3. v0.3: longer short story or 20–30-page screenplay
4. Later: TV pilots, feature screenplays, novellas, and novels

The internal data model should still be format-neutral from the start. A `StoryProject` should contain structured characters, beats, scenes, and artifacts; only its final renderer should initially support prose.

### Explicitly out of scope for v0.1

- Novels
- Feature screenplays
- Full TV pilots
- Stage plays
- Poetry
- Songs
- YouTube scripts
- Collaborative/multi-user writing
- Image, audio, or video generation
- Research-heavy historical accuracy

That is not a statement about the eventual product—only the first controlled experiment.

---

## 2. Local-first versus hosted priority

Choose:

> Local-first application and storage, with optional cloud inference.

For the initial version:

- Open Hollywood runs on your PC.
- Projects and workflow state live in local SQLite storage.
- Ollama runs locally.
- Cloud model calls are opt-in.
- No accounts, subscriptions, cloud synchronization, teams, or multi-tenancy.
- The first UI can run in a local browser.
- Tauri packaging comes after the agent workflow is reliable.

This is the lowest-risk architecture for your situation because it gives you:

- Fast iteration
- Direct access to Ollama
- Private local story storage
- No hosting expenses
- No authentication system
- Easier inspection of prompts, artifacts, checkpoints, and logs
- Freedom to change database schemas quickly

“Local-first” does not mean “local-model-only.” The workflow can use cloud models while all project management and orchestration remain local.

### Recommended deployment progression

- v0.1: React UI + local FastAPI service + local worker + SQLite
- v0.2: Tauri desktop packaging
- v1.x: optional hosted deployment after the workflow proves valuable

Do not build both local and hosted products simultaneously.

---

## 3. Required approval checkpoints

For v0.1, use only one mandatory checkpoint.

### Mandatory: Story Blueprint approval

The blueprint should contain:

- The system’s interpretation of the premise
- Assumptions it made
- Genre, tone, maturity, and intended effect
- Logline
- Themes
- World and key locations
- Character dossiers
- Character relationships
- Central conflict
- Story arc
- Scene-by-scene outline
- Proposed ending
- Voice/style guidance
- Potential risks or unresolved decisions

The user can:

- Approve
- Request modifications
- Reject and regenerate
- Select between alternatives
- Change a specific character, event, or ending
- Fork the blueprint

Limit automatic blueprint revision to two attempts per user instruction. If the user still dislikes it, pause rather than letting agents keep guessing.

### Optional development checkpoint: first-scene sample

During development, add a switch called something like:

> Pause after first scene

This is useful for diagnosing tone, dialogue, and voice. It should be disabled in normal autonomous runs because otherwise Open Hollywood gradually becomes SammyAI.

### Final review

The completed story is presented for review, but this is not an execution checkpoint—the workflow has already completed. The user can request a new revision run from there.

Therefore, the normal v0.1 experience is:

```text
Premise → autonomous blueprint creation → human approval
        → autonomous drafting/editing → completed story
```

That is sparse enough to test genuine autonomy.

---

## 4. Mature-content boundary

Define an Open Hollywood policy separately from provider behavior.

I recommend two initial content modes:

### Standard Fiction

Suitable for broad audiences. Violence, language, and sexuality remain limited.

### Mature Fiction

Permits fictional:

- Strong language
- Criminal characters and activity
- Drug and alcohol use
- Graphic or disturbing violence
- Horror
- Morally objectionable characters
- Consensual adult sexual content
- Serious treatment of abuse, exploitation, and other difficult subjects

The app should not treat depiction as endorsement. A corrupt character, murderer, abuser, or criminal should be allowed to behave consistently with the story.

### Hard boundary

Irrespective of mode, exclude at least:

- Sexual content involving minors
- Sexual exploitation involving identifiable real people
- Material whose real purpose is actionable assistance for serious wrongdoing rather than fiction
- Content illegal to possess or distribute

Some difficult fictional subjects will remain provider-dependent. If one provider refuses a scene, Open Hollywood should report:

- Which provider refused
- Which task was affected
- Whether an allowed fallback is available
- Whether the user wants to retry with another configured model

It should not silently sanitize the entire story.

Store maturity requirements in the creative brief so every agent receives the same interpretation. Eventually, model profiles can carry compatibility flags such as `supports_mature_fiction`, based on your own tests rather than marketing claims.

---

## 5. Canonical evaluation rubric

Use a single human-facing rubric for every complete story. Agent-specific rubrics can be added later, but they should feed into this canonical standard.

Score each category from 1 to 5:

| Dimension | Weight | Main question |
|---|---:|---|
| Causal coherence and structure | 20% | Do events follow convincingly, build, and reach a complete ending? |
| Character depth and consistency | 15% | Do characters have distinct motives, contradictions, and believable behavior? |
| Dialogue | 15% | Is it distinctive, subtextual, natural, and non-expository? |
| Originality and specificity | 15% | Does the story avoid generic AI patterns and obvious clichés? |
| Voice and prose quality | 10% | Is the writing controlled, vivid, and stylistically consistent? |
| Emotional and thematic impact | 10% | Does the story produce a meaningful emotional or thematic effect? |
| Pacing and tension | 10% | Does each section earn its place and move at an appropriate pace? |
| Continuity and constraint adherence | 5% | Does it honor the prompt, blueprint, established facts, and format? |

Use three anchor descriptions:

- **1:** seriously broken
- **3:** competent but ordinary or noticeably flawed
- **5:** memorable, highly controlled, and close to publishable with minor editing

Avoid overly precise definitions for every number initially. You need a rubric you can actually use repeatedly.

### Hard gates

A story fails regardless of average score if it:

- Is incomplete
- Contradicts a central established fact
- Omits a mandatory prompt requirement
- Contains placeholders or model commentary
- Breaks the target format
- Ends because the token limit was reached
- Incorporates critic notes into the story as prose

### The essential baseline

Compare the agentic workflow against:

> One strong model producing the same story directly from the same prompt, with a roughly comparable total output budget.

Otherwise, you will learn whether stories are good, but not whether the agentic architecture improves them.

For each test prompt, create:

- A: single-model baseline
- B: Open Hollywood agentic result
- Optionally C: hybrid-model agentic result

Present A/B blindly and randomize their order.

### Suggested v0.1 success criteria

Do not require “best human writer” quality yet. Require:

- At least 95% of runs complete without technical failure.
- No severe continuity errors in at least 80% of stories.
- Weighted human score of at least 3.5/5.
- No individual category below 2.5.
- Agentic output preferred to the single-model baseline in at least 60–65% of blind comparisons.
- Median cloud cost remains within the configured run budget.

These are ambitious but measurable.

---

## 6. Hardware profile

Your RTX 3060 with 8GB VRAM and 64GB system RAM is a good minimum development target.

Define it as:

> OH-Local-8GB reference profile

### Initial local limits

- Primary model size: approximately 7B–9B
- Quantization: 4-bit or 5-bit, depending on actual fit and performance
- One local generation at a time
- Initial context: 8K
- Experimental context: 16K only after measuring speed and memory
- No assumption that several local agents run concurrently
- System RAM may support partial CPU offload, but that should be treated as a slower fallback

The important insight is that agents are logical roles. They do not need simultaneously loaded models. A single local model can sequentially perform several roles with separate prompts and state.

### Best initial role assignment

Use the local 8B-class model for:

- Intake extraction
- Creative-brief structuring
- Story-bible updates
- Summarization
- Entity and continuity extraction
- Basic critique
- Constraint checking
- Schema repair
- Local-only baseline drafting

Use stronger cloud models selectively for:

- Story architecture
- Character psychology
- Final prose generation
- Difficult dialogue
- Whole-story editing
- High-confidence evaluation

That gives you a meaningful hybrid system without paying cloud prices for every mechanical operation.

### Hardware measurements to record

For every local model/profile:

- Cold-load time
- Time to first token
- Tokens per second
- Prompt processing time
- Peak VRAM
- Peak system RAM
- Structured-output success rate
- Maximum reliable context
- Whether CPU offload occurred
- Quality score by assigned role

A model that writes attractive prose but fails 20% of structured story-bible updates should not be assigned to that role.

---

## 7. Cloud-model strategy

Begin with three profiles, not a huge model matrix.

### Local baseline

Every role uses the same local model.

Purpose: establish the lowest-cost baseline and expose which tasks local models cannot perform reliably.

### Hybrid economical

- Local model: extraction, summaries, continuity, story-bible maintenance
- Affordable cloud model: brainstorming, scene planning, routine critique
- Premium cloud model: architecture, writing, final edit

Purpose: likely production direction.

### Cloud quality

Use strong cloud models for all substantive creative and evaluation work.

Purpose: estimate the quality ceiling and determine whether local substitutions materially hurt results.

Do not start by testing ten models. Start with:

- One local model
- One affordable cloud model
- One premium cloud model

Also avoid changing the workflow and models simultaneously. First freeze a graph version, then compare model profiles against it.

For repeatable benchmarks, use stable or versioned model identifiers when providers expose them. Aliases and preview models are suitable for exploration but can change underneath your benchmark. OpenAI’s model documentation explicitly exposes snapshots for behavioral consistency, while current Google documentation warns that preview models may change and have more restrictive limits. [OpenAI model documentation](https://developers.openai.com/api/docs/models/chat-latest), [Gemini pricing/model notes](https://ai.google.dev/gemini-api/docs/pricing).

---

## 8. Cloud cost limits

Set limits at four levels rather than choosing only a monthly number.

### Suggested initial limits

| Limit | Recommended starting value |
|---|---:|
| Blueprint-only development run | $0.50 |
| Complete 2,500–5,000-word story | $2.00 |
| Explicit premium comparison run | $5.00 |
| Daily development limit | $10.00 |
| Monthly API limit | $50.00 |
| One-time formal benchmark budget | $100.00 |

The worker must check its remaining budget before every model call. If the next call could exceed the hard ceiling, it should pause rather than complete the request and calculate the cost afterward.

### Provider allocation

A reasonable first month would be:

- Local Ollama: no inference charge
- Ollama Cloud: begin on Free; upgrade to Pro only when limits interfere
- Google: free/small paid experiments
- OpenAI: small prepaid API balance reserved for premium comparisons

Ollama currently lists Free, $20/month Pro, and $100/month Max plans. Its cloud usage is measured primarily through GPU utilization rather than a fixed token allowance, and Pro permits three concurrent cloud models. Start with Free or Pro; Max is unnecessary at this stage. [Ollama pricing](https://ollama.com/pricing).

Google’s inexpensive models make it practical to assign structured or high-volume tasks to a low-cost cloud tier, while reserving more expensive models for high-impact creative work. Its paid pricing varies substantially by model and output tokens are generally more expensive than inputs. [Gemini API pricing](https://ai.google.dev/gemini-api/docs/pricing).

Creative-writing workflows are output-heavy, so track output and reasoning tokens especially carefully. Do not estimate costs only from the original user prompt.

### Privacy consideration

Do not use unpublished or personally sensitive story material on a free tier until you have reviewed its data terms. Google’s current pricing table distinguishes free-tier use that may improve its products from paid-tier use that does not. Ollama states that its cloud prompts and responses are not logged or used for training. [Gemini pricing and data-use table](https://ai.google.dev/gemini-api/docs/pricing), [Ollama cloud privacy statement](https://ollama.com/pricing).

Use synthetic benchmark prompts for free-tier testing.

---

## 9. Representative prompt corpus

Start with 12 frozen prompts. Expand to 24 only after the workflow regularly completes.

Your stroller prompt should be included because it is an excellent sparse-premise test.

### Initial corpus structure

#### Sparse-premise tests

1. The new stroller outside the abandoned, unfinished building.
2. A woman receives a birthday card written in her own handwriting, dated ten years in the future.
3. Every night, one apartment in a large building appears to move to a different floor.

Purpose: test assumption-making, originality, and premise development.

#### Character and dialogue tests

4. A priest and a lifelong criminal discover they are protecting the same person.
5. Two estranged siblings must identify their father’s body, but each insists the dead man is not him.
6. A romantic dramedy in which two people want the same relationship for incompatible reasons.

Purpose: distinct voices, subtext, conflict, and changing power.

#### Structural tests

7. An unreliable-narrator mystery whose final revelation must reinterpret earlier scenes without invalidating them.
8. A non-linear science-fiction story about memories being used as currency.
9. A tragedy in which the protagonist succeeds at the stated goal and destroys what actually mattered.

Purpose: causality, setup/payoff, sequencing, and endings.

#### Constraint tests

10. A suspense story in one location, over one night, with no weapons and no supernatural explanation.
11. A quiet literary story with no villain, no death, and no twist ending.
12. A dark comedy with five significant characters in which every character is concealing a different version of the same event.

Purpose: constraint adherence, ensemble continuity, and resistance to familiar shortcuts.

### Store metadata with every prompt

Each corpus item should include:

- Prompt ID and version
- Full prompt
- Why it exists
- Genre
- Intended maturity
- Target length
- Required elements
- Forbidden shortcuts
- Likely failure modes
- Evaluation dimensions stressed
- Whether factual research is allowed
- Random seed where supported

Never quietly edit a benchmark prompt. Create a new version.

When expanding from 12 to 24, add:

- Two mature-content tests
- Two screenplay-oriented tests
- Two research-grounded stories
- Two longer continuity tests
- Two intentionally contradictory prompts
- Two prompts written in a language other than English, if multilingual support matters

---

## 10. Expected failure cases

Do not merely list failures. Define how the application must respond to each one.

| Failure | Required behavior |
|---|---|
| Orchestrator loops or keeps revising | Stop at graph/call/revision limit and preserve partial artifacts |
| Local model runs out of memory | Cancel safely, unload model, offer smaller profile or cloud fallback |
| Model returns invalid structured data | Validate, allow one repair attempt, then fallback or pause |
| Provider times out or rate-limits | Retry with backoff, then use configured fallback |
| Provider refuses mature content | Report provider/task clearly; never silently sanitize |
| Story bible contradicts a draft | Reject draft artifact and issue a bounded continuity revision |
| Characters acquire the same voice | Dialogue critic identifies convergence and requests a targeted pass |
| Draft becomes generic or clichéd | Critic must cite concrete passages and request specific changes |
| User changes the approved blueprint | Mark dependent artifacts stale and regenerate only affected branches |
| Application restarts during a run | Resume from the last durable checkpoint without duplicating calls |
| Budget is nearly exhausted | Pause before exceeding it and show projected next-step cost |
| Model truncates an ending | Mark artifact incomplete; never accept it as a finished story |
| Evaluator always favors one provider | Blind outputs and periodically reverse presentation order |
| Agent includes notes in the manuscript | Format validator rejects the artifact |
| Context grows uncontrollably | Context compiler enforces per-role budgets and summarizes dependencies |

The first formal technical test suite should deliberately trigger each of these conditions.

---

# The smallest worthwhile milestone

Your first milestone should not be “Open Hollywood writes a story.”

It should be:

> Given one sparse premise, Open Hollywood creates a durable, structured story blueprint using local or cloud models, lets the user revise or approve it, survives a restart, and records every model call, artifact version, token count, cost, and failure.

Only after that milestone works should autonomous drafting begin.

This order will validate the difficult foundations—state, delegation, memory, model routing, approval, persistence, and budgets—before expensive story generation hides architectural problems behind impressive prose.

A concise v0.1 product contract would therefore be:

- One short-story format
- Local-first storage and orchestration
- Optional local/cloud/hybrid inference
- One mandatory blueprint approval
- Standard and Mature Fiction modes
- One canonical weighted rubric
- RTX 3060 8GB as the minimum reference hardware
- $2 normal-run and $50 monthly cloud ceilings
- Twelve frozen benchmark prompts
- Fifteen explicitly tested failure conditions
- Agentic output compared blindly against a single-model baseline

That is a strong, appropriately small foundation from which Open Hollywood can grow.
