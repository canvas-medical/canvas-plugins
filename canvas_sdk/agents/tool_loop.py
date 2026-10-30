"""The tool-use loop every agent runs: call the model, dispatch its tool calls, repeat."""

import json
import logging
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Literal, cast

import anthropic
from anthropic.types import TextBlock, ToolUseBlock

from canvas_sdk.agents.gateway import LLMGateway, attempt_timeout
from canvas_sdk.agents.history import DEFAULT_HISTORY_CHARS, window_messages
from canvas_sdk.agents.run_record import RunDeadlineExceeded, ToolCallRecord, current_recorder
from canvas_sdk.agents.tool_registry import ToolRegistry

if TYPE_CHECKING:
    from canvas_sdk.effects import Effect

log = logging.getLogger("plugin_runner_logger")

# Stop reasons that can leave complete tool calls to run: a normal tool turn, or a
# turn cut off by max_tokens after one or more tool calls finished.
_TOOL_STOP_REASONS = frozenset({"tool_use", "max_tokens"})

# The most of one tool result sent to the model. The history window cannot drop the
# current turn's results, so an uncapped result (a whole note, a long list) could push
# the call past the context window.
MAX_TOOL_RESULT_CHARS = 50_000


@dataclass
class ToolLoopResult:
    """What a :func:`run_tool_loop` produced.

    Attributes:
        text: The text of the model's last turn, stripped; empty when it had none.
        messages: The messages passed in followed by every turn of this loop, as
            JSON-safe dicts. A transcript you can store and pass back on the next run.
        turns: How many times the model was called.
        stopped: ``"end_turn"`` when the model finished, ``"max_turns"`` when the turn
            cap stopped it, ``"call_limit"`` when the run's model-call ceiling did, and
            ``"unexpected"`` for any other stop reason.
        stop_reason: The model's stop reason on its last turn.
        effects: The ``effects`` list from ``ctx``, holding what the tools staged.
    """

    text: str = ""
    messages: list[dict[str, Any]] = field(default_factory=list)
    effects: list["Effect"] = field(default_factory=list)
    turns: int = 0
    stopped: Literal["end_turn", "max_turns", "call_limit", "unexpected"] = "max_turns"
    stop_reason: str | None = None


def _tool_result(tool_use_id: str, content: str, *, is_error: bool = False) -> dict[str, Any]:
    result: dict[str, Any] = {"type": "tool_result", "tool_use_id": tool_use_id, "content": content}
    if is_error:
        result["is_error"] = True
    return result


def _run_tool(tools: ToolRegistry, block: ToolUseBlock, ctx: dict[str, Any]) -> dict[str, Any]:
    """Run one tool call; a failure goes back to the model as an error so it can recover.

    A gateway error or the run's deadline, raised by a sub-agent the tool ran, ends
    the run instead.
    """
    recorder = current_recorder.get()
    started = time.perf_counter()
    try:
        result = tools.execute(block.name, dict(block.input), ctx=ctx)
    except (anthropic.APIError, RunDeadlineExceeded):
        if recorder is not None:
            recorder.record_tool_call(
                ToolCallRecord(block.name, False, "aborted", _elapsed_ms(started))
            )
        raise
    except Exception as exc:
        log.warning(f"Tool {block.name!r} failed: {type(exc).__name__}")
        if recorder is not None:
            recorder.record_tool_call(
                ToolCallRecord(block.name, False, type(exc).__name__, _elapsed_ms(started))
            )
        return _tool_result(block.id, f"Tool execution failed: {exc!s}", is_error=True)
    if recorder is not None:
        recorder.record_tool_call(ToolCallRecord(block.name, True, "", _elapsed_ms(started)))
    return _tool_result(block.id, _capped(json.dumps(result, default=str)))


def _capped(content: str) -> str:
    """``content`` cut to :data:`MAX_TOOL_RESULT_CHARS`, saying so, so one result fits a call."""
    if len(content) <= MAX_TOOL_RESULT_CHARS:
        return content
    return (
        content[:MAX_TOOL_RESULT_CHARS]
        + f"\n[Result cut at {MAX_TOOL_RESULT_CHARS} of {len(content)} characters. "
        "Narrow the request, for example with filters or a lower limit, to see the rest.]"
    )


def _elapsed_ms(started: float) -> int:
    return int((time.perf_counter() - started) * 1000)


def _stopped(result: ToolLoopResult) -> ToolLoopResult:
    """Record how the loop ended in the run's recorder, and return ``result``."""
    if (recorder := current_recorder.get()) is not None:
        recorder.record_stop(result.stopped)
    return result


def run_tool_loop(
    gateway: LLMGateway,
    *,
    tools: ToolRegistry,
    ctx: dict[str, Any],
    system: str,
    messages: list[dict[str, Any]],
    max_turns: int = 8,
    max_tokens: int = 4096,
    model: str | None = None,
    history_chars: int | None = DEFAULT_HISTORY_CHARS,
    cache_system: bool = True,
    on_turn: Callable[[int], None] | None = None,
) -> ToolLoopResult:
    """Call the model with ``tools`` until it finishes, dispatching its tool calls.

    Each turn calls the model, records its reply, and runs every tool call it made
    through ``tools.execute(..., ctx=ctx)``, sending the results back on the next turn.
    A tool that raises goes back to the model as an ``is_error`` result. The loop ends
    when the model ends its turn, after ``max_turns`` calls, or on any other stop
    reason; in that last case unanswered tool calls get error results, so the returned
    transcript stays valid to store and send again. Errors from the gateway propagate,
    including those from a sub-agent a tool runs.

    In a platform run, the loop also stops when the run reaches its model-call ceiling
    (``stopped="call_limit"``), raises ``RunDeadlineExceeded`` once the run is too
    close to its deadline to make another call, and gives each call no longer than the
    time left, split across its retries. A tool result longer than :data:`MAX_TOOL_RESULT_CHARS` is cut, with a
    note telling the model.

    Args:
        gateway: The run's :class:`LLMGateway`.
        tools: The tools the model may call, normally the agent's scoped ``self.tools``.
        ctx: Per-run context passed to every tool (``patient_id``, ``effects``, ...).
            Gets an empty ``effects`` list when it has none.
        system: The system prompt.
        messages: The conversation so far, ending with the turn to answer. Not modified.
        max_turns: The most model calls to make.
        max_tokens: ``max_tokens`` for each call.
        model: The model to call; defaults to ``gateway.model``.
        history_chars: The size budget for the history sent each turn
            (:func:`window_messages`); ``None`` sends all of it. The full history is
            always returned in :attr:`ToolLoopResult.messages`.
        cache_system: Mark the system prompt for prompt caching.
        on_turn: Called with the turn index before each model call. Its exceptions are
            logged and ignored.
    """
    client = gateway.client()
    transcript = list(messages)
    system_param: Any = (
        [{"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}]
        if cache_system
        else system
    )
    result = ToolLoopResult(messages=transcript, effects=ctx.setdefault("effects", []))

    for turn in range(max_turns):
        if on_turn is not None:
            try:
                on_turn(turn)
            except Exception:
                log.exception("on_turn hook raised; ignoring")

        recorder = current_recorder.get()
        request_options: dict[str, Any] = {}
        if recorder is not None:
            recorder.check_deadline()
            if not recorder.reserve_model_call():
                log.warning(
                    f"Tool loop stopped at the run's {recorder.max_model_calls} model calls"
                )
                result.stopped = "call_limit"
                return _stopped(result)
            if (left := recorder.seconds_left()) is not None:
                request_options["timeout"] = attempt_timeout(left)

        sent = transcript if history_chars is None else window_messages(transcript, history_chars)
        response = client.messages.create(
            model=model or gateway.model,
            max_tokens=max_tokens,
            system=system_param,
            tools=cast(Any, tools.definitions()),
            messages=cast(Any, sent),
            **request_options,
        )
        result.turns = turn + 1
        result.stop_reason = response.stop_reason
        log.info(
            f"Tool loop turn={turn} stop_reason={response.stop_reason} "
            f"blocks={[block.type for block in response.content]}"
        )

        transcript.append(
            {"role": "assistant", "content": [block.model_dump() for block in response.content]}
        )
        result.text = "\n".join(
            block.text for block in response.content if isinstance(block, TextBlock)
        ).strip()
        tool_uses = [block for block in response.content if isinstance(block, ToolUseBlock)]

        if response.stop_reason == "end_turn":
            result.stopped = "end_turn"
            return _stopped(result)
        if response.stop_reason in _TOOL_STOP_REASONS and tool_uses:
            transcript.append(
                {"role": "user", "content": [_run_tool(tools, block, ctx) for block in tool_uses]}
            )
            continue

        result.stopped = "unexpected"
        if tool_uses:
            reason = f"Not run: the turn ended with stop reason {response.stop_reason!r}."
            transcript.append(
                {
                    "role": "user",
                    "content": [
                        _tool_result(block.id, reason, is_error=True) for block in tool_uses
                    ],
                }
            )
        log.warning(f"Tool loop stopped on unexpected stop_reason={response.stop_reason!r}")
        return _stopped(result)

    log.warning(f"Tool loop hit max_turns={max_turns}")
    return _stopped(result)


__exports__ = ("ToolLoopResult", "run_tool_loop")
