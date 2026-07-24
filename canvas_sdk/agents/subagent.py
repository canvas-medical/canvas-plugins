"""Sub-agent helpers — focused, parallel LLM calls within a parent agent's turn.

A sub-agent is a *role*, not a class. :class:`SubAgentSpec` captures the
parameters of one focused LLM call: a persona system prompt, a tool
subset (scoped from the parent's manifest-granted catalog), and a turn
budget. The parent invokes one or more sub-agents inside its own
``run()`` to delegate narrow sub-questions and synthesize the results.

Use cases worth fanning out for:

- **Pre-visit brief** — spawn focused sub-agents per chart-domain
  (recent labs, recent meds, recent visits, outstanding tasks) in
  parallel; parent assembles the brief. Each sub-agent has a tight
  context window scoped to its domain.
- **Multi-channel drafting** — patient message + chart note + team
  ping drafted in parallel by personas tuned for each audience.
- **Cohort comparison** — per-dimension reasoning across similar
  patients.

Sub-agents share the parent's ``ctx`` dict (patient_id, staff_id,
effects accumulator, note_id) so any write effects they originate flow
into the same dispatch queue. They have NO separate persistent state,
no ``scope_key``, and no ``agent_lock`` — the parent's lock covers
them. A sub-agent's tool subset is intersected with the parent's
manifest-granted catalog (via :meth:`ToolRegistry.scope`), so a
sub-agent can never access tools the parent itself isn't allowed to
use. The manifest stays the security boundary.

Parallelism is via ``canvas_sdk.utils.http.ThreadPoolExecutor`` (the
sandbox-allowlisted re-export of :class:`concurrent.futures.ThreadPoolExecutor`).
Anthropic's Python client is thread-safe; list appends on the shared
``effects`` accumulator are atomic in CPython.

If a sub-agent ever needs durable state, event-driven invocation, or
cross-plugin reuse, that's the signal to promote it to a full
:class:`AgentPlugin` subclass — those are agents, not roles.
"""

import json
import logging
from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Any, cast

from anthropic import Anthropic
from anthropic.types import TextBlock, ToolUseBlock

from canvas_sdk.agents.gateway import LLMGateway
from canvas_sdk.agents.tool_registry import ToolRegistry
from canvas_sdk.utils.http import ThreadPoolExecutor

log = logging.getLogger("plugin_runner_logger")


@dataclass(frozen=True)
class SubAgentSpec:
    """Configuration for one focused sub-agent invocation.

    Attributes:
        name: Identifier for logs and the keys of the
            :func:`run_subagents` result dict. Keep short and
            machine-friendly (e.g. ``"labs_trends"``).
        system_prompt: The persona prompt for this sub-agent. Should be
            narrow and specific — that's the whole point of fanning
            out. Avoid restating the parent's mission.
        allowed_tool_names: Tool names this sub-agent may use. MUST be
            a subset of the parent's manifest-granted catalog; names
            outside the parent's catalog are silently dropped at
            scope-time. Keep tight — one of the wins of fan-out is
            that the model isn't distracted by tools it can't use here.
        max_turns: Cap on tool-use loop iterations. Default 4 — most
            domain-scoped sub-agents converge in 1-2 turns. Bump if
            the persona genuinely needs multi-step reasoning.
        max_tokens: Anthropic max_tokens per turn. Default 2048 —
            sub-agents return summaries, not essays.
    """

    name: str
    system_prompt: str
    allowed_tool_names: frozenset[str] = field(default_factory=frozenset)
    max_turns: int = 4
    max_tokens: int = 2048


def run_subagent(
    spec: SubAgentSpec,
    user_message: str,
    *,
    parent_tools: ToolRegistry,
    parent_ctx: dict[str, Any],
    gateway: LLMGateway,
) -> str:
    """Run one sub-agent's focused tool-use loop and return its final text.

    The loop mirrors the standard pattern used by :class:`AgentPlugin`
    implementations: alternating ``client.messages.create`` calls and
    ``tool_use`` dispatch until the model emits ``stop_reason="end_turn"``
    or the turn budget is exhausted.

    Errors during individual tool calls are reported back to the model
    as ``tool_result`` blocks with ``is_error=True`` so the sub-agent
    can recover; exceptions from the LLM call or other unexpected
    failures propagate to the caller.

    Args:
        spec: Persona, tool subset, and limits for this sub-agent.
        user_message: The question/task the parent is delegating. Sub-
            agents start fresh per call — they have no message history.
        parent_tools: The parent agent's tool registry. ``spec``'s
            tool subset is intersected against this via :meth:`ToolRegistry.scope`.
        parent_ctx: The parent's tool context (patient_id, staff_id,
            effects list, note_id, etc.). Shared — write effects from
            the sub-agent flow into the parent's accumulator.
        gateway: The parent's :class:`LLMGateway`. Reused as-is; the
            Anthropic client is thread-safe.

    Returns:
        The sub-agent's final text response, stripped. Empty string if
        the loop runs out of turns without an ``end_turn`` stop, or if
        the final turn produced no text block.
    """
    sub_tools = parent_tools.scope(spec.allowed_tool_names)
    client = Anthropic(api_key=gateway.api_key)
    messages: list[dict[str, Any]] = [{"role": "user", "content": user_message}]

    for turn in range(spec.max_turns):
        response = client.messages.create(
            model=gateway.model,
            max_tokens=spec.max_tokens,
            system=spec.system_prompt,
            tools=cast(Any, sub_tools.definitions()),
            messages=cast(Any, messages),
        )
        log.info(
            f"SubAgent[{spec.name}] turn={turn} stop_reason={response.stop_reason} "
            f"blocks={[b.type for b in response.content]}"
        )

        messages.append(
            {
                "role": "assistant",
                "content": [block.model_dump() for block in response.content],
            }
        )

        if response.stop_reason == "end_turn":
            for block in response.content:
                if isinstance(block, TextBlock):
                    return block.text.strip()
            return ""

        tool_use_blocks = [b for b in response.content if isinstance(b, ToolUseBlock)]
        if response.stop_reason not in ("tool_use", "max_tokens") or not tool_use_blocks:
            log.warning(
                f"SubAgent[{spec.name}]: unexpected stop_reason={response.stop_reason!r}; bailing"
            )
            break

        tool_results: list[dict[str, Any]] = []
        for block in tool_use_blocks:
            try:
                result = sub_tools.execute(block.name, dict(block.input), ctx=parent_ctx)
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(result, default=str),
                    }
                )
            except Exception as exc:
                log.exception(f"SubAgent[{spec.name}]: tool {block.name!r} raised")
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": f"Tool execution failed: {exc!s}",
                        "is_error": True,
                    }
                )
        messages.append({"role": "user", "content": tool_results})

    return ""


def run_subagents(
    specs: Iterable[SubAgentSpec],
    user_message: str,
    *,
    parent_tools: ToolRegistry,
    parent_ctx: dict[str, Any],
    gateway: LLMGateway,
    max_parallel: int = 4,
) -> dict[str, str]:
    """Run multiple sub-agents in parallel; return ``{spec.name: final_text}``.

    A failed sub-agent's entry is a string starting with
    ``"(sub-agent ... failed: ...)"`` rather than its result — the
    parent can decide whether to mention the failure or proceed with
    the rest. Order of the returned dict is insertion order of
    ``specs`` (regardless of completion order).

    Args:
        specs: Sub-agent configurations. ``spec.name`` must be unique
            within the call — duplicates clobber each other in the
            result dict.
        user_message: Shared delegation prompt. To give each sub-agent
            a different question, run them via :func:`run_subagent`
            directly or wrap them in a parent-side dispatch step.
        parent_tools: The parent agent's tool registry.
        parent_ctx: The parent's tool context. Shared across all
            sub-agents — write effects from any sub-agent land in the
            same accumulator.
        gateway: The parent's :class:`LLMGateway`.
        max_parallel: Upper bound on concurrent sub-agents. Defaults
            to 4. Bigger fan-outs should consider Anthropic
            per-organization rate limits.

    Returns:
        Mapping of spec name to final text. Failures are returned as
        diagnostic strings, not raised.
    """
    spec_list = list(specs)
    if not spec_list:
        return {}

    workers = min(len(spec_list), max(1, max_parallel))
    results: dict[str, str] = {spec.name: "" for spec in spec_list}
    with ThreadPoolExecutor(max_workers=workers) as pool:
        future_to_name = {
            pool.submit(
                run_subagent,
                spec,
                user_message,
                parent_tools=parent_tools,
                parent_ctx=parent_ctx,
                gateway=gateway,
            ): spec.name
            for spec in spec_list
        }
        for future, name in future_to_name.items():
            try:
                results[name] = future.result()
            except Exception as exc:
                log.exception(f"SubAgent[{name}] failed")
                results[name] = f"(sub-agent {name!r} failed: {exc!s})"
    return results


__exports__ = ("SubAgentSpec", "run_subagent", "run_subagents")
