import pytest

from canvas_sdk.test_utils.factories import (
    CanvasUserFactory,
    CustomCommandFactory,
    PluginCommandFactory,
)
from canvas_sdk.v1.data.command import Command
from canvas_sdk.v1.data.custom_command import CustomCommand


def _anchor_command(custom_command: CustomCommand, schema_key: str) -> Command:
    """Create the Command that anchors ``custom_command``, carrying ``schema_key``.

    ``anchor_object_type`` mirrors the view, which sources it from the anchor's
    ``django_content_type.model`` — the lowercased model name.
    """
    return Command.objects.create(
        note=custom_command.note,
        patient=custom_command.patient,
        schema_key=schema_key,
        data={},
        state="staged",
        origination_source="ui",
        anchor_object_type="customcommand",
        anchor_object_dbid=custom_command.dbid,
    )


@pytest.mark.django_db
def test_committed_filters_and_links_to_patient() -> None:
    """committed() returns only committed, non-EIE rows, reachable via patient.custom_commands."""
    committer = CanvasUserFactory.create()
    committed = CustomCommandFactory.create(committer=committer)
    CustomCommandFactory.create(committer=None)
    CustomCommandFactory.create(committer=committer, entered_in_error=CanvasUserFactory.create())

    assert set(CustomCommand.objects.committed()) == {committed}
    assert list(committed.patient.custom_commands.all()) == [committed]


@pytest.mark.django_db
def test_plugin_command_resolves_via_schema_key() -> None:
    """plugin_command returns the PluginCommand whose schema_key matches the anchoring command."""
    plugin_command = PluginCommandFactory.create(schema_key="my_plugin_command")
    custom_command = CustomCommandFactory.create()
    _anchor_command(custom_command, schema_key="my_plugin_command")

    assert custom_command.plugin_command == plugin_command


@pytest.mark.django_db
def test_plugin_command_is_none_without_a_match() -> None:
    """plugin_command is None with no anchoring command, or when no registration matches."""
    assert CustomCommandFactory.create().plugin_command is None

    PluginCommandFactory.create(schema_key="registered")
    orphan = CustomCommandFactory.create()
    _anchor_command(orphan, schema_key="not_registered")

    assert orphan.plugin_command is None
