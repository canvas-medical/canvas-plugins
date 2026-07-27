from canvas_sdk.agents import AgentRunResult, AgentState
from canvas_sdk.commands import PlanCommand


def test_agent_run_result_carries_state_and_empty_effects() -> None:
    """A bare result wraps a state and an empty effects list by default."""
    state = AgentState()
    result = AgentRunResult(state=state)
    assert result.state is state
    assert result.effects == []


def test_agent_run_result_accepts_effects() -> None:
    """The effects field accepts canvas_sdk.effects.Effect wrappers."""
    plan = PlanCommand(note_uuid="note-uuid", narrative="follow up").originate()
    result = AgentRunResult(state=AgentState(), effects=[plan])
    assert result.effects == [plan]


def test_agent_run_result_default_effects_not_shared() -> None:
    """Each result instance gets its own effects list (default_factory, not [])."""
    a = AgentRunResult(state=AgentState())
    b = AgentRunResult(state=AgentState())
    a.effects.append(PlanCommand(note_uuid="note-uuid", narrative="follow up").originate())
    assert b.effects == [], "default_factory should give each instance its own list"
