from dataclasses import dataclass

from canvas_sdk.clients.llms.structures.settings.llm_settings import LlmSettings


@dataclass
class LlmSettingsAnthropic(LlmSettings):
    """Configuration settings for Anthropic Claude LLM API.

    Extends LlmSettings with Anthropic-specific parameters.

    Attributes:
        api_key: API authentication key for the LLM service (inherited).
        model: Name or identifier of the LLM model to use (inherited).
        temperature: Controls randomness in responses (0.0-1.0). None omits it from the request,
            which models from Claude Opus 4.7 onward require (they reject sampling parameters).
        max_tokens: Maximum number of tokens to generate, including thinking tokens.
    example:
        ```python3
        LlmSettingsAnthropic(
            api_key=environ.get("anthropic_key"),
            model="claude-opus-5-5",
            temperature=None,
            max_tokens=16000,
        )
        ```
    """

    temperature: float | None
    max_tokens: float

    def to_dict(self) -> dict:
        """Convert settings to Anthropic API request format.

        Returns:
            Dictionary containing model name, max_tokens, and temperature when set.
        """
        result = super().to_dict() | {"max_tokens": self.max_tokens}
        if self.temperature is not None:
            result["temperature"] = self.temperature
        return result


__exports__ = ("LlmSettingsAnthropic",)
