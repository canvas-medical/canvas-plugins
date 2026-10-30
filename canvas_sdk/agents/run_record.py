"""What an agent run did, and the limits it runs under, for the platform.

The plugin-runner opens a :class:`RunRecorder` around each run and reads it back
afterwards. :func:`canvas_sdk.agents.run_tool_loop` records into whichever recorder is
current and checks its limits before each model call, so plugin code never touches
it: this module is not importable from the plugin sandbox.
"""

import time
from contextvars import ContextVar
from dataclasses import dataclass, field
from threading import Lock

# Time kept back from a run's deadline for what follows the agent's last model call:
# saving its state and returning its effects.
DEADLINE_MARGIN_SECONDS = 30.0


class RunDeadlineExceeded(Exception):
    """The run is too close to its deadline to finish; its state and effects are discarded."""


@dataclass(frozen=True)
class ToolCallRecord:
    """One tool call: its name, outcome, and duration. No arguments or results."""

    name: str
    ok: bool
    error_type: str
    duration_ms: int


@dataclass
class RunRecorder:
    """Counts a run's model calls, records its tool calls, and holds its limits.

    ``deadline`` is a ``time.monotonic()`` value, or None for no deadline.
    ``max_model_calls`` caps the model calls of the whole run, sub-agents included.
    Sub-agents record from worker threads, so writes take a lock.
    """

    model_calls: int = 0
    stop_reason: str = ""
    tool_calls: list[ToolCallRecord] = field(default_factory=list)
    deadline: float | None = None
    max_model_calls: int | None = None
    _lock: Lock = field(default_factory=Lock, repr=False)

    def reserve_model_call(self) -> bool:
        """Count a model call about to be made, or return False when the run's ceiling is reached."""
        with self._lock:
            if self.max_model_calls is not None and self.model_calls >= self.max_model_calls:
                return False
            self.model_calls += 1
            return True

    def seconds_left(self) -> float | None:
        """Seconds until the deadline less the margin, or None without a deadline."""
        if self.deadline is None:
            return None
        return self.deadline - time.monotonic() - DEADLINE_MARGIN_SECONDS

    def check_deadline(self) -> None:
        """Raise :class:`RunDeadlineExceeded` once the run is inside the margin of its deadline."""
        left = self.seconds_left()
        if left is not None and left <= 0:
            raise RunDeadlineExceeded("the run reached its deadline")

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
