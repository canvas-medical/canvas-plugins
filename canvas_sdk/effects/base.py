import functools
import inspect
import json
from typing import Any

from pydantic import NonNegativeInt

from canvas_sdk.base import Model
from canvas_sdk.effects import Effect, EffectType


def validate_delay_seconds(func):  # type: ignore[no-untyped-def]
    """Decorator that validates delay_seconds is non-negative at runtime."""
    sig = inspect.signature(func)
    params = list(sig.parameters)
    delay_idx = params.index("delay_seconds")

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        delay_value = kwargs.get("delay_seconds")
        if delay_value is None and len(args) > delay_idx:
            delay_value = args[delay_idx]
        if delay_value is not None and delay_value < 0:
            raise ValueError(f"delay_seconds must be non-negative, got {delay_value}")
        return func(*args, **kwargs)

    return wrapper


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

    @validate_delay_seconds
    def apply(self, delay_seconds: NonNegativeInt | None = None) -> Effect:
        self._validate_before_effect("apply")
        effect = Effect(type=self.Meta.effect_type, payload=json.dumps(self.effect_payload))
        if delay_seconds is not None:
            effect.delay_seconds = delay_seconds
        return effect


__exports__ = (
    "_BaseEffect",
    # Not defined here but used in a current plugin
    "EffectType",
)
