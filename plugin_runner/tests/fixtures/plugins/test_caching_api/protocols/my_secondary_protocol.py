from test_caching_api.wrapper import WrappedCache, wrapped_get_cache

from canvas_sdk.effects import Effect, EffectType
from canvas_sdk.events import EventType
from canvas_sdk.protocols import BaseProtocol


class Protocol(BaseProtocol):
    """
    You should put a helpful description of this protocol's behavior here.
    """

    # Name the event type you wish to run in response to
    RESPONDS_TO = EventType.Name(EventType.UNKNOWN)

    def compute(self) -> list[Effect]:
        """Test that the plugin successfully sets and gets a key-value pair in the cache."""
        cache = wrapped_get_cache()
        cache.set("foo2", "bar2")

        WrappedCache.set("foo3", "bar3")

        payload = f"{cache.get('foo2')}{WrappedCache.get('foo3')}"

        return [
            Effect(
                type=EffectType.LOG,
                payload=payload,
            )
        ]
