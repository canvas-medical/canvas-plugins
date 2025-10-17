from canvas_sdk.effects import Effect
from canvas_sdk.effects.launch_modal import LaunchModalEffect
from canvas_sdk.handlers.application import Application
from logger import log


class CcmatApp(Application):
    """An embeddable application that can be registered to Canvas."""

    def on_open(self) -> Effect:
        """Handle the on_open event."""
        # Implement this method to handle the application on_open event.
        patient_id = self.event.context.get("patient", {}).get("id", None)

        return LaunchModalEffect(
            title="Chronic Care Management Activity Tracker",
            url=f"/plugin-io/api/chronic_care_management_activity_tracker/{patient_id}/app",
            target=LaunchModalEffect.TargetType.RIGHT_CHART_PANE,
        ).apply()

    def on_context_change(self) -> Effect | None:
        """Handle the on_context_change event."""
        # Implement this method to handle the application on_context_change event.

        current_url = self.event.context.get("url", "")

        if "patient" in current_url:
            # Context has changed to a patient
            patient_id = self.event.context.get("patient", {}).get("id")
            # You can perform actions based on the new patient context here
            # For example, log the patient ID or update internal state
            log.info(f"Context changed to patient with ID: {patient_id}")

        return None
