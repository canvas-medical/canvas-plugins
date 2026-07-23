"""Example settings page registered under /set-up/fasting_program/.

This handler responds to home-app's INSTANCE_CONFIG__GET_SETTINGS_PAGE event
and returns a SettingsPageForm describing the section. The home-app renderer
will display it under the Clinical category in the /set-up/ sidebar.
"""

from canvas_sdk.effects.form import FormField, InputType
from canvas_sdk.effects.settings_page_form import SettingsPageForm
from canvas_sdk.handlers.settings_page import SettingsPageHandler


class FastingProgramSettings(SettingsPageHandler):
    """Customer-configurable parameters for the fasting protocol."""

    SECTION_KEY = "fasting_program"
    SECTION_TITLE = "Fasting Program"
    SECTION_CATEGORY = "Clinical"
    SECTION_DESCRIPTION = (
        "Customer-configurable parameters for the fasting protocol. "
        "Changes take effect on the next protocol evaluation."
    )

    def render(self) -> SettingsPageForm:
        """Build the settings form rendered under /set-up/fasting_program/."""
        return SettingsPageForm(
            section_key=self.SECTION_KEY,
            title=self.SECTION_TITLE,
            category=self.SECTION_CATEGORY,
            description=self.SECTION_DESCRIPTION,
            form_fields=[
                FormField(
                    key="fasting_hours",
                    label="Fasting Window (hours)",
                    type=InputType.NUMBER,
                    required=True,
                    min_value=8,
                    max_value=24,
                    value=16,
                    group="Protocol Parameters",
                    help_text="The fasting window assigned to a patient when the protocol fires.",
                ),
                FormField(
                    key="signoff_roles",
                    label="Roles Authorized to Sign Off",
                    type=InputType.CHECKLIST_PICKER,
                    options=["MD", "NP", "RN"],
                    value=["MD", "NP"],
                    group="Authorization",
                    help_text="Only staff with one of these roles can mark the protocol complete.",
                ),
                FormField(
                    key="responsibilities",
                    label="Active Responsibilities",
                    type=InputType.TOGGLE_CARDS,
                    options=[
                        "POPULATION_HEALTH_CAMPAIGN_OUTREACH",
                        "COMMUNICATE_DIAGNOSTIC_RESULTS_TO_PATIENT",
                    ],
                    group="Authorization",
                ),
                FormField(
                    key="accent_color",
                    label="Patient-facing Accent Color",
                    type=InputType.COLOR_PICKER,
                    value="#01A4FF",
                    group="Branding",
                ),
                FormField(
                    key="reminder_window_hours",
                    label="Reminder Lead Time (hours)",
                    type=InputType.NUMBER,
                    min_value=1,
                    max_value=72,
                    value=24,
                    group="Patient Experience",
                ),
                FormField(
                    key="patient_email_subject",
                    label="Patient Reminder Subject Line",
                    type=InputType.TEXT,
                    placeholder="Don't forget your fast tomorrow!",
                    group="Patient Experience",
                ),
                FormField(
                    key="rollout_phase",
                    label="Rollout Phase",
                    type=InputType.STATUS_BADGE,
                    value="Beta",
                    editable=False,
                    group="Metadata",
                ),
                FormField(
                    key="program_key",
                    label="Program Key",
                    type=InputType.KEY_PILL,
                    value="FAST-2026",
                    editable=False,
                    group="Metadata",
                ),
            ],
            audit_footer="Last saved by the Fasting Program plugin",
        )
