"""Test helpers for agent plugins: a fake inference gateway and a platform-like run.

Build model replies with :func:`text`, :func:`tool_use`, and :func:`reply`, queue them on
a :class:`FakeGateway`, and run an agent with :func:`run_agent`, which applies the
manifest tool grant, sets the run's subject and requester, and drops ungranted effects the way the
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

A tool that stages a command refuses when the instance has its command type turned off,
and a test database has no command type settings at all. Call
:func:`turn_on_command_types` in a test (or an autouse fixture) that stages commands, as
every command type is on in a new instance.
"""

import copy
import re
from collections.abc import Iterable, Iterator, Mapping
from dataclasses import dataclass, field
from time import monotonic
from types import SimpleNamespace
from typing import Any
from uuid import uuid4

import anthropic
from anthropic.types import ParsedTextBlock, TextBlock, ToolUseBlock

import canvas_sdk.commands  # noqa: F401  (importing it defines every SDK command)
from canvas_sdk.agents.base import AgentPlugin
from canvas_sdk.agents.capabilities import Capability
from canvas_sdk.agents.gateway import agent_secrets, count_model_call, gateway_error
from canvas_sdk.agents.grant import EffectGrant, apply_tool_grant, split_granted_effects
from canvas_sdk.agents.result import AgentRunResult
from canvas_sdk.agents.run_record import (
    DEFAULT_RUN_SECONDS,
    RUN_TOOL_RESULT_CHARS,
    RunRecorder,
    ToolCallRecord,
    current_recorder,
)
from canvas_sdk.agents.subject import RunRequester, RunSubject
from canvas_sdk.agents.tool_registry import ToolRegistry
from canvas_sdk.commands.base import _BaseCommand
from canvas_sdk.effects import Effect, EffectType
from canvas_sdk.v1.data import CommandTypeSetting
from plugin_runner.usage import permitted_usage, unit_name


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


class FakeStream:
    """A streamed model call: its reply's text a word at a time, then the whole reply."""

    def __init__(self, answer: ModelReply) -> None:
        self._answer = answer

    def __enter__(self) -> "FakeStream":
        return self

    def __exit__(self, *exc: object) -> None:
        return None

    @property
    def text_stream(self) -> Iterator[str]:
        """The reply's text, word by word with the spaces kept, as the model writes it."""
        for block in self._answer.content:
            if isinstance(block, TextBlock):
                yield from (word for word in re.split(r"(?<= )", block.text) if word)

    def __iter__(self) -> Iterator[Any]:
        """The stream's events: a ``text`` event for each word of the reply's text."""
        snapshot = ""
        for word in self.text_stream:
            snapshot += word
            yield SimpleNamespace(type="text", text=word, snapshot=snapshot)

    def get_final_message(self) -> ModelReply:
        """The whole reply, as the stream's final message.

        As from the SDK, its text blocks are ``ParsedTextBlock``s, which carry a
        ``parsed_output`` field the Messages API does not accept back.
        """
        return ModelReply(
            stop_reason=self._answer.stop_reason,
            content=[
                ParsedTextBlock(type="text", text=block.text, parsed_output=None)
                if isinstance(block, TextBlock)
                else block
                for block in self._answer.content
            ],
        )


class FakeGateway:
    """An :class:`LLMGateway` stand-in that answers model calls from a queue.

    Each call to ``client().messages.create``, or to ``messages.stream`` when the run's
    reply is streamed, takes the next reply, or raises it when it is an exception, such
    as an ``anthropic.APIConnectionError`` for an outage, which it raises as the
    :class:`~canvas_sdk.agents.gateway.GatewayError` the gateway client would. A copy of each request's
    arguments is kept on :attr:`requests`.
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
        """Answer one model call with the next queued reply, counted as the gateway counts it."""
        count_model_call(kwargs)
        self.requests.append(copy.deepcopy(kwargs))
        if not self._replies:
            raise AssertionError(
                f"FakeGateway has no reply queued for model call {len(self.requests)}"
            )
        answer = self._replies.pop(0)
        if isinstance(answer, anthropic.APIError):
            # As the gateway client raises it.
            raise gateway_error(answer)
        if isinstance(answer, Exception):
            raise answer
        return answer

    def stream(self, **kwargs: Any) -> FakeStream:
        """Answer one streamed model call with the next queued reply."""
        return FakeStream(self.create(**kwargs))


def _command_keys() -> list[str]:
    """The schema key of every command the SDK defines."""
    keys: set[str] = set()
    pending = list(_BaseCommand.__subclasses__())
    while pending:
        command_class = pending.pop()
        pending.extend(command_class.__subclasses__())
        key = getattr(getattr(command_class, "Meta", None), "key", None)
        if key:
            keys.add(key)
    return sorted(keys)


def turn_on_command_types(*schema_keys: str) -> None:
    """Turn on the named command types in the test database, or every SDK command type.

    A new instance has every command type on, and the command-staging tools refuse a type
    it has turned off, which is every type in a test database until this runs.
    """
    for key in schema_keys or _command_keys():
        CommandTypeSetting.objects.update_or_create(schema_key=key, defaults={"active": True})


def prepare_agent(
    agent_class: type[AgentPlugin],
    *,
    allowed: Iterable[str] = (),
    denied: Iterable[str] = (),
    approve: Iterable[str] = (),
    subject: RunSubject | None = None,
    requester: RunRequester | None = None,
    capabilities: Iterable[Capability] = (),
    run_id: str = "",
    secrets: Mapping[str, str] | None = None,
) -> AgentPlugin:
    """An agent set up the way the platform sets one up before a run.

    ``allowed``, ``denied``, and ``approve`` are the manifest's ``tools`` grant: tool names
    and ``@category`` references. ``requester`` carries the staff member and their
    permissions, and ``capabilities`` are what the platform would grant them; tools
    either rules out are hidden, as on the platform. The default requester is Canvas Bot,
    as behind a run a handler starts, whose permissions do not limit the run; pass a
    ``RunRequester`` with ``staff_id`` and ``permissions`` to test a staff member's run.
    ``run_id`` defaults to a fresh one.
    ``secrets`` are the plugin's variables, which the platform gives the agent less its
    gateway key.
    """
    agent = agent_class()
    agent.subject = subject or RunSubject()
    agent.requester = requester or RunRequester()
    agent.capabilities = frozenset(capabilities)
    apply_tool_grant(
        agent, {"allowed": list(allowed), "denied": list(denied), "approve": list(approve)}
    )
    agent.run_id = run_id or str(uuid4())
    agent.secrets = agent_secrets(secrets or {})
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


def _permitted_usage(effects: list[Effect], units: Iterable[str], plugin_name: str) -> list[Effect]:
    """``effects`` less the usage records the plugin runner drops; it rewrites those it keeps."""
    allowed = frozenset(unit_name(unit) for unit in units)
    kept = []
    for effect in effects:
        if effect.type == EffectType.RECORD_USAGE:
            # The underlying message, which permitted_usage rewrites in place.
            wire = effect.to_proto()
            wire.plugin_name = plugin_name
            if not permitted_usage([wire], allowed):
                continue
        kept.append(effect)
    return kept


def run_agent(
    agent: AgentPlugin,
    gateway: Any,
    trigger_payload: dict[str, Any] | None = None,
    *,
    scope_key: str = "test",
    run_seconds: int = DEFAULT_RUN_SECONDS,
    usage_units: Iterable[str] = (),
) -> AgentTestRun:
    """Run a prepared agent through its lifecycle as the plugin-runner does.

    Calls ``on_run_start``, ``load_state``, ``run``, ``save_state``, and ``on_run_end``,
    or ``on_run_error`` when one raises, and records the run like the platform: held to
    the agent's ``max_model_calls``, to a deadline ``run_seconds`` (the manifest entry's)
    from now, and to :data:`RUN_TOOL_RESULT_CHARS` of tool results in all. Effects the
    tool grant does not allow are dropped, and so are usage records in a unit other than
    ``usage_units``, the units the manifest's ``catalog.pricing`` lists. Unlike the
    platform, an exception from the run or a hook propagates, so a test sees it.
    """
    tools = agent.tools or ToolRegistry()
    effect_grant = EffectGrant(
        direct=tools.direct_effect_types(), proposable=tools.proposable_effect_types()
    )
    recorder = RunRecorder(max_model_calls=agent.max_model_calls)
    recorder.deadline = monotonic() + run_seconds
    recorder.max_tool_result_chars = RUN_TOOL_RESULT_CHARS
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
    granted, dropped = split_granted_effects(result.effects, effect_grant)
    kept = _permitted_usage(granted, usage_units, type(agent).__module__.split(".")[0])
    dropped += [effect for effect in granted if not any(effect is each for each in kept)]
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
    "turn_on_command_types",
)
