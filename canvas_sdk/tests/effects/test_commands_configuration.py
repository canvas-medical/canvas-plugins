from canvas_sdk.commands.commands.custom_command import CustomCommand
from canvas_sdk.commands.constants import CommandChartSection
from canvas_sdk.effects import EffectType
from canvas_sdk.effects.commands_configuration import CommandsConfiguration


def test_commands_configuration_with_empty_list() -> None:
    """Test CommandsConfiguration with an empty commands list."""
    config = CommandsConfiguration(commands=[])
    payload = config.apply()
    assert payload.type == EffectType.COMMANDS_CONFIGURATION
    assert payload.payload == '{"data": {"commands": []}}'


def test_commands_configuration_with_single_custom_command() -> None:
    """Test CommandsConfiguration with a single custom command."""
    custom_command = CustomCommand()
    command_config = custom_command.configure(
        label="Custom Command",
        section=CommandChartSection.PLAN,
    )
    config = CommandsConfiguration(commands=[command_config])
    payload = config.apply()
    assert payload.type == EffectType.COMMANDS_CONFIGURATION
    assert (
        payload.payload
        == '{"data": {"commands": [{"key": "customCommand", "label": "Custom Command", "section": "plan"}]}}'
    )


def test_commands_configuration_values_property() -> None:
    """Test that the values property returns the correct structure."""
    custom_command = CustomCommand()
    command_config = custom_command.configure(
        label="Test Command",
        section=CommandChartSection.PLAN,
    )
    config = CommandsConfiguration(commands=[command_config])
    values = config.values
    assert values == {"commands": [command_config]}
    assert "commands" in values
    assert len(values["commands"]) == 1
    assert values["commands"][0]["key"] == "customCommand"
    assert values["commands"][0]["label"] == "Test Command"
    assert values["commands"][0]["section"] == "plan"
