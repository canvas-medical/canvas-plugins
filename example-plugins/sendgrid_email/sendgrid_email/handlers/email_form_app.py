from canvas_sdk.effects import Effect
from canvas_sdk.effects.launch_modal import LaunchModalEffect
from canvas_sdk.handlers.application import Application
from canvas_sdk.templates import render_to_string

from ..constants.constants import Constants


class EmailFormApp(Application):
    """Application handler for displaying the Sendgrid email form interface.

    Provides a modal interface for sending emails, viewing sent emails,
    and managing inbound/outbound webhooks through Sendgrid.
    """

    def on_open(self) -> Effect:
        """Render and display the email form modal.

        Returns:
            Effect: A LaunchModalEffect that displays the email form in the right chart pane.
        """
        content = render_to_string(
            "templates/email_form.html",
            {
                "sendEmailURL": f"{Constants.plugin_api_base_route}/send_email",
                "emailsSentURL": f"{Constants.plugin_api_base_route}/emails_sent",
                "emailEventsURL": f"{Constants.plugin_api_base_route}/email_events",
                "outboundWebhookURL": f"{Constants.plugin_api_base_route}/outbound_webhook",
                "outboundStatusesURL": f"{Constants.plugin_api_base_route}/outbound_email_status",
                "inboundWebhookURL": f"{Constants.plugin_api_base_route}/inbound_webhook",
                "inboundEmailURL": f"{Constants.plugin_api_base_route}/inbound_email",
            },
        )

        return LaunchModalEffect(
            content=content,
            target=LaunchModalEffect.TargetType.RIGHT_CHART_PANE,
        ).apply()
