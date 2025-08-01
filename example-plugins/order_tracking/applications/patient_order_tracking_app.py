from canvas_sdk.effects import Effect
from canvas_sdk.effects.launch_modal import LaunchModalEffect
from canvas_sdk.handlers.application import Application
from canvas_sdk.templates import render_to_string


class PatientOrderTrackingApplication(Application):
    """An embeddable application that can be registered to Canvas."""

    def on_open(self) -> Effect:
        return LaunchModalEffect(
            target=LaunchModalEffect.TargetType.RIGHT_CHART_PANE,
            content=render_to_string("templates/patient_worklist_orders.html"),
        ).apply()