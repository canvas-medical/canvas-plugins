"""RunLoggingMixin — write one :class:`AgentRunLog` row per agent invocation.

Demonstrates the doc §6.3 lifecycle-hook seam. Agents that inherit
from this mixin get an audit row for every invocation: status,
wall-clock duration, LLM turn count, and any error info — all without
the agent's ``run()`` having to thread observability through its
business logic.

MRO: declare the mixin *before* :class:`AgentPlugin`:

    class MyAgent(RunLoggingMixin, AgentPlugin):
        def run(self, state, gateway, trigger_payload):
            for turn_index in range(MAX_TURNS):
                self._llm_turn_count += 1
                ...

The agent's loop bumps ``self._llm_turn_count`` on each LLM call; the
mixin's ``on_run_end`` / ``on_run_error`` stamps it onto the log row.

Hook failures are swallowed by the plugin-runner (per
``_invoke_agent_hook`` in ``plugin_runner.py``), so a broken
observability path can't crash the underlying agent run. The mixin
itself guards against ``on_run_end`` / ``on_run_error`` firing when
``on_run_start`` was skipped (e.g., if the row creation itself failed).
"""

from __future__ import annotations

from datetime import UTC, datetime

from agent_runner_poc.models.run_log import AgentRunLog
from canvas_sdk.agents import AgentRunResult


class RunLoggingMixin:
    """Write one :class:`AgentRunLog` row per invocation via lifecycle hooks."""

    # Type-annotated for mypy. Set by on_run_start; guarded by None-checks
    # in the close path so a row-creation failure doesn't cascade.
    _run_log: AgentRunLog | None = None
    _run_started_at: datetime
    _llm_turn_count: int = 0

    def on_run_start(self, scope_key: str) -> None:
        """Open a 'running' row tagged with the agent's class name + scope_key."""
        self._llm_turn_count = 0
        self._run_started_at = datetime.now(UTC)
        self._run_log = AgentRunLog.objects.create(
            agent_class_name=self.__class__.__name__,
            scope_key=scope_key,
            status="running",
        )

    def on_run_end(self, result: AgentRunResult) -> None:
        """Close the row as successful."""
        self._close_run_log(status="success")

    def on_run_error(self, exc: BaseException) -> None:
        """Close the row as errored, recording the exception type + truncated message."""
        if self._run_log is None:
            return
        self._run_log.error_type = type(exc).__name__
        # Truncate to avoid bloating the row on giant tracebacks.
        self._run_log.error_message = str(exc)[:500]
        self._close_run_log(status="error")

    def _close_run_log(self, *, status: str) -> None:
        """Stamp completed_at, duration_ms, llm_turns, status; persist."""
        if self._run_log is None:
            return
        completed_at = datetime.now(UTC)
        duration_ms = int((completed_at - self._run_started_at).total_seconds() * 1000)
        # django-stubs types DateTimeField[str, str] in this codebase; the
        # runtime field accepts datetime objects fine (Django's standard
        # behavior). Suppress the stub-vs-runtime mismatch on the assignment.
        self._run_log.completed_at = completed_at  # type: ignore[assignment]
        self._run_log.duration_ms = duration_ms
        self._run_log.llm_turns = self._llm_turn_count
        self._run_log.status = status
        self._run_log.save()
