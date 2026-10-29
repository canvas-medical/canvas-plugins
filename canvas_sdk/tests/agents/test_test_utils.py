import json
from typing import Any

import pytest

from canvas_sdk.agents import AgentPlugin, AgentRunResult, AgentState, RunSubject, ToolRegistry
from canvas_sdk.effects import Effect, EffectType
from canvas_sdk.test_utils.agents import (
    FakeGateway,
    prepare_agent,
    reply,
    run_agent,
    text,
    tool_use,
)

tools = ToolRegistry()


@tools.tool(
    name="log_patient",
    description="x",
    input_schema={"type": "object"},
    effect_types=("LOG",),
    categories=("demo",),
)
def _log_patient(arguments: dict[str, Any], *, ctx: dict[str, Any]) -> dict[str, Any]:
    ctx["effects"].append(Effect(type=EffectType.LOG, payload=json.dumps(ctx["patient_id"])))
    return {"ok": True}


@tools.tool(name="broken", description="x", input_schema={"type": "object"})
def _broken(arguments: dict[str, Any], *, ctx: dict[str, Any]) -> None:
    raise ValueError("no such record")


class _Agent(AgentPlugin):
    tools = tools
    hooks: list[str]

    def __init__(self) -> None:
        self.hooks = []

    def load_state(self, scope_key: str) -> AgentState:
        return AgentState()

    def run(self, state: AgentState, gateway: Any, trigger_payload: dict) -> AgentRunResult:
        result = self.run_tool_loop(
            gateway, system="s", messages=[{"role": "user", "content": "go"}]
        )
        # An effect no granted tool stages, which the platform drops.
        banner = Effect(type=EffectType.ADD_BANNER_ALERT, payload="{}")
        return AgentRunResult(state=state, effects=[*result.effects, banner])

    def save_state(self, scope_key: str, state: AgentState) -> None:
        return None

    def on_run_start(self, scope_key: str) -> None:
        self.hooks.append("start")

    def on_run_end(self, result: AgentRunResult) -> None:
        self.hooks.append("end")

    def on_run_error(self, exc: BaseException) -> None:
        self.hooks.append("error")


def test_a_reply_that_calls_a_tool_stops_for_it() -> None:
    """The stop reason follows the content unless a test says otherwise."""
    assert reply(tool_use("x")).stop_reason == "tool_use"
    assert reply(text("done")).stop_reason == "end_turn"
    assert reply(text("cut"), stop_reason="max_tokens").stop_reason == "max_tokens"


def test_the_fake_gateway_answers_in_order_and_keeps_each_request() -> None:
    """A test asserts on what the agent sent the model."""
    gateway = FakeGateway(reply(text("one")), reply(text("two")))
    client = gateway.client()

    first = client.messages.create(model="m", messages=[{"role": "user", "content": "a"}])
    second = client.messages.create(model="m", messages=[])

    assert [first.content, second.content] == [[text("one")], [text("two")]]
    assert gateway.requests[0]["messages"] == [{"role": "user", "content": "a"}]


def test_the_fake_gateway_raises_a_queued_exception() -> None:
    """An outage or refusal is queued like a reply."""
    gateway = FakeGateway(RuntimeError("outage"))

    with pytest.raises(RuntimeError, match="outage"):
        gateway.client().messages.create()


def test_the_fake_gateway_says_when_the_agent_called_more_than_queued() -> None:
    """A missing reply is a failed expectation, not a hang."""
    with pytest.raises(AssertionError, match="no reply queued for model call 1"):
        FakeGateway().client().messages.create()


def test_a_prepared_agent_has_its_grant_subject_and_run_id() -> None:
    """The same setup the plugin-runner does before load_state."""
    agent = prepare_agent(_Agent, allowed=["@demo"], subject=RunSubject(patient_id="p1"))

    assert agent.tools is not None
    assert [d["name"] for d in agent.tools.definitions()] == ["log_patient"]
    assert agent.tools_allowed == frozenset({"log_patient"})
    assert agent.subject.patient_id == "p1"
    assert agent.run_id


def test_a_run_reports_the_platform_view_of_what_it_did() -> None:
    """Kept and dropped effects, model calls, and tool calls, as the run record has them."""
    agent = prepare_agent(
        _Agent, allowed=["log_patient", "broken"], subject=RunSubject(patient_id="p1")
    )
    gateway = FakeGateway(
        reply(tool_use("log_patient"), tool_use("broken")),
        reply(text("done")),
    )

    run = run_agent(agent, gateway)

    assert [json.loads(effect.payload) for effect in run.effects] == ["p1"]
    assert [effect.type for effect in run.dropped] == [EffectType.ADD_BANNER_ALERT]
    assert run.model_calls == 2
    assert [(call.name, call.ok, call.error_type) for call in run.tool_calls] == [
        ("log_patient", True, ""),
        ("broken", False, "ValueError"),
    ]
    assert run.stop_reason == "end_turn"
    assert agent.hooks == ["start", "end"]  # type: ignore[attr-defined]


def test_an_error_in_the_run_reaches_the_test() -> None:
    """The platform would swallow it into success=False; a test needs to see it."""
    agent = prepare_agent(_Agent, allowed=["@demo"])

    with pytest.raises(AssertionError, match="no reply queued"):
        run_agent(agent, FakeGateway())

    assert agent.hooks == ["start", "error"]  # type: ignore[attr-defined]
