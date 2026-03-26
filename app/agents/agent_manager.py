"""
Agent Manager: Handles LLM calls for character agents.
"""

import json
import logging
from typing import List, Tuple
import ollama

from app.models.types import DialogueTurn

logger = logging.getLogger(__name__)


class AgentManager:
    """Manages individual agent LLM calls."""

    def __init__(self, llm_model: str = "gemma3:4b", llm_server: str = "http://localhost:11434"):
        """
        Initialize the agent manager.

        Args:
            llm_model: Name of the LLM model to use
            llm_server: URL to the Ollama server
        """
        self.llm_model = llm_model
        self.llm_server = llm_server
        self.client = ollama.Client(host=llm_server)

    def _clean_agent_response(self, response: str, character_name: str) -> str:
        """
        Clean agent response to ensure it contains only dialogue for this turn.
        
        Args:
            response: Raw response from LLM
            character_name: Character name for logging
            
        Returns:
            Cleaned dialogue response
        """
        # Remove leading/trailing whitespace
        response = response.strip()
        
        # If response starts with character name followed by colon, remove it
        if response.startswith(character_name + ":"):
            response = response[len(character_name) + 1:].strip()
        
        # Remove common stage direction markers
        # Remove lines that are purely stage directions (in asterisks or brackets)
        lines = response.split('\n')
        dialogue_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Skip lines that are purely action/stage directions
            if (line.startswith('*') and line.endswith('*')) or \
               (line.startswith('[') and line.endswith(']')) or \
               (line.startswith('(') and line.endswith(')')):
                continue
            
            # Skip lines that are other characters speaking
            if ':' in line:
                potential_name, _ = line.split(':', 1)
                if potential_name.strip() and potential_name.strip() != character_name:
                    # This looks like another character speaking, skip it
                    continue
            
            dialogue_lines.append(line)
        
        # Join dialogue lines back together
        cleaned = ' '.join(dialogue_lines)
        
        # Limit to first few sentences to ensure single turn
        sentences = cleaned.split('.')
        if len(sentences) > 4:  # Allow up to 3-4 sentences
            cleaned = '.'.join(sentences[:3]) + '.' if sentences[0] else ''
        
        return cleaned.strip()

    def get_agent_response(
        self,
        character_name: str,
        system_prompt: str,
        dialogue_history: List[DialogueTurn],
        stage_direction: str = "",
        llm_options: dict = None,
    ) -> str:
        """
        Get a response from an agent.

        Args:
            character_name: Name of the character (for logging)
            system_prompt: The character's system prompt
            dialogue_history: Conversation history so far
            stage_direction: Optional director's stage direction
            llm_options: Optional LLM parameters (temperature, top_p, etc.)

        Returns:
            The agent's response dialogue
        """
        # Build the conversation history for this agent's perspective
        # Each agent sees the other's lines as "user" messages
        messages = []

        # Add system prompt as first message
        messages.append({
            "role": "system",
            "content": system_prompt
        })

        for turn in dialogue_history:
            if turn.character_name == character_name:
                # This character's own lines
                messages.append({
                    "role": "assistant",
                    "content": turn.dialogue
                })
            else:
                # Other character's lines appear as user input
                messages.append({
                    "role": "user",
                    "content": turn.dialogue
                })

        # If we have a stage direction from the director, add it to context
        if stage_direction:
            context_msg = f"[Director's note: {stage_direction}]"
            messages.append({
                "role": "user",
                "content": context_msg
            })

        logger.info(f"Calling LLM for {character_name} with {len(messages)} messages")

        try:
            response = self.client.chat(
                model=self.llm_model,
                messages=messages,
                stream=False,
                options=llm_options,
            )

            # Extract the response text
            agent_response = response["message"]["content"].strip()
            
            # Clean the response to ensure it's just dialogue for this turn
            agent_response = self._clean_agent_response(agent_response, character_name)
            
            logger.info(f"{character_name} responded: {agent_response[:100]}...")

            return agent_response

        except Exception as e:
            logger.error(f"Error calling LLM for {character_name}: {e}")
            raise

    def parse_director_response(self, response_text: str) -> dict:
        """
        Parse the director agent's JSON response.

        Args:
            response_text: The raw response from the director agent

        Returns:
            Parsed JSON as dictionary

        Raises:
            ValueError: If response cannot be parsed as valid JSON
        """
        try:
            # Try to extract JSON from the response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1

            if json_start == -1 or json_end == 0:
                logger.warning(f"No JSON found in director response, using defaults")
                logger.debug(f"Response was: {response_text[:200]}")
                return self._normalize_director_fields({
                    'turn_count': 0,
                    'emotional_arc': 'resolution',
                    'closure_detected': True,
                    'scene_end': True,
                    'ending_type': None,
                    'stage_direction': '',
                    'arc_stages_hit': ['opening', 'tension', 'climax', 'resolution'],
                    'unresolved_threads': [],
                    'resolved_threads': []
                })

            json_str = response_text[json_start:json_end]
            parsed = json.loads(json_str)
            
            return self._normalize_director_fields(parsed)

        except json.JSONDecodeError as e:
            logger.debug(f"Failed to parse director JSON: {e}")
            logger.debug(f"Response was: {response_text[:500]}")
            
            # Try to fix unescaped control characters
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            if json_start != -1 and json_end > 0:
                json_str = response_text[json_start:json_end]
                
                # More robust control character fixing:
                # Replace control characters (except within already-escaped sequences)
                fixed_chars = []
                i = 0
                while i < len(json_str):
                    ch = json_str[i]
                    
                    # Check for control characters that need escaping
                    if ch == '\n':
                        fixed_chars.append('\\n')
                    elif ch == '\r':
                        fixed_chars.append('\\r')
                    elif ch == '\t':
                        fixed_chars.append('\\t')
                    elif ch == '\b':
                        fixed_chars.append('\\b')
                    elif ch == '\f':
                        fixed_chars.append('\\f')
                    elif ord(ch) < 32:  # Other control characters
                        fixed_chars.append(f'\\u{ord(ch):04x}')
                    else:
                        fixed_chars.append(ch)
                    i += 1
                
                fixed_str = ''.join(fixed_chars)
                try:
                    parsed = json.loads(fixed_str)
                    logger.info("Successfully parsed JSON after fixing control characters")
                    return self._normalize_director_fields(parsed)
                except json.JSONDecodeError as e2:
                    logger.error(f"Still failed after control character fix: {e2}")
                    # As last resort, return defaults
                    logger.warning("Falling back to default director state")
                    return self._normalize_director_fields({
                        'turn_count': 0,
                        'emotional_arc': 'resolution',
                        'closure_detected': True,
                        'scene_end': True,
                        'ending_type': None,
                        'stage_direction': '',
                        'arc_stages_hit': ['opening', 'tension', 'climax', 'resolution'],
                        'unresolved_threads': [],
                        'resolved_threads': []
                    })
            
            # If we can't extract JSON at all, return defaults
            logger.warning("Could not extract JSON from director response, using defaults")
            return self._normalize_director_fields({
                'turn_count': 0,
                'emotional_arc': 'resolution',
                'closure_detected': True,
                'scene_end': True,
                'ending_type': None,
                'stage_direction': '',
                'arc_stages_hit': ['opening', 'tension', 'climax', 'resolution'],
                'unresolved_threads': [],
                'resolved_threads': []
            })

    def _normalize_director_fields(self, parsed: dict) -> dict:
        """Helper to normalize director response fields."""
        normalized = {}
        
        field_mappings = {
            'turn': 'turn_count',
            'scene_turn': 'turn_count',
            'stage': 'emotional_arc',
            'emotional_arc_stage': 'emotional_arc',
            'threads': 'unresolved_threads',
            'current_turn': 'turn_count',
            'current_stage': 'emotional_arc',
        }
        
        for key, value in parsed.items():
            if key in ['dialogue', 'scene_summary']:
                # Skip these unexpected fields
                continue
            
            # Special handling for ending_preference dict - extract highest probability ending
            if key == 'ending_preference' and isinstance(value, dict) and value:
                normalized['ending_type'] = max(value.items(), key=lambda x: x[1])[0]
            # Skip ending_type if it's not a string (e.g., float probability value)
            elif key == 'ending_type':
                if isinstance(value, str):
                    normalized['ending_type'] = value
                # else: skip non-string values
            else:
                correct_key = field_mappings.get(key, key)
                normalized[correct_key] = value
        
        # Provide sensible defaults for all required fields
        if 'turn_count' not in normalized:
            normalized['turn_count'] = 0
        if 'emotional_arc' not in normalized:
            normalized['emotional_arc'] = "resolution"  # Fallback to final stage
        if 'closure_detected' not in normalized:
            normalized['closure_detected'] = False
        if 'scene_end' not in normalized:
            normalized['scene_end'] = False
        if 'arc_stages_hit' not in normalized:
            normalized['arc_stages_hit'] = []
        if 'unresolved_threads' not in normalized:
            normalized['unresolved_threads'] = []
        if 'resolved_threads' not in normalized:
            normalized['resolved_threads'] = []
        if 'stage_direction' not in normalized:
            normalized['stage_direction'] = ""
        if 'ending_type' not in normalized or normalized.get('ending_type') is None:
            normalized['ending_type'] = None
        
        return normalized

    def get_director_response(
        self,
        director_system_prompt: str,
        dialogue_history: List[DialogueTurn],
        current_turn_count: int,
        llm_options: dict = None,
    ) -> dict:
        """
        Get the director agent's scene state evaluation.

        Args:
            director_system_prompt: Director's system prompt
            dialogue_history: Full conversation history
            current_turn_count: Current turn number
            llm_options: Optional LLM parameters (temperature, top_p, etc.)

        Returns:
            Parsed director state dictionary
        """
        # Build conversation for director (sees full dialogue)
        dialogue_text = "\n".join([
            f"{turn.character_name}: {turn.dialogue}"
            for turn in dialogue_history
        ])

        messages = [
            {
                "role": "user",
                "content": f"""Evaluate this scene after turn {current_turn_count}:

{dialogue_text}

Return ONLY valid JSON with no other text."""
            }
        ]

        logger.info(f"Calling director agent for turn {current_turn_count}")

        try:
            response = self.client.chat(
                model=self.llm_model,
                messages=[
                    {
                        "role": "system",
                        "content": director_system_prompt
                    }
                ] + messages,
                stream=False,
                options=llm_options,
            )

            response_text = response["message"]["content"].strip()
            logger.info(f"Director response: {response_text[:200]}...")

            return self.parse_director_response(response_text)

        except Exception as e:
            logger.error(f"Error getting director response: {e}")
            raise
