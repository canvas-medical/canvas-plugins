import json
from typing import Any

from pydantic import BaseModel, ConfigDict

from canvas_sdk.effects import Effect, EffectType


class _BaseEffect(BaseModel):
    """
    A Canvas Effect that changes user behavior or autonomously performs activities on behalf of users.
    """

    class Meta:
        effect_type = EffectType.UNKNOWN_EFFECT

    model_config = ConfigDict(strict=True, validate_assignment=True)

    @property
    def values(self) -> dict[str, Any]:
        return {}

    @property
    def effect_payload(self) -> dict[str, Any]:
        return {"data": self.values}

    def apply(self) -> Effect:
        return Effect(type=self.Meta.effect_type, payload=json.dumps(self.effect_payload))
