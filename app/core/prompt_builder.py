"""
Prompt Builder: Assembles final system prompts from character, genre, and context blocks.
"""

from app.models.types import Character, GenreBlock, SceneConfig


class PromptBuilder:
    """Constructs system prompts by combining character, genre, and scene context."""

    @staticmethod
    def build_character_prompt(
        character: Character,
        genre_block: GenreBlock,
        scene_context: str,
    ) -> str:
        """
        Build the final system prompt for a character.

        Args:
            character: Character definition with constitution
            genre_block: Genre-specific performance directions
            scene_context: The scene context and setup

        Returns:
            The assembled system prompt
        """
        prompt = f"""{character.constitution}

SCENE CONTEXT:
{scene_context}

GENRE: {genre_block.genre.value.upper().replace('_', ' ')}
{genre_block.performance_directions}

CRITICAL INSTRUCTIONS FOR THIS TURN:
- Generate ONLY your character's next line of dialogue for this turn
- Do not generate dialogue for other characters
- Do not generate stage directions, narration, or scene descriptions
- Do not write in asterisks (*), brackets, or action descriptions
- Do not start with your character name (just the dialogue)
- Respond naturally and maintain the conversation flow based on what was said before
"""
        return prompt.strip()

    @staticmethod
    def build_director_prompt(
        scene_config: SceneConfig,
        genre_block: GenreBlock,
    ) -> str:
        """
        Build the director agent's system prompt.

        Args:
            scene_config: Scene configuration
            genre_block: Genre-specific settings

        Returns:
            The director system prompt
        """
        ending_types_str = ", ".join(
            [f'"{et}"' for et in genre_block.ending_types]
        )

        prompt = f"""{scene_config.director_system_prompt}

SCENE SETUP:
{scene_config.scene_context}

POSSIBLE ENDING TYPES FOR THIS GENRE:
{', '.join(genre_block.ending_types)}

ENDING PREFERENCES (higher = more likely):
"""
        for ending_type, weight in genre_block.ending_weights.items():
            prompt += f"\n  - {ending_type}: {weight}"

        prompt += f"""

SAFETY LIMITS:
- Minimum {scene_config.min_turns} turns before allowing scene_end=true
- Maximum {scene_config.max_turns} turns total
- Only set scene_end=true when closure_detected is true AND emotional_arc has reached at least "climax"
"""
        return prompt.strip()
