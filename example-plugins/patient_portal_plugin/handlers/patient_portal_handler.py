from canvas_sdk.effects import Effect
from canvas_sdk.effects.widgets import PortalWidget
from canvas_sdk.events import EventType
from canvas_sdk.handlers.base import BaseHandler
from canvas_sdk.templates import render_to_string
from canvas_sdk.v1.data import Patient


# Inherit from BaseHandler to properly get registered for events
class PatientPortalHandler(BaseHandler):
    """Handler responsible for rendering a patient portal widgets."""

    RESPONDS_TO = EventType.Name(EventType.PATIENT_PORTAL__WIDGET_CONFIGURATION)

    BACKGROUND_COLOR = "#17634d"  # Default background color if not set in secrets

    def compute(self) -> list[Effect]:
        """This method gets called when an event of the type RESPONDS_TO is fired."""
        # Get the patient needed fields to generate the preferred full name
        patient = Patient.objects.only("first_name", "last_name", "suffix", "nickname").get(id=self.target)
        # Get the background color from secrets, defaulting to a specific color if not set
        background_color = self.secrets.get("BACKGROUND_COLOR") or self.BACKGROUND_COLOR

        payload = {
            "preferred_full_name": patient.preferred_full_name,
            "background_color": background_color,
        }

        header_widget = PortalWidget(
            content=render_to_string("templates/header_widget.html", payload),
            size=PortalWidget.Size.EXPANDED,
            priority=10,
        )

        return [header_widget.apply()]
