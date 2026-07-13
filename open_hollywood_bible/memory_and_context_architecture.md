# Memory and context architecture

Memory is probably the most consequential technical design in this project.

Do not treat “memory” as one ever-growing chat transcript or one vector database.

## Five memory layers

### 1. User intent

The original prompt, explicit requirements, approved assumptions, maturity setting, format, and later user instructions.

This is small and always authoritative.

### 2. Canonical story state

A structured story bible containing:

- Characters and relationships
- World rules
- Locations
- Timeline
- Themes
- Voice guide
- Established facts
- Open mysteries
- Promises and payoffs
- Current character knowledge
- Prohibited contradictions

This is the shared source of truth.

### 3. Versioned artifacts

Every blueprint, outline, scene, critique, and revision is immutable. A new revision creates a new version with lineage rather than overwriting the old one.

### 4. Workflow/checkpoint state

Execution status, next node, retries, budgets, approvals, errors, and node outputs. LangGraph supports SQLite checkpointers for local workflows and PostgreSQL checkpointers for production. [Persistence and checkpointer options](https://docs.langchain.com/oss/python/langgraph/persistence).

### 5. Ephemeral agent context

Each model call receives a generated context packet containing only:

- Its assignment
- Relevant user constraints
- Required story-bible sections
- Direct dependency artifacts
- A concise summary of preceding material
- Its output schema and rubric

This context is discarded after the call, although the exact assembled prompt should be retained in the invocation audit record when privacy settings permit.

## Retrieval policy

Use deterministic retrieval first:

- Scene 14 receives its scene plan.
- It receives the characters appearing in Scene 14.
- It receives facts and unresolved threads tagged as relevant to Scene 14.
- It receives summaries of the immediately preceding scenes.
- It receives the voice and format guide.

Add semantic retrieval later for research notes and very long manuscripts. Vector search should support the story model, not replace it.

Ollama can enforce JSON-schema structured outputs for compatible local models, making it useful for story-bible updates and agent state. [Ollama structured outputs](https://docs.ollama.com/capabilities/structured-outputs).