
"""
Demo script to test the scene orchestrator without the web UI.
Run with: python demo.py
"""

import sys
import logging
from app.core.scene_templates import get_template
from app.orchestrator.scene_orchestrator import SceneOrchestrator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def print_separator(title=""):
    """Print a visual separator."""
    if title:
        print(f"\n{'=' * 60}")
        print(f"  {title}")
        print(f"{'=' * 60}\n")
    else:
        print(f"{'-' * 60}\n")


def print_turn(dialogue, director_state):
    """Print a single turn."""
    print(f"[Turn {dialogue.turn_number}] {dialogue.character_name}:")
    print(f"  {dialogue.dialogue}\n")

    if dialogue.stage_direction:
        print(f"  [Director's note: {dialogue.stage_direction}]\n")

    # Print director state summary
    print(f"  Scene state:")
    print(f"    - Emotional arc: {director_state.emotional_arc}")
    print(f"    - Closure detected: {director_state.closure_detected}")
    print(f"    - Ending type: {director_state.ending_type}")
    if director_state.unresolved_threads:
        print(f"    - Unresolved: {', '.join(director_state.unresolved_threads)}")
    if director_state.resolved_threads:
        print(f"    - Resolved: {', '.join(director_state.resolved_threads)}")


def demo():
    """Run a demo scene execution."""
    print_separator("Open Hollywood - Demo Scene Execution")
    print("This script will execute a complete scene using the AI agents.")
    print("Make sure Ollama is running with gemma3:4b model!\n")

    # Load the confession scene template
    print("Loading 'Confession' scene template...")
    try:
        config = get_template("confession")
        print(f"✓ Loaded: {config.title}")
        print(f"  Genre: {config.genre.value}")
        print(f"  Characters: {', '.join([c.name for c in config.characters])}")
        print(f"  Max turns: {config.max_turns}\n")
    except Exception as e:
        print(f"✗ Failed to load template: {e}")
        sys.exit(1)

    # Create orchestrator
    print_separator("Initializing Scene Orchestrator")
    try:
        orchestrator = SceneOrchestrator(config)
        print("✓ Orchestrator initialized")
        print(f"✓ LLM Model: {config.llm_model}")
        print(f"✓ LLM Server: {config.llm_server}\n")
    except Exception as e:
        print(f"✗ Failed to initialize orchestrator: {e}")
        print("Make sure Ollama is running: ollama serve")
        sys.exit(1)

    # Execute scene with callback
    print_separator("Executing Scene")
    print("Starting dialogue...\n")

    turn_count = [0]  # Use list to allow modification in nested function

    def on_turn_callback(dialogue, director_state):
        """Callback after each turn."""
        turn_count[0] += 1
        print_turn(dialogue, director_state)

        if director_state.scene_end:
            print("\n[Director called scene END]")

    try:
        result = orchestrator.execute_scene(on_turn_callback=on_turn_callback)

        print_separator("Scene Complete")
        print(f"Total turns executed: {len(result.dialogue_history)}")
        print(f"Completion reason: {result.completion_reason}")

        if result.director_state:
            print(f"\nFinal Scene State:")
            print(f"  - Emotional Arc: {result.director_state.emotional_arc}")
            print(f"  - Ending Type: {result.director_state.ending_type}")
            print(f"  - Closure Detected: {result.director_state.closure_detected}")
            print(f"  - Unresolved Threads: {result.director_state.unresolved_threads}")
            print(f"  - Resolved Threads: {result.director_state.resolved_threads}")

        print("\n✓ Scene execution successful!")

    except KeyboardInterrupt:
        print("\n\nScene execution interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print_separator("Error During Execution")
        print(f"✗ {type(e).__name__}: {e}")
        logger.exception("Full traceback:")
        sys.exit(1)

    print_separator()
    print("Demo complete. Open http://127.0.0.1:8000 to use the web UI!")


if __name__ == "__main__":
    demo()
