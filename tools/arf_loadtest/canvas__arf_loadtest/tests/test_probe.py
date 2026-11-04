import json

import pytest
from canvas__arf_loadtest.agents.probe import ChatProbeAgent, ProbeAgent
from canvas__arf_loadtest.models import Counter, ProbeRecord

from canvas_sdk.agents import AgentPlugin, RunSubject
from canvas_sdk.test_utils.agents import (
    FakeGateway,
    prepare_agent,
    reply,
    run_agent,
    text,
    tool_use,
)
from canvas_sdk.test_utils.factories import PatientFactory

GRANT = ["@config_reads"]
SCRIPT = {"tools": [["find_note_types", {}]], "latency_ms": 0, "text": "done"}


def _probe(agent_class: type[AgentPlugin] = ProbeAgent, **subject: str) -> AgentPlugin:
    return prepare_agent(agent_class, allowed=GRANT, subject=RunSubject(**subject))


def _gateway() -> FakeGateway:
    return FakeGateway(reply(tool_use("find_note_types", {})), reply(text("done")))


@pytest.mark.django_db
def test_probe_runs_the_script_and_counts_the_run() -> None:
    """Each run on a key reads the count before it and leaves it one higher."""
    for seq in range(3):
        run_agent(
            _probe(),
            _gateway(),
            {"scenario": "s4", "seq": seq, "script": SCRIPT},
            scope_key="key:loadtest:s4:shared",
        )

    assert Counter.objects.get(key="key:loadtest:s4:shared").value == 3
    records = ProbeRecord.objects.filter(scenario="s4").order_by("seq")
    assert [(r.seq, r.saw, r.kind) for r in records] == [
        (0, 0, "probe"),
        (1, 1, "probe"),
        (2, 2, "probe"),
    ]
    assert all(r.started_at <= r.finished_at for r in records)


@pytest.mark.django_db
def test_probe_hands_the_gateway_its_script() -> None:
    """The fake gateway reads the run's script from the system prompt."""
    gateway = _gateway()
    agent = _probe()

    run = run_agent(agent, gateway, {"scenario": "s1", "seq": 0, "script": SCRIPT}, scope_key="k")

    system = gateway.requests[0]["system"]
    system_text = system if isinstance(system, str) else system[0]["text"]
    assert f"LOADTEST_SCRIPT={json.dumps(SCRIPT)}" in system_text
    assert [call.name for call in run.tool_calls] == ["find_note_types"]
    assert ProbeRecord.objects.get().run_id == agent.run_id


@pytest.mark.django_db
def test_probe_has_only_the_config_reads() -> None:
    """The probes read configuration, never a chart."""
    assert {d["name"] for d in _probe().tools.definitions()} == {
        "find_clinical_codes",
        "find_lab_partner_tests",
        "find_lab_partners",
        "find_note_types",
        "find_practice_locations",
    }


@pytest.mark.django_db
def test_chat_turn_records_the_turn_before_it() -> None:
    """A conversation's counter holds its last turn, which the next turn records as saw."""
    patient = PatientFactory.create()
    for seq in (1, 2, 3):
        run_agent(
            _probe(ChatProbeAgent, patient_id=patient.id),
            _gateway(),
            {"scenario": "s3", "seq": seq, "script": SCRIPT},
            scope_key="chat",
        )

    records = ProbeRecord.objects.filter(scenario="s3").order_by("seq")
    assert [(r.seq, r.saw, r.kind) for r in records] == [
        (1, 0, "chat"),
        (2, 1, "chat"),
        (3, 2, "chat"),
    ]
    assert Counter.objects.get(key="chat").value == 3
