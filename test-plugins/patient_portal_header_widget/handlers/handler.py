from canvas_sdk.effects.widgets import PortalWidget
from canvas_sdk.events import EventType
from canvas_sdk.handlers.base import BaseHandler
from canvas_sdk.templates import render_to_string
from canvas_sdk.v1.data import Patient
from logger import log


# Inherit from BaseHandler to properly get registered for events
class Handler(BaseHandler):
    """You should put a helpful description of this protocol's behavior here."""

    RESPONDS_TO = EventType.Name(EventType.PATIENT_PORTAL__WIDGET_CONFIGURATION)

    def compute(self):
        """This method gets called when an event of the type RESPONDS_TO is fired."""
        patient = Patient.objects.get(id=self.target)
        background_color = self.secrets["BACKGROUND_COLOR"]
        if not background_color:
            background_color = "rgb(12, 98, 72)"
        log.info(f"Patient: {patient}, Background Color: {background_color}")

        payload = {
            "patient": str(patient),
            "background_color": background_color,
        }

        header_widget = PortalWidget(
            content=render_to_string("header_widget.html", payload),
            size=PortalWidget.Size.EXPANDED,
            priority=10,
        )

        return [header_widget.apply()]
