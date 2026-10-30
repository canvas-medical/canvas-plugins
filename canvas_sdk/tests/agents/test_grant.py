from typing import Any

from canvas_sdk.agents import AgentPlugin, AgentRunResult, AgentState, ToolRegistry
from canvas_sdk.agents.grant import apply_tool_grant

tools = ToolRegistry()


def _noop(arguments: dict[str, Any], *, ctx: dict[str, Any]) -> dict[str, Any]:
    return {}


for _name, _effect in (("read_a", ()), ("read_b", ()), ("write_task", ("CREATE_TASK",))):
    tools.register(
        {"name": _name, "description": "x", "input_schema": {"type": "object"}},
        _noop,
        categories=("reads",) if _name.startswith("read") else ("writes",),
        effect_types=_effect,
    )


class _Agent(AgentPlugin):
    tools = tools

    def load_state(self, scope_key: str) -> AgentState:
        return AgentState()

    def run(self, state: AgentState, gateway: Any, trigger_payload: dict) -> AgentRunResult:
        return AgentRunResult(state=state)

    def save_state(self, scope_key: str, state: AgentState) -> None:
        return None


def _names(agent: AgentPlugin) -> set[str]:
    assert agent.tools is not None
    return {definition["name"] for definition in agent.tools.definitions()}


def test_denied_is_subtracted_after_categories_expand() -> None:
    """A manifest can grant a category but hold back one of its tools."""
    agent = _Agent()

    apply_tool_grant(agent, {"allowed": ["@reads"], "denied": ["read_b"]})

    assert _names(agent) == {"read_a"}
    assert agent.tools_allowed == frozenset({"read_a"})


def test_denied_wins_over_a_tool_named_in_allowed() -> None:
    """Denying a tool removes it however it was granted."""
    agent = _Agent()

    apply_tool_grant(agent, {"allowed": ["read_a", "write_task"], "denied": ["write_task"]})

    assert _names(agent) == {"read_a"}


def test_a_grant_with_nothing_allowed_gives_no_tools() -> None:
    """An agent whose manifest grants nothing can call nothing and emit nothing."""
    agent = _Agent()

    effect_types = apply_tool_grant(agent, {})

    assert _names(agent) == set()
    assert effect_types == frozenset()


def test_the_grant_returns_the_effect_types_its_tools_declare() -> None:
    """These bound which of the agent's returned effects the platform keeps."""
    agent = _Agent()

    assert apply_tool_grant(agent, {"allowed": ["@reads"]}) == frozenset()
    assert apply_tool_grant(_Agent(), {"allowed": ["@writes"]}) == frozenset({"CREATE_TASK"})
