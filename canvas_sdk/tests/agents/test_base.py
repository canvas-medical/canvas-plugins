import pytest

from canvas_sdk.agents import (
    AgentPlugin,
    AgentRunResult,
    AgentState,
    Capability,
    LLMGateway,
    RunRequester,
    RunSubject,
    ToolRegistry,
)
from canvas_sdk.test_utils.factories import NoteFactory, PatientFactory, StaffFactory
from canvas_sdk.v1.data.note import CurrentNoteStateEvent, Note, NoteStates


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
    gateway = LLMGateway(base_url="https://gateway.test", api_key="cnvs_sk_test")
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


_GATEWAY = LLMGateway(base_url="https://gateway.test", api_key="cnvs_sk_test")


def test_tool_context_carries_the_run_subject() -> None:
    """Tools get the platform's patient, note, and requester, plus the run's plumbing."""
    agent = _MinimalAgent()
    agent.tools = ToolRegistry()
    agent.subject = RunSubject(patient_id="p1", note_id="n1")
    agent.requester = RunRequester(staff_id="s1", permissions=frozenset({"api.change_task"}))

    ctx = agent.tool_context(_GATEWAY, {"focus": "labs"})

    assert ctx == {
        "focus": "labs",
        "patient_id": "p1",
        "staff_id": "s1",
        "note_id": "n1",
        "claim_id": None,
        "permissions": frozenset({"api.change_task"}),
        "capabilities": frozenset(),
        "effects": [],
        "gateway": _GATEWAY,
        "parent_tools": agent.tools,
    }


def test_tool_context_carries_the_claim_and_capabilities() -> None:
    """Claims tools get the run's claim and the capabilities the platform granted."""
    agent = _MinimalAgent()
    agent.subject = RunSubject(claim_id="c1")
    agent.capabilities = frozenset({Capability.REVENUE})

    ctx = agent.tool_context(_GATEWAY)

    assert ctx["claim_id"] == "c1"
    assert ctx["capabilities"] == frozenset({Capability.REVENUE})


@pytest.mark.parametrize(
    "key",
    [
        "patient_id",
        "staff_id",
        "note_id",
        "claim_id",
        "permissions",
        "capabilities",
        "effects",
        "gateway",
    ],
)
def test_tool_context_refuses_to_replace_what_the_run_sets(key: str) -> None:
    """An agent cannot point its tools at another patient or claim, or grant itself access."""
    agent = _MinimalAgent()
    agent.subject = RunSubject(patient_id="p1")

    with pytest.raises(ValueError, match=key):
        agent.tool_context(_GATEWAY, {key: "other"})


def test_tool_context_without_a_subject_has_no_patient() -> None:
    """A run with no subject, such as a scheduled one, gives tools no patient."""
    ctx = _MinimalAgent().tool_context(_GATEWAY)

    assert ctx["patient_id"] is None
    assert ctx["staff_id"] is None
    assert ctx["note_id"] is None


def _open_note(**kwargs: object) -> Note:
    note = NoteFactory.create(**kwargs)
    CurrentNoteStateEvent.objects.create(note=note, state=NoteStates.NEW)
    return note


@pytest.mark.django_db
def test_tool_context_uses_the_requesting_staffs_open_note() -> None:
    """With no note on the subject, drafts go to the requester's open note on the patient."""
    patient = PatientFactory.create()
    clinician = StaffFactory.create()
    own_note = _open_note(patient=patient, provider=clinician)
    _open_note(patient=patient)
    agent = _MinimalAgent()
    agent.subject = RunSubject(patient_id=patient.id)
    agent.requester = RunRequester(staff_id=clinician.id)

    assert agent.tool_context(_GATEWAY)["note_id"] == str(own_note.id)


@pytest.mark.django_db
def test_tool_context_without_a_requester_picks_no_open_note() -> None:
    """A run nobody started has no clinician, so drafts never land on someone's note."""
    patient = PatientFactory.create()
    _open_note(patient=patient)
    agent = _MinimalAgent()
    agent.subject = RunSubject(patient_id=patient.id)

    assert agent.tool_context(_GATEWAY)["note_id"] is None
