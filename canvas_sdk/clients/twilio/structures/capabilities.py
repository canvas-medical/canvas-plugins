from dataclasses import dataclass
from typing import Self


@dataclass(frozen=True)
class Capabilities:
    """Represents the communication capabilities of a Twilio phone number.

    Attributes:
        fax: Whether the phone number supports fax.
        mms: Whether the phone number supports MMS (multimedia messages).
        sms: Whether the phone number supports SMS (text messages).
        voice: Whether the phone number supports voice calls.
    """

    fax: bool
    mms: bool
    sms: bool
    voice: bool

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        """Create a Capability instance from a dictionary.

        Args:
            data: Dictionary containing capability data from Twilio API.

        Returns:
            Capability instance with parsed capability flags.
        """
        return cls(
            fax=bool(data["fax"]),
            mms=bool(data["mms"]),
            sms=bool(data["sms"]),
            voice=bool(data["voice"]),
        )

    def to_dict(self) -> dict:
        """Convert the Capability to a dictionary representation.

        Returns:
            Dictionary containing all capability flags.
        """
        return {
            "fax": self.fax,
            "mms": self.mms,
            "sms": self.sms,
            "voice": self.voice,
        }


__exports__ = ()
