"""The fake gateway answers the way the Anthropic SDK, and so run_tool_loop, expects."""

import socket
import threading
import time
from collections.abc import Iterator
from typing import Any

import anthropic
import pytest
import uvicorn
from adk_loadtest import gateway
from anthropic.types import MessageParam, ToolUseBlock
from fastapi.testclient import TestClient

SCRIPT = 'LOADTEST_SCRIPT={"tools": [["find_note_types", {}]], "latency_ms": 0, "text": "all done"}'


@pytest.fixture(autouse=True)
def reset() -> Iterator[None]:
    """Restore the gateway's defaults around each test."""
    TestClient(gateway.app).post("/reset")
    yield


@pytest.fixture(scope="module")
def server() -> Iterator[str]:
    """The gateway on a real port, as an agent's Anthropic client reaches it."""
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    config = uvicorn.Config(gateway.app, host="127.0.0.1", port=port, log_level="warning")
    running = uvicorn.Server(config)
    thread = threading.Thread(target=running.run, daemon=True)
    thread.start()
    while not running.started:
        time.sleep(0.01)
    yield f"http://127.0.0.1:{port}"
    running.should_exit = True
    thread.join()


def _client(server: str) -> anthropic.Anthropic:
    return anthropic.Anthropic(base_url=server, api_key="loadtest", max_retries=0)


def _ask(client: anthropic.Anthropic, messages: list[MessageParam]) -> Any:
    return client.messages.create(
        model="claude-loadtest", max_tokens=100, system=SCRIPT, messages=messages
    )


def test_the_script_calls_its_tools_then_ends(server: str) -> None:
    """Each assistant turn already sent advances the script by one step."""
    client = _client(server)
    first = _ask(client, [{"role": "user", "content": "go"}])
    tool = first.content[0]
    second = _ask(
        client,
        [
            {"role": "user", "content": "go"},
            {"role": "assistant", "content": [tool.model_dump()]},
            {
                "role": "user",
                "content": [{"type": "tool_result", "tool_use_id": tool.id, "content": "[]"}],
            },
        ],
    )

    assert (first.stop_reason, tool.type, tool.name) == ("tool_use", "tool_use", "find_note_types")
    assert (second.stop_reason, second.content[0].text) == ("end_turn", "all done")


def test_a_streamed_answer_matches_the_unstreamed_one(server: str) -> None:
    """run_tool_loop streams when an agent shows its reply; the final message is the same."""
    with _client(server).messages.stream(
        model="claude-loadtest",
        max_tokens=100,
        system=[{"type": "text", "text": SCRIPT}],
        messages=[{"role": "user", "content": "go"}],
    ) as stream:
        final = stream.get_final_message()

    tool = final.content[0]
    assert final.stop_reason == "tool_use"
    assert isinstance(tool, ToolUseBlock)
    assert (tool.name, tool.input) == ("find_note_types", {})


def test_injected_faults_reach_the_client_as_api_errors(server: str) -> None:
    """A 429 is an outage the platform retries; a 401 a refusal it does not."""
    control = TestClient(gateway.app)
    control.post("/control", json={"rate_429": 1.0})
    with pytest.raises(anthropic.RateLimitError):
        _ask(_client(server), [{"role": "user", "content": "go"}])

    control.post("/control", json={"rate_429": 0.0, "rate_401": 1.0})
    with pytest.raises(anthropic.AuthenticationError):
        _ask(_client(server), [{"role": "user", "content": "go"}])

    assert control.get("/stats").json()["faults"] == {"429": 1, "401": 1}


def test_latency_holds_each_answer_and_is_counted_in_flight() -> None:
    """The configured latency is the model time a run spends per call."""
    control = TestClient(gateway.app)
    control.post("/control", json={"latency_ms": 200, "jitter": 0})
    started = time.monotonic()
    control.post(
        "/v1/messages",
        json={"system": "no script", "messages": [{"role": "user", "content": "go"}]},
    )

    assert time.monotonic() - started >= 0.2
    stats = control.get("/stats").json()
    assert (stats["requests"], stats["max_in_flight"], stats["in_flight"]) == (1, 1, 0)


def test_an_unknown_setting_is_refused() -> None:
    """A misspelled control setting is an error, not a silent no-op."""
    assert TestClient(gateway.app).post("/control", json={"latency": 5}).status_code == 400
