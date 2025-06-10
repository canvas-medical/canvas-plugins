import importlib
import random
import string
import typing
from pathlib import Path

import pytest

import settings
from canvas_sdk.events import Event, EventRequest, EventType
from plugin_runner.plugin_runner import LOADED_PLUGINS

if typing.TYPE_CHECKING:
    from typing import Any

    from pytest_mock import MockerFixture


@pytest.fixture
def mock_plugin_caller(
    mocker: "MockerFixture", request: "Any"
) -> typing.Generator[str, None, None]:
    """A fixture that mocks plugin_only decorator.
    It generates a random plugin name and patches the plugin_only to simulate plugin behavior.
    """
    plugin_name = "".join(random.choice(string.ascii_lowercase) for i in range(10))

    def patched_plugin_only(
        func: typing.Callable[..., typing.Any],
    ) -> typing.Callable[..., typing.Any]:
        """A mock decorator to simulate plugin-only behavior."""

        def wrapper(*args: typing.Any, **kwargs: typing.Any) -> typing.Any:
            kwargs["plugin_name"] = plugin_name

            return func(*args, **kwargs)

        return wrapper

    mocker.patch("canvas_sdk.utils.plugins.plugin_only", side_effect=patched_plugin_only)

    import canvas_sdk.caching.plugins

    # Reload the canvas_sdk.caching.plugins module to apply the mock
    importlib.reload(canvas_sdk.caching.plugins)

    yield plugin_name
    # Cleanup: Unpatch the plugin_only decorator after the test
    mocker.stopall()
    importlib.reload(canvas_sdk.caching.plugins)


def test_get_cache_returns_the_correct_cache_client(
    mock_plugin_caller: str,
    mocker: "MockerFixture",
) -> None:
    """Test that get_cache returns the correct cache client."""
    from canvas_sdk.caching.plugins import get_cache

    mock_get_cache_client = mocker.patch("canvas_sdk.caching.plugins.get_cache_client")

    result = get_cache()

    mock_get_cache_client.assert_called_once_with(
        "plugins", mock_plugin_caller, settings.CANVAS_SDK_CACHE_TIMEOUT_SECONDS
    )

    # Assert that the result is the same as the mocked cache client
    assert result == mock_get_cache_client.return_value


@pytest.mark.parametrize("install_test_plugin", ["test_caching_api"], indirect=True)
def test_plugin_successfully_sets_gets_key_value_in_cache(
    install_test_plugin: Path, load_test_plugins: None
) -> None:
    """Test that the plugin successfully sets and gets a key-value pair in the cache."""
    plugin = LOADED_PLUGINS["test_caching_api:test_caching_api.protocols.my_protocol:Protocol"]
    effects = plugin["class"](Event(EventRequest(type=EventType.UNKNOWN))).compute()

    assert effects[0].payload == "bar"


@pytest.mark.parametrize("install_test_plugin", ["test_caching_api"], indirect=True)
def test_plugin_access_to_private_properties_cache_is_forbidden(
    install_test_plugin: Path, load_test_plugins: None
) -> None:
    """Test that plugin access to private properties of the cache api is forbidden."""
    assert (
        "test_caching_api:test_caching_api.protocols.my_protocol:ForbiddenProtocol"
        not in LOADED_PLUGINS
    )


@pytest.mark.parametrize("install_test_plugin", ["test_caching_api"], indirect=True)
def test_plugin_import_cache_from_other_modules_within_plugin(
    install_test_plugin: Path, load_test_plugins: None
) -> None:
    """Test that plugin can import cache from other modules within the plugin package."""
    plugin = LOADED_PLUGINS["test_caching_api:test_caching_api.protocols.my_protocol:CacheImport"]
    effects = plugin["class"](Event(EventRequest(type=EventType.UNKNOWN))).compute()

    assert effects[0].payload == "bar"


def test_plugin_caller_name_cannot_be_set(
    mock_plugin_caller: str,
    mocker: "MockerFixture",
) -> None:
    """Test that the plugin caller name cannot be overridden."""
    from canvas_sdk.caching.plugins import get_cache

    mock_get_cache_client = mocker.patch("canvas_sdk.caching.plugins.get_cache_client")

    get_cache(plugin_name="test_plugin")

    mock_get_cache_client.assert_called_once_with(
        "plugins", mock_plugin_caller, settings.CANVAS_SDK_CACHE_TIMEOUT_SECONDS
    )
