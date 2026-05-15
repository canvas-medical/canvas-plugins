from dataclasses import dataclass
from json import loads

from canvas_sdk.clients.sendgrid.structures.parsed_attachment import ParsedAttachment
from canvas_sdk.clients.sendgrid.structures.parsed_envelope import ParsedEnvelope
from canvas_sdk.clients.sendgrid.structures.parsed_header import ParsedHeader


@dataclass(frozen=True)
class ParsedEmail:
    """Represents a complete inbound email parsed by SendGrid's Inbound Parse Webhook."""

    headers: list[ParsedHeader]
    charsets: dict[str, str]
    envelope: ParsedEnvelope
    email_from: str
    email_to: str
    subject: str
    text: str
    html: str
    attachments: int
    attachment_info: dict[str, ParsedAttachment]
    content_ids: dict[str, str]
    spf: str
    dkim: str
    spam_report: list[str]
    spam_score: float

    @classmethod
    def from_dict(cls, data: dict) -> "ParsedEmail":
        """Create ParsedEmail instance from dictionary."""
        headers = [line.split(":") for line in data["headers"].split("\n")]

        attachments = 0
        if "attachments" in data:
            attachments = int(data["attachments"])
        attachment_info = {}
        if "attachment_info" in data:
            attachment_info = {
                key: ParsedAttachment.from_dict(info)
                for key, info in loads(data["attachment_info"]).items()
            }
        content_ids = {}
        if "content-ids" in data:
            content_ids = loads(data["content-ids"])
        spam_score = 0.0
        if "spam_score" in data:
            spam_score = float(data["spam_score"])
        spam_report = []
        if "spam_report" in data:
            spam_report = data["spam_report"].split("\n")

        return cls(
            headers=[
                ParsedHeader(name=header[0].strip(), value=":".join(header[1:]).strip())
                for header in headers
            ],
            charsets=loads(data["charsets"]),
            envelope=ParsedEnvelope.from_dict(loads(data["envelope"])),
            email_from=data["from"],
            email_to=data["to"],
            subject=data["subject"],
            text=data["text"],
            html=data["html"],
            attachments=attachments,
            attachment_info=attachment_info,
            content_ids=content_ids,
            spf=data["SPF"],
            dkim=data["dkim"],
            spam_report=spam_report,
            spam_score=spam_score,
        )

    def to_dict(self) -> dict:
        """Convert parsed email to dictionary format."""
        return {
            "headers": [h.to_dict() for h in self.headers],
            "charsets": self.charsets,
            "envelope": self.envelope.to_dict(),
            "emailFrom": self.email_from,
            "emailTo": self.email_to,
            "subject": self.subject,
            "text": self.text,
            "html": self.html,
            "attachments": self.attachments,
            "attachmentInfo": {key: info.to_dict() for key, info in self.attachment_info.items()},
            "contentIds": self.content_ids,
            "spf": self.spf,
            "dkim": self.dkim,
            "spamReport": self.spam_report,
            "spamScore": str(round(self.spam_score, 2)),
        }


__exports__ = ()
