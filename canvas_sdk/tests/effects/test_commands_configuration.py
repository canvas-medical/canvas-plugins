from canvas_sdk.commands.commands.html_command import HtmlCommand
from canvas_sdk.commands.constants import CommandChartSection
from canvas_sdk.effects import EffectType
from canvas_sdk.effects.commands_configuration import CommandsConfiguration


def test_commands_configuration_with_empty_list() -> None:
    """Test CommandsConfiguration with an empty commands list."""
    config = CommandsConfiguration(commands=[])
    payload = config.apply()
    assert payload.type == EffectType.COMMANDS_CONFIGURATION
    assert payload.payload == '{"data": {"commands": []}}'


def test_commands_configuration_with_single_html_command() -> None:
    """Test CommandsConfiguration with a single HTML command."""
    html_command = HtmlCommand()
    command_config = html_command.configure(
        label="Custom HTML Command",
        section=CommandChartSection.PLAN,
    )
    config = CommandsConfiguration(commands=[command_config])
    payload = config.apply()
    assert payload.type == EffectType.COMMANDS_CONFIGURATION
    assert (
        payload.payload
        == '{"data": {"commands": [{"key": "htmlCommand", "label": "Custom HTML Command", "section": "plan"}]}}'
    )


def test_commands_configuration_values_property() -> None:
    """Test that the values property returns the correct structure."""
    html_command = HtmlCommand()
    command_config = html_command.configure(
        label="Test Command",
        section=CommandChartSection.PLAN,
    )
    config = CommandsConfiguration(commands=[command_config])
    values = config.values
    assert values == {"commands": [command_config]}
    assert "commands" in values
    assert len(values["commands"]) == 1
    assert values["commands"][0]["key"] == "htmlCommand"
    assert values["commands"][0]["label"] == "Test Command"
    assert values["commands"][0]["section"] == "plan"
