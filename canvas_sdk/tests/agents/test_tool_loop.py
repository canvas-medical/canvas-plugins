import copy
import json
from types import SimpleNamespace
from typing import Any

import anthropic
import httpx2
import pytest
from anthropic.types import TextBlock, ToolUseBlock

from canvas_sdk.agents import (
    AgentPlugin,
    AgentRunResult,
    AgentState,
    RunSubject,
    ToolRegistry,
    run_tool_loop,
)


def _tool_use(name: str, block_id: str, **arguments: Any) -> ToolUseBlock:
    return ToolUseBlock(id=block_id, name=name, input=arguments, type="tool_use")


def _text(text: str) -> TextBlock:
    return TextBlock(text=text, type="text")


def _response(stop_reason: str, *content: Any) -> SimpleNamespace:
    return SimpleNamespace(stop_reason=stop_reason, content=list(content))


class _FakeClient:
    """Returns queued responses and records a copy of each request."""

    def __init__(self, *responses: Any) -> None:
        self._responses = list(responses)
        self.requests: list[dict[str, Any]] = []
        self.messages = self

    def create(self, **kwargs: Any) -> Any:
        self.requests.append(copy.deepcopy(kwargs))
        response = self._responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response


class _FakeGateway:
    model = "claude-test"

    def __init__(self, client: _FakeClient) -> None:
        self._client = client

    def client(self) -> _FakeClient:
        return self._client


def _tools() -> ToolRegistry:
    tools = ToolRegistry()

    @tools.tool(name="read_chart", description="x", input_schema={"type": "object"})
    def _read_chart(arguments: dict[str, Any], *, ctx: dict[str, Any]) -> dict[str, Any]:
        return {"patient": ctx["patient_id"], "asked": arguments}

    @tools.tool(name="broken", description="x", input_schema={"type": "object"})
    def _broken(arguments: dict[str, Any], *, ctx: dict[str, Any]) -> None:
        raise ValueError("no such record")

    return tools


def _run(client: _FakeClient, messages: list[dict[str, Any]] | None = None, **kwargs: Any) -> Any:
    return run_tool_loop(
        _FakeGateway(client),  # type: ignore[arg-type]
        tools=kwargs.pop("tools", _tools()),
        ctx={"patient_id": "p1"},
        system="You are a test agent.",
        messages=messages or [{"role": "user", "content": "go"}],
        **kwargs,
    )


def test_end_turn_returns_the_final_text() -> None:
    """A model that answers without tools ends the loop after one turn."""
    result = _run(_FakeClient(_response("end_turn", _text("  All clear. "))))

    assert result.text == "All clear."
    assert result.turns == 1
    assert result.stopped == "end_turn"
    assert result.messages[-1] == {
        "role": "assistant",
        "content": [{"type": "text", "text": "  All clear. ", "citations": None}],
    }


def test_tool_calls_are_dispatched_and_their_results_sent_back() -> None:
    """Each tool call runs with ctx and its JSON result goes back on the next turn."""
    client = _FakeClient(
        _response("tool_use", _tool_use("read_chart", "t1", section="labs")),
        _response("end_turn", _text("done")),
    )

    result = _run(client)

    results = client.requests[1]["messages"][-1]
    assert results["role"] == "user"
    assert results["content"] == [
        {
            "type": "tool_result",
            "tool_use_id": "t1",
            "content": json.dumps({"patient": "p1", "asked": {"section": "labs"}}),
        }
    ]
    assert result.turns == 2
    assert result.stopped == "end_turn"


def test_a_failing_tool_goes_back_to_the_model_as_an_error() -> None:
    """The model sees the failure and can recover; the run does not end."""
    client = _FakeClient(
        _response("tool_use", _tool_use("broken", "t1")),
        _response("end_turn", _text("sorry")),
    )

    _run(client)

    (tool_result,) = client.requests[1]["messages"][-1]["content"]
    assert tool_result["is_error"] is True
    assert "no such record" in tool_result["content"]


def test_an_ungranted_tool_is_reported_as_unknown() -> None:
    """A tool the scoped registry lacks fails like any other tool, back to the model."""
    client = _FakeClient(
        _response("tool_use", _tool_use("originate_prescribe_medication", "t1")),
        _response("end_turn", _text("ok")),
    )

    _run(client)

    (tool_result,) = client.requests[1]["messages"][-1]["content"]
    assert tool_result["is_error"] is True
    assert "Unknown tool" in tool_result["content"]


def test_complete_tool_calls_cut_off_by_max_tokens_still_run() -> None:
    """max_tokens with tool calls dispatches them and continues."""
    client = _FakeClient(
        _response("max_tokens", _tool_use("read_chart", "t1")),
        _response("end_turn", _text("done")),
    )

    result = _run(client)

    assert client.requests[1]["messages"][-1]["content"][0]["tool_use_id"] == "t1"
    assert result.stopped == "end_turn"


def test_the_turn_cap_stops_the_loop() -> None:
    """A model that keeps calling tools stops at max_turns with its results recorded."""
    client = _FakeClient(
        _response("tool_use", _tool_use("read_chart", "t1")),
        _response("tool_use", _tool_use("read_chart", "t2")),
    )

    result = _run(client, max_turns=2)

    assert result.stopped == "max_turns"
    assert result.turns == 2
    assert result.messages[-1]["content"][0]["tool_use_id"] == "t2"


def test_an_unexpected_stop_never_leaves_a_tool_call_without_a_result() -> None:
    """A stored transcript ending on an unanswered tool call would fail every later call."""
    client = _FakeClient(_response("refusal", _tool_use("read_chart", "t1")))

    result = _run(client)

    assert result.stopped == "unexpected"
    assert result.stop_reason == "refusal"
    (tool_result,) = result.messages[-1]["content"]
    assert tool_result == {
        "type": "tool_result",
        "tool_use_id": "t1",
        "content": "Not run: the turn ended with stop reason 'refusal'.",
        "is_error": True,
    }


def test_the_model_sees_a_window_and_the_full_history_comes_back() -> None:
    """Long histories are windowed for the call but returned whole for storage."""
    history: list[dict[str, Any]] = [
        {"role": "user", "content": "old " + "x" * 5000},
        {"role": "assistant", "content": [{"type": "text", "text": "old answer"}]},
        {"role": "user", "content": "new question"},
    ]
    client = _FakeClient(_response("end_turn", _text("new answer")))

    result = _run(client, messages=history, history_chars=200)

    assert client.requests[0]["messages"] == [history[2]]
    assert result.messages[:3] == history
    assert len(result.messages) == 4


def test_windowing_can_be_turned_off() -> None:
    """history_chars=None sends everything."""
    history: list[dict[str, Any]] = [
        {"role": "user", "content": "old " + "x" * 5000},
        {"role": "assistant", "content": [{"type": "text", "text": "old answer"}]},
        {"role": "user", "content": "new question"},
    ]
    client = _FakeClient(_response("end_turn", _text("new answer")))

    _run(client, messages=history, history_chars=None)

    assert client.requests[0]["messages"] == history


def test_the_system_prompt_is_marked_for_caching_by_default() -> None:
    """The system prompt is the stable prefix every turn and run shares."""
    client = _FakeClient(_response("end_turn", _text("ok")))

    _run(client)

    assert client.requests[0]["system"] == [
        {
            "type": "text",
            "text": "You are a test agent.",
            "cache_control": {"type": "ephemeral"},
        }
    ]


def test_caching_can_be_turned_off() -> None:
    """cache_system=False sends the system prompt as a plain string."""
    client = _FakeClient(_response("end_turn", _text("ok")))

    _run(client, cache_system=False)

    assert client.requests[0]["system"] == "You are a test agent."


def test_the_request_uses_the_gateway_model_and_the_given_limits() -> None:
    """Model defaults to the gateway's; tools come from the registry."""
    client = _FakeClient(_response("end_turn", _text("ok")))

    _run(client, max_tokens=123)

    request = client.requests[0]
    assert request["model"] == "claude-test"
    assert request["max_tokens"] == 123
    assert [tool["name"] for tool in request["tools"]] == ["read_chart", "broken"]


def test_on_turn_fires_before_each_call() -> None:
    """The turn hook sees 0, 1, ... once per LLM call."""
    seen: list[int] = []
    client = _FakeClient(
        _response("tool_use", _tool_use("read_chart", "t1")),
        _response("end_turn", _text("done")),
    )

    _run(client, on_turn=seen.append)

    assert seen == [0, 1]


def test_a_failing_turn_hook_does_not_end_the_run() -> None:
    """Hooks are for observability, so their failures are logged and ignored."""

    def _broken_hook(turn_index: int) -> None:
        raise RuntimeError("metrics are down")

    result = _run(_FakeClient(_response("end_turn", _text("ok"))), on_turn=_broken_hook)

    assert result.stopped == "end_turn"


def test_gateway_errors_propagate() -> None:
    """The platform classifies gateway failures, so the loop must not swallow them."""
    request = httpx2.Request("POST", "https://gateway.test/v1/messages")
    error = anthropic.APIConnectionError(request=request)

    with pytest.raises(anthropic.APIConnectionError):
        _run(_FakeClient(error))


def test_the_callers_message_list_is_not_modified() -> None:
    """The loop works on a copy; the caller decides what to store."""
    history = [{"role": "user", "content": "go"}]

    _run(_FakeClient(_response("end_turn", _text("ok"))), messages=history)

    assert history == [{"role": "user", "content": "go"}]


def test_the_result_effects_are_the_ctx_effects_list() -> None:
    """Sub-agents share the parent's ctx, so their effects land in the parent's list."""
    effects: list[Any] = ["staged earlier"]
    ctx = {"patient_id": "p1", "effects": effects}

    result = run_tool_loop(
        _FakeGateway(_FakeClient(_response("end_turn", _text("ok")))),  # type: ignore[arg-type]
        tools=_tools(),
        ctx=ctx,
        system="s",
        messages=[{"role": "user", "content": "go"}],
    )

    assert result.effects is effects


class _LoopingAgent(AgentPlugin):
    tools = _tools()

    def __init__(self) -> None:
        self.turns_seen: list[int] = []

    def on_turn(self, turn_index: int) -> None:
        self.turns_seen.append(turn_index)

    def load_state(self, scope_key: str) -> AgentState:
        return AgentState()

    def run(self, state: AgentState, gateway: Any, trigger_payload: dict) -> AgentRunResult:
        return AgentRunResult(state=state)

    def save_state(self, scope_key: str, state: AgentState) -> None:
        return None


def test_the_agent_method_uses_its_tools_and_on_turn_hook() -> None:
    """AgentPlugin.run_tool_loop passes self.tools and wires on_turn."""
    agent = _LoopingAgent()
    agent.tools = _LoopingAgent.tools.scope({"read_chart"})
    agent.subject = RunSubject(patient_id="p1")
    client = _FakeClient(
        _response("tool_use", _tool_use("read_chart", "t1")),
        _response("end_turn", _text("done")),
    )

    result = agent.run_tool_loop(
        _FakeGateway(client),  # type: ignore[arg-type]
        system="s",
        messages=[{"role": "user", "content": "go"}],
    )

    assert [tool["name"] for tool in client.requests[0]["tools"]] == ["read_chart"]
    assert agent.turns_seen == [0, 1]
    assert result.stopped == "end_turn"


def test_the_agent_method_gives_tools_the_run_subject() -> None:
    """Tools read the platform's patient; the agent never names one."""
    agent = _LoopingAgent()
    agent.tools = _LoopingAgent.tools.scope({"read_chart"})
    agent.subject = RunSubject(patient_id="p1")
    client = _FakeClient(
        _response("tool_use", _tool_use("read_chart", "t1")),
        _response("end_turn", _text("done")),
    )

    agent.run_tool_loop(
        _FakeGateway(client),  # type: ignore[arg-type]
        system="s",
        messages=[{"role": "user", "content": "go"}],
    )

    (tool_result,) = client.requests[1]["messages"][-1]["content"]
    assert json.loads(tool_result["content"])["patient"] == "p1"


def test_the_agent_method_returns_the_effects_its_tools_staged() -> None:
    """Staged effects come back on the result, so the agent returns them as-is."""
    tools = ToolRegistry()

    @tools.tool(name="stage", description="x", input_schema={"type": "object"})
    def _stage(arguments: dict[str, Any], *, ctx: dict[str, Any]) -> dict[str, Any]:
        ctx["effects"].append("an effect")
        return {"ok": True}

    agent = _LoopingAgent()
    agent.tools = tools
    client = _FakeClient(
        _response("tool_use", _tool_use("stage", "t1")),
        _response("end_turn", _text("done")),
    )

    result = agent.run_tool_loop(
        _FakeGateway(client),  # type: ignore[arg-type]
        system="s",
        messages=[{"role": "user", "content": "go"}],
    )

    assert result.effects == ["an effect"]
