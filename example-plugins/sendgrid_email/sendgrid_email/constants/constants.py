from dataclasses import dataclass


@dataclass(frozen=True)
class _Constants:
    """Configuration constants for the Sendgrid email plugin.

    Attributes:
        sendgrid_api_key: Key name for retrieving the Sendgrid API key from secrets.
        plugin_api_base_route: Base route for all plugin API endpoints.
        customer_identifier: Environment variable key for customer identification.
    """

    sendgrid_api_key: str = "SendgridAPIKey"
    plugin_api_base_route: str = "/plugin-io/api/sendgrid_email"
    customer_identifier: str = "CUSTOMER_IDENTIFIER"


Constants = _Constants()
