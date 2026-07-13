# Recommended creative workflow

```mermaid
flowchart TD
    A["User premise"] --> B["Intake and creative brief"]
    B --> C["Premise and theme"]
    C --> D1["World specialist"]
    C --> D2["Character specialist"]
    C --> D3["Genre or research specialist"]
    D1 --> E["Continuity integrator"]
    D2 --> E
    D3 --> E
    E --> F["Story architecture and beat sheet"]
    F --> G["Blueprint evaluation"]
    G --> H{"Human approval"}
    H -->|"Revise"| C
    H -->|"Approve"| I["Scene or chapter production loop"]
    I --> J["Writer"]
    J --> K["Dialogue or character pass"]
    K --> L["Critic and continuity check"]
    L --> M{"Passes rubric?"}
    M -->|"No, attempts remain"| J
    M -->|"Yes or limit reached"| N["Store canonical artifact"]
    N --> O{"More units?"}
    O -->|"Yes"| I
    O -->|"No"| P["Whole-work editor"]
    P --> Q["Formatter and exporter"]
    Q --> R["Final review"]
```

## Recommended agent catalog

| Agent | Responsibility | Recommended model class |
|---|---|---|
| Orchestrator | Chooses workflow route, dependencies, budgets, and completion | Strong reasoning model |
| Brainstormer | Generates alternatives, thematic possibilities, reversals | Creative general model |
| World Builder | Locations, society, history, atmosphere, rules | Creative model |
| Character Architect | Psychology, goals, contradictions, arcs, relationships | Strong creative/reasoning model |
| Story Architect | Acts, beats, causality, tension, pacing | Strong reasoning model |
| Researcher | Factual grounding when requested | Tool-capable model |
| Scene Planner | Scene goals, conflict, reveal, entry/exit state | Affordable reasoning model |
| Writer | Produces prose or screenplay units | Best available prose model |
| Character Actor | Writes or critiques one character’s dialogue and behavior | Creative model; current engine concept |
| Dialogue Director | Reconciles character passes into one coherent scene | Strong dialogue model |
| Continuity Supervisor | Detects contradictions and unresolved setup | Reliable structured-output model |
| Critic | Scores against a defined rubric | Independent evaluator model |
| Editor | Whole-work voice, rhythm, repetition, clarity | Best editing model |
| Formatter | Deterministic conversion and validation | Code, not an LLM |

Not every story needs every specialist. The graph should choose the smallest useful team.