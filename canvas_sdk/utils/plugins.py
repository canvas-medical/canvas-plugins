import inspect
from collections.abc import Callable
from pathlib import Path
from types import FrameType
from typing import Any

from canvas_sdk.utils.metrics import measured
from settings import PLUGIN_DIRECTORY


@measured
def plugin_only(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator to restrict a function's execution to plugins only."""

    def wrapper(*args: Any, **kwargs: Any) -> Any:
        current_frame = inspect.currentframe()
        caller = current_frame.f_back if current_frame else None

        if not caller or "__is_plugin__" not in caller.f_globals:
            return None

        plugin_name = caller.f_globals["__name__"].split(".")[0]
        plugin_dir = Path(PLUGIN_DIRECTORY) / plugin_name
        kwargs["plugin_name"] = plugin_name
        kwargs["plugin_dir"] = plugin_dir.resolve()

        return func(*args, **kwargs)

    return wrapper


@measured
def is_plugin_caller(depth: int = 10, frame: FrameType | None = None) -> tuple[bool, str | None]:
    """Check if a function is called from a plugin."""
    current_frame = frame or inspect.currentframe()
    caller = current_frame.f_back if current_frame else None

    if not caller:
        return False, None

    if "__is_plugin__" not in caller.f_globals:
        if depth > 0:
            return is_plugin_caller(frame=caller, depth=depth - 1)
        else:
            return False, None

    module = caller.f_globals.get("__name__")
    qualname = caller.f_code.co_qualname

    return True, f"{module}.{qualname}"


__exports__ = ()
