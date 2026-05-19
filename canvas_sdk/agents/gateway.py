import os
from dataclasses import dataclass
from typing import Any

DEFAULT_MODEL = "claude-sonnet-4-6"


class LLMGatewayConfigurationError(RuntimeError):
    """Raised when an LLMGateway can't be built because its credential source is empty."""


@dataclass
class LLMGateway:
    """LLM access handed to AgentPlugin.run().

    PoC: ``api_key`` holds a real Anthropic developer key; the plugin calls
    Anthropic directly with it. The key comes from one of two places
    depending on who's constructing the gateway:

    - The plugin-runner's ``RunAgent`` RPC builds the gateway for triggered
      agents using :meth:`from_environment` over the runner pod's env.
    - Plugin code (e.g. a chart-side chat surface) builds it for itself
      using :meth:`from_plugin_secrets` over ``self.secrets`` — the sandbox
      doesn't let plugin code read ``os.environ``.

    V1 (per the Agent Runner Framework doc §6.10): ``api_key`` becomes a
    short-lived session token and ``base_url`` points at the Canvas LLM
    gateway, which materializes the real per-customer subaccount key at
    the HTTP boundary and writes audit/cost rows there. The factory
    methods below are the forward-compat seam — their bodies change, the
    call sites in plugin and plugin-runner code stay the same.
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

        Used by plugin code (SimpleAPI / Application handlers, etc.) that
        invokes an :class:`AgentPlugin` inline within a single request.
        The plugin's ``self.secrets`` is populated from manifest-declared
        ``variables[]`` entries and configured per-customer in home-app
        admin.

        Args:
            secrets: The plugin handler's ``self.secrets`` dict.
            key_name: Name of the secret carrying the API key. Defaults to
                ``"ANTHROPIC_API_KEY"`` — the canonical name for plugins
                using this helper unchanged.
            model_name: Name of the secret carrying the model identifier.
                Optional in the secrets dict; ``default_model`` is used
                when absent or empty.
            default_model: Fallback model when ``model_name`` isn't set.

        Raises:
            LLMGatewayConfigurationError: If ``key_name`` is missing or
                empty in ``secrets``. Plugin authors should surface this
                as a user-facing error directing the customer to the
                plugin's secrets-config page.
        """
        api_key = secrets.get(key_name)
        if not api_key:
            raise LLMGatewayConfigurationError(
                f"LLM API key missing: plugin secret {key_name!r} is not set. "
                f"Configure it in the plugin's admin page."
            )
        model = secrets.get(model_name) or default_model
        return cls(api_key=api_key, model=model)

    @classmethod
    def from_environment(
        cls,
        *,
        key_name: str = "ANTHROPIC_DEV_API_KEY",
        model_name: str = "ANTHROPIC_DEV_MODEL",
        default_model: str = DEFAULT_MODEL,
        env: dict[str, str] | None = None,
    ) -> "LLMGateway":
        """Build a gateway from process environment variables.

        Used by platform code (the plugin-runner's ``RunAgent`` RPC, etc.)
        that has access to ``os.environ``. Plugin code cannot import
        ``os`` in the sandbox; plugin code should use
        :meth:`from_plugin_secrets` instead.

        Args:
            key_name: Environment variable holding the API key. Defaults to
                ``"ANTHROPIC_DEV_API_KEY"`` — the PoC's pod-env path.
            model_name: Environment variable holding the model identifier.
                Optional; ``default_model`` is used when absent.
            default_model: Fallback model when ``model_name`` isn't set.
            env: Optional environment dict (for tests). Defaults to
                ``os.environ``.

        Raises:
            LLMGatewayConfigurationError: If ``key_name`` is missing or
                empty in the environment.
        """
        source = env if env is not None else os.environ
        api_key = source.get(key_name)
        if not api_key:
            raise LLMGatewayConfigurationError(
                f"LLM API key missing: environment variable {key_name!r} is not set."
            )
        model = source.get(model_name) or default_model
        return cls(api_key=api_key, model=model)


__exports__ = ("LLMGateway", "LLMGatewayConfigurationError")
