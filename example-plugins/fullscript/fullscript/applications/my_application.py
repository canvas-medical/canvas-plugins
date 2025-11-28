from canvas_sdk.effects import Effect
from canvas_sdk.effects.launch_modal import LaunchModalEffect
from canvas_sdk.handlers.application import Application
from logger import log


def get_application_url(
    params: dict, patient_key: str | None = None, note_id: str | None = None
) -> str:
    """Get the path to the Fullscript application."""
    url = "/plugin-io/api/fullscript/app/fullscript-app"

    if patient_key:
        url += f"?patient={patient_key}"
    for param in params:
        url += f"&{param}={params[param]}"
    if note_id:
        url += f"&noteId={note_id}"

    return url


class MyApplication(Application):
    """An embeddable application that can be registered to Canvas."""

    def on_open(self) -> Effect:
        """Handle the on_open event."""
        # Implement this method to handle the application on_open event.
        log.info("Application opened")
        log.info(self.context)

        patient_key = self.context["patient"].get("id") if self.context.get("patient") else None
        params = self.context["params"] if self.context.get("params") else {}

        url = get_application_url(params, patient_key)

        return LaunchModalEffect(
            url=url,
            target=LaunchModalEffect.TargetType.RIGHT_CHART_PANE_LARGE,
        ).apply()
