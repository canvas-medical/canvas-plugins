from enum import Enum


class RecipientType(Enum):
    """Defines the types of recipients for an email."""

    TO = "to"
    CC = "cc"
    BCC = "bcc"


__exports__ = ()
