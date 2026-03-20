from canvas_sdk.effects import Effect
from canvas_sdk.events import EventType
from canvas_sdk.handlers import BaseHandler
from logger import log


class Forbidden(BaseHandler):
    """You should put a helpful description of this handler's behavior here."""

    # Name the event type you wish to run in response to
    RESPONDS_TO = EventType.Name(EventType.UNKNOWN)

    def compute(self) -> list[Effect]:
        """This method gets called when an event of the type RESPONDS_TO is fired."""
        from test_implicit_imports_plugin.utils.base import OtherClass

        OtherClass()

        return []


class Allowed(BaseHandler):
    """You should put a helpful description of this handler's behavior here."""

    RESPONDS_TO = EventType.Name(EventType.UNKNOWN)

    def compute(self) -> list[Effect]:
        """This method gets called when an event of the type RESPONDS_TO is fired."""
        from test_implicit_imports_plugin.templates import Template

        log.info(Template().render())

        return []
