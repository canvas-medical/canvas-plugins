from canvas_sdk.caching.plugins import get_cache
from canvas_sdk.effects import Effect
from canvas_sdk.events import EventType
from canvas_sdk.protocols import BaseProtocol


class InvalidProtocol(BaseProtocol):
    """
    You should put a helpful description of this protocol's behavior here.
    """

    # Name the event type you wish to run in response to
    RESPONDS_TO = EventType.Name(EventType.UNKNOWN)

    def compute(self) -> list[Effect]:
        """Test forbidden access to private properties."""
        cache = get_cache()
        cache._connection.clear()
        return []
