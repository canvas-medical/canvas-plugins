from typing import Any

import pytest

from canvas_sdk.agents import (
    AgentPlugin,
    AgentRunResult,
    AgentState,
    Capability,
    RunRequester,
    ToolNotAllowed,
    ToolRegistry,
)
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

# A write only staff holding a permission may make, and a read only a capability opens.
tools.register(
    {"name": "update_task", "description": "x", "input_schema": {"type": "object"}},
    _noop,
    categories=("writes",),
    effect_types=("UPDATE_TASK",),
    required_permissions=("api.change_task",),
)
tools.register(
    {"name": "read_claims", "description": "x", "input_schema": {"type": "object"}},
    _noop,
    categories=("reads",),
    required_capabilities=(Capability.REVENUE,),
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

    apply_tool_grant(agent, {"allowed": ["@reads"], "denied": ["read_b", "read_claims"]})

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
    assert apply_tool_grant(_Agent(), {"allowed": ["@writes"]}) == frozenset(
        {"CREATE_TASK", "UPDATE_TASK"}
    )


def test_tools_the_requester_lacks_a_permission_for_are_hidden() -> None:
    """A staff member without change_task is never offered the task update, nor its effects."""
    agent = _Agent()
    agent.requester = RunRequester(staff_id="s1", permissions=frozenset({"api.view_task"}))

    effect_types = apply_tool_grant(agent, {"allowed": ["@writes"]})

    assert _names(agent) == {"write_task"}
    assert agent.tools_allowed == frozenset({"write_task"})
    assert effect_types == frozenset({"CREATE_TASK"})


def test_a_requester_holding_the_permission_is_offered_the_tool() -> None:
    """The grant hides only what the requester could not do in the chart."""
    agent = _Agent()
    agent.requester = RunRequester(staff_id="s1", permissions=frozenset({"api.change_task"}))

    apply_tool_grant(agent, {"allowed": ["@writes"]})

    assert _names(agent) == {"write_task", "update_task"}


def test_a_run_permissions_do_not_limit_is_offered_every_granted_tool() -> None:
    """Canvas Bot, patient, and superuser runs have no permission set to check."""
    agent = _Agent()
    agent.requester = RunRequester(staff_id=None, permissions=None)

    apply_tool_grant(agent, {"allowed": ["@writes"]})

    assert _names(agent) == {"write_task", "update_task"}


def test_tools_needing_a_capability_the_run_lacks_are_hidden() -> None:
    """The claims reads appear only for a run granted the revenue capability."""
    without = _Agent()
    apply_tool_grant(without, {"allowed": ["@reads"]})
    with_revenue = _Agent()
    with_revenue.capabilities = frozenset({Capability.REVENUE})
    apply_tool_grant(with_revenue, {"allowed": ["@reads"]})

    assert "read_claims" not in _names(without)
    assert "read_claims" in _names(with_revenue)


def test_the_registry_refuses_a_tool_the_runs_permissions_do_not_cover() -> None:
    """A sub-agent, or a model replaying a remembered tool name, cannot get past the hiding."""
    with pytest.raises(ToolNotAllowed, match="api.change_task"):
        tools.execute("update_task", {}, ctx={"permissions": frozenset(), "effects": []})

    assert tools.execute("update_task", {}, ctx={"permissions": None, "effects": []}) == {}
