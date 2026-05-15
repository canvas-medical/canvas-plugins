from canvas_sdk.effects import Effect
from canvas_sdk.effects.launch_modal import LaunchModalEffect
from canvas_sdk.handlers.application import Application


class NoteManagementApplication(Application):
    """
    External note management application that demonstrates OAuth 2.0 integration.

    This application opens in a new tab and provides:
    1. OAuth 2.0 Authorization Code Flow with PKCE
    2. Automatic token refresh
    3. Note management operations (lock, sign, unlock, check-in, no-show)

    Users can authenticate with Canvas and perform note operations through a
    simple web interface.
    """

    def on_open(self) -> Effect:
        """Handle the application open event.

        Launches the note management application in a new window.
        """
        # Build the URL to the API endpoint that serves the HTML
        app_url = "/plugin-io/api/note_management_app/app"

        return LaunchModalEffect(
            url=app_url,
            target=LaunchModalEffect.TargetType.NEW_WINDOW,
        ).apply()
