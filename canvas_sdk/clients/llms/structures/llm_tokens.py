from __future__ import annotations


class LlmTokens:
    """Token usage information for LLM API calls.

    Tracks the number of tokens used in prompts and generated responses.
    """

    def __init__(self, prompt: int, generated: int):
        """Initialize token counts.

        Args:
            prompt: Number of tokens in the prompt.
            generated: Number of tokens in the generated response.
        """
        self.prompt = prompt
        self.generated = generated

    def add(self, counts: LlmTokens) -> None:
        """Add token counts from another LlmTokens instance.

        Args:
            counts: Token counts to add to this instance.
        """
        self.prompt = self.prompt + counts.prompt
        self.generated = self.generated + counts.generated

    def __eq__(self, other: object) -> bool:
        """Compare two LlmTokens instances for equality.

        Args:
            other: Object to compare with.

        Returns:
            True if both prompt and generated counts are equal.
        """
        assert isinstance(other, LlmTokens)
        return self.prompt == other.prompt and self.generated == other.generated

    def to_dict(self) -> dict:
        """Convert token counts to a dictionary representation.

        Returns:
            Dictionary with 'prompt' and 'generated' keys.
        """
        return {
            "prompt": self.prompt,
            "generated": self.generated,
        }


__exports__ = ("LlmTokens",)
