import shutil
from pathlib import Path
from typing import Generator
from unittest.mock import MagicMock, patch

import pytest

from canvas_generated.messages.effects_pb2 import EffectType
from canvas_generated.messages.plugins_pb2 import ReloadPluginsRequest
from canvas_sdk.events import Event, EventType
from plugin_runner.plugin_runner import (
    EVENT_PROTOCOL_MAP,
    LOADED_PLUGINS,
    PluginRunner,
    load_plugins,
    sandbox_from_package,
)


@pytest.fixture
def setup_test_plugin(request: pytest.FixtureRequest) -> Generator[Path, None, None]:
    """Copies a specified plugin from the fixtures directory to the data directory
    and removes it after the test.

    Parameters:
    - request.param: The name of the plugin package to copy.

    Yields:
    - Path to the copied plugin directory.
    """
    # Define base directories
    base_dir = Path("./plugin_runner/tests")
    fixture_plugin_dir = base_dir / "fixtures" / "plugins"
    data_plugin_dir = base_dir / "data" / "plugins"

    # The plugin name should be passed as a parameter to the fixture
    plugin_name = request.param  # Expected to be a str
    src_plugin_path = fixture_plugin_dir / plugin_name
    dest_plugin_path = data_plugin_dir / plugin_name

    # Ensure the data plugin directory exists
    data_plugin_dir.mkdir(parents=True, exist_ok=True)

    # Copy the specific plugin from fixtures to data
    try:
        shutil.copytree(src_plugin_path, dest_plugin_path)
        yield dest_plugin_path  # Provide the path to the test
    finally:
        # Cleanup: remove data/plugins directory after the test
        if dest_plugin_path.exists():
            shutil.rmtree(dest_plugin_path)


@pytest.fixture
def plugin_runner() -> PluginRunner:
    """Fixture to initialize PluginRunner with mocks."""
    runner = PluginRunner()
    runner.statsd_client = MagicMock()
    return runner


@pytest.mark.parametrize("setup_test_plugin", ["example_plugin"], indirect=True)
def test_load_plugins_with_valid_plugin(setup_test_plugin: Path) -> None:
    """Test loading plugins with a valid plugin."""
    load_plugins()

    assert "example_plugin:example_plugin.protocols.my_protocol:Protocol" in LOADED_PLUGINS
    assert (
        LOADED_PLUGINS["example_plugin:example_plugin.protocols.my_protocol:Protocol"]["active"]
        is True
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("setup_test_plugin", ["test_module_imports_plugin"], indirect=True)
async def test_load_plugins_with_plugin_that_imports_other_modules_within_plugin_package(
    setup_test_plugin: Path, plugin_runner: PluginRunner
) -> None:
    """Test loading plugins with a valid plugin that imports other modules within the current plugin package."""
    load_plugins()
    assert (
        "test_module_imports_plugin:test_module_imports_plugin.protocols.my_protocol:Protocol"
        in LOADED_PLUGINS
    )
    assert (
        LOADED_PLUGINS[
            "test_module_imports_plugin:test_module_imports_plugin.protocols.my_protocol:Protocol"
        ]["active"]
        is True
    )

    result = [
        response
        async for response in plugin_runner.HandleEvent(Event(type=EventType.UNKNOWN), None)
    ]

    assert len(result) == 1
    assert result[0].success is True
    assert len(result[0].effects) == 1
    assert result[0].effects[0].type == EffectType.LOG
    assert result[0].effects[0].payload == "Successfully imported!"


@pytest.mark.parametrize(
    "setup_test_plugin",
    [
        "test_module_imports_outside_plugin_v1",
        "test_module_imports_outside_plugin_v2",
        "test_module_imports_outside_plugin_v3",
    ],
    indirect=True,
)
def test_load_plugins_with_plugin_that_imports_other_modules_outside_plugin_package(
    setup_test_plugin: Path,
) -> None:
    """Test loading plugins with an invalid plugin that imports other modules outside the current plugin package."""
    with pytest.raises(ImportError, match="is not an allowed import"):
        sandbox_from_package(setup_test_plugin)


@pytest.mark.parametrize("setup_test_plugin", ["example_plugin"], indirect=True)
def test_reload_plugin(setup_test_plugin: Path) -> None:
    """Test reloading a plugin."""
    load_plugins()
    load_plugins()

    assert "example_plugin:example_plugin.protocols.my_protocol:Protocol" in LOADED_PLUGINS
    assert (
        LOADED_PLUGINS["example_plugin:example_plugin.protocols.my_protocol:Protocol"]["active"]
        is True
    )


@pytest.mark.parametrize("setup_test_plugin", ["example_plugin"], indirect=True)
def test_remove_plugin_should_be_removed_from_loaded_plugins(setup_test_plugin: Path) -> None:
    """Test removing a plugin."""
    load_plugins()
    assert "example_plugin:example_plugin.protocols.my_protocol:Protocol" in LOADED_PLUGINS
    shutil.rmtree(setup_test_plugin)
    load_plugins()
    assert "example_plugin:example_plugin.protocols.my_protocol:Protocol" not in LOADED_PLUGINS


@pytest.mark.parametrize("setup_test_plugin", ["example_plugin"], indirect=True)
def test_load_plugins_should_refresh_event_protocol_map(setup_test_plugin: Path) -> None:
    """Test that the event protocol map is refreshed when loading plugins."""
    assert EVENT_PROTOCOL_MAP == {}
    load_plugins()
    assert EventType.Name(EventType.UNKNOWN) in EVENT_PROTOCOL_MAP
    assert EVENT_PROTOCOL_MAP[EventType.Name(EventType.UNKNOWN)] == [
        "example_plugin:example_plugin.protocols.my_protocol:Protocol"
    ]


@pytest.mark.asyncio
@pytest.mark.parametrize("setup_test_plugin", ["example_plugin"], indirect=True)
async def test_handle_plugin_event_returns_expected_result(
    setup_test_plugin: Path, plugin_runner: PluginRunner
) -> None:
    """Test that HandleEvent successfully calls the relevant plugins and returns the expected result."""
    load_plugins()

    event = Event(type=EventType.UNKNOWN)

    result = []
    async for response in plugin_runner.HandleEvent(event, None):
        result.append(response)

    assert len(result) == 1
    assert result[0].success is True
    assert len(result[0].effects) == 1
    assert result[0].effects[0].type == EffectType.LOG
    assert result[0].effects[0].payload == "Hello, world!"


@pytest.mark.asyncio
@pytest.mark.parametrize("setup_test_plugin", ["example_plugin"], indirect=True)
async def test_reload_plugins_event_handler_successfully_loads_plugins(
    setup_test_plugin: Path, plugin_runner: PluginRunner
) -> None:
    """Test ReloadPlugins Event handler successfully loads plugins."""

    with patch("plugin_runner.plugin_runner.publish_message", MagicMock()) as mock_publish_message:
        request = ReloadPluginsRequest()

        result = []
        async for response in plugin_runner.ReloadPlugins(request, None):
            result.append(response)

        mock_publish_message.assert_called_once_with({"action": "restart"})

    assert len(result) == 1
    assert result[0].success is True
    assert "example_plugin:example_plugin.protocols.my_protocol:Protocol" in LOADED_PLUGINS


@pytest.mark.asyncio
async def test_reload_plugins_import_error(plugin_runner: PluginRunner) -> None:
    """Test ReloadPlugins response when an ImportError occurs."""
    request = ReloadPluginsRequest()

    with patch("plugin_runner.plugin_runner.load_plugins", side_effect=ImportError):
        responses = []
        async for response in plugin_runner.ReloadPlugins(request, None):
            responses.append(response)

        assert len(responses) == 1
        assert responses[0].success is False
