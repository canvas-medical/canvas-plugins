from dataclasses import dataclass


@dataclass(frozen=True)
class Secrets:
    """Secret key names for LLM API credentials stored in the plugin secrets."""

    anthropic_key: str = "AnthropicKey"
    google_key: str = "GoogleKey"
    openai_key: str = "OpenaiKey"
