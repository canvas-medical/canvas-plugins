"""What an agent run did, recorded for the platform's run record.

The plugin-runner opens a :class:`RunRecorder` around each run and reads it back
afterwards. :func:`canvas_sdk.agents.run_tool_loop` records into whichever recorder is
current, so plugin code never touches it: this module is not importable from the
plugin sandbox.
"""

from contextvars import ContextVar
from dataclasses import dataclass, field
from threading import Lock


@dataclass(frozen=True)
class ToolCallRecord:
    """One tool call: its name, outcome, and duration. No arguments or results."""

    name: str
    ok: bool
    error_type: str
    duration_ms: int


@dataclass
class RunRecorder:
    """Counts a run's model calls and records its tool calls.

    Sub-agents record from worker threads, so writes take a lock.
    """

    model_calls: int = 0
    stop_reason: str = ""
    tool_calls: list[ToolCallRecord] = field(default_factory=list)
    _lock: Lock = field(default_factory=Lock, repr=False)

    def record_model_call(self) -> None:
        """Count one model call."""
        with self._lock:
            self.model_calls += 1

    def record_tool_call(self, call: ToolCallRecord) -> None:
        """Record one dispatched tool call."""
        with self._lock:
            self.tool_calls.append(call)

    def record_stop(self, stop_reason: str) -> None:
        """Record the stop reason of a tool loop that ended; the last one wins."""
        with self._lock:
            self.stop_reason = stop_reason


current_recorder: ContextVar[RunRecorder | None] = ContextVar("current_recorder", default=None)

# Nothing here is importable from the plugin sandbox.
__exports__ = ()
