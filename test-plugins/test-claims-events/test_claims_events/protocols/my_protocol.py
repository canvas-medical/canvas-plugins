import json

from canvas_sdk.effects import Effect
from canvas_sdk.events import EventType
from canvas_sdk.protocols import BaseProtocol
from logger import log


# Inherit from BaseProtocol to properly get registered for events
class Protocol(BaseProtocol):
    """You should put a helpful description of this protocol's behavior here."""

    # Name the event type you wish to run in response to
    RESPONDS_TO = [EventType.Name(EventType.CLAIM_UPDATED), EventType.Name(EventType.CLAIM_CREATED)]

    def compute(self) -> list[Effect]:
        """This method gets called when an event of the type RESPONDS_TO is fired."""
        log.info(f"Event received in Protocol: {self.event}")
        log.info(f"Event context: {json.dumps(self.event.context, indent=2, default=str)}")

        # Return zero, one, or many effects.
        # Example:
        return []
