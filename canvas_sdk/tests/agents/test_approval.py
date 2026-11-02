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


@tools.tool(
    name="note_and_plan",
    description="x",
    input_schema={"type": "object"},
    effect_types=("CREATE_NOTE", "ORIGINATE_PLAN_COMMAND"),
)
def _note_and_plan(arguments: dict[str, Any], *, ctx: dict[str, Any]) -> dict[str, Any]:
    """Stages a note and a plan on it, as originate_review_note does."""
    ctx["effects"].append(Effect(type=EffectType.CREATE_NOTE, payload='{"note": "n1"}'))
    ctx["effects"].append(Effect(type=EffectType.ORIGINATE_PLAN_COMMAND, payload='{"note": "n1"}'))
    return {"ok": True}


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
    assert data["effects"] == [{"type": "CREATE_TASK", "payload": '{"data": {"title": "x"}}'}]
    assert result["status"] == "awaiting_approval"
    assert result["proposal_ids"] == [data["proposal_id"]]
    assert result["tool_result"] == {"ok": True}


def test_a_tool_call_that_stages_several_changes_proposes_them_together() -> None:
    """The requester approves or denies the whole call, and its changes apply in order.

    A plan on a note the same call creates cannot apply, or be approved, without the note.
    """
    agent = _Agent()
    grant = apply_tool_grant(agent, {"allowed": ["note_and_plan"], "approve": ["note_and_plan"]})
    assert agent.tools is not None
    effects: list[Effect] = []

    result = agent.tools.execute("note_and_plan", {}, ctx={"effects": effects})

    (proposal,) = effects
    data = json.loads(proposal.payload)["data"]
    assert [effect["type"] for effect in data["effects"]] == [
        "CREATE_NOTE",
        "ORIGINATE_PLAN_COMMAND",
    ]
    assert result["proposal_ids"] == [data["proposal_id"]]
    assert split_granted_effects([proposal], grant) == ([proposal], [])


def test_a_proposal_mixing_in_a_change_no_approval_tool_stages_is_dropped() -> None:
    """Every change a proposal carries must be one the agent's approval-listed tools make."""
    _, grant = _granted(["create_task"])
    mixed = propose(
        [
            Effect(type=EffectType.CREATE_TASK, payload="{}"),
            Effect(type=EffectType.ADD_BANNER_ALERT, payload="{}"),
        ],
        "create_task",
        {},
    )
    empty = propose([], "create_task", {})

    assert split_granted_effects([mixed, empty], grant) == ([], [mixed, empty])


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
    proposed = propose([bare], "create_task", {})

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
    nested = propose([propose([Effect(type=EffectType.CREATE_TASK)], "t", {})], "t", {})

    kept, dropped = split_granted_effects([decision, propose([decision], "t", {}), nested], grant)

    assert kept == []
    assert len(dropped) == 3


def test_a_proposal_of_an_effect_no_approval_tool_stages_is_dropped() -> None:
    """A proposal still has to wrap a change the agent's approval-listed tools make."""
    _, grant = _granted(["create_task"])
    other = propose([Effect(type=EffectType.ADD_BANNER_ALERT, payload="{}")], "create_task", {})

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


@tools.tool(
    name="create_task_too",
    description="x",
    input_schema={"type": "object"},
    effect_types=("CREATE_TASK",),
)
def _create_task_too(arguments: dict[str, Any], *, ctx: dict[str, Any]) -> dict[str, Any]:
    ctx["effects"].append(Effect(type=EffectType.CREATE_TASK, payload='{"data": {"title": "y"}}'))
    return {"ok": True}


def test_a_tool_sharing_an_effect_type_with_an_approval_tool_proposes_too() -> None:
    """Approval covers the change, not one tool's name, so no granted tool can make it bare.

    Otherwise agent code could return the change unwrapped, as if a tool needing no
    approval had staged it, and the grant check could not tell the two apart.
    """
    agent = _Agent()
    grant = apply_tool_grant(
        agent, {"allowed": ["create_task", "create_task_too"], "approve": ["create_task"]}
    )
    assert agent.tools is not None
    bare = Effect(type=EffectType.CREATE_TASK, payload="{}")

    assert agent.tools.requires_approval("create_task_too")
    assert grant.direct == frozenset()
    assert split_granted_effects([bare], grant) == ([], [bare])
