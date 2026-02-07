"""Configuration for the Gemini AI Agent.

Contains settings for model selection, temperature, and other
agent parameters.
"""

import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class AgentConfig:
    """Configuration settings for the AI agent."""

    # Model configuration - using Gemini 2.5 Flash (free tier)
    model: str = "gemini-2.5-flash"
    temperature: float = 0.7
    max_tokens: int = 1000

    # API configuration
    api_key: Optional[str] = None

    def __post_init__(self):
        """Load API key from environment if not provided."""
        if self.api_key is None:
            self.api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

    def validate(self) -> bool:
        """Validate the configuration.

        Returns:
            True if configuration is valid

        Raises:
            ValueError: If configuration is invalid
        """
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY is required")

        if self.temperature < 0 or self.temperature > 2:
            raise ValueError("Temperature must be between 0 and 2")

        if self.max_tokens < 1:
            raise ValueError("Max tokens must be at least 1")

        return True


# Default configuration instance
default_config = AgentConfig()


def get_agent_config() -> AgentConfig:
    """Get the default agent configuration.

    Returns:
        AgentConfig instance with default or environment-based settings
    """
    return default_config
