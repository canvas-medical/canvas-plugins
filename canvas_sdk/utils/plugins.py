import inspect
from collections.abc import Callable
from pathlib import Path
from typing import Any

from settings import PLUGIN_DIRECTORY


def plugin_only(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator to restrict a function's execution to plugins only."""

    def wrapper(*args: Any, **kwargs: Any) -> Any:
        current_frame = inspect.currentframe()
        caller = current_frame.f_back if current_frame else None

        if not caller or "__is_plugin__" not in caller.f_globals:
            return None

        plugin_name = caller.f_globals["__name__"].split(".")[0]
        plugin_dir = Path(PLUGIN_DIRECTORY) / plugin_name
        kwargs["plugin_dir"] = plugin_dir.resolve()

        return func(*args, **kwargs)

    return wrapper
