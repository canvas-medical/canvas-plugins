"""Live progress of an agent run, for the person waiting on it.

The plugin-runner streams heartbeats while a run is alive and, for an agent whose
manifest entry sets ``"progress": "activity"``, a label as each tool starts and
finishes. Tool arguments and results are never part of it. The tool loop reports into
the run's :class:`~canvas_sdk.agents.run_record.RunRecorder`, so plugin code never
touches this module: it is not importable from the plugin sandbox.
"""

import contextlib
import queue
from dataclasses import dataclass

# How much of a run's progress reaches the browser, each level including the ones
# before it: "status" is heartbeats only, "activity" adds a label per tool call.
PROGRESS_LEVELS = ("status", "activity")
DEFAULT_PROGRESS = "status"
# The label for a tool that registered none, so its internal name never reaches the UI.
DEFAULT_PROGRESS_LABEL = "Looking something up"
# Tool events waiting to be streamed; past this a slow reader loses events rather than
# slowing the run, and heartbeats still say the run is alive.
MAX_QUEUED_EVENTS = 100


def agent_progress_level(manifest_entry: dict) -> str:
    """The progress level the agent ``manifest_entry`` declares, or the default."""
    level = manifest_entry.get("progress")
    return level if level in PROGRESS_LEVELS else DEFAULT_PROGRESS


@dataclass(frozen=True)
class ToolProgress:
    """A tool call starting or finishing: its label, and for a finish, whether it succeeded."""

    kind: str
    label: str
    ok: bool = False


class ProgressFeed:
    """The tool events a run's agent may show, queued for the plugin-runner to stream."""

    def __init__(self, level: str) -> None:
        self.level = level
        self._queue: queue.Queue[ToolProgress] = queue.Queue(maxsize=MAX_QUEUED_EVENTS)

    def tool(self, kind: str, label: str, ok: bool = False) -> None:
        """Queue a tool event when the agent's level shows tool activity."""
        if self.level != "activity":
            return
        with contextlib.suppress(queue.Full):
            self._queue.put_nowait(ToolProgress(kind, label, ok))

    def next(self, timeout: float) -> ToolProgress | None:
        """The next queued event, or None when none arrives within ``timeout`` seconds."""
        try:
            return self._queue.get(timeout=timeout)
        except queue.Empty:
            return None


# Nothing here is importable from the plugin sandbox.
__exports__ = ()
