from types import SimpleNamespace
from typing import Any

from anthropic.types import TextBlock, ToolUseBlock

from canvas_sdk.agents import SubAgentSpec, ToolRegistry, run_subagents
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
