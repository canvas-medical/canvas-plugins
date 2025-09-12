from canvas_sdk.commands import PlanCommand
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
        plan = PlanCommand(narrative="the button worked!")
        p2 = ProtocolCard(
            patient_id=patient_id,
            key="buttons",
            title="buttons",
            narrative="there should be buttons here",
            recommendations=[plan.recommend(title="have a plan!")],
        )
        p2.add_recommendation(
            title="go to canvas", button="here", href="https://www.canvasmedical.com"
        )
        return [p2.apply()]
