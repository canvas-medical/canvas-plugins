# Add your plugin code here
from typing import Any

from canvas_core import events, logging
from canvas_core.plugins.events import PluginInitialized

logger = logging.get_logger(__name__)


@events.handle_event(PluginInitialized)
def handle_plugin_initialized_event(event: PluginInitialized, **kwargs: Any) -> None:
    """Handle plugin initialization."""
    plugin = event.plugin

    if plugin.name == "{{ cookiecutter.project_slug }}":
        logger.info("Plugin successfully initialized", plugin=plugin.name, version=plugin.version)
