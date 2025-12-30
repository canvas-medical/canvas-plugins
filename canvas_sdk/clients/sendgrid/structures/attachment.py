from __future__ import annotations

from base64 import b64encode
from dataclasses import dataclass
from http import HTTPStatus

from canvas_sdk.clients.sendgrid.constants.attachment_disposition import AttachmentDisposition
from canvas_sdk.clients.sendgrid.structures.request_failed import RequestFailed
from canvas_sdk.utils import Http


@dataclass(frozen=True)
class Attachment:
    """Represents an email attachment with content and metadata."""

    content_id: str
    content: str  # base64 encoded
    type: str  # mime type
    filename: str
    disposition: AttachmentDisposition

    def to_dict(self) -> dict:
        """Convert attachment to dictionary format."""
        return {
            "content_id": self.content_id,
            "content": self.content,
            "type": self.type,
            "filename": self.filename,
            "disposition": self.disposition.value,
        }

    @classmethod
    def from_url_inline(cls, url: str, headers: dict, filename: str, content_id: str) -> Attachment:
        """Create an attachment by fetching content from URL, optionally as inline."""
        request = Http(url).get("", headers=headers)
        if request.status_code != HTTPStatus.OK:
            raise RequestFailed(request.status_code, request.content.decode())
        disposition = AttachmentDisposition.ATTACHMENT
        if content_id:
            disposition = AttachmentDisposition.INLINE
        return Attachment(
            content=b64encode(request.content).decode("utf-8"),
            filename=filename,
            content_id=content_id,
            type=request.headers["Content-Type"],
            disposition=disposition,
        )

    @classmethod
    def from_url(cls, url: str, headers: dict, filename: str) -> Attachment:
        """Create an attachment by fetching content from URL."""
        return cls.from_url_inline(url, headers, filename, "")


__exports__ = ()
