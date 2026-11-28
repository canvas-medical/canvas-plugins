from typing import Any

from canvas_sdk.effects.base import EffectType, _BaseEffect


class FieldActionValue(_BaseEffect):
    """An Effect that supplies the value a command field action fills into its field.

    Return it from a handler for the ``COMMAND__FIELD_ACTION__VALUE`` event. The event
    target is the command's id, and the context names the action being resolved:

    * ``schema_key``: the command's schema key, such as ``"prescribe"``
    * ``field``: the field the action fills, such as ``"sig"``
    * ``action``: the action's name, such as ``"standard_sig"``
    * ``fields``: the command's current field values

    A ``value`` of ``None`` means the action has no value to fill.

    Example:
        if self.event.context["action"] == "standard_sig":
            return [FieldActionValue(value="Take 1 tablet by mouth daily").apply()]
    """

    class Meta:
        effect_type = EffectType.FIELD_ACTION_VALUE

    value: str | None

    @property
    def values(self) -> dict[str, Any]:
        """The value to fill into the field."""
        return {"value": self.value}


__exports__ = ("FieldActionValue",)
