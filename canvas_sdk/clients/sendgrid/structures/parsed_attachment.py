from dataclasses import dataclass


@dataclass(frozen=True)
class ParsedAttachment:
    """Represents an attachment from an inbound parsed email."""

    filename: str
    name: str
    type: str
    content_id: str

    @classmethod
    def from_dict(cls, data: dict) -> "ParsedAttachment":
        """Create ParsedAttachment instance from dictionary."""
        return cls(
            filename=data["filename"],
            name=data["name"],
            type=data["type"],
            content_id=data["content-id"],
        )

    def to_dict(self) -> dict:
        """Convert parsed attachment to dictionary format."""
        return {
            "filename": self.filename,
            "name": self.name,
            "type": self.type,
            "contentId": self.content_id,
        }


__exports__ = ()
