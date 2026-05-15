from dataclasses import dataclass
from typing import Self

from canvas_sdk.clients.sendgrid.structures.structure import Structure


@dataclass(frozen=True)
class ParseSetting(Structure):
    """Represents configuration for parsing incoming emails.

    ATTENTION: for the `hostname` field an MX record should exist
    with a priority of 10, and pointing to the address: mx.sendgrid.net.

    https://www.twilio.com/docs/sendgrid/for-developers/parsing-email/setting-up-the-inbound-parse-webhook
    """

    url: str  # url receiving the POST from SendGrid when an incoming email is received
    hostname: str  # validated domain or subdomain of a validated domain,
    spam_check: bool
    send_raw: bool

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        """Create ParseSetting instance from dictionary."""
        return cls(
            url=data["url"],
            hostname=data["hostname"],
            spam_check=bool(data["spam_check"]),
            send_raw=bool(data["send_raw"]),
        )

    def to_dict(self) -> dict:
        """Convert parse setting to dictionary format."""
        return {
            "url": self.url,
            "hostname": self.hostname,
            "spam_check": self.spam_check,
            "send_raw": self.send_raw,
        }


__exports__ = ()
