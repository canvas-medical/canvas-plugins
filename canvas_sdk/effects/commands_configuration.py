from typing import Any

from canvas_sdk.commands.base import CommandConfiguration
from canvas_sdk.effects import EffectType, _BaseEffect


class CommandsConfiguration(_BaseEffect):
    """An Effect that will configure the commands available.

    The commands list should contain dictionaries returned by calling the
    configure() method on command instances (e.g., HtmlCommand().configure()).
    """

    class Meta:
        effect_type = EffectType.COMMANDS_CONFIGURATION

    commands: list[CommandConfiguration] = []

    @property
    def values(self) -> dict[str, Any]:
        """The CommandsConfiguration values."""
        return {
            "commands": self.commands,
        }


__exports__ = ("CommandsConfiguration",)
