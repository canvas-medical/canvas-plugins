from canvas_sdk.effects import Effect
from canvas_sdk.effects.widgets import PortalWidget
from canvas_sdk.events import EventType
from canvas_sdk.handlers.base import BaseHandler
from canvas_sdk.templates import render_to_string
from canvas_sdk.v1.data.care_team import CareTeamMembership, CareTeamMembershipStatus


# Inherit from BaseHandler to properly get registered for events
class CareTeamWidgetHandler(BaseHandler):
    """The CareTeamWidgetHandler class is responsible for handling the care team widget event."""

    # Name the event type you wish to run in response to
    RESPONDS_TO = EventType.Name(EventType.PATIENT_PORTAL__WIDGET_CONFIGURATION)

    def compute(self) -> list[Effect]:
        """This method gets called when an event of the type RESPONDS_TO is fired."""
        patient_care_team = CareTeamMembership.objects.values(
            "staff__first_name",
            "staff__last_name",
            "staff__prefix",
            "staff__suffix",
            "staff__photos__url",
            "role_display",
        ).filter(
            patient__id=self.target,
            status=CareTeamMembershipStatus.ACTIVE,
        )

        care_team = []
        for member in patient_care_team:
            # Aliasing the member's name components for clarity
            name = f"{member['staff__first_name']} {member['staff__last_name']}"
            prefixed_name = f"{member['staff__prefix']} " if member['staff__prefix'] else "" + f"{name}"
            professional_name = f"{prefixed_name}, {member['staff__suffix']}" if member['staff__suffix'] else prefixed_name
            photo_url = member['staff__photos__url']
            role = member['role_display']

            care_team.append(
                {
                    "name": name,
                    "prefixed_name": prefixed_name,
                    "professional_name": professional_name,
                    "photo_url": photo_url,
                    "role": role,
                }
            )

        payload = {
            "care_team": care_team,
        }

        care_team_widget = PortalWidget(
            content=render_to_string("care_team_widget.html", payload),
            size=PortalWidget.Size.COMPACT,
            priority=11,
        )

        return [
            care_team_widget.apply(),
        ]
