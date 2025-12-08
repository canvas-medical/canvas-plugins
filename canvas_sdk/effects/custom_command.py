import json
from typing import Any
from uuid import UUID

from canvas_sdk.effects import Effect, EffectType, _BaseEffect


class CustomCommand(_BaseEffect):
    """Custom command effect."""

    note_uuid: str | UUID
    command_uuid: str | UUID | None
    schema_key: str
    data: dict

    @property
    def values(self) -> dict[str, Any]:
        """Command values."""
        return self.data

    def originate(self, line_number: int = -1) -> Effect:
        """Originate a new custom command in the note body."""
        return Effect(
            type=EffectType.CUSTOM_COMMAND__ORIGINATE,
            payload=json.dumps(
                {
                    "command": self.command_uuid,
                    "note": self.note_uuid,
                    "schema_key": self.schema_key,
                    "data": self.values,
                    "line_number": line_number,
                }
            ),
        )


__exports__ = ("CustomCommand",)
