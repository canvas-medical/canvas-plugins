"""Test helpers for agent plugins: a fake inference gateway and a platform-like run.

Build model replies with :func:`text`, :func:`tool_use`, and :func:`reply`, queue them on
a :class:`FakeGateway`, and run an agent with :func:`run_agent`, which applies the
manifest tool grant, sets the run's subject, and drops ungranted effects the way the
plugin-runner does::

    gateway = FakeGateway(
        reply(tool_use("find_conditions")),
        reply(text("No new follow-up needed.")),
    )
    agent = prepare_agent(
        MyAgent, allowed=["@clinical_reads"], subject=RunSubject(patient_id=patient.id)
    )

    run = run_agent(agent, gateway)

    assert run.effects == []
    assert [call.name for call in run.tool_calls] == ["find_conditions"]
"""

import copy
from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4

from anthropic.types import TextBlock, ToolUseBlock

from canvas_sdk.agents.base import AgentPlugin
from canvas_sdk.agents.grant import apply_tool_grant, split_granted_effects
from canvas_sdk.agents.result import AgentRunResult
from canvas_sdk.agents.run_record import RunRecorder, ToolCallRecord, current_recorder
from canvas_sdk.agents.subject import RunSubject
from canvas_sdk.effects import Effect


def text(value: str) -> TextBlock:
    """A text block of a model reply."""
    return TextBlock(text=value, type="text")


def tool_use(name: str, input: dict[str, Any] | None = None, *, id: str = "") -> ToolUseBlock:
    """A tool call block of a model reply; ``id`` defaults to a fresh one."""
    return ToolUseBlock(
        id=id or f"toolu_{uuid4().hex[:12]}", name=name, input=input or {}, type="tool_use"
    )


@dataclass
class ModelReply:
    """What the fake gateway answers one model call with."""

    stop_reason: str
    content: list[TextBlock | ToolUseBlock]


def reply(*blocks: TextBlock | ToolUseBlock, stop_reason: str = "") -> ModelReply:
    """A model reply; its stop reason is ``tool_use`` when it calls a tool, else ``end_turn``."""
    if not stop_reason:
        calls_a_tool = any(isinstance(block, ToolUseBlock) for block in blocks)
        stop_reason = "tool_use" if calls_a_tool else "end_turn"
    return ModelReply(stop_reason=stop_reason, content=list(blocks))


class FakeGateway:
    """An :class:`LLMGateway` stand-in that answers model calls from a queue.

    Each call to ``client().messages.create`` takes the next reply, or raises it when it
    is an exception, such as an ``anthropic.APIConnectionError`` for an outage. A copy of
    each request's arguments is kept on :attr:`requests`.
    """

    model = "claude-test"

    def __init__(self, *replies: ModelReply | Exception) -> None:
        self._replies = list(replies)
        self.requests: list[dict[str, Any]] = []
        self.messages = self

    def client(self, **kwargs: Any) -> "FakeGateway":
        """The fake client; it is the gateway itself."""
        return self

    def create(self, **kwargs: Any) -> ModelReply:
        """Answer one model call with the next queued reply."""
        self.requests.append(copy.deepcopy(kwargs))
        if not self._replies:
            raise AssertionError(
                f"FakeGateway has no reply queued for model call {len(self.requests)}"
            )
        answer = self._replies.pop(0)
        if isinstance(answer, Exception):
            raise answer
        return answer


def prepare_agent(
    agent_class: type[AgentPlugin],
    *,
    allowed: Iterable[str] = (),
    denied: Iterable[str] = (),
    subject: RunSubject | None = None,
    run_id: str = "",
) -> AgentPlugin:
    """An agent set up the way the platform sets one up before a run.

    ``allowed`` and ``denied`` are the manifest's ``tools`` grant: tool names and
    ``@category`` references. ``run_id`` defaults to a fresh one.
    """
    agent = agent_class()
    apply_tool_grant(agent, {"allowed": list(allowed), "denied": list(denied)})
    agent.subject = subject or RunSubject()
    agent.run_id = run_id or str(uuid4())
    return agent


@dataclass
class AgentTestRun:
    """What one :func:`run_agent` call did.

    Attributes:
        result: What ``run()`` returned.
        effects: The returned effects the platform would apply.
        dropped: The returned effects the tool grant drops.
        model_calls: Model calls the run's tool loops made, sub-agents included.
        tool_calls: The tool calls those loops dispatched, in order.
        stop_reason: How the run's last tool loop ended.
    """

    result: AgentRunResult
    effects: list[Effect] = field(default_factory=list)
    dropped: list[Effect] = field(default_factory=list)
    model_calls: int = 0
    tool_calls: list[ToolCallRecord] = field(default_factory=list)
    stop_reason: str = ""


def run_agent(
    agent: AgentPlugin,
    gateway: Any,
    trigger_payload: dict[str, Any] | None = None,
    *,
    scope_key: str = "test",
) -> AgentTestRun:
    """Run a prepared agent through its lifecycle as the plugin-runner does.

    Calls ``on_run_start``, ``load_state``, ``run``, ``save_state``, and ``on_run_end``,
    or ``on_run_error`` when one raises, and records the run like the platform, holding
    it to the agent's ``max_model_calls``. Unlike
    the platform, an exception from the run or a hook propagates, so a test sees it.
    """
    granted_effect_types = agent.tools.effect_types() if agent.tools else frozenset()
    recorder = RunRecorder(max_model_calls=agent.max_model_calls)
    token = current_recorder.set(recorder)
    try:
        agent.on_run_start(scope_key)
        try:
            state = agent.load_state(scope_key)
            result = agent.run(state, gateway, trigger_payload or {})
            agent.save_state(scope_key, result.state)
        except Exception as exc:
            agent.on_run_error(exc)
            raise
        agent.on_run_end(result)
    finally:
        current_recorder.reset(token)
    kept, dropped = split_granted_effects(result.effects, granted_effect_types)
    return AgentTestRun(
        result=result,
        effects=kept,
        dropped=dropped,
        model_calls=recorder.model_calls,
        tool_calls=list(recorder.tool_calls),
        stop_reason=recorder.stop_reason,
    )


__exports__ = (
    "AgentTestRun",
    "FakeGateway",
    "ModelReply",
    "prepare_agent",
    "reply",
    "run_agent",
    "text",
    "tool_use",
)
