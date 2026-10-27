"""LLM access for agents, through Canvas's inference gateway.

The plugin runner builds an :class:`LLMGateway` from the instance's
``INFERENCE_GATEWAY_URL`` and the agent plugin's own ``INFERENCE_GATEWAY_KEY`` secret,
which the plugin declares in its manifest ``variables`` with ``sensitive: true``.
:meth:`LLMGateway.client` returns an ``anthropic.Anthropic`` client pointed at the
gateway with that key and the runner's attribution headers.
"""

import os
from collections.abc import Mapping
from dataclasses import dataclass, field

from anthropic import Anthropic

DEFAULT_MODEL = "claude-sonnet-4-6"

GATEWAY_URL_VARIABLE = "INFERENCE_GATEWAY_URL"
GATEWAY_KEY_SECRET = "INFERENCE_GATEWAY_KEY"

ATTRIBUTION_PREFIX = "x-canvas-"


class LLMGatewayConfigurationError(RuntimeError):
    """The gateway URL or the plugin's gateway key is not set."""


@dataclass(frozen=True)
class LLMGateway:
    """LLM access handed to :meth:`AgentPlugin.run`.

    ``model`` is a default for agents that do not choose their own; the gateway
    refuses a model the organization has not enabled.
    """

    base_url: str
    api_key: str = field(repr=False)
    model: str = DEFAULT_MODEL
    attribution: Mapping[str, str] = field(default_factory=dict)

    def client(self, *, max_retries: int = 2) -> Anthropic:
        """An Anthropic client pointed at the gateway, carrying the attribution headers."""
        return Anthropic(
            api_key=self.api_key,
            base_url=self.base_url,
            max_retries=max_retries,
            default_headers={
                f"{ATTRIBUTION_PREFIX}{name}": value
                for name, value in self.attribution.items()
                if value
            },
        )


def gateway_from_plugin_secrets(
    secrets: Mapping[str, object],
    *,
    plugin: str,
    agent: str,
    run_id: str = "",
    instance: str = "",
    model: str = DEFAULT_MODEL,
    environ: Mapping[str, str] | None = None,
) -> LLMGateway:
    """Build a gateway from the instance's gateway URL and the plugin's key secret.

    Called by the runner, which stamps the attribution with the plugin, agent and
    run it is executing.
    """
    environ = os.environ if environ is None else environ
    base_url = environ.get(GATEWAY_URL_VARIABLE, "").strip()
    key = str(secrets.get(GATEWAY_KEY_SECRET) or "").strip()
    missing = []
    if not base_url:
        missing.append(f"instance config {GATEWAY_URL_VARIABLE}")
    if not key:
        missing.append(f"plugin secret {GATEWAY_KEY_SECRET}")
    if missing:
        raise LLMGatewayConfigurationError(
            f"Agent LLM access is not configured: {' and '.join(missing)} unset."
        )
    return LLMGateway(
        base_url=base_url,
        api_key=key,
        model=model,
        attribution={"instance": instance, "plugin": plugin, "agent": agent, "run-id": run_id},
    )


__exports__ = ("LLMGateway", "LLMGatewayConfigurationError")
