from canvas_sdk.effects import Effect
from canvas_sdk.effects.launch_modal import LaunchModalEffect
from canvas_sdk.handlers.application import Application
from canvas_sdk.templates import render_to_string


class AwsFormApp(Application):
    """Application handler for launching the AWS S3 management form interface."""

    PLUGIN_API_BASE_ROUTE = "/plugin-io/api/aws_manip"

    def on_open(self) -> Effect:
        """Render and launch the AWS S3 management modal form.

        Returns:
            Effect to launch the modal with the AWS S3 management interface.
        """
        content = render_to_string(
            "templates/aws_form.html",
            {
                "listItemsURL": f"{self.PLUGIN_API_BASE_ROUTE}/list_items",
                "getItemURL": f"{self.PLUGIN_API_BASE_ROUTE}/get_item",
                "presignedUrlURL": f"{self.PLUGIN_API_BASE_ROUTE}/presigned_url",
                "uploadItemURL": f"{self.PLUGIN_API_BASE_ROUTE}/upload_item",
                "deleteItemURL": f"{self.PLUGIN_API_BASE_ROUTE}/delete_item",
            },
        )

        return LaunchModalEffect(
            content=content,
            target=LaunchModalEffect.TargetType.RIGHT_CHART_PANE,
        ).apply()
