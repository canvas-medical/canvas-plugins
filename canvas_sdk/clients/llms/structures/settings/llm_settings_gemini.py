from dataclasses import dataclass

from canvas_sdk.clients.llms.structures.settings.llm_settings import LlmSettings


@dataclass
class LlmSettingsGemini(LlmSettings):
    """Configuration settings for Google Gemini LLM API.

    Extends LlmSettings with Gemini-specific parameters.

    Attributes:
        api_key: API authentication key for the LLM service (inherited).
        model: Name or identifier of the LLM model to use (inherited).
        temperature: Controls randomness in responses (0.0-1.0).

    Example:
        ```python3
        LlmSettingsGemini(
            api_key=environ.get("google_key"),
            model="models/gemini-2.0-flash",
            temperature=2.0,
        )
        ```
    """

    temperature: float

    def to_dict(self) -> dict:
        """Convert settings to Google Gemini API request format.

        Returns:
            Dictionary containing model name and generationConfig with temperature.
        """
        return super().to_dict() | {
            "generationConfig": {"temperature": self.temperature},
        }


__exports__ = ("LlmSettingsGemini",)
