from dataclasses import dataclass
from datetime import datetime
from typing import Self

from canvas_sdk.clients.twilio.constants import Constants, HttpMethod
from canvas_sdk.clients.twilio.structures.capabilities import Capabilities
from canvas_sdk.clients.twilio.structures.helper import Helper
from canvas_sdk.clients.twilio.structures.structure import Structure


@dataclass(frozen=True)
class Phone(Structure):
    """Represents a Twilio phone number with its configuration and capabilities.

    Attributes:
        account_sid: The unique identifier for the Twilio account.
        capabilities: Communication capabilities of the phone number.
        date_created: When the phone number was added to the account.
        date_updated: When the phone number configuration was last updated.
        friendly_name: User-defined name for the phone number.
        phone_number: The phone number in E.164 format.
        sid: The unique identifier for this phone number resource.
        sms_fallback_method: HTTP method for the SMS fallback URL.
        sms_fallback_url: URL to request if the SMS URL fails.
        sms_method: HTTP method for the SMS URL.
        sms_url: URL to request when an SMS is received.
        status_callback_method: HTTP method for the status callback URL.
        status_callback: URL to receive status updates.
        status: Current status of the phone number.
    """

    account_sid: str
    capabilities: Capabilities
    date_created: datetime
    date_updated: datetime
    friendly_name: str
    phone_number: str
    sid: str
    sms_fallback_method: HttpMethod
    sms_fallback_url: str
    sms_method: HttpMethod
    sms_url: str
    status_callback_method: HttpMethod
    status_callback: str
    status: str

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        """Create a Phone instance from a dictionary.

        Args:
            data: Dictionary containing phone number data from Twilio API.

        Returns:
            Phone instance populated with the provided data.
        """
        return cls(
            account_sid=data["account_sid"],
            capabilities=Capabilities.from_dict(data["capabilities"]),
            date_created=Helper.to_datetime(data, "date_created"),
            date_updated=Helper.to_datetime(data, "date_updated"),
            friendly_name=data["friendly_name"],
            phone_number=data["phone_number"],
            sid=data["sid"],
            sms_fallback_method=HttpMethod(data["sms_fallback_method"]),
            sms_fallback_url=data["sms_fallback_url"],
            sms_method=HttpMethod(data["sms_method"]),
            sms_url=data["sms_url"],
            status_callback_method=HttpMethod(data["status_callback_method"]),
            status_callback=data["status_callback"],
            status=data["status"],
        )

    def to_dict(self) -> dict:
        """Convert the Phone to a dictionary representation.

        Returns:
            Dictionary containing all phone number data and configuration.
        """
        return {
            "account_sid": self.account_sid,
            "capabilities": self.capabilities.to_dict(),
            "date_created": Helper.from_datetime(self.date_created, Constants.twilio_date),
            "date_updated": Helper.from_datetime(self.date_updated, Constants.twilio_date),
            "created": Helper.from_datetime(self.date_created, Constants.standard_date),
            "updated": Helper.from_datetime(self.date_updated, Constants.standard_date),
            "friendly_name": self.friendly_name,
            "phone_number": self.phone_number,
            "sid": self.sid,
            "sms_fallback_method": self.sms_fallback_method,
            "sms_fallback_url": self.sms_fallback_url,
            "sms_method": self.sms_method,
            "sms_url": self.sms_url,
            "status_callback_method": self.status_callback_method,
            "status_callback": self.status_callback,
            "status": self.status,
        }


__exports__ = ()
