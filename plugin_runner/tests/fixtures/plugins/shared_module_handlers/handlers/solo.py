from canvas_sdk.effects import Effect, EffectType
from canvas_sdk.events import EventType
from canvas_sdk.handlers import BaseHandler


class SoloHandler(BaseHandler):
    """Only handler declared from its module."""

    RESPONDS_TO = EventType.Name(EventType.UNKNOWN)

    def compute(self) -> list[Effect]:
        """Return a log effect naming this handler."""
        return [Effect(type=EffectType.LOG, payload="solo")]
