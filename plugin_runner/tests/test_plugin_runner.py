import base64
import json
import logging
import pickle
import shutil
from base64 import b64encode
from http import HTTPStatus
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, Mock, patch

import pytest

from canvas_generated.messages.effects_pb2 import Effect, EffectType
from canvas_generated.messages.plugins_pb2 import (
    ReloadPluginRequest,
    ReloadPluginsRequest,
    UnloadPluginRequest
)
from canvas_sdk.effects.payment_processor import (
    AddPaymentMethodResponse,
    CardTransaction,
    PaymentMethod,
    PaymentProcessorForm,
    PaymentProcessorMetadata,
    RemovePaymentMethodResponse,
)
from canvas_sdk.effects.simple_api import AcceptConnection, DenyConnection, Response
from canvas_sdk.events import Event, EventRequest, EventType
from plugin_runner.plugin_runner import (
    EVENT_HANDLER_MAP,
    LOADED_PLUGINS,
    PluginRunner,
    load_or_reload_plugin,
    load_plugin,
    load_plugins,
    synchronize_plugins,
    unload_plugin,
)
from settings import PLUGIN_DIRECTORY


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


@pytest.mark.parametrize("install_test_plugin", ["test_module_imports_plugin"], indirect=True)
def test_load_plugins_with_plugin_that_imports_other_modules_within_plugin_package(
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

    result = list(plugin_runner.HandleEvent(EventRequest(type=EventType.UNKNOWN), None))

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
def test_load_plugins_should_refresh_event_handler_map(
    load_test_plugins: None, install_test_plugin: Path
) -> None:
    """Test that the event handler map is refreshed when loading plugins."""
    assert EVENT_HANDLER_MAP == {}
    load_plugins()
    assert EventType.Name(EventType.UNKNOWN) in EVENT_HANDLER_MAP
    assert EVENT_HANDLER_MAP[EventType.Name(EventType.UNKNOWN)] == [
        "example_plugin:example_plugin.protocols.my_protocol:Protocol"
    ]


@pytest.mark.parametrize("install_test_plugin", ["example_plugin"], indirect=True)
@pytest.mark.parametrize("load_test_plugins", [None], indirect=True)
def test_load_plugin_should_refresh_event_handler_map(
    load_test_plugins: None, install_test_plugin: Path
) -> None:
    """Test that the event handler map is refreshed when loading a specific plugin."""
    assert EVENT_HANDLER_MAP == {}
    load_plugin(install_test_plugin)
    assert EventType.Name(EventType.UNKNOWN) in EVENT_HANDLER_MAP
    assert EVENT_HANDLER_MAP[EventType.Name(EventType.UNKNOWN)] == [
        "example_plugin:example_plugin.protocols.my_protocol:Protocol"
    ]


@pytest.mark.parametrize("install_test_plugin", ["example_plugin"], indirect=True)
def test_unload_plugin_should_remove_from_loaded_plugins(
    install_test_plugin: Path, load_test_plugins: None
) -> None:
    """Test that unloading a plugin successfully removes it from loaded plugins."""
    assert "example_plugin:example_plugin.protocols.my_protocol:Protocol" in LOADED_PLUGINS
    assert (
        LOADED_PLUGINS["example_plugin:example_plugin.protocols.my_protocol:Protocol"]["active"]
        is True
    )
    unload_plugin("example_plugin")
    assert "example_plugin:example_plugin.protocols.my_protocol:Protocol" not in LOADED_PLUGINS


@pytest.mark.parametrize("install_test_plugin", ["example_plugin"], indirect=True)
def test_unload_plugin_should_refresh_event_handler_map(
    install_test_plugin: Path, load_test_plugins: None
) -> None:
    """Test that unloading a plugin should refresh event handler map."""

    class OtherPluginHandler:
        RESPONDS_TO = EventType.Name(EventType.UNKNOWN)

    LOADED_PLUGINS["other_example_plugin:example_plugin.protocols.my_protocol:Protocol"] = {
        "active": True,
        "class": OtherPluginHandler,
        "sandbox": None,
        "handler": None,
        "secrets": {},
    }

    unload_plugin("example_plugin")
    assert (
        "example_plugin:example_plugin.protocols.my_protocol:Protocol"
        not in EVENT_HANDLER_MAP[EventType.Name(EventType.UNKNOWN)]
    )

    assert len(EVENT_HANDLER_MAP[EventType.Name(EventType.UNKNOWN)]) == 1


@pytest.mark.parametrize("install_test_plugin", ["example_plugin"], indirect=True)
def test_handle_plugin_event_returns_expected_result(
    install_test_plugin: Path, plugin_runner: PluginRunner, load_test_plugins: None
) -> None:
    """Test that HandleEvent successfully calls the relevant plugins and returns the expected result."""
    event = EventRequest(type=EventType.UNKNOWN)

    result = []
    for response in plugin_runner.HandleEvent(event, None):
        result.append(response)

    assert len(result) == 1
    assert result[0].success is True
    assert len(result[0].effects) == 1
    assert result[0].effects[0].type == EffectType.LOG
    assert result[0].effects[0].payload == "Hello, world!"


@pytest.mark.parametrize(
    "method_name, plugin_request, expected_message",
    [
        (
            "ReloadPlugins",
            ReloadPluginsRequest(),
            {"action": "reload"},
        ),
        (
            "ReloadPlugin",
            ReloadPluginRequest(plugin="test_plugin"),
            {"action": "reload", "plugin": "test_plugin"},
        ),
        (
            "UnloadPlugin",
            UnloadPluginRequest(plugin="test_plugin"),
            {"action": "unload", "plugin": "test_plugin"},
        ),
    ],
    ids=["reload_all", "reload", "unload"],
)
def test_plugin_runner_event_publishes_message(
    plugin_runner: PluginRunner,
    method_name: str,
    plugin_request: ReloadPluginRequest | ReloadPluginsRequest | UnloadPluginRequest,
    expected_message: dict,
) -> None:
    """Test plugin runner methods publish the expected message."""
    with patch(
        "plugin_runner.plugin_runner.publish_message", new_callable=Mock
    ) as mock_publish_message:
        method = getattr(plugin_runner, method_name)
        result = list(method(plugin_request, None))

        mock_publish_message.assert_called_once_with(message=expected_message)

    assert len(result) == 1
    assert result[0].success is True


def test_synchronize_plugins_calls_install_and_load_plugins() -> None:
    """Test that synchronize_plugins calls install_plugins and load_plugins."""
    with (
        patch("plugin_runner.plugin_runner.get_client", new_callable=MagicMock) as mock_get_client,
        patch(
            "plugin_runner.plugin_runner.install_plugins", new_callable=Mock
        ) as mock_install_plugins,
        patch("plugin_runner.plugin_runner.load_plugins", new_callable=Mock) as mock_load_plugins,
    ):
        mock_client = Mock()
        mock_pubsub = Mock()
        mock_get_client.return_value = (mock_client, mock_pubsub)
        mock_pubsub.get_message.return_value = {
            "type": "pmessage",
            "data": pickle.dumps({"action": "reload"}),
        }

        synchronize_plugins(run_once=True)

        mock_install_plugins.assert_called_once()
        mock_load_plugins.assert_called_once()


def test_synchronize_plugins_installs_and_loads_enabled_plugin() -> None:
    """Test that synchronize_plugins installs and loads only the given enabled plugin."""
    plugin_name = "my_enabled_plugin"

    with (
        patch("plugin_runner.plugin_runner.get_client") as mock_get_client,
        patch("plugin_runner.plugin_runner.enabled_plugins") as mock_enabled_plugins,
        patch("plugin_runner.plugin_runner.install_plugin") as mock_install_plugin,
        patch("plugin_runner.plugin_runner.load_or_reload_plugin") as mock_load_or_reload_plugin,
        patch("plugin_runner.plugin_runner.install_plugins") as mock_install_plugins,
        patch("plugin_runner.plugin_runner.load_plugins") as mock_load_plugins,
    ):
        mock_client = Mock()
        mock_pubsub = Mock()
        mock_get_client.return_value = (mock_client, mock_pubsub)
        mock_enabled_plugins.return_value = {plugin_name: {"version": "0.1.0"}}

        mock_pubsub.get_message.return_value = {
            "type": "pmessage",
            "data": pickle.dumps({"action": "reload", "plugin": plugin_name}),
        }

        synchronize_plugins(run_once=True)

        mock_install_plugin.assert_called_once_with(plugin_name, attributes={"version": "0.1.0"})

        expected_path = (Path(PLUGIN_DIRECTORY) / plugin_name).resolve()
        mock_load_or_reload_plugin.assert_called_once_with(expected_path)

        mock_install_plugins.assert_not_called()
        mock_load_plugins.assert_not_called()


def test_synchronize_plugins_uninstalls_and_unloads_disabled_plugin() -> None:
    """Test that synchronize_plugins uninstalls and unloads the given plugin if disabled."""
    plugin_name = "my_disabled_plugin"

    with (
        patch("plugin_runner.plugin_runner.get_client") as mock_get_client,
        patch("plugin_runner.plugin_runner.enabled_plugins") as mock_enabled_plugins,
        patch("plugin_runner.plugin_runner.uninstall_plugin") as mock_uninstall_plugin,
        patch("plugin_runner.plugin_runner.unload_plugin") as mock_unload_plugin,
        patch("plugin_runner.plugin_runner.install_plugins") as mock_install_plugins,
        patch("plugin_runner.plugin_runner.load_plugins") as mock_load_plugins,
    ):
        mock_client = Mock()
        mock_pubsub = Mock()
        mock_get_client.return_value = (mock_client, mock_pubsub)

        mock_enabled_plugins.return_value = {}

        mock_pubsub.get_message.return_value = {
            "type": "pmessage",
            "data": pickle.dumps({"action": "unload", "plugin": plugin_name}),
        }

        synchronize_plugins(run_once=True)

        mock_uninstall_plugin.assert_called_once_with(plugin_name)
        mock_unload_plugin.assert_called_once_with(plugin_name)

        mock_install_plugins.assert_not_called()
        mock_load_plugins.assert_not_called()


@pytest.mark.parametrize("install_test_plugin", ["test_module_imports_plugin"], indirect=True)
def test_changes_to_plugin_modules_should_be_reflected_after_reload(
    install_test_plugin: Path, load_test_plugins: None, plugin_runner: PluginRunner
) -> None:
    """Test that changes to plugin modules are reflected after reloading the plugin."""
    event = EventRequest(type=EventType.UNKNOWN)

    result = []
    for response in plugin_runner.HandleEvent(event, None):
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
    for response in plugin_runner.HandleEvent(event, None):
        result.append(response)

    assert len(result) == 1
    assert result[0].success is True
    assert len(result[0].effects) == 1
    assert result[0].effects[0].type == EffectType.LOG
    assert result[0].effects[0].payload == "Successfully changed!"


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
def test_simple_api(
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
    for response in plugin_runner.HandleEvent(event, None):
        result.append(response)

    expected_response = Response(status_code=status_code).apply()
    if status_code == HTTPStatus.OK:
        expected_response.plugin_name = "test_simple_api"
        expected_response.handler_name = "canvas_sdk.handlers.simple_api.api.SimpleAPIBase.compute"

    assert result[0].effects == [expected_response]


@pytest.mark.parametrize(
    argnames="context",
    argvalues=[
        (
            {
                "plugin_name": "test_simple_api",
                "channel_name": "test_channel",
                "headers": {},
            }
        ),
        (
            {
                "plugin_name": "unknown_plugin",
                "channel_name": "test_channel",
                "headers": {},
            }
        ),
    ],
    ids=["success", "no handlers"],
)
@pytest.mark.parametrize("install_test_plugin", ["test_simple_api"], indirect=True)
def test_simple_api_websocket(
    install_test_plugin: Path,
    load_test_plugins: None,
    plugin_runner: PluginRunner,
    context: dict[str, Any],
) -> None:
    """Test that the PluginRunner returns responses to  SimpleAPI Websocket events."""
    event = EventRequest(
        type=EventType.SIMPLE_API_WEBSOCKET_AUTHENTICATE,
        context=json.dumps(context),
    )

    result = []
    for response in plugin_runner.HandleEvent(event, None):
        result.append(response)

    expected_response = (
        AcceptConnection().apply()
        if context["plugin_name"] == "test_simple_api"
        else DenyConnection().apply()
    )
    if context["plugin_name"] == "test_simple_api":
        expected_response.plugin_name = "test_simple_api"
        expected_response.handler_name = (
            "canvas_sdk.handlers.simple_api.websocket.WebSocketAPI.compute"
        )

    assert result[0].effects == [expected_response]


@pytest.mark.parametrize(
    argnames="event_type, context, expected_responses",
    argvalues=[
        (
            EventType.REVENUE__PAYMENT_PROCESSOR__LIST,
            {},
            [
                PaymentProcessorMetadata(
                    identifier=base64.b64encode(
                        b"test_payment_processor.protocols.my_protocol:CustomPaymentProcessor"
                    ).decode("utf-8"),
                    type=PaymentProcessorMetadata.PaymentProcessorType.CARD,
                ).apply()
            ],
        ),
        (
            EventType.REVENUE__PAYMENT_PROCESSOR__SELECTED,
            {
                "identifier": base64.b64encode(
                    b"test_payment_processor.protocols.my_protocol:CustomPaymentProcessor"
                ).decode("utf-8"),
            },
            [
                PaymentProcessorForm(intent="pay", content="<form>Payment Form</form>").apply(),
                PaymentProcessorForm(
                    intent="add_card", content="<form>Add Card Form</form>"
                ).apply(),
            ],
        ),
        (
            EventType.REVENUE__PAYMENT_PROCESSOR__SELECTED,
            {
                "identifier": "unknown_processor",
            },
            [],
        ),
        (
            EventType.REVENUE__PAYMENT_PROCESSOR__CHARGE,
            {
                "identifier": base64.b64encode(
                    b"test_payment_processor.protocols.my_protocol:CustomPaymentProcessor"
                ).decode("utf-8"),
                "amount": "1.23",
                "token": "tok_123",
            },
            [CardTransaction(success=True, transaction_id="txn_123", api_response={}).apply()],
        ),
        (
            EventType.REVENUE__PAYMENT_PROCESSOR__CHARGE,
            {
                "identifier": base64.b64encode(b"unknown_processor").decode("utf-8"),
                "amount": "1.23",
                "token": "tok_123",
            },
            [],
        ),
        (
            EventType.REVENUE__PAYMENT_PROCESSOR__PAYMENT_METHODS__LIST,
            {
                "identifier": base64.b64encode(
                    b"test_payment_processor.protocols.my_protocol:CustomPaymentProcessor"
                ).decode("utf-8"),
                "patient": {
                    "id": "patient_1",
                },
            },
            [
                PaymentMethod(
                    payment_method_id="pm_1",
                    brand="Visa",
                    expiration_year=2025,
                    expiration_month=12,
                    card_holder_name="John Doe",
                    postal_code="12345",
                    card_last_four_digits="1234",
                ).apply(),
            ],
        ),
        (
            EventType.REVENUE__PAYMENT_PROCESSOR__PAYMENT_METHODS__LIST,
            {
                "identifier": base64.b64encode(b"unknown_processor").decode("utf-8"),
                "patient": {
                    "id": "patient_1",
                },
            },
            [],
        ),
        (
            EventType.REVENUE__PAYMENT_PROCESSOR__PAYMENT_METHODS__ADD,
            {
                "identifier": base64.b64encode(
                    b"test_payment_processor.protocols.my_protocol:CustomPaymentProcessor"
                ).decode("utf-8"),
                "patient": {
                    "id": "patient_1",
                },
            },
            [AddPaymentMethodResponse(success=True).apply()],
        ),
        (
            EventType.REVENUE__PAYMENT_PROCESSOR__PAYMENT_METHODS__ADD,
            {
                "identifier": base64.b64encode(b"unknown_processor").decode("utf-8"),
                "patient": {
                    "id": "patient_1",
                },
            },
            [],
        ),
        (
            EventType.REVENUE__PAYMENT_PROCESSOR__PAYMENT_METHODS__REMOVE,
            {
                "identifier": base64.b64encode(
                    b"test_payment_processor.protocols.my_protocol:CustomPaymentProcessor"
                ).decode("utf-8"),
                "patient": {
                    "id": "patient_1",
                },
            },
            [RemovePaymentMethodResponse(success=True).apply()],
        ),
        (
            EventType.REVENUE__PAYMENT_PROCESSOR__PAYMENT_METHODS__REMOVE,
            {
                "identifier": base64.b64encode(b"unknown_processor").decode("utf-8"),
                "patient": {
                    "id": "patient_1",
                },
            },
            [],
        ),
    ],
    ids=[
        "metadata-event",
        "selected-event",
        "select-event-unknown-processor",
        "charge-event",
        "charge-event-unknown-processor",
        "payment-methods-list-event",
        "payment-methods-list-event-unknown-processor",
        "add-payment-method-event",
        "add-payment-method-event-unknown-processor",
        "remove-payment-method-event",
        "remove-payment-method-event-unknown-processor",
    ],
)
@pytest.mark.parametrize("install_test_plugin", ["test_payment_processor"], indirect=True)
@patch("canvas_sdk.handlers.payment_processors.card.Patient", autospec=True)
def test_payment_processor(
    mock_patient_model: MagicMock,
    install_test_plugin: Path,
    load_test_plugins: None,
    plugin_runner: PluginRunner,
    event_type: EventType,
    context: dict[str, Any],
    expected_responses: list[Any],
) -> None:
    """Test that the PluginRunner returns responses to Payment Processor events."""
    event = EventRequest(
        type=event_type,
        context=json.dumps(context),
    )

    result = []
    for response in plugin_runner.HandleEvent(event, None):
        result.append(response)

    expected_effects = [
        Effect(
            type=expected_response.type,
            payload=expected_response.payload,
            plugin_name="test_payment_processor",
            handler_name="canvas_sdk.handlers.payment_processors.base.PaymentProcessor.compute",
        )
        for expected_response in expected_responses
    ]

    assert result[0].effects == expected_effects
