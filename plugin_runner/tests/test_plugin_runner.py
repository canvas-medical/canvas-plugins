import asyncio
import json
import logging
import pickle
import shutil
from base64 import b64encode
from http import HTTPStatus
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from canvas_generated.messages.effects_pb2 import EffectType
from canvas_generated.messages.plugins_pb2 import ReloadPluginsRequest
from canvas_sdk.effects.simple_api import Response
from canvas_sdk.events import Event, EventRequest, EventType
from plugin_runner.plugin_runner import (
    EVENT_HANDLER_MAP,
    LOADED_PLUGINS,
    PluginRunner,
    load_or_reload_plugin,
    load_plugins,
    synchronize_plugins,
)


@pytest.fixture
def plugin_runner() -> PluginRunner:
    """Fixture to initialize PluginRunner with mocks."""
    runner = PluginRunner()
    runner.statsd_client = MagicMock()  # type: ignore[attr-defined]
    return runner


@pytest.mark.parametrize("install_test_plugin", ["example_plugin"], indirect=True)
def test_load_plugins_with_valid_plugin(install_test_plugin: Path, load_test_plugins: None) -> None:
    """Test loading plugins with a valid plugin."""
    assert "example_plugin:example_plugin.protocols.my_protocol:Protocol" in LOADED_PLUGINS
    assert (
        LOADED_PLUGINS["example_plugin:example_plugin.protocols.my_protocol:Protocol"]["active"]
        is True
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("install_test_plugin", ["test_module_imports_plugin"], indirect=True)
async def test_load_plugins_with_plugin_that_imports_other_modules_within_plugin_package(
    install_test_plugin: Path, plugin_runner: PluginRunner, load_test_plugins: None
) -> None:
    """Test loading plugins with a valid plugin that imports other modules within the current plugin package."""
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
        async for response in plugin_runner.HandleEvent(EventRequest(type=EventType.UNKNOWN), None)
    ]

    assert len(result) == 1
    assert result[0].success is True
    assert len(result[0].effects) == 1
    assert result[0].effects[0].type == EffectType.LOG
    assert result[0].effects[0].payload == "Successfully imported!"


@pytest.mark.parametrize(
    "install_test_plugin",
    [
        "test_module_imports_outside_plugin_v1",
        "test_module_imports_outside_plugin_v2",
        "test_module_imports_outside_plugin_v3",
    ],
    indirect=True,
)
def test_load_plugins_with_plugin_that_imports_other_modules_outside_plugin_package(
    install_test_plugin: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """Test loading plugins with an invalid plugin that imports other modules outside the current plugin package."""
    with caplog.at_level(logging.ERROR):
        load_or_reload_plugin(install_test_plugin)

    assert any("Error importing module" in record.message for record in caplog.records), (
        "log.error() was not called with the expected message."
    )


@pytest.mark.parametrize(
    "install_test_plugin",
    [
        "test_module_forbidden_imports_plugin",
    ],
    indirect=True,
)
def test_load_plugins_with_plugin_that_imports_forbidden_modules(
    install_test_plugin: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """Test loading plugins with an invalid plugin that imports forbidden modules."""
    with caplog.at_level(logging.ERROR):
        load_or_reload_plugin(install_test_plugin)

    assert any("Error importing module" in record.message for record in caplog.records), (
        "log.error() was not called with the expected message."
    )


@pytest.mark.parametrize(
    "install_test_plugin",
    [
        "test_module_forbidden_imports_runtime_plugin",
    ],
    indirect=True,
)
def test_load_plugins_with_plugin_that_imports_forbidden_modules_at_runtime(
    install_test_plugin: Path,
) -> None:
    """Test loading plugins with an invalid plugin that imports forbidden modules at runtime."""
    with pytest.raises(ImportError, match="is not an allowed import."):
        load_or_reload_plugin(install_test_plugin)
        class_handler = LOADED_PLUGINS[
            "test_module_forbidden_imports_runtime_plugin:test_module_forbidden_imports_runtime_plugin.protocols.my_protocol:Protocol"
        ]["class"]
        class_handler(Event(EventRequest(type=EventType.UNKNOWN))).compute()


@pytest.mark.parametrize(
    "install_test_plugin",
    [
        "test_implicit_imports_plugin",
    ],
    indirect=True,
)
def test_plugin_that_implicitly_imports_allowed_modules(
    install_test_plugin: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """Test loading plugins with a plugin that implicitly imports allowed modules."""
    with caplog.at_level(logging.INFO):
        load_or_reload_plugin(install_test_plugin)
        class_handler = LOADED_PLUGINS[
            "test_implicit_imports_plugin:test_implicit_imports_plugin.protocols.my_protocol:Allowed"
        ]["class"]
        class_handler(Event(EventRequest(type=EventType.UNKNOWN))).compute()

    assert any("Hello, World!" in record.message for record in caplog.records), (
        "log.info() with Template.render() was not called."
    )


@pytest.mark.parametrize(
    "install_test_plugin",
    [
        "test_implicit_imports_plugin",
    ],
    indirect=True,
)
def test_plugin_that_implicitly_imports_forbidden_modules(
    install_test_plugin: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """Test loading plugins with an invalid plugin that implicitly imports forbidden modules."""
    with (
        caplog.at_level(logging.INFO),
        pytest.raises(ImportError, match="'os' is not an allowed import."),
    ):
        load_or_reload_plugin(install_test_plugin)
        class_handler = LOADED_PLUGINS[
            "test_implicit_imports_plugin:test_implicit_imports_plugin.protocols.my_protocol:Forbidden"
        ]["class"]
        class_handler(Event(EventRequest(type=EventType.UNKNOWN))).compute()

    assert any("os list dir" in record.message for record in caplog.records) is False, (
        "log.info() with os.listdir() was called."
    )


@pytest.mark.parametrize("install_test_plugin", ["example_plugin"], indirect=True)
def test_reload_plugin(install_test_plugin: Path, load_test_plugins: None) -> None:
    """Test reloading a plugin."""
    load_plugins()

    assert "example_plugin:example_plugin.protocols.my_protocol:Protocol" in LOADED_PLUGINS
    assert (
        LOADED_PLUGINS["example_plugin:example_plugin.protocols.my_protocol:Protocol"]["active"]
        is True
    )


@pytest.mark.parametrize("install_test_plugin", ["example_plugin"], indirect=True)
def test_remove_plugin_should_be_removed_from_loaded_plugins(
    install_test_plugin: Path, load_test_plugins: None
) -> None:
    """Test removing a plugin."""
    assert "example_plugin:example_plugin.protocols.my_protocol:Protocol" in LOADED_PLUGINS
    shutil.rmtree(install_test_plugin)
    load_plugins()
    assert "example_plugin:example_plugin.protocols.my_protocol:Protocol" not in LOADED_PLUGINS


@pytest.mark.parametrize("install_test_plugin", ["example_plugin"], indirect=True)
@pytest.mark.parametrize("load_test_plugins", [None], indirect=True)
def test_load_plugins_should_refresh_event_protocol_map(
    load_test_plugins: None, install_test_plugin: Path
) -> None:
    """Test that the event protocol map is refreshed when loading plugins."""
    assert EVENT_HANDLER_MAP == {}
    load_plugins()
    assert EventType.Name(EventType.UNKNOWN) in EVENT_HANDLER_MAP
    assert EVENT_HANDLER_MAP[EventType.Name(EventType.UNKNOWN)] == [
        "example_plugin:example_plugin.protocols.my_protocol:Protocol"
    ]


@pytest.mark.asyncio
@pytest.mark.parametrize("install_test_plugin", ["example_plugin"], indirect=True)
async def test_handle_plugin_event_returns_expected_result(
    install_test_plugin: Path, plugin_runner: PluginRunner, load_test_plugins: None
) -> None:
    """Test that HandleEvent successfully calls the relevant plugins and returns the expected result."""
    event = EventRequest(type=EventType.UNKNOWN)

    result = []
    async for response in plugin_runner.HandleEvent(event, None):
        result.append(response)

    assert len(result) == 1
    assert result[0].success is True
    assert len(result[0].effects) == 1
    assert result[0].effects[0].type == EffectType.LOG
    assert result[0].effects[0].payload == "Hello, world!"


@pytest.mark.asyncio
async def test_reload_plugins_event_handler_successfully_publishes_message(
    plugin_runner: PluginRunner,
) -> None:
    """Test ReloadPlugins Event handler successfully publishes a message with restart action."""
    with patch(
        "plugin_runner.plugin_runner.publish_message", new_callable=AsyncMock
    ) as mock_publish_message:
        request = ReloadPluginsRequest()

        result = []
        async for response in plugin_runner.ReloadPlugins(request, None):
            result.append(response)

        mock_publish_message.assert_called_once_with(message={"action": "reload"})

    assert len(result) == 1
    assert result[0].success is True


@pytest.mark.asyncio
async def test_synchronize_plugins_calls_install_and_load_plugins() -> None:
    """Test that synchronize_plugins calls install_plugins and load_plugins."""
    with (
        patch("plugin_runner.plugin_runner.get_client", new_callable=MagicMock) as mock_get_client,
        patch(
            "plugin_runner.plugin_runner.install_plugins", new_callable=AsyncMock
        ) as mock_install_plugins,
        patch(
            "plugin_runner.plugin_runner.load_plugins", new_callable=AsyncMock
        ) as mock_load_plugins,
    ):
        mock_client = AsyncMock()
        mock_pubsub = AsyncMock()
        mock_get_client.return_value = (mock_client, mock_pubsub)
        mock_pubsub.get_message.return_value = {
            "type": "pmessage",
            "data": pickle.dumps({"action": "reload"}),
        }

        task = asyncio.create_task(synchronize_plugins(run_once=True))
        await asyncio.sleep(0.1)  # Give some time for the coroutine to run
        task.cancel()

        mock_install_plugins.assert_called_once()
        mock_load_plugins.assert_called_once()


@pytest.mark.asyncio
@pytest.mark.parametrize("install_test_plugin", ["test_module_imports_plugin"], indirect=True)
async def test_changes_to_plugin_modules_should_be_reflected_after_reload(
    install_test_plugin: Path, load_test_plugins: None, plugin_runner: PluginRunner
) -> None:
    """Test that changes to plugin modules are reflected after reloading the plugin."""
    event = EventRequest(type=EventType.UNKNOWN)

    result = []
    async for response in plugin_runner.HandleEvent(event, None):
        result.append(response)

    assert len(result) == 1
    assert result[0].success is True
    assert len(result[0].effects) == 1
    assert result[0].effects[0].type == EffectType.LOG
    assert result[0].effects[0].payload == "Successfully imported!"

    NEW_CODE = """
def import_me() -> str:
    return "Successfully changed!"
"""
    file_path = install_test_plugin / "other_module" / "base.py"
    file_path.write_text(NEW_CODE, encoding="utf-8")

    # Reload the plugin
    load_plugins()

    result = []
    async for response in plugin_runner.HandleEvent(event, None):
        result.append(response)

    assert len(result) == 1
    assert result[0].success is True
    assert len(result[0].effects) == 1
    assert result[0].effects[0].type == EffectType.LOG
    assert result[0].effects[0].payload == "Successfully changed!"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    argnames="context,status_code",
    argvalues=[
        (
            {
                "plugin_name": "test_simple_api",
                "method": "GET",
                "path": "/route",
                "query_string": "",
                "body": b64encode(b"").decode(),
                "headers": {},
            },
            HTTPStatus.OK,
        ),
        (
            {
                "plugin_name": "test_simple_api",
                "method": "GET",
                "path": "/notfound",
                "query_string": "",
                "body": b64encode(b"").decode(),
                "headers": {},
            },
            HTTPStatus.NOT_FOUND,
        ),
        (
            {
                "plugin_name": "test_simple_api",
                "method": "GET",
                "path": "/error",
                "query_string": "",
                "body": b64encode(b"").decode(),
                "headers": {},
            },
            HTTPStatus.INTERNAL_SERVER_ERROR,
        ),
    ],
    ids=["success", "not found error", "multiple handlers error"],
)
@pytest.mark.parametrize("install_test_plugin", ["test_simple_api"], indirect=True)
async def test_simple_api(
    install_test_plugin: Path,
    load_test_plugins: None,
    plugin_runner: PluginRunner,
    context: dict[str, Any],
    status_code: HTTPStatus,
) -> None:
    """Test that the PluginRunner returns responses to SimpleAPI request events."""
    event = EventRequest(
        type=EventType.SIMPLE_API_REQUEST,
        context=json.dumps(context),
    )

    result = []
    async for response in plugin_runner.HandleEvent(event, None):
        result.append(response)

    expected_response = Response(status_code=status_code).apply()
    if status_code == HTTPStatus.OK:
        expected_response.plugin_name = "test_simple_api"

    assert result[0].effects == [expected_response]
