from canvas_generated.messages.effects_pb2 import Effect
from canvas_sdk.commands import PrescribeCommand
from canvas_sdk.effects.protocol_card import ProtocolCard
from canvas_sdk.events import EventType
from canvas_sdk.protocols import BaseProtocol
from logger import log


class Protocol(BaseProtocol):
    """
    This protocol responds to the NOTE_STATE_CHANGE_EVENT_CREATED event.
    When a note is created, protocol will be created with a prescribe command.
    If prescribe command is triggered, it will be initialized with supervising provider field.
    """

    RESPONDS_TO = EventType.Name(EventType.NOTE_STATE_CHANGE_EVENT_CREATED)

    def compute(self) -> list[Effect]:
        """This method gets called when an event of the type RESPONDS_TO is fired."""
        log.info(f"Note {self.context['note_id']} on patient {self.context['patient_id']}")

        p = ProtocolCard(
            patient_id=self.context["patient_id"],
            key="testing-protocol-cards",
            title="This is a Prescribe ProtocolCard title",
        )

        prescription_rec = PrescribeCommand(
            supervising_provider_id="4150cd20de8a470aa570a852859ac87e",
        )
        p.recommendations.append(
            prescription_rec.recommend(title="This inserts a prescribe command", button="Prescribe")
        )

        return [p.apply()]
