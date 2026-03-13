from canvas_sdk.effects import Effect, EffectType
from canvas_sdk.events import EventType
from canvas_sdk.handlers import BaseHandler


class Handler(BaseHandler):
    """
    You should put a helpful description of this handler's behavior here.
    """

    # Name the event type you wish to run in response to
    RESPONDS_TO = EventType.Name(EventType.UNKNOWN)

    NARRATIVE_STRING = "I was inserted from my plugin's handler."

    def compute(self) -> list[Effect]:
        """This method gets called when an event of the type RESPONDS_TO is fired."""
        return [Effect(type=EffectType.LOG, payload="Hello, world!")]
