from datetime import datetime
from typing import Any, Generator

import pytest

from canvas_sdk.commands.tests.test_utils import (
    COMMANDS,
    MaskedValue,
    clean_up_files_and_plugins,
    create_new_note,
    get_original_note_body_commands,
    get_token,
    install_plugin,
    trigger_plugin_event,
    write_protocol_code,
)


@pytest.fixture(scope="session")
def token() -> MaskedValue:
    return get_token()


@pytest.fixture(scope="session")
def new_note(token: MaskedValue) -> dict:
    return create_new_note(token)


@pytest.fixture(scope="session")
def plugin_name() -> str:
    return f"commands{datetime.now().timestamp()}".replace(".", "")


@pytest.fixture(scope="session")
def write_and_install_protocol_and_clean_up(
    plugin_name: str, token: MaskedValue, new_note: dict
) -> Generator[None, None, None]:
    write_protocol_code(new_note["externallyExposableId"], plugin_name, COMMANDS)
    install_plugin(plugin_name, token)

    yield

    clean_up_files_and_plugins(plugin_name, token)


@pytest.mark.integtest
def test_protocol_that_inserts_every_command(
    write_and_install_protocol_and_clean_up: None, token: MaskedValue, new_note: dict
) -> None:
    trigger_plugin_event(token)

    commands_in_body = get_original_note_body_commands(new_note["id"], token)
    command_keys = [c.Meta.key for c in COMMANDS]

    assert len(command_keys) == len(commands_in_body)
    for i, command_key in enumerate(command_keys):
        assert commands_in_body[i] == command_key
