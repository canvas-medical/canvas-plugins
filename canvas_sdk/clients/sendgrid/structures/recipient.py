from dataclasses import dataclass

from canvas_sdk.clients.sendgrid.constants import RecipientType
from canvas_sdk.clients.sendgrid.structures import Address


@dataclass(frozen=True)
class Recipient:
    """Represents an email recipient with type (TO, CC, BCC)."""

    address: Address
    type: RecipientType


__exports__ = ()
