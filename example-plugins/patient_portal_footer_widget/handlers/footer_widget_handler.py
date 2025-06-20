from canvas_sdk.effects import Effect
from canvas_sdk.effects.widgets import PortalWidget
from canvas_sdk.events import EventType
from canvas_sdk.handlers.base import BaseHandler
from canvas_sdk.templates import render_to_string


# Inherit from BaseHandler to properly get registered for events
class FooterWidgetHandler(BaseHandler):
    """The FooterWidgetHandler class is responsible for handling the footer widget event in the patient portal."""

    # Name the event type you wish to run in response to
    RESPONDS_TO = EventType.Name(EventType.PATIENT_PORTAL__WIDGET_CONFIGURATION)

    def compute(self) -> list[Effect]:
        """This method gets called when an event of the type RESPONDS_TO is fired."""
        return [
            PortalWidget(
                content=render_to_string("footer_widget.html"),
                size=PortalWidget.Size.EXPANDED,
                priority=12,
            ).apply(),
        ]
