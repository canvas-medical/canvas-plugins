import json
from pathlib import Path

import pytest
from canvas__adk_loadtest.agents.probe import ChatProbeAgent, ExtendedProbeAgent, ProbeAgent
from canvas__adk_loadtest.models import Counter, ProbeRecord

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

MANIFEST = Path(__file__).parents[1] / "canvas__adk_loadtest" / "CANVAS_MANIFEST.json"
GRANT = ["@config_reads"]
CHART_READS = [
    "@clinical_reads",
    "@task_reads",
    "@message_reads",
    "@document_reads",
    "@claims_reads",
    "@intake_reads",
]
SCRIPT = {"tools": [["find_note_types", {}]], "latency_ms": 0, "text": "done"}


def _probe(agent_class: type[AgentPlugin] = ProbeAgent, **subject: str) -> AgentPlugin:
    return prepare_agent(agent_class, allowed=GRANT, subject=RunSubject(**subject))


def _granted(agent_class: type[AgentPlugin]) -> AgentPlugin:
    """The probe with the grant the manifest gives it."""
    (entry,) = (
        agent
        for agent in json.loads(MANIFEST.read_text())["components"]["agents"]
        if agent["class"].endswith(f":{agent_class.__name__}")
    )
    return prepare_agent(agent_class, allowed=entry["tools"]["allowed"])


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
@pytest.mark.parametrize("agent_class", [ProbeAgent, ExtendedProbeAgent, ChatProbeAgent])
def test_probe_reads_configuration_never_a_chart(agent_class: type[AgentPlugin]) -> None:
    """The manifest grants each probe configuration reads and no tool that reads a chart."""
    agent = _granted(agent_class)
    assert agent.tools is not None and agent_class.tools is not None
    names = {d["name"] for d in agent.tools.definitions()}

    assert "find_note_types" in names
    assert sorted(names & agent_class.tools.resolve_allowed(CHART_READS)) == []


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
