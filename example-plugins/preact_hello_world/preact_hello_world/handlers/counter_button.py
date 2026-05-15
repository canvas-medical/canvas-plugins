from canvas_sdk.effects import Effect
from canvas_sdk.effects.launch_modal import LaunchModalEffect
from canvas_sdk.handlers.action_button import ActionButton
from canvas_sdk.templates import render_to_string


class CounterButton(ActionButton):
    """ActionButton that launches a Preact counter demo in the right chart pane."""

    BUTTON_TITLE = "Counter Demo"
    BUTTON_KEY = "COUNTER_DEMO"
    BUTTON_LOCATION = ActionButton.ButtonLocation.NOTE_HEADER

    def handle(self) -> list[Effect]:
        """Display the bundled Preact counter app in the right chart pane."""
        return [
            LaunchModalEffect(
                target=LaunchModalEffect.TargetType.RIGHT_CHART_PANE,
                content=render_to_string("templates/counter.html"),
                title="Counter Demo",
            ).apply()
        ]
