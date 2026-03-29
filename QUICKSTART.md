# Open Hollywood - Quick Start Guide

## Prerequisites Checklist

- [ ] Python 3.10+ (via `python --version`)
- [ ] Virtual environment activated: `source bin/activate`
- [ ] Ollama installed (from https://ollama.ai)
- [ ] Ollama running: `ollama serve` (should see "Listening on")
- [ ] Gemma3:4b model: `ollama pull gemma3:4b`

## 30-Second Setup

```bash
# From the project directory
cd /YOUR_PATH/openHollywood

# Activate environment
source bin/activate

# Verify Ollama connection
curl http://localhost:11434/api/tags

# Run the server
python run.py
```

## 30-Second Usage

1. Open browser: http://127.0.0.1:8000
2. Keep defaults or modify scene parameters
3. Click "Start Scene"
4. Watch the AI agents perform!

## Troubleshooting

### "Connection refused" 
Make sure Ollama is running: `ollama serve` in another terminal

### Server won't start
- Check Python version: `python --version`
- Reinstall deps: `pip install -r requirements.txt`
- Check port 8000 is free: `lsof -i :8000`

### Slow responses
- First run loads model into GPU/CPU (takes ~30 seconds)
- Subsequent runs are faster
- For faster inference, try: `ollama pull gemma2:2b`

### Scene ends immediately
- This might indicate the Director thinks the scene is complete
- Check the console logs for details
- Try increasing `max_turns` in the UI

## Next Steps

1. Review [README](README.md) for full documentation
2. Look at [Open Hollywood Architecture](project_info/hollywood_architecture.txt) to understand the system
3. Modify `sinner_system_prompt.md` and `priest_system_prompt.md` to customize characters
4. Add new genres in `app/orchestrator/scene_orchestrator.py`
5. Create new scene templates in `app/core/scene_templates.py`

## Architecture at a Glance

```
User Interface (Browser)
    ↓ (WebSocket)
FastAPI Server
    ↓
Scene Orchestrator
    ├─→ Prompt Builder (assembles system prompts)
    ├─→ Agent Manager (calls Ollama)
    │   ├─→ Character Agents (isolated LLM instances)
    │   └─→ Director Agent (scene state evaluation)
    └─→ WebSocket broadcasts (real-time UI updates)
```

## Key Files to Know

- `app/main.py` - FastAPI application
- `app/orchestrator/scene_orchestrator.py` - Core scene logic
- `app/agents/agent_manager.py` - LLM integration
- `static/app.js` - Frontend logic
- `app/core/scene_templates.py` - Reusable scene configs

## Performance Tips

1. **First Run**: Model loads into memory (~30-60 seconds)
2. **Subsequent Runs**: Much faster (2-10 seconds per turn)
3. **GPU**: If available, Ollama uses it automatically

## Common Customizations

### Change Max Turns
In the UI: Adjust "Maximum Turns" before starting

### Change Model
Edit `app/models/types.py`, line with `llm_model="gemma3:4b"`

### Change Scene Context
In the UI: Modify "Scene Context" text area

### Add New Genre
1. Add to `Genre` enum in `app/models/types.py`
2. Add block to `GENRE_BLOCKS` in `scene_orchestrator.py`

## Testing

```bash
# Test imports
python -c "from app.models.types import SceneConfig; print('OK')"

# Check Ollama models
curl http://localhost:11434/api/tags | python -m json.tool
```
