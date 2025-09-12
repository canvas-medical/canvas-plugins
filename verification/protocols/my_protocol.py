from canvas_sdk.effects import Effect
from canvas_sdk.effects.send_contact_verification import SendContactVerificationEffect
from canvas_sdk.events import EventType
from canvas_sdk.protocols import BaseProtocol


# Inherit from BaseProtocol to properly get registered for events
class Protocol(BaseProtocol):
    """You should put a helpful description of this protocol's behavior here."""

    # Name the event type you wish to run in response to
    RESPONDS_TO = EventType.Name(EventType.PATIENT_CONTACT_POINT_CREATED)

    def compute(self) -> list[Effect]:
        """This method gets called when an event of the type RESPONDS_TO is fired."""
        contact_point_id = self.event.target
        verification_effect = SendContactVerificationEffect(contact_point_id=contact_point_id)
        return [verification_effect.apply()]
