# 🎬 Open Hollywood - AI Scene Execution Engine

Open Hollywood is a system where AI agents execute theatrical scenes like actors in Hollywood movies and Broadway theater shows, with Zero human involvement during execution (only setup required). Open Hollywood is a sibling project to [SammyAI](https://github.com/sasadjukic/sammyai) that tries to solve a few important issues when LLMs are tasked to generate creative content. Both SammyAI and Open Hollywood are currently developed and tested separately to give a chance for troubleshooting problems in isolated, smaller environments.

In this testing phase, Open Hollywood is using local LLM models (Gemma3:4b) to perfect the engine dynamics. Once the engine dynamics are sorted out, Open Hollywood will be ready for use with all other LLM models. 

In this very early stage of development, Open Hollywood tests scenes with only two actors (AI agents) but this number is projected to increase for more complex scenes. 

## Architecture Overview

The system is built around these core components:

### 1. **Prompt Builder**
Assembles final system prompts from three building blocks:
- Character Constitution (fixed character definition)
- Genre Block (genre-specific performance directions)
- Scene Context (episode setup)

### 2. **Agents**
Two isolated LLM instances with independent perspectives:
- Each agent has their own system prompt
- Each sees the other's dialogue as "user" messages
- Powered by Ollama's Gemma3:4b model

### 3. **Orchestrator**
Traffic controller managing scene flow:
- Alternates turns between characters
- Maintains shared dialogue history
- Enforces turn limits
- Triggers director after each turn

### 4. **Director Agent**
Evaluates scene state after every turn:
- Tracks emotional arc (opening → tension → climax → resolution)
- Detects scene ending conditions
- Injects stage directions for next turn
- Returns structured JSON state

### 5. **Web UI**
Real-time scene viewer with:
- Live dialogue streaming
- Emotional arc tracking
- Thread resolution display
- Stage direction annotations

## Prerequisites

1. **Python 3.10+** (already set up in virtual environment)
2. **Ollama** installed and running with `gemma3:4b` model
   ```bash
   # Install Ollama from https://ollama.ai
   ollama pull gemma3:4b
   ollama serve
   ```

## Running the Application

### Start the Server

```bash
python run.py
```

Or with custom settings:
```bash
python run.py --host 0.0.0.0 --port 8000 --reload
```

The server will start at `http://127.0.0.1:8000`

### 2. Open in Browser

Navigate to: **http://127.0.0.1:8000**

## Usage Guide

### Setup Phase (Only Human Involvement Needed)

1. **Configure Scene:**
   - Enter scene title
   - Select genre (Dark Comedy, Drama, Thriller, etc.)
   - Describe scene context
   - Choose maximum turns

2. **Click "Start Scene"**

3. **Watch AI Agents Execute**
   - Dialogue streams in real-time
   - Emotional arc updates
   - Director's notes appear
   - Scene auto-ends when complete

## Extensibility

### Adding New Genres

Edit `app/orchestrator/scene_orchestrator.py` and add to `GENRE_BLOCKS`:

```python
Genre.YOUR_GENRE: GenreBlock(
    genre=Genre.YOUR_GENRE,
    performance_directions="Your genre instructions...",
    ending_types=["TYPE1", "TYPE2", ...],
    ending_weights={"TYPE1": 0.5, "TYPE2": 0.5, ...}
)
```

## Key Design Principles

1. **Modularity**: Each component (Prompt Builder, Agents, Orchestrator, Director) is independent
2. **Extensibility**: New genres, characters, and ending types can be added without modifying core logic
3. **Isolation**: Agents maintain separate perspectives - no prompt bleeding
4. **Determinism**: Scene state is tracked precisely for consistent, realistic execution
5. **Real-time**: WebSocket provides live scene updates to browsers

## Future Enhancements

- Multi-character scenes (3+ actors)
- Custom character creation UI
- Saving character templates