from canvas_sdk.effects import Effect
from canvas_sdk.effects.launch_modal import LaunchModalEffect
from canvas_sdk.handlers.application import Application
from canvas_sdk.templates import render_to_string


class PdfFormApp(Application):
    """Application handler that displays the PDF processing form in a modal."""

    PLUGIN_API_BASE_ROUTE = "/plugin-io/api/pdf_manip"

    def on_open(self) -> Effect:
        """Render and launch the PDF processing form modal in the right chart pane."""
        content = render_to_string(
            "templates/pdf_form.html",
            {
                "processorsURL": f"{self.PLUGIN_API_BASE_ROUTE}/processors",
                "statusURL": f"{self.PLUGIN_API_BASE_ROUTE}/status",
                "executeURL": f"{self.PLUGIN_API_BASE_ROUTE}/execute",
                "resultURL": f"{self.PLUGIN_API_BASE_ROUTE}/result",
                "storedFilesURL": f"{self.PLUGIN_API_BASE_ROUTE}/stored_files",
                "deleteFilesURL": f"{self.PLUGIN_API_BASE_ROUTE}/delete_files",
            },
        )

        return LaunchModalEffect(
            content=content,
            target=LaunchModalEffect.TargetType.RIGHT_CHART_PANE,
        ).apply()
