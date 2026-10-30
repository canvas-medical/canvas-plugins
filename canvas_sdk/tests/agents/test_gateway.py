import time
from typing import Any

import httpx2
import pytest

from canvas_sdk.agents import LLMGateway, LLMGatewayConfigurationError
from canvas_sdk.agents.gateway import attempt_timeout, gateway_from_plugin_secrets
from canvas_sdk.agents.run_record import DEADLINE_MARGIN_SECONDS, RunRecorder, current_recorder

GATEWAY_URL = "https://gateway.test"
KEY = "cnvs_sk_plugin_key"

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


def gateway() -> LLMGateway:
    """A gateway attributed the way the runner attributes one."""
    return LLMGateway(
        base_url=GATEWAY_URL,
        api_key=KEY,
        attribution={
            "instance": "acme-prod",
            "plugin": "agent_runner_poc",
            "agent": "agent_runner_poc.agents.chart_chat:ChartChatAgent",
            "run-id": "run-1",
        },
    )


def test_a_call_goes_to_the_gateway_with_the_plugins_key_and_attribution() -> None:
    """On the wire: the gateway URL, the key as x-api-key, and the attribution headers."""
    sent: list[httpx2.Request] = []

    def handler(request: httpx2.Request) -> httpx2.Response:
        sent.append(request)
        return httpx2.Response(200, json=MESSAGE)

    client = (
        gateway()
        .client()
        .with_options(http_client=httpx2.Client(transport=httpx2.MockTransport(handler)))
    )
    client.messages.create(
        model="claude-sonnet-4-6", max_tokens=16, messages=[{"role": "user", "content": "hi"}]
    )

    assert str(sent[0].url) == f"{GATEWAY_URL}/v1/messages"
    assert sent[0].headers["x-api-key"] == KEY
    assert sent[0].headers["x-canvas-instance"] == "acme-prod"
    assert sent[0].headers["x-canvas-plugin"] == "agent_runner_poc"
    assert sent[0].headers["x-canvas-agent"] == "agent_runner_poc.agents.chart_chat:ChartChatAgent"
    assert sent[0].headers["x-canvas-run-id"] == "run-1"


def test_blank_attribution_values_are_not_sent() -> None:
    """An empty attribution value sends no header at all."""
    client = LLMGateway(
        base_url=GATEWAY_URL, api_key=KEY, attribution={"plugin": "p", "run-id": ""}
    ).client()

    assert client.default_headers.get("x-canvas-plugin") == "p"
    assert "x-canvas-run-id" not in client.default_headers


def test_repr_leaves_out_the_key() -> None:
    """Logging a gateway does not write the key into the log."""
    assert KEY not in repr(gateway())


def test_gateway_from_plugin_secrets_reads_the_url_and_the_plugins_key() -> None:
    """The URL is instance config; the key is the plugin's own secret."""
    gw = gateway_from_plugin_secrets(
        {"INFERENCE_GATEWAY_KEY": f"  {KEY}  "},
        plugin="p",
        agent="p.agents.a:A",
        run_id="run-1",
        environ={"INFERENCE_GATEWAY_URL": GATEWAY_URL},
    )

    assert gw.base_url == GATEWAY_URL
    assert gw.api_key == KEY
    assert gw.model == "claude-sonnet-4-6"
    assert gw.attribution["plugin"] == "p"
    assert gw.attribution["run-id"] == "run-1"


@pytest.mark.parametrize(
    "secrets, environ, missing",
    [
        ({}, {}, "instance config INFERENCE_GATEWAY_URL and plugin secret INFERENCE_GATEWAY_KEY"),
        ({"INFERENCE_GATEWAY_KEY": KEY}, {"INFERENCE_GATEWAY_URL": " "}, "INFERENCE_GATEWAY_URL"),
        (
            {"INFERENCE_GATEWAY_KEY": ""},
            {"INFERENCE_GATEWAY_URL": GATEWAY_URL},
            "INFERENCE_GATEWAY_KEY",
        ),
    ],
    ids=["neither", "no-url", "empty-key"],
)
def test_gateway_from_plugin_secrets_names_what_is_missing(
    secrets: dict[str, str], environ: dict[str, str], missing: str
) -> None:
    """A missing URL or key is named, with where it is set."""
    with pytest.raises(LLMGatewayConfigurationError, match=missing):
        gateway_from_plugin_secrets(secrets, plugin="p", agent="p.agents.a:A", environ=environ)


def test_in_a_run_the_client_timeout_splits_the_time_left_across_attempts() -> None:
    """A call and its retries together end before the run's deadline."""
    recorder = RunRecorder(deadline=time.monotonic() + DEADLINE_MARGIN_SECONDS + 60)
    token = current_recorder.set(recorder)
    try:
        client = gateway().client(max_retries=2)
    finally:
        current_recorder.reset(token)

    assert 19 < client.timeout <= 20  # type: ignore[operator]
    assert client.max_retries == 2


def test_attempt_timeout_never_drops_below_a_second() -> None:
    """A run at its margin still gets a usable timeout; the tool loop stops it first."""
    assert attempt_timeout(0.5) == 1.0
    assert attempt_timeout(90, max_retries=2) == 30.0
