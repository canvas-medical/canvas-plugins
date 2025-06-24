from canvas_sdk.effects import Effect
from canvas_sdk.effects.widgets import PortalWidget
from canvas_sdk.events import EventType
from canvas_sdk.handlers.base import BaseHandler
from canvas_sdk.templates import render_to_string
from canvas_sdk.v1.data import Patient
from canvas_sdk.v1.data.care_team import CareTeamMembership, CareTeamMembershipStatus


# Inherit from BaseHandler to properly get registered for events
class PatientPortalHandler(BaseHandler):
    """Handler responsible for rendering a patient portal widgets."""

    RESPONDS_TO = EventType.Name(EventType.PATIENT_PORTAL__WIDGET_CONFIGURATION)

    BACKGROUND_COLOR = "#17634d"  # Default background color if not set in secrets

    def compute(self) -> list[Effect]:
        """This method gets called when an event of the type RESPONDS_TO is fired."""
        return [
            self._create_header_widget(),
            self._create_care_team_widget()
        ]

    def _create_header_widget(self) -> Effect:
        """Constructs the header widget for the patient portal."""
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

        return header_widget.apply()

    def _create_care_team_widget(self) -> Effect:
        """Constructs the care team widget for the patient portal."""
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

        # Get the background color from secrets, defaulting to a specific color if not set
        title_color = self.secrets.get("BACKGROUND_COLOR") or self.BACKGROUND_COLOR

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
            "title_color": title_color,
        }

        care_team_widget = PortalWidget(
            content=render_to_string("templates/care_team_widget.html", payload),
            size=PortalWidget.Size.COMPACT,
            priority=11,
        )

        return care_team_widget.apply()
