import inspect
from pathlib import Path
from typing import Any

from django.template import Context, Template

from settings import PLUGIN_DIRECTORY


def render_to_string(template_name: str, context: dict[str, Any] | None = None) -> str | None:
    """Load a template and render it with the given context.

    Args:
        template_name (str): The path to the template file, relative to the plugin package.
            If the path starts with a forward slash ("/"), it will be stripped during resolution.
        context (dict[str, Any] | None): A dictionary of variables to pass to the template
            for rendering. Defaults to None, which uses an empty context.

    Returns:
        str: The rendered template as a string.

    Raises:
        FileNotFoundError: If the template file does not exist within the plugin's directory
            or if the resolved path is invalid.
    """
    plugins_dir = Path(PLUGIN_DIRECTORY).resolve()
    current_frame = inspect.currentframe()
    caller = current_frame.f_back if current_frame else None

    if not caller or "__is_plugin__" not in caller.f_globals:
        return None

    plugin_name = caller.f_globals["__name__"].split(".")[0]
    plugin_dir = plugins_dir / plugin_name
    template_path = Path(plugin_dir / template_name.lstrip("/")).resolve()

    if not template_path.is_relative_to(plugin_dir):
        raise PermissionError(f"Invalid template '{template_name}'")
    elif not template_path.exists():
        raise FileNotFoundError(f"Template {template_name} not found.")

    template = Template(template_path.read_text())

    return template.render(Context(context))
