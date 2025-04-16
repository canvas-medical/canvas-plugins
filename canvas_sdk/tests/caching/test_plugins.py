from __future__ import annotations

import importlib
import random
import string
import sys
import typing
from collections.abc import Generator
from pathlib import Path
from unittest.mock import patch

import pytest

import settings
from plugin_runner.plugin_runner import LOADED_PLUGINS

if typing.TYPE_CHECKING:
    from collections.abc import Callable
    from typing import Any

    from pytest_mock import MockerFixture


@pytest.fixture
def mock_plugin_caller(mocker: MockerFixture, request: Any) -> Generator[str]:
    """A fixture that mocks plugin_only decorator.
    It generates a random plugin name and patches the plugin_only to simulate plugin behavior.
    """
    plugin_name = "".join(random.choice(string.ascii_lowercase) for _ in range(10))

    def patched_plugin_only(
        func: Callable[..., Any],
    ) -> Callable[..., Any]:
        """A mock decorator to simulate plugin-only behavior."""

        def wrapper(*args: Any, **kwargs: Any) -> Any:
            kwargs["plugin_name"] = plugin_name

            return func(*args, **kwargs)

        return wrapper

    mocker.patch("canvas_sdk.utils.plugins.plugin_only", side_effect=patched_plugin_only)

    yield plugin_name


def nuke_caching() -> None:
    """
    The sandbox adds to our test pollution by holding references to things that get mocked.
    """
    if "canvas_sdk.caching.plugins" in sys.modules:
        importlib.reload(sys.modules["canvas_sdk.caching.plugins"])

    if "canvas_sdk.caching.client" in sys.modules:
        importlib.reload(sys.modules["canvas_sdk.caching.client"])


def test_get_cache_returns_the_correct_cache_client(
    mock_plugin_caller: str,
) -> None:
    """Test that get_cache returns the correct cache client."""
    nuke_caching()

    with (
        patch("canvas_sdk.caching.client.get_cache") as get_cache_client,
        patch("canvas_sdk.caching.plugins.get_cache_client", get_cache_client),
    ):
        import canvas_sdk.caching.plugins

        result = canvas_sdk.caching.plugins.get_cache()

        get_cache_client.assert_called_once_with(
            "plugins",
            mock_plugin_caller,
            settings.CANVAS_SDK_CACHE_TIMEOUT_SECONDS,
        )

        # Assert that the result is the same as the mocked cache client
        assert result == get_cache_client.return_value

    nuke_caching()


@pytest.mark.parametrize("install_test_plugin", ["test_caching_api"], indirect=True)
def test_plugin_successfully_sets_gets_key_value_in_cache(
    install_test_plugin: Path, load_test_plugins: None
) -> None:
    """Test that the plugin successfully sets and gets a key-value pair in the cache."""
    from canvas_sdk.events import Event, EventRequest, EventType

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
