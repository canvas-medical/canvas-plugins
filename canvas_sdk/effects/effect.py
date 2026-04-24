"""SDK-facing :class:`Effect` wrapper around the generated protobuf.

Plugin authors construct these via the helpers in :mod:`canvas_sdk.effects`
(``Response().apply()``, ``claim.add_comment(...)``, etc.) and return them
from handler ``compute()`` methods. At the plugin/runtime boundary, the
plugin_runner reads ``.type`` and ``.payload`` to build the wire-format
protobuf that ships over gRPC.

The wrapper exists so behaviors like :meth:`set_async` can be real methods
on a class we own, rather than attributes monkey-patched onto the generated
protobuf class.
"""

import json

from canvas_generated.messages.effects_pb2 import Effect as _PbEffect
from canvas_generated.messages.effects_pb2 import EffectType

ASYNC_PROPS_KEY = "async_props"


def _validate_non_negative_int(name: str, value: object) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be an int, got {type(value).__name__}")
    if value < 0:
        raise ValueError(f"{name} must be non-negative, got {value}")


class Effect:
    """Thin wrapper around :class:`canvas_generated.messages.effects_pb2.Effect`.

    Exposes the two fields plugin code ever touches (``type``, ``payload``)
    plus :meth:`set_async` for opting into Celery-backed execution, and
    :meth:`to_proto` for the runtime to retrieve the wire-format message.
    """

    __slots__ = ("_pb",)

    def __init__(
        self,
        type: EffectType | str = EffectType.UNKNOWN_EFFECT,
        payload: str = "",
    ) -> None:
        self._pb = _PbEffect(type=type, payload=payload)

    @property
    def type(self) -> EffectType:  # noqa: D102
        return self._pb.type

    @type.setter
    def type(self, value: EffectType) -> None:
        self._pb.type = value

    @property
    def payload(self) -> str:  # noqa: D102
        return self._pb.payload

    @payload.setter
    def payload(self, value: str) -> None:
        self._pb.payload = value

    def set_async(
        self,
        *,
        delay_seconds: int | None = None,
        max_retries: int | None = None,
    ) -> "Effect":
        """Attach async execution options to this effect.

        The platform will run the effect through Celery rather than inline.

        Args:
            delay_seconds: Wait this many seconds before running. ``0`` runs
                immediately on Celery (async-now). Must be non-negative.
            max_retries: Maximum number of retry attempts on failure. When
                ``None`` (the default), the key is omitted from the payload
                and the platform default applies. Pass ``0`` to explicitly
                disable retries.

        Returns:
            The same ``Effect`` with async options merged into its payload,
            so callers can chain: ``claim.add_comment(...).set_async(...)``.
        """
        if delay_seconds is None and max_retries is None:
            return self

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

        payload[ASYNC_PROPS_KEY] = props
        self.payload = json.dumps(payload)
        return self

    def to_proto(self) -> _PbEffect:
        """Return the underlying protobuf Effect.

        Called at the runtime/gRPC boundary to serialize the effect to its
        wire format. Plugin code should not need this.
        """
        return self._pb

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Effect):
            return self._pb == other._pb
        if isinstance(other, _PbEffect):
            return self._pb == other
        return NotImplemented

    def __repr__(self) -> str:
        return f"Effect(type={self._pb.type}, payload={self._pb.payload!r})"


__exports__ = ("Effect", "EffectType")
