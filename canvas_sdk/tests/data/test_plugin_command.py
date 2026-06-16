import uuid

import pytest

from canvas_sdk.test_utils.factories.plugin_command import PluginCommandFactory
from canvas_sdk.v1.data import PluginCommand


@pytest.mark.django_db
def test_plugin_command_exposes_uuid_id_and_registered_fields() -> None:
    """A PluginCommand is readable with a UUID id and the registered command metadata."""
    command = PluginCommandFactory.create(
        name="myCommand",
        command_key="myCommand",
        schema_key="my_command_abcd1234",
        label="My Command",
        section="plan",
    )

    fetched = PluginCommand.objects.get(dbid=command.dbid)

    assert isinstance(fetched.id, uuid.UUID)
    assert fetched.name == "myCommand"
    assert fetched.command_key == "myCommand"
    assert fetched.schema_key == "my_command_abcd1234"
    assert fetched.label == "My Command"
    assert fetched.section == "plan"
