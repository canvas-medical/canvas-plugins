"""The chat's note when the previous run's changes did not all reach Canvas."""

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

import pytest
from canvas__agent_runner_poc.agents.chart_chat import ChartChatAgent
from canvas__agent_runner_poc.agents.claims_chat import ClaimsChatAgent
from canvas__agent_runner_poc.agents.decisions import (
    UNAPPLIED_START,
    is_decisions_note,
    record_unapplied,
)

from canvas_sdk.agents import AgentPlugin, Capability, RunRequester, RunSubject
from canvas_sdk.test_utils.agents import FakeGateway, prepare_agent, reply, run_agent, text
from canvas_sdk.test_utils.factories import PatientFactory, StaffFactory
from canvas_sdk.v1.data import AgentRun, AgentRunStatus

AGENT_ID = "canvas__agent_runner_poc.agents.chart_chat:ChartChatAgent"
SCOPE = "patient_and_staff:p1:s1"
HISTORY = [{"role": "user", "content": "add a plan"}, {"role": "assistant", "content": "Done."}]


def _previous(status: str = AgentRunStatus.FAILED, **counts: Any) -> AgentRun:
    return AgentRun.objects.create(
        id=uuid4(),
        plugin_name="canvas__agent_runner_poc",
        agent_id=counts.pop("agent_id", AGENT_ID),
        handler_name="h",
        scope="patient_and_staff",
        scope_key=counts.pop("scope_key", SCOPE),
        status=status,
        error_kind="",
        error=counts.pop("error", ""),
        queued_at=datetime(2026, 11, 9, tzinfo=UTC),
        finished_at=datetime(2026, 11, 9, 0, 1, tzinfo=UTC),
        attempts=0,
        stop_reason="",
        capabilities=[],
        **counts,
    )


def _agent() -> AgentPlugin:
    return prepare_agent(ChartChatAgent)


@pytest.mark.django_db
def test_a_run_whose_changes_did_not_apply_is_noted_for_the_model() -> None:
    """The saved conversation says the plan was added; the next turn hears it was not."""
    run = _previous(
        effects_returned=3, effects_dropped=1, effects_applied=0, error="Permission denied"
    )

    messages = record_unapplied(HISTORY, _agent(), SCOPE, "clinician")

    (note,) = messages[len(HISTORY) :]
    assert is_decisions_note(note)
    text = note["content"][0]["text"]
    assert str(run.id) in text
    assert "2 of the 2 changes" in text
    assert "Permission denied" in text


@pytest.mark.django_db
@pytest.mark.parametrize(
    "counts",
    [
        {"effects_returned": 2, "effects_dropped": 0, "effects_applied": 2},
        {"effects_returned": 2, "effects_dropped": 2, "effects_applied": 0},
        # The plugin never returned, so it saved no state claiming anything.
        {"effects_returned": None, "effects_applied": 0},
        # Another conversation's run.
        {"effects_returned": 1, "effects_applied": 0, "scope_key": "patient_and_staff:p2:s1"},
    ],
)
def test_no_note_when_every_kept_change_applied_or_none_was_claimed(counts: dict) -> None:
    """A run that kept its word, or returned nothing, needs no correction."""
    _previous(**counts)

    assert record_unapplied(HISTORY, _agent(), SCOPE, "clinician") == HISTORY


@pytest.mark.django_db
def test_the_note_is_added_once() -> None:
    """The next turn's conversation already holds it."""
    _previous(effects_returned=1, effects_applied=0)
    once = record_unapplied(HISTORY, _agent(), SCOPE, "clinician")

    assert record_unapplied(once, _agent(), SCOPE, "clinician") == once


@pytest.mark.django_db
def test_the_run_itself_is_not_its_own_previous_run() -> None:
    """The current run's record is still running; only earlier runs count."""
    run = _previous(effects_returned=1, effects_applied=0)
    agent = prepare_agent(ChartChatAgent, run_id=str(run.id))

    assert record_unapplied(HISTORY, agent, SCOPE, "clinician") == HISTORY


@pytest.mark.django_db
@pytest.mark.parametrize("agent_class", [ChartChatAgent, ClaimsChatAgent])
def test_each_chat_tells_the_model_before_the_next_message(agent_class: type[AgentPlugin]) -> None:
    """The model reads the note ahead of the person's new message."""
    staff = StaffFactory.create()
    patient = PatientFactory.create()
    _previous(
        effects_returned=1,
        effects_applied=0,
        agent_id=f"{agent_class.__module__}:{agent_class.__name__}",
    )
    agent = prepare_agent(
        agent_class,
        subject=RunSubject(patient_id=patient.id),
        requester=RunRequester(staff_id=staff.id),
        capabilities=(Capability.REVENUE,),
    )
    gateway = FakeGateway(reply(text("Sorry, that did not go through.")))

    run_agent(agent, gateway, {"user_message": "Did it work?"}, scope_key=SCOPE)

    *_, note, question = gateway.requests[0]["messages"]
    assert note["content"][0]["text"].startswith(UNAPPLIED_START)
    assert question["content"] == "Did it work?"
