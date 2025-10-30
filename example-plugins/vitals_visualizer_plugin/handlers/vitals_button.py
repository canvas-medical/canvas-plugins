from canvas_sdk.effects import Effect
from canvas_sdk.effects.launch_modal import LaunchModalEffect
from canvas_sdk.handlers.action_button import ActionButton


class VitalsVisualizerButton(ActionButton):
    """A button that opens the vitals visualization modal."""

    BUTTON_TITLE = "Visualize"
    BUTTON_KEY = "vitals_visualizer_button"
    BUTTON_LOCATION = ActionButton.ButtonLocation.CHART_SUMMARY_VITALS_SECTION
    PRIORITY = 1

    def handle(self) -> list[Effect]:
        """Handle button click by opening vitals visualization modal."""
        # The API endpoint will be at /plugin-io/api/vitals_visualizer_plugin/visualize
        # We need to pass the patient ID in the URL
        patient_id = self.target

        return [
            LaunchModalEffect(
                url=f"/plugin-io/api/vitals_visualizer_plugin/visualize?patient_id={patient_id}",
                target=LaunchModalEffect.TargetType.RIGHT_CHART_PANE_LARGE,
                title="Vitals Visualization",
            ).apply()
        ]
