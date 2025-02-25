from collections.abc import Generator
from datetime import datetime
from typing import cast

import pytest

import settings
from canvas_sdk.commands.tests.test_utils import (
    COMMANDS,
    MaskedValue,
    clean_up_files_and_plugins,
    create_new_note,
    get_original_note_body_commands,
    get_token,
    install_plugin,
    trigger_plugin_event,
    wait_for_log,
    write_protocol_code,
)


@pytest.fixture(scope="session")
def token() -> MaskedValue:
    """Get a valid token."""
    return get_token()


@pytest.fixture(scope="session")
def new_note(token: MaskedValue) -> dict:
    """Create a new note."""
    return create_new_note(token)


@pytest.fixture(scope="session")
def plugin_name() -> str:
    """The plugin name to be used."""
    return f"commands{datetime.now().timestamp()}".replace(".", "")


@pytest.fixture(scope="session")
def write_and_install_protocol_and_clean_up(
    plugin_name: str, token: MaskedValue, new_note: dict
) -> Generator[None, None, None]:
    """Write the protocol code, install the plugin, and clean up after the test."""
    write_protocol_code(new_note["externallyExposableId"], plugin_name, COMMANDS)
    message_received_event, thread, ws = wait_for_log(
        cast(str, settings.INTEGRATION_TEST_URL),
        token.value,
        f"Loading plugin '{plugin_name}",
    )
    install_plugin(plugin_name, token)
    message_received_event.wait(timeout=15.0)

    # unfortunately sometimes the log websocket just doesn't return any
    # messages, so asserting on the state of the timeout here causes failures
    # even though the delay itself will cause the waiting test to pass (because
    # the plugin has been loaded).
    # timeout_not_hit = message_received_event.wait(timeout=15.0)
    # if not timeout_not_hit:
    #     ws.close()
    # assert timeout_not_hit, f"plugin loading message timeout hit: Loading plugin '{plugin_name}"

    yield

    ws.close()
    thread.join()
    clean_up_files_and_plugins(plugin_name, token)


@pytest.mark.integtest
def test_protocol_that_inserts_every_command(
    write_and_install_protocol_and_clean_up: None, token: MaskedValue, new_note: dict
) -> None:
    """Test that the protocol inserts every command."""
    trigger_plugin_event(token)

    commands_in_body = get_original_note_body_commands(new_note["id"], token)

    # TODO: Temporary workaround to ignore the updateGoal command until the integration test instance is fixed.
    command_keys = [c.Meta.key for c in COMMANDS]
    assert len(command_keys) == len(commands_in_body)
    for i, command_key in enumerate(command_keys):
        assert commands_in_body[i] == command_key
