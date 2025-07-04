from canvas_sdk.effects import Effect
from canvas_sdk.events import EventType
from canvas_sdk.protocols import BaseProtocol


class Protocol(BaseProtocol):
    """
    You should put a helpful description of this protocol's behavior here.
    """

    # Name the event type you wish to run in response to
    RESPONDS_TO = [
        EventType.Name(EventType.UNKNOWN),
        EventType.Name(EventType.PLUGIN_HANDLE_EVENT_EXCEPTION),
    ]

    def compute(self) -> list[Effect]:
        """This method gets called when an event of the type RESPONDS_TO is fired."""
        raise Exception("This is a test exception")
