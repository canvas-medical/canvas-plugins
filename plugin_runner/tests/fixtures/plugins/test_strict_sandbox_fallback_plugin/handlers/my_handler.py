from canvas_sdk.effects import Effect, EffectType
from canvas_sdk.events import EventType
from canvas_sdk.handlers import BaseHandler

# Reading `mro` fails under SandboxMode.STRICT and succeeds under
# SandboxMode.LEGACY_PERMISSIVE, so this plugin loads only via the fallback path.
DICT_MRO = dict.mro


class Handler(BaseHandler):
    """A handler that only the permissive sandbox will load."""

    # Name the event type you wish to run in response to
    RESPONDS_TO = EventType.Name(EventType.UNKNOWN)

    def compute(self) -> list[Effect]:
        """This method gets called when an event of the type RESPONDS_TO is fired."""
        return [Effect(type=EffectType.LOG, payload=str(DICT_MRO))]
