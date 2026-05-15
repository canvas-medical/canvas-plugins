from dataclasses import dataclass

from canvas_sdk.clients.llms.structures.settings.llm_settings import LlmSettings


@dataclass
class LlmSettingsGpt5(LlmSettings):
    """Configuration settings for OpenAI GPT-5 LLM API.

    Extends LlmSettings with GPT-5-specific parameters for reasoning and text generation.

    Attributes:
        api_key: API authentication key for the LLM service (inherited).
        model: Name or identifier of the LLM model to use (inherited).
        reasoning_effort: Level of reasoning effort ('none', 'low', 'medium', 'high').
        text_verbosity: Level of text verbosity in responses ('low', 'medium', 'high').

    Example:
        ```python3
        LlmSettingsGpt5(
            api_key=environ.get("openai_key"),
            model="gpt-5.1",
            reasoning_effort="none",
            text_verbosity="low",
        )
        ```
    """

    reasoning_effort: str
    text_verbosity: str

    def to_dict(self) -> dict:
        """Convert settings to OpenAI GPT-5 API request format.

        Returns:
            Dictionary containing model name, reasoning config, and text config.
        """
        return super().to_dict() | {
            "reasoning": {
                "effort": self.reasoning_effort,
            },
            "text": {
                "verbosity": self.text_verbosity,
            },
        }


__exports__ = ("LlmSettingsGpt5",)
