from typing import Any

from canvas_generated.messages.effects_pb2 import EffectType
from canvas_sdk.effects import _BaseEffect


class BatchOriginateCommandEffect(_BaseEffect):
    """An Effect that will originate multiple commands in a batch operation."""

    class Meta:
        effect_type = EffectType.BATCH_ORIGINATE_COMMANDS

    commands: list

    @property
    def values(self) -> dict[str, Any]:
        """The BatchOriginateCommandEffect's values."""
        return {"commands": [command._originate_for_batch() for command in self.commands]}


__exports__ = ("BatchOriginateCommandEffect",)
