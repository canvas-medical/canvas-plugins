from typing import Any

from pydantic import Field

from canvas_sdk.effects import EffectType, _BaseEffect


class BatchCommitCommandEffect(_BaseEffect):
    """An Effect that will commit multiple commands in a batch operation."""

    class Meta:
        effect_type = EffectType.BATCH_COMMIT_COMMANDS

    commands: list = Field(min_length=1)

    @property
    def values(self) -> dict[str, Any]:
        """The BatchCommitCommandEffect's values."""
        return {"commands": [command._commit_payload_for_batch() for command in self.commands]}


__exports__ = ("BatchCommitCommandEffect",)
