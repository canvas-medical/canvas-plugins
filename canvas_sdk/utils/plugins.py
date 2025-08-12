import inspect
from collections.abc import Callable
from pathlib import Path
from types import FrameType
from typing import Any

from canvas_sdk.utils.metrics import measured
from settings import PLUGIN_DIRECTORY


def find_plugin_ancestor(frame: FrameType | None, max_depth: int = 10) -> FrameType | None:
    """
    Recurse backwards to find any plugin ancestor of this frame.
    """
    parent_frame = frame.f_back if frame else None

    if not parent_frame:
        return None

    if max_depth == 0:
        return None

    if "__is_plugin__" in parent_frame.f_globals:
        return parent_frame

    return find_plugin_ancestor(frame=parent_frame, max_depth=max_depth - 1)


@measured
def plugin_context(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator to restrict a function's execution to plugins only."""

    def wrapper(*args: Any, **kwargs: Any) -> Any:
        plugin_frame = find_plugin_ancestor(inspect.currentframe())

        if not plugin_frame:
            raise RuntimeError(
                "Method that expected plugin context was called from outside a plugin."
            )

        plugin_name = plugin_frame.f_globals["__name__"].split(".")[0]
        plugin_dir = Path(PLUGIN_DIRECTORY) / plugin_name

        kwargs["plugin_name"] = plugin_name
        kwargs["plugin_dir"] = plugin_dir.resolve()

        return func(*args, **kwargs)

    return wrapper


@measured
def is_plugin_caller() -> tuple[bool, str | None]:
    """Check if a function is called from a plugin."""
    plugin_frame = find_plugin_ancestor(inspect.currentframe())

    if plugin_frame:
        module = plugin_frame.f_globals.get("__name__")
        qualname = plugin_frame.f_code.co_qualname

        return True, f"{module}.{qualname}"

    return False, None


__exports__ = ()
