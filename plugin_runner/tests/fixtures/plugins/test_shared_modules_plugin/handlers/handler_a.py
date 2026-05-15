from canvas_sdk.effects import Effect, EffectType
from canvas_sdk.events import EventType
from canvas_sdk.handlers import BaseHandler
from test_shared_modules_plugin.common_tools.constants import GREETING


class HandlerA(BaseHandler):
    """Handler A that imports from shared constants."""

    RESPONDS_TO = EventType.Name(EventType.UNKNOWN)

    def compute(self) -> list[Effect]:
        """Compute effects."""
        return [Effect(type=EffectType.LOG, payload=GREETING)]
