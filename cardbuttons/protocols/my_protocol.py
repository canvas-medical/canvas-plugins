from canvas_sdk.effects import Effect
from canvas_sdk.effects.protocol_card import ProtocolCard
from canvas_sdk.events import EventType
from canvas_sdk.protocols import BaseProtocol


# Inherit from BaseProtocol to properly get registered for events
class Protocol(BaseProtocol):
    """You should put a helpful description of this protocol's behavior here."""

    # Name the event type you wish to run in response to
    RESPONDS_TO = EventType.Name(EventType.DIAGNOSE_COMMAND__POST_ORIGINATE)

    def compute(self) -> list[Effect]:
        """This method gets called when an event of the type RESPONDS_TO is fired."""
        patient_id = str(self.context["patient"]["id"])
        p = ProtocolCard(
            patient_id=patient_id,
            key="no-buttons",
            title="no buttons",
            narrative="there should be no buttons here",
        )
        p.add_recommendation(title="hello")
        p.add_recommendation(title="how are you")
        return [p.apply()]
