"""
Configuration and constants for the Open Hollywood system.
"""

from enum import Enum
from typing import Dict, List


class EndingType(str, Enum):
    """Generic ending types that can be customized per scene."""
    ABSOLUTION = "ABSOLUTION"
    REFUSAL = "REFUSAL"
    FAITH_CRISIS = "FAITH_CRISIS"
    UNEXPECTED_BOND = "UNEXPECTED_BOND"
    DEFLECTION = "DEFLECTION"
    RESOLUTION = "RESOLUTION"
    CONFLICT = "CONFLICT"
    DISCONNECTION = "DISCONNECTION"


class EmotionalArcStage(str, Enum):
    """Standard emotional arc stages."""
    OPENING = "opening"
    TENSION = "tension"
    CLIMAX = "climax"
    RESOLUTION = "resolution"


# LLM Provider Configuration
# Model URIs follow the format: "provider://model-identifier"
# Examples: "ollama://gemma4:e4b", "openai://gpt-4", "anthropic://claude-3-opus"
OLLAMA_CONFIG = {
    "default_model": "ollama://gemma4:e4b",
    "default_server": "http://localhost:11434",
    "timeout": 300,  # seconds
}

# Cloud Provider API Configuration
# These are sourced from environment variables at runtime:
# - OPENAI_API_KEY for OpenAI models
# - ANTHROPIC_API_KEY for Anthropic Claude models
# - GOOGLE_API_KEY for Google Gemini models
PROVIDER_CONFIG = {
    "openai": {
        "env_var": "OPENAI_API_KEY",
        "endpoint": "https://api.openai.com/v1",
    },
    "anthropic": {
        "env_var": "ANTHROPIC_API_KEY",
        "endpoint": "https://api.anthropic.com",
    },
    "google": {
        "env_var": "GOOGLE_API_KEY",
        "endpoint": "https://generativelanguage.googleapis.com",
    },
}

# Scene Execution Configuration
SCENE_CONFIG = {
    "default_max_turns": 30,
    "default_min_turns": 6,
    "turn_delay": 0.1,  # seconds between turns for UI (allows streaming)
}

# UI Configuration
UI_CONFIG = {
    "host": "127.0.0.1",
    "port": 8000,
    "auto_reload": False,
}

# Logging Configuration
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
}

# Genre-specific configurations can be extended here
GENRE_DESCRIPTIONS = {
    "dark_comedy": "Dry, understated humor beneath gravity. Absurdity breaks through tragedy.",
    "drama": "Emotional depth and authenticity. Every word carries weight.",
    "thriller": "Tension and urgency. Every exchange is a power struggle.",
    "comedy": "Light and entertaining. Look for every opportunity for laughs.",
    "tragedy": "Inevitability and doom. Each exchange moves toward catastrophe.",
}

# Character base attributes (can be extended)
CHARACTER_BASE_ATTRIBUTES = [
    "age",
    "occupation",
    "background",
    "personality_traits",
    "speech_patterns",
    "motivations",
    "secrets",
]
