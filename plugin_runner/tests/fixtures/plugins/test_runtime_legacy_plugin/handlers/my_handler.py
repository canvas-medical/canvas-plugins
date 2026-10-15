from canvas_sdk.effects import Effect, EffectType
from canvas_sdk.events import EventType
from canvas_sdk.handlers import BaseHandler
from test_runtime_legacy_plugin.helpers import working_directory


class Handler(BaseHandler):
    """A handler whose helper only works under the deprecated sandbox rules."""

    # Name the event type you wish to run in response to
    RESPONDS_TO = EventType.Name(EventType.UNKNOWN)

    def compute(self) -> list[Effect]:
        """This method gets called when an event of the type RESPONDS_TO is fired."""
        return [Effect(type=EffectType.LOG, payload=working_directory())]
