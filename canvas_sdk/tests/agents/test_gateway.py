import json
from typing import Any

import anthropic
import httpx2
import pytest

from canvas_sdk.agents import LLMGateway, LLMGatewayConfigurationError
from canvas_sdk.agents.gateway import PLACEHOLDER_KEY, gateway_from_environment

GATEWAY_URL = "https://gateway.test"
KEY = "cnvs_sk_real_key"

ERROR: dict[str, Any] = {"type": "error", "error": {"type": "x", "message": "no"}}

MESSAGE: dict[str, Any] = {
    "id": "msg_1",
    "type": "message",
    "role": "assistant",
    "model": "claude-sonnet-4-6",
    "content": [{"type": "text", "text": "hi"}],
    "stop_reason": "end_turn",
    "stop_sequence": None,
    "usage": {"input_tokens": 1, "output_tokens": 1},
}


def recording(sent: list[httpx2.Request], status: int = 200) -> httpx2.MockTransport:
    """A mock gateway that records each request it receives."""

    def handler(request: httpx2.Request) -> httpx2.Response:
        sent.append(request)
        body: dict[str, Any] = MESSAGE if status == 200 else ERROR
        return httpx2.Response(status, json=body)

    return httpx2.MockTransport(handler)


def gateway(sent: list[httpx2.Request], status: int = 200) -> LLMGateway:
    """A gateway with attribution, backed by the recording mock."""
    return LLMGateway(
        base_url=GATEWAY_URL,
        key=KEY,
        attribution={
            "instance": "acme-prod",
            "plugin": "agent_runner_poc",
            "agent": "agent_runner_poc.agents.chart_chat:ChartChatAgent",
            "run-id": "run-1",
        },
        transport=recording(sent, status),
    )


def create(
    client: anthropic.Anthropic, extra_headers: dict[str, str] | None = None
) -> anthropic.types.Message:
    """One minimal messages.create call."""
    return client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=16,
        messages=[{"role": "user", "content": "hi"}],
        extra_headers=extra_headers,
    )


def test_the_real_key_goes_to_the_gateway_in_place_of_the_placeholder() -> None:
    """The wire request carries the real key; no bearer token rides along."""
    sent: list[httpx2.Request] = []
    create(gateway(sent).client())

    assert len(sent) == 1
    assert str(sent[0].url) == f"{GATEWAY_URL}/v1/messages"
    assert sent[0].headers["x-api-key"] == KEY
    assert "authorization" not in sent[0].headers


def test_attribution_headers_are_set_by_the_gateway_not_the_plugin() -> None:
    """Plugin-supplied x-canvas-* headers are replaced or dropped."""
    sent: list[httpx2.Request] = []
    create(
        gateway(sent).client(),
        extra_headers={"x-canvas-plugin": "someone_else", "x-canvas-spoof": "1"},
    )

    headers = sent[0].headers
    assert headers["x-canvas-instance"] == "acme-prod"
    assert headers["x-canvas-plugin"] == "agent_runner_poc"
    assert headers["x-canvas-agent"] == "agent_runner_poc.agents.chart_chat:ChartChatAgent"
    assert headers["x-canvas-run-id"] == "run-1"
    assert "x-canvas-spoof" not in headers


def test_blank_attribution_values_are_not_sent() -> None:
    """An empty attribution value sends no header at all."""
    sent: list[httpx2.Request] = []
    client = LLMGateway(
        base_url=GATEWAY_URL,
        key=KEY,
        attribution={"plugin": "p", "run-id": ""},
        transport=recording(sent),
    ).client()
    create(client)

    assert "x-canvas-run-id" not in sent[0].headers


def test_the_client_api_key_is_the_placeholder() -> None:
    """The client plugins hold knows only the placeholder."""
    client = gateway([]).client()

    assert client.api_key == PLACEHOLDER_KEY
    assert KEY not in json.dumps(dict(client.auth_headers))


def test_responses_carry_the_request_the_plugin_built_not_the_keyed_copy() -> None:
    """A raw response exposes the placeholder request, never the keyed copy."""
    sent: list[httpx2.Request] = []
    raw = (
        gateway(sent)
        .client()
        .messages.with_raw_response.create(
            model="claude-sonnet-4-6",
            max_tokens=16,
            messages=[{"role": "user", "content": "hi"}],
        )
    )

    assert raw.http_request.headers["x-api-key"] == PLACEHOLDER_KEY
    assert raw.http_response.request.headers["x-api-key"] == PLACEHOLDER_KEY


def test_an_error_response_carries_the_placeholder_too() -> None:
    """A status error exposes the placeholder request, never the keyed copy."""
    with pytest.raises(anthropic.APIStatusError) as caught:
        create(gateway([], status=402).client())

    assert caught.value.status_code == 402
    assert caught.value.response.request.headers["x-api-key"] == PLACEHOLDER_KEY


def test_a_request_to_another_host_is_refused_before_it_leaves() -> None:
    """An absolute URL off the gateway host never reaches the network."""
    sent: list[httpx2.Request] = []
    client = gateway(sent).client()

    with pytest.raises(anthropic.APIConnectionError):
        client.get("https://exfiltrate.example/collect", cast_to=object)

    assert sent == []


def test_reassigning_base_url_cannot_redirect_the_key() -> None:
    """A plugin rewriting base_url still cannot send the key elsewhere."""
    sent: list[httpx2.Request] = []
    client = gateway(sent).client()
    client.base_url = "https://exfiltrate.example"

    with pytest.raises(anthropic.APIConnectionError):
        create(client)

    assert sent == []


def test_a_different_port_on_the_gateway_host_is_refused() -> None:
    """The origin check includes the port."""
    sent: list[httpx2.Request] = []
    client = gateway(sent).client()

    with pytest.raises(anthropic.APIConnectionError):
        client.get("https://gateway.test:8443/v1/messages", cast_to=object)

    assert sent == []


def test_repr_names_the_model_and_nothing_else() -> None:
    """Logging or printing a gateway cannot leak the key."""
    assert repr(gateway([])) == "LLMGateway(model='claude-sonnet-4-6')"
    assert KEY not in str(gateway([]))


def test_no_public_attribute_of_the_gateway_or_client_holds_the_key() -> None:
    """No public attribute on the gateway or its client renders the key."""
    gw = gateway([])
    client = gw.client()

    for obj in (gw, client):
        for name in dir(obj):
            if name.startswith("_"):
                continue
            value = getattr(obj, name, None)
            if callable(value):
                continue
            assert KEY not in repr(value), f"{type(obj).__name__}.{name} exposes the key"


@pytest.mark.parametrize("base_url", ["", "gateway.test", "ftp://gateway.test"])
def test_a_base_url_that_is_not_http_is_refused(base_url: str) -> None:
    """A misconfigured gateway URL fails at construction."""
    with pytest.raises(LLMGatewayConfigurationError):
        LLMGateway(base_url=base_url, key=KEY)


def test_an_empty_key_is_refused() -> None:
    """An empty key fails at construction rather than as a 401 later."""
    with pytest.raises(LLMGatewayConfigurationError):
        LLMGateway(base_url=GATEWAY_URL, key="")


def test_gateway_from_environment_reads_both_variables() -> None:
    """The runner builds a working gateway from its environment."""
    gw = gateway_from_environment(
        plugin="p",
        agent="p.agents.a:A",
        environ={"INFERENCE_GATEWAY_URL": GATEWAY_URL, "INFERENCE_GATEWAY_KEY": KEY},
    )

    assert gw.model == "claude-sonnet-4-6"
    assert str(gw.client().base_url).startswith(GATEWAY_URL)


@pytest.mark.parametrize(
    "environ, missing",
    [
        ({}, "INFERENCE_GATEWAY_URL, INFERENCE_GATEWAY_KEY"),
        ({"INFERENCE_GATEWAY_URL": GATEWAY_URL}, "INFERENCE_GATEWAY_KEY"),
        ({"INFERENCE_GATEWAY_KEY": KEY, "INFERENCE_GATEWAY_URL": " "}, "INFERENCE_GATEWAY_URL"),
    ],
)
def test_gateway_from_environment_names_what_is_missing(
    environ: dict[str, str], missing: str
) -> None:
    """A missing variable is named in the error."""
    with pytest.raises(LLMGatewayConfigurationError, match=missing):
        gateway_from_environment(plugin="p", agent="p.agents.a:A", environ=environ)
