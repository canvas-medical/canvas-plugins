from canvas_sdk.effects import Effect
from canvas_sdk.effects.launch_modal import LaunchModalEffect
from canvas_sdk.handlers.application import Application
from canvas_sdk.templates import render_to_string


class NoteRestrictionDashboard(Application):
    """Global dashboard to view and manage note access restrictions."""

    def on_open(self) -> Effect:
        """Render and open the Note Access Dashboard as a full-page modal."""
        return LaunchModalEffect(
            content=render_to_string("templates/note_restriction_dashboard.html"),
            target=LaunchModalEffect.TargetType.PAGE,
        ).apply()
