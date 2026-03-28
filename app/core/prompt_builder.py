"""
Prompt Builder: Assembles final system prompts from character, genre, and context blocks.
"""

from typing import Optional
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
    def build_director_briefing_prompt(
        scene_config: SceneConfig,
        genre_block: GenreBlock,
    ) -> str:
        """
        Build the director's pre-scene briefing prompt.

        Args:
            scene_config: Scene configuration
            genre_block: Genre-specific settings

        Returns:
            The briefing prompt
        """
        # Full character details for deep understanding
        character_details = "\n\n".join(
            f"CHARACTER: {c.name}\n{c.constitution}"
            for c in scene_config.characters
        )

        ending_options = "\n".join(
            f"- {et} (weight: {genre_block.ending_weights.get(et, 0)})"
            for et in genre_block.ending_types
        )

        prompt = f"""You are the Director of a theatrical scene. Before the scene begins, you must read 
everything below and make one creative decision: which ending this scene will build toward.

GENRE: {genre_block.genre.value.upper().replace('_', ' ')}
{genre_block.performance_directions}

SCENE CONTEXT:
{scene_config.scene_context}

CHARACTERS:
{character_details}

POSSIBLE ENDINGS (higher weight = more dramatically appropriate):
{ending_options}

Based on everything above, choose ONE ending and describe in 2-3 sentences how the scene 
should emotionally progress to reach it. Consider the characters' natures deeply — 
what would feel true to who they are?

Return ONLY this JSON:
{{
  "chosen_ending": "<ending type>",
  "pacing_notes": "<2-3 sentence emotional roadmap to reach this ending>"
}}"""
        return prompt.strip()

    @staticmethod
    def build_director_prompt(
        scene_config: SceneConfig,
        genre_block: GenreBlock,
        chosen_ending: Optional[str] = None,
        pacing_notes: str = "",
    ) -> str:
        """
        Build the director agent's system prompt.

        Args:
            scene_config: Scene configuration
            genre_block: Genre-specific settings
            chosen_ending: The pre-decided ending (if any)
            pacing_notes: The pre-decided pacing strategy (if any)

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

        if chosen_ending and pacing_notes:
            prompt += f"""

YOUR PRE-DECIDED VISION:
- TARGET ENDING: {chosen_ending}
- PACING VISION: {pacing_notes}

Your stage_direction must always steer characters toward {chosen_ending}, 
not toward collecting more plot details. You are a dramatist, not an interrogator.
Guide the emotional truth of the scene, not the factual record of events.
"""

        prompt += f"""

SAFETY LIMITS:
- Minimum {scene_config.min_turns} turns before allowing scene_end=true
- Maximum {scene_config.max_turns} turns total
- Only set scene_end=true when closure_detected is true AND emotional_arc has reached at least "climax"
"""
        return prompt.strip()
