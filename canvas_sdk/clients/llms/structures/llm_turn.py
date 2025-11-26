from __future__ import annotations

from typing import NamedTuple


class LlmTurn(NamedTuple):
    """A single conversation turn in an LLM interaction.

    Attributes:
        role: The role of the speaker (e.g., 'system', 'user', 'model').
        text: List of text strings for this turn.
    """

    role: str
    text: list[str]

    def to_dict(self) -> dict:
        """Convert the turn to a dictionary representation.

        Returns:
            Dictionary with 'role' and 'text' keys.
        """
        return {
            "role": self.role,
            "text": self.text,
        }

    @classmethod
    def load_from_dict(cls, dict_list: list[dict]) -> list[LlmTurn]:
        """Load a list of turns from a list of dictionaries.

        Args:
            dict_list: List of dictionaries, each containing 'role' and 'text' keys.

        Returns:
            List of LlmTurn instances created from the dictionaries.
        """
        return [
            LlmTurn(
                role=json_object.get("role") or "",
                text=json_object.get("text") or [],
            )
            for json_object in dict_list
        ]


__exports__ = ("LlmTurn",)
