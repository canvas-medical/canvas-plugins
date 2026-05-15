from dataclasses import dataclass


@dataclass(frozen=True)
class _Constants:
    """Configuration constants for the SendGrid email plugin."""

    sendgrid_api_key: str = "SendgridAPIKey"
    plugin_api_base_route: str = "/plugin-io/api/email_sender"
    customer_identifier: str = "CUSTOMER_IDENTIFIER"


Constants = _Constants()
