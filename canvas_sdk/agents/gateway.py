from dataclasses import dataclass
from typing import Any

DEFAULT_MODEL = "claude-sonnet-4-6"


class LLMGatewayConfigurationError(RuntimeError):
    """Raised when an LLMGateway can't be built because its credential source is empty."""


@dataclass
class LLMGateway:
    """LLM access handed to AgentPlugin.run().

    PoC: ``api_key`` holds a real Anthropic developer key sourced from a
    plugin secret; the plugin calls Anthropic directly with it. There is
    deliberately only one credential source — the plugin's
    ``self.secrets`` — for both invocation paths (the platform's
    ``RunAgent`` RPC for triggered agents, and inline invocation by
    plugin code for chat-style agents). Plugin authors configure the key
    once per plugin in home-app admin; they never see the container
    environment.

    V1 (per the Agent Runner Framework doc §6.10): ``api_key`` becomes a
    short-lived session token and ``base_url`` points at the Canvas LLM
    gateway, which materializes the real per-customer subaccount key at
    the HTTP boundary and writes audit/cost rows there.
    :meth:`from_plugin_secrets` is the forward-compat seam — its body
    changes to mint a session token from the gateway service, call sites
    stay stable.
    """

    api_key: str
    model: str
    base_url: str | None = None

    @classmethod
    def from_plugin_secrets(
        cls,
        secrets: dict[str, Any],
        *,
        key_name: str = "ANTHROPIC_API_KEY",
        model_name: str = "ANTHROPIC_MODEL",
        default_model: str = DEFAULT_MODEL,
    ) -> "LLMGateway":
        """Build a gateway from a plugin's secrets dict.

        The single supported construction path. Used by:

        - Plugin code (SimpleAPI / Application handlers, etc.) that
          invokes an :class:`AgentPlugin` inline — ``self.secrets`` is
          populated from manifest-declared ``variables[]`` entries and
          configured per-customer in home-app admin.
        - The platform's ``RunAgent`` RPC for triggered agents —
          ``LOADED_PLUGINS[key]["secrets"]`` is the same secrets dict the
          plugin's own handlers receive.

        Args:
            secrets: The plugin's secrets dict.
            key_name: Name of the secret carrying the API key. Defaults
                to ``"ANTHROPIC_API_KEY"`` — the canonical name plugins
                using this helper unchanged should pick.
            model_name: Name of the secret carrying the model identifier.
                Optional in the secrets dict; ``default_model`` is used
                when absent or empty.
            default_model: Fallback model when ``model_name`` isn't set.

        Raises:
            LLMGatewayConfigurationError: If ``key_name`` is missing or
                empty in ``secrets``. Callers should surface this as a
                user-facing error directing the customer to the plugin's
                secrets-config page.
        """
        api_key = secrets.get(key_name)
        if not api_key:
            raise LLMGatewayConfigurationError(
                f"LLM API key missing: plugin secret {key_name!r} is not set. "
                f"Configure it in the plugin's admin page."
            )
        model = secrets.get(model_name) or default_model
        return cls(api_key=api_key, model=model)


__exports__ = ("LLMGateway", "LLMGatewayConfigurationError")
