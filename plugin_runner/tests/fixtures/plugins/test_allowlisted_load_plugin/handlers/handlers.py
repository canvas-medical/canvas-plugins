from canvas_sdk.effects import Effect, EffectType
from canvas_sdk.events import EventType
from canvas_sdk.handlers import BaseHandler
from test_allowlisted_load_plugin.helpers.display import has_precision


class PrecisionCheck(BaseHandler):
    """Runs a helper that reads an ungranted name from an allowed module."""

    RESPONDS_TO = EventType.Name(EventType.UNKNOWN)

    def compute(self) -> list[Effect]:
        """Run the helper."""
        return [Effect(type=EffectType.LOG, payload=has_precision())]
