from dataclasses import dataclass

from canvas_sdk.clients.llms.structures.settings.llm_settings import LlmSettings


@dataclass
class LlmSettingsAnthropic(LlmSettings):
    """Configuration settings for Anthropic Claude LLM API.

    Extends LlmSettings with Anthropic-specific parameters.

    Attributes:
        api_key: API authentication key for the LLM service (inherited).
        model: Name or identifier of the LLM model to use (inherited).
        temperature: Controls randomness in responses (0.0-1.0).
        max_tokens: Maximum number of tokens to generate.
    example:
        ```python3
        LlmSettingsAnthropic(
            api_key=environ.get("anthropic_key"),
            model="claude-sonnet-4-5-20250929",
            temperature=0.78,
            max_tokens=8192,
        )
        ```
    """

    temperature: float
    max_tokens: float

    def to_dict(self) -> dict:
        """Convert settings to Anthropic API request format.

        Returns:
            Dictionary containing model name, temperature, and max_tokens.
        """
        return super().to_dict() | {
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }


__exports__ = ("LlmSettingsAnthropic",)
