from dataclasses import dataclass


@dataclass(frozen=True)
class Secrets:
    """Secret key names for the Extend AI PDF plugin."""

    extend_ai_key: str = "ExtendAiKey"
