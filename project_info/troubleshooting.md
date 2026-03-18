## Troubleshooting

### "Connection refused" error
- Ensure Ollama is running: `ollama serve`
- Check it's accessible: `curl http://localhost:11434/api/tags`

### Slow responses
- Gemma3:4b is optimized for speed; if still slow, reduce model size or upgrade hardware
- You can try: `ollama pull gemma2:2b` for faster responses

### JSON parsing errors from Director
- The director prompt expects structured JSON output
- Review `director_system_prompt.md` for required fields
- Increase model temperature slightly if needed

### Scene ends immediately
- Check `min_turns` in `SceneConfig`
- Verify director's `turn_count` and emotional arc logic
- Review `_should_end_scene()` in orchestrator