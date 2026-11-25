"""Sentry event processors shared by the runner and the SDK handlers."""

from typing import Any


def without_frame_locals(event: Any, hint: Any) -> Any:
    """A Sentry event with every stack frame's local variables removed."""
    for kind in ("exception", "threads"):
        for value in (event.get(kind) or {}).get("values") or []:
            for frame in (value.get("stacktrace") or {}).get("frames") or []:
                frame.pop("vars", None)
    return event
