from dataclasses import dataclass


@dataclass(frozen=True)
class _Constants:
    """Configuration constants for the Twilio SMS/MMS plugin.

    This frozen dataclass stores constant values used throughout the plugin,
    including Twilio API credentials keys and plugin routing configuration.
    """

    twillio_account_sid: str = "TwilioAccountSID"
    twillio_api_key: str = "TwilioAPIKey"
    twillio_api_secret: str = "TwilioAPISecret"
    plugin_api_base_route: str = "/plugin-io/api/twilio_sms_mms"
    customer_identifier: str = "CUSTOMER_IDENTIFIER"


Constants = _Constants()
