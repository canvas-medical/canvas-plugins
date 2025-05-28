from typing import Any

from canvas_sdk.effects.base import EffectType, _BaseEffect


class SnoozeProtocolCard(_BaseEffect):
    """
    An Effect that will result in the snoozing or un-snoozing of a protocol card in Canvas.
    """

    class Meta:
        effect_type = EffectType.SNOOZE_OR_UNSNOOZE_PROTOCOL_CARD
        apply_required_fields = ("patient_id", "key", "snooze_command_id")

    patient_id: str | None = None
    snooze_command_id: str | None = None
    key: str | None = None

    @property
    def effect_payload(self) -> dict[str, Any]:
        """The payload of the effect."""
        return {
            "patient": self.patient_id,
            "key": self.key,
            "data": self.values,
        }

    @property
    def values(self) -> dict[str, Any]:
        """The SnoozeProtocolCard's values."""
        return {
            "snooze_command_id": self.snooze_command_id,
        }


__exports__ = ("SnoozeProtocolCard",)
