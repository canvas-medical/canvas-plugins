"""Plugin code reaching the gateway's key or host through what a model call hands back."""

import json
import threading
from collections.abc import Iterator
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

import pytest

from canvas_sdk.agents.gateway import build_gateway
from plugin_runner.tests.test_sandbox import _sandbox_from_code

KEY = "cnvs_sk_plugin_secret"

# Attributes the anthropic error and stream objects carry the request on.
REQUEST_ATTRIBUTES = ("request", "response", "body", "http_request", "headers")

PROBE = f"""
def reachable(value):
    found = []
    for name in {REQUEST_ATTRIBUTES!r}:
        try:
            attribute = getattr(value, name)
        except AttributeError:
            continue
        if attribute is not None:
            found.append((name, repr(attribute)))
    return found


def create(gateway):
    try:
        gateway.client(max_retries=0).messages.create(
            model="m", max_tokens=5, messages=[{{"role": "user", "content": "hi"}}]
        )
    except Exception as error:
        return {{"error": repr(error), "message": str(error), "reachable": reachable(error)}}
    return {{}}


def stream(gateway):
    with gateway.client(max_retries=0).messages.stream(
        model="m", max_tokens=5, messages=[{{"role": "user", "content": "hi"}}]
    ) as reply:
        text = "".join(reply.text_stream)
        return {{
            "text": text,
            "final": repr(reply.get_final_message()),
            "reachable": reachable(reply),
        }}
"""

SSE = [
    (
        "message_start",
        {
            "type": "message_start",
            "message": {
                "id": "msg_1",
                "type": "message",
                "role": "assistant",
                "model": "m",
                "content": [],
                "stop_reason": None,
                "stop_sequence": None,
                "usage": {"input_tokens": 1, "output_tokens": 0},
            },
        },
    ),
    (
        "content_block_start",
        {"type": "content_block_start", "index": 0, "content_block": {"type": "text", "text": ""}},
    ),
    (
        "content_block_delta",
        {"type": "content_block_delta", "index": 0, "delta": {"type": "text_delta", "text": "ok"}},
    ),
    ("content_block_stop", {"type": "content_block_stop", "index": 0}),
    (
        "message_delta",
        {
            "type": "message_delta",
            "delta": {"stop_reason": "end_turn", "stop_sequence": None},
            "usage": {"output_tokens": 1},
        },
    ),
    ("message_stop", {"type": "message_stop"}),
]


@pytest.fixture
def gateway_server() -> Iterator[str]:
    """A gateway stand-in: 401 for a plain call, a one-word reply for a streamed one."""

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self) -> None:
            body = json.loads(self.rfile.read(int(self.headers["content-length"])))
            if body.get("stream"):
                self.send_response(200)
                self.send_header("content-type", "text/event-stream")
                self.end_headers()
                for event, data in SSE:
                    self.wfile.write(f"event: {event}\ndata: {json.dumps(data)}\n\n".encode())
                return
            payload = json.dumps(
                {"type": "error", "error": {"type": "authentication_error", "message": "no"}}
            ).encode()
            self.send_response(401)
            self.send_header("content-type", "application/json")
            self.send_header("content-length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        def log_message(self, *args: Any) -> None:
            return None

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_address[1]}"
    finally:
        server.shutdown()


def _probe(name: str, base_url: str) -> dict[str, Any]:
    scope = _sandbox_from_code(PROBE).execute()
    result: dict[str, Any] = scope[name](build_gateway(base_url=base_url, api_key=KEY))
    return result


def _leaks(result: dict[str, Any], base_url: str) -> list[str]:
    text = json.dumps(result)
    return [secret for secret in (KEY, base_url, "127.0.0.1") if secret in text]


def test_a_failed_call_hands_plugin_code_no_key_or_host(gateway_server: str) -> None:
    """A refused call raises GatewayError, whose message is the gateway's and nothing more."""
    result = _probe("create", gateway_server)

    assert "GatewayError" in result["error"]
    assert result["message"] == "no"
    assert result["reachable"] == []
    assert _leaks(result, gateway_server) == []


def test_an_unreachable_gateway_hands_plugin_code_no_key_or_host() -> None:
    """A connection error carries the request on the anthropic error; the SDK error does not."""
    # Nothing listens on port 9 (discard), so the connection is refused.
    base_url = "http://127.0.0.1:9"

    result = _probe("create", base_url)

    assert "GatewayError" in result["error"]
    assert result["reachable"] == []
    assert _leaks(result, base_url) == []


def test_a_stream_hands_plugin_code_its_reply_but_no_key_or_host(gateway_server: str) -> None:
    """A stream exposes its text and final message, never the response it was read from."""
    result = _probe("stream", gateway_server)

    assert result["text"] == "ok"
    assert "ok" in result["final"]
    assert result["reachable"] == []
    assert _leaks(result, gateway_server) == []


def test_create_refuses_stream_true(gateway_server: str) -> None:
    """create(stream=True) would return the client's raw stream, which holds the response."""
    scope = _sandbox_from_code(
        """
def create_streamed(gateway):
    try:
        gateway.client(max_retries=0).messages.create(
            model="m", max_tokens=5, stream=True, messages=[{"role": "user", "content": "hi"}]
        )
    except ValueError as error:
        return str(error)
"""
    ).execute()

    refused = scope["create_streamed"](build_gateway(base_url=gateway_server, api_key=KEY))

    assert "messages.stream" in refused
