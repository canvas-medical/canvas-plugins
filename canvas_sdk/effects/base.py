import functools
import inspect
import json
from collections.abc import Callable
from typing import Any

from pydantic import NonNegativeInt

from canvas_sdk.base import Model
from canvas_sdk.effects import Effect, EffectType

_DELAY_PARAM = inspect.Parameter(
    "delay_seconds",
    inspect.Parameter.KEYWORD_ONLY,
    default=None,
    annotation="NonNegativeInt | None",
)

_DELAY_SECONDS_DOC = (
    "\n\nArgs:\n    delay_seconds (int | None): Optional number of seconds to delay the effect.\n"
)


def async_effect(func: Callable[..., Effect]) -> Callable[..., Effect]:
    """Add a `delay_seconds` keyword argument to a method that returns an Effect.

    The wrapped method returns a plain Effect. This decorator:
    - Injects `delay_seconds` as a keyword-only argument on the public signature.
    - Validates it is non-negative (raises ValueError otherwise).
    - Sets it on the returned Effect when provided.
    """

    @functools.wraps(func)
    def wrapper(*args: Any, delay_seconds: NonNegativeInt | None = None, **kwargs: Any) -> Effect:
        if delay_seconds is not None and delay_seconds < 0:
            raise ValueError(f"delay_seconds must be non-negative, got {delay_seconds}")
        effect = func(*args, **kwargs)
        if delay_seconds is not None:
            effect.delay_seconds = delay_seconds
        return effect

    sig = inspect.signature(func)
    params = list(sig.parameters.values())
    insert_idx = len(params)
    for i, p in enumerate(params):
        if p.kind == inspect.Parameter.VAR_KEYWORD:
            insert_idx = i
            break
    params.insert(insert_idx, _DELAY_PARAM)
    wrapper.__signature__ = sig.replace(parameters=params)  # type: ignore[attr-defined]

    wrapper.__doc__ = (wrapper.__doc__ or "").rstrip() + _DELAY_SECONDS_DOC

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

    @async_effect
    def apply(self) -> Effect:
        self._validate_before_effect("apply")
        return Effect(type=self.Meta.effect_type, payload=json.dumps(self.effect_payload))


__exports__ = (
    "_BaseEffect",
    # Not defined here but used in a current plugin
    "EffectType",
)
