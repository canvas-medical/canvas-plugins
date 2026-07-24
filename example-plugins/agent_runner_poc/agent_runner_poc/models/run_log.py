"""AgentRunLog — one row per ``AgentPlugin`` invocation.

Written by :class:`RunLoggingMixin` lifecycle-hook overrides:
``on_run_start`` opens the row with ``status="running"``; ``on_run_end``
closes it as ``"success"``; ``on_run_error`` closes it as ``"error"``
with the exception type + truncated message. Captures wall-clock
duration and LLM turn count for each run.

Demonstrates the doc §6.3 hook-surface seam — cross-cutting
observability without polluting agent business logic — and gives the
V1 cost/audit story (§6.4) a concrete schema to layer per-call token
and cost counters on top of.

PoC retention: rows accumulate indefinitely. V1 should either prune
on a TTL or roll up into aggregate counters once cost accounting
lands gateway-side.
"""

from __future__ import annotations

from django.db.models import DateTimeField, Index, IntegerField, TextField

from canvas_sdk.v1.data.base import CustomModel


class AgentRunLog(CustomModel):
    """One row per AgentPlugin invocation (success or failure)."""

    agent_class_name: TextField[str, str] = TextField()
    scope_key: TextField[str, str] = TextField()

    # Lifecycle status. Transitions: running → success | error.
    status: TextField[str, str] = TextField()

    # Set by auto_now_add on first save; captured in on_run_start.
    started_at: DateTimeField[str, str] = DateTimeField(auto_now_add=True)

    # Set by on_run_end / on_run_error when the row is closed. Null
    # while the row is still in "running" status.
    completed_at: DateTimeField[str, str] = DateTimeField(null=True, blank=True)

    # Wall-clock duration end-to-end (started_at → completed_at).
    # Null while running; set on close.
    duration_ms: IntegerField[int, int] = IntegerField(null=True, blank=True)

    # Number of LLM turns the agent's run() took before exiting (success
    # or error). Captured by the mixin from ``self._llm_turn_count``,
    # which the agent's run loop increments on each iteration.
    llm_turns: IntegerField[int, int] = IntegerField(null=True, blank=True)

    # Populated only when status == "error".
    error_type: TextField[str, str] = TextField(blank=True, default="")
    error_message: TextField[str, str] = TextField(blank=True, default="")

    class Meta:
        indexes = [
            # "recent runs of this agent" — drives any debugging-by-class view.
            Index(fields=["agent_class_name", "-started_at"]),
            # "recent runs against this scope_key" — drives per-patient or
            # per-chat audit-trail queries.
            Index(fields=["scope_key", "-started_at"]),
        ]
