import threading
from types import SimpleNamespace
from typing import Any

import anthropic
import httpx2
import pytest
from anthropic.types import TextBlock, ToolUseBlock

from canvas_sdk.agents import SubAgentSpec, ToolRegistry, run_subagent, run_subagents, subagent
from canvas_sdk.agents.gateway import count_model_call
from canvas_sdk.agents.run_record import RunDeadlineExceeded, RunRecorder, current_recorder
from canvas_sdk.agents.subagent import MAX_PARALLEL
from canvas_sdk.test_utils.agents import FakeGateway, reply, text, tool_use
from canvas_sdk.v1.plugin_database_context import (
    get_access_level,
    get_current_plugin,
    get_current_schema,
    plugin_database_context,
)


class _FakeMessages:
    """Answers a tool call on the first turn and ends on the second."""

    def __init__(self) -> None:
        self.calls = 0

    def create(self, **kwargs: Any) -> SimpleNamespace:
        count_model_call(kwargs)
        self.calls = self.calls + 1
        if self.calls == 1:
            return SimpleNamespace(
                stop_reason="tool_use",
                content=[ToolUseBlock(id="t1", name="read_chart", input={}, type="tool_use")],
            )
        return SimpleNamespace(
            stop_reason="end_turn", content=[TextBlock(text="done", type="text")]
        )


class _FakeGateway:
    model = "claude-test"

    def client(self) -> SimpleNamespace:
        return SimpleNamespace(messages=_FakeMessages())


def test_subagent_tools_run_in_the_parent_plugins_database_context() -> None:
    """Sub-agents run on worker threads, which must see the parent's plugin and namespace."""
    seen: list[tuple[str | None, str | None, str]] = []
    tools = ToolRegistry()

    @tools.tool(name="read_chart", description="x", input_schema={"type": "object"})
    def _read_chart(arguments: dict[str, Any], *, ctx: dict[str, Any]) -> dict[str, Any]:
        seen.append((get_current_plugin(), get_current_schema(), get_access_level()))
        return {}

    spec = SubAgentSpec(
        name="labs", system_prompt="x", allowed_tool_names=frozenset({"read_chart"})
    )
    with plugin_database_context("my_plugin", namespace="my_namespace", access_level="read_write"):
        results = run_subagents(
            [spec],
            "question",
            parent_tools=tools,
            parent_ctx={},
            gateway=_FakeGateway(),  # type: ignore[arg-type]
        )

    assert results == {"labs": "done"}
    assert seen == [("my_plugin", "my_namespace", "read_write")]


def test_subagent_model_and_tool_calls_land_in_the_runs_recorder() -> None:
    """The run record counts sub-agents' work, which happens on pool threads."""
    tools = ToolRegistry()

    @tools.tool(name="read_chart", description="x", input_schema={"type": "object"})
    def _read_chart(arguments: dict[str, Any], *, ctx: dict[str, Any]) -> dict[str, Any]:
        return {}

    specs = [
        SubAgentSpec(name=name, system_prompt="x", allowed_tool_names=frozenset({"read_chart"}))
        for name in ("labs", "meds")
    ]
    recorder = RunRecorder()
    token = current_recorder.set(recorder)
    try:
        run_subagents(
            specs,
            "question",
            parent_tools=tools,
            parent_ctx={},
            gateway=_FakeGateway(),  # type: ignore[arg-type]
        )
    finally:
        current_recorder.reset(token)

    assert recorder.model_calls == 4
    assert [(call.name, call.ok) for call in recorder.tool_calls] == [("read_chart", True)] * 2


class _FailingGateway:
    model = "claude-test"

    def __init__(self, error: Exception) -> None:
        self.error = error

    def client(self) -> SimpleNamespace:
        def create(**kwargs: Any) -> None:
            raise self.error

        return SimpleNamespace(messages=SimpleNamespace(create=create))


def test_a_subagents_gateway_error_is_raised_for_the_run_to_report() -> None:
    """An outage or refusal inside a sub-agent ends the run as LLM_UNAVAILABLE or LLM_REFUSED."""
    error = anthropic.APIConnectionError(
        request=httpx2.Request("POST", "https://gateway.test/v1/messages")
    )
    spec = SubAgentSpec(name="labs", system_prompt="x")

    with pytest.raises(anthropic.APIConnectionError):
        run_subagents(
            [spec],
            "question",
            parent_tools=ToolRegistry(),
            parent_ctx={},
            gateway=_FailingGateway(error),  # type: ignore[arg-type]
        )


def test_any_other_subagent_failure_comes_back_as_its_result() -> None:
    """The parent decides what to do about a sub-agent that failed on its own."""
    spec = SubAgentSpec(name="labs", system_prompt="x")

    results = run_subagents(
        [spec],
        "question",
        parent_tools=ToolRegistry(),
        parent_ctx={},
        gateway=_FailingGateway(ValueError("bad prompt")),  # type: ignore[arg-type]
    )

    assert results == {"labs": "(sub-agent 'labs' failed: bad prompt)"}


def test_max_parallel_is_capped() -> None:
    """Each worker holds a database connection, so a fan-out cannot ask for unbounded threads."""
    running: list[int] = []
    peak: list[int] = [0]
    lock = threading.Lock()
    release = threading.Event()
    tools = ToolRegistry()

    @tools.tool(name="read_chart", description="x", input_schema={"type": "object"})
    def _read_chart(arguments: dict[str, Any], *, ctx: dict[str, Any]) -> dict[str, Any]:
        with lock:
            running.append(1)
            peak[0] = max(peak[0], len(running))
            # Held past the cap's worth of arrivals, so a larger pool would start more.
            if len(running) == MAX_PARALLEL:
                threading.Timer(0.3, release.set).start()
        release.wait(timeout=5)
        with lock:
            running.pop()
        return {}

    specs = [
        SubAgentSpec(name=f"s{i}", system_prompt="x", allowed_tool_names=frozenset({"read_chart"}))
        for i in range(MAX_PARALLEL + 4)
    ]
    run_subagents(
        specs,
        "question",
        parent_tools=tools,
        parent_ctx={},
        gateway=_FakeGateway(),  # type: ignore[arg-type]
        max_parallel=100,
    )

    assert peak[0] == MAX_PARALLEL


def test_a_subagent_reaches_only_the_tools_its_spec_allows() -> None:
    """A sub-agent's tools are its spec's subset of the parent's granted tools."""
    called: list[str] = []
    tools = ToolRegistry()
    for name in ("read_chart", "write_chart"):

        @tools.tool(name=name, description="x", input_schema={"type": "object"})
        def _tool(arguments: dict[str, Any], *, ctx: dict[str, Any], _name: str = name) -> dict:
            called.append(_name)
            return {}

    gateway = FakeGateway(reply(tool_use("write_chart")), reply(text("done")))
    spec = SubAgentSpec(
        name="labs", system_prompt="x", allowed_tool_names=frozenset({"read_chart"})
    )

    result = run_subagent(
        spec,
        "question",
        parent_tools=tools,
        parent_ctx={},
        gateway=gateway,  # type: ignore[arg-type]
    )

    assert result == "done"
    assert called == []
    assert [d["name"] for d in gateway.requests[0]["tools"]] == ["read_chart"]


def test_a_subagent_cannot_widen_past_the_parents_grant() -> None:
    """A spec naming a tool the parent's scoped registry lacks gets nothing for it."""
    tools = ToolRegistry()

    @tools.tool(name="read_chart", description="x", input_schema={"type": "object"})
    def _read(arguments: dict[str, Any], *, ctx: dict[str, Any]) -> dict:
        return {}

    gateway = FakeGateway(reply(text("done")))
    spec = SubAgentSpec(
        name="labs",
        system_prompt="x",
        allowed_tool_names=frozenset({"read_chart", "delete_chart"}),
    )

    run_subagent(spec, "question", parent_tools=tools, parent_ctx={}, gateway=gateway)  # type: ignore[arg-type]

    assert [d["name"] for d in gateway.requests[0]["tools"]] == ["read_chart"]


def test_a_subagent_calls_the_model_its_spec_names() -> None:
    """A cheap extraction can run on a cheap model while the parent uses a stronger one."""
    gateway = FakeGateway(reply(text("Two values.")))
    spec = SubAgentSpec(name="extract", system_prompt="Extract.", model="claude-haiku-4-5")

    answer = run_subagent(
        spec,
        "Read it.",
        parent_tools=ToolRegistry(),
        parent_ctx={"effects": []},
        gateway=gateway,  # type: ignore[arg-type]
    )

    assert answer == "Two values."
    assert gateway.requests[0]["model"] == "claude-haiku-4-5"


def test_a_subagent_past_the_runs_deadline_ends_the_run() -> None:
    """Running out of time in a sub-agent ends the run, as it would in the parent."""
    spec = SubAgentSpec(name="labs", system_prompt="x")

    with pytest.raises(RunDeadlineExceeded):
        run_subagents(
            [spec],
            "question",
            parent_tools=ToolRegistry(),
            parent_ctx={},
            gateway=_FailingGateway(RunDeadlineExceeded("out of time")),  # type: ignore[arg-type]
        )


def test_each_subagent_worker_closes_its_database_connections(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A pool thread's connection is closed when its sub-agent finishes, failing or not."""
    closed_on: list[str] = []
    monkeypatch.setattr(
        subagent.connections,
        "close_all",
        lambda: closed_on.append(threading.current_thread().name),
    )
    specs = [SubAgentSpec(name=name, system_prompt="x") for name in ("labs", "meds")]

    run_subagents(
        specs,
        "question",
        parent_tools=ToolRegistry(),
        parent_ctx={},
        gateway=_FailingGateway(ValueError("bad prompt")),  # type: ignore[arg-type]
    )

    assert len(closed_on) == 2
    assert threading.current_thread().name not in closed_on


def test_a_subagent_is_never_given_a_composition_tool() -> None:
    """A sub-agent cannot run sub-agents of its own, so a run fans out one level."""
    tools = ToolRegistry()

    @tools.tool(
        name="summarize",
        description="x",
        input_schema={"type": "object"},
        categories=("composition",),
    )
    def _summarize(arguments: dict[str, Any], *, ctx: dict[str, Any]) -> dict[str, Any]:
        return {}

    @tools.tool(name="read_chart", description="x", input_schema={"type": "object"})
    def _read_chart(arguments: dict[str, Any], *, ctx: dict[str, Any]) -> dict[str, Any]:
        return {}

    gateway = FakeGateway(reply(text("done")))
    spec = SubAgentSpec(
        name="labs", system_prompt="x", allowed_tool_names=frozenset({"summarize", "read_chart"})
    )

    run_subagent(
        spec,
        "question",
        parent_tools=tools,
        parent_ctx={},
        gateway=gateway,  # type: ignore[arg-type]
    )

    assert [tool["name"] for tool in gateway.requests[0]["tools"]] == ["read_chart"]
