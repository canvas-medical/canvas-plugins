from canvas_sdk.effects import Effect
from canvas_sdk.effects.launch_modal import LaunchModelEffect
from canvas_sdk.handlers.application import Application


class MyApplication(Application):
    """An embeddable application that can be registered to Canvas."""

    def on_open(self) -> Effect:
        """Handle the on_open event."""
        # Implement this method to handle the application on_open event.
        return LaunchModelEffect(url="", target=LaunchModelEffect.TargetType.DEFAULT_MODAL).apply()
