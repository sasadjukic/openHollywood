"""
Orchestrator: Manages scene execution flow, coordinating agents and directors.
"""

import logging
import time
from typing import List, Optional, Callable, Any
from app.models.types import (
    SceneConfig,
    DialogueTurn,
    DirectorState,
    SceneState,
    GenreBlock,
    Genre,
)
from app.core.prompt_builder import PromptBuilder
from app.agents.agent_manager import AgentManager

logger = logging.getLogger(__name__)


class SceneOrchestrator:
    """Orchestrates the execution of a theatrical scene."""

    # Genre configurations
    GENRE_BLOCKS = {
        Genre.DARK_COMEDY: GenreBlock(
            genre=Genre.DARK_COMEDY,
            performance_directions="Perform this scene with dry, understated humor running beneath the gravity. Awkward silences are comedic. The priest is slightly exasperated, the ritual faintly absurd. Tragedy is present but absurdity keeps breaking through.",
            ending_types=["ABSOLUTION", "REFUSAL", "FAITH_CRISIS", "UNEXPECTED_BOND", "DEFLECTION"],
            ending_weights={
                "ABSOLUTION": 0.2,
                "REFUSAL": 0.2,
                "FAITH_CRISIS": 0.25,
                "UNEXPECTED_BOND": 0.25,
                "DEFLECTION": 0.1,
            }
        ),
        Genre.DRAMA: GenreBlock(
            genre=Genre.DRAMA,
            performance_directions="Perform this scene with emotional depth and realism. Every word carries weight. Silences are pregnant with meaning. Focus on authenticity and emotional truth.",
            ending_types=["ABSOLUTION", "REFUSAL", "FAITH_CRISIS", "UNEXPECTED_BOND"],
            ending_weights={
                "ABSOLUTION": 0.3,
                "REFUSAL": 0.2,
                "FAITH_CRISIS": 0.3,
                "UNEXPECTED_BOND": 0.2,
            }
        ),
        Genre.THRILLER: GenreBlock(
            genre=Genre.THRILLER,
            performance_directions="Perform this scene with tension and urgency. Every exchange is a power struggle. Expect revelations and twists. Keep the audience on edge.",
            ending_types=["ABSOLUTION", "REFUSAL", "FAITH_CRISIS", "DEFLECTION"],
            ending_weights={
                "ABSOLUTION": 0.1,
                "REFUSAL": 0.4,
                "FAITH_CRISIS": 0.3,
                "DEFLECTION": 0.2,
            }
        ),
        Genre.COMEDY: GenreBlock(
            genre=Genre.COMEDY,
            performance_directions="Perform this scene for laughs. Look for every opportunity for humor - wordplay, physical comedy, absurdity. Keep it light and entertaining.",
            ending_types=["DEFLECTION", "UNEXPECTED_BOND"],
            ending_weights={
                "DEFLECTION": 0.5,
                "UNEXPECTED_BOND": 0.5,
            }
        ),
        Genre.TRAGEDY: GenreBlock(
            genre=Genre.TRAGEDY,
            performance_directions="Perform this scene with inevitability and doom. Each exchange moves inexorably toward catastrophe. Beauty emerges from despair.",
            ending_types=["FAITH_CRISIS", "REFUSAL", "ABSOLUTION"],
            ending_weights={
                "FAITH_CRISIS": 0.4,
                "REFUSAL": 0.4,
                "ABSOLUTION": 0.2,
            }
        ),
    }

    def __init__(self, scene_config: SceneConfig):
        """
        Initialize the orchestrator.

        Args:
            scene_config: Configuration for the scene
        """
        self.scene_config = scene_config
        self.agent_manager = AgentManager(
            llm_model=scene_config.llm_model,
            llm_server=scene_config.llm_server,
        )
        self.genre_block = self.GENRE_BLOCKS.get(
            scene_config.genre,
            self.GENRE_BLOCKS[Genre.DRAMA]  # default to drama
        )
        self.prompt_builder = PromptBuilder()
        self.dialogue_history: List[DialogueTurn] = []
        self.current_turn = 0

    def execute_scene(
        self,
        on_turn_callback: Optional[Callable[[DialogueTurn, DirectorState], None]] = None,
    ) -> SceneState:
        """
        Execute the scene from start to finish.

        Args:
            on_turn_callback: Callback function called after each turn with (dialogue, director_state)

        Returns:
            Final scene state
        """
        logger.info(f"Starting scene: {self.scene_config.title}")
        scene_state = SceneState(
            scene_id=f"{self.scene_config.title.replace(' ', '_')}_{int(time.time())}",
            config=self.scene_config,
            dialogue_history=[],
            current_speaker_index=0,
            is_running=True,
        )

        try:
            # Each turn is a complete round where each character gets a chance to speak
            for self.current_turn in range(1, self.scene_config.max_turns + 1):
                logger.info(f"Turn {self.current_turn}")

                for character_index in range(len(self.scene_config.characters)):
                    current_speaker = self.scene_config.characters[character_index]

                    # Get stage direction from previous director evaluation (if any)
                    stage_direction = ""
                    if scene_state.director_state:
                        stage_direction = scene_state.director_state.stage_direction

                    # Build this character's system prompt
                    character_prompt = self.prompt_builder.build_character_prompt(
                        current_speaker,
                        self.genre_block,
                        self.scene_config.scene_context,
                    )

                    # Get agent response
                    agent_response = self.agent_manager.get_agent_response(
                        character_name=current_speaker.name,
                        system_prompt=character_prompt,
                        dialogue_history=self.dialogue_history,
                        stage_direction=stage_direction,
                    )

                    # Add to dialogue history
                    turn = DialogueTurn(
                        turn_number=self.current_turn,
                        character_name=current_speaker.name,
                        dialogue=agent_response,
                        stage_direction=stage_direction,
                        timestamp=time.time(),
                    )
                    self.dialogue_history.append(turn)
                    scene_state.dialogue_history.append(turn)

                    # Get director evaluation
                    director_prompt = self.prompt_builder.build_director_prompt(
                        self.scene_config,
                        self.genre_block,
                    )
                    director_response = self.agent_manager.get_director_response(
                        director_system_prompt=director_prompt,
                        dialogue_history=self.dialogue_history,
                        current_turn_count=self.current_turn,
                    )

                    # Convert to DirectorState
                    scene_state.director_state = DirectorState(**director_response)

                    logger.info(f"Director state: arc={scene_state.director_state.emotional_arc}, "
                               f"end={scene_state.director_state.scene_end}")

                    # Call callback if provided
                    if on_turn_callback:
                        on_turn_callback(turn, scene_state.director_state)

                    # Check if scene should end
                    if self._should_end_scene(scene_state):
                        scene_state.completion_reason = f"Director called end at turn {self.current_turn}"
                        logger.info(f"Scene ended: {scene_state.completion_reason}")
                        break

                # Check if we should break out of the turn loop
                if self._should_end_scene(scene_state):
                    break

            if self.current_turn >= self.scene_config.max_turns:
                scene_state.completion_reason = f"Reached maximum turns ({self.scene_config.max_turns})"
                logger.info(f"Scene ended: {scene_state.completion_reason}")

            scene_state.is_running = False
            scene_state.is_completed = True

        except Exception as e:
            logger.error(f"Error during scene execution: {e}")
            scene_state.is_running = False
            scene_state.is_completed = True
            scene_state.completion_reason = f"Error: {str(e)}"
            raise

        return scene_state

    def _should_end_scene(self, scene_state: SceneState) -> bool:
        """
        Determine if the scene should end based on director state.

        Args:
            scene_state: Current scene state

        Returns:
            True if scene should end, False otherwise
        """
        if not scene_state.director_state:
            return False

        director = scene_state.director_state

        # Must have reached minimum turns
        if director.turn_count < self.scene_config.min_turns:
            return False

        # Director must request scene_end
        if not director.scene_end:
            return False

        # Must have reached at least "climax" in emotional arc
        arc_stages = ["opening", "tension", "climax", "resolution"]
        try:
            current_arc_index = arc_stages.index(director.emotional_arc)
            climax_index = arc_stages.index("climax")
            if current_arc_index < climax_index:
                return False
        except ValueError:
            # If we can't parse the arc, allow ending
            pass

        # Closure must be detected
        if not director.closure_detected:
            return False

        return True
