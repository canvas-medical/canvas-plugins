from dataclasses import dataclass

from canvas_sdk.clients.llms.structures.settings.llm_settings import LlmSettings


@dataclass
class LlmSettingsGpt4(LlmSettings):
    """Configuration settings for OpenAI GPT-4 LLM API.

    Extends LlmSettings with GPT-4-specific parameters.

    Attributes:
        api_key: API authentication key for the LLM service (inherited).
        model: Name or identifier of the LLM model to use (inherited).
        temperature: Controls randomness in responses (0.0-1.0).

    Example:
        ```python3
        LlmSettingsGpt4(
            api_key=environ.get("openai_key"),
            model="gpt-4o",
            temperature=2.0,
        )
        ```
    """

    temperature: float

    def to_dict(self) -> dict:
        """Convert settings to OpenAI GPT-4 API request format.

        Returns:
            Dictionary containing model name and temperature.
        """
        return super().to_dict() | {
            "temperature": self.temperature,
        }


__exports__ = ("LlmSettingsGpt4",)
