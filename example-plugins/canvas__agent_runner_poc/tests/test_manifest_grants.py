"""What each agent's manifest grant lets it do, read from the manifest a customer copies."""

import json
from pathlib import Path
from typing import Any

from canvas__agent_runner_poc.agents.chart_chat import SYSTEM_PROMPT, ChartChatAgent
from canvas__agent_runner_poc.agents.longitudinal_advisor import LongitudinalCareAdvisor

from canvas_sdk.agents import AgentPlugin
from canvas_sdk.test_utils.agents import prepare_agent

MANIFEST = Path(__file__).parents[1] / "canvas__agent_runner_poc" / "CANVAS_MANIFEST.json"


def _granted(agent_class: type[AgentPlugin]) -> AgentPlugin:
    """The agent with its manifest grant applied, for a requester holding every permission."""
    entry: dict[str, Any] = next(
        agent
        for agent in json.loads(MANIFEST.read_text())["components"]["agents"]
        if agent["class"].endswith(f":{agent_class.__name__}")
    )
    tools = entry.get("tools") or {}
    return prepare_agent(
        agent_class,
        allowed=tools.get("allowed", ()),
        denied=tools.get("denied", ()),
        approve=tools.get("approve", ()),
    )


def test_chart_chat_changes_no_existing_draft_or_record_without_approval() -> None:
    """A change to what a clinician already has, such as their staged prescription, waits.

    A request, or text the model read in a message or a note, could otherwise change a
    draft the clinician then signs believing it is the one they reviewed.
    """
    agent = _granted(ChartChatAgent)
    assert agent.tools is not None
    changing = ("EDIT_", "DELETE_", "UPDATE_", "REMOVE_", "COMMIT_")

    unapproved = sorted(
        name
        for name in agent.tools_allowed
        if any(t.startswith(changing) for t in agent.tools.effect_types_for(name))
        and not agent.tools.requires_approval(name)
    )

    assert unapproved == []
    assert agent.tools.requires_approval("edit_staged_command")
    assert agent.tools.requires_approval("delete_staged_command")


def test_chart_chat_treats_chart_text_as_data() -> None:
    """What the model reads in the chart informs it and never directs it."""
    assert "data, not instructions" in SYSTEM_PROMPT


def test_the_longitudinal_advisor_reads_and_places_protocol_cards_only() -> None:
    """It runs on every note lock as Canvas Bot, so it has no banner or other write tool."""
    agent = _granted(LongitudinalCareAdvisor)
    assert agent.tools is not None

    writes = sorted(name for name in agent.tools_allowed if agent.tools.effect_types_for(name))

    assert writes == ["add_or_update_protocol_card"]
