from types import SimpleNamespace

import pytest
import pytest_canvas.plugin
from agent_runner_poc.agents.chart_chat import ChartChatAgent
from anthropic.types import TextBlock, ToolUseBlock

from canvas_sdk.agents import RunSubject
from canvas_sdk.test_utils.factories import PatientFactory, StaffFactory


def _agent_for(patient_id: str, staff_id: str) -> ChartChatAgent:
    """A chat agent for one clinician's run on one patient, as the platform sets it up."""
    agent = ChartChatAgent()
    agent.subject = RunSubject(patient_id=patient_id, staff_id=staff_id)
    return agent


@pytest.mark.django_db
def test_each_clinician_has_their_own_conversation() -> None:
    """One clinician's chat never becomes another's context."""
    patient = PatientFactory.create()
    first = _agent_for(patient.id, StaffFactory.create().id)
    second = _agent_for(patient.id, StaffFactory.create().id)

    state = first.load_state("patient_and_staff")
    state.data["messages"] = [{"role": "user", "content": "How is her A1c trending?"}]
    first.save_state("patient_and_staff", state)

    assert second.load_state("patient_and_staff").data["messages"] == []
    assert first.load_state("patient_and_staff").data["messages"] == [
        {"role": "user", "content": "How is her A1c trending?"}
    ]


def test_pytest_canvas_still_lacks_the_custom_data_fixture() -> None:
    """Tripwire for tests/conftest.py, which stands in for a pytest-canvas fixture."""
    assert not hasattr(pytest_canvas.plugin, "create_plugin_custom_model_tables"), (
        "pytest-canvas now creates plugin Custom Data tables itself; delete the "
        "custom_data_tables fixture in example-plugins/agent_runner_poc/tests/conftest.py"
    )


class _FakeClient:
    """Returns queued responses in order."""

    def __init__(self, *responses: SimpleNamespace) -> None:
        self._responses = list(responses)
        self.messages = self

    def create(self, **kwargs: object) -> SimpleNamespace:
        return self._responses.pop(0)


class _FakeGateway:
    model = "claude-test"

    def __init__(self, client: _FakeClient) -> None:
        self._client = client

    def client(self) -> _FakeClient:
        return self._client


@pytest.mark.django_db
def test_run_answers_through_the_tool_loop_and_keeps_the_transcript() -> None:
    """The agent stores the clinician's turn, the tool exchange, and the answer."""
    agent = _agent_for(PatientFactory.create().id, StaffFactory.create().id)
    agent.tools = ChartChatAgent.tools.scope({"get_patient_demographics"})
    gateway = _FakeGateway(
        _FakeClient(
            SimpleNamespace(
                stop_reason="tool_use",
                content=[
                    ToolUseBlock(
                        id="t1", name="get_patient_demographics", input={}, type="tool_use"
                    )
                ],
            ),
            SimpleNamespace(
                stop_reason="end_turn", content=[TextBlock(text="She is 54.", type="text")]
            ),
        )
    )
    state = agent.load_state("patient_and_staff")

    result = agent.run(state, gateway, {"user_message": "How old is she?"})

    roles = [message["role"] for message in result.state.data["messages"]]
    assert roles == ["user", "assistant", "user", "assistant"]
    assert result.state.data["messages"][0] == {"role": "user", "content": "How old is she?"}
    assert result.state.data["messages"][-1]["content"][0]["text"] == "She is 54."
