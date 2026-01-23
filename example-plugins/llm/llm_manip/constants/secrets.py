from dataclasses import dataclass


@dataclass(frozen=True)
class Secrets:
    """Secret key names for LLM API credentials stored in the plugin secrets."""

    llm_key: str = "LlmKey"
