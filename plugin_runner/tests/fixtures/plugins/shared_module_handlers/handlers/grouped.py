from canvas_sdk.effects import Effect, EffectType
from canvas_sdk.events import EventType
from canvas_sdk.handlers import BaseHandler

# Module-level state. Every execution of this module rebinds it to a fresh
# object, so handlers that share one execution also share this identity while
# handlers from separate executions do not.
MODULE_MARKER: dict[str, str] = {"module": "grouped"}


class AlphaHandler(BaseHandler):
    """First handler declared from the grouped module."""

    RESPONDS_TO = EventType.Name(EventType.UNKNOWN)

    def compute(self) -> list[Effect]:
        """Return a log effect naming this handler."""
        return [Effect(type=EffectType.LOG, payload="alpha")]


class BetaHandler(BaseHandler):
    """Second handler declared from the grouped module."""

    RESPONDS_TO = EventType.Name(EventType.UNKNOWN)

    def compute(self) -> list[Effect]:
        """Return a log effect naming this handler."""
        return [Effect(type=EffectType.LOG, payload="beta")]


class GammaHandler(BaseHandler):
    """Third handler declared from the grouped module."""

    RESPONDS_TO = EventType.Name(EventType.UNKNOWN)

    def compute(self) -> list[Effect]:
        """Return a log effect naming this handler."""
        return [Effect(type=EffectType.LOG, payload="gamma")]
