from enum import Enum


class AttachmentDisposition(Enum):
    """Defines how an attachment should be displayed in an email."""

    ATTACHMENT = "attachment"
    INLINE = "inline"


__exports__ = ()
