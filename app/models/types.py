"""
Data models for the Open Hollywood scene execution engine.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum


class Genre(str, Enum):
    """Available genres for scenes."""
    DARK_COMEDY = "dark_comedy"
    DRAMA = "drama"
    THRILLER = "thriller"
    COMEDY = "comedy"
    TRAGEDY = "tragedy"


class Character(BaseModel):
    """Represents a character in the scene."""
    name: str = Field(..., description="Character name")
    constitution: str = Field(..., description="Character system prompt / backstory")
    description: Optional[str] = Field(None, description="Brief character description")


class GenreBlock(BaseModel):
    """Genre-specific performance directions."""
    genre: Genre
    performance_directions: str = Field(..., description="How to perform in this genre")
    ending_types: List[str] = Field(
        ..., description="Possible ending types for this genre"
    )
    ending_weights: Dict[str, float] = Field(
        ..., description="Probability weights for each ending type"
    )


class SceneConfig(BaseModel):
    """Configuration for a scene execution."""
    title: str = Field(..., description="Scene title")
    genre: Genre = Field(..., description="Genre of the scene")
    characters: List[Character] = Field(..., description="Characters in the scene")
    scene_context: str = Field(..., description="Scene context and setup")
    director_system_prompt: str = Field(..., description="Director's system prompt")
    max_turns: int = Field(default=30, description="Maximum number of turns")
    min_turns: int = Field(default=6, description="Minimum turns before ending allowed")
    llm_model: str = Field(default="gemma3:4b", description="LLM model name")
    llm_server: str = Field(default="http://localhost:11434", description="Ollama server URL")
    temperature: float = Field(default=0.7, description="LLM temperature")
    top_p: float = Field(default=0.9, description="LLM top_p")
    repeat_penalty: float = Field(default=1.1, description="LLM repeat_penalty")


class DialogueTurn(BaseModel):
    """A single turn in the dialogue."""
    turn_number: int
    character_name: str
    dialogue: str
    stage_direction: Optional[str] = None
    timestamp: float


class DirectorState(BaseModel):
    """State tracked by the director agent."""
    turn_count: int
    emotional_arc: str
    arc_stages_hit: List[str]
    unresolved_threads: List[str]
    resolved_threads: List[str]
    closure_detected: bool
    ending_type: Optional[str] = None
    target_ending: Optional[str] = None
    pacing_notes: str = ""
    stage_direction: str = ""
    scene_end: bool = False


class SceneState(BaseModel):
    """Overall scene state."""
    scene_id: str
    config: SceneConfig
    dialogue_history: List[DialogueTurn]
    director_state: Optional[DirectorState] = None
    current_speaker_index: int = 0
    is_running: bool = False
    is_completed: bool = False
    completion_reason: Optional[str] = None
