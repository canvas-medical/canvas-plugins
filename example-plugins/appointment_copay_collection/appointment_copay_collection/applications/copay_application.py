from canvas_sdk.effects import Effect
from canvas_sdk.effects.launch_modal import LaunchModalEffect
from canvas_sdk.handlers.application import Application


class CopayApplication(Application):
    """Patient portal menu item that opens the appointment copay page."""

    def on_open(self) -> Effect:
        """Open the copay page as a full portal page."""
        return LaunchModalEffect(
            url="/plugin-io/api/appointment_copay_collection/portal/page",
            target=LaunchModalEffect.TargetType.PAGE,
        ).apply()
