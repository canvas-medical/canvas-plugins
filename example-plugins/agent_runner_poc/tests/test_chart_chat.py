import pytest
import pytest_canvas.plugin
from agent_runner_poc.agents.chart_chat import ChartChatAgent, chart_chat_scope_key

from canvas_sdk.test_utils.factories import PatientFactory, StaffFactory


def test_scope_key_names_the_patient_and_the_clinician() -> None:
    """Runs serialize per clinician's conversation, not per chart."""
    assert chart_chat_scope_key("p1", "s1") == "agent_runner_poc:chart_chat:patient:p1:staff:s1"


@pytest.mark.django_db
def test_each_clinician_has_their_own_conversation() -> None:
    """One clinician's chat never becomes another's context."""
    patient = PatientFactory.create()
    first = StaffFactory.create()
    second = StaffFactory.create()
    agent = ChartChatAgent()
    first_key = chart_chat_scope_key(patient.id, first.id)

    state = agent.load_state(first_key)
    state.data["messages"] = [{"role": "user", "content": "How is her A1c trending?"}]
    agent.save_state(first_key, state)

    assert agent.load_state(chart_chat_scope_key(patient.id, second.id)).data["messages"] == []
    assert agent.load_state(first_key).data["messages"] == [
        {"role": "user", "content": "How is her A1c trending?"}
    ]


def test_pytest_canvas_still_lacks_the_custom_data_fixture() -> None:
    """Tripwire for tests/conftest.py, which stands in for a pytest-canvas fixture."""
    assert not hasattr(pytest_canvas.plugin, "create_plugin_custom_model_tables"), (
        "pytest-canvas now creates plugin Custom Data tables itself; delete the "
        "custom_data_tables fixture in example-plugins/agent_runner_poc/tests/conftest.py"
    )
