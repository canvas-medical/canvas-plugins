from dataclasses import dataclass


@dataclass
class LlmSettings:
    """Configuration settings for an LLM API.

    Attributes:
        api_key: API authentication key for the LLM service.
        model: Name or identifier of the LLM model to use.
    """

    api_key: str
    model: str

    def to_dict(self) -> dict:
        """Convert settings to a dictionary representation.

        Returns:
            Dictionary containing the model name (excludes API key for security).
        """
        return {
            "model": self.model,
        }


__exports__ = ("LlmSettings",)
