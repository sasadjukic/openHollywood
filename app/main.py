"""
FastAPI application for the Open Hollywood scene execution engine.
"""

import logging
import json
import asyncio
from typing import Dict, List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os
import queue
import time

from app.models.types import SceneConfig, Character, Genre
from app.orchestrator.scene_orchestrator import SceneOrchestrator
from app.core.scene_templates import list_templates, get_template, CONFESSION_SCENE

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Open Hollywood", description="AI Scene Execution Engine")

# Store active scenes
active_scenes: Dict[str, SceneOrchestrator] = {}
scene_results: Dict[str, dict] = {}

# WebSocket connections
active_connections: Dict[str, List[WebSocket]] = {}


# Serve static files
static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/")
async def root():
    """Serve the main HTML page."""
    html_path = os.path.join(os.path.dirname(__file__), "..", "templates", "index.html")
    if os.path.exists(html_path):
        return FileResponse(html_path)
    return {"message": "Open Hollywood - AI Scene Execution Engine"}


@app.get("/api/genres")
async def get_genres():
    """Get available genres."""
    return {
        "genres": [
            {"id": g.value, "name": g.value.replace('_', ' ').title()}
            for g in Genre
        ]
    }


@app.get("/api/templates")
async def get_templates():
    """Get available scene templates."""
    return {"templates": list_templates()}


@app.get("/api/templates/default")
async def get_default_template():
    """Get the default (Confession) scene template."""
    return CONFESSION_SCENE


@app.get("/api/templates/{template_id}")
async def get_scene_template(template_id: str):
    """Get a specific scene template."""
    try:
        template = get_template(template_id)
        return template
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/api/scenes")
async def create_scene(config: SceneConfig):
    """
    Create and start a new scene.

    Args:
        config: Scene configuration

    Returns:
        Scene ID and initial state
    """
    try:
        orchestrator = SceneOrchestrator(config)
        scene_id = f"scene_{len(active_scenes)}"
        active_scenes[scene_id] = orchestrator
        active_connections[scene_id] = []

        logger.info(f"Created scene: {scene_id}")

        return {
            "scene_id": scene_id,
            "title": config.title,
            "genre": config.genre.value,
            "characters": [
                {"name": c.name, "description": c.description or ""}
                for c in config.characters
            ],
        }

    except Exception as e:
        logger.error(f"Error creating scene: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.websocket("/ws/scene/{scene_id}")
async def websocket_endpoint(websocket: WebSocket, scene_id: str):
    """
    WebSocket endpoint for receiving real-time scene updates.

    Args:
        websocket: WebSocket connection
        scene_id: ID of the scene to watch
    """
    if scene_id not in active_scenes:
        await websocket.close(code=4004, reason="Scene not found")
        return

    await websocket.accept()
    active_connections[scene_id].append(websocket)

    logger.info(f"WebSocket connected for scene {scene_id}")

    try:
        # Send initial state
        await websocket.send_json({
            "type": "connected",
            "scene_id": scene_id,
            "message": "Connected to scene"
        })

        # Keep connection alive and listen for commands
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)

                if message.get("type") == "start":
                    # Start the scene execution
                    await _execute_scene(scene_id)
                elif message.get("type") == "stop":
                    # Stop the scene (if running)
                    logger.info(f"Stop command received for {scene_id}")

            except json.JSONDecodeError:
                await websocket.send_json({"type": "error", "message": "Invalid JSON"})

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for scene {scene_id}")
        active_connections[scene_id].remove(websocket)


async def _execute_scene(scene_id: str):
    """Execute a scene and broadcast updates to connected clients."""
    orchestrator = active_scenes[scene_id]
    connections = active_connections[scene_id]
    
    # Use a queue to collect turns from the blocking executor
    turn_queue = queue.Queue()

    def on_turn_callback(turn, director_state):
        """Called after each turn (synchronous callback from executor)."""
        turn_queue.put({
            "turn": turn,
            "director_state": director_state
        })

    try:
        # Run scene execution in a thread pool
        import concurrent.futures
        
        def run_scene():
            return orchestrator.execute_scene(on_turn_callback=on_turn_callback)
        
        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # Start scene execution
            future = loop.run_in_executor(executor, run_scene)
            
            # While scene is executing, process updates from the queue
            while not future.done():
                try:
                    # Non-blocking queue get with timeout
                    turn_data = turn_queue.get(timeout=0.1)
                    turn = turn_data["turn"]
                    director_state = turn_data["director_state"]
                    
                    message = {
                        "type": "turn",
                        "turn_number": turn.turn_number,
                        "character": turn.character_name,
                        "dialogue": turn.dialogue,
                        "stage_direction": turn.stage_direction,
                        "director_state": {
                            "emotional_arc": director_state.emotional_arc,
                            "arc_stages_hit": director_state.arc_stages_hit,
                            "unresolved_threads": director_state.unresolved_threads,
                            "resolved_threads": director_state.resolved_threads,
                            "closure_detected": director_state.closure_detected,
                            "ending_type": director_state.ending_type,
                        }
                    }

                    # Broadcast to all connected clients
                    for connection in connections:
                        try:
                            await connection.send_json(message)
                        except Exception as e:
                            logger.error(f"Error sending message: {e}")

                except queue.Empty:
                    # No turn data yet, continue waiting
                    await asyncio.sleep(0.05)
            
            # Get the final result
            result = await future

        # Broadcast scene completion
        message = {
            "type": "scene_end",
            "completion_reason": result.completion_reason,
            "total_turns": orchestrator.current_turn,
            "ending_type": result.director_state.ending_type if result.director_state else None,
        }

        for connection in connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error sending completion message: {e}")

        # Store result
        scene_results[scene_id] = {
            "status": "completed",
            "result": result.dict(exclude_unset=True)
        }

    except Exception as e:
        logger.error(f"Error executing scene: {e}")

        message = {
            "type": "error",
            "message": str(e),
        }

        for connection in connections:
            try:
                await connection.send_json(message)
            except Exception as ex:
                logger.error(f"Error sending error message: {ex}")

        scene_results[scene_id] = {
            "status": "error",
            "error": str(e)
        }


@app.get("/api/scenes/{scene_id}")
async def get_scene(scene_id: str):
    """Get scene status and results."""
    if scene_id in active_scenes:
        return {
            "status": "active",
            "scene_id": scene_id,
        }

    if scene_id in scene_results:
        return scene_results[scene_id]

    raise HTTPException(status_code=404, detail="Scene not found")


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}