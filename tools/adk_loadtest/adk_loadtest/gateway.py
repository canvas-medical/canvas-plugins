"""A fake inference gateway for load testing the Agent Development Kit.

It answers ``POST /v1/messages`` the way Canvas's inference gateway does, streaming
included, so an agent's ``run_tool_loop`` runs unchanged against it, but from a script
rather than a model: the run under test is about the platform's scheduling and locking,
not about what a model says.

A request's system prompt carries the script as ``LOADTEST_SCRIPT={...}``::

    {"tools": [["find_note_types", {}], ["find_practice_locations", {}]],
     "latency_ms": 2000, "text": "done"}

Each assistant turn already in the conversation advances the script by one step: turn
``i`` calls ``tools[i]``, and once the tools run out the model ends its turn with
``text``. ``latency_ms`` is how long each answer takes; without one, the gateway's
configured latency applies.

``POST /control`` sets latency and fault injection for every request that follows;
``GET /stats`` reports what the gateway served. Faults are drawn per request: a 429 or
a 500 is an outage the platform retries, a 401 a refusal it does not.
"""

import asyncio
import json
import random
import re
import threading
import time
import uuid
from collections import Counter
from collections.abc import AsyncIterator
from dataclasses import asdict, dataclass, field
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse

SCRIPT_MARKER = re.compile(r"LOADTEST_SCRIPT=(\{.*?\})(?:\s|$)", re.DOTALL)
MODEL = "claude-loadtest"


@dataclass
class Control:
    """How the gateway answers: latency, and how often it fails."""

    latency_ms: int = 1000
    # Spread of the latency as a fraction of it: each answer waits uniformly within
    # latency_ms * (1 ± jitter).
    jitter: float = 0.25
    rate_429: float = 0.0
    rate_500: float = 0.0
    rate_401: float = 0.0


@dataclass
class Stats:
    """What the gateway served since it started or was reset."""

    requests: int = 0
    streamed: int = 0
    faults: Counter[str] = field(default_factory=Counter)
    in_flight: int = 0
    max_in_flight: int = 0


app = FastAPI(title="ADK load test gateway")
_control = Control()
_stats = Stats()
_lock = threading.Lock()


def _system_text(system: Any) -> str:
    if isinstance(system, str):
        return system
    if isinstance(system, list):
        return "\n".join(str(block.get("text", "")) for block in system if isinstance(block, dict))
    return ""


def script_for(body: dict[str, Any]) -> dict[str, Any]:
    """The script a request's system prompt carries, or an empty one."""
    found = SCRIPT_MARKER.search(_system_text(body.get("system")))
    if not found:
        return {}
    script: dict[str, Any] = json.loads(found.group(1))
    return script


def next_step(body: dict[str, Any]) -> dict[str, Any]:
    """The content block and stop reason the script gives for this turn."""
    script = script_for(body)
    turn = sum(1 for message in body.get("messages", []) if message.get("role") == "assistant")
    tools = script.get("tools") or []
    if turn < len(tools):
        name, arguments = tools[turn]
        return {
            "block": {
                "type": "tool_use",
                "id": f"toolu_{uuid.uuid4().hex[:24]}",
                "name": name,
                "input": arguments,
            },
            "stop_reason": "tool_use",
        }
    return {
        "block": {"type": "text", "text": str(script.get("text") or "done")},
        "stop_reason": "end_turn",
    }


def _latency_seconds(body: dict[str, Any]) -> float:
    script = script_for(body)
    base = float(script.get("latency_ms", _control.latency_ms)) / 1000
    spread = base * _control.jitter
    return max(0.0, random.uniform(base - spread, base + spread))


def _fault() -> JSONResponse | None:
    """A drawn fault response, as Anthropic's API shapes its errors, or None."""
    roll = random.random()
    for status, rate, kind in (
        (429, _control.rate_429, "rate_limit_error"),
        (500, _control.rate_500, "api_error"),
        (401, _control.rate_401, "authentication_error"),
    ):
        if roll < rate:
            with _lock:
                _stats.faults[str(status)] += 1
            return JSONResponse(
                {"type": "error", "error": {"type": kind, "message": f"injected {status}"}},
                status_code=status,
            )
        roll -= rate
    return None


def _message(step: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": f"msg_{uuid.uuid4().hex[:24]}",
        "type": "message",
        "role": "assistant",
        "model": MODEL,
        "content": [step["block"]],
        "stop_reason": step["stop_reason"],
        "stop_sequence": None,
        "usage": {"input_tokens": 100, "output_tokens": 20},
    }


def _sse(event: str, data: dict[str, Any]) -> bytes:
    return f"event: {event}\ndata: {json.dumps(data)}\n\n".encode()


async def _stream(message: dict[str, Any]) -> AsyncIterator[bytes]:
    """The server-sent events Anthropic streams for ``message``."""
    block = message["content"][0]
    yield _sse(
        "message_start",
        {"type": "message_start", "message": {**message, "content": [], "stop_reason": None}},
    )
    if block["type"] == "text":
        yield _sse(
            "content_block_start",
            {
                "type": "content_block_start",
                "index": 0,
                "content_block": {"type": "text", "text": ""},
            },
        )
        yield _sse(
            "content_block_delta",
            {
                "type": "content_block_delta",
                "index": 0,
                "delta": {"type": "text_delta", "text": block["text"]},
            },
        )
    else:
        yield _sse(
            "content_block_start",
            {
                "type": "content_block_start",
                "index": 0,
                "content_block": {**block, "input": {}},
            },
        )
        yield _sse(
            "content_block_delta",
            {
                "type": "content_block_delta",
                "index": 0,
                "delta": {"type": "input_json_delta", "partial_json": json.dumps(block["input"])},
            },
        )
    yield _sse("content_block_stop", {"type": "content_block_stop", "index": 0})
    yield _sse(
        "message_delta",
        {
            "type": "message_delta",
            "delta": {"stop_reason": message["stop_reason"], "stop_sequence": None},
            "usage": {"output_tokens": message["usage"]["output_tokens"]},
        },
    )
    yield _sse("message_stop", {"type": "message_stop"})


@app.post("/v1/messages")
async def messages(request: Request) -> Any:
    """Answer one model call from the request's script, after the configured latency."""
    body = await request.json()
    with _lock:
        _stats.requests += 1
        _stats.in_flight += 1
        _stats.max_in_flight = max(_stats.max_in_flight, _stats.in_flight)
    try:
        await asyncio.sleep(_latency_seconds(body))
        if (fault := _fault()) is not None:
            return fault
        message = _message(next_step(body))
        if body.get("stream"):
            with _lock:
                _stats.streamed += 1
            return StreamingResponse(_stream(message), media_type="text/event-stream")
        return JSONResponse(message)
    finally:
        with _lock:
            _stats.in_flight -= 1


@app.post("/control")
async def control(request: Request) -> Any:
    """Set latency and fault rates for the requests that follow; returns the settings."""
    updates = await request.json()
    for name, value in updates.items():
        if not hasattr(_control, name):
            return JSONResponse({"error": f"unknown setting {name!r}"}, status_code=400)
        setattr(_control, name, type(getattr(_control, name))(value))
    return asdict(_control)


@app.get("/stats")
async def stats() -> dict[str, Any]:
    """What the gateway has served."""
    with _lock:
        return {**asdict(_stats), "faults": dict(_stats.faults), "at": time.time()}


@app.post("/reset")
async def reset() -> dict[str, Any]:
    """Zero the stats and restore the default settings."""
    global _control, _stats
    with _lock:
        _control = Control()
        _stats = Stats()
    return {"ok": True}
