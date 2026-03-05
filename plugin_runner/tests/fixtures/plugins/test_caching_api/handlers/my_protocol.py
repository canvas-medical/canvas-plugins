from canvas_sdk.caching.plugins import get_cache
from canvas_sdk.effects import Effect, EffectType
from canvas_sdk.events import EventType
from canvas_sdk.handlers import BaseHandler


class Protocol(BaseHandler):
    """
    You should put a helpful description of this handler's behavior here.
    """

    # Name the event type you wish to run in response to
    RESPONDS_TO = EventType.Name(EventType.UNKNOWN)

    def compute(self) -> list[Effect]:
        """Test that the plugin successfully sets and gets a key-value pair in the cache."""
        cache = get_cache()
        cache.set("foo", "bar")
        return [Effect(type=EffectType.LOG, payload=cache.get("foo"))]
