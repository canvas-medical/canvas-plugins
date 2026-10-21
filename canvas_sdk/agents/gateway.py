"""LLM access for agents, through Canvas's inference gateway.

The plugin runner builds an :class:`LLMGateway` from ``INFERENCE_GATEWAY_URL`` and
``INFERENCE_GATEWAY_KEY`` in its own environment and hands it to the agent. Plugin
code never holds the key: :meth:`LLMGateway.client` returns an ``anthropic.Anthropic``
client whose ``api_key`` is a placeholder, and an HTTP transport underneath it adds
the real key and Canvas's attribution headers to each request.

The key stays out of plugin reach three ways:

- It lives in private attributes, which the sandbox refuses to read on objects a
  plugin did not define.
- The transport sends a copy of each request. httpx sets ``response.request`` back
  to the request the client built, so responses and errors carry the placeholder.
- The transport refuses any host but the gateway's, and any call but the two the
  gateway proxies, because a plugin can reassign a client's ``base_url`` or pass an
  absolute URL to ``client.get``.
"""

import os
from collections.abc import Mapping

import httpx2
from anthropic import Anthropic

DEFAULT_MODEL = "claude-sonnet-4-6"

GATEWAY_URL_VARIABLE = "INFERENCE_GATEWAY_URL"
GATEWAY_KEY_VARIABLE = "INFERENCE_GATEWAY_KEY"

# What the Anthropic client sends as its own key. The transport swaps the real key
# in on the way out, so this is what any plugin-visible request object carries.
PLACEHOLDER_KEY = "canvas-inference-gateway"

# The only calls the key is sent with: the two endpoints the gateway proxies.
GATEWAY_ROUTES = frozenset({("POST", "/v1/messages"), ("POST", "/v1/messages/count_tokens")})

ATTRIBUTION_PREFIX = "x-canvas-"
_CREDENTIAL_HEADERS = frozenset({"x-api-key", "authorization"})


class LLMGatewayConfigurationError(RuntimeError):
    """The gateway is not configured, or a request tried to leave it."""


def _origin(url: httpx2.URL) -> tuple[str, str, int | None]:
    return (url.scheme, url.host, url.port)


class _GatewayTransport(httpx2.BaseTransport):
    """Adds the gateway key and attribution to requests bound for the gateway."""

    def __init__(
        self,
        gateway_url: httpx2.URL,
        key: str,
        attribution: Mapping[str, str],
        inner: httpx2.BaseTransport | None = None,
    ) -> None:
        self._origin = _origin(gateway_url)
        # A gateway mounted under a path prefix still serves /v1/... beneath it.
        self._prefix = gateway_url.path.rstrip("/")
        self._key = key
        self._attribution = dict(attribution)
        self._inner = inner or httpx2.HTTPTransport()

    def handle_request(self, request: httpx2.Request) -> httpx2.Response:
        if _origin(request.url) != self._origin:
            raise LLMGatewayConfigurationError(
                f"Refusing to send gateway credentials to {request.url.host!r}; "
                "agent clients only reach the Canvas inference gateway."
            )
        route = (request.method, request.url.path.removeprefix(self._prefix))
        if route not in GATEWAY_ROUTES:
            raise LLMGatewayConfigurationError(
                f"Refusing {request.method} {request.url.path}; the gateway serves "
                "only the Messages API and token counting."
            )
        headers = [
            (name, value)
            for name, value in request.headers.multi_items()
            if name.lower() not in _CREDENTIAL_HEADERS
            and not name.lower().startswith(ATTRIBUTION_PREFIX)
        ]
        headers.append(("x-api-key", self._key))
        headers.extend(self._attribution.items())
        upstream = httpx2.Request(
            request.method,
            request.url,
            headers=headers,
            stream=request.stream,
            extensions=request.extensions,
        )
        return self._inner.handle_request(upstream)

    def close(self) -> None:
        self._inner.close()


class LLMGateway:
    """LLM access handed to :meth:`AgentPlugin.run`.

    ``model`` is a default for agents that do not choose their own; the gateway
    refuses a model the organization has not enabled. ``client()`` is the only way
    to make calls, and every call it makes is metered and attributed by the gateway.
    """

    __slots__ = ("_attribution", "_base_url", "_inner", "_key", "model")

    def __init__(
        self,
        *,
        base_url: str,
        key: str,
        model: str = DEFAULT_MODEL,
        attribution: Mapping[str, str] | None = None,
        transport: httpx2.BaseTransport | None = None,
    ) -> None:
        url = httpx2.URL(base_url)
        if url.scheme not in ("http", "https") or not url.host:
            raise LLMGatewayConfigurationError(
                f"{GATEWAY_URL_VARIABLE} must be an http(s) URL, not {base_url!r}."
            )
        if not key:
            raise LLMGatewayConfigurationError(f"{GATEWAY_KEY_VARIABLE} is empty.")
        self._base_url = url
        self._key = key
        self._attribution = {
            f"{ATTRIBUTION_PREFIX}{name}": value
            for name, value in (attribution or {}).items()
            if value
        }
        self._inner = transport
        self.model = model

    def client(self, *, max_retries: int = 2) -> Anthropic:
        """An Anthropic client that reaches only the gateway, with the key added underneath it."""
        transport = _GatewayTransport(self._base_url, self._key, self._attribution, self._inner)
        return Anthropic(
            api_key=PLACEHOLDER_KEY,
            base_url=str(self._base_url),
            max_retries=max_retries,
            http_client=httpx2.Client(transport=transport),
        )

    def __repr__(self) -> str:
        return f"LLMGateway(model={self.model!r})"


def gateway_from_environment(
    *,
    plugin: str,
    agent: str,
    run_id: str = "",
    instance: str = "",
    model: str = DEFAULT_MODEL,
    environ: Mapping[str, str] | None = None,
) -> LLMGateway:
    """Build a gateway from the plugin runner's environment.

    Called by the runner, never by plugin code: it is not exported, so the
    sandbox refuses to import it, and the attribution it stamps names the plugin
    and agent the runner is executing rather than whatever a plugin claims.
    """
    environ = os.environ if environ is None else environ
    base_url = environ.get(GATEWAY_URL_VARIABLE, "").strip()
    key = environ.get(GATEWAY_KEY_VARIABLE, "").strip()
    missing = [
        name
        for name, value in ((GATEWAY_URL_VARIABLE, base_url), (GATEWAY_KEY_VARIABLE, key))
        if not value
    ]
    if missing:
        raise LLMGatewayConfigurationError(
            f"Agent LLM access is not configured: {', '.join(missing)} unset."
        )
    return LLMGateway(
        base_url=base_url,
        key=key,
        model=model,
        attribution={"instance": instance, "plugin": plugin, "agent": agent, "run-id": run_id},
    )


__exports__ = ("LLMGateway", "LLMGatewayConfigurationError")
