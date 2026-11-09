"""LLM access for agents, through Canvas's inference gateway.

The plugin runner builds an :class:`LLMGateway` from the instance's
``INFERENCE_GATEWAY_URL`` and the agent plugin's own ``INFERENCE_GATEWAY_KEY`` secret,
which the plugin declares in its manifest ``variables`` with ``sensitive: true``.
:meth:`LLMGateway.client` returns a :class:`GatewayClient`, which calls the gateway with
that key and the runner's attribution headers.

Plugin code gets the gateway in ``run()`` and cannot build one, read its key or host, or
change where a call goes or what it is attributed to: the key, host, and attribution are
private, the constructor takes a seal only :func:`build_gateway` holds, and the client
offers ``messages.create`` and ``messages.stream`` only. Every call through the client
counts toward the run's model-call ceiling.
"""

import os
from collections.abc import Mapping
from typing import Any

from anthropic import NOT_GIVEN, Anthropic, NotGiven

from canvas_sdk.agents.run_record import RunRecorder, current_recorder

DEFAULT_MODEL = "claude-sonnet-4-6"

# The Anthropic client's own default.
DEFAULT_MAX_RETRIES = 2

GATEWAY_URL_VARIABLE = "INFERENCE_GATEWAY_URL"
GATEWAY_KEY_SECRET = "INFERENCE_GATEWAY_KEY"

ATTRIBUTION_PREFIX = "x-canvas-"

# Request options that would change where a call goes or what it is attributed to.
_REFUSED_OPTIONS = frozenset({"extra_headers", "extra_query"})

# Held by build_gateway only; plugin code cannot name a module's underscored values.
_SEAL = object()


class LLMGatewayConfigurationError(RuntimeError):
    """The gateway URL or the plugin's gateway key is not set."""


class ModelCallLimitReached(RuntimeError):
    """The run has made as many model calls as its ceiling allows."""


class GatewayMessages:
    """``messages.create`` and ``messages.stream``, each counted against the run's ceiling.

    The run is the one the client was built in, whatever thread later makes the call.
    """

    def __init__(self, client: Anthropic, recorder: RunRecorder | None = None) -> None:
        self._client = client
        self._recorder = recorder

    def create(self, **request: Any) -> Any:
        """Make one model call through the gateway; see ``anthropic`` ``messages.create``."""
        count_model_call(request, self._recorder)
        return self._client.messages.create(**request)

    def stream(self, **request: Any) -> Any:
        """Stream one model call through the gateway; see ``anthropic`` ``messages.stream``."""
        count_model_call(request, self._recorder)
        return self._client.messages.stream(**request)


class GatewayClient:
    """A client for the inference gateway, offering only model calls.

    Its host, key, and attribution headers are fixed by the gateway that built it.
    """

    def __init__(self, client: Anthropic, recorder: RunRecorder | None = None) -> None:
        self._client = client
        self.messages = GatewayMessages(client, recorder)


def count_model_call(request: Mapping[str, Any], recorder: RunRecorder | None = None) -> None:
    """Count a model call against the run's ceiling, refusing options the gateway owns.

    ``recorder`` is the run the client was built in, or the current one. Raises
    :class:`ModelCallLimitReached` at the ceiling and once that run has ended. Not exported
    to plugin code.
    """
    if refused := sorted(_REFUSED_OPTIONS & request.keys()):
        raise ValueError(f"The gateway sets its own {', '.join(refused)}; leave them out.")
    recorder = recorder or current_recorder.get()
    if recorder is not None and recorder.closed:
        raise ModelCallLimitReached("The run has ended; it makes no more model calls.")
    if recorder is not None and not recorder.reserve_model_call():
        raise ModelCallLimitReached(f"The run has made its {recorder.max_model_calls} model calls.")


class LLMGateway:
    """LLM access handed to :meth:`AgentPlugin.run`.

    ``model`` is a default for agents that do not choose their own; the gateway
    refuses a model the organization has not enabled. Only the platform builds one.
    """

    def __init__(
        self,
        *,
        seal: object,
        base_url: str,
        api_key: str,
        model: str = DEFAULT_MODEL,
        attribution: Mapping[str, str] | None = None,
    ) -> None:
        if seal is not _SEAL:
            raise TypeError("Only the platform builds a gateway; an agent receives one in run().")
        self._base_url = base_url
        self._api_key = api_key
        self._attribution = dict(attribution or {})
        self._model = model

    @property
    def model(self) -> str:
        """The default model for calls that name none."""
        return self._model

    def __repr__(self) -> str:
        return f"LLMGateway(model={self._model!r})"

    def with_model(self, model: str) -> "LLMGateway":
        """This gateway with ``model`` as its default: same URL, key, and attribution."""
        if model == self._model:
            return self
        return LLMGateway(
            seal=_SEAL,
            base_url=self._base_url,
            api_key=self._api_key,
            model=model,
            attribution=self._attribution,
        )

    def client(self, *, max_retries: int = DEFAULT_MAX_RETRIES) -> GatewayClient:
        """A client for the gateway, carrying the attribution headers.

        In a platform run, each attempt's timeout is the time left before the run's
        deadline split across the attempts, so retries cannot carry a call past it.
        """
        left = _seconds_left()
        timeout: float | NotGiven = (
            NOT_GIVEN if left is None else attempt_timeout(left, max_retries)
        )
        return GatewayClient(
            Anthropic(
                api_key=self._api_key,
                base_url=self._base_url,
                max_retries=max_retries,
                timeout=timeout,
                default_headers={
                    f"{ATTRIBUTION_PREFIX}{name}": value
                    for name, value in self._attribution.items()
                    if value
                },
            ),
            current_recorder.get(),
        )


def build_gateway(
    *,
    base_url: str,
    api_key: str,
    model: str = DEFAULT_MODEL,
    attribution: Mapping[str, str] | None = None,
) -> LLMGateway:
    """Build a gateway; the runner's and tests' way in, not exported to plugin code."""
    return LLMGateway(
        seal=_SEAL, base_url=base_url, api_key=api_key, model=model, attribution=attribution
    )


def attempt_timeout(seconds_left: float, max_retries: int = DEFAULT_MAX_RETRIES) -> float:
    """One attempt's timeout when ``seconds_left`` must cover the first try and every retry."""
    return max(1.0, seconds_left / (max_retries + 1))


def _seconds_left() -> float | None:
    recorder = current_recorder.get()
    return recorder.seconds_left() if recorder is not None else None


# Secrets the plugin runner keeps from an agent: its gateway key, which the runner turns
# into the agent's gateway, and the GraphQL token handlers get.
AGENT_WITHHELD_SECRETS = frozenset({GATEWAY_KEY_SECRET, "graphql_jwt"})


def agent_secrets(secrets: Mapping[str, object]) -> dict[str, str]:
    """The plugin's variables as an agent sees them, a copy with the withheld ones left out."""
    return {
        name: str(value)
        for name, value in secrets.items()
        if name not in AGENT_WITHHELD_SECRETS and value is not None
    }


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
    return build_gateway(
        base_url=base_url,
        api_key=key,
        model=model,
        attribution={"instance": instance, "plugin": plugin, "agent": agent, "run-id": run_id},
    )


__exports__ = (
    "GatewayClient",
    "LLMGateway",
    "LLMGatewayConfigurationError",
    "ModelCallLimitReached",
)
