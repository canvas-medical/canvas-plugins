"""Tools a manifest lists under ``tools.approve`` propose their changes instead of making them."""

import json
from typing import Any

from canvas_sdk.agents import AgentPlugin, AgentRunResult, AgentState, ToolRegistry
from canvas_sdk.agents.approval import propose
from canvas_sdk.agents.grant import EffectGrant, apply_tool_grant, split_granted_effects
from canvas_sdk.effects import Effect, EffectType
from canvas_sdk.effects.agent import DecideAgentProposal

tools = ToolRegistry()


@tools.tool(
    name="create_task",
    description="x",
    input_schema={"type": "object"},
    categories=("writes",),
    effect_types=("CREATE_TASK",),
)
def _create_task(arguments: dict[str, Any], *, ctx: dict[str, Any]) -> dict[str, Any]:
    ctx["effects"].append(Effect(type=EffectType.CREATE_TASK, payload='{"data": {"title": "x"}}'))
    return {"ok": True}


@tools.tool(
    name="refuse",
    description="x",
    input_schema={"type": "object"},
    categories=("writes",),
    effect_types=("CREATE_TASK",),
)
def _refuse(arguments: dict[str, Any], *, ctx: dict[str, Any]) -> dict[str, Any]:
    return {"ok": False, "error": "nothing to do"}


@tools.tool(name="read", description="x", input_schema={"type": "object"})
def _read(arguments: dict[str, Any], *, ctx: dict[str, Any]) -> dict[str, Any]:
    return {"rows": []}


class _Agent(AgentPlugin):
    tools = tools

    def load_state(self, scope_key: str) -> AgentState:
        return AgentState()

    def run(self, state: AgentState, gateway: Any, trigger_payload: dict) -> AgentRunResult:
        return AgentRunResult(state=state)

    def save_state(self, scope_key: str, state: AgentState) -> None:
        return None


def _granted(approve: list[str]) -> tuple[AgentPlugin, EffectGrant]:
    agent = _Agent()
    grant = apply_tool_grant(agent, {"allowed": ["@writes", "read"], "approve": approve})
    return agent, grant


def test_an_approval_listed_tool_proposes_its_change_and_says_so() -> None:
    """The model learns nothing changed yet, and the run returns a proposal, not the task."""
    agent, _ = _granted(["create_task"])
    assert agent.tools is not None
    effects: list[Effect] = []

    result = agent.tools.execute("create_task", {"title": "Call"}, ctx={"effects": effects})

    (proposal,) = effects
    assert proposal.type == EffectType.PROPOSE_AGENT_ACTION
    data = json.loads(proposal.payload)["data"]
    assert (data["tool"], data["arguments"]) == ("create_task", {"title": "Call"})
    assert data["effect"]["type"] == "CREATE_TASK"
    assert result["status"] == "awaiting_approval"
    assert result["proposal_ids"] == [data["proposal_id"]]
    assert result["tool_result"] == {"ok": True}


def test_a_tool_not_listed_makes_its_change() -> None:
    """Approval is per tool: the rest stage their effects as before."""
    agent, _ = _granted([])
    assert agent.tools is not None
    effects: list[Effect] = []

    agent.tools.execute("create_task", {}, ctx={"effects": effects})

    assert [effect.type for effect in effects] == [EffectType.CREATE_TASK]


def test_an_approval_listed_tool_that_stages_nothing_returns_its_own_result() -> None:
    """There is nothing to approve when the tool refused."""
    agent, _ = _granted(["refuse"])
    assert agent.tools is not None
    effects: list[Effect] = []

    result = agent.tools.execute("refuse", {}, ctx={"effects": effects})

    assert result == {"ok": False, "error": "nothing to do"}
    assert effects == []


def test_categories_resolve_in_the_approve_list() -> None:
    """The manifest names tools for approval the same way it grants them."""
    agent, grant = _granted(["@writes"])
    assert agent.tools is not None

    assert agent.tools.requires_approval("create_task")
    assert agent.tools.requires_approval("refuse")
    assert not agent.tools.requires_approval("read")
    assert grant.proposable == frozenset({"CREATE_TASK"})
    assert grant.direct == frozenset()


def test_a_change_listed_for_approval_cannot_be_returned_bare() -> None:
    """Agent code appending the raw effect would skip approval, so the platform drops it."""
    _, grant = _granted(["create_task", "refuse"])
    bare = Effect(type=EffectType.CREATE_TASK, payload="{}")
    proposed = propose(bare, "create_task", {})

    kept, dropped = split_granted_effects([bare, proposed], grant)

    assert kept == [proposed]
    assert dropped == [bare]


def test_an_agent_can_never_decide_or_nest_a_proposal() -> None:
    """Only the requester decides; a proposal of a decision is dropped as well."""
    grant = EffectGrant(
        direct=frozenset({"DECIDE_AGENT_PROPOSAL"}),
        proposable=frozenset({"DECIDE_AGENT_PROPOSAL", "PROPOSE_AGENT_ACTION"}),
    )
    decision = DecideAgentProposal(
        proposal_id="00000000-0000-0000-0000-000000000001", decision="approve"
    ).apply()
    nested = propose(propose(Effect(type=EffectType.CREATE_TASK), "t", {}), "t", {})

    kept, dropped = split_granted_effects([decision, propose(decision, "t", {}), nested], grant)

    assert kept == []
    assert len(dropped) == 3


def test_a_proposal_of_an_effect_no_approval_tool_stages_is_dropped() -> None:
    """A proposal still has to wrap a change the agent's approval-listed tools make."""
    _, grant = _granted(["create_task"])
    other = propose(Effect(type=EffectType.ADD_BANNER_ALERT, payload="{}"), "create_task", {})

    assert split_granted_effects([other], grant) == ([], [other])


def test_sub_agents_inherit_approval() -> None:
    """A sub-agent scoped from its parent's tools proposes the same changes."""
    agent, _ = _granted(["create_task"])
    assert agent.tools is not None

    assert agent.tools.scope(["create_task"]).requires_approval("create_task")


def test_a_decision_carries_the_proposal_and_the_users_choice() -> None:
    """The plugin returns this when the user approves or denies."""
    effect = DecideAgentProposal(
        proposal_id="00000000-0000-0000-0000-000000000001", decision="deny", reason="wrong patient"
    ).apply()

    assert effect.type == EffectType.DECIDE_AGENT_PROPOSAL
    assert json.loads(effect.payload)["data"] == {
        "proposal_id": "00000000-0000-0000-0000-000000000001",
        "decision": "deny",
        "reason": "wrong patient",
    }
