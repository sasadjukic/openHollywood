"""
LLM Provider abstraction layer supporting multiple providers via URI-based model naming.

Model URI format: "provider://model-identifier"
Examples:
  - ollama://gemma4:e4b (local Ollama server)
  - openai://gpt-4-turbo (OpenAI GPT-4)
  - anthropic://claude-3-opus (Anthropic Claude)
  - google://gemini-2.0-pro (Google Gemini)

Backward compatibility: Plain model names (e.g., "gemma4:e4b") are treated as "ollama://gemma4:e4b"
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import os
import logging

logger = logging.getLogger(__name__)


@dataclass
class ChatMessage:
    """Represents a single message in the chat history."""
    role: str  # "user", "assistant", "system"
    content: str


@dataclass
class ChatResponse:
    """Unified response format from any LLM provider."""
    message: str
    stop_reason: str
    provider: str


class LLMClient(ABC):
    """Abstract base class for all LLM providers."""

    @abstractmethod
    def chat(
        self,
        messages: List[ChatMessage],
        model_name: str,
        options: Optional[Dict[str, Any]] = None,
    ) -> ChatResponse:
        """
        Send a chat request to the LLM (synchronous).

        Args:
            messages: List of chat messages
            model_name: Model identifier (with or without provider prefix)
            options: Optional parameters (temperature, top_p, etc.)

        Returns:
            ChatResponse with unified format

        Note: This is synchronous for backward compatibility. 
              Future versions will support async via async_chat().
        """
        pass


class OllamaClient(LLMClient):
    """Client for local Ollama server."""

    def __init__(self, server_url: str = "http://localhost:11434"):
        """
        Initialize Ollama client.

        Args:
            server_url: Base URL of Ollama server (default: http://localhost:11434)
        """
        self.server_url = server_url
        # Import here to avoid dependency if only using cloud providers
        try:
            import ollama
            self.client = ollama.Client(host=server_url)
        except ImportError:
            raise ImportError(
                "ollama package not installed. "
                "Install with: pip install ollama"
            )

    def chat(
        self,
        messages: List[ChatMessage],
        model_name: str,
        options: Optional[Dict[str, Any]] = None,
    ) -> ChatResponse:
        """
        Send a chat request to Ollama (synchronous).

        Args:
            messages: List of chat messages
            model_name: Ollama model identifier (e.g., "gemma4:e4b" or "ollama://gemma4:e4b")
            options: Optional parameters

        Returns:
            ChatResponse with message and stop_reason
        """
        # Extract just the model name from URI if present (e.g., "ollama://gemma4:e4b" -> "gemma4:e4b")
        if "://" in model_name:
            _, actual_model_name = model_name.split("://", 1)
        else:
            actual_model_name = model_name
        
        # Convert ChatMessage objects to dict format for Ollama
        formatted_messages = [
            {"role": msg.role, "content": msg.content} for msg in messages
        ]

        # Default options for Ollama
        ollama_options = {
            "temperature": 0.7,
            "top_p": 0.9,
            "repeat_penalty": 1.1,
        }
        if options:
            ollama_options.update(options)

        try:
            response = self.client.chat(
                model=actual_model_name,
                messages=formatted_messages,
                stream=False,
                options=ollama_options,
            )
            return ChatResponse(
                message=response.get("message", {}).get("content", ""),
                stop_reason=response.get("stop_reason", "end_turn"),
                provider="ollama",
            )
        except Exception as e:
            logger.error(f"Ollama chat error: {e}")
            raise

    def check_model_available(self, model_name: str) -> bool:
        """Check if a model is available locally."""
        try:
            models = self.client.list()
            available_models = [m["name"].split(":")[0] for m in models.get("models", [])]
            return model_name.split(":")[0] in available_models
        except Exception as e:
            logger.warning(f"Could not check model availability: {e}")
            return False


class OpenAIClient(LLMClient):
    """Stub for OpenAI API client."""

    def __init__(self):
        """Initialize OpenAI client."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.warning(
                "OPENAI_API_KEY not found in environment. "
                "OpenAI models will not be available."
            )
        self.api_key = api_key
        self._client_available = api_key is not None

    def chat(
        self,
        messages: List[ChatMessage],
        model_name: str,
        options: Optional[Dict[str, Any]] = None,
    ) -> ChatResponse:
        """
        Send a chat request to OpenAI (stub implementation).

        This is a placeholder for future implementation.
        """
        if not self._client_available:
            raise RuntimeError(
                "OpenAI API key not configured. "
                "Set OPENAI_API_KEY environment variable."
            )

        # Placeholder: full implementation pending
        # from openai import AsyncOpenAI
        # client = AsyncOpenAI(api_key=self.api_key)
        # ...message formatting and API call...

        raise NotImplementedError(
            "OpenAI client support is not yet implemented. "
            "Please use local Ollama models or contribute an implementation."
        )


class AnthropicClient(LLMClient):
    """Stub for Anthropic Claude API client."""

    def __init__(self):
        """Initialize Anthropic client."""
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            logger.warning(
                "ANTHROPIC_API_KEY not found in environment. "
                "Anthropic Claude models will not be available."
            )
        self.api_key = api_key
        self._client_available = api_key is not None

    def chat(
        self,
        messages: List[ChatMessage],
        model_name: str,
        options: Optional[Dict[str, Any]] = None,
    ) -> ChatResponse:
        """
        Send a chat request to Anthropic (stub implementation).

        This is a placeholder for future implementation.
        """
        if not self._client_available:
            raise RuntimeError(
                "Anthropic API key not configured. "
                "Set ANTHROPIC_API_KEY environment variable."
            )

        # Placeholder: full implementation pending
        # from anthropic import Anthropic
        # client = Anthropic(api_key=self.api_key)
        # ...message formatting and API call...

        raise NotImplementedError(
            "Anthropic client support is not yet implemented. "
            "Please use local Ollama models or contribute an implementation."
        )


class GoogleClient(LLMClient):
    """Stub for Google Gemini API client."""

    def __init__(self):
        """Initialize Google client."""
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            logger.warning(
                "GOOGLE_API_KEY not found in environment. "
                "Google Gemini models will not be available."
            )
        self.api_key = api_key
        self._client_available = api_key is not None

    def chat(
        self,
        messages: List[ChatMessage],
        model_name: str,
        options: Optional[Dict[str, Any]] = None,
    ) -> ChatResponse:
        """
        Send a chat request to Google (stub implementation).

        This is a placeholder for future implementation.
        """
        if not self._client_available:
            raise RuntimeError(
                "Google API key not configured. "
                "Set GOOGLE_API_KEY environment variable."
            )

        # Placeholder: full implementation pending
        # from google.generativeai import GenerativeModel
        # client = GenerativeModel(model_name)
        # ...message formatting and API call...

        raise NotImplementedError(
            "Google Gemini client support is not yet implemented. "
            "Please use local Ollama models or contribute an implementation."
        )


class LLMClientFactory:
    """Factory for creating LLM clients based on URI-style model names."""

    # Mapping of provider prefixes to client classes
    _providers = {
        "ollama": OllamaClient,
        "openai": OpenAIClient,
        "anthropic": AnthropicClient,
        "google": GoogleClient,
    }

    # Cache for client instances
    _client_cache: Dict[str, LLMClient] = {}

    @classmethod
    def parse_model_uri(cls, model_uri: str) -> tuple[str, str]:
        """
        Parse a model URI into provider and model name.

        Format: "provider://model-name" or plain "model-name" for Ollama default

        Args:
            model_uri: Full model URI or plain model name

        Returns:
            Tuple of (provider, model_name)

        Examples:
            "ollama://gemma4:e4b" -> ("ollama", "gemma4:e4b")
            "openai://gpt-4" -> ("openai", "gpt-4")
            "gemma4:e4b" -> ("ollama", "gemma4:e4b")  # Backward compat
        """
        if "://" in model_uri:
            provider, model_name = model_uri.split("://", 1)
            return provider.lower(), model_name
        else:
            # Backward compatibility: plain model names default to Ollama
            return "ollama", model_uri

    @classmethod
    def create(cls, model_uri: str, **kwargs) -> LLMClient:
        """
        Create or retrieve a cached LLM client for the given model URI.

        Args:
            model_uri: Full model URI (e.g., "ollama://gemma4:e4b")
            **kwargs: Provider-specific initialization arguments

        Returns:
            LLMClient instance for the specified provider

        Raises:
            ValueError: If provider is not supported
            RuntimeError: If provider is available but misconfigured
        """
        provider, model_name = cls.parse_model_uri(model_uri)

        # Check cache first (keyed by provider, not model)
        if provider in cls._client_cache:
            return cls._client_cache[provider]

        if provider not in cls._providers:
            raise ValueError(
                f"Unsupported LLM provider: '{provider}'. "
                f"Supported providers: {', '.join(cls._providers.keys())}"
            )

        try:
            client_class = cls._providers[provider]
            client = client_class(**kwargs)
            cls._client_cache[provider] = client
            logger.info(f"Created {provider} LLM client")
            return client
        except Exception as e:
            logger.error(f"Failed to create {provider} client: {e}")
            raise

    @classmethod
    def reset_cache(cls):
        """Clear the client cache (useful for testing)."""
        cls._client_cache.clear()

    @classmethod
    def get_supported_providers(cls) -> List[str]:
        """Return list of supported provider names."""
        return list(cls._providers.keys())
