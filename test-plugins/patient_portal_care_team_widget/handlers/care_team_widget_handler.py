from canvas_sdk.effects import Effect
from canvas_sdk.effects.widgets import PortalWidget
from canvas_sdk.events import EventType
from canvas_sdk.handlers.base import BaseHandler
from canvas_sdk.templates import render_to_string
from canvas_sdk.v1.data.care_team import CareTeamMembershipStatus
from canvas_sdk.v1.data.patient import Patient


# Inherit from BaseProtocol to properly get registered for events
class CareTeamWidgetHandler(BaseHandler):
    """The CareTeamWidgetHandler class is responsible for handling the care team widget event."""

    # Name the event type you wish to run in response to
    RESPONDS_TO = EventType.Name(EventType.PATIENT_PORTAL__WIDGET_CONFIGURATION)

    def compute(self) -> list[Effect]:
        """This method gets called when an event of the type RESPONDS_TO is fired."""
        care_team = []
        patient = Patient.objects.get(id=self.target)
        patient_care_team = patient.care_team_memberships.filter(status=CareTeamMembershipStatus.ACTIVE)

        for member in patient_care_team:
            # Prefetch the photo for each care team member
            care_team.append(
                {
                    "prefix": member.staff.prefix,
                    "suffix": member.staff.suffix,
                    "first_name": member.staff.first_name,
                    "last_name": member.staff.last_name,
                    "photo_url": member.staff.photos.first().url,
                    "role": member.role,
                }
            )

        payload = {
            "care_team": care_team,
            "patient_id": patient.id,
            "patient_name": patient.name,
        }

        care_team_widget = PortalWidget(
            content=render_to_string("templates/care_team_widget.html", payload),
            size=PortalWidget.Size.COMPACT,
            priority=11,
        )

        return [
            care_team_widget.apply(),
        ]
