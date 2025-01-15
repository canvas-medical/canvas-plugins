from canvas_sdk.effects import Effect
from canvas_sdk.effects.launch_modal import LaunchModalEffect
from canvas_sdk.handlers.application import Application


class MyApplication(Application):
    """An embeddable application that can be registered to Canvas."""

    def on_open(self) -> Effect:
        """Handle the on_open event."""
        # Implement this method to handle the application on_open event.
        return LaunchModalEffect(
            url="https://www.canvasmedical.com/extensions",
            target=LaunchModalEffect.TargetType.DEFAULT_MODAL,
        ).apply()
