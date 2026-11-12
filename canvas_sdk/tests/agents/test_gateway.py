import threading
import time
from typing import Any

import httpx2
import pytest

from canvas_sdk.agents import LLMGateway, LLMGatewayConfigurationError
from canvas_sdk.agents.gateway import (
    GatewayError,
    GatewayMessages,
    ModelCallLimitReached,
    _converted,
    agent_secrets,
    attempt_timeout,
    build_gateway,
    gateway_from_plugin_secrets,
)
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
    return build_gateway(
        base_url=GATEWAY_URL,
        api_key=KEY,
        attribution={
            "instance": "acme-prod",
            "plugin": "canvas__chart_chat",
            "agent": "canvas__chart_chat.agents.chart_chat:ChartChatAgent",
            "run-id": "run-1",
        },
    )


def test_a_call_goes_to_the_gateway_with_the_plugins_key_and_attribution() -> None:
    """On the wire: the gateway URL, the key as x-api-key, and the attribution headers."""
    sent: list[httpx2.Request] = []

    def handler(request: httpx2.Request) -> httpx2.Response:
        sent.append(request)
        return httpx2.Response(200, json=MESSAGE)

    client = gateway().client()
    # A test reaches the wrapped Anthropic client; plugin code cannot.
    client._client = client._client.with_options(
        http_client=httpx2.Client(transport=httpx2.MockTransport(handler))
    )
    client.messages = GatewayMessages(client._client)
    client.messages.create(
        model="claude-sonnet-4-6", max_tokens=16, messages=[{"role": "user", "content": "hi"}]
    )

    assert str(sent[0].url) == f"{GATEWAY_URL}/v1/messages"
    assert sent[0].headers["x-api-key"] == KEY
    assert sent[0].headers["x-canvas-instance"] == "acme-prod"
    assert sent[0].headers["x-canvas-plugin"] == "canvas__chart_chat"
    assert (
        sent[0].headers["x-canvas-agent"] == "canvas__chart_chat.agents.chart_chat:ChartChatAgent"
    )
    assert sent[0].headers["x-canvas-run-id"] == "run-1"


def test_blank_attribution_values_are_not_sent() -> None:
    """An empty attribution value sends no header at all."""
    client = build_gateway(
        base_url=GATEWAY_URL, api_key=KEY, attribution={"plugin": "p", "run-id": ""}
    ).client()

    assert client._client.default_headers.get("x-canvas-plugin") == "p"
    assert "x-canvas-run-id" not in client._client.default_headers


def test_repr_leaves_out_the_key() -> None:
    """Logging a gateway does not write the key into the log."""
    assert KEY not in repr(gateway())


def test_gateway_from_plugin_secrets_reads_the_url_and_the_key_from_the_plugins_secrets() -> None:
    """Platform sends both with every deploy, so a key always meets its own gateway."""
    gw = gateway_from_plugin_secrets(
        {"INFERENCE_GATEWAY_KEY": f"  {KEY}  ", "INFERENCE_GATEWAY_URL": GATEWAY_URL},
        plugin="p",
        agent="p.agents.a:A",
        run_id="run-1",
    )

    assert gw._base_url == GATEWAY_URL
    assert gw._api_key == KEY
    assert gw.model == "claude-sonnet-4-6"
    assert gw._attribution["plugin"] == "p"
    assert gw._attribution["run-id"] == "run-1"


@pytest.mark.parametrize(
    "secrets, missing",
    [
        ({}, "plugin secrets INFERENCE_GATEWAY_URL and INFERENCE_GATEWAY_KEY"),
        ({"INFERENCE_GATEWAY_KEY": KEY, "INFERENCE_GATEWAY_URL": " "}, "INFERENCE_GATEWAY_URL"),
        (
            {"INFERENCE_GATEWAY_KEY": "", "INFERENCE_GATEWAY_URL": GATEWAY_URL},
            "INFERENCE_GATEWAY_KEY",
        ),
    ],
    ids=["neither", "no-url", "empty-key"],
)
def test_gateway_from_plugin_secrets_names_what_is_missing(
    secrets: dict[str, str], missing: str
) -> None:
    """A missing URL or key is named."""
    with pytest.raises(LLMGatewayConfigurationError, match=missing):
        gateway_from_plugin_secrets(secrets, plugin="p", agent="p.agents.a:A")


def test_the_instance_environment_is_not_a_gateway_url(monkeypatch: pytest.MonkeyPatch) -> None:
    """Only the plugin's own secrets say where its key works."""
    monkeypatch.setenv("INFERENCE_GATEWAY_URL", GATEWAY_URL)

    with pytest.raises(LLMGatewayConfigurationError, match="INFERENCE_GATEWAY_URL"):
        gateway_from_plugin_secrets(
            {"INFERENCE_GATEWAY_KEY": KEY}, plugin="p", agent="p.agents.a:A"
        )


def test_in_a_run_the_client_timeout_splits_the_time_left_across_attempts() -> None:
    """A call and its retries together end before the run's deadline."""
    recorder = RunRecorder(deadline=time.monotonic() + DEADLINE_MARGIN_SECONDS + 60)
    token = current_recorder.set(recorder)
    try:
        client = gateway().client(max_retries=2)
    finally:
        current_recorder.reset(token)

    assert 19 < client._client.timeout <= 20  # type: ignore[operator]
    assert client._client.max_retries == 2


def test_attempt_timeout_never_drops_below_a_second() -> None:
    """A run at its margin still gets a usable timeout; the tool loop stops it first."""
    assert attempt_timeout(0.5) == 1.0
    assert attempt_timeout(90, max_retries=2) == 30.0


def test_with_model_keeps_the_url_key_and_attribution() -> None:
    """A tier switch changes the default model and nothing a call is billed or routed by."""
    gateway = build_gateway(
        base_url="https://gateway.test", api_key="k", attribution={"plugin": "p", "run-id": "r"}
    )

    cheap = gateway.with_model("claude-haiku-4-5")

    assert (cheap._base_url, cheap._api_key, cheap._attribution, cheap.model) == (
        "https://gateway.test",
        "k",
        {"plugin": "p", "run-id": "r"},
        "claude-haiku-4-5",
    )
    assert gateway.model == "claude-sonnet-4-6"
    assert gateway.with_model(gateway.model) is gateway


def test_agent_secrets_leave_out_the_gateway_key_url_and_the_handler_token() -> None:
    """An agent sees its plugin's variables; the runner keeps the key it builds the gateway from."""
    secrets = {
        "INFERENCE_GATEWAY_KEY": "k",
        "INFERENCE_GATEWAY_URL": GATEWAY_URL,
        "graphql_jwt": "t",
        "MODEL": "claude-haiku-4-5",
    }

    assert agent_secrets(secrets) == {"MODEL": "claude-haiku-4-5"}


def test_the_client_offers_model_calls_only() -> None:
    """No way to change the host, the key, or the attribution from the client."""
    client = gateway().client()

    assert not hasattr(client, "with_options")
    assert not hasattr(client, "default_headers")
    assert not hasattr(client.messages, "with_raw_response")
    for option in ("extra_headers", "extra_query"):
        with pytest.raises(ValueError, match="gateway sets its own"):
            client.messages.create(model="m", max_tokens=1, messages=[], **{option: {}})


def test_plugin_code_cannot_build_a_gateway() -> None:
    """Without the seal only the runner's builder holds, a gateway pointed elsewhere fails."""
    with pytest.raises(TypeError, match="Only the platform builds a gateway"):
        LLMGateway(seal=object(), base_url="https://elsewhere.invalid", api_key=KEY)


def test_every_call_through_the_client_counts_toward_the_runs_ceiling() -> None:
    """A direct call, outside run_tool_loop, is counted and capped like the loop's own."""
    made: list[dict] = []

    class _Inner:
        class messages:  # noqa: N801
            @staticmethod
            def create(**request: Any) -> str:
                made.append(request)
                return "reply"

    recorder = RunRecorder(max_model_calls=1)
    token = current_recorder.set(recorder)
    try:
        messages = GatewayMessages(_Inner())  # type: ignore[arg-type]
        messages.create(model="m", max_tokens=1, messages=[])
        with pytest.raises(ModelCallLimitReached):
            messages.create(model="m", max_tokens=1, messages=[])
    finally:
        current_recorder.reset(token)

    assert (recorder.model_calls, len(made)) == (1, 1)


def test_a_client_counts_against_the_run_it_was_built_in_from_any_thread() -> None:
    """Another thread, without the run's context, cannot make uncounted calls."""
    made: list[dict] = []

    class _Anthropic:
        class messages:  # noqa: N801
            @staticmethod
            def create(**request: Any) -> str:
                made.append(request)
                return "reply"

    recorder = RunRecorder(max_model_calls=1)
    token = current_recorder.set(recorder)
    try:
        client = gateway().client()
    finally:
        current_recorder.reset(token)
    client.messages._client = _Anthropic()  # type: ignore[assignment]
    outcome: list[BaseException | str] = []

    def call() -> None:
        try:
            outcome.append(client.messages.create(model="m", max_tokens=1, messages=[]))
        except ModelCallLimitReached as exc:
            outcome.append(exc)

    for _ in range(2):
        thread = threading.Thread(target=call)
        thread.start()
        thread.join()

    assert outcome[0] == "reply" and isinstance(outcome[1], ModelCallLimitReached)
    assert recorder.model_calls == 1


def test_a_client_kept_past_its_run_is_refused() -> None:
    """Once the run ends, a client its code kept makes no more calls."""
    recorder = RunRecorder()
    token = current_recorder.set(recorder)
    try:
        client = gateway().client()
    finally:
        current_recorder.reset(token)
    recorder.close()

    with pytest.raises(ModelCallLimitReached, match="has ended"):
        client.messages.create(model="m", max_tokens=1, messages=[])


def test_a_gateway_kept_past_its_run_builds_no_client() -> None:
    """A module-level copy of the run's gateway, used after the run ended, makes no calls."""
    recorder = RunRecorder(max_model_calls=1)
    kept = build_gateway(base_url=GATEWAY_URL, api_key=KEY, recorder=recorder)
    recorder.close()

    with pytest.raises(ModelCallLimitReached, match="has ended"):
        kept.client()
    with pytest.raises(ModelCallLimitReached, match="has ended"):
        kept.with_model("claude-haiku-4-5").client()


def test_a_client_counts_against_its_gateways_run_outside_that_run() -> None:
    """With no run current, as after the run's context is gone, the gateway's run still counts."""
    recorder = RunRecorder(max_model_calls=1)
    client = build_gateway(base_url=GATEWAY_URL, api_key=KEY, recorder=recorder).client()
    client.messages._client = type(
        "_Anthropic", (), {"messages": type("m", (), {"create": staticmethod(lambda **r: "reply")})}
    )()

    assert client.messages.create(model="m", max_tokens=1, messages=[]) == "reply"
    with pytest.raises(ModelCallLimitReached):
        client.messages.create(model="m", max_tokens=1, messages=[])
    assert recorder.model_calls == 1


def test_a_transport_error_while_streaming_reaches_the_caller_without_its_request() -> None:
    """The client lets a mid-stream read error through; it carries the request it was on."""
    request = httpx2.Request("POST", f"{GATEWAY_URL}/v1/messages", headers={"x-api-key": KEY})

    def events() -> Any:
        yield "first"
        raise httpx2.ReadError("connection reset", request=request)

    received = []
    with pytest.raises(GatewayError) as raised:
        for event in _converted(events()):
            received.append(event)

    assert received == ["first"]
    assert raised.value.status_code is None
    assert raised.value.error_type == "connection_error"
    assert raised.value.__context__ is None
    assert KEY not in repr(vars(raised.value))


def test_a_streamed_call_counts_against_the_runs_ceiling() -> None:
    """A stream is a model call like any other, so it cannot get past the ceiling."""
    opened: list[dict] = []

    class _Stream:
        def __enter__(self) -> "_Stream":
            return self

        def __exit__(self, *exc: object) -> None:
            return None

    class _Anthropic:
        class messages:  # noqa: N801
            @staticmethod
            def stream(**request: Any) -> _Stream:
                opened.append(request)
                return _Stream()

    recorder = RunRecorder(max_model_calls=1)
    messages = GatewayMessages(_Anthropic(), recorder)  # type: ignore[arg-type]

    messages.stream(model="m", max_tokens=1, messages=[])
    with pytest.raises(ModelCallLimitReached):
        messages.stream(model="m", max_tokens=1, messages=[])

    assert (recorder.model_calls, len(opened)) == (1, 1)
