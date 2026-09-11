from canvas_sdk.effects import Effect, EffectType
from canvas_sdk.events import EventType
from canvas_sdk.handlers import BaseHandler


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
