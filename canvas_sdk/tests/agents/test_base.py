import pytest

from canvas_sdk.agents import AgentPlugin, AgentRunResult, AgentState, LLMGateway


class _MinimalAgent(AgentPlugin):
    """Concrete subclass that satisfies the three abstract methods."""

    def load_state(self, scope_key: str) -> AgentState:
        return AgentState()

    def run(
        self,
        state: AgentState,
        gateway: LLMGateway,
        trigger_payload: dict,
    ) -> AgentRunResult:
        return AgentRunResult(state=state)

    def save_state(self, scope_key: str, state: AgentState) -> None:
        return None


def test_agent_plugin_cannot_be_instantiated_directly() -> None:
    """AgentPlugin is abstract; instantiation must fail."""
    with pytest.raises(TypeError, match="abstract"):
        AgentPlugin()  # type: ignore[abstract]


def test_subclass_missing_load_state_cannot_instantiate() -> None:
    """A subclass without load_state must still be abstract."""

    class Incomplete(AgentPlugin):
        def run(self, state, gateway, trigger_payload):  # type: ignore[no-untyped-def]
            return AgentRunResult(state=state)

        def save_state(self, scope_key, state):  # type: ignore[no-untyped-def]
            return None

    with pytest.raises(TypeError, match="load_state"):
        Incomplete()  # type: ignore[abstract]


def test_subclass_missing_run_cannot_instantiate() -> None:
    """A subclass without run must still be abstract."""

    class Incomplete(AgentPlugin):
        def load_state(self, scope_key):  # type: ignore[no-untyped-def]
            return AgentState()

        def save_state(self, scope_key, state):  # type: ignore[no-untyped-def]
            return None

    with pytest.raises(TypeError, match="run"):
        Incomplete()  # type: ignore[abstract]


def test_subclass_missing_save_state_cannot_instantiate() -> None:
    """A subclass without save_state must still be abstract."""

    class Incomplete(AgentPlugin):
        def load_state(self, scope_key):  # type: ignore[no-untyped-def]
            return AgentState()

        def run(self, state, gateway, trigger_payload):  # type: ignore[no-untyped-def]
            return AgentRunResult(state=state)

    with pytest.raises(TypeError, match="save_state"):
        Incomplete()  # type: ignore[abstract]


def test_concrete_subclass_instantiates_and_drives_lifecycle() -> None:
    """A subclass implementing all three methods runs end-to-end."""
    agent = _MinimalAgent()
    state = agent.load_state("scope:1")
    gateway = LLMGateway(api_key="sk-test", model="claude-sonnet-4-6")
    result = agent.run(state, gateway, {"hello": "world"})
    agent.save_state("scope:1", result.state)

    assert isinstance(result, AgentRunResult)
    assert result.state is state
    assert result.effects == []


def test_lifecycle_hooks_default_to_no_op() -> None:
    """on_run_start / on_turn / on_run_end / on_run_error are no-op by default.

    The methods are typed ``-> None``; we just need them to be callable without
    raising. Asserting equality with ``None`` would trip mypy's func-returns-value
    check, so we call them for their side effect (i.e., the absence of one).
    """
    agent = _MinimalAgent()
    agent.on_run_start("scope:1")
    agent.on_turn(0)
    agent.on_run_end(AgentRunResult(state=AgentState()))
    agent.on_run_error(RuntimeError("boom"))
