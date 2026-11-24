from canvas_sdk.agents import AgentState


def test_agent_state_defaults_to_empty_data() -> None:
    """A bare AgentState() should expose an empty mutable dict."""
    state = AgentState()
    assert state.data == {}


def test_agent_state_accepts_initial_data() -> None:
    """The data field can be populated at construction time."""
    state = AgentState(data={"turn": 1, "summary": "ok"})
    assert state.data == {"turn": 1, "summary": "ok"}


def test_agent_state_data_is_mutable() -> None:
    """Mutating data after construction is supported (it's a dataclass)."""
    state = AgentState()
    state.data["count"] = 3
    assert state.data == {"count": 3}


def test_agent_state_default_dicts_are_not_shared() -> None:
    """Each AgentState() must get its own data dict (no shared default trap)."""
    a = AgentState()
    b = AgentState()
    a.data["x"] = 1
    assert b.data == {}, "default_factory should give each instance its own dict"
