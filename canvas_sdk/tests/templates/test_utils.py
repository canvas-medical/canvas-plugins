from pathlib import Path

import pytest

from canvas_sdk.effects import Effect
from canvas_sdk.events import Event, EventRequest, EventType
from plugin_runner.plugin_runner import LOADED_PLUGINS


@pytest.mark.parametrize("install_test_plugin", ["test_render_template"], indirect=True)
def test_render_to_string_valid_template(
    install_test_plugin: Path, load_test_plugins: None
) -> None:
    """Test that the render_to_string function loads and renders a valid template."""
    plugin = LOADED_PLUGINS[
        "test_render_template:test_render_template.protocols.my_protocol:ValidTemplate"
    ]
    result: list[Effect] = plugin["class"](Event(EventRequest(type=EventType.UNKNOWN))).compute()
    assert "html" in result[0].payload


@pytest.mark.parametrize("install_test_plugin", ["test_render_template"], indirect=True)
def test_render_to_string_invalid_template(
    install_test_plugin: Path, load_test_plugins: None
) -> None:
    """Test that the render_to_string function raises an error for invalid templates."""
    plugin = LOADED_PLUGINS[
        "test_render_template:test_render_template.protocols.my_protocol:InvalidTemplate"
    ]
    with pytest.raises(FileNotFoundError):
        plugin["class"](Event(EventRequest(type=EventType.UNKNOWN))).compute()


@pytest.mark.parametrize("install_test_plugin", ["test_render_template"], indirect=True)
def test_render_to_string_forbidden_template(
    install_test_plugin: Path, load_test_plugins: None
) -> None:
    """Test that the render_to_string function raises an error for a template outside plugin package."""
    plugin = LOADED_PLUGINS[
        "test_render_template:test_render_template.protocols.my_protocol:ForbiddenTemplate"
    ]
    with pytest.raises(PermissionError):
        plugin["class"](Event(EventRequest(type=EventType.UNKNOWN))).compute()
