"""Live progress of an agent run, for the person waiting on it.

The plugin-runner streams heartbeats while a run is alive. An agent whose manifest entry
sets ``"progress": "activity"`` adds a label as each tool starts and finishes, and
``"reply"`` adds its reply text as the model writes it. Tool arguments and results are
never part of it. The tool loop reports into the run's
:class:`~canvas_sdk.agents.run_record.RunRecorder`, so plugin code never touches this
module: it is not importable from the plugin sandbox.
"""

import threading
from collections import deque
from dataclasses import dataclass

# How much of a run's progress reaches the browser, each level including the ones
# before it: "status" is heartbeats only, "activity" adds a label per tool call, and
# "reply" adds the reply text as it is written.
PROGRESS_LEVELS = ("status", "activity", "reply")
DEFAULT_PROGRESS = "status"
# The label for a tool that registered none, so its internal name never reaches the UI.
DEFAULT_PROGRESS_LABEL = "Looking something up"
# Tool events waiting to be streamed; past this a slow reader loses tool events rather
# than slowing the run. Text is never dropped: it merges into the text before it.
MAX_QUEUED_EVENTS = 100


def agent_progress_level(manifest_entry: dict) -> str:
    """The progress level the agent ``manifest_entry`` declares, or the default."""
    level = manifest_entry.get("progress")
    return level if level in PROGRESS_LEVELS else DEFAULT_PROGRESS


@dataclass(frozen=True)
class ProgressEvent:
    """One thing to show the person waiting: a tool call, a new model turn, or text."""

    kind: str
    label: str = ""
    ok: bool = False
    text: str = ""


class ProgressFeed:
    """The progress a run's agent may show, queued in order for the plugin-runner to stream."""

    def __init__(self, level: str) -> None:
        self.level = level
        self._events: deque[ProgressEvent] = deque()
        self._ready = threading.Condition()

    @property
    def shows_activity(self) -> bool:
        """Whether tool calls are shown."""
        return self.level in ("activity", "reply")

    @property
    def shows_reply(self) -> bool:
        """Whether reply text is shown."""
        return self.level == "reply"

    def tool(self, kind: str, label: str, ok: bool = False) -> None:
        """Queue a tool event when the agent's level shows tool activity."""
        if not self.shows_activity:
            return
        with self._ready:
            if len(self._events) < MAX_QUEUED_EVENTS:
                self._events.append(ProgressEvent(kind, label, ok))
                self._ready.notify()

    def turn(self) -> None:
        """Queue the start of a model call, whose text replaces the turn's before it."""
        if not self.shows_reply:
            return
        with self._ready:
            self._events.append(ProgressEvent("turn_started"))
            self._ready.notify()

    def text(self, delta: str) -> None:
        """Queue reply text, merged into text still waiting to be streamed."""
        if not self.shows_reply or not delta:
            return
        with self._ready:
            if self._events and self._events[-1].kind == "text":
                delta = self._events.pop().text + delta
            self._events.append(ProgressEvent("text", text=delta))
            self._ready.notify()

    def next(self, timeout: float) -> ProgressEvent | None:
        """The next queued event, or None when none arrives within ``timeout`` seconds."""
        with self._ready:
            if not self._events:
                self._ready.wait(timeout)
            return self._events.popleft() if self._events else None


# Nothing here is importable from the plugin sandbox.
__exports__ = ()
