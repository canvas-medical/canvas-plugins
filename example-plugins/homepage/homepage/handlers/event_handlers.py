from canvas_sdk.effects import Effect
from canvas_sdk.effects.set_default_homepage import SetDefaultHomepage
from canvas_sdk.events import EventType
from canvas_sdk.handlers import BaseHandler


class Homepage(BaseHandler):
    """Handler for homepage configuration events."""

    # Name the event type you wish to run in response to
    RESPONDS_TO = EventType.Name(EventType.HOMEPAGE_CONFIGURATION)

    def compute(self) -> list[Effect]:
        """Set the default homepage."""
        return [SetDefaultHomepage(page=SetDefaultHomepage.Pages.PATIENTS).apply()]
