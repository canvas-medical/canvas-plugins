import json
from typing import Any

from canvas_sdk.base import Model
from canvas_sdk.effects import Effect, EffectType


class _BaseEffect(Model):
    """
    A Canvas Effect that changes user behavior or autonomously performs activities on behalf of users.
    """

    patient_filter: dict | None = None

    class Meta:
        effect_type = EffectType.UNKNOWN_EFFECT

    @property
    def values(self) -> dict[str, Any]:
        return {}

    @property
    def effect_payload(self) -> dict[str, Any]:
        return {"data": self.values}

    def apply(self) -> Effect:
        self._validate_before_effect("apply")
        return Effect(type=self.Meta.effect_type, payload=json.dumps(self.effect_payload))


__exports__ = (
    "_BaseEffect",
    # Not defined here but used in a current plugin
    "EffectType",
)
