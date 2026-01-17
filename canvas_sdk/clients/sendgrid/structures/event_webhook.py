from dataclasses import dataclass
from typing import Self

from canvas_sdk.clients.sendgrid.structures.structure import Structure


@dataclass(frozen=True)
class EventWebhook(Structure):
    """Represents a webhook configuration for receiving email event notifications.

    schema defined in https://www.twilio.com/docs/sendgrid/api-reference/webhooks/create-an-event-webhook#request-body
    """

    enabled: bool
    url: str  # url receiving the POST from SendGrid with the new email status
    group_resubscribe: bool
    group_unsubscribe: bool
    delivered: bool
    spam_report: bool
    bounce: bool
    unsubscribe: bool
    processed: bool
    open: bool
    click: bool
    dropped: bool
    friendly_name: str  # name of the webhook

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        """Create EventWebhook instance from dictionary."""
        return cls(
            enabled=bool(data["enabled"]),
            url=data["url"],
            group_resubscribe=bool(data["group_resubscribe"]),
            group_unsubscribe=bool(data["group_unsubscribe"]),
            delivered=bool(data["delivered"]),
            spam_report=bool(data["spam_report"]),
            bounce=bool(data["bounce"]),
            unsubscribe=bool(data["unsubscribe"]),
            processed=bool(data["processed"]),
            open=bool(data["open"]),
            click=bool(data["click"]),
            dropped=bool(data["dropped"]),
            friendly_name=data["friendly_name"],
        )

    def to_dict(self) -> dict:
        """Convert event webhook to dictionary format."""
        return {
            "enabled": self.enabled,
            "url": self.url,
            "group_resubscribe": self.group_resubscribe,
            "group_unsubscribe": self.group_unsubscribe,
            "delivered": self.delivered,
            "spam_report": self.spam_report,
            "bounce": self.bounce,
            "unsubscribe": self.unsubscribe,
            "processed": self.processed,
            "open": self.open,
            "click": self.click,
            "dropped": self.dropped,
            "friendly_name": self.friendly_name,
        }


__exports__ = ()
