from canvas_sdk.effects import Effect
from canvas_sdk.effects.launch_modal import LaunchModalEffect
from canvas_sdk.handlers.action_button import ActionButton


class HelloWorldButton(ActionButton):
    """A simple button that shows a hello world message."""

    BUTTON_TITLE = "Hello World"
    BUTTON_KEY = "hello_world_button"
    BUTTON_LOCATION = ActionButton.ButtonLocation.NOTE_HEADER
    PRIORITY = 1

    def handle(self) -> list[Effect]:
        """Handle button click by showing hello world UI."""
        return [
            LaunchModalEffect(
                content="<h1>Hello World!</h1><p>This is a simple Canvas plugin UI.</p>",
                target=LaunchModalEffect.TargetType.RIGHT_CHART_PANE,
                title="Hello World",
            ).apply()
        ]
