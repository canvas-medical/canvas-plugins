"""Async execution options for effects.

Plugin developers call :meth:`Effect.set_async` on a returned effect to have
the platform execute it via Celery instead of inline. Supports delay and
retries.

``set_async`` is attached to the generated protobuf :class:`Effect` class at
module import time so it can be chained off any helper that returns an
``Effect`` — e.g. ``claim.add_comment(...).set_async(delay_seconds=60)``. It
mutates the effect's payload in place and returns the same effect to enable
the chained form.
"""

import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from canvas_generated.messages.effects_pb2 import Effect as _PbEffect

    class Effect(_PbEffect):
        """Stub — runtime is the real protobuf Effect with ``set_async`` attached below."""

        def set_async(  # noqa: D102 — see attached function below for real docs
            self,
            *,
            delay_seconds: int | None = ...,
            max_retries: int | None = ...,
        ) -> "Effect": ...
else:
    from canvas_generated.messages.effects_pb2 import Effect

ASYNC_PROPS_KEY = "async_props"


def _validate_non_negative_int(name: str, value: object) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be an int, got {type(value).__name__}")
    if value < 0:
        raise ValueError(f"{name} must be non-negative, got {value}")


def set_async(  # noqa: D417 — `self` is the bound Effect instance
    self: Effect,
    *,
    delay_seconds: int | None = None,
    max_retries: int | None = None,
) -> Effect:
    """Attach async execution options to this effect.

    The platform will run the effect through Celery rather than inline. All
    async options are packed into the effect's payload under the
    ``async_props`` key, so no extra protobuf fields are needed.

    Args:
        delay_seconds: Wait this many seconds before running. ``0`` runs
            immediately on Celery (async-now). Must be non-negative.
        max_retries: Maximum number of retry attempts on failure. When
            ``None`` (the default), the key is omitted from the payload and
            the platform default applies. Pass ``0`` to explicitly disable
            retries.

    Returns:
        The same ``Effect`` with async options merged into its payload, so
        callers can chain: ``claim.add_comment(...).set_async(...)``.
    """
    if self.payload:
        try:
            payload = json.loads(self.payload)
        except json.JSONDecodeError as e:
            raise ValueError("Effect payload must be valid JSON to use set_async()") from e
    else:
        payload = {}
    props = payload.get(ASYNC_PROPS_KEY) or {}

    if delay_seconds is not None:
        _validate_non_negative_int("delay_seconds", delay_seconds)
        props["delay_seconds"] = delay_seconds

    if max_retries is not None:
        _validate_non_negative_int("max_retries", max_retries)
        props["max_retries"] = max_retries

    if props:
        payload[ASYNC_PROPS_KEY] = props
        self.payload = json.dumps(payload)
    return self


Effect.set_async = set_async  # type: ignore[method-assign]


__exports__ = ()
