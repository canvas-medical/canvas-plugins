from canvas_sdk.effects import Effect
from canvas_sdk.effects.launch_modal import LaunchModalEffect
from canvas_sdk.handlers.application import Application


class PanelManagementApp(Application):
    """An embeddable application that can be registered to Canvas."""

    def on_open(self) -> Effect:
        """Handle the on_open event."""
        return LaunchModalEffect(
            url="/plugin-io/api/panel_management_dashboard_app/app/",
            target=LaunchModalEffect.TargetType.DEFAULT_MODAL,
        ).apply()
