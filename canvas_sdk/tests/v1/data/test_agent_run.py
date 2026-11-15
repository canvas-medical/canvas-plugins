from datetime import UTC, datetime
from uuid import uuid4

import pytest

from canvas_sdk.test_utils.factories import PatientFactory
from canvas_sdk.v1.data import AgentRun, AgentRunStatus, AgentRunSubject, AgentRunToolCall


def _run(**fields: object) -> AgentRun:
    defaults: dict[str, object] = {
        "id": uuid4(),
        "plugin_name": "my_plugin",
        "agent_id": "my_plugin.agents.chat:ChatAgent",
        "handler_name": "my_plugin.handlers.chat:ChatAPI",
        "scope": "patient",
        "scope_key": "patient:p1",
        "status": AgentRunStatus.SUCCEEDED,
        "error_kind": "",
        "error": "",
        "queued_at": datetime(2026, 10, 29, tzinfo=UTC),
        "attempts": 0,
        "stop_reason": "end_turn",
        "capabilities": [],
    }
    return AgentRun.objects.create(**{**defaults, **fields})


@pytest.mark.django_db
def test_a_patients_runs_and_a_runs_tool_calls_are_reachable() -> None:
    """Plugins find runs by patient and read each run's tool calls."""
    patient = PatientFactory.create()
    run = _run(patient=patient)
    AgentRunToolCall.objects.create(
        run=run, seq=0, name="find_vitals", ok=True, error_type="", duration_ms=12
    )

    assert list(patient.agent_runs.all()) == [run]
    assert [call.name for call in run.tool_calls.all()] == ["find_vitals"]


@pytest.mark.django_db
def test_a_run_is_found_by_the_run_id_its_effect_carried() -> None:
    """The id a RunAgentEffect generated is the record's id."""
    run_id = uuid4()
    _run(id=run_id, status=AgentRunStatus.GAVE_UP)

    assert AgentRun.objects.get(id=run_id).status == "gave_up"


@pytest.mark.django_db
def test_a_runs_subject_and_capabilities_are_readable() -> None:
    """Plugins find runs about a claim, and see what each run was allowed to do."""
    run = _run(scope="claim", scope_key="claim:c1", capabilities=["revenue"])
    AgentRunSubject.objects.create(run=run, kind="claim", ref_id="c1")

    found = AgentRun.objects.get(subjects__kind="claim", subjects__ref_id="c1")

    assert found == run
    assert found.capabilities == ["revenue"]
