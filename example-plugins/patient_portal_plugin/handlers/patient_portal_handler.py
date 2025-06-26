from canvas_sdk.effects import Effect
from canvas_sdk.effects.widgets import PortalWidget
from canvas_sdk.events import EventType
from canvas_sdk.handlers.base import BaseHandler
from canvas_sdk.templates import render_to_string
from canvas_sdk.v1.data import Patient
from canvas_sdk.v1.data.care_team import CareTeamMembership, CareTeamMembershipStatus
from canvas_sdk.v1.data.medication import Medication
from logger import log


# Inherit from BaseHandler to properly get registered for events
class PatientPortalHandler(BaseHandler):
    """Handler responsible for rendering a patient portal widgets."""

    RESPONDS_TO = EventType.Name(EventType.PATIENT_PORTAL__WIDGET_CONFIGURATION)

    # Default background and title color for the portal's widgets if not provided in secrets
    DEFAULT_BACKGROUND_COLOR = "#17634d"

    # Default emergency contact number if not provided in secrets
    DEFAULT_EMERGENCY_CONTACT = "1-888-555-5555"

    def compute(self) -> list[Effect]:
        """This method gets called when an event of the type RESPONDS_TO is fired."""
        return [
            self.header_widget,
            self.care_team_widget,
            self.prescriptions_widget,
            self.footer_widget,
        ]

    @property
    def header_widget(self) -> Effect:
        """Constructs the header widget for the patient portal."""
        # Get the patient needed fields to generate the preferred full name
        patient = Patient.objects.only("first_name", "last_name", "suffix", "nickname").get(id=self.target)

        payload = {
            "preferred_full_name": patient.preferred_full_name,
            "background_color": self.background_color,
        }

        header_widget = PortalWidget(
            content=render_to_string("templates/header_widget.html", payload),
            size=PortalWidget.Size.EXPANDED,
            priority=10,
        )

        return header_widget.apply()

    @property
    def care_team_widget(self) -> Effect:
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

        care_team = []
        for member in patient_care_team:
            # Aliasing the member's name components for clarity
            name = f"{member['staff__first_name']} {member['staff__last_name']}"
            prefixed_name = f"{member['staff__prefix']} " if member['staff__prefix'] else name
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
            "title_color": self.background_color,
        }

        care_team_widget = PortalWidget(
            content=render_to_string("templates/care_team_widget.html", payload),
            size=PortalWidget.Size.COMPACT,
            priority=20,
        )

        return care_team_widget.apply()

    @property
    def prescriptions_widget(self) -> Effect:
        """Constructs the prescriptions widget for the patient portal."""
        prescriptions = Medication.objects.for_patient(self.target)
        patient = Patient.objects.get(id=self.target)
        preferred_pharmacy = patient.preferred_pharmacy
        log.info(preferred_pharmacy)

        payload = {
            "prescriptions": prescriptions,
            "preferred_pharmacy": preferred_pharmacy,
            "title_color": self.background_color,
        }

        prescriptions_widget = PortalWidget(
            content=render_to_string("templates/prescriptions_widget.html", payload),
            size=PortalWidget.Size.MEDIUM,
            priority=21,
        )

        return prescriptions_widget.apply()

    @property
    def footer_widget(self) -> Effect:
        """This method gets called when an event of the type RESPONDS_TO is fired."""
        return PortalWidget(
            content=render_to_string("templates/footer_widget.html", {
                "background_color": self.background_color,
                "emergency_contact": self.emergency_contact,
            }),
            size=PortalWidget.Size.EXPANDED,
            priority=30,
        ).apply()

    @property
    def background_color(self) -> str:
        """Get the background color from secrets, defaulting to a specific color if not set."""
        return self.secrets.get("BACKGROUND_COLOR") or self.DEFAULT_BACKGROUND_COLOR

    @property
    def emergency_contact(self) -> str:
        """Get the emergency contact from secrets, defaulting to a specific contact if not set."""
        return self.secrets.get("EMERGENCY_CONTACT") or self.DEFAULT_EMERGENCY_CONTACT
