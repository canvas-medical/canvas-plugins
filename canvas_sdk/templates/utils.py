from functools import cache, lru_cache
from pathlib import Path
from typing import Any

from django.template.backends.django import get_installed_libraries
from django.template.engine import Engine

from canvas_sdk.utils.plugins import plugin_context


@cache
def _installed_template_libraries() -> dict[str, str]:
    """Cache Django's template tag libraries lookup."""
    return get_installed_libraries()


@lru_cache(maxsize=5)
def _engine_for_plugin(plugin_dir: str) -> Engine:
    """Create a Django template engine for the given plugin directory."""
    return Engine(dirs=[plugin_dir], libraries=_installed_template_libraries())


@plugin_context
def render_to_string(
    template_name: str,
    context: dict[str, Any] | None = None,
    **kwargs: Any,
) -> str | None:
    """Load a template and render it with the given context.

    Args:
        template_name (str): The path to the template file, relative to the plugin package.
            If the path starts with a forward slash ("/"), it will be stripped during resolution.
        context (dict[str, Any] | None): A dictionary of variables to pass to the template
            for rendering. Defaults to None, which uses an empty context.
        kwargs (Any): Additional keyword arguments.

    Returns:
        str: The rendered template as a string.

    Raises:
        FileNotFoundError: If the template file does not exist within the plugin's directory
            or if the resolved path is invalid.
    """
    plugin_dir = kwargs["plugin_dir"]
    template_path = Path(plugin_dir / template_name.lstrip("/")).resolve()

    if not template_path.is_relative_to(plugin_dir):
        raise PermissionError(f"Invalid template '{template_name}'")
    elif not template_path.exists():
        raise FileNotFoundError(f"Template {template_name} not found.")

    engine = _engine_for_plugin(plugin_dir)
    return engine.render_to_string(str(template_path), context=context)


__exports__ = ("render_to_string",)
