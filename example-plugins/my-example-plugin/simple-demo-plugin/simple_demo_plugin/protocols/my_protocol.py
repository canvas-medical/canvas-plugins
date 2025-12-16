"""Simple demo protocol that displays a banner when a patient chart is opened."""

from canvas_sdk.effects.banner_alert import AddBannerAlert
from canvas_sdk.events import EventType
from canvas_sdk.protocols import BaseProtocol
from logger import log


class Protocol(BaseProtocol):
    """Displays a welcome banner when a patient record is updated.

    This is the simplest possible Canvas plugin demonstrating:
    - How to respond to Canvas events (PATIENT_UPDATED)
    - How to return effects to the UI (AddBannerAlert)
    - Basic plugin structure
    """

    # Listen for patient update events
    RESPONDS_TO = EventType.Name(EventType.PATIENT_UPDATED)

    def compute(self) -> list[AddBannerAlert]:
        """Display a welcome banner when a patient record is updated.

        Returns:
            A list containing a single AddBannerAlert effect with a demo message.
        """
        # Log for debugging (visible in Canvas CLI logs)
        log.info(f"Patient updated event triggered for patient ID: {self.event.target.id}")

        # Return a banner alert effect to display in the UI
        return [
            AddBannerAlert(
                narrative="Hello from your demo plugin! This patient record was just updated.",
                intent=AddBannerAlert.Intent.INFO,
                placement=[AddBannerAlert.Placement.TIMELINE],
            )
        ]
