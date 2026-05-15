from canvas_sdk.effects import Effect
from canvas_sdk.effects.launch_modal import LaunchModalEffect
from canvas_sdk.handlers.application import Application
from canvas_sdk.templates import render_to_string

from ..constants.constants import Constants


class SmsFormApp(Application):
    """Application handler for the SMS/MMS form interface.

    This class provides the UI application that launches a modal with the SMS/MMS
    management interface, including forms for sending messages and viewing message history.
    """

    def on_open(self) -> Effect:
        """Handle the application open event.

        Renders the SMS form HTML template with all necessary API endpoint URLs
        and launches it in a modal on the right chart pane.

        Returns:
            Effect: LaunchModalEffect with the rendered SMS form content.
        """
        host = f"https://{self.environment[Constants.customer_identifier]}.canvasmedical.com"
        content = render_to_string(
            "templates/sms_form.html",
            {
                "smsSendURL": f"{Constants.plugin_api_base_route}/sms_send",
                "phoneListURL": f"{Constants.plugin_api_base_route}/phone_list",
                "setInboundWebhookURL": f"{Constants.plugin_api_base_route}/inbound_webhook",
                "messageListURL": f"{Constants.plugin_api_base_route}/message_list",
                "messageURL": f"{Constants.plugin_api_base_route}/message",
                "mediaURL": f"{Constants.plugin_api_base_route}/medias",
                "deleteMessageURL": f"{Constants.plugin_api_base_route}/message_delete",
                "defaultCallbackURL": f"{host}{Constants.plugin_api_base_route}/outbound_api_status",
            },
        )

        return LaunchModalEffect(
            content=content,
            target=LaunchModalEffect.TargetType.RIGHT_CHART_PANE,
        ).apply()
