# SETUP CHECKLIST

## Prerequisites

- [ ] Python 3.10+ installed locally
- [ ] Virtual environment `openHollywood` created
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] Ollama installed from https://ollama.ai
- [ ] Ollama gemma4:e4b model downloaded: `ollama pull gemma4:e4b`

## System Verification

Run this command to verify everything is set up correctly:

```bash
cd /YOUR_PATH/openHollywood
source bin/activate
python -c "exec(open('demo.py').read())" --check  # or just run tests
```

✓ Expected output: "ALL SYSTEMS READY!"

## Project Structure Verification

Verify these files exist:

```
□ app/main.py                          - FastAPI server
□ app/orchestrator/scene_orchestrator.py - Core logic
□ app/agents/agent_manager.py          - LLM integration
□ app/core/prompt_builder.py           - Prompt assembly
□ app/models/types.py                  - Data models
□ templates/index.html                 - Web UI
□ static/app.js                        - Frontend logic
□ static/style.css                     - Styling
□ run.py                               - Server entry point
□ demo.py                              - CLI demo
□ requirements.txt                     - Dependencies
□ README.md                            - Documentation
```

## Pre-Launch Checklist

Before starting the server, verify:

1. **Ollama Running**
   ```bash
   # In separate terminal
   ollama serve
   # Should show: "Listening on 127.0.0.1:11434"
   ```

2. **Virtual Environment Active**
   ```bash
   cd /YOUR_PATH/openHollywood
   source bin/activate
   # Prompt should show (openHollywood)
   ```

3. **Dependencies Installed**
   ```bash
   pip list | grep fastapi
   # Should show: fastapi
   ```

4. **Port 8000 Available**
   ```bash
   lsof -i :8000
   # Should show nothing (port is free)
   ```

## Launch Sequence

### Step 1: Start Ollama (Terminal 1)
```bash
ollama serve
```
Wait for: "Listening on 127.0.0.1:11434"

### Step 2: Activate Environment (Terminal 2)
```bash
cd /YOUR_PATH/openHollywood
source bin/activate
```

### Step 3: Start Server (Terminal 2)
```bash
python run.py
```
Wait for: "Application startup complete"

### Step 4: Open Browser (Any browser)
Navigate to: http://127.0.0.1:8000

## First Run Experience

### UI Setup Phase
1. Keep default values or customize:
   - Scene Title: "Confession"
   - Genre: "Dark Comedy"
   - Scene Context: provided
   - Max Turns: 30

2. Click "Start Scene"

3. Watch dialogue stream in real-time:
   - Characters take turns
   - Each turn shows:
     - Character name
     - Dialogue
     - Emotional arc
     - Director's direction (if any)

4. Scene auto-ends when director signals completion

### Expected Timeline
- First run: 30-60 seconds total
- Subsequent runs: 2-10 seconds per turn
- 10-15 turns typical for confession scene

## Troubleshooting

### "Connection refused"
**Problem**: Can't connect to Ollama
**Solution**: 
```bash
# Make sure Ollama is running
ollama serve

# In another terminal, test connection
curl http://localhost:11434/api/tags
```

### "Port already in use"
**Problem**: Port 8000 is taken
**Solution**:
```bash
# Find what's using port 8000
lsof -i :8000

# Kill the process or use different port
python run.py --port 8001
```

### "Module not found"
**Problem**: Import error
**Solution**:
```bash
# Verify you're in the venv
source bin/activate

# Reinstall dependencies
pip install -r requirements.txt

# Try importing manually
python -c "from app.main import app"
```

### Scene ends immediately
**Problem**: Director calls end too early
**Solution**:
```
Check console logs for director state
Increase min_turns in scene config
Verify director system prompt is correct
```

### Slow responses
**Problem**: Takes >5 seconds per turn
**Solution**:
```
This is normal on first run (model loading)
Try smaller model: ollama pull gemma2:2b
Check CPU/GPU usage
Increase system memory
```

## Advanced Setup

### Using Different LLM Model

1. Download model
   ```bash
   ollama pull neural-chat:7b
   ```

2. Modify config in `app/models/types.py`:
   ```python
   llm_model: str = Field(default="neural-chat:7b", ...)
   ```

3. Or pass when creating scene via API

### Using Remote Ollama

Modify server URL when creating scene:
```json
{
    "llm_server": "http://192.168.1.100:11434"
}
```

### Development Mode

Start with auto-reload:
```bash
python run.py --reload
```

Changes to code will automatically reload the server.

## Verification Commands

### Quick Checks
```bash
# Check Python version
python --version

# Check virtual environment
which python

# Check key packages
pip show fastapi
pip show ollama

# Test model availability
curl http://localhost:11434/api/tags | python -m json.tool

# Import check
python -c "from app.main import app; print('OK')"
```

### Full System Test
```bash
python demo.py
```

This will:
1. Load the confession scene template
2. Initialize the orchestrator
3. Save execution output
4. Show completion message

## Post-Launch

### Access Points
- **Web UI**: http://127.0.0.1:8000
- **API Docs**: http://127.0.0.1:8000/docs (auto-generated Swagger)
- **API Redoc**: http://127.0.0.1:8000/redoc

### Monitoring

Watch the server terminal for:
- INFO: Scene created
- INFO: Turn X dialogue from character
- INFO: Director state evaluation
- WARNING: Any issues

### Creating Custom Scenes

See [EXTENDING.md](EXTENDING.md) for:
- Adding genres
- Creating characters
- Defining scenes
- Customizing director logic

## Cleanup & Shutdown

### Stop Server
```bash
# In server terminal
Ctrl+C
```

### Stop Ollama
```bash
# In Ollama terminal
Ctrl+C
```

### Deactivate Environment
```bash
deactivate
```

### Clear Cache (Optional)
```bash
find . -type d -name __pycache__ -exec rm -r {} +
find . -type f -name "*.pyc" -delete
```

## Uninstall (If Needed)

```bash
# Deactivate and remove just the installed packages
cd /YOUR_PATH/openHollywood
source bin/activate
pip freeze > /tmp/installed.txt
pip uninstall -y -r /tmp/installed.txt

# Or remove entire venv
deactivate
cd /YOUR_PATH/openHollywood
rm -rf openHollywood/bin
rm -rf openHollywood/lib
rm -rf openHollywood/include
```

## Success Criteria

You've successfully set up Open Hollywood when:

✓ Ollama runs without errors
✓ Server starts and shows "Application startup complete"
✓ Browser loads http://127.0.0.1:8000
✓ Scene setup form displays
✓ Clicking "Start Scene" begins dialogue
✓ Dialogue updates in real-time
✓ Scene completes with director signal

## Documentation Map

| Document | Purpose |
|----------|---------|
| **README.md** | Full system documentation |
| **QUICKSTART.md** | 30-second startup guide |
| **PROJECT_SUMMARY.md** | Overview & statistics |
| **EXTENDING.md** | How to add features |
| **hollywood_architecture.txt** | System design |
| **steps_to_complete.md** | Original requirements |
| **This file** | Setup checklist |

## Next Steps

1. ✓ Complete this checklist
2. → Start the system (see Launch Sequence)
3. → Try a scene execution
4. → Read EXTENDING.md for customization
5. → Modify prompts and genres

## Support

If issues arise:
1. Check the Troubleshooting section above
2. Review QUICKSTART.md
3. Check console logs for detailed errors
4. Verify all prerequisites are met

## Final Note

All infrastructure is ready. The system is production-ready with:
- ✓ Installed dependencies
- ✓ All core modules
- ✓ Web UI complete
- ✓ Demo script ready
- ✓ Comprehensive documentation
- ✓ Extensible architecture

You're ready to bring AI theatrical scenes to life! 🎬
