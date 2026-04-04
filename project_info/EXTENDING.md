# Extending Open Hollywood

This guide shows how to add new features and customize the system.

## Adding a New Genre

### 1. Add Genre to Enum

In `app/models/types.py`:

```python
class Genre(str, Enum):
    """Available genres for scenes."""
    YOUR_GENRE = "your_genre"  # Add this
```

### 2. Add Genre Block to Orchestrator

In `app/orchestrator/scene_orchestrator.py`, add to `GENRE_BLOCKS`:

```python
Genre.YOUR_GENRE: GenreBlock(
    genre=Genre.YOUR_GENRE,
    performance_directions="Specific instructions for how to perform in this genre...",
    ending_types=["ENDING1", "ENDING2", "ENDING3"],
    ending_weights={
        "ENDING1": 0.4,
        "ENDING2": 0.3,
        "ENDING3": 0.3,
    }
),
```

### 3. Update Frontend

In `templates/index.html`, add option to genre select:

```html
<option value="your_genre">Your Genre</option>
```

## Adding a New Character Template

### 1. Create Constitution File

Create `your_character_system_prompt.md` with detailed character definition.

### 2. Add to CharacterTemplates Class

In `app/core/scene_templates.py`:

```python
YOUR_CHARACTER = Character(
    name="Character Name",
    description="Brief description",
    constitution="""Full multi-line character definition from your .md file..."""
)
```

### 3. Add to Scene Template (or use in frontend form)

```python
CUSTOM_SCENE = SceneConfig(
    title="Your Scene",
    genre=Genre.DRAMA,
    characters=[
        CharacterTemplates.YOUR_CHARACTER,
        CharacterTemplates.ANOTHER_CHARACTER,
    ],
    # ... other config
)

SCENE_TEMPLATES["custom_scene"] = CUSTOM_SCENE
```

## Creating a New Scene Template

### 1. Define in `app/core/scene_templates.py`

```python
YOUR_SCENE = SceneConfig(
    title="Your Scene Title",
    genre=Genre.DRAMA,
    characters=[...],
    scene_context="Describe the setting and context...",
    director_system_prompt="""Your director prompt...""",
    max_turns=30,
    min_turns=6,
    llm_model="gemma4:e4b",
    llm_server="http://localhost:11434",
)

SCENE_TEMPLATES["your_scene"] = YOUR_SCENE
```

### 2. Or Add via Frontend Form

Users can create scenes directly in the web UI with custom parameters.

## Changing the LLM Model

### Option 1: Change Default

In `app/models/types.py`:

```python
llm_model: str = Field(default="gemma2:2b", ...)  # or other model
```

### Option 2: Pass via API

When creating a scene, include:

```json
{
    "llm_model": "neural-chat:7b",
    "llm_server": "http://localhost:11434"
}
```

## Adding Custom Ending Types

### 1. Update Director System Prompt

Include in `director_system_prompt` field:

```python
"ending_type": <"YOUR_ENDING"|"ANOTHER"|...>
```

### 2. Update Genre Block

Add to `ending_types` list and weight in `ending_weights`.

### 3. Update Frontend Display

The frontend automatically shows whatever ending types the director returns.

## Modifying Director Logic

Edit `app/orchestrator/scene_orchestrator.py`, method `_should_end_scene()`:

```python
def _should_end_scene(self, scene_state: SceneState) -> bool:
    """Your custom ending logic here."""
    if some_custom_condition:
        return True
    return False
```

## Multi-Character Scenes

To support 3+ characters:

### 1. Update Orchestrator Turn Logic

In `execute_scene()`, change:

```python
# Current: alternates between 2 characters
current_speaker = self.scene_config.characters[scene_state.current_speaker_index]
next_speaker_index = (scene_state.current_speaker_index + 1) % len(self.scene_config.characters)
```

This already supports N characters! Just add more to the characters list.

### 2. Update Director Prompt

Ensure director prompt accounts for multiple speakers.

### 3. Test Frontend

The WebSocket naturally broadcasts to all clients.

## Custom Prompt Modifications

### Character Prompt Variants

Create variations in `PromptBuilder`:

```python
@staticmethod
def build_character_prompt_with_memory(
    character: Character,
    genre_block: GenreBlock,
    scene_context: str,
    character_memory: str,  # New parameter
) -> str:
    # Build prompt including memory
    ...
```

### Director Prompt Variants

Similarly, create custom director prompts for different evaluation criteria.

## Adding Real-time Features

### Scene State Caching

In `app/main.py`, extend the scene storage to persist state:

```python
scene_history: Dict[str, List[dict]] = {}  # Store complete turn history
```

### Scene Replay

Add endpoint to re-run a scene:

```python
@app.post("/api/scenes/{scene_id}/replay")
async def replay_scene(scene_id: str):
    # Re-execute with same config
    pass
```

## Performance Optimization

### 1. Model Quantization

Use ollama's quantized models:

```bash
ollama pull gemma3:4b-q4_0  # 4-bit quantized
ollama pull gemma2:2b       # Smaller model
```

### 2. Parallel Agent Calls

Modify `execute_scene()` to call agents in parallel:

```python
import asyncio

# Call multiple agents simultaneously
tasks = [agent1_task, agent2_task, director_task]
results = await asyncio.gather(*tasks)
```

### 3. Response Caching

Cache identical prompts to same character:

```python
@functools.lru_cache(maxsize=100)
def get_cached_response(prompt_hash, dialogue_hash):
    # Return cached result
    pass
```

## Error Handling

### Custom Director Response Validation

In `AgentManager.parse_director_response()`:

```python
def parse_director_response(self, response_text: str) -> dict:
    # Add custom validation
    parsed = json.loads(json_str)
    
    # Validate required fields
    required_fields = ["turn_count", "emotional_arc", "scene_end"]
    if not all(f in parsed for f in required_fields):
        raise ValueError("Missing required fields in director response")
    
    return parsed
```

### Fallback Responses

Provide sensible defaults when director fails:

```python
def get_director_response(self, ...):
    try:
        return self.agent_manager.get_director_response(...)
    except Exception:
        logger.warning("Director failed, using fallback state")
        return {
            "turn_count": self.current_turn,
            "emotional_arc": "tension",
            "scene_end": False,
            ...
        }
```

## Testing Custom Features

### Unit Tests

```python
from app.orchestrator.scene_orchestrator import SceneOrchestrator
from app.core.scene_templates import SCENE_TEMPLATES

def test_custom_genre():
    config = SCENE_TEMPLATES["your_scene"]
    orchestrator = SceneOrchestrator(config)
    # assertions
```

### Integration Tests

Run the demo script:

```bash
python demo.py
```

## Database Integration

### Store Scene History

```python
import sqlite3

def store_scene_result(scene_id: str, result: SceneState):
    conn = sqlite3.connect("scenes.db")
    # Store dialogue_history, director_state, metadata
    conn.commit()
```

### Query Past Scenes

```python
def get_scene_by_id(scene_id: str):
    # Retrieve from database
    pass
```

## API Extensions

### Webhook Notifications

```python
@app.post("/api/webhooks/register")
async def register_webhook(url: str):
    # Store webhook URL
    # Call it when scene completes
    pass
```

### History Export

```python
@app.get("/api/scenes/{scene_id}/export")
async def export_scene(scene_id: str, format: str = "json"):
    # Export to JSON, PDF, TRANSCRIPT, etc.
    pass
```

## Documentation

- When you add features, update this file
- Update README.md with new capabilities
- Document breaking changes in `CHANGELOG.md`
- Keep system prompts (.md files) current

## Support for Complex Scenarios

### Emotions Tracking

Extend `DirectorState` to track emotional spectrum per character:

```python
emotions: Dict[str, Dict[str, float]] = {
    "Father Aldric": {"anger": 0.2, "sadness": 0.5, ...},
    "Marco": {"guilt": 0.8, "fear": 0.3, ...}
}
```

### Dialogue Quality Metrics

Track coherence, relevance, emotional intensity:

```python
dialogue_metrics: Dict[str, float] = {
    "coherence": 0.85,
    "relevance": 0.92,
    "emotional_intensity": 0.7,
}
```

## Contributing Back

If you create cool extensions, consider:
- Sharing genre blocks
- Creating reusable character templates
- Publishing performance benchmarks
- Contributing prompt improvements
